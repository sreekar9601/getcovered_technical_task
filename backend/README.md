# Login Form Detector - Backend

FastAPI backend for detecting authentication components on websites.

## Features

- 🚀 Fast static scraping with BeautifulSoup4
- 🔍 Intelligent detection of traditional login forms
- 🔑 OAuth/SSO button identification
- ⚡ Dual-path scraping (static + dynamic with Playwright)
- 🛡️ Comprehensive error handling
- 📊 RESTful API with automatic documentation

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright (for Phase 2)

```bash
playwright install chromium
```

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Or using Python directly
python -m app.main
```

The API will be available at: http://localhost:8000

## API Documentation

### Interactive Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

#### POST /api/scrape

Scrape a website and detect authentication components.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response (Success):**
```json
{
  "success": true,
  "url": "https://example.com",
  "auth_found": true,
  "scraping_method": "static",
  "components": {
    "traditional_form": {
      "found": true,
      "html_snippets": ["<form>...</form>"],
      "indicators": ["password_input", "email_input"]
    },
    "oauth_buttons": {
      "found": true,
      "providers": ["google", "github"],
      "html_snippets": ["<button>Sign in with Google</button>"],
      "indicators": ["google_oauth"]
    }
  },
  "metadata": {
    "scrape_time_ms": 1234,
    "page_title": "Login - Example",
    "redirect_detected": false
  }
}
```

#### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── scraper.py           # Web scraping logic
│   ├── detector.py          # Authentication detection
│   └── utils.py             # Helper functions
├── tests/                   # Unit tests (coming soon)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Testing

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/api/health

# Scrape a website
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/login"}'
```

### Test Websites (Phase 1 - Static Sites)

1. https://old.reddit.com/login
2. https://stackoverflow.com/users/login
3. https://github.com/login
4. https://www.wikipedia.org (look for login link)
5. https://news.ycombinator.com/login

## Development

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Log important operations

### Adding New Features

1. Update models in `models.py` if needed
2. Implement logic in appropriate module
3. Update API endpoints in `main.py`
4. Test thoroughly
5. Update documentation

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'app'`
- **Solution:** Make sure you're in the `backend` directory and virtual environment is activated

**Issue:** `Port 8000 already in use`
- **Solution:** Change port with `uvicorn app.main:app --port 8001`

**Issue:** SSL certificate errors
- **Solution:** Some sites have invalid SSL certificates. The scraper handles this gracefully.

## Next Steps (Upcoming Phases)

- [ ] Phase 2: Integrate Playwright for JavaScript-heavy sites
- [ ] Phase 2: Enhanced OAuth detection
- [ ] Phase 3: Rate limiting and caching
- [ ] Phase 4: Comprehensive test suite
- [ ] Phase 5: Docker containerization
- [ ] Phase 5: Deployment to Railway/Render

## License

MIT

