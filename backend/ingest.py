
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialiser ChromaDB
client = chromadb.PersistentClient(
    path="./chroma_db"
)

# 2. Choisir le modèle d'embeddings
embedding_function = (
    embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
)

# 3. Créer ou récupérer la collection
collection = client.get_or_create_collection(
    name="medimind_knowledge",
    embedding_function=embedding_function
)


def split_text(text, chunk_size=1000, overlap=150):
    """Découpe un document en petits morceaux."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        # slicing du text
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# 4. Lire les fichiers
knowledge_dir = Path("./knowledge")

for file_path in knowledge_dir.glob("*.txt"):

    text = file_path.read_text(encoding="utf-8")
    chunks = split_text(text)

    # 5. Enregistrer les morceaux
    ids = [
        f"{file_path.stem}_{i}"
        for i in range(len(chunks))
    ]

    # Spécifier la source de chaque chunks
    metadatas = [
        {"source": file_path.name}
        for _ in chunks
    ]

    # update or insert : mettre à jour ou insérer le document
    collection.upsert(
        ids=ids,
        documents=chunks,
        metadatas=metadatas
    )

    print(f"{file_path.name} : {len(chunks)} morceaux enregistrés.")

print("Base de connaissances créée !")
