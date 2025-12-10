"""
Portfolio Diversification Analyzer Module for Streamlit App

This module provides the core functionality for analyzing investment portfolios
using Google Gemini via DSPy and calculating diversification metrics.
"""

import os
import re
import pandas as pd
import subprocess
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field
import dspy
from dspy.functional import TypedPredictor


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


# ===== DSPy Signatures =====

class AnalyzePortfolioDiversification(dspy.Signature):
    """Analyze investment portfolio diversification using HHI metrics."""
    
    portfolio_data: str = dspy.InputField(desc="Portfolio holdings with names and values")
    metrics_data: str = dspy.InputField(desc="Calculated HHI and diversification metrics")
    analysis: PortfolioAnalysis = dspy.OutputField(desc="Complete portfolio analysis with HHI metrics and commentary")


# ===== Portfolio Analyzer Class =====

class PortfolioAnalyzer:
    """
    Main class for portfolio diversification analysis.
    Integrates Google Gemini via DSPy with portfolio metrics calculation.
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

        # Configure DSPy with Google Gemini
        self._setup_dspy()
        
        # Initialize the predictor
        self.predictor = TypedPredictor(AnalyzePortfolioDiversification)

    def _setup_dspy(self):
        """Setup DSPy with Google Gemini model."""
        lm = dspy.LM(
            model='google/gemini-2.5-flash',
            api_key=self.api_key,
            temperature=0.7
        )
        dspy.configure(lm=lm)

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
            # Removing last value, which does not correspond to an investment
            values = values[:-1]

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
        investments = investments.assign(
            weights=lambda df: df['value'] / total_value,
            weights_squared=lambda df: df['weights'] ** 2
        )
        hhi = investments['weights_squared'].sum()

        n = len(investments)
        if n > 1:
            normalized_hhi = (hhi - 1/n) / (1 - 1/n)
        else:
            normalized_hhi = 1.0  # Single investment = maximum concentration

        return {
            "hhi": hhi,
            "normalized_hhi": normalized_hhi,
            "total_value": total_value,
            "investments_df": investments
        }

    def analyze_portfolio(self, pdf_path: str) -> PortfolioAnalysis:
        """
        Analyze a portfolio PDF and return diversification analysis.

        Args:
            pdf_path: Path to the PDF file containing portfolio data

        Returns:
            PortfolioAnalysis object with HHI metrics and commentary
        """
        # Extract portfolio data
        investments = self.extract_portfolio_from_pdf(pdf_path)
        
        # Calculate metrics
        metrics = self.calculate_hhi_metrics(investments)
        investments_with_weights = metrics['investments_df']
        
        # Format portfolio data for DSPy
        portfolio_data = f"Portfolio contains {len(investments)} investments:\n\n"
        for _, row in investments_with_weights.iterrows():
            portfolio_data += f"- {row['name']}: ${row['value']:,.2f} ({row['weights']*100:.2f}%)\n"
        
        # Format metrics data for DSPy
        metrics_data = f"""
Total Portfolio Value: ${metrics['total_value']:,.2f}
Number of Holdings: {len(investments)}
HHI (Herfindahl-Hirschman Index): {metrics['hhi']:.4f}
Normalized HHI: {metrics['normalized_hhi']:.4f}

HHI Interpretation Guidelines:
- HHI close to 1.0 (or normalized HHI close to 1.0): Highly concentrated portfolio (low diversification)
- HHI around 0.1-0.3: Moderately concentrated
- HHI below 0.1: Well diversified
- Normalized HHI ranges from 0 (perfect diversification) to 1 (complete concentration)

Investment Details:
{portfolio_data}
"""
        
        # Get diversification level
        diversification_level = self.get_diversification_level(metrics['normalized_hhi'])
        
        # Create analysis using DSPy
        try:
            result = self.predictor(
                portfolio_data=portfolio_data,
                metrics_data=metrics_data
            )
            
            # Ensure all required fields are present
            analysis = result.analysis
            
            # Override with calculated values to ensure accuracy
            analysis.total_value = metrics['total_value']
            analysis.num_holdings = len(investments)
            analysis.hhi = round(metrics['hhi'], 4)
            analysis.normalized_hhi = round(metrics['normalized_hhi'], 4)
            analysis.diversification_level = diversification_level
            
            return analysis
            
        except Exception as e:
            # Fallback: create analysis manually if DSPy fails
            print(f"DSPy prediction failed: {e}. Using fallback analysis.")
            
            commentary = self._generate_fallback_commentary(
                investments_with_weights,
                metrics,
                diversification_level
            )
            
            return PortfolioAnalysis(
                total_value=metrics['total_value'],
                num_holdings=len(investments),
                hhi=round(metrics['hhi'], 4),
                normalized_hhi=round(metrics['normalized_hhi'], 4),
                diversification_level=diversification_level,
                commentary=commentary
            )

    def _generate_fallback_commentary(
        self, 
        investments: pd.DataFrame, 
        metrics: dict, 
        diversification_level: str
    ) -> str:
        """Generate fallback commentary if DSPy fails."""
        
        total_value = metrics['total_value']
        num_holdings = len(investments)
        hhi = metrics['hhi']
        normalized_hhi = metrics['normalized_hhi']
        
        # Get top 3 holdings
        top_holdings = investments.nlargest(3, 'value')
        
        commentary = f"""Your portfolio, comprising {num_holdings} investments with a total value of ${total_value:,.2f}, has been analyzed for diversification.

Based on the HHI of {hhi:.4f}, your portfolio is classified as **{diversification_level}**. The Normalized HHI of {normalized_hhi:.4f} provides additional context about your diversification relative to the number of holdings.

**Top Holdings:**
"""
        for _, row in top_holdings.iterrows():
            commentary += f"- {row['name']}: ${row['value']:,.2f} ({row['weights']*100:.1f}%)\n"
        
        commentary += "\n**Recommendations:**\n"
        
        if normalized_hhi < 0.2:
            commentary += """1. **Maintain Your Diversification Strategy:** Your portfolio shows excellent diversification. Continue your current approach.
2. **Regular Monitoring:** Periodically review your portfolio to ensure it remains aligned with your goals.
3. **Consider Sectoral Diversification:** Ensure your investments span different sectors and asset classes."""
        elif normalized_hhi < 0.5:
            commentary += """1. **Consider Rebalancing:** Your portfolio shows moderate concentration. Consider redistributing from larger holdings to smaller positions.
2. **Add New Positions:** Consider adding new, uncorrelated investments to improve diversification.
3. **Monitor Large Holdings:** Keep an eye on your largest positions to prevent excessive concentration."""
        else:
            commentary += """1. **Urgent Rebalancing Needed:** Your portfolio is highly concentrated. Consider significantly reducing your largest positions.
2. **Diversify Immediately:** Add multiple new investments across different sectors and asset classes.
3. **Risk Management:** High concentration increases risk. Prioritize diversification to protect your portfolio."""
        
        return commentary

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