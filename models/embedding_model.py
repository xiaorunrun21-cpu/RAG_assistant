#Embed模型初始化
from langchain.embeddings import init_embeddings
from config import EMBED_MODEL_NAME

#初始化embedding 模型
embedding_model = init_embeddings(
    model = EMBED_MODEL_NAME,
    provider  = "huggingface"
)

def embed_question(question:str)->list:
    """
    将question向量化
    """
    question_vectors = embedding_model.embed_query(question)
    return question_vectors