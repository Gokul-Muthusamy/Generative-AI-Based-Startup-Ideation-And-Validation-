from ai_engine.llm.gemini_service import gemini_service


class SuggestionAgent:
    """
    Suggestion Agent:
    Recommends new features, future scope, ways to improve uniqueness, and government schemes/funding opportunities.
    """

    def execute(self, startup_name, domain, problem, solution, location=""):
        prompt = f"""
        ROLE: You are an expert Startup Advisor and Government Grant Specialist.
        TASK: Provide AI suggestions for the generated startup idea.
        
        STARTUP: {startup_name} (Domain: {domain})
        PROBLEM: {problem}
        SOLUTION: {solution}
        LOCATION: {location if location else "Global"}
        
        Return a JSON object with a single key "swot" containing a formatted Markdown string.
        The markdown string MUST contain the following sections:
        - **New Features & Improvements:** 3-4 bullet points on how to make the product more unique.
        - **Future Scope:** What this could evolve into over the next 3-5 years.
        - **Possible Technologies:** Next-gen technologies that could be integrated (e.g. AI agents, blockchain).
        - **Funding Opportunities:** Potential government schemes, incubators, or grants relevant to the domain and location.
        """

        try:
            response = gemini_service.generate_content(prompt, response_schema_json=True)
            if response and isinstance(response, dict) and 'swot' in response:
                return response['swot']
        except Exception:
            pass

        return "**New Features & Improvements:**\n- Integrate predictive AI models tailored for Tamil Nadu & Indian market users\n- Expand to B2B enterprise clients & regional college incubators\n\n**Future Scope:**\n- Multi-lingual Tamil & English AI assistant support\n- Mobile app companion for iOS and Android\n\n**Funding Opportunities:**\n- StartupTN TanSEED Grant Scheme (up to ₹10 Lakhs equity-free seed grant)\n- EDII-TN Innovation Voucher Programme (IVP-A & IVP-B)\n- TANSIM Startup Tamil Nadu Incubation support\n- Startup India Seed Fund Scheme (SISFS)."


suggestion_agent = SuggestionAgent()
