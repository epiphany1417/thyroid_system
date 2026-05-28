import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'thyroid-system-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'mysql+pymysql://root:password@localhost:3306/thyroid_system?charset=utf8mb4')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-2024')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24小时
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # LLM配置（支持OpenAI、Claude及兼容接口）
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')
    LLM_API_KEY = os.environ.get('LLM_API_KEY', 'sk-your-openai-key')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'deepseek-chat')
