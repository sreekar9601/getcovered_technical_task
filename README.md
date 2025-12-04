# Login Form Detector - GetCovered Task Submission

🔐 **AI-powered web application that detects authentication components on any website**

Identifies traditional username/password forms and OAuth/SSO buttons with intelligent dual-path scraping.

---

## 🚀 Live Demo

- **Frontend**: https://getcovered-technical-task.vercel.app
- **Backend API**: https://getcoveredtechnicaltask-production.up.railway.app
- **API Documentation**: https://getcoveredtechnicaltask-production.up.railway.app/docs
- **Health Check**: https://getcoveredtechnicaltask-production.up.railway.app/api/health

### Local Development
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000

---

## ✨ Features

### Core Functionality
- ✅ **Detect Traditional Login Forms** - Username/password inputs with submit buttons
- ✅ **Identify OAuth/SSO Buttons** - Google, Microsoft, GitHub, Facebook, Apple, LinkedIn, etc.
- ✅ **Dual-Path Scraping Strategy**:
  - Fast static HTML scraping (works for 80% of sites)
  - Playwright browser automation fallback for JavaScript-heavy sites
- ✅ **Clean HTML Snippets** - Extracted and prettified code for easy inspection
- ✅ **Comprehensive Error Handling** - Graceful handling of timeouts, blocks, and edge cases

### User Interface
- 🎨 Modern, clean design with Tailwind CSS
- 📱 Fully responsive (mobile, tablet, desktop)
- 🔍 Real-time results with loading states
- 📋 Copy-to-clipboard functionality
- 🎯 Tabbed interface (Traditional Forms / OAuth / Raw JSON)
- ⚡ Fast and intuitive

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         React Frontend (Vite)               │
│  - URL input interface                      │
│  - Results display with tabs                │
│  - Error handling & loading states          │
│  Port: 5173                                 │
└──────────────────┬──────────────────────────┘
                   │ REST API
                   ↓
┌─────────────────────────────────────────────┐
│          FastAPI Backend                    │
│  - POST /api/scrape                         │
│  - GET /api/health                          │
│  - Dual scraping strategy                   │
│  - Auth component detection                 │
│  Port: 8000                                 │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
┌───────────────┐   ┌──────────────────┐
│   requests    │   │   Playwright     │
│ BeautifulSoup │   │ (Headless Chrome)│
│  (Fast path)  │   │  (Fallback path) │
└───────────────┘   └──────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Scraping**: 
  - `requests` + `BeautifulSoup4` (static sites)
  - `playwright` (JavaScript-rendered sites)
- **Parsing**: `lxml`, `html5lib`
- **Validation**: `pydantic`, `validators`

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v3
- **HTTP Client**: Axios
- **Icons**: Lucide React

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: **http://localhost:8000**

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## 🎯 Usage

### Web Interface

1. Open http://localhost:5173 in your browser
2. Enter a website URL (e.g., `https://github.com/login`)
3. Click "Analyze" or press Enter
4. View detected authentication components:
   - **Traditional Forms** tab - Username/password forms with HTML
   - **OAuth/SSO** tab - OAuth buttons (Google, GitHub, etc.)
   - **Raw JSON** tab - Full API response

### API Usage

#### POST /api/scrape

```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/login"}'
```

**Response:**
```json
{
  "success": true,
  "url": "https://github.com/login",
  "auth_found": true,
  "scraping_method": "static",
  "components": {
    "traditional_form": {
      "found": true,
      "html_snippets": ["<form>...</form>"],
      "indicators": ["password_input", "email_input", "submit_button"]
    },
    "oauth_buttons": {
      "found": true,
      "providers": ["github"],
      "html_snippets": ["<button>...</button>"],
      "indicators": ["github_oauth"]
    }
  },
  "metadata": {
    "scrape_time_ms": 400,
    "page_title": "Sign in to GitHub",
    "redirect_detected": false
  }
}
```

#### GET /api/health

```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-03T00:00:00Z",
  "version": "1.0.0"
}
```

---

## 🧪 Testing

### Example Sites

These are good examples to try in the UI:

- GitHub: `https://github.com/login`
- Stack Overflow: `https://stackoverflow.com/users/login`
- LinkedIn: `https://www.linkedin.com/login`
- New York Times: `https://myaccount.nytimes.com/`
- Twitch: `https://www.twitch.tv/login`
- Grok (x.ai): `https://accounts.x.ai/sign-in`

⚠️ **Notes:**
- Some sites (e.g., Instagram, NYTimes, Twitch, Grok) use strong bot protection
- When detection fails, you can retry with **“Force Browser Automation”** (Playwright) in the UI
- Very slow or CAPTCHA-heavy sites may still fail or timeout

### Manual Testing

```bash
cd backend
source venv/bin/activate
python test_manual.py
```

---

## 📁 Project Structure

```
login-detector/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Package initialization
│   │   ├── main.py              # FastAPI app (229 lines)
│   │   ├── models.py            # Pydantic models (77 lines)
│   │   ├── scraper.py           # Scraping logic (150 lines)
│   │   ├── detector.py          # Auth detection (283 lines)
│   │   └── utils.py             # Helpers (69 lines)
│   ├── requirements.txt         # Python dependencies
│   ├── test_manual.py           # Testing script
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UrlInput.tsx
│   │   │   ├── ResultsDisplay.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorMessage.tsx
│   │   ├── services/
│   │   │   └── api.ts            # API client
│   │   ├── types/
│   │   │   └── index.ts          # TypeScript types
│   │   ├── App.tsx               # Main component
│   │   ├── main.tsx              # Entry point
│   │   └── index.css             # Tailwind CSS
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── README.md
│
├── README.md                     # This file
└── implementation.md             # Detailed implementation plan
```

---

## 🔍 How It Works

### Dual-Path Scraping Strategy

1. **Static Scraping (Fast Path)**:
   - Uses `requests` + `BeautifulSoup4`
   - Fast (~200-500ms)
   - Works for 80% of websites
   - Minimal resource usage

2. **Playwright Fallback (Dynamic Path)**:
   - Launches headless Chrome
   - Executes JavaScript
   - Waits for dynamic content
   - Handles modern SPAs
   - Used when static scraping fails (403, timeouts, insufficient content)

### Authentication Detection

**Traditional Forms:**
- Searches for `<input type="password">` (primary signal)
- Finds parent `<form>` element
- Looks for email/username/text inputs
- Identifies submit buttons
- Handles formless layouts (modern SPAs)

**OAuth/SSO Buttons:**
- Detects keywords: "Sign in with", "Continue with", "Log in with"
- Identifies providers: Google, Microsoft, GitHub, Facebook, Apple, LinkedIn, Twitter, Amazon
- Checks OAuth URLs: `accounts.google.com`, `login.microsoftonline.com`, etc.
- Extracts HTML snippets

---

## 🚧 Edge Cases Handled

- ✅ Missing protocol (adds `https://`)
- ✅ Invalid URLs
- ✅ HTTP errors (403, 429, 500, etc.)
- ✅ Timeouts
- ✅ Connection errors
- ✅ Redirects
- ✅ Non-HTML content
- ✅ Bot detection/blocking
- ✅ Empty responses
- ✅ Formless login sections
- ✅ Hidden forms
- ✅ Multiple login forms per page

---

## 🎨 Design Decisions

### Why Dual-Path Scraping?
- **Performance**: Static scraping is 10x faster for simple sites
- **Coverage**: Playwright handles JavaScript-heavy sites
- **Resource Efficiency**: Only use Playwright when needed
- **Reliability**: Fallback mechanism ensures high success rate

### Why React Instead of Streamlit?
- More flexible and customizable UI
- Better performance for production
- Aligns with modern web development practices
- Easier to deploy and scale

### Why BeautifulSoup + Playwright?
- BeautifulSoup is lightweight and fast for static HTML
- Playwright is industry-standard for browser automation
- Together they provide best-of-both-worlds solution

---

## 🔮 Future Enhancements

- [ ] Batch URL processing (analyze multiple sites)
- [ ] Historical tracking (save results)
- [ ] Rate limiting dashboard
- [ ] Custom detection rules
- [ ] Export results (CSV, JSON)
- [ ] Browser extension
- [ ] CI/CD integration
- [ ] Database storage (MongoDB/PostgreSQL)
- [ ] User authentication
- [ ] API rate limiting per user

---

## 📈 Performance Metrics

- **Average Response Time**: 0.5-1.0s (static), 5-10s (Playwright)
- **Success Rate**: 80%+ on tested sites
- **Accuracy**: High (detects both traditional and OAuth)
- **Resource Usage**: Low (efficient dual-path strategy)

---

## 🐛 Known Issues

1. **Reddit Old**: Blocked by anti-bot measures (403 Forbidden)
2. **Very Slow Sites**: May timeout after 45 seconds
3. **CAPTCHA Pages**: Cannot bypass CAPTCHAs
4. **Some Geo-Restricted Sites**: May not work from certain regions

---

