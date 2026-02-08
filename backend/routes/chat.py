from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from openai import OpenAI
from entitymodels.schemas import PredictionResponse, PredictionRequest, PredictionDataResponse, PredictionDataRequest, \
    AnomalyDetectionResponse, AnomalyDetectionRequest, AnomalyDetectionDataResponse, AnomalyDetectionDataRequest
import json
import traceback
import base64
import io
import numpy as np
from datetime import datetime, timedelta
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
from entitymodels.entities import User
from routes.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException

# 导入你已有工具
from .model import (
    predict as pf,
    anomalydetection as adf,
    get_prediction_data as gpdf,
    get_anomalydetection_data as gadf,
)

# 可用的数据集
PREDICTION_DATASETS = ["ETTh1", "ETTh2", "ETTm1", "ETTm2"]
ANOMALY_DATASETS = ["SMD", "PSM", "MSL"]

router = APIRouter(prefix="/apiv2", tags=["chat"])

# ====== 配置 DeepSeek ======
DEEPSEEK_API_KEY = "my token"

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)


# ====== 请求体 ======
class ChatRequest(BaseModel):
    message: str


# ====== 工具定义（给大模型看的 schema） ======
tools = [
    {
        "type": "function",
        "function": {
            "name": "predict",
            "description": (
                "用于时间序列预测任务。"
                "当用户提到'预测'、'forecast'、'predict'、'未来趋势'等意图时必须调用此工具。"
                "支持指定数据集和预测步长。"
                "该工具会返回预测数据、统计信息，并自动生成预测曲线图（维度0）。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dataname": {
                        "type": "string",
                        "description": "数据集名称，例如：ETTh1, ETTh2, ETTm1, ETTm2"
                    },
                    "step": {
                        "type": "integer",
                        "description": "预测步长，例如 96 表示预测未来96个时间点"
                    }
                },
                "required": ["dataname"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "anomaly_detection",
            "description": (
                "用于异常检测任务。"
                "当用户提到'异常检测'、'outlier'、'异常点'等请求时必须调用此工具。"
                "返回异常分数、标签及统计信息，并自动生成绘制异常图（维度0）。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dataname": {
                        "type": "string",
                        "description": "异常检测数据集名称，如 SMD, PSM, MSL"
                    }
                },
                "required": ["dataname"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_datasets",
            "description": "当用户询问有哪些数据集、支持哪些数据时调用。",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


def calculate_stats(data: List[List[float]], dim: int = 0) -> Dict[str, Any]:
    """计算数据统计信息"""
    if not data:
        return {}

    # 确保维度有效
    if len(data[0]) <= dim:
        dim = 0

    values = [row[dim] for row in data if len(row) > dim]

    if not values:
        return {}

    return {
        "length": len(data),
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
        "dimensions": len(data[0]) if data else 0
    }


async def get_available_datasets() -> dict:
    """
    获取当前可用的数据集列表

    Returns:
        可用数据集的字典
    """
    result = {
        "success": True,
        "message": "获取可用数据集成功",
        "prediction_datasets": PREDICTION_DATASETS,
        "anomaly_datasets": ANOMALY_DATASETS,
        "description": {
            "prediction": "时序预测数据集，用于时间序列预测任务",
            "anomaly": "异常检测数据集，用于异常检测任务"
        }
    }
    return result


def create_prediction_chart(history_data: List[float], truth_data: List[float],
                            prediction_data: List[float], dataset_name: str, step: int) -> str:
    """
    创建预测结果图表

    Args:
        history_data: 历史数据
        truth_data: 真实数据
        prediction_data: 预测数据
        dataset_name: 数据集名称
        step: 预测步长

    Returns:
        base64编码的图片字符串
    """
    try:
        # 设置中文字体和样式
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.figsize'] = [12, 6]

        fig, ax = plt.subplots(figsize=(12, 6))

        # 生成时间索引
        total_len = len(history_data) + len(truth_data)
        time_index = list(range(total_len))

        # 历史数据部分
        hist_start = 0
        hist_end = len(history_data)
        hist_indices = time_index[hist_start:hist_end]

        # 预测/真实数据部分
        pred_start = hist_end
        pred_end = total_len
        pred_indices = time_index[pred_start:pred_end]

        # 绘制历史数据
        ax.plot(hist_indices, history_data, 'b-', linewidth=1.5, label='历史数据', alpha=0.8)

        # 绘制真实数据
        if truth_data and len(truth_data) > 0:
            ax.plot(pred_indices, truth_data, 'g-', linewidth=1.5, label='真实数据', alpha=0.8)

        # 绘制预测数据
        if prediction_data and len(prediction_data) > 0:
            ax.plot(pred_indices, prediction_data, 'r--', linewidth=2, label='预测数据', alpha=0.9)

        # 添加垂直虚线分隔历史与预测区域
        ax.axvline(x=hist_end, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        ax.text(hist_end, ax.get_ylim()[0], ' 预测开始', verticalalignment='bottom',
                horizontalalignment='left', color='gray', fontsize=10)

        # 计算预测误差
        mse = None
        mae = None
        if truth_data and prediction_data and len(truth_data) == len(prediction_data):
            truth_np = np.array(truth_data)
            pred_np = np.array(prediction_data)
            mse = np.mean((truth_np - pred_np) ** 2)
            mae = np.mean(np.abs(truth_np - pred_np))

        # 添加统计信息文本
        stats_text = f'数据集: {dataset_name}\n预测步长: {step}\n历史数据长度: {len(history_data)}\n预测数据长度: {len(prediction_data)}'
        if mse is not None and mae is not None:
            stats_text += f'\nMSE: {mse:.4f}\nMAE: {mae:.4f}'

        # 添加文本框
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)

        # 设置图表属性
        ax.set_xlabel('时间点', fontsize=12)
        ax.set_ylabel('数值', fontsize=12)
        ax.set_title(f'{dataset_name} 时序预测结果 (维度0)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best', fontsize=10)

        # 调整布局
        plt.tight_layout()

        # 保存为base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)

        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return img_base64

    except Exception as e:
        print(f"生成预测图表失败: {e}")
        return ""


def create_anomaly_chart(origin_data: List[float], reconstruction_data: List[float],
                         anomaly_score: List[float], pred_labels: List[int],
                         threshold: float, dataset_name: str) -> str:
    """
    创建异常检测结果图表

    Args:
        origin_data: 原始数据
        reconstruction_data: 重构数据
        anomaly_score: 异常分数
        pred_labels: 异常标签
        threshold: 异常阈值
        dataset_name: 数据集名称

    Returns:
        base64编码的图片字符串
    """
    try:
        # 设置中文字体和样式
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.figsize'] = [12, 8]

        fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # 生成时间索引
        time_index = list(range(len(origin_data)))

        # 第一个子图：原始数据 vs 重构数据
        ax1 = axes[0]

        # 绘制原始数据
        ax1.plot(time_index, origin_data, 'b-', linewidth=1.2, label='原始数据', alpha=0.8)

        # 绘制重构数据
        if reconstruction_data and len(reconstruction_data) > 0:
            ax1.plot(time_index[:len(reconstruction_data)], reconstruction_data,
                     'r--', linewidth=1.5, label='重构数据', alpha=0.7)

        # 高亮异常区域
        anomaly_regions = []
        in_anomaly = False
        start_idx = 0

        for i, label in enumerate(pred_labels):
            if label == 1 and not in_anomaly:
                in_anomaly = True
                start_idx = i
            elif label == 0 and in_anomaly:
                in_anomaly = False
                anomaly_regions.append((start_idx, i - 1))

        # 处理最后一个异常区域
        if in_anomaly:
            anomaly_regions.append((start_idx, len(pred_labels) - 1))

        # 绘制异常区域背景
        for start, end in anomaly_regions:
            ax1.axvspan(start, end, color='red', alpha=0.2, label='异常区域' if start == anomaly_regions[0][0] else "")

        ax1.set_ylabel('数值', fontsize=12)
        ax1.set_title(f'{dataset_name} 异常检测结果 (维度0)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='best', fontsize=10)

        # 第二个子图：异常分数
        ax2 = axes[1]

        if anomaly_score and len(anomaly_score) > 0:
            ax2.plot(time_index[:len(anomaly_score)], anomaly_score,
                     'g-', linewidth=1.2, label='异常分数', alpha=0.8)

        # 绘制异常阈值线
        ax2.axhline(y=threshold, color='r', linestyle='--', linewidth=1.5,
                    label=f'异常阈值: {threshold:.4f}', alpha=0.7)

        # 在异常区域填充背景
        for start, end in anomaly_regions:
            ax2.axvspan(start, end, color='red', alpha=0.2)

        # 统计信息
        anomaly_count = sum(pred_labels)
        anomaly_ratio = (anomaly_count / len(pred_labels) * 100) if pred_labels else 0

        stats_text = f'数据集: {dataset_name}\n异常阈值: {threshold:.4f}\n异常点数量: {anomaly_count}\n异常比例: {anomaly_ratio:.2f}%'

        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
                 verticalalignment='top', bbox=props)

        ax2.set_xlabel('时间点', fontsize=12)
        ax2.set_ylabel('异常分数', fontsize=12)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='best', fontsize=10)

        # 调整布局
        plt.tight_layout()

        # 保存为base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)

        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return img_base64

    except Exception as e:
        print(f"生成异常检测图表失败: {e}")
        traceback.print_exc()
        return ""


async def predict(dataname: str, step: int = 96) -> dict:
    """
    在指定数据集上执行时序预测

    Args:
        dataname: 数据集名称 (ETTh1, ETTh2, ETTm1, ETTm2)
        step: 预测步长 (默认96)

    Returns:
        预测结果的字典，包含统计信息和图表
    """
    try:
        if dataname not in PREDICTION_DATASETS:
            available = ", ".join(PREDICTION_DATASETS)
            return {
                "success": False,
                "message": f"数据集 '{dataname}' 不可用。可用数据集: {available}"
            }

        # 1. 获取预测结果
        prediction_response = await pf(request=PredictionRequest(
            dataname=dataname,
            step=96,
        ))

        if prediction_response.status != 0:
            return {
                "success": False,
                "message": f"预测失败: {prediction_response.message or '未知错误'}"
            }

        prediction_data = prediction_response.data or []
        prediction_stats = calculate_stats(prediction_data)

        # 2. 获取历史数据和真实数据
        data_response = await gpdf(request=PredictionDataRequest(
            dataname=dataname,
            datatype=1,
        ))

        if data_response.status != 0:
            return {
                "success": False,
                "message": f"获取数据失败: {data_response.message or '未知错误'}"
            }

        history_data = data_response.history_data or []
        truth_data = data_response.truth_data or []

        # 提取第一个维度的数据用于绘图
        history_data_dim0 = [row[0] for row in history_data] if history_data and len(history_data) > 0 else []
        truth_data_dim0 = [row[0] for row in truth_data] if truth_data and len(truth_data) > 0 else []
        prediction_data_dim0 = [row[0] for row in prediction_data] if prediction_data and len(
            prediction_data) > 0 else []

        # 3. 生成图表
        chart_base64 = create_prediction_chart(
            history_data=history_data_dim0,
            truth_data=truth_data_dim0,
            prediction_data=prediction_data_dim0,
            dataset_name=dataname,
            step=step
        )

        result = {
            "success": True,
            "message": f"在数据集 {dataname} 上成功完成预测，预测步长 {step}",
            "history_data": history_data_dim0,  # 历史数据（维度0）
            "truth_data": truth_data_dim0,  # 真实数据（维度0）
            "data": prediction_data_dim0,  # 预测数据（维度0）
            "stats": prediction_stats,
            "chart_type": "prediction",
            "chart_base64": chart_base64
        }

        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"预测过程中发生错误: {str(e)}"
        }


async def anomaly_detection(dataname: str) -> dict:
    """
    在指定数据集上执行异常检测

    Args:
        dataname: 数据集名称 (SMD, PSM, MSL)

    Returns:
        异常检测结果的字典，包含阈值、异常分数、预测标签、统计信息和图表
    """
    try:
        if dataname not in ANOMALY_DATASETS:
            available = ", ".join(ANOMALY_DATASETS)
            return {
                "success": False,
                "message": f"数据集 '{dataname}' 不可用。可用数据集: {available}"
            }

        # 1. 获取异常检测结果
        detection_response = await adf(request=AnomalyDetectionRequest(
            dataname=dataname
        ))

        if detection_response.status != 0:
            return {
                "success": False,
                "message": f"异常检测失败: {detection_response.message or '未知错误'}"
            }

        threshold = detection_response.threshold or 0
        reconstruction_data = detection_response.reconstruction_data or []
        anomaly_score = detection_response.anomaly_score or []
        pred_labels = detection_response.pred_labels or []

        # 2. 获取原始数据
        data_response = await gadf(request=AnomalyDetectionDataRequest(
            dataname=dataname,
        ))

        if data_response.status != 0:
            return {
                "success": False,
                "message": f"获取数据失败: {data_response.message or '未知错误'}"
            }

        origin_data = data_response.origin_data or []

        # 提取第一个维度的数据用于绘图
        origin_data_dim0 = [row[0] for row in origin_data] if origin_data and len(origin_data) > 0 else []
        reconstruction_data_dim0 = [row[0] for row in reconstruction_data] if reconstruction_data and len(
            reconstruction_data) > 0 else []
        anomaly_score_dim0 = [row[0] for row in anomaly_score] if anomaly_score and len(anomaly_score) > 0 else []

        # 3. 统计异常点数量
        anomaly_count = sum(pred_labels) if pred_labels else 0
        anomaly_ratio = (anomaly_count / len(pred_labels) * 100) if pred_labels else 0

        stats = {
            "threshold": threshold,
            "anomaly_count": anomaly_count,
            "anomaly_ratio": f"{anomaly_ratio:.2f}%",
            "data_length": len(pred_labels),
            "reconstruction_stats": calculate_stats(reconstruction_data),
            "score_stats": calculate_stats(anomaly_score)
        }

        # 4. 生成图表
        chart_base64 = create_anomaly_chart(
            origin_data=origin_data_dim0,
            reconstruction_data=reconstruction_data_dim0,
            anomaly_score=anomaly_score_dim0,
            pred_labels=pred_labels,
            threshold=threshold,
            dataset_name=dataname
        )

        result = {
            "success": True,
            "message": f"在数据集 {dataname} 上成功完成异常检测",
            "threshold": threshold,
            ###############下面数据太大了，喂给大模型要吃瘪###############
            # "origin_data": origin_data_dim0,
            # "reconstruction_data": reconstruction_data_dim0,
            # "anomaly_score": anomaly_score_dim0,
            # "pred_labels": pred_labels,
            ###############
            "stats": stats,
            "chart_type": "anomaly_detection",
            "chart_base64": chart_base64
        }

        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"异常检测过程中发生错误: {str(e)}"
        }


# ====== 工具执行映射 ======
async def execute_tool(name: str, args: dict):
    if name == "predict":
        print("******************************", args)
        return await predict(**args)
    elif name == "anomaly_detection":
        return await anomaly_detection(**args)
    elif name == "get_available_datasets":
        return await get_available_datasets()
    else:
        return {"error": "未知工具"}


# ====== 核心接口 ======
@router.post("/chat")
async def chat(
        req: ChatRequest,
        current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {
                "success": False,
                "reply": "token 失效",
                "tool_used": None,
                "raw_tool_result": None
            }
    user_msg = req.message

    messages = [
        {
            "role": "system",
            "content": "你是一个时序分析专家，负责根据用户请求合理调用工具并解释结果。"
        },
        {
            "role": "user",
            "content": user_msg
        }
    ]

    try:
        # ===== 第一次请求模型 =====
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        if not response.choices:
            return {
                "success": False,
                "reply": "模型未返回有效结果",
                "tool_used": None,
                "raw_tool_result": None
            }

        msg = response.choices[0].message

        # ===== 没有调用工具，直接返回 =====
        if not getattr(msg, "tool_calls", None):
            return {
                "success": True,
                "reply": msg.content or "模型未返回内容",
                "tool_used": None,
                "raw_tool_result": None
            }

        # ===== 模型选择调用工具 =====
        tool_call = msg.tool_calls[0]
        tool_name = tool_call.function.name

        # 安全解析参数
        try:
            tool_args = json.loads(tool_call.function.arguments or "{}")
        except Exception:
            return {
                "success": False,
                "reply": f"工具参数解析失败：{tool_call.function.arguments}",
                "tool_used": tool_name,
                "raw_tool_result": None
            }

        # ===== 执行工具 =====
        try:
            tool_result = await execute_tool(tool_name, tool_args)
        except Exception as e:
            return {
                "success": False,
                "reply": f"工具执行失败：{str(e)}",
                "tool_used": tool_name,
                "raw_tool_result": None
            }

        # ===== 把工具结果喂回模型 =====
        messages.append(msg)

        # 为工具结果添加图表描述
        tool_result_with_description = tool_result.copy()
        if tool_result.get("success") and tool_result.get("chart_base64"):
            if tool_name == "predict":
                tool_result_with_description["chart_description"] = "已生成预测结果图表，包含历史数据、预测数据和真实数据的对比。"
            elif tool_name == "anomaly_detection":
                tool_result_with_description["chart_description"] = "已生成异常检测结果图表，包含原始数据、重构数据、异常分数和异常区域标识。"

        if tool_name == "anomaly_detection":
            # 删除图像 base64，避免喂给大模型（给大模型的输入过大，会总结失败）
            tool_result_with_description.pop("chart_base64", None)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result_with_description, ensure_ascii=False)
        })

        try:
            final_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )

            final_msg = final_response.choices[0].message.content
        except Exception:
            # 就算模型总结失败，也要把工具结果返回
            final_msg = "工具已成功执行，但模型总结失败，请查看工具结果。"

        return {
            "success": True,
            "reply": final_msg,
            "tool_used": tool_name,
            "raw_tool_result": tool_result
        }

    except Exception as e:
        # 最外层兜底，永远防止 500
        traceback.print_exc()
        return {
            "success": False,
            "reply": f"系统异常: {str(e)}",
            "tool_used": None,
            "raw_tool_result": None
        }