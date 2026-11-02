from dotenv import load_dotenv
import os

load_dotenv(override = True)


#Deepseek模型配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")


#Qwen模型配置
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")


#Milvus数据库基本配置
MILVUS_BASE_URL = os.getenv("MILVUS_BASE_URL")
DB_NAME = "rag_tutorial"
COLLECTION_NAME = "docs"
KNOWLEDGE_FILE = "data/knowledge.txt"


#Embedding模型配置
EMBED_MODEL_NAME = "BAAI/bge-small-zh-v1.5"
EMBED_DIM = 512

#Redis数据库配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

