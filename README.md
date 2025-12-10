# agentic-systems-studies
Repo to save and share whatever I'm studying about LLMs and its applications.

This repo contains a few different versions of simple agents that analyze an investment portfolio with tools to calculate an HHI index and give recommendations as to how risk can be minimized. As the only metric calculating tool available right now is an HHI index calculator, portfolio diversification is the main point of analysis as of now. In folder "aux/" you can find a pdf generator that generates relatively random B3 portfolio pdfs for you to test, and shell scripts to run both agent's versions for the pdfs generated in aux/. The agent itself is in scripts pydantic_diversification_analyst.py (v0.1, uses a regex to find relevant information on the pdf files) and pydantic_diversification_analyst_sup.py (v0.2, uses another agent to read through pdf contents). pydantic_pdf_reader.py is a pdf-reading agent, called by pydantic_diversification_analyst_sup.py, and portfolio_analyzer.py is a wrapper for pydantic_diversification_analyst_sup.py to call it into a streamlit app. This app hasn't been deployed yet because it sometimes breaks, as pydantic_diversification_analyst_sup.py not always respects its instructions to only provide structured output.

<b>Instructions:</b> if you wish to use it without any adaptations to code, you need to have an investment portfolio from B3 (or use the pdf_generator in folder aux/) and a Gemini API key, and you should export them (or their path, in the case of the pdf) as environment variables called PDF_PATH and GEMINI_API_KEY, respectively.

<b>Next steps:</b>

- Act upon agent evaluation findings: first version has a problem on its pdf-reading tool, second version fixes this problem but is very intensive in gemini use, usage quotas are exceeded fast;
- Manage to somehow ensure agent's output is always structured, so that streamlit app works always (instead of more often than not).
- Improve agent capabilities by including more diversification measures so that final analysis is more robust  -- include Sharpe ratio, effective number of assets, Gini coefficients, diversification ratios, measures of variance (these depend on performance data), average pairwise correlation, effective number of bets and diversification score (Choueifaity & Coignard, 2008) as metrics;
- Analyze feasibility and, if possible, create a benchmark comparing agent's performance with current market practices.



