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
