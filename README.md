# 🧠 MediMind

**A bilingual AI companion for student mental well-being: talk it through, track your mood, and always know where to find human help.**

Built for **DSH Hacks V2** · Theme: **AI x Healthcare**

🎥 **Demo video:** https://vimeo.com/1245592585?share=copy&fl=sv&fe=ci

> ⚠️ MediMind is a hackathon prototype, **not a medical device**. It does not diagnose or treat anything and does not replace a psychologist, a doctor, or an emergency service. If you or someone else is in immediate danger, contact your local emergency services or a crisis line.

---

## The problem

Many students deal with stress, exam pressure, loneliness, or low mood, and don't know who to talk to right away. Counselling services have waiting lists, friends aren't always available at 2 a.m., and generic chatbots can say things that are unsafe or simply wrong in a mental-health context.

## Our solution

MediMind is a web app that gives students a calm place to put their feelings into words, while keeping **safety and human help at the center**:

- an AI companion that listens and offers simple, practical coping suggestions;
- a mood journal that helps spot patterns over time;
- a safety layer that recognises signs of distress and points to real people, in the student's own country.

It runs on an **open-source model served locally with Ollama**, so conversations are not sent to a third-party AI API.

## Features

| | |
|---|---|
| 💬 **AI conversation** | Create and resume conversations, starter prompts (breathing, stress, sleep, exam anxiety), loading and error states. |
| 📚 **Grounded answers (RAG)** | Replies draw on a knowledge base of 21 student well-being topics per language (academic stress, burnout, procrastination, sleep, loneliness, and more), retrieved with multilingual embeddings. |
| 📓 **Mood journal** | Daily mood level, a note, one or more causes, history with filters, and simple statistics. Today's mood can be shared with the assistant for more relevant replies. |
| 🛡️ **Safety layer** | Multi-step handling of distress and emergencies (see below). |
| 🆘 **Human help by country** | Helplines for France, Belgium, Switzerland, Luxembourg, Canada, the USA and the UK, shown in the app independently of the AI. |
| 🌍 **Bilingual** | Full English / French interface; the assistant detects the language of each message and replies accordingly. |
| 🔐 **Private accounts** | Sign-up and login with sessions and Argon2 password hashing; conversations and moods belong to each account. |
| 📱 **Responsive + themes** | Works on desktop and mobile, with a theme selector. |

## How the safety layer works

Mental-health conversations need more than a prompt saying "be careful", so each message goes through several steps:

```text
User message
   │
   ├─ 1. Fast rule-based check (no LLM): signs of imminent risk, physical emergency, violence
   │        └─ if triggered → pre-written safe response pointing to emergency help
   │
   ├─ 2. Structured LLM analysis: topic, risk level, emotion, intensity, whether to refer to a human
   │        └─ high risk → dedicated "crisis" mode with a stricter prompt
   │
   ├─ 3. Retrieval from the bilingual knowledge base (RAG) for on-topic well-being messages
   │        └─ off-topic requests are politely redirected
   │
   └─ 4. Output control: removes diagnoses, medication advice, method/dosage details
          and phone numbers invented by the model (numbers only come from the app's verified list)
```

The emergency path does not depend on the model: help resources stay visible in the interface even if Ollama is unavailable.

## Architecture

```text
Browser
└── Vue.js frontend (Vue Router, vue-i18n)
    └── /api/...
        └── FastAPI backend
            ├── Authentication and sessions
            ├── Conversations and messages
            ├── Mood journal
            ├── SQLite database
            └── AI service
                ├── Language detection (EN / FR)
                ├── ChromaDB knowledge base (multilingual embeddings)
                └── Ollama · qwen3:4b-instruct
```

| Layer | Technology |
|---|---|
| Frontend | Vue.js, Vue Router, vue-i18n, Vite |
| Backend | FastAPI, Starlette sessions, pwdlib (Argon2) |
| Database | SQLite |
| AI | Ollama with `qwen3:4b-instruct`, ChromaDB, `paraphrase-multilingual-MiniLM-L12-v2` embeddings, Lingua language detection |

## Getting started

**Prerequisites:** [Node.js](https://nodejs.org/) (LTS), [Python](https://www.python.org/) 3.10+, [Ollama](https://ollama.com/download) running, and an internet connection on first run (to download the embedding model).

```bash
# 1. Clone
git clone https://github.com/amel-sc/personal.S5.devpost.DSHHacksV2.MediMind.git
cd personal.S5.devpost.DSHHacksV2.MediMind

# 2. Download the language model
ollama pull qwen3:4b-instruct

# 3. Backend
cd backend
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
echo "SESSION_SECRET=replace-with-a-long-random-string" > .env
python services/ingest.py           # builds the knowledge base (once)
uvicorn main:app --reload           # API on http://127.0.0.1:8000

# 4. Frontend (in a second terminal)
cd frontend
npm install
npm run dev                         # app on http://localhost:5173
```

The SQLite database is created automatically on startup. If `backend/` and `frontend/` are not at the repository root, adjust the `cd` commands.

## Privacy and security

- Passwords are hashed with Argon2 and never stored in plain text.
- Access control is enforced by the API, not only by frontend route guards.
- Secrets live in a `.env` file that is not committed.
- Conversations are processed by a local model rather than a third-party AI service.

## Limitations

We want to be upfront about what this prototype is and is not:

- It has **not been clinically validated**, and the effectiveness of its distress detection has not been formally evaluated. It can miss situations or react to harmless messages.
- It needs a machine able to run a 4B-parameter model through Ollama, so there is no public hosted demo yet.
- Helplines are included for 7 countries only.
- Accessibility targets WCAG 2.2 AA, but the interface has not been formally audited.

## What's next

- Formal testing of sensitive scenarios in English and French, with documented criteria.
- Structured guided breathing and grounding exercises.
- Account and data export / deletion, plus a clear data-retention policy.
- More countries and languages for help resources.
- A hosting setup suited to running a local model.