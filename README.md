# agentic-systems-studies
Repo to save and share whatever I'm studying about LLMs and its applications.

As of now, this repo contains only a few versions of a simple agent that reads an investment portfolio (either by calling another agent as tool or by using pdf-to-string tools) listed on a B3 pdf and analyzes how diversified your investments are.

<b>Instructions:</b> if you wish to use it without any adaptations to code, you need to have an investment portfolio from B3 and a Gemini API key, and you should export them (or their path, in the case of the pdf) as environment variables called PDF_PATH and GEMINI_API_KEY, respectively.

<b>Next steps:</b>

- Improve agent capabilities by including more diversification measures so that final analysis is more robust  -- include Sharpe ratio, effective number of assets, Gini coefficients, diversification ratios, measures of variance (these depend on performance data), average pairwise correlation, effective number of bets and diversification score (Choueifaity & Coignard, 2008) as metrics;
    
- Analyze feasibility and, if possible, create a benchmark comparing agent's performance with current market practices.



