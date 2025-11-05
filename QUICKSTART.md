# 🚀 Quick Start Guide

Get your Portfolio Diversification Analyzer running in 3 minutes!

## Prerequisites

1. **Google Gemini API Key**: Get yours at https://aistudio.google.com/apikey

## Option 1: Easy Start (Using Run Script)

### Linux/Mac:
```bash
./run_app.sh
```

### Windows:
```cmd
run_app.bat
```

The script will:
- Create a virtual environment (if needed)
- Install all dependencies
- Launch the Streamlit app

## Option 2: Manual Start

### Step 1: Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key (Optional)
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Step 4: Run the App
```bash
streamlit run app.py
```

## Using the App

1. **Open your browser** at http://localhost:8501
2. **Enter your API key** in the sidebar (or skip if you set it in .env)
3. **Upload a B3 portfolio PDF**
4. **Click "Analyze Portfolio"**
5. **Review the results!**

## Need Help?

- See [STREAMLIT_README.md](STREAMLIT_README.md) for detailed documentation
- Check the troubleshooting section for common issues
- The app includes built-in help in the sidebar

---

**Happy analyzing! 📊**
