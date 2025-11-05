# Portfolio Analyzer - Architecture Notes

## Overview

The `portfolio_analyzer.py` module has been updated to wrap the functionality from `pydantic_diversification_analyst_sup.py`, implementing a multi-agent architecture for portfolio analysis.

## Architecture Changes

### Previous Design
- Direct PDF parsing using PyPDF2 with regex patterns
- Single-agent approach
- Tightly coupled PDF extraction and analysis

### Current Design (Multi-Agent)
- **Agent 1**: PDF Reader (`pydantic_pdf_reader.py`)
  - Extracts investment data from PDF files
  - Uses Google Gemini's multimodal capabilities
  - Can process both text and images from PDFs
  - Runs as a subprocess for modularity

- **Agent 2**: Diversification Analyzer (`portfolio_analyzer.py`)
  - Calculates HHI and normalized HHI metrics
  - Provides AI-powered analysis and recommendations
  - Calls PDF reader agent via subprocess

## Key Components

### 1. PDF Reader Agent (`pydantic_pdf_reader.py`)

**Input**: PDF file path (via command-line argument)

**Output**: Formatted text with investment data
```
Portfolio Investments:

  * **ITUB4** - R$ 1,000.00
  * **PETR4** - R$ 2,500.00

Total Portfolio Value: R$ 3,500.00
```

**Tools Available to Agent**:
- `read_pdf_as_text()`: Extract text content from PDF
- `read_pdf_as_images()`: Convert PDF pages to images for vision analysis

### 2. Diversification Analyzer (`portfolio_analyzer.py`)

**Input**: PDF file path

**Process**:
1. Calls PDF reader agent as subprocess
2. Parses output using regex patterns:
   - Names: `\*\s+\*\*(.+?)\*\*`
   - Values: `R\$ ([\d,]+\.\d{2})`
3. Calculates HHI metrics
4. Runs AI analysis for insights

**Tools Available to Agent**:
- `read_portfolio_pdf()`: Formats portfolio data for AI
- `calculate_diversification_metrics()`: Computes HHI metrics

**Output**: `PortfolioAnalysis` Pydantic model with:
- Total value
- Number of holdings
- HHI and normalized HHI
- Diversification level
- AI commentary

### 3. Streamlit App (`app.py`)

**Purpose**: User interface for the analyzer

**Features**:
- File upload
- API key configuration
- Progress indicators
- Results visualization
- Export functionality

## Data Flow

```
User uploads PDF
    ↓
Streamlit App (app.py)
    ↓
Portfolio Analyzer (portfolio_analyzer.py)
    ↓
Subprocess call → PDF Reader Agent (pydantic_pdf_reader.py)
    ↓                   ↓
    ↓              Google Gemini API
    ↓                   ↓
    ↓              Extracts investments
    ↓                   ↓
Parses formatted output ←
    ↓
Calculates HHI metrics
    ↓
AI Analysis → Google Gemini API
    ↓
Returns PortfolioAnalysis
    ↓
Streamlit displays results
```

## Benefits of Multi-Agent Architecture

1. **Modularity**: Each agent has a specific, well-defined responsibility
2. **Reusability**: PDF reader can be used independently
3. **Flexibility**: Easy to swap out or upgrade individual components
4. **Scalability**: Can add more specialized agents for additional features
5. **Robustness**: AI-based PDF extraction handles varying formats better than regex

## Environment Variables

Both agents require:
- `GEMINI_API_KEY`: Google Gemini API key

The subprocess call passes the current environment, ensuring the PDF reader has access to the API key.

## Error Handling

- PDF file not found
- PDF reader script not found
- Subprocess timeout (60 seconds)
- Subprocess failure (stderr captured)
- Empty extraction results
- API errors (from Google Gemini)

## Future Enhancements

Potential improvements to consider:

1. **Caching**: Cache PDF extraction results to avoid redundant API calls
2. **Batch Processing**: Support multiple PDF files
3. **Asset Class Analysis**: Extend to analyze diversification across asset classes
4. **Historical Tracking**: Store and compare portfolio changes over time
5. **Visualization**: Add charts for portfolio composition
6. **Additional Metrics**: Implement more portfolio analysis metrics (Sharpe ratio, etc.)
7. **Direct Integration**: Instead of subprocess, could import and call functions directly

## Testing

To test the components independently:

**Test PDF Reader**:
```bash
export GEMINI_API_KEY="your_key"
python pydantic_pdf_reader.py path/to/portfolio.pdf
```

**Test Analyzer (standalone)**:
```bash
export GEMINI_API_KEY="your_key"
export PDF_PATH="path/to/portfolio.pdf"
python pydantic_diversification_analyst_sup.py
```

**Test Streamlit App**:
```bash
streamlit run app.py
```
