# AI Chatbot

A full-stack AI chatbot web app. Users can sign up, sign in, chat with an AI bot powered by the OpenRouter API, and review their previous conversations.

## What It Does

This app lets you have a conversation with an AI assistant in your browser, similar to ChatGPT.

1. **Create an account:** sign up with a name, email and password. Passwords are stored as hashes, never as plain text.
2. **Sign in:** log in with your name and password.
3. **Chat with the bot:** type a message and the app sends it to an AI model through OpenRouter. The bot replies in a chat window. It has its own identity (a built-in persona), so it introduces itself and answers in a consistent style.
4. **Review your history:** every message you send and every reply is saved, and you can see your previous chats on the history page. You only see your own chats.
5. **Activity tracking:** the app records sign-ins, sign-outs and requests, so there is a record of who did what and when.

Bonus features (planned): speak your message instead of typing, and send an image for the AI to describe.

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

## Project Status

- [x] Task 1: Database
- [ ] Task 2: Backend (Flask API)
- [ ] Task 3: Frontend (Nuxt)
- [ ] Task 4: Audio and vision (bonus)