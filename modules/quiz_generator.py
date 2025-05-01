# Ajout dans un nouveau fichier: quiz_generator.py
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Chargement des variables d'environnement
load_dotenv()

class QuizQuestion(BaseModel):
    question: str = Field(description="La question posée")
    options: List[str] = Field(description="Les options de réponse")
    correct_answer: int = Field(description="L'index de la réponse correcte (0-3)")
    explanation: str = Field(description="Explication de la réponse correcte")

class QuizGenerator:
    def __init__(self):
        # Utilisation de Groq au lieu d'Ollama pour être cohérent avec le reste de l'application
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            raise ValueError("La clé API Groq n'est pas définie. Veuillez la définir dans le fichier .env")
        
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY, 
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.7
        )
        
        self.parser = PydanticOutputParser(pydantic_object=QuizQuestion)
        
    def generate_quiz(self, topic, difficulty="moyen", num_questions=5):
        """Génère un quiz sur un sujet donné avec le nombre exact de questions demandées
        
        Args:
            topic: Le sujet du quiz
            difficulty: Le niveau de difficulté (facile, moyen, difficile)
            num_questions: Le nombre de questions à générer
            
        Returns:
            List[QuizQuestion]: Une liste d'objets QuizQuestion
        """
        # Création du prompt pour générer les questions du quiz
        prompt_template = """
        Tu es un expert en conception de quiz éducatifs. Ton objectif est de créer un quiz sur le sujet: {topic}.
        
        Crée {num_questions} questions de quiz de niveau {difficulty} sur ce sujet.
        
        Pour chaque question:
        1. Formule une question claire et précise
        2. Fournis exactement 4 options de réponse dont une seule est correcte
        3. Indique l'index de la réponse correcte (0, 1, 2 ou 3)
        4. Fournis une explication détaillée de la bonne réponse
        
        Réponds UNIQUEMENT au format JSON suivant, sans aucun autre texte:
        ```json
        [
          {{
            "question": "La question posée",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer": 0,
            "explanation": "Explication détaillée de la réponse correcte"
          }}
        ]
        ```
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["topic", "difficulty", "num_questions"]
        )
        
        formatted_prompt = prompt.format(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions
        )
        
        try:
            # Génération du quiz avec le LLM
            response = self.llm.invoke(formatted_prompt)
            result = response.content
            
            # Extraction du JSON de la réponse
            import re
            json_match = re.search(r'```json\s+(.*?)\s+```', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = result
            
            # Conversion du JSON en liste d'objets QuizQuestion
            questions_data = json.loads(json_str)
            quiz_questions = []
            
            for q_data in questions_data:
                quiz_question = QuizQuestion(
                    question=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"]
                )
                quiz_questions.append(quiz_question)
            
            return quiz_questions
        
        except Exception as e:
            print(f"Erreur lors de la génération du quiz: {e}")
            # En cas d'erreur, retourner une question par défaut
            default_question = QuizQuestion(
                question="Question non disponible en raison d'une erreur",
                options=["Option A", "Option B", "Option C", "Option D"],
                correct_answer=0,
                explanation="Une erreur s'est produite lors de la génération du quiz."
            )
            return [default_question]
