# AI Chatbot

A full-stack AI chatbot web app. Users can sign up, sign in, chat with Sage, an AI assistant powered by the OpenRouter API, and review their previous conversations.

## What It Does

This app lets you have a conversation with an AI assistant in your browser, similar to ChatGPT.

1. **Create an account:** sign up with a name, email and password. Passwords are stored as hashes, never as plain text.
2. **Sign in:** log in with your name and password. The app gives you a token that proves who you are for the next hour.
3. **Chat with Sage:** type a message and the app sends it to an AI model through OpenRouter. Sage replies in a chat window.
4. **Review your history:** every message you send and every reply is saved, and you can see your previous chats on the history page. You only see your own chats.
5. **Activity tracking:** the app records sign-ins, failed sign-ins, sign-outs and chat requests, so there is a record of who did what and when.

Bonus features (planned): speak your message instead of typing, and send an image for the AI to describe.

### Meet Sage

Sage is the app's built-in AI assistant. Its identity comes from a system message in `backend/persona.py`, which is sent with every request. That is why Sage introduces itself by name and answers in a consistent style.

**What Sage helps with**
- Answering questions and explaining ideas.
- Writing, learning, brainstorming and coding.
- Follow-up questions. The last 10 saved messages are sent as context, so "What is my name?" works after you have said your name.

**How Sage talks**
- Starts with the direct answer, then adds short reasoning, examples or next steps when they help.
- Keeps replies short for simple questions and detailed for complex ones.
- Matches your tone, whether casual, professional, technical or creative.
- Avoids filler, repetition and excessive emojis.

**Sage's principles**
- Calm, friendly, practical and nonjudgmental.
- Honest about uncertainty. It says when it doesn't know instead of inventing facts or abilities.
- Always an AI assistant, never pretending to be human.
- Politely declines harmful requests and suggests a safe alternative when possible.

**Limits**
- No long-term memory beyond the last 10 messages, and no web access or tools.
- It only sees the signed-in user's own messages.

## Tech Stack

- **Database:** MySQL (XAMPP / phpMyAdmin)
- **Backend:** Python + Flask
- **Frontend:** Nuxt (Vue) with Nuxt UI
- **AI:** OpenRouter API

## Features

- Sign up and sign in with a name and password
- Chat with an AI bot that has its own persona
- Chat history saved per user
- Activity logging (logins, logouts, and requests)

## Database

Create the database by running `database/schema.sql` in phpMyAdmin (SQL tab). It creates a database named `ai_chatbot` with three tables.

### Tables

| Table | Purpose |
|-------|---------|
| `users` | One row per registered user: name, email, password hash, created time |
| `chat_history` | One row per message, with a `role` of `user` or `assistant`, owned by a user |
| `logs` | One row per event: login, logout, or request, with path, method and status code |

### Key rules

- `users.name` and `users.email` are `UNIQUE` because name is used to sign in, so two users with the same name would make signin ambiguous, and each email should belong to one account.
- `chat_history.user_id` uses `ON DELETE CASCADE` because messages belong to the user, so deleting an account removes their chats and leaves no orphan rows.
- `logs.user_id` allows `NULL` and uses `ON DELETE SET NULL` because logs are a record of system activity that should survive a user deletion, and failed signins have no user id to store.
- Passwords are stored only as hashes in `users.password_hash`, never as plain text.
- The bot's persona is not stored in the database. It is the same for every request, so it lives in the Flask code.

## Backend

The backend is a Flask REST API that handles accounts, the AI chat, saved history and activity logging.

### Setup

1. `cd backend`
2. Create and activate a virtual environment:
   - `python -m venv venv`
   - Windows (Git Bash): `source venv/Scripts/activate`
   - macOS / Linux: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `backend/.env` and fill in your real values. Never commit `.env`.
5. Start **MySQL** in XAMPP and make sure the `ai_chatbot` database exists (see the Database section).
6. Run the server: `python app.py`. It starts on `http://127.0.0.1:5000`.

### Environment variables

| Variable | Purpose |
|---|---|
| `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | MySQL connection (XAMPP defaults: `localhost`, `root`, empty, `ai_chatbot`) |
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `OPENROUTER_MODEL` | OpenRouter model ID (currently a free NVIDIA Nemotron model) |
| `JWT_SECRET` | Long random string used to sign auth tokens |

### Endpoints

Protected endpoints need the header `Authorization: Bearer <token>`. The token comes from `/api/signin` and expires after 1 hour.

| Method | Path | Auth | Purpose | Status codes |
|---|---|---|---|---|
| POST | `/api/signup` | No | Create an account (name, email, password, confirm_password) | `201`, `400`, `409` |
| POST | `/api/signin` | No | Sign in with name and password, returns a token | `200`, `400`, `401` |
| POST | `/api/signout` | Yes | Record a logout event | `200`, `401` |
| POST | `/api/chat` | Yes | Send a message to Sage and get a reply | `200`, `400`, `401`, `502` |
| GET | `/api/history` | Yes | List the signed-in user's saved messages, oldest first | `200`, `401` |
| GET | `/api/me` | Yes | Return the signed-in user's id (token check) | `200`, `401` |

### Status codes

| Code | Meaning in this API |
|---|---|
| `200` | Success |
| `201` | Account created |
| `400` | Invalid request (missing field, passwords don't match, message too long) |
| `401` | Missing, invalid or expired token, or wrong name or password |
| `409` | Name or email already exists |
| `502` | The AI service (OpenRouter) failed |

All errors return JSON in the form `{"error": "message"}`.

### Design notes

- **Passwords** are stored only as salted hashes (Werkzeug).
- **SQL** uses parameterized queries (`%s` placeholders) to prevent SQL injection.
- **Sign-in errors** use one generic message, "Invalid name or password", so attackers can't learn which names exist.
- **Ownership:** the user id comes from the verified token, never from the request body, so users only see their own chats.
- **Chat flow:** the AI is called first, then the user message and the reply are saved together, so history never holds a question without an answer.
- **Logging:** logins, failed logins, logouts and chat requests are written to the `logs` table. A logging failure never breaks a request.
- **Signout:** tokens are stateless, so signout records the event and the frontend must discard the token. It stays valid until it expires.
- **CORS** allows the Nuxt dev server at `http://localhost:3000`.

## Project Status

- [x] Task 1: Database
- [ ] Task 2: Backend (Flask API)
- [ ] Task 3: Frontend (Nuxt)
- [ ] Task 4: Audio and vision (bonus)