# RAG based Intelligent Q&A System v0.1

一个基于 DeepSeek 的命令行知识库问答助手。把知识库文档放在 `data/knowledge.txt`，首次运行时会自动切分、向量化并写入 Milvus；之后提问时，回答会结合 Milvus 检索到的文档片段、Redis 中的对话历史和系统提示词约束生成。

欢迎通过 Issue 或 PR 指正问题，项目会持续更新。

## 功能特性

- **知识库入库**：读取 `data/knowledge.txt`，按 200 字符切块、80 字符重叠切分，经 `BAAI/bge-small-zh-v1.5` 转为 512 维向量写入 Milvus。仅在 Milvus 中不存在目标 collection 时自动触发，知识库更新后需手动重建。
- **语义检索**：向量字段使用 AUTOINDEX 索引与 COSINE 度量，每次提问召回相似度最高的 3 个片段。
- **会话级记忆**：问答记录以 JSON 逐条追加到 Redis 的 `chat:{会话 ID}` 列表，读取时通过 tiktoken 按 token 预算回溯历史，上限 2000 token。
- **提示词约束**：系统提示词规定「对话历史优先、其次知识库、两者都无则明确回复不知道」，并要求模型忽略用户问题中夹带的指令。
- **空闲保护**：连续 600 秒无输入时程序自动退出，避免进程长时间空转。

## 系统架构

```text
【知识库入库】首次运行或手动触发

data/knowledge.txt
   │ 读取
   ▼
文本切分（chunk_size=200，overlap=80）
   │
   ▼
BAAI/bge-small-zh-v1.5（512 维）
   │ 写入
   ▼
Milvus（AUTOINDEX + COSINE）


【在线问答】每次提问

用户问题
   │ 向量化（同一嵌入模型）
   ▼
Milvus 检索 Top-3 片段
   │
   ▼
拼装 Prompt：检索片段 + 对话历史 + 问题
   │
   ▼
DeepSeek 生成回答
   │
   ▼
写入 Redis（chat:{会话 ID}）
```

## 技术栈

| 模块 | 选型 | 版本 | 职责 |
|---|---|---|---|
| 大模型 | DeepSeek（OpenAI 兼容接口） | - | 生成最终回答，模型名在 `services/rag.py` 中配置 |
| 编排框架 | LangChain | 1.4.7 | 消息结构、Agent 初始化与提示词注入 |
| 文本切分 | langchain_text_splitters | 1.1.3 | 按分隔符递归切块，块大小 200、重叠 80 |
| 嵌入模型 | BAAI/bge-small-zh-v1.5 | - | 本地推理，将文本转为 512 维向量 |
| 向量数据库 | Milvus（pymilvus 客户端） | 3.0.2 | 存储向量并执行相似度检索 |
| 会话记忆 | Redis（redis-py 客户端） | 8.1.0 | 存储会话级对话记录 |
| 上下文计量 | tiktoken | 0.14.0 | 统计历史消息 token，限制在 2000 以内 |
| 运行环境 | Python | 3.14 | - |

完整依赖版本见 `requirements.txt`。

## 快速开始

### 1. 环境要求

- Python 3.14
- Docker Desktop（用于运行 Milvus；已部署 Milvus 服务可跳过）
- Redis 服务（本地安装或 Docker 运行均可）

### 2. 获取代码并安装依赖

```powershell
git clone <your-repo-url>
cd RAG_assistant

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3. 配置环境变量

```powershell
Copy-Item .env.example .env
```

打开 `.env`，至少填写 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL` 与 `MILVUS_BASE_URL`，字段说明见下方「配置说明」。

> `.env` 已在 `.gitignore` 中忽略，请勿提交密钥。

### 4. 启动依赖服务

启动 Milvus（镜像版本与本项目使用的 pymilvus 3.0.2 客户端保持一致）：

```powershell
docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 -p 2379:2379 -v ${PWD}/volumes/milvus:/var/lib/milvus milvusdb/milvus:v3.0.2 standalone
```

确认容器与端口状态：

```powershell
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
```

Redis 若使用 Docker 启动：

```powershell
docker run -d --name redis -p 6379:6379 redis
```

> Redis 连接地址固定在 `config.py` 中（`localhost:6379`，db 0），不支持通过 `.env` 修改。若 Redis 部署在其他地址，需直接修改 `config.py`。

### 5. 运行程序

```powershell
python main.py
```

首次运行时若 Milvus 中不存在 `docs` collection，程序会自动读取 `data/knowledge.txt` 并完成入库。

> 必须在项目根目录执行，因为知识库路径 `data/knowledge.txt` 是相对路径。

输入 `exit` 或 `退出` 结束对话。

### 6. 更新知识库

修改 `data/knowledge.txt` 后需手动重建 collection：

```powershell
python -m services.ingest
```

重建时会先删除旧 collection 再创建，已有向量数据会被清空。

### 7. 使用示例

```text
请输入您的问题: 什么是 RAG
RAG 即检索增强生成：先从知识库中检索与问题相关的片段，再把这些片段作为上下文交给大模型生成回答。（内容示意）

请输入您的问题: exit
祝您生活愉快，再见！
```

## 配置说明

| 变量 | 必填 | 说明 | 示例 |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | 是 | 大模型接口密钥 | `sk-...` |
| `DEEPSEEK_BASE_URL` | 是 | OpenAI 兼容接口地址 | `https://<服务商地址>/v1` |
| `MILVUS_BASE_URL` | 是 | Milvus 连接地址 | `http://localhost:19530` |

以下参数为代码内固定值，修改需直接改源码：

| 参数 | 值 | 位置 |
|---|---|---|
| 数据库名 / collection 名 | `rag_tutorial` / `docs` | `config.py` |
| 文本切块大小 / 重叠 | 200 / 80 | `utils/document_read.py` |
| 检索返回条数 | 3 | `database/Milvus/Milvus_client.py` |
| 记忆 token 上限 | 2000 | `services/memory.py` |
| 空闲超时 | 600 秒 | `main.py` |
| 模型名 | `deepseek-flash` | `services/rag.py` |

## 目录结构

```text
RAG_assistant/
├── main.py                    # 程序入口：空闲计时与对话循环
├── config.py                  # 读取 .env 并集中定义配置常量
├── requirements.txt           # 依赖清单
├── .env.example               # 环境变量模板
├── data/
│   └── knowledge.txt          # 知识库源文件
├── database/
│   └── Milvus/
│       └── Milvus_client.py   # Milvus 连接、建表与检索
├── models/
│   └── embedding_model.py     # 本地嵌入模型封装
├── services/
│   ├── ingest.py              # 知识库切分与入库
│   ├── rag.py                 # 模型初始化、Agent 与检索
│   ├── generate_answer.py     # 组装 Prompt 并生成回答
│   └── memory.py              # Redis 会话记忆读写
└── utils/
    └── document_read.py       # 文档读取与文本切分
```

## 核心实现要点

- **切分策略**：`RecursiveCharacterTextSplitter` 优先按 `==============================` 分隔符切块，其次按空行、换行、句号、空格；块大小 200 字符、重叠 80 字符，保证相邻块语义衔接。
- **向量化**：入库与查询共用 `BAAI/bge-small-zh-v1.5`，输出 512 维向量，模型在本地推理。
- **索引与检索**：collection schema 含 `id`、`vector`、`text`、`source`、`chunk_id` 五个字段，向量字段建立 AUTOINDEX 索引并使用 COSINE 度量，默认返回 Top-3。
- **生成流程**：检索片段与 Redis 历史消息一并拼入 Prompt，交由 LangChain Agent 调用 DeepSeek 生成回答。
- **记忆管理**：读取历史时从最新消息向前累加 token 数，超过 2000 即停止回溯，超出部分保留在 Redis 但不参与生成。
- **注入防护**：系统提示词要求将用户问题视为数据，其中的代码或指令一律忽略。

## 已知限制

1. 知识库仅支持单个 `txt` 文件，暂不支持 PDF、Word 或多文件批量导入。
2. 会话为短期记忆：会话 ID 每次启动重新生成，不跨进程延续。正常输入 `exit` 退出时会清理 Redis 记录，空闲超时退出时进程直接终止，残留记录不会被清理。
3. Redis 中的会话记录未设置过期时间，长期运行会累积无用数据。
4. 更新知识库必须手动重建 collection，且重建会清空已有向量数据。
5. 检索片段直接拼入 Prompt，未做重排序与来源引用标注。
6. 当前为命令行交互，未提供 Web 界面或 HTTP 接口。
7. Milvus 目前在 Windows 环境的 Docker 中运行，尚未迁移至 Linux 部署。

## Roadmap

- [ ] 支持 PDF、Word、Markdown 等多格式与多文件知识库
- [ ] 为 Redis 会话记录增加 TTL，并清理超时退出产生的残留数据
- [ ] 引入重排序模型（Rerank）提升召回质量
- [ ] 迁移 Milvus 至 Linux 环境部署
- [ ] 提供 Web UI 或 HTTP API
- [ ] 补充单元测试与入库脚本的幂等处理

## License

MIT
