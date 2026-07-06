# Skill: Advanced Vector Databases (Pinecone & Weaviate)

## Purpose
To build production-ready RAG, semantic search, and similarity systems with modern vector databases.

## When to Use
- For building semantic search over large document collections
- When implementing RAG (Retrieval-Augmented Generation)
- For recommendation systems using embeddings
- When building question-answering systems
- For similarity search (images, text, audio)

## Procedure

### 1. Pinecone Setup & Indexing
Get started with Pinecone.

```python
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index
index_name = "rag-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # text-embedding-3-small
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Connect to index
index = pc.Index(index_name)

# Create embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Sample documents
documents = [
    Document(page_content="LangGraph is a library for building stateful agents.", metadata={"source": "doc1", "category": "ai"}),
    Document(page_content="Vector databases store embeddings for similarity search.", metadata={"source": "doc2", "category": "database"}),
    Document(page_content="RAG combines retrieval with LLM generation.", metadata={"source": "doc3", "category": "ai"}),
    Document(page_content="Pinecone is a serverless vector database.", metadata={"source": "doc4", "category": "database"})
]

# Add to vector store
vector_store = PineconeVectorStore.from_documents(
    documents=documents,
    embedding=embeddings,
    index_name=index_name,
    namespace="production"
)
```

### 2. Advanced Retrieval with Pinecone
Implement hybrid search and filtering.

```python
# Semantic search
results = vector_store.similarity_search(
    "What is LangGraph?",
    k=3,
    filter={"category": "ai"}  # Metadata filtering
)

# Similarity search with score
results_with_scores = vector_store.similarity_search_with_score(
    "Tell me about vector databases",
    k=3
)

# Hybrid search (dense + sparse)
# Use Pinecone's hybrid search with BM25
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone_text.sparse import BM25Encoder

bm25_encoder = BM25Encoder()
bm25_encoder.fit([d.page_content for d in documents])

hybrid_retriever = PineconeHybridSearchRetriever(
    embeddings=embeddings,
    sparse_encoder=bm25_encoder,
    index=index,
    namespace="production",
    top_k=3
)

hybrid_results = hybrid_retriever.invoke("What is RAG?")
```

### 3. Weaviate Setup
Use Weaviate for self-hosted or managed vector search.

```python
import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType, Configure

# Connect to Weaviate
client = weaviate.connect_to_wcs(
    cluster_url=os.getenv("WEAVIATE_CLUSTER_URL"),
    auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
    }
)

# Create collection
if not client.collections.exists("Document"):
    collection = client.collections.create(
        name="Document",
        vectorizer_config=Configure.Vectorizer.text2vec_openai(model="text-embedding-3-small"),
        generative_config=Configure.Generative.openai(model="gpt-4o"),
        properties=[
            Property(name="content", data_type=DataType.TEXT),
            Property(name="source", data_type=DataType.TEXT),
            Property(name="category", data_type=DataType.TEXT),
            Property(name="created_at", data_type=DataType.DATE)
        ]
    )
else:
    collection = client.collections.get("Document")

# Add objects
with collection.batch.dynamic() as batch:
    for doc in documents:
        batch.add_object(
            properties={
                "content": doc.page_content,
                "source": doc.metadata["source"],
                "category": doc.metadata["category"],
                "created_at": "2024-01-01T00:00:00Z"
            }
        )
```

### 4. Weaviate Generative Search (RAG)
Built-in generative search with Weaviate.

```python
# Basic search
response = collection.query.near_text(
    query="What is LangGraph?",
    limit=3,
    filters=wvc.query.Filter.by_property("category").equal("ai"),
    return_properties=["content", "source"]
)

# Generative search (RAG)
generative_response = collection.generate.near_text(
    query="Explain LangGraph in simple terms",
    limit=3,
    single_prompt="Summarize this content: {content}"
)

for obj in generative_response.objects:
    print(f"Source: {obj.properties['source']}")
    print(f"Generated: {obj.generated}")
    print("---")

# Grouped task
grouped_response = collection.generate.near_text(
    query="Tell me about vector databases",
    limit=5,
    grouped_task="Write a comprehensive summary of all these documents"
)

print("Grouped Summary:", grouped_response.generated)
```

### 5. Production Best Practices
Optimize vector DB for production.

```python
# Pinecone optimization
# 1. Use namespaces for isolation
vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    namespace="tenant-123"
)

# 2. Batch operations
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

split_docs = text_splitter.split_documents(documents)

# Add in batches
for i in range(0, len(split_docs), 100):
    batch = split_docs[i:i+100]
    vector_store.add_documents(batch)

# 3. Weaviate: Use tenant isolation
multi_tenancy_config = Configure.multi_tenancy(enabled=True)

# 4. Monitor usage
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
```

## Best Practices
- **Embedding Model**: Choose appropriate embedding model (dimensions, cost)
- **Chunking**: Use good text splitting strategy (chunk size, overlap)
- **Metadata**: Add rich metadata for filtering
- **Indexing**: Use batch operations for large datasets
- **Hybrid Search**: Combine vector + keyword search for better results
- **Namespaces/Tenants**: Isolate data for multi-tenant apps
- **Monitoring**: Monitor query latency and cost
- **Caching**: Cache frequent queries to reduce cost
