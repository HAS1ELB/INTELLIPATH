import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("La clé API Groq n'est pas définie. Veuillez la définir dans le fichier .env")

class SyllabusGenerator:
    def __init__(self, temperature: float = 0.7):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY, 
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=temperature
        )
        self._setup_templates()
    
    def _setup_templates(self):
        self.system_template = """
        Tu es un expert en conception pédagogique spécialisé dans la création de syllabus de cours.
        Tu vas créer un syllabus complet, structuré et engageant pour le sujet demandé.
        
        Le syllabus doit suivre cette structure précise en format Markdown:
        
        # Syllabus: {topic}
        
        ## Introduction
        [Brève présentation du sujet et de sa pertinence]
        
        ## Objectifs d'apprentissage
        [Liste de 4-6 objectifs d'apprentissage concrets et mesurables]
        
        ## Prérequis
        [Liste des connaissances ou compétences préalables nécessaires]
        
        ## Structure du cours
        [Aperçu de l'organisation générale du cours]
        
        ## Modules
        [Chaque module doit suivre ce format:]
        
        ### Module 1: [Titre]
        - **Description**: Description détaillée du module
        - **Concepts clés**:
          * Liste des concepts importants
        - **Activités d'apprentissage**:
          * Lectures, exercices, pratiques recommandés
        - **Ressources**:
          * Ressources spécifiques au module (liens, articles, vidéos)
        - **Évaluation**:
          * Questions ou exercices pour vérifier la compréhension
        - **Pour aller plus loin**:
          * Ressources complémentaires pour approfondir
        
        ### Module 2: [Titre]
        [...]
        
        ## Calendrier suggéré
        [Organisation temporelle des modules]
        
        ## Ressources principales
        [Ressources générales pour l'ensemble du cours]
        
        ## Méthodologie d'apprentissage
        [Conseils sur comment aborder efficacement ce cours]
        
        ## Projets pratiques suggérés
        [2-3 projets concrets pour appliquer les connaissances]
        
        ## Conclusion
        [Synthèse et encouragements]
        
        Caractéristiques importantes:
        - Adapte précisément le contenu au niveau demandé ({level})
        - Ajuste la progression pour une durée de {duration}
        - Structure le contenu pour favoriser le style d'apprentissage {learning_style}
        - Utilise systématiquement des exemples concrets et des métaphores pour faciliter la compréhension
        - Organise le contenu selon une progression logique des concepts
        - Inclut des éléments graphiques et visuels décrits textuellement pour les apprenants visuels
        """
        
        self.user_template = """
        Crée un syllabus de cours complet sur: {topic}
        
        Niveau: {level}
        Durée: {duration}
        Style d'apprentissage préféré: {learning_style}
        
        Instructions additionnelles:
        {additional_instructions}
        
        Le syllabus doit être structuré, complet, et suivre exactement le format requis.
        Utilise un français clair, précis et pédagogique.
        """
    
    def generate(self, topic: str, params: Dict[str, Any]) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_template),
            ("user", self.user_template)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        additional_instructions = []
        if params.get("include_projects", True):
            additional_instructions.append("Inclure des projets pratiques progressifs et immersifs.")
        if params.get("include_resources", True):
            additional_instructions.append("Inclure des ressources d'apprentissage variées (livres, articles, vidéos, outils, GitHub repositories).")
        if params.get("include_assessments", True):
            additional_instructions.append("Inclure des méthodes d'évaluation progressives adaptées à l'auto-apprentissage.")
            
        syllabus = chain.invoke({
            "topic": topic,
            "level": params.get("level", "Intermédiaire"),
            "duration": params.get("duration", "1 mois"),
            "learning_style": params.get("learning_style", "Pratique"),
            "additional_instructions": "\n".join(additional_instructions)
        })
        
        return self._post_process_syllabus(syllabus, topic)
    
    def _post_process_syllabus(self, syllabus: str, topic: str) -> str:
        if not syllabus.startswith("# Syllabus:"):
            syllabus = f"# Syllabus: {topic}\n\n" + syllabus
            
        syllabus = syllabus.replace("```markdown", "").replace("```", "")
        
        return syllabus


def generate_syllabus(topic: str, task: str, temperature: float = 0.7) -> str:
    generator = SyllabusGenerator(temperature=temperature)
    
    level = "Intermédiaire"
    duration = "1 mois"
    learning_style = "Pratique"
    include_projects = True
    include_resources = True
    include_assessments = True
    
    if "débutant" in task.lower():
        level = "Débutant"
    elif "avancé" in task.lower():
        level = "Avancé"
    
    if "1-2 semaines" in task:
        duration = "1-2 semaines"
    elif "3 mois" in task:
        duration = "3 mois"
    elif "6 mois" in task:
        duration = "6 mois"
    
    learning_styles = ["Visuel", "Auditif", "Lecture/Écriture", "Pratique"]
    for style in learning_styles:
        if style.lower() in task.lower():
            learning_style = style
            break
    
    include_projects = "projets pratiques" in task.lower()
    include_resources = "ressources" in task.lower()
    include_assessments = "évaluation" in task.lower()
    
    params = {
        "level": level,
        "duration": duration,
        "learning_style": learning_style,
        "include_projects": include_projects,
        "include_resources": include_resources,
        "include_assessments": include_assessments
    }
    
    return generator.generate(topic, params)