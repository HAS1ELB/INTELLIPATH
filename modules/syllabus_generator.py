import os
from typing import List
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Chargement des variables d'environnement
load_dotenv()

# Récupération de la clé API Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("La clé API Groq n'est pas définie. Veuillez la définir dans le fichier .env")

class SyllabusGenerator:
    """Classe pour générer un syllabus de cours personnalisé"""
    
    def __init__(self, temperature: float = 0.7):
        """
        Initialise le générateur de syllabus
        
        Args:
            temperature: Niveau de créativité (0.0 à 1.0)
        """
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY, 
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=temperature
        )
    
    def generate(self, topic: str, task: str) -> str:
        """
        Génère un syllabus basé sur le sujet et les critères spécifiés
        
        Args:
            topic: Le sujet principal du cours
            task: Description détaillée de ce qui est attendu dans le syllabus
            
        Returns:
            str: Le syllabus généré au format Markdown
        """
        # Système de prompts pour la génération du syllabus
        system_template = """
        Tu es un expert en conception pédagogique spécialisé dans la création de syllabus de cours.
        Ta mission est de créer un syllabus complet, structuré et engageant pour le sujet demandé.
        
        Le syllabus doit être présenté dans un format Markdown bien structuré et inclure:
        
        1. Un titre clair et une brève introduction au sujet
        2. Les objectifs d'apprentissage
        3. Une structure modulaire avec des sections numérotées
        4. Pour chaque module:
           - Titre et description
           - Concepts clés à maîtriser
           - Activités d'apprentissage suggérées
        5. Une timeline/calendrier suggéré
        
        {custom_requirements}
        
        Assure-toi que le contenu est:
        - Adapté au niveau demandé (débutant, intermédiaire, avancé)
        - Logiquement organisé avec une progression naturelle des concepts
        - Pratique et applicable à des situations réelles
        - Engageant et stimulant pour l'apprenant
        
        Utilise un format Markdown soigné avec des titres (##, ###), des listes à puces, et des séparateurs si nécessaire.
        """
        
        # Prompt utilisateur qui spécifie le sujet et les exigences particulières
        user_template = """
        Crée un syllabus de cours complet sur le sujet: {topic}
        
        Détails supplémentaires: {task}
        
        Le syllabus doit être en français et présenté dans un format Markdown clair et structuré.
        """
        
        # Création du modèle de prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", user_template)
        ])
        
        # Création de la chaîne de traitement
        chain = prompt | self.llm | StrOutputParser()
        
        # Exécution de la chaîne avec les paramètres fournis
        syllabus = chain.invoke({
            "topic": topic,
            "task": task,
            "custom_requirements": "Inclure des sections pour l'évaluation et des ressources recommandées."
        })
        
        return syllabus


def generate_syllabus(topic: str, task: str, temperature: float = 0.7) -> str:
    """
    Fonction d'aide pour générer un syllabus
    
    Args:
        topic: Le sujet principal du cours
        task: Description détaillée de ce qui est attendu dans le syllabus
        temperature: Niveau de créativité (0.0 à 1.0)
        
    Returns:
        str: Le syllabus généré au format Markdown
    """
    generator = SyllabusGenerator(temperature=temperature)
    return generator.generate(topic, task)
