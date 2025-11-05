"""
Portfolio Diversification Analyzer Module for Streamlit App

This module provides the core functionality for analyzing investment portfolios
using Google Gemini and calculating diversification metrics.
Wraps the functionality from pydantic_diversification_analyst_sup.py.
"""

import os
import re
import pandas as pd
import subprocess
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


# ===== Data Models =====

class Investment(BaseModel):
    """Represents a single investment holding."""
    name: str
    value: float
    percentage: float = 0.0


class PortfolioAnalysis(BaseModel):
    """Results of portfolio diversification analysis."""
    total_value: float = Field(description="Total portfolio value")
    num_holdings: int = Field(description="Number of holdings")
    hhi: float = Field(description="Herfindahl-Hirschman Index (0-1)")
    normalized_hhi: float = Field(description="Normalized HHI (0-1)")
    diversification_level: str = Field(description="Diversification assessment")
    commentary: str = Field(description="Detailed analysis commentary")


@dataclass
class PortfolioDependencies:
    """Dependencies for the portfolio agent."""
    pdf_path: str


# ===== Portfolio Analyzer Class =====

class PortfolioAnalyzer:
    """
    Main class for portfolio diversification analysis.
    Integrates Google Gemini agent with portfolio metrics calculation.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the portfolio analyzer.

        Args:
            api_key: Google Gemini API key. If not provided, will use GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment")

        # Initialize Google Gemini provider and model
        self.provider = GoogleProvider(api_key=self.api_key)
        self.model = GoogleModel(provider=self.provider, model_name='gemini-2.5-flash')

        # Initialize the agent
        self._setup_agent()

    def _setup_agent(self):
        """Setup the Pydantic-AI agent with tools."""
        self.agent: Agent[PortfolioDependencies, PortfolioAnalysis] = Agent(
            self.model,
            system_prompt="""You are a financial portfolio analyst specializing in diversification analysis.

            Your task is to analyze investment portfolios using the Herfindahl-Hirschman Index (HHI) and provide
            clear, actionable insights about portfolio diversification.

            HHI Interpretation Guidelines:
            - HHI close to 1.0 (or normalized HHI close to 1.0): Highly concentrated portfolio (low diversification)
            - HHI around 0.1-0.3: Moderately concentrated
            - HHI below 0.1: Well diversified

            Normalized HHI ranges from 0 (perfect diversification) to 1 (complete concentration).

            Provide practical, friendly advice on portfolio diversification. Be specific about numbers
            and provide actionable recommendations."""
        )

        # Register tools
        @self.agent.tool
        async def read_portfolio_pdf(ctx: RunContext[PortfolioDependencies]) -> str:
            """Read and parse the portfolio PDF file."""
            investments = self.extract_portfolio_from_pdf(ctx.deps.pdf_path)

            result = f"Portfolio contains {len(investments)} investments:\n\n"
            for inv in investments.name.unique():
                invdata = investments.query(f"name == '{inv}'")
                result += f"- {inv}: ${invdata.value.iloc[0]:,.2f}\n"

            return result

        @self.agent.tool
        async def calculate_diversification_metrics(ctx: RunContext[PortfolioDependencies]) -> dict:
            """Calculate HHI and diversification metrics for the portfolio."""
            investments = self.extract_portfolio_from_pdf(ctx.deps.pdf_path)
            metrics = self.calculate_hhi_metrics(investments)

            return {
                "num_holdings": len(investments),
                "total_value": metrics["total_value"],
                "hhi": round(metrics["hhi"], 4),
                "normalized_hhi": round(metrics["normalized_hhi"], 4),
                "investments": [
                    {
                        "name": inv,
                        "value": investments.query(f"name == '{inv}'").value.iloc[0],
                        "percentage": round(investments.query(f"name == '{inv}'").weights.iloc[0], 2)
                    }
                    for inv in investments.name.unique()
                ]
            }

    @staticmethod
    def extract_portfolio_from_pdf(pdf_path: str) -> pd.DataFrame:
        """
        Extract investment data from a B3 PDF file using the pydantic_pdf_reader agent.
        This function calls the PDF reader agent as a subprocess to extract structured data.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            DataFrame with investment names and values
        """
        try:
            # Get the directory where this script is located
            script_dir = Path(__file__).parent
            pdf_reader_script = script_dir / 'pydantic_pdf_reader.py'

            # Check if the PDF reader script exists
            if not pdf_reader_script.exists():
                raise FileNotFoundError(
                    f"pydantic_pdf_reader.py not found at {pdf_reader_script}. "
                    "Make sure it's in the same directory as portfolio_analyzer.py"
                )

            # Run the PDF reader agent as a subprocess
            result = subprocess.run(
                ['python', str(pdf_reader_script), pdf_path],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ}  # Pass current environment (including GEMINI_API_KEY)
            )

            # Check if subprocess completed successfully
            if result.returncode != 0:
                raise Exception(f"pydantic_pdf_reader.py failed with error: {result.stderr}")

            # Get the text output from the subprocess
            text_output = result.stdout

            # Parse investment names and values from the text output using regex
            names = re.findall(r'\*\s+\*\*(.+?)\*\*', text_output)
            values = re.findall(r'R\$ ([\d,]+\.\d{2})', text_output)
            values = values[:-1]  # Removing total portfolio value

            # Convert values to float (removing commas)
            values = [float(v.replace(',', '')) for v in values]

            # Create DataFrame
            investments = pd.DataFrame({
                'name': names,
                'value': values
            })

            if investments.empty:
                raise Exception("No investments found in PDF. The PDF format may not be supported.")

        except FileNotFoundError as e:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}") from e
        except subprocess.TimeoutExpired:
            raise Exception(f"PDF processing timed out for: {pdf_path}")
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}") from e

        return investments

    @staticmethod
    def calculate_hhi_metrics(investments: pd.DataFrame) -> dict:
        """
        Calculate HHI and normalized HHI for a portfolio.

        HHI = Σ(wi²) where wi is the weight of each investment
        Normalized HHI = (HHI - 1/n) / (1 - 1/n) where n is number of investments

        Args:
            investments: DataFrame with investment data

        Returns:
            Dictionary with HHI metrics
        """
        total_value = investments['value'].sum()
        investments['weights'] = investments['value'] / total_value
        investments['weights_squared'] = investments['weights'] ** 2
        hhi = investments['weights_squared'].sum()

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

    async def analyze_portfolio(self, pdf_path: str) -> PortfolioAnalysis:
        """
        Analyze a portfolio PDF and return diversification analysis.

        Args:
            pdf_path: Path to the PDF file containing portfolio data

        Returns:
            PortfolioAnalysis object with HHI metrics and commentary
        """
        deps = PortfolioDependencies(pdf_path=pdf_path)

        result = await self.agent.run(
            """Analyze the portfolio from the PDF file.

            1. Read the portfolio data
            2. Calculate the diversification metrics including HHI and normalized HHI
            3. Provide a comprehensive analysis of the portfolio's diversification level
            4. Give specific recommendations based on the HHI values

            Be specific about the numbers and provide actionable insights.""",
            deps=deps,
        )

        return result.output

    def get_diversification_level(self, normalized_hhi: float) -> str:
        """
        Get a human-readable diversification level based on normalized HHI.

        Args:
            normalized_hhi: The normalized HHI value (0-1)

        Returns:
            String describing the diversification level
        """
        if normalized_hhi >= 0.8:
            return "Highly Concentrated (Poor Diversification)"
        elif normalized_hhi >= 0.5:
            return "Moderately Concentrated"
        elif normalized_hhi >= 0.2:
            return "Moderately Diversified"
        else:
            return "Well Diversified"
