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

## Project Status

- [x] Task 1: Database
- [ ] Task 2: Backend (Flask API)
- [ ] Task 3: Frontend (Nuxt)
- [ ] Task 4: Audio and vision (bonus)