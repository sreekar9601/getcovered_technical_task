#!/bin/bash

# Login Form Detector - Quick Setup Script

echo "🔐 Login Form Detector - Setup"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env file..."
    cat > backend/.env << 'EOF'
# Gemini API Key for LLM-based detection fallback
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
EOF
    echo "✅ Created backend/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit backend/.env and add your GEMINI_API_KEY"
    echo ""
else
    echo "✅ backend/.env already exists"
fi

# Check if frontend .env exists
if [ ! -f "frontend/.env" ]; then
    echo "📝 Creating frontend/.env file..."
    cat > frontend/.env << 'EOF'
# Backend API URL
VITE_API_URL=http://localhost:8000
EOF
    echo "✅ Created frontend/.env"
else
    echo "✅ frontend/.env already exists"
fi

echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Add your Gemini API key to backend/.env"
echo "   Get one here: https://makersuite.google.com/app/apikey"
echo ""
echo "2. Run with Docker:"
echo "   docker-compose up --build"
echo ""
echo "3. Or run locally:"
echo "   Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "✨ Happy coding!"

