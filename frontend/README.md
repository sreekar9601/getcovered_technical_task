# Login Form Detector - Frontend

React + TypeScript frontend for the Login Form Detector application.

## Features

- 🎨 Modern, clean UI with Tailwind CSS
- 📱 Fully responsive design
- ⚡ Fast and intuitive
- 🔍 Real-time authentication detection
- 📋 Copy-to-clipboard functionality
- 🎯 Tabbed results view (Traditional Forms / OAuth / Raw JSON)

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

Create a `.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at: http://localhost:5173

## Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── UrlInput.tsx          # URL input component
│   │   ├── ResultsDisplay.tsx    # Results display with tabs
│   │   ├── LoadingSpinner.tsx    # Loading indicator
│   │   └── ErrorMessage.tsx      # Error display
│   ├── services/
│   │   └── api.ts                # API client
│   ├── types/
│   │   └── index.ts              # TypeScript types
│   ├── App.tsx                   # Main app component
│   ├── main.tsx                  # Entry point
│   └── index.css                 # Global styles (Tailwind)
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## Usage

1. Enter a website URL in the input field
2. Click "Analyze" or press Enter
3. View detected authentication components:
   - **Traditional Forms** tab: Username/password forms with HTML snippets
   - **OAuth/SSO** tab: OAuth buttons from providers like Google, GitHub, etc.
   - **Raw JSON** tab: Full API response for debugging

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variable: `VITE_API_URL=<your-backend-url>`
4. Deploy

### Build Command

```bash
npm run build
```

### Output Directory

```
dist/
```

## License

MIT
