import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-interview-prep-secret-key-2026')
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/ai_interview_db')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'ai_interview_db')
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-service-account.json')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
    
    # AI API Config (Supports Gemini / OpenAI / Ollama / Fallback)
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_MODEL = os.environ.get('AI_MODEL', 'gemini-1.5-pro')
