from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import numpy as np
import os
import json
from datetime import datetime

from entitymodels.schemas import DataRequest, DataResponse, DataStatistic
from algorithm.data_loader import load_dataset, get_data_statistics, get_sample_data, load_forcast_dataset
from routes.auth import get_current_user
from entitymodels.entities import User

router = APIRouter(prefix="/api", tags=["info"])
# 缓存已加载的数据
_data_cache = {}
valid_anomalydetection_datasets = ["SMD", "PSM", "MSL"]
valid_forcast_datasets = ["ETTh1", "ETTh2", "ETTm1", "ETTm2"]

def get_cached_data(dataname: str) -> tuple:
    """从缓存获取数据，如果不存在则加载"""
    if dataname not in _data_cache:
        try:
            data_folder = os.path.join(os.path.dirname(__file__), "..", "algorithm", "data")
            if dataname in valid_anomalydetection_datasets:
                train_loader, test_loader, labels = load_dataset(dataname, data_folder)
            elif dataname in valid_forcast_datasets:
                train_loader, test_loader, labels = load_forcast_dataset(dataname, data_folder)
            _data_cache[dataname] = {
                "train": train_loader.data,
                "test": test_loader.data,
                "label": labels,
                "timestamp": datetime.now(),
                "data_info": {
                    "train_shape": train_loader.data.shape,
                    "test_shape": test_loader.data.shape,
                    "label_shape": labels.shape if labels is not None else None,  # 安全处理
                    "data_type": "Time Series"
                }
            }
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"加载数据失败: {str(e)}")

    return (
        _data_cache[dataname]["train"],
        _data_cache[dataname]["test"],
        _data_cache[dataname]["label"],
        _data_cache[dataname]["data_info"]
    )


@router.post("/getdata", response_model=DataResponse)
async def get_data(
        request: DataRequest,
        current_user: User = Depends(get_current_user)
):
    """
    获取数据集信息

    Args:
        request: 包含数据名称和类型
            dataname: 数据集名称 (SMD, PSM, MSL)
            datatype: 数据类型 (1:训练, 2:测试, 3:标签)
    """
    if not current_user:
        return DataResponse(
                status=-1,
                message="token 无效",
                statistic=None,
                sample_data=[],
                data_info={}
            )

    try:
        # 验证数据名称
        # valid_anomalydetection_datasets = ["SMD", "PSM", "MSL"]
        # valid_forcast_datasets = ["ETTh1", "ETTh2", "ETTm1", "ETTm2"]
        valid_datasets = valid_anomalydetection_datasets + valid_forcast_datasets
        if request.dataname not in valid_datasets:
            return DataResponse(
                status=-1,
                message=f"不支持的数据集: {request.dataname}。支持的数据集: {', '.join(valid_datasets)}",
                statistic=None,
                sample_data=[],
                data_info={}
            )

        # 从缓存获取数据
        train_data, test_data, label_data, data_info = get_cached_data(request.dataname)

        # 根据数据类型选择数据
        if request.datatype == 1:
            data = train_data
            data_type_name = "训练数据"
        elif request.datatype == 2:
            data = test_data
            data_type_name = "测试数据"
        elif request.datatype == 3:
            data = label_data
            data_type_name = "标签数据"
        else:
            return DataResponse(
                status=-1,
                message=f"无效的数据类型: {request.datatype}。支持: 1(训练), 2(测试), 3(标签)",
                statistic=None,
                sample_data=[],
                data_info={}
            )

        # 获取统计信息
        statistics = get_data_statistics(data)

        # 获取样本数据（用于前端展示）
        sample_data = get_sample_data(data, sample_size=1000)

        # 更新数据信息
        data_info.update({
            "dataname": request.dataname,
            "datatype": request.datatype,
            "datatype_name": data_type_name,
            "sample_size": len(sample_data),
            "total_size": len(data)
        })

        return DataResponse(
            status=0,
            message=f"成功加载{data_type_name}",
            statistic=DataStatistic(**statistics),
            sample_data=sample_data,
            data_info=data_info
        )

    except Exception as e:
        return DataResponse(
            status=-1,
            message=f"获取数据失败: {str(e)}",
            statistic=DataStatistic(**create_default_statistic()),
            sample_data=[],
            data_info={}
        )
def create_default_statistic() -> Dict[str, Any]:
    """创建默认的统计信息字典"""
    return {
        "data_length": 0,
        "data_dimension": 0,
        "data_max": 0.0,
        "data_min": 0.0,
        "data_mean": 0.0,
        "data_std": 0.0,
        "data_shape": [0, 0]
    }

@router.get("/datasets")
async def get_available_datasets(current_user: User = Depends(get_current_user)):
    """获取可用的数据集列表"""
    if not current_user:
        return {
            "status": -2,
            "message": "token 失效",
            "datasets": None
        }

    data_folder = os.path.join(os.path.dirname(__file__), "..", "algorithm", "data")

    datasets = []
    if os.path.exists(data_folder):
        for item in os.listdir(data_folder):
            item_path = os.path.join(data_folder, item)
            if os.path.isdir(item_path):
                # 检查是否包含必要的文件
                required_files = ['train.npy', 'test.npy', 'labels.npy']
                has_files = all(
                    os.path.exists(os.path.join(item_path, f))
                    for f in required_files
                ) or all(
                    os.path.exists(os.path.join(item_path, f'machine-1-1_{f}.npy'))
                    for f in ['train', 'test']
                ) or all (
                    os.path.exists(os.path.join(item_path, f'{f}.csv'))
                    for f in [item]
                )

                if has_files:
                    datasets.append({
                        "name": item,
                        "path": item_path,
                        "files": os.listdir(item_path)
                    })

    return {
        "status": 0,
        "message": "成功",
        "datasets": datasets
    }