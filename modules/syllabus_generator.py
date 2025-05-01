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
        # Système de prompts amélioré pour la génération du syllabus
        system_template = """
        Tu es un expert en conception pédagogique spécialisé dans la création de syllabus de cours.
        Ta mission est de créer un syllabus complet, structuré et engageant pour le sujet demandé.
        
        Le syllabus doit être présenté dans un format Markdown bien structuré et inclure:
        
        1. Un titre clair et une brève introduction au sujet
        2. Les objectifs d'apprentissage concrets et mesurables
        3. Les prérequis nécessaires pour suivre le cours
        4. Une structure modulaire avec des sections numérotées
        5. Pour chaque module:
           - Titre clair et description détaillée
           - Concepts clés à maîtriser
           - Activités d'apprentissage suggérées et pratiques
           - Ressources spécifiques au module (lectures, vidéos, outils)
           - Petits exercices de vérification de compréhension
        6. Une timeline/calendrier suggéré avec des jalons
        7. Une bibliographie commentée des ressources principales
        8. Des conseils méthodologiques pour optimiser l'apprentissage
        9. Des suggestions de projets pratiques pour appliquer les connaissances
        
        {custom_requirements}
        
        Assure-toi que le contenu est:
        - Adapté au niveau demandé (débutant, intermédiaire, avancé)
        - Logiquement organisé avec une progression naturelle des concepts
        - Pratique et applicable à des situations réelles
        - Engageant et stimulant pour l'apprenant
        - À jour avec les dernières connaissances et pratiques du domaine
        
        Utilise un format Markdown soigné avec:
        - Titres et sous-titres hiérarchiques (##, ###, ####)
        - Listes à puces et numérotées
        - Emphase pour les concepts importants (*italique*, **gras**)
        - Blocs de code pour les exemples techniques si nécessaire
        - Citations pour les définitions ou points importants (>)
        - Tableaux pour organiser l'information complexe si approprié
        - Séparateurs (---) entre les grandes sections
        
        Le syllabus doit être détaillé mais bien structuré pour faciliter la navigation.
        """
        
        # Prompt utilisateur amélioré
        user_template = """
        Crée un syllabus de cours complet et détaillé sur le sujet: {topic}
        
        Détails supplémentaires et exigences: {task}
        
        Le syllabus doit être en français et présenté dans un format Markdown clair et structuré.
        
        Assure-toi que le contenu est:
        - Adapté au profil d'un apprenant autodidacte
        - Progressif dans sa difficulté
        - Accompagné de multiples exemples pratiques
        - Enrichi de métaphores et d'analogies pour faciliter la compréhension
        - Structuré pour encourager l'apprentissage actif
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
            "custom_requirements": """
            Inclure également:
            - Des techniques d'auto-évaluation pour chaque module
            - Des suggestions de ressources complémentaires diversifiées (livres, articles, vidéos, podcasts)
            - Des conseils pour surmonter les obstacles courants dans l'apprentissage de ce sujet
            - Des liens entre les concepts théoriques et des applications pratiques réelles
            - Une section "Pour aller plus loin" à la fin de chaque module
            """
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
