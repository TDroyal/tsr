# 时序项目启动！！！

## backend
启动命令
```shell
conda create -n tsr python=3.11 # 创建conda环境
conda activate tsr # 使用该环境
pip install -r requirements.txt # 下载相关包
python run.py # 启动服务命令
```

注意：
```python
# routes/chat.py下面的DEEPSEEK_API_KEY 需要改为自己的llm token。
DEEPSEEK_API_KEY = "my token"
```

## frontend
vue3 项目 npm管理依赖
```shell
npm install
npm run serve
```

## 首页
![home](resources/home.png?raw=true "home")

## 预测页面
![forcast](resources/forcast.png?raw=true "forcast")

## 异常检测页面
![anomaly detection](resources/anomaly_detection.png?raw=true "anomaly detection")

## 智能问题助手页面
![QA](resources/QA.png?raw=true "QA")

## 时序助手使用示例
![QA example](resources/QA_example.png?raw=true "QA example")
