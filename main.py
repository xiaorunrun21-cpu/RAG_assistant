from services.generate_answer import generate_answer
from database.Milvus.Milvus_client import client
from config import COLLECTION_NAME
import os
import threading
import uuid
from services.memory import clear_memory


IDLE_TIMEOUT = 60*10


def _timeout_exit():
    """当用户超过10分钟没有进行对话时,程序自动退出"""
    
    print("您已超过十分钟没有进行对话，程序将自动退出。")
    os._exit(0)

if not client.has_collection(COLLECTION_NAME):
    from services.ingest import ingest_knowledge
    ingest_knowledge()

timer = threading.Timer(IDLE_TIMEOUT, _timeout_exit)
timer.daemon = True
timer.start()


current_id = str(uuid.uuid4())[:6]

# 对话窗口循环
while True:
    timer.cancel()
    timer = threading.Timer(IDLE_TIMEOUT, _timeout_exit)
    timer.daemon = True
    timer.start()

    question = input("请输入您的问题:")
    
    if question == "exit" or question == "退出":
        print("祝您生活愉快，再见！")
        clear_memory(current_id)
        break
    try:
        answer = generate_answer(current_id,question)
        print(answer)
    except Exception as e:
        print(f"抱歉,程序运行时出错:{e}")