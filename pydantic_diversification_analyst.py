"""
Portfolio Diversification Analyzer using Pydantic-AI

This simple project uses pydantic-ai to create an agent that analyzes investment portfolios,
calculates the normalized Herfindahl-Hirschman Index (HHI), and provides diversification insights.
"""

import re
import pandas as pd
from dataclasses import dataclass
from typing import List
import PyPDF2
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


# ===== Setup =====

provider = GoogleProvider(api_key=GEMINI_API_KEY)
model = GoogleModel(provider=provider, model_name='gemini-2.5-flash')
pdf_path = 'posicao-2025-10-06.pdf'


# ===== Data Models =====
# create class Investment to store name, value, size in the total portfolio
class Investment(BaseModel):
    """Represents a single investment holding."""
    name: str
    value: float
    percentage: float = 0.0

# create class PortfolioAnalysis to store the results of the analysis that will be returned by the agent
class PortfolioAnalysis(BaseModel):
    """Results of portfolio diversification analysis."""
    total_value: float = Field(description="Total portfolio value")
    num_holdings: int = Field(description="Number of holdings")
    hhi: float = Field(description="Herfindahl-Hirschman Index (0-1)")
    normalized_hhi: float = Field(description="Normalized HHI (0-1)")
    diversification_level: str = Field(description="Diversification assessment")
    commentary: str = Field(description="Detailed analysis commentary")

# create class PortfolioDependencies to store the dependencies for the agent -- in this case, just the PDF path
@dataclass
class PortfolioDependencies:
    """Dependencies for the portfolio agent."""
    pdf_path: str


# ===== Helper Functions =====

def extract_portfolio_from_pdf(pdf_path: str) -> pd.DataFrame:
    """
    Extract investment data from a B3 PDF file.
    """
    results = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            results = {
                'name_values': [],
                'total_values': []
            }
    
            name_pattern = r'atualizado\s+(\S+)'
    
            value_pattern = r'Total\s+R\$\s*([\d.,]+)'
    
            name_matches = re.findall(name_pattern, text, re.IGNORECASE)
            results['name_values'] = [match.strip() for match in name_matches]
    
            value_matches = re.findall(value_pattern, text, re.IGNORECASE)
            results['inv_values'] = [f"R$ {match.strip()}" for match in value_matches]

            investments = pd.DataFrame({
                'name': pd.Series(results['name_values']),
                'value': pd.Series(results['inv_values'])
            })
            investments['value'] = (investments['value'].str.replace('\D', '', regex = True).astype(float)) / 100
            investments = investments.fillna(0)
    
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"Error reading PDF: {e}")
    
    return investments


def calculate_hhi_metrics(investments: pd.DataFrame) -> dict:
    """
    Calculate HHI and normalized HHI for a portfolio.
    
    HHI = Σ(wi²) where wi is the weight of each investment
    Normalized HHI = (HHI - 1/n) / (1 - 1/n) where n is number of investments
    """
    # Calculate total value
    total_value = investments['value'].sum()
    
    # Calculate weights
    investments['weights'] = (investments['value'] / total_value)
    
    # Calculate HHI 
    investments['weights_squared'] = investments['weights'] ** 2
    hhi = investments['weights_squared'].sum()
    
    # Calculate normalized HHI
    n = len(investments)
    if n > 1:
        normalized_hhi = (hhi - 1/n) / (1 - 1/n)
    else:
        normalized_hhi = 1.0  # Single investment = maximum concentration
    
    return {
        "hhi": hhi,
        "normalized_hhi": normalized_hhi,
        "total_value": total_value
    }


# ===== Pydantic-AI Agent Setup =====

# Create the agent with result type
portfolio_agent: Agent[PortfolioDependencies, PortfolioAnalysis] = Agent(
    model,
    #deps_type=PortfolioDependencies,
    #result_type=PortfolioAnalysis,
    system_prompt="""You are a financial portfolio analyst specializing in diversification analysis.
    
    Your task is to analyze investment portfolios using the Herfindahl-Hirschman Index (HHI) and provide
    clear, actionable insights about portfolio diversification.
    
    HHI Interpretation Guidelines:
    - HHI close to 1.0 (or normalized HHI close to 1.0): Highly concentrated portfolio (low diversification)
    - HHI around 0.1-0.3: Moderately concentrated
    - HHI below 0.1: Well diversified
    
    Normalized HHI ranges from 0 (perfect diversification) to 1 (complete concentration).
    
    Provide practical, friendly advice on portfolio diversification."""
)


@portfolio_agent.tool
async def read_portfolio_pdf(ctx: RunContext[PortfolioDependencies]) -> str:
    """Read and parse the portfolio PDF file."""
    investments = extract_portfolio_from_pdf(ctx.deps.pdf_path)
    
    # Format the data for the agent
    
    result = f"Portfolio contains {len(investments)} investments:\n\n"
    for inv in investments.name.unique():
        invdata = investments.query(f"name == '{inv}'")
        result += f"- {inv}: ${invdata.value.iloc[0]:,.2f}\n"
    
    return result


@portfolio_agent.tool
async def calculate_diversification_metrics(ctx: RunContext[PortfolioDependencies]) -> dict:
    """Calculate HHI and diversification metrics for the portfolio."""
    investments = extract_portfolio_from_pdf(ctx.deps.pdf_path)
    
    metrics = calculate_hhi_metrics(investments)
    
    return {
        "num_holdings": len(investments),
        "total_value": metrics["total_value"],
        "hhi": round(metrics["hhi"], 4),
        "normalized_hhi": round(metrics["normalized_hhi"], 4),
        "investments": [
            {"name": inv, "value": investments.query(f"name == '{inv}'").value.iloc[0], "percentage": round(investments.query(f"name == '{inv}'").weights.iloc[0], 2)}
            for inv in investments.name.unique()
        ]
    }


# ===== Main Function =====

async def analyze_portfolio(pdf_path: str) -> PortfolioAnalysis:
    """
    Analyze a portfolio PDF and return diversification analysis.
    
    Args:
        pdf_path: Path to the PDF file containing portfolio data
        
    Returns:
        PortfolioAnalysis object with HHI metrics and commentary
    """
    deps = PortfolioDependencies(pdf_path=pdf_path)
    
    result = await portfolio_agent.run(
        """Analyze the portfolio from the PDF file. 
        
        1. Read the portfolio data
        2. Calculate the diversification metrics including HHI and normalized HHI
        3. Provide a comprehensive analysis of the portfolio's diversification level
        4. Give specific recommendations based on the HHI values
        
        Be specific about the numbers and provide actionable insights.""",
        deps=deps,
        #result_type=PortfolioAnalysis
    )
    
    return result.output


# Running agent
import asyncio

analysis = asyncio.run(analyze_portfolio(pdf_path))

print(analysis)