from langchain_core.messages import HumanMessage,AIMessage
import redis
import json
from config import REDIS_HOST,REDIS_PORT,REDIS_DB
import tiktoken

redis_client = redis.Redis(host = REDIS_HOST,port = REDIS_PORT,  db = REDIS_DB,
                           decode_responses = True)

encoder = tiktoken.encoding_for_model("gpt-4")


def count_tokens(text:str)->int:
    """计算文本的token的数量"""
    tokens = len(encoder.encode(text))
    return tokens

def add_memory(conversation_id:str,question:str,answer:str):
    """添加记忆"""
    try:
        key = f"chat:{conversation_id}"
        redis_client.rpush(key,json.dumps({"role":"user","content":question}))
        redis_client.rpush(key,json.dumps({"role":"assistant","content":answer}))
    except Exception as e:
        print(f"抱歉,程序运行时出错:{e}")

    
def get_memory(conversation_id:str,max_tokens:int = 2000)->list:
    """读取记忆,保证总token不超过max_tokens"""
    try:
        key = f"chat:{conversation_id}"
        items = redis_client.lrange(key,0,-1)
        messages=[]
        for item in items:
            data = json.loads(item)
            if data["role"] == "user":
                messages.append(HumanMessage(content = data["content"]))
            elif data["role"] == "assistant":
                messages.append(AIMessage(content = data["content"]))
        result = []
        total_tokens = 0
        for msg in reversed(messages):
            msg_tokens = count_tokens(msg.content)
            if total_tokens +msg_tokens > max_tokens:
                break
            result.insert(0,msg)
            total_tokens +=msg_tokens
        return result
    except Exception as e:
        print(f"抱歉,程序运行时出错:{e}") 
        return []

def clear_memory(conversation_id:str):
    """清洗无用记忆(关闭会话窗口后，会话记忆会自动清除)"""
    try:
        key = f"chat:{conversation_id}"
        redis_client.delete(key)
    except Exception as e:
        print(f"抱歉,程序运行时出错:{e}")
