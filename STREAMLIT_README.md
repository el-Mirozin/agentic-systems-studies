# 📊 Portfolio Diversification Analyzer

A Streamlit web application powered by Google Gemini AI that analyzes investment portfolio diversification from PDF files. The app calculates the Herfindahl-Hirschman Index (HHI) and provides AI-driven insights to help you understand and improve your portfolio diversification.

## ✨ Features

- **🤖 AI-Powered Analysis**: Uses Google Gemini 2.5 Flash for intelligent portfolio analysis
- **📈 Diversification Metrics**: Calculates HHI and Normalized HHI
- **📄 PDF Upload**: Easy drag-and-drop PDF file upload
- **🎨 Beautiful UI**: Clean, modern interface built with Streamlit
- **💾 Export Results**: Download analysis reports as text files
- **🔒 Secure**: API keys can be entered in the app or stored in environment variables

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   cd /home/henrique/Documents/ML_AI/git_projects/agentic-systems-studies
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional but recommended):
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

### Running the App

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser**: The app will automatically open at `http://localhost:8501`

3. **Configure your API key**:
   - Enter your Google Gemini API key in the sidebar, OR
   - Set it in your `.env` file as `GEMINI_API_KEY`

4. **Upload and analyze**:
   - Upload a B3 portfolio PDF file
   - Click "Analyze Portfolio"
   - Review the results and AI recommendations

## 📁 Project Structure

```
.
├── app.py                                    # Main Streamlit application
├── portfolio_analyzer.py                     # Portfolio analysis module (wraps _sup functionality)
├── pydantic_pdf_reader.py                    # PDF extraction agent (called as subprocess)
├── pydantic_diversification_analyst_sup.py   # Enhanced analysis script with agent orchestration
├── pydantic_diversification_analyst.py       # Original analysis script
├── requirements.txt                          # Python dependencies
├── .env.example                              # Example environment variables
├── STREAMLIT_README.md                      # This file
├── QUICKSTART.md                            # Quick start guide
└── .env                                     # Your environment variables (create this)
```

## 🏗️ Architecture

The application uses a multi-agent architecture:

1. **PDF Reader Agent** (`pydantic_pdf_reader.py`): Extracts investment data from PDF files using Google Gemini's vision and text capabilities
2. **Diversification Analyzer** (`portfolio_analyzer.py`): Calculates HHI metrics and provides AI-powered analysis
3. **Streamlit App** (`app.py`): Provides the web interface for user interaction

The analyzer calls the PDF reader agent as a subprocess, allowing for modular, specialized processing of different tasks.

## 🧮 Understanding the Metrics

### HHI (Herfindahl-Hirschman Index)
- Formula: HHI = Σ(wi²) where wi is the weight of each investment
- Ranges from 1/n to 1 (where n = number of holdings)
- Lower values indicate better diversification

### Normalized HHI
- Scaled version of HHI ranging from 0 to 1
- **0** = Perfect diversification (all investments equally weighted)
- **1** = Complete concentration (all money in one investment)

### Interpretation Guide
- 🟢 **< 0.2**: Well diversified
- 🟡 **0.2-0.5**: Moderately diversified
- 🟠 **0.5-0.8**: Moderately concentrated
- 🔴 **> 0.8**: Highly concentrated

## 📋 Supported File Formats

The app supports **B3 investment portfolio PDF files**. The PDF Reader Agent uses Google Gemini's multimodal capabilities to extract:
- Investment names and tickers
- Investment values
- Portfolio totals

The AI-based extraction is more flexible than regex-based approaches and can handle varying PDF formats and layouts.

## 🔧 Advanced Configuration

### Using Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_actual_api_key_here
PDF_PATH=path/to/default/portfolio.pdf  # Optional
```

### Customizing the Agent

You can modify the agent's behavior by editing `portfolio_analyzer.py`:

- Change the model: Update `model_name` in `GoogleModel` initialization
- Modify system prompt: Edit the `system_prompt` in the Agent setup
- Add new tools: Define new functions and decorate with `@agent.tool`

## 🛠️ Development

### Module: `portfolio_analyzer.py`

The core analysis module provides:

- **PortfolioAnalyzer class**: Main analyzer with Google Gemini integration
- **extract_portfolio_from_pdf()**: Extracts data from B3 PDFs
- **calculate_hhi_metrics()**: Computes HHI and normalized HHI
- **analyze_portfolio()**: Runs the AI agent for complete analysis

### Running the Standalone Scripts

You can also use the command-line scripts directly:

**Enhanced version with agent orchestration:**
```bash
# Set environment variables
export GEMINI_API_KEY="your_key_here"
export PDF_PATH="path/to/portfolio.pdf"

# Run the enhanced script (uses PDF reader agent)
python pydantic_diversification_analyst_sup.py
```

**Original version:**
```bash
# Run the original script (direct PDF parsing)
python pydantic_diversification_analyst.py
```

**PDF Reader only:**
```bash
# Extract portfolio data from PDF
python pydantic_pdf_reader.py path/to/portfolio.pdf
```

## 📊 Example Output

The app provides:
- **Total Portfolio Value**: Sum of all investments
- **Number of Holdings**: Count of different investments
- **HHI Index**: Raw HHI value
- **Normalized HHI**: Scaled diversification metric
- **Diversification Level**: Human-readable assessment
- **AI Commentary**: Detailed analysis and recommendations from Gemini

## 🔐 Security & Privacy

- PDF files are processed locally and stored temporarily
- Temporary files are deleted immediately after analysis
- API keys can be entered securely (masked input) or via environment variables
- Only portfolio data is sent to Google Gemini for analysis

## 🐛 Troubleshooting

### Common Issues

**"API key not configured"**
- Make sure you've entered your API key in the sidebar
- Or set `GEMINI_API_KEY` in your `.env` file

**"Error reading PDF"**
- Ensure the PDF is from B3 and follows the expected format
- Check that the file is not corrupted
- Verify the file is a valid PDF

**"Module not found" errors**
- Run `pip install -r requirements.txt` again
- Make sure your virtual environment is activated

**Analysis takes too long**
- Large PDFs may take longer to process
- The AI analysis typically takes 10-30 seconds
- Check your internet connection (API calls require internet)

## 📚 Dependencies

Key dependencies:
- `streamlit`: Web application framework
- `pydantic-ai`: AI agent framework
- `google-generativeai`: Google Gemini API
- `pypdf2`: PDF processing
- `pandas`: Data manipulation
- `python-dotenv`: Environment variable management

See `requirements.txt` for the complete list.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is for educational and personal use.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Uses [Pydantic-AI](https://ai.pydantic.dev/) for agent framework

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the example files in the repository
3. Create an issue on the project repository

---

**Happy Investing! 📈💰**
