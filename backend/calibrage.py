import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
collection = client.get_collection(name="medimind_knowledge", embedding_function=ef)

# ---------------------------------------------------------------------------
# Questions de test
# (question, mots-clés attendus dans le NOM DU FICHIER retrouvé)
# None = message vague : aucun thème précis attendu, exclu du calcul du seuil
# ---------------------------------------------------------------------------
TESTS = {
    "fr": {
        "bien_etre": [
            ("Je stresse pour mes examens", ["stress", "anxiete"]),
            ("Je n'arrive pas à dormir", ["sommeil"]),
            ("Comment faire un exercice de respiration ?", ["exercice", "respiration", "anxiete", "stress"]),
            ("Je me sens seul depuis la rentrée", ["isolement", "adaptation"]),
            ("ça va pas trop", None),
            ("je suis crevé", None),
            ("je mange plus rien depuis 2 semaines", ["alimentaire", "depression"]),
            ("j'ai plus d'argent pour finir le mois", ["financ"]),
            ("je doute de ma filière", ["orientation"]),
            ("je passe ma vie sur TikTok", ["addiction"]),
            ("j'ai l'impression d'être nul comparé aux autres", ["confiance", "imposteur"]),
            ("je repousse tout au dernier moment", ["procrastination"]),
            ("je n'arrive pas à me concentrer quand je révise", ["concentration"]),
            ("je suis épuisé, je n'ai plus envie d'étudier", ["burnout", "epuisement", "depression"]),
            ("je me dispute tout le temps avec mes parents", ["relation"]),
            ("j'ai peur de parler devant la classe", ["sociale"]),
        ],
        "hors_sujet": [
            "Comment cuisiner du riz ?", "Qui a gagné la Coupe du monde ?",
            "Corrige mon code Python", "Quelle est la capitale du Japon ?",
            "Recette de gâteau au chocolat", "Explique la photosynthèse",
            "Quel temps fera-t-il demain ?", "Traduis ce texte en anglais",
            "Comment réparer mon vélo ?", "Écris une dissertation sur Voltaire",
        ],
    },
    "en": {
        "bien_etre": [
            ("I'm so stressed about my exams", ["stress", "anxiete"]),
            ("I can't sleep", ["sommeil"]),
            ("How do I do a breathing exercise?", ["exercice", "respiration", "anxiete", "stress"]),
            ("I've felt lonely since I moved here", ["isolement", "adaptation"]),
            ("not doing great", None),
            ("I'm so tired", None),
            ("I haven't been eating for two weeks", ["alimentaire", "depression"]),
            ("I'm out of money until the end of the month", ["financ"]),
            ("I'm not sure I chose the right major", ["orientation"]),
            ("I spend my whole life on TikTok", ["addiction"]),
            ("I feel stupid compared to my classmates", ["confiance", "imposteur"]),
            ("I keep putting everything off until the last minute", ["procrastination"]),
            ("I can't focus when I study", ["concentration"]),
            ("I'm exhausted and I don't want to study anymore", ["burnout", "epuisement", "depression"]),
            ("I keep fighting with my parents", ["relation"]),
            ("I'm scared of speaking in front of the class", ["sociale"]),
        ],
        "hors_sujet": [
            "How do I cook rice?", "Who won the World Cup?",
            "Fix my Python code", "What is the capital of Japan?",
            "Chocolate cake recipe", "Explain photosynthesis",
            "What's the weather tomorrow?", "Translate this text into French",
            "How do I fix my bike?", "Write an essay about Shakespeare",
        ],
    },
}


def verifier_index():
    """Affiche le nombre de fichiers indexés par langue."""
    metas = collection.get(include=["metadatas"])["metadatas"]
    par_langue = {}
    for m in metas:
        par_langue.setdefault(m.get("langue", "?"), set()).add(m["source"])

    print("=== INDEX ===")
    for langue, sources in sorted(par_langue.items()):
        print(f"[{langue}] {len(sources)} fichiers")
    if "?" in par_langue:
        print("⚠️ Des documents n'ont pas de métadonnée 'langue' : "
              "supprimez ./chroma_db et réindexez.")
    return par_langue


def tester(langue, questions, hors_sujet=False):
    """Interroge ChromaDB et renvoie une liste de (distance, statut)."""
    label = "HORS SUJET" if hors_sujet else "BIEN-ÊTRE"
    print(f"\n=== {label} ({langue.upper()}) ===")
    resultats = []

    for item in questions:
        q, attendus = (item, None) if hors_sujet else item

        r = collection.query(query_texts=[q], n_results=1, where={"langue": langue})
        d = r["distances"][0][0]
        source = r["metadatas"][0][0]["source"]

        if hors_sujet:
            statut, symbole = "hors_sujet", "  "
        elif attendus is None:
            statut, symbole = "vague", "· "
        elif any(mot in source.lower() for mot in attendus):
            statut, symbole = "ok", "✅"
        else:
            statut, symbole = "faux", "❌"

        print(f"{symbole} {d:.3f}  {q:<52} → {source}")
        resultats.append((d, statut))

    return resultats


def suggerer_seuil(langue, resultats):
    """
    Le seuil se place entre :
    - le dernier BON document (thème correct),
    - et le premier cas MAUVAIS (question hors sujet ou mauvais thème).
    """
    bons = [d for d, s in resultats if s == "ok"]
    mauvais = [d for d, s in resultats if s in ("faux", "hors_sujet")]
    nb_faux = sum(1 for _, s in resultats if s == "faux")

    print(f"\n--- Bilan {langue.upper()} ---")
    print(f"Thèmes corrects : {len(bons)} | thèmes faux : {nb_faux}")

    borne = min(mauvais)
    bons_sous_borne = [d for d in bons if d < borne]
    if not bons_sous_borne:
        print("⚠️ Aucun bon document avant le premier cas mauvais : "
              "améliorez les documents (exemples de phrases) avant de calibrer.")
        return None

    seuil = round((max(bons_sous_borne) + borne) / 2, 2)
    perdus = [d for d in bons if d >= seuil]

    print(f"Dernier bon document : {max(bons_sous_borne):.3f}")
    print(f"Premier cas mauvais  : {borne:.3f}")
    print(f"→ Seuil suggéré : {seuil}")
    if perdus:
        print(f"  ({len(perdus)} bon(s) document(s) au-dessus du seuil : "
              "ils passeront par le classifieur)")
    return seuil


# ---------------------------------------------------------------------------
verifier_index()

seuils = {}
for langue, groupes in TESTS.items():
    res_ok = tester(langue, groupes["bien_etre"])
    res_ko = tester(langue, groupes["hors_sujet"], hors_sujet=True)
    seuils[langue] = suggerer_seuil(langue, res_ok + res_ko)

print("\n=== À COPIER DANS assistant.py ===")
print(f"SEUIL_DISTANCE = {seuils}")
