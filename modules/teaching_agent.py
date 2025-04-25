import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Chargement des variables d'environnement
load_dotenv()

# Récupération de la clé API Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("La clé API Groq n'est pas définie. Veuillez la définir dans le fichier .env")

class TeachingAgent:
    """Agent pour l'enseignement interactif basé sur un syllabus"""
    
    def __init__(self, temperature: float = 0.7):
        """
        Initialise l'agent d'enseignement
        
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
        self.conversation_history = []
        
        # Création du template de prompt pour l'agent enseignant
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{user_input}")
        ])
        
        # Création de la chaîne de traitement
        self.chain = self.prompt_template | self.llm | StrOutputParser()
    
    def _get_system_prompt(self) -> str:
        """
        Génère le prompt système pour l'agent enseignant
        
        Returns:
            str: Le prompt système
        """
        return """
        Tu es un professeur expert et pédagogue spécialisé dans {topic}. 
        Ta mission est d'enseigner à l'apprenant en suivant le syllabus fourni.
        
        ### Syllabus du cours:
        {syllabus}
        
        ### Instructions:
        1. Réponds aux questions de l'apprenant concernant le sujet avec clarté et pédagogie
        2. Base tes réponses sur le contenu du syllabus quand c'est possible
        3. Suis une progression logique dans l'enseignement en fonction du syllabus
        4. Si une question sort du cadre du syllabus, indique-le gentiment tout en fournissant une réponse adaptée
        5. Utilise des exemples concrets et des analogies pour faciliter la compréhension
        6. Encourage l'apprenant à mettre en pratique ses connaissances
        7. Identifie les lacunes potentielles et suggère des révisions quand nécessaire
        
        ### Historique de la conversation:
        {conversation_history}
        
        Réponds toujours en français avec une approche pédagogique, bienveillante et structurée.
        """
    
    def seed_agent(self, syllabus: str, topic: str) -> None:
        """
        Initialise l'agent avec un syllabus et un sujet
        
        Args:
            syllabus: Le syllabus du cours au format Markdown
            topic: Le sujet principal du cours
        """
        self.syllabus = syllabus
        self.topic = topic
        self.conversation_history = []
    
    def respond(self, user_input: str) -> str:
        """
        Génère une réponse à l'input de l'utilisateur
        
        Args:
            user_input: La question ou commentaire de l'utilisateur
            
        Returns:
            str: La réponse de l'agent enseignant
        """
        if not self.syllabus or not self.topic:
            return "Veuillez d'abord initialiser l'agent avec un syllabus et un sujet."
        
        # Préparation de l'historique de conversation formaté
        formatted_history = ""
        for message in self.conversation_history:
            role = "Apprenant" if message["role"] == "user" else "Professeur"
            formatted_history += f"{role}: {message['content']}\n\n"
        
        # Génération de la réponse
        response = self.chain.invoke({
            "user_input": user_input,
            "syllabus": self.syllabus,
            "topic": self.topic,
            "conversation_history": formatted_history
        })
        
        # Mise à jour de l'historique de conversation
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
