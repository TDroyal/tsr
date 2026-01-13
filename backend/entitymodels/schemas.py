from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np

class LoginRequest(BaseModel):
    username: str
    password: str

# 这些都是一个个的json
class LoginResponse(BaseModel):
    status: int
    message: str
    token: str


class TokenData(BaseModel):
    username: Optional[str] = None
    usertype: Optional[str] = None


# class UserBase(BaseModel):
#     username: str
#     email: str
#     usertype: str
#     status: bool
#
#
# class User(UserBase):
#     id: int
#
#     class Config:
#         from_attributes = True


class JWTPayload(BaseModel):
    user_id: int
    username: str
    usertype: int
    exp: int


class DataRequest(BaseModel):
    dataname: str
    datatype: int  # 1: 训练数据, 2: 测试数据, 3: 标签数据
    # datatask: int  # 1: 预测任务数据集 2：异常检测任务数据集

class DataStatistic(BaseModel):
    data_length: int
    data_dimension: int
    data_max: float
    data_min: float
    data_mean: float
    data_std: float
    data_shape: List[int]

class DataResponse(BaseModel):
    status: int
    message: str
    statistic: DataStatistic
    sample_data: List[List[float]]  # 前1000行数据用于展示
    data_info: Dict[str, Any]

class PredictionResponse(BaseModel):
    status: int
    message: str
    data: List[List[float]]
class PredictionRequest(BaseModel):
    dataname: str = "ETTm2" # 默认值=ETTm2
    step: int = 96 # 默认值96
class PredictionDataResponse(BaseModel):
    status: int
    message: str
    history_data: List[List[float]]
    truth_data: List[List[float]]
class PredictionDataRequest(BaseModel):
    dataname: str = "ETTm2"  # 默认值=ETTm2
    datatype: int = 1  # 1表示是预测数据集 2表示是异常检测数据集


class AnomalyDetectionResponse(BaseModel):
    status: int
    message: str
    threshold: float
    reconstruction_data: List[List[float]]
    anomaly_score: List[List[float]]
    pred_labels: List[int]
    '''
    
    '''
class AnomalyDetectionRequest(BaseModel):
    dataname: str
class AnomalyDetectionDataResponse(BaseModel):
    status: int
    message: str
    origin_data: List[List[float]]
class AnomalyDetectionDataRequest(BaseModel):
    dataname: str