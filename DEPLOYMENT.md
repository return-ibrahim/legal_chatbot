# LexQuery Deployment Guide

## Quick Start Commands

### Backend (Local)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env and add GROQ_API_KEY
python ingest.py
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Local)
```bash
cd frontend
npm install
npm run dev
```

## Deployment Options

### Option 1: HuggingFace Spaces (Backend) + Vercel (Frontend)

#### Backend on HuggingFace:
1. Create Space at huggingface.co/spaces
2. Choose Docker SDK
3. Add Dockerfile:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python ingest.py
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```
4. Push backend code
5. Add secrets in Space settings:
   - GROQ_API_KEY=your_key
   - SECRET_KEY=your_secret
   - FRONTEND_URL=your_vercel_url

#### Frontend on Vercel:
1. Push frontend to GitHub
2. Import to Vercel
3. Add environment variable:
   - NEXT_PUBLIC_API_URL=your_hf_space_url

### Option 2: Render (Backend) + Vercel (Frontend)

#### Backend on Render:
1. Create Web Service at render.com
2. Connect GitHub repo
3. Settings:
   - Build: `pip install -r requirements.txt && python ingest.py`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

#### Frontend on Vercel:
Same as Option 1

## Environment Variables

### Backend (.env)
```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_for_jwt_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./lexquery.db
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## Get Groq API Key (Free)
1. Go to https://console.groq.com/
2. Sign up
3. Create API key
4. Copy to .env file

## Troubleshooting

### CORS Error:
Update `FRONTEND_URL` in backend .env

### Database Error:
Run `python ingest.py` to create database

### FAISS Not Found:
Make sure `python ingest.py` completed successfully

### Port Already in Use:
Change port in uvicorn command or kill existing process

## Production Checklist
- [ ] Update SECRET_KEY to strong random value
- [ ] Add real Groq API key
- [ ] Run data ingestion script
- [ ] Configure CORS for production domain
- [ ] Test all API endpoints
- [ ] Test authentication flow
- [ ] Verify search functionality
- [ ] Verify chat functionality
- [ ] Check responsive design
- [ ] Monitor API usage
