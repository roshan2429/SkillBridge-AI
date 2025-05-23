# SkillBridge AI Chatbot 

A full-stack AI-powered chatbot for SkillBridge, built with FastAPI, LangChain, and React.

## Overview
This project is uses a Retrieval-Augmented Generation (RAG) pipeline . The backend is built with FastAPI and LangChain. The frontend is a Vite-based React app styled with Tailwind CSS.

## Setup Instructions

### Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file with:
   ```
   OPENAI_API_KEY=your-api-key
   ADZUNA_APP_ID=your-app-ID
   ADZUNA_API_KEY=your-api-key
   ```
4. Run the backend:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Access the app at `http://localhost:3000`.

## Usage
- Open the frontend in a browser.
- Ask  questions .
- The chatbot responds with concise answers .

## Technologies
- **Backend**: FastAPI, LangChain, Chroma, Python
- **Frontend**: React, Vite, Tailwind CSS

## Author
Roshan, Master’s in Computer Science (2025)
