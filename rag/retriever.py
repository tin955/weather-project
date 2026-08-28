from pathlib import Path
from langchain_community.vectorstores import Chroma
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
VECTOR_DB_DIR = PROJECT_ROOT / "rag" / "vector_db"
MODEL_PATH = "D:/Documents/Desktop/models/paraphrase-multilingual-MiniLM-L12-v2"

# 加载模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModel.from_pretrained(MODEL_PATH)


def encode_texts(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings.tolist()


class CustomEmbeddings:
    def embed_documents(self, texts):
        return encode_texts(texts)

    def embed_query(self, text):
        return encode_texts([text])[0]


def get_retriever(top_k=3):
    embeddings = CustomEmbeddings()
    vector_store = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings
    )
    # 新版 LangChain 使用 as_retriever() 返回的对象
    return vector_store.as_retriever(search_kwargs={"k": top_k})


def retrieve_context(query, top_k=3):
    retriever = get_retriever(top_k)
    # 新版使用 invoke 方法
    docs = retriever.invoke(query)
    return [doc.page_content for doc in docs]


if __name__ == "__main__":
    result = retrieve_context("CSP")
    print("检索结果：")
    for i, r in enumerate(result):
        print(f"{i + 1}. {r[:200]}...")