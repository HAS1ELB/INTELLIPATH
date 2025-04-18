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
        
    def generate_quiz(self, topic, difficulty="moyen", num_questions=5):
        """Génère un quiz sur un sujet donné avec le nombre exact de questions demandé"""
        quiz_questions = []
        attempts = 0
        max_attempts = num_questions * 3  # Permettre plusieurs tentatives pour obtenir le bon nombre de questions
        
        while len(quiz_questions) < num_questions and attempts < max_attempts:
            attempts += 1
            
            prompt = PromptTemplate(
                template="""Génère une question de quiz sur le sujet {topic} avec une difficulté {difficulty}.
                La question doit avoir 4 options de réponse et une seule bonne réponse.
                Fournis également une explication détaillée de la réponse correcte.
                
                Voici un exemple de format attendu:
                {{
                    "question": "Quelle est la capitale de la France?",
                    "options": ["Madrid", "Paris", "Rome", "Berlin"],
                    "correct_answer": 1,
                    "explanation": "Paris est la capitale de la France depuis de nombreux siècles."
                }}
                
                Assure-toi de respecter exactement ce format JSON.
                """,
                input_variables=["topic", "difficulty"]
            )
            
            formatted_prompt = prompt.format(topic=topic, difficulty=difficulty)
            response = self.llm.invoke(formatted_prompt)
            
            try:
                # Tenter de trouver et extraire le JSON de la réponse
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    question = json.loads(json_str)
                    
                    # Vérifier que la question a tous les champs nécessaires
                    if all(k in question for k in ["question", "options", "correct_answer", "explanation"]):
                        # Vérifier que correct_answer est un entier valide
                        if isinstance(question["correct_answer"], int) and 0 <= question["correct_answer"] < len(question["options"]):
                            quiz_questions.append(question)
                            print(f"Question {len(quiz_questions)} générée avec succès")
                        else:
                            print(f"Format incorrect pour correct_answer: {question['correct_answer']}")
                    else:
                        print(f"Champs manquants dans la question")
                else:
                    print("Impossible de trouver un JSON valide dans la réponse")
                    
            except Exception as e:
                print(f"Erreur lors de l'analyse de la question: {e}")
                print(f"Réponse reçue: {response}")
                continue
        
        # S'assurer qu'au moins une question est générée même si le nombre demandé n'est pas atteint
        if not quiz_questions:
            fallback_question = {
                "question": f"Question de secours sur {topic}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Ceci est une question de secours générée car la génération automatique a échoué."
            }
            quiz_questions.append(fallback_question)
        
        print(f"Quiz généré avec {len(quiz_questions)} questions sur les {num_questions} demandées")
        return quiz_questions
    
    def evaluate_answer(self, question, user_answer):
        """Évalue la réponse de l'utilisateur et fournit un feedback"""
        is_correct = question["correct_answer"] == user_answer
        feedback = question["explanation"] if is_correct else f"La réponse correcte était: {question['options'][question['correct_answer']]}. {question['explanation']}"
        
        return {
            "is_correct": is_correct,
            "feedback": feedback
        }
