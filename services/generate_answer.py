from services.rag import retrieve
from services.rag import agent
from services.memory import get_memory,add_memory


def generate_answer(conversation_id:str,question :str)->str:
    """根据问的问题，生成合适的答案"""
    try:

        hits = retrieve(question)

        #创建一个空容器，用于存储检索到的知识库文档内容
        context_blocks =[]

        for hit in hits:
            text  = hit["entity"].get("text")   
            context_blocks.append(text)

        context = "\n\n".join(context_blocks)
        history_messages = get_memory(conversation_id)
        user_prompt = f"""
        问题:
            {question}
        知识库文档:
            {context}
    """
        result = agent.invoke({
            "messages" :[*history_messages,{"role":"user","content":user_prompt}]
        })

        final_msg = result["messages"][-1]

        add_memory(conversation_id,question, final_msg.content)
        return final_msg.content
    except Exception as e:
        return f"抱歉,程序运行时出错:{e}"
        
