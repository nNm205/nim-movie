<div align="center">

# <img src="./docs/images/nim_movie_logo.png">

**AI-Powered Movie Streaming & Recommendation Platform**

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/pgvector-RAG-blue?style=for-the-badge" />
</p>

<p>
  <a href="https://nim-movie.vercel.app">
    <img src="https://img.shields.io/badge/🌐_Live_Demo-Visit-success?style=for-the-badge" />
  </a>
  <a href="https://nim-movie-production.up.railway.app/docs">
    <img src="https://img.shields.io/badge/API_Docs-Swagger-009688?style=for-the-badge" />
  </a>
</p>

</div>

---

## 📖 Overview

NimMovie is a modern movie streaming and recommendation platform inspired by Netflix, built with **FastAPI**, **React**, and **PostgreSQL**. It provides movie discovery, watchlist management, user reviews, and an **AI-powered RAG assistant** capable of answering movie-related questions and generating personalized recommendations through natural language interactions.

The application is deployed on **Vercel**, **Railway**, and **Supabase PostgreSQL** with a production-ready architecture.

---

## 🖼️ Screenshots

### 🏠 Home

<img src="./docs/images/nim_movie_home.png" alt="Home page" width="900" />

### 🎬 Movie Detail

<img src="./docs/images/nim_movie_movie-detail.png" alt="Movie detail page" width="900" />

### 📚 Watchlist

<img src="./docs/images/nim_movie_watchlist.png" alt="Watchlist page" width="900" />

### 🤖 AI Chatbot

<img src="./docs/images/nim_movie_chatbot.png" alt="AI chatbot" width="700" />

---

## 🚀 Features

### 🎥 Movie Platform

* Browse Trending, Popular, Top Rated Movies
* Advanced Search & Discovery
* Movie Details, Trailer & Cast Information
* Personal Watchlist Management
* User Reviews & Ratings

### 🤖 AI Assistant

* Natural Language Movie Recommendations
* Retrieval-Augmented Generation (RAG)
* Vector Search with pgvector
* Citation-Based Responses
* Real-Time Streaming via SSE

### 🔐 Security

* JWT Authentication
* Password Hashing (bcrypt)
* Role-Based Access Control (RBAC)
* Protected Frontend Routes

---

## ⚙️ Tech Stack

| Frontend     | Backend    | AI & Data |
| ------------ | ---------- | --------- |
| React 19     | FastAPI    | OpenAI    |
| Vite         | SQLAlchemy | Gemini    |
| Tailwind CSS | Pydantic   | pgvector  |
| React Router | JWT Auth   | Supabase  |
| Axios        | Alembic    | TMDB API  |

---

## 🏛️ Architecture

```text
React + Vite
      │
      ▼
 FastAPI Backend
      │
 ┌────┴────┐
 ▼         ▼
PostgreSQL  TMDB API
(pgvector)  LLM Providers
      │
      ▼
 RAG Pipeline
```

---

## ▶️ Getting Started

### Clone Repository

```bash
git clone https://github.com/nNm205/nim-movie.git
cd nim-movie
```

### Backend

```bash
cd backend

pip install -r requirements.txt

alembic upgrade head

uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger Docs:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

> Configure environment variables using `.env.example` before running the application.

---

## ☁️ Deployment

| Component | Platform            |
| --------- | ------------------- |
| Frontend  | Vercel              |
| Backend   | Railway             |
| Database  | Supabase PostgreSQL |

### Live Demo

🌐 Frontend: https://nim-movie.vercel.app

📚 API Docs: https://nim-movie-production.up.railway.app/docs

---

## 👨‍💻 Author

**Nguyễn Nhật Minh**

* GitHub: https://github.com/nNm205
* Email: [minh2m5@gmail.com](mailto:minh2m5@gmail.com)

---

<div align="center"> 

**If you find this project useful, please consider giving it a star ⭐ .** 

*Built with ☕ and a lot of git commit --amend* 

</div>
