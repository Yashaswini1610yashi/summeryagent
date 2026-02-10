from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

class Summarizer:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

    def generate_summary(self, text: str, mode: str = "Detailed Summary", target_lang: str = "English") -> str:
        """Generate a structured summary based on the specified mode and language."""
        
        modes = {
            "Short Summary": "a concise 2-3 sentence overview.",
            "Detailed Summary": "a comprehensive analysis with detailed sections.",
            "Bullet Points": "a list of the most important takeaways.",
            "Explain Like I’m 5": "a very simple explanation that a child could understand."
        }
        
        mode_desc = modes.get(mode, modes["Detailed Summary"])
        
        template = """
        You are a professional AI document analyst. 
        Analyze the following text and provide a structured summary in {target_lang}.
        
        The summary must follow this exact structure:
        - **Main Topic**: [The primary subject of the document]
        - **Key Points**: [A summary of the core arguments or facts]
        - **Important Insights**: [Deeper observations or critical data points]
        - **Final Conclusion**: [The overall takeaway or ending sentiment]
        
        Summary Mode: {mode_desc}
        
        Text to analyze:
        {text}
        
        Strict Translation Rule:
        The output must be entirely in {target_lang}. Preserve the original meaning accurately.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        chain = prompt | self.llm | StrOutputParser()
        
        # We only pass a portion of the text if it's too large, or better, we could summarize chunks then merge.
        # For simplicity in this version, we take the first 10k tokens (handled by Gemini's large context).
        return chain.invoke({
            "text": text[:30000], # Gemini 1.5 handles large context, but let's be safe for initial summary
            "mode_desc": mode_desc,
            "target_lang": target_lang
        })
