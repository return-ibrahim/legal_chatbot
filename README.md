# LexQuery - AI Legal Assistant 

A production-level SaaS web application that combines legal search with AI-powered question answering using Retrieval Augmented Generation (RAG). Built with Next.js 14 and FastAPI.

##  Features

- **Authentication System**: JWT-based registration and login
- **Legal Search Engine**: Keyword-based semantic search through court judgments
- **AI Legal Chatbot**: Natural language Q&A powered by RAG (FAISS + Groq LLM)
- **Chat History**: Automatic conversation tracking
- **Secure by Default**: Strict legal intent filtering to prevent off-topic replies
- **Professional SaaS UI**: Clean navigation with Sidebar and History
- **Zero-Setup Database**: Pre-loaded legal index and local SQLite DB included

##  Technology Stack

### Frontend
- Next.js 14 (App Router)
- Tailwind CSS
- shadcn/ui components
- Axios for API calls
- TypeScript

### Backend
- Python FastAPI
- FAISS vector database
- sentence-transformers (all-MiniLM-L6-v2)
- Groq API (llama3-8b-8192)
- SQLite database
- JWT authentication

##  Project Structure

```
lexquery_project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── auth.py          # JWT authentication
│   │   ├── rag.py           # RAG pipeline
│   │   ├── search.py        # Search functionality
│   │   ├── db.py            # Database connection
│   │   └── models.py        # SQLAlchemy models
│   ├── data/                # FAISS index and metadata
│   ├── ingest.py            # Data ingestion script
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── app/
    │   ├── page.tsx         # Landing page
    │   ├── layout.tsx       # Root layout
    │   ├── globals.css
    │   ├── auth/
    │   │   ├── login/
    │   │   └── register/
    │   └── dashboard/
    │       ├── layout.tsx   # Dashboard layout
    │       ├── search/      # Search page
    │       ├── chat/        # AI chat page
    │       └── history/     # History page
    ├── components/ui/       # shadcn/ui components
    ├── lib/
    │   ├── api.ts           # API service layer
    │   └── utils.ts
    ├── package.json
    ├── tailwind.config.js
    └── .env.local
```

## 🏃‍♂️ Local Development Setup

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy .env.example to .env
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and add your Groq API key
# Get free API key from: https://console.groq.com/
```

5. **Database Initialization**
The project comes with a pre-indexed legal database (`lexquery.db`). On your first run, the system will automatically initialize all required tables. If you wish to re-ingest data:
```bash
python ingest.py
```

6. **Run the backend**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run development server**
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

##  Getting Groq API Key (Free)

1. Visit [https://console.groq.com/](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key to your `.env` file

##  Data Ingestion

The `ingest.py` script includes sample legal cases. To use real data:

1. Prepare a CSV file with columns: `title`, `court`, `date`, `text`, `source`
2. Place it in `backend/data/legal_cases.csv`
3. Run the ingestion script:

```bash
cd backend
python ingest.py
```

This will:
- Load and process documents
- Create embeddings using sentence-transformers
- Build FAISS index for fast similarity search
- Save metadata for retrieval

##  Deployment

### Backend Deployment (HuggingFace Spaces)

1. **Create a HuggingFace Space**
   - Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
   - Create new Space with Docker SDK

2. **Create Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python ingest.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

3. **Push code to Space**
```bash
git push origin main
```

4. **Set environment variables** in Space settings:
   - `GROQ_API_KEY`
   - `SECRET_KEY`
   - `FRONTEND_URL`

### Backend Deployment (Render - Alternative)

1. **Create account** at [https://render.com](https://render.com)
2. **Create new Web Service**
3. **Connect GitHub repository**
4. **Configure**:
   - Build Command: `pip install -r requirements.txt && python ingest.py`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Add environment variables** in Render dashboard

### Frontend Deployment (Vercel)

1. **Install Vercel CLI** (optional)
```bash
npm i -g vercel
```

2. **Deploy**
```bash
cd frontend
vercel
```

Or:

1. **Push to GitHub**
2. **Import project** at [https://vercel.com](https://vercel.com)
3. **Configure**:
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
4. **Add environment variable**:
   - `NEXT_PUBLIC_API_URL` = Your backend URL

##  Connecting Frontend to Backend

1. Update `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

2. Update backend CORS settings in `backend/app/main.py` to allow your frontend domain

##  API Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /search` - Search legal documents
- `POST /chat` - AI chatbot (RAG)
- `GET /history` - Get chat history
- `GET /profile` - Get user profile

##  UI Pages

- `/` - Landing page
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/dashboard/search` - Search judgments
- `/dashboard/chat` - AI lawyer chat
- `/dashboard/history` - Conversation history

##  Testing

1. **Register a new account**
2. **Try keyword search**: "Section 302 IPC"
3. **Ask AI questions**: "What is the punishment for murder?"
4. **View history** of your interactions

##  Security

- JWT authentication with httpOnly cookies
- Password hashing with bcrypt
- CORS protection
- Environment variable protection
- Input validation

##  License

MIT License - Feel free to use for learning and commercial projects

##  Contributing

Contributions welcome! Please open an issue or submit a PR.

##  Support

For issues or questions, please open a GitHub issue.


