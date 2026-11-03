import chromadb
from chromadb.utils import embedding_functions
import math

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
        "bien_etre": [   # mots-clés EN, adaptés aux noms des fichiers anglais
            ("I'm so stressed about my exams", ["stress", "anxiety"]),
            ("I can't sleep", ["sleep"]),
            ("How do I do a breathing exercise?", ["exercise", "breathing", "anxiety", "stress"]),
            ("I've felt lonely since I moved here", ["isolation", "loneliness", "adjustment"]),
            ("not doing great", None),
            ("I'm so tired", None),
            ("I haven't been eating for two weeks", ["eating", "depress"]),
            ("I'm out of money until the end of the month", ["financ"]),
            ("I'm not sure I chose the right major", ["career", "field_of_study"]),
            ("I spend my whole life on TikTok", ["addiction"]),
            ("I feel stupid compared to my classmates", ["confidence", "esteem", "impostor"]),
            ("I keep putting everything off until the last minute", ["procrastination"]),
            ("I can't focus when I study", ["concentration"]),
            ("I'm exhausted and I don't want to study anymore", ["burnout", "exhaustion", "depress"]),
            ("I keep fighting with my parents", ["relationship"]),
            ("I'm scared of speaking in front of the class", ["social_anxiety"]),
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
    label = "HORS SUJET" if hors_sujet else "BIEN-ÊTRE"
    print(f"\n=== {label} ({langue.upper()}) ===")
    resultats = []

    for item in questions:
        q, attendus = (item, None) if hors_sujet else item

        r = collection.query(query_texts=[q], n_results=2, where={"langue": langue})
        d = r["distances"][0][0]
        sources = [m["source"].lower() for m in r["metadatas"][0]]

        def correspond(source):
            return any(mot in source for mot in attendus)

        if hors_sujet:
            statut, symbole = "hors_sujet", "  "
        elif attendus is None:
            statut, symbole = "vague", "· "
        elif correspond(sources[0]):
            statut, symbole = "ok", "✅"
        elif len(sources) > 1 and correspond(sources[1]):
            statut, symbole = "ok", "🟡"      # bon thème en 2e position
        else:
            statut, symbole = "faux", "❌"

        print(f"{symbole} {d:.3f}  {q:<52} → {sources[0]}")
        resultats.append((d, statut, q))

    return resultats


def suggerer_seuil(langue, resultats):
    bons = [d for d, s, _ in resultats if s == "ok"]
    faux = [q for _, s, q in resultats if s == "faux"]
    hors = [d for d, s, _ in resultats if s == "hors_sujet"]

    print(f"\n--- Bilan {langue.upper()} ---")
    print(f"Thèmes corrects : {len(bons)} | thèmes faux : {len(faux)}")
    for q in faux:
        print(f"   ❌ à corriger dans les documents : « {q} »")

    borne = min(hors)                              # hors sujet le plus proche
    bons_sous = [d for d in bons if d < borne]
    seuil = math.floor((max(bons_sous) + borne) / 2 * 100) / 100   # arrondi vers le bas

    print(f"Dernier bon document : {max(bons_sous):.3f}")
    print(f"Hors sujet le plus proche : {borne:.3f}")
    print(f"→ Seuil suggéré : {seuil}")
    au_dessus = [d for d in bons if d >= seuil]
    if au_dessus:
        print(f"  ({len(au_dessus)} bon(s) document(s) au-dessus : ils passeront par le classifieur)")
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
