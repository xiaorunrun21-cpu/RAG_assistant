from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import KNOWLEDGE_FILE
#加载数据
def document_read():
    loader = TextLoader(file_path =KNOWLEDGE_FILE,encoding = "utf-8")
    documents =loader.load()

    #按照规则切分数据


    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 200,
        chunk_overlap = 80,
        separators = [
            "==============================",
            "\n\n",
            "\n",
            "。",
            " ",
            ""
        ]
    )

    chunks =splitter.split_documents(documents)

    print(f"文档共切分为{len(chunks)}")

    return chunks


