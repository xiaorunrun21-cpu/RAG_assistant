"""链接Milvus数据库"""

from pymilvus import MilvusClient
import config
from pymilvus import DataType

milvus_url = config.MILVUS_BASE_URL
db_name=config.DB_NAME
collection_name=config.COLLECTION_NAME
embed_dim = config.EMBED_DIM


#初始化Milvus数据库
client = MilvusClient(milvus_url)

#列举出来所有的数据库，如果不存在就创建一个新的数据库
existed_database = client.list_databases()
if db_name not in existed_database:
    client.create_database(db_name)

client.use_database(db_name)


def create_collection():
    """创建collection """

    #如果collection存在，就删除它,再创建
    if client.has_collection(collection_name):
        client.drop_collection(collection_name)

    #创建collection的schema
    schema =MilvusClient.create_schema(
        auto_id = False,
        enable_dynamic_field = False
    )

    schema.add_field(
        field_name = "id",
        datatype = DataType.INT64,
        is_primary =True
    )
    schema.add_field(
        field_name = "vector",
        datatype = DataType.FLOAT_VECTOR,
        dim = embed_dim
    )

    schema.add_field(
        field_name = "text",
        datatype = DataType.VARCHAR,
        max_length = 1024
    )

    schema.add_field(
        field_name = "source",
        datatype = DataType.VARCHAR,
        max_length = 1024
    )

    schema.add_field(
        field_name = "chunk_id",
        datatype = DataType.INT64,
    )

    #创建collection的索引参数
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name = "vector",
        index_type = "AUTOINDEX",
        metric_type = "COSINE"
    )

    client.create_collection(
        collection_name = collection_name,
        schema = schema,
        index_params = index_params
    )

def search_similar(vectors:list,limit = 3)->list:
    """根据向量在Milvus数据库中检索相似的向量"""
    result = client.search(
        collection_name = collection_name,
        data = [vectors],
        limit = limit,
        output_fields = ["id","text","source","chunk_id"]
    )
    return result[0]