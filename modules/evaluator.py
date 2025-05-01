import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("La clé API Groq n'est pas définie. Veuillez la définir dans le fichier .env")

class LearningEvaluator:
    """Évaluateur d'apprentissage qui génère et corrige des questions sur le contenu du syllabus"""
    
    def __init__(self, temperature: float = 0.4):
        """
        Initialise l'évaluateur d'apprentissage
        
        Args:
            temperature: Paramètre de créativité pour le modèle
        """
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY, 
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=temperature
        )
        
        self.syllabus = ""
        self.topic = ""
        self.current_module = None
        
        self._setup_prompt_templates()
    
    def _setup_prompt_templates(self):
        self.question_generation_prompt = """
        Tu es un expert en pédagogie et en évaluation des connaissances, spécialisé dans la création de questions pertinentes sur {topic}.
        
        Génère {num_questions} questions d'évaluation basées sur le module suivant du syllabus:
        
        ---
        {module_content}
        ---
        
        Les questions doivent:
        1. Évaluer la compréhension des concepts clés du module
        2. Inclure des questions de différents niveaux (connaissance, compréhension, application)
        3. Être claires, précises et formulées en français
        4. Privilégier des questions ouvertes qui favorisent la réflexion
        
        Pour chaque question, fournis également une proposition de réponse idéale pour aider à l'auto-évaluation.
        
        Format de la réponse (strictement en JSON):
        ```json
        [
          {
            "question": "Question 1",
            "type": "concept", // concept, application, réflexion
            "suggested_answer": "Réponse idéale à la question 1"
          },
          {
            "question": "Question 2",
            "type": "application",
            "suggested_answer": "Réponse idéale à la question 2"
          }
        ]
        ```
        
        Ne fournis pas d'explication supplémentaire, uniquement le JSON demandé.
        """
        
        self.answer_evaluation_prompt = """
        Tu es un expert en pédagogie et en évaluation des connaissances, spécialisé dans l'analyse des réponses d'apprenants sur {topic}.
        
        Évalue la réponse de l'apprenant à la question suivante:
        
        Question: {question}
        
        Réponse suggérée: {suggested_answer}
        
        Réponse de l'apprenant: {user_answer}
        
        Fournis une évaluation constructive qui:
        1. Identifie les points forts de la réponse
        2. Repère les concepts mal compris ou incomplets
        3. Suggère des améliorations précises
        4. Propose des ressources ou exemples complémentaires
        
        Ton évaluation doit être bienveillante, précise et orientée vers le progrès de l'apprenant.
        Inclus une note approximative sur 10 pour aider l'apprenant à situer sa compréhension.
        """
    
    def set_syllabus(self, syllabus: str, topic: str):
        """
        Définit le syllabus et le sujet pour l'évaluateur
        
        Args:
            syllabus: Le syllabus complet
            topic: Le sujet du cours
        """
        self.syllabus = syllabus
        self.topic = topic
    
    def set_current_module(self, module_content: str):
        """
        Définit le module actuel pour l'évaluation
        
        Args:
            module_content: Contenu du module à évaluer
        """
        self.current_module = module_content
    
    def generate_questions(self, num_questions: int = 3) -> List[Dict[str, Any]]:
        """
        Génère des questions d'évaluation basées sur le module actuel
        
        Args:
            num_questions: Nombre de questions à générer
            
        Returns:
            List[Dict[str, Any]]: Liste de questions avec réponses suggérées
        """
        if not self.current_module:
            return []
        
        prompt = ChatPromptTemplate.from_template(self.question_generation_prompt)
        chain = prompt | self.llm | StrOutputParser()
        
        result = chain.invoke({
            "topic": self.topic,
            "module_content": self.current_module,
            "num_questions": num_questions
        })
        
        # Extraire le JSON de la réponse
        import json
        import re
        
        json_match = re.search(r'```json\s+(.*?)\s+```', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = result
        
        try:
            questions = json.loads(json_str)
            return questions
        except json.JSONDecodeError:
            # Fallback en cas d'erreur de parsing JSON
            return [{"question": "Erreur lors de la génération des questions. Veuillez réessayer."}]
    
    def evaluate_answer(self, question: str, suggested_answer: str, user_answer: str) -> str:
        """
        Évalue la réponse de l'utilisateur à une question
        
        Args:
            question: La question posée
            suggested_answer: Réponse suggérée/idéale
            user_answer: Réponse fournie par l'utilisateur
            
        Returns:
            str: Évaluation détaillée de la réponse
        """
        prompt = ChatPromptTemplate.from_template(self.answer_evaluation_prompt)
        chain = prompt | self.llm | StrOutputParser()
        
        result = chain.invoke({
            "topic": self.topic,
            "question": question,
            "suggested_answer": suggested_answer,
            "user_answer": user_answer
        })
        
        return result