# AI Book Creation Backend

This is the backend service for the AI Book Creation Guide project. It provides a RAG (Retrieval-Augmented Generation) chatbot API that answers questions about book content using vector similarity search.

## Tech Stack

- **Framework**: FastAPI
- **Runtime**: Python 3.11
- **Deployment**: Vercel serverless functions
- **Database**: PostgreSQL (Neon) 
- **Vector Store**: Qdrant
- **AI Services**: OpenAI, Google Gemini

## Local Development

### Prerequisites

- Python 3.11
- Poetry or pip for dependency management

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the required environment variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=your_database_url
   RATE_LIMIT=30/minute
   ```

4. Start the development server:
   ```bash
   python start_dev.py
   ```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

## API Endpoints

- `GET /` - Health check and API info
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `POST /query` - Query endpoint for RAG functionality
- `POST /query-selected` - Query selected documents endpoint
- `GET /health` - Health check endpoint

## Deployment

This backend is ready for deployment on Vercel:

1. Push the code to a Git repository
2. Connect your repository to Vercel
3. The build will automatically use the configuration in `vercel.json`
4. Set the environment variables in the Vercel dashboard

## Architecture

The backend follows a modular structure:

```
backend/
├── app/                 # Main application
│   ├── main.py          # FastAPI application entry point
│   ├── api/             # API routes and models
│   ├── core/            # Core configurations and utilities
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
├── ingestion/           # Document ingestion and processing
├── scripts/             # Setup and utility scripts
└── tests/               # Test files
```

## Environment Variables

The application requires the following environment variables:

- `OPENAI_API_KEY` - API key for OpenAI services
- `QDRANT_URL` - URL for Qdrant vector database
- `QDRANT_API_KEY` - API key for Qdrant (if using cloud)
- `GEMINI_API_KEY` - API key for Google Gemini
- `DATABASE_URL` - PostgreSQL database URL
- `RATE_LIMIT` - API rate limiting configuration

## Project Structure

- `app/main.py` - Main FastAPI application with Mangum adapter for Vercel
- `app/api/routes/` - API route definitions
- `app/core/` - Configuration, logging, and security
- `app/services/` - Core business logic for RAG operations
- `ingestion/` - Document processing and ingestion
- `scripts/` - Database setup and other utility scripts

## License

MIT