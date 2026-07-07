"""
llm.py

Handles communication with the Gemini LLM.

Project : AgriAssist
"""

import os

import google.generativeai as genai
from dotenv import load_dotenv

from config import LLM_MODEL
from logger import get_logger

logger = get_logger(__name__)

load_dotenv()


class GeminiLLM:
    """
    Wrapper around Google Gemini.
    """

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if api_key is None:
            raise ValueError("GEMINI_API_KEY not found in .env")

        genai.configure(api_key=api_key)

        logger.info("Gemini API Initialized")

        self.model = genai.GenerativeModel(
            model_name=LLM_MODEL
        )

    def generate(
        self,
        prompt: str
    ) -> str:
        """
        Generate response from Gemini.
        """

        try:

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:

            logger.exception(e)

            return "Sorry, I couldn't generate a response."


if __name__ == "__main__":

    llm = GeminiLLM()

    question = input("Ask : ")

    answer = llm.generate(question)

    print("\n")

    print("=" * 70)

    print(answer)