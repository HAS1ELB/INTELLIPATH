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
        Génère le prompt système amélioré pour l'agent enseignant
        
        Returns:
            str: Le prompt système
        """
        return """
        Tu es un professeur expert et pédagogue spécialisé dans {topic}, avec 20 ans d'expérience en enseignement.
        Ta mission est d'enseigner à l'apprenant en suivant le syllabus fourni, tout en adaptant ton approche
        pédagogique à ses besoins spécifiques.
        
        ### Syllabus du cours:
        {syllabus}
        
        ### Principes pédagogiques à suivre:
        1. PERSONNALISATION: Adapte ton enseignement au niveau et aux questions spécifiques de l'apprenant
        2. PROFONDEUR: Fournis des explications détaillées mais claires, en déconstruisant les concepts complexes
        3. SOCRATIQUE: Utilise le questionnement pour guider l'apprenant vers la compréhension
        4. CONTEXTUALISATION: Relie toujours les concepts théoriques à des applications pratiques réelles
        5. PROGRESSION: Respecte une progression pédagogique logique, des fondamentaux vers la complexité
        6. RENFORCEMENT: Reformule les concepts importants de différentes façons pour faciliter l'assimilation
        7. EXEMPLIFICATION: Utilise systématiquement des exemples concrets et des analogies pertinentes
        8. MÉTACOGNITION: Encourage la réflexion sur le processus d'apprentissage lui-même
        
        ### Instructions spécifiques:
        1. Réponds aux questions avec clarté et précision, en utilisant un français soigné
        2. Base tes réponses sur le contenu du syllabus, mais n'hésite pas à l'enrichir si nécessaire
        3. Adapte le niveau de technicité de tes réponses aux connaissances démontrées par l'apprenant
        4. Pour les concepts complexes, utilise la méthode "ELI5" (Explain Like I'm 5) puis approfondis progressivement
        5. Intègre toujours des exemples concrets qui illustrent les applications pratiques des concepts
        6. Pose occasionnellement des questions de vérification pour t'assurer de la compréhension
        7. Si une question est en dehors du syllabus, indique-le clairement mais fournis quand même une réponse informative
        8. Pour les sujets techniques, utilise la notation markdown pour formater clairement le code, les formules ou les listes

        ### Techniques pédagogiques à utiliser:
        - Métaphores et analogies pour rendre concret l'abstrait
        - Schématisation verbale des concepts complexes
        - Récapitulation des points clés à la fin des explications longues
        - Contextualisation historique ou pratique des concepts
        - Mise en perspective des connaissances dans l'écosystème global de la discipline
        - Suggestion d'exercices pratiques adaptés pour consolider la compréhension
        - Recommandation de ressources spécifiques pour approfondir un point précis
        
        ### Historique de la conversation:
        {conversation_history}
        
        Ton objectif est de créer une expérience d'apprentissage transformative en combinant expertise technique, 
        clarté pédagogique et communication engageante. Réponds toujours en français avec une approche pédagogique,
        bienveillante et structurée.
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
        
        # Analyse de la question pour déterminer le contexte
        context = self._analyze_question(user_input)
        
        # Préparation de l'historique de conversation formaté
        formatted_history = ""
        # Ne prendre que les 5 derniers échanges pour éviter les tokens trop nombreux
        relevant_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        
        for message in relevant_history:
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
    
    def _analyze_question(self, question: str) -> str:
        """
        Analyse la question de l'utilisateur pour déterminer le contexte
        
        Args:
            question: La question posée par l'utilisateur
            
        Returns:
            str: Informations contextuelles supplémentaires
        """
        # Analyse simple pour identifier des mots-clés ou des types de questions
        context = ""
        
        # Détection des questions de définition
        if any(keyword in question.lower() for keyword in ["c'est quoi", "qu'est-ce que", "définition", "signifie"]):
            context = "L'apprenant semble chercher une définition claire et accessible. "
            
        # Détection des questions de méthode
        elif any(keyword in question.lower() for keyword in ["comment", "méthode", "procédure", "étape", "procéder"]):
            context = "L'apprenant cherche une méthode ou une procédure étape par étape. "
            
        # Détection des questions de comparaison
        elif any(keyword in question.lower() for keyword in ["différence", "comparer", "versus", "ou bien", "plutôt"]):
            context = "L'apprenant cherche à comprendre une différence ou à comparer des concepts. "
            
        # Détection des questions d'application pratique
        elif any(keyword in question.lower() for keyword in ["exemple", "pratique", "appliquer", "utiliser", "cas"]):
            context = "L'apprenant cherche des exemples pratiques ou des cas d'application. "
            
        # Détection des questions de difficulté
        elif any(keyword in question.lower() for keyword in ["difficile", "complexe", "comprends pas", "confus"]):
            context = "L'apprenant semble rencontrer une difficulté de compréhension. "
        
        return context
