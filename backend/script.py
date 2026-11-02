from transformers import pipeline

chat = pipeline("text-generation",
                model="Qwen/Qwen3-4B-Instruct-2507",
                device_map="auto")

SYSTEM_PROMPT = """Tu es MediMind, un assistant de bien-être pour étudiants.
Tu n'es PAS psychologue : tu ne poses jamais de diagnostic et tu ne parles pas de médicaments.
Tu proposes écoute, exercices de respiration et informations validées.
Si la personne va mal, tu l'encourages à contacter un professionnel."""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Je stresse trop pour mes partiels"},
]
out = chat(messages, max_new_tokens=300)
print(out[0]["generated_text"][-1]["content"])
