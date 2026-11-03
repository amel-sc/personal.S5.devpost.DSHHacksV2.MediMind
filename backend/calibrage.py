import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
collection = client.get_collection(name="medimind_knowledge", embedding_function=ef)

bien_etre = [
    "Je stresse pour mes examens", "Je n'arrive pas à dormir",
    "Comment faire un exercice de respiration ?", "Je me sens seul depuis la rentrée",
    "ça va pas trop", "je suis crevé", "je mange plus rien depuis 2 semaines",
    "j'ai plus d'argent pour finir le mois", "je doute de ma filière",
    "je passe ma vie sur TikTok", "j'ai l'impression d'être nul comparé aux autres",
    "je repousse tout au dernier moment", "I feel so anxious before exams",
]
hors_sujet = [
    "Comment cuisiner du riz ?", "Qui a gagné la Coupe du monde ?",
    "Corrige mon code Python", "Quelle est la capitale du Japon ?",
    "Recette de gâteau au chocolat", "Explique la photosynthèse",
    "Quel temps fera-t-il demain ?", "Traduis ce texte en anglais",
]

def tester(questions, label):
    print(f"\n=== {label} ===")
    distances = []
    for q in questions:
        r = collection.query(query_texts=[q], n_results=1)
        d = r["distances"][0][0]
        theme = r["metadatas"][0][0].get("theme", r["metadatas"][0][0]["source"])
        distances.append(d)
        print(f"{d:.3f}  {q:<50} → {theme}")
    return distances

d_ok = tester(bien_etre, "BIEN-ÊTRE")
d_ko = tester(hors_sujet, "HORS SUJET")

print(f"\nBien-être max : {max(d_ok):.3f}")
print(f"Hors sujet min : {min(d_ko):.3f}")
if max(d_ok) < min(d_ko):
    print(f"Seuil suggéré : {(max(d_ok) + min(d_ko)) / 2:.2f}")
else:
    print("⚠️ Les groupes se chevauchent : le classifieur gérera les cas douteux.")
