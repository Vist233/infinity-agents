import os
import uuid

# 生成全局唯一的 secret_key
SECRET_KEY = os.environ.get("APP_SECRET_KEY", str(uuid.uuid4()))

# 数据库目录配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在目录
DATABASE_DIR = os.path.join(BASE_DIR, "Database")

# API Key 配置
API_KEY = os.environ.get("YI_API_KEY", "your API key here")

# 确保目录存在
os.makedirs(DATABASE_DIR, exist_ok=True)
