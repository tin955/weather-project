import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "rag" / "knowledge"
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


def index_documents():
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    documents = []
    for file in os.listdir(KNOWLEDGE_DIR):
        file_path = os.path.join(KNOWLEDGE_DIR, file)
        if file.endswith(('.txt', '.md')):
            docs = TextLoader(file_path, encoding='utf-8').load()
            documents.extend(docs)
            print(f"✅ 加载: {file}")

    if not documents:
        print("⚠️ 知识库为空")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embeddings = CustomEmbeddings()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR)
    )
    vector_store.persist()
    print(f"✅ 索引完成，共 {len(chunks)} 个片段")


if __name__ == "__main__":
    index_documents()