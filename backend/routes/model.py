# 做预测和异常监测的接口
from fastapi import APIRouter, Depends, HTTPException
from entitymodels.schemas import PredictionResponse, PredictionRequest, PredictionDataResponse, PredictionDataRequest, AnomalyDetectionResponse, AnomalyDetectionRequest, AnomalyDetectionDataResponse, AnomalyDetectionDataRequest
from algorithm.model.prediction.test import prediction, get_origin_data
from algorithm.model.anomalydetection.test import get_anomaly_data, anomaly_detection
from entitymodels.entities import User
from routes.auth import get_current_user

router = APIRouter(prefix="/api", tags=["model"])


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
        获取数据集信息

        Args:
            request: 包含数据名称和类型
                dataname: 数据集名称 (ETTm2, Ettm1 默认值=ETTm2)
                step: 预测步长（默认值=96）
    """
    if not current_user:
        return PredictionResponse(
            status=-1,
            message="token 无效",
            data=[],
        )
    # step = request.step
    # print(step)
    prediction_y = prediction(request.dataname, request.step)

    return PredictionResponse(
        status=0,
        message="预测成功",
        data=prediction_y,
    )

@router.post("/get_prediction_data", response_model=PredictionDataResponse)
async def get_prediction_data(
        request: PredictionDataRequest,
        current_user: User = Depends(get_current_user)
):
    """
        获取数据集信息

        Args:
            request: 包含数据名称和类型
                dataname: 数据集名称 (ETTm2, Ettm1 默认值=ETTm2)
                datatype: 数据集类型 (默认是1 预测任务数据集 2是异常检测任务数据集)
    """
    if not current_user:
        return PredictionDataResponse(
            status=-1,
            message="token 无效",
            history_data=[],  # 包含history_x和truth_y
            truth_data=[],
        )

    if request.datatype == 1:
        history_x, truth_y = get_origin_data(request.dataname)

    return PredictionDataResponse (
        status=0,
        message="获取数据成功",
        history_data=history_x,  # 包含history_x和truth_y
        truth_data = truth_y,
    )


@router.post("/anomalydetection", response_model=AnomalyDetectionResponse)
async def anomalydetection(
    request: AnomalyDetectionRequest,
    current_user: User = Depends(get_current_user)
):
    """
        获取数据集信息

        Args:
            request: 包含数据名称和类型
                dataname: 数据集名称
    """
    if not current_user:
        return AnomalyDetectionResponse(
            status=-1,
            message="token 无效",
            threshold=0,
            reconstruction_data=[],
            anomaly_score=[],
            pred_labels=[],
        )
    # step = request.step
    # print(step)
    threshold, reconstruction_data, anomaly_score, pred_labels = anomaly_detection(request.dataname)
    '''
    threshold: float
    reconstruction_data: List[List[float]]
    anomaly_score: List[List[float]]
    pred_labels: List[int]
    '''
    return AnomalyDetectionResponse(
        status=0,
        message="预测成功",
        threshold=threshold,
        reconstruction_data=reconstruction_data,
        anomaly_score = anomaly_score,
        pred_labels = pred_labels,
    )

@router.post("/get_anomalydetection_data", response_model=AnomalyDetectionDataResponse)
async def get_anomalydetection_data(
        request: AnomalyDetectionDataRequest,
        current_user: User = Depends(get_current_user)
):
    """
        获取数据集信息

        Args:
            request: 包含数据名称和类型
                dataname: 数据集名称
    """
    if not current_user:
        return AnomalyDetectionDataResponse(
            status=-1,
            message="token 无效",
            origin_data=[],
        )

    origin_data = get_anomaly_data(request.dataname)
    '''
    origin_data: List[List[float]]
    '''
    return AnomalyDetectionDataResponse (
        status=0,
        message="获取数据成功",
        origin_data=origin_data,
    )