"""
Portfolio Diversification Analyzer - Streamlit App

A Streamlit application that uses an agent to analyze investment portfolio
diversification from PDF files.
"""

import streamlit as st
import os
import asyncio
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from portfolio_analyzer_dspy import PortfolioAnalyzer
#from portfolio_analyzer import PortfolioAnalyzer

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Portfolio Diversification Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def get_diversification_color(normalized_hhi: float) -> str:
    """Return color based on diversification level."""
    if normalized_hhi >= 0.8:
        return "🔴"
    elif normalized_hhi >= 0.5:
        return "🟠"
    elif normalized_hhi >= 0.2:
        return "🟡"
    else:
        return "🟢"


def display_metrics(analysis):
    """Display portfolio metrics in a nice layout."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Portfolio Value",
            value=f"R$ {analysis['total_value']:,.2f}"
        )

    with col2:
        st.metric(
            label="Number of Holdings",
            value=analysis['num_holdings']
        )

    with col3:
        diversification_emoji = get_diversification_color(analysis.normalized_hhi)
        st.metric(
            label="HHI Index",
            value=f"{analysis['hhi']:.4f}"
        )

    with col4:
        st.metric(
            label="Normalized HHI",
            value=f"{diversification_emoji} {analysis['normalized_hhi']:.4f}"
        )


def main():
    """Main application function."""

    # Header
    st.markdown('<p class="main-header">📊 Portfolio Diversification Analyzer</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key input
        st.subheader("Google Gemini API Key")
        api_key_input = st.text_input(
            "Enter your API key",
            type="password",
            help="Your Google Gemini API key. You can also set this in a .env file as GEMINI_API_KEY",
            value=""
        )

        # Use API key from input or environment
        api_key = api_key_input if api_key_input else os.getenv('GEMINI_API_KEY')

        if api_key:
            st.success("✅ API key configured")
        else:
            st.warning("⚠️ Please enter your API key")

        st.markdown("---")

        # Information section
        st.subheader("ℹ️ About")
        st.info("""
        This tool analyzes investment portfolio diversification using:

        - **HHI (Herfindahl-Hirschman Index)**: Measures portfolio concentration
        - **Normalized HHI**: Scaled version (0-1) for easier interpretation
        - **AI Analysis**: Google Gemini provides detailed insights

        **Interpretation:**
        - 🟢 < 0.2: Well diversified
        - 🟡 0.2-0.5: Moderately diversified
        - 🟠 0.5-0.8: Moderately concentrated
        - 🔴 > 0.8: Highly concentrated
        """)

        st.markdown("---")
        st.caption("Powered by Google Gemini 2.5 Flash")

    # Main content
    st.subheader("📄 Upload Your Portfolio PDF")
    st.write("Upload a B3 investment portfolio PDF file to analyze its diversification.")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your investment portfolio PDF file from B3"
    )

    # Analysis button and logic
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        # Display file details
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }

        with st.expander("📋 File Details"):
            st.json(file_details)

        # Analyze button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyze_button = st.button("🚀 Analyze Portfolio", type="primary", use_container_width=True)

        if analyze_button:
            if not api_key:
                st.error("❌ Please provide a Google Gemini API key in the sidebar.")
                return

            # Create temporary file to save uploaded PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            try:
                # Show progress
                with st.spinner("🔍 Analyzing your portfolio... This may take a few moments."):
                    # Initialize analyzer
                    analyzer = PortfolioAnalyzer(api_key=api_key)

                    # Run analysis
                    analysis = analyzer.analyze_portfolio(tmp_file_path)
                    #analysis = asyncio.run(analyzer.analyze_portfolio(tmp_file_path))

                st.success("✅ Analysis completed!")

                # Display results
                st.markdown("---")
                st.subheader("📊 Analysis Results")

                # Metrics
                display_metrics(analysis)

                # Diversification level
                st.markdown("---")
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.subheader("📈 Diversification Level")
                    diversification_emoji = get_diversification_color(analysis.normalized_hhi)
                    st.markdown(f"## {diversification_emoji} {analysis.diversification_level}")

                with col2:
                    st.subheader("🤖 AI Commentary")
                    st.markdown(analysis.commentary)

                # Detailed metrics explanation
                st.markdown("---")
                with st.expander("📚 Understanding Your Metrics"):
                    st.markdown(f"""
                    ### What do these numbers mean?

                    **HHI (Herfindahl-Hirschman Index): {analysis.hhi:.4f}**
                    - Calculated as the sum of squared weights of each investment
                    - Ranges from 1/n (perfect diversification) to 1 (complete concentration)
                    - Lower values indicate better diversification

                    **Normalized HHI: {analysis.normalized_hhi:.4f}**
                    - Scaled version of HHI ranging from 0 to 1
                    - 0 = Perfect diversification (all investments equally weighted)
                    - 1 = Complete concentration (all money in one investment)
                    - Your portfolio: {analysis.diversification_level}

                    **Number of Holdings: {analysis.num_holdings}**
                    - Total number of different investments in your portfolio
                    - More holdings doesn't always mean better diversification
                    - What matters is how the value is distributed across holdings
                    """)

                # Download option for results
                st.markdown("---")
                st.subheader("💾 Export Results")

                # Create a summary text
                summary_text = f"""
PORTFOLIO DIVERSIFICATION ANALYSIS REPORT
==========================================

Generated by Portfolio Diversification Analyzer

PORTFOLIO SUMMARY
-----------------
Total Value: R$ {analysis.total_value:,.2f}
Number of Holdings: {analysis.num_holdings}

DIVERSIFICATION METRICS
-----------------------
HHI Index: {analysis.hhi:.4f}
Normalized HHI: {analysis.normalized_hhi:.4f}
Diversification Level: {analysis.diversification_level}

AI ANALYSIS & RECOMMENDATIONS
------------------------------
{analysis.commentary}

==========================================
Note: This analysis is for informational purposes only and should not be considered
financial advice. Please consult with a qualified financial advisor for personalized
investment guidance.
"""

                st.download_button(
                    label="📥 Download Analysis Report",
                    data=summary_text,
                    file_name=f"portfolio_analysis_{uploaded_file.name.replace('.pdf', '')}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"❌ An error occurred during analysis: {str(e)}")
                st.exception(e)

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)

    else:
        # Show instructions when no file is uploaded
        st.info("👆 Please upload a portfolio PDF file to begin the analysis.")

        with st.expander("📖 How to use this tool"):
            st.markdown("""
            ### Step-by-step guide:

            1. **Get your API key**: Obtain a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
            2. **Enter API key**: Paste your API key in the sidebar (or set it in a `.env` file)
            3. **Upload PDF**: Upload your B3 investment portfolio PDF file
            4. **Analyze**: Click the "Analyze Portfolio" button
            5. **Review**: Examine the detailed analysis and recommendations
            6. **Export**: Download the analysis report for your records

            ### Supported file format:
            - B3 investment portfolio PDF files with investment names and values

            ### Privacy:
            - Your PDF is processed locally and temporarily
            - Files are deleted immediately after analysis
            - Only portfolio data is sent to Google Gemini for analysis
            """)


if __name__ == "__main__":
    main()
