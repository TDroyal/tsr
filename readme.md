# 时序项目启动！！！

## backend
### 启动命令
```shell
conda create -n tsr python=3.11 # 创建conda环境
conda activate tsr # 使用该环境
pip install -r requirements.txt # 下载相关包
python run.py # 启动服务命令
```

### 注意：
```python
# backend/routes/chat.py下面的DEEPSEEK_API_KEY 需要改为自己的llm token。
DEEPSEEK_API_KEY = "my token"

# 修改mysql的配置 账号密码等 在backend/dao/database.py下面
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://your-username:your-password@127.0.0.1/your-database-name"
```
### 模型下载：
你可以在[Google Drive](https://drive.google.com/drive/folders/1UlcATyAnMxuVdjWuROoopvEteEre_aOo)下载项目必须的相关算法，下载并解压命名为`algorithm`，然后将这整个文件夹放在`backend`目录下，即`backend/algorithm`。


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
