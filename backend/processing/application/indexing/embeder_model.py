from langchain_openai import OpenAIEmbeddings


def load_embedding_model():
    print("🚀 Loading embedding model...")
    return OpenAIEmbeddings(model="text-embedding-3-large")
