"""
Investment Portfolio PDF Extractor using pydantic-ai
Extracts investment names and values from unstructured PDF documents.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import base64
import io

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
import pypdf


#===== Setup =====
provider = GoogleProvider(api_key=GEMINI_API_KEY)
model = GoogleModel(provider=provider, model_name='gemini-2.5-flash')
pdf_path = PDF_PATH

# Define the structured output model
class Investment(BaseModel):
    """Represents a single investment in the portfolio."""
    name: str = Field(description="The name or ticker of the investment")
    value: float = Field(description="The current value of the investment in the portfolio's currency")
    currency: str = Field(default="USD", description="Currency of the value")


class PortfolioData(BaseModel):
    """Complete portfolio extraction result."""
    investments: List[Investment] = Field(description="List of all investments found in the portfolio")
    total_value: float = Field(description="Total portfolio value if stated, otherwise sum of investments")
    currency: str = Field(default="USD", description="Primary currency of the portfolio")


# Define dependencies for the agent
@dataclass
class PortfolioDeps:
    """Dependencies passed to the agent."""
    pdf_path: Path
    

# Create the agent with GPT-4 Vision capabilities
agent = Agent(
    model=model,
    result_type=PortfolioData,
    deps_type=PortfolioDeps,
    system_prompt=(
        "You are an expert financial analyst specializing in portfolio analysis. "
        "Your task is to extract investment information from portfolio documents that may have varying formats. "
        "\n\n"
        "When analyzing a portfolio document:\n"
        "1. Identify all investment holdings (stocks, bonds, funds, ETFs, etc.)\n"
        "2. Extract the exact name for each investment\n"
        "3. Find the current value for each investment\n"
        "4. Identify the currency being used\n"
        "5. Calculate or extract the total portfolio value\n"
        "\n"
        "Be thorough and accurate. If you find percentages, allocations, or quantities, "
        "focus on extracting the actual monetary values. Handle various formats including "
        "tables, lists, and narrative text."
    ),
)


@agent.tool
async def read_pdf_as_text(ctx: RunContext[PortfolioDeps]) -> str:
    """Extract text content from the PDF file."""
    pdf_path = ctx.deps.pdf_path
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text_content = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = pypdf.PdfReader(file)
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text = page.extract_text()
            text_content.append(f"--- Page {page_num} ---\n{text}\n")
    
    return "\n".join(text_content)


@agent.tool
async def read_pdf_as_images(ctx: RunContext[PortfolioDeps]) -> List[str]:
    """
    Convert PDF pages to base64-encoded images for vision analysis.
    Returns list of base64 image strings.
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return ["pdf2image not available - install with: pip install pdf2image"]
    
    pdf_path = ctx.deps.pdf_path
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Convert PDF to images
    images = convert_from_path(str(pdf_path), dpi=150)
    
    base64_images = []
    for img in images:
        # Convert PIL Image to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        base64_images.append(f"data:image/png;base64,{img_base64}")
    
    return base64_images


async def extract_portfolio_data(pdf_path: str | Path) -> PortfolioData:
    """
    Main function to extract investment data from a PDF.
    
    Args:
        pdf_path: Path to the PDF file containing portfolio information
        
    Returns:
        PortfolioData object with extracted investments and values
    """
    pdf_path = Path(pdf_path)
    deps = PortfolioDeps(pdf_path=pdf_path)
    
    # Run the agent with a prompt to analyze the portfolio
    result = await agent.run(
        "Please analyze this portfolio document and extract all investment holdings with their values. "
        "Use the available tools to read the PDF content, either as text or as images if the layout is complex. "
        "Make sure to capture all investments accurately.",
        deps=deps,
    )
    
    return result.data


# Example usage
async def main():
    """Example of how to use the portfolio extractor."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_portfolio.pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    print(f"Extracting portfolio data from: {pdf_path}")
    
    try:
        portfolio = await extract_portfolio_data(pdf_path)
        
        # Print results as formatted JSON
        print("\n" + "="*50)
        print("PORTFOLIO EXTRACTION RESULTS")
        print("="*50 + "\n")
        
        print(portfolio.model_dump_json(indent=2))
        
        print("\n" + "="*50)
        print(f"Total Investments Found: {len(portfolio.investments)}")
        print(f"Total Portfolio Value: {portfolio.currency} {portfolio.total_value:,.2f}")
        print("="*50)
        
    except Exception as e:
        print(f"Error extracting portfolio data: {e}")
        raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())