import os, json, random, streamlit as st
try:
    import openai
except ImportError:
    openai = None
from typing import Dict, Any, List

class AIEngine:
    def __init__(self):
        key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.client = openai.OpenAI(api_key=key) if key and openai else None

    def generate_learning_content(self, subject:str, topic:str, level:int)->str:
        if self.client:
            prompt = f"Explain {topic} in {subject} for level {level} student with key points and example."
            try:
                resp = self.client.chat.completions.create(model="gpt-3.5-turbo",
                    messages=[{"role":"user","content":prompt}], max_tokens=500, temperature=0.7)
                return resp.choices[0].message.content
            except Exception as e:
                st.error(str(e))
        # fallback
        return f"### {topic}\nThis is placeholder content for {subject} at level {level}. Connect your API key for richer explanations."

    def generate_question(self, subject:str, topic:str, level:int)->Dict[str,Any]:
        if self.client:
            prompt = f"Create a {['easy','medium','hard'][level-1]} MCQ about {topic} ({subject}) in JSON."
            try:
                resp = self.client.chat.completions.create(model="gpt-3.5-turbo",
                        messages=[{"role":"user","content":prompt}], max_tokens=300, temperature=0.7)
                try:
                    return json.loads(resp.choices[0].message.content)
                except json.JSONDecodeError:
                    pass
            except Exception as e:
                st.error(str(e))
        # fallback random
        options = ["A","B","C","D"]
        correct = random.choice(options)
        return {"question": f"Sample {topic} question", "options": options,
                "correct_answer": correct, "explanation": "placeholder"}

    def generate_quiz_questions(self, content: str) -> List[Dict[str, Any]]:
        """
        Generates multiple-choice quiz questions based on the provided content.
        """
        # Example implementation (replace with actual AI logic)
        questions = [
            {
                "question": "What is the main topic of the content?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "Explanation for the correct answer."
            },
            # Add more questions dynamically based on content
        ]
        return questions

    def generate_similar_questions(self, incorrect_questions: List[str]) -> List[Dict[str, Any]]:
        """
        Generates similar questions based on the incorrect ones.
        """
        # Example implementation (replace with actual AI logic)
        similar_questions = [
            {
                "question": f"Similar question to: {q}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option B",
                "explanation": "Explanation for the correct answer."
            }
            for q in incorrect_questions
        ]
        return similar_questions