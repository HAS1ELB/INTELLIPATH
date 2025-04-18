# Ajout dans un nouveau fichier: quiz_generator.py
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import json

class QuizQuestion(BaseModel):
    question: str = Field(description="La question posée")
    options: List[str] = Field(description="Les options de réponse")
    correct_answer: int = Field(description="L'index de la réponse correcte (0-3)")
    explanation: str = Field(description="Explication de la réponse correcte")

class QuizGenerator:
    def __init__(self):
        self.llm = OllamaLLM(model="llama3", temperature=0.7)
        self.parser = PydanticOutputParser(pydantic_object=QuizQuestion)
        
    def generate_quiz(self, topic, difficulty="medium", num_questions=5):
        """Génère un quiz sur un sujet donné"""
        quiz_questions = []
        
        for i in range(num_questions):
            prompt = PromptTemplate(
                template="""Génère une question de quiz sur le sujet {topic} avec une difficulté {difficulty}.
                La question doit avoir 4 options de réponse et une seule bonne réponse.
                Fournis également une explication détaillée de la réponse correcte.
                {format_instructions}
                """,
                input_variables=["topic", "difficulty"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )
            
            formatted_prompt = prompt.format(topic=topic, difficulty=difficulty)
            response = self.llm.invoke(formatted_prompt)
            
            try:
                question = self.parser.parse(response)
                quiz_questions.append(question.dict())
            except Exception as e:
                print(f"Erreur lors de l'analyse de la question: {e}")
                continue
                
        return quiz_questions
    
    def evaluate_answer(self, question, user_answer):
        """Évalue la réponse de l'utilisateur et fournit un feedback"""
        is_correct = question["correct_answer"] == user_answer
        feedback = question["explanation"] if is_correct else f"La réponse correcte était: {question['options'][question['correct_answer']]}. {question['explanation']}"
        
        return {
            "is_correct": is_correct,
            "feedback": feedback
        }