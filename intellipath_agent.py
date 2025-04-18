# Ajout dans un nouveau fichier: intellipath_agent.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_ollama import OllamaLLM
import langgraph.graph as g

# Définition des états de l'agent
class AgentState(BaseModel):
    user_input: str
    context: Dict[str, Any] = Field(default_factory=dict)
    current_syllabus: Optional[str] = None
    current_topic: Optional[str] = None
    steps_completed: List[str] = Field(default_factory=list)
    quiz_in_progress: bool = False
    user_id: str = "default_user"
    response: Optional[str] = None
    next_action: Optional[str] = None

# Fonctions de traitement pour le graphe
def parse_user_intent(state: AgentState) -> AgentState:
    """Détermine l'intention de l'utilisateur"""
    llm = OllamaLLM(model="llama3", temperature=0.1)
    
    intent_prompt = f"""
    Analyse l'entrée utilisateur suivante et détermine son intention principale:
    
    Entrée: {state.user_input}
    
    Réponds uniquement avec l'une des catégories suivantes:
    1. question_cours - L'utilisateur pose une question sur le contenu du cours
    2. demande_quiz - L'utilisateur souhaite faire un quiz
    3. recherche_recommandation - L'utilisateur demande des recommandations de cours
    4. analyse_progression - L'utilisateur veut voir sa progression
    5. conversation_generale - Conversation générale sans intention spécifique
    """
    
    intent = llm.invoke(intent_prompt).strip()
    state.context["detected_intent"] = intent
    return state

def route_to_next_step(state: AgentState) -> str:
    """Détermine l'étape suivante en fonction de l'intention détectée"""
    intent = state.context.get("detected_intent", "conversation_generale")
    
    if "question" in intent.lower():
        return "answer_question"
    elif "quiz" in intent.lower():
        return "generate_quiz"
    elif "recommandation" in intent.lower():
        return "recommend_courses"
    elif "progression" in intent.lower():
        return "show_progress"
    else:
        return "general_response"

def answer_question(state: AgentState) -> AgentState:
    """Répond à une question sur le contenu du cours"""
    llm = OllamaLLM(model="llama3", temperature=0.5)
    
    if not state.current_syllabus:
        state.response = "Je n'ai pas encore de syllabus chargé. Veuillez d'abord spécifier un sujet d'étude."
        return state
    
    question_prompt = f"""
    En tant qu'agent instructeur, réponds à la question suivante en te basant sur le syllabus du cours:
    
    Syllabus: {state.current_syllabus}
    
    Question: {state.user_input}
    
    Fournis une réponse détaillée et éducative.
    """
    
    state.response = llm.invoke(question_prompt)
    state.steps_completed.append("answer_question")
    return state

def generate_quiz(state: AgentState) -> AgentState:
    """Génère un quiz sur le sujet actuel"""
    llm = OllamaLLM(model="llama3", temperature=0.7)
    
    if not state.current_topic:
        state.response = "Je n'ai pas de sujet spécifique pour générer un quiz. Veuillez d'abord spécifier un sujet."
        return state
    
    quiz_prompt = f"""
    Crée un mini-quiz de 3 questions à choix multiples sur le sujet: {state.current_topic}
    
    Pour chaque question:
    1. Pose une question claire
    2. Fournis 4 options de réponse (A, B, C, D)
    3. Indique la réponse correcte
    4. Donne une brève explication de la réponse
    
    Formate le quiz d'une manière facile à lire.
    """
    
    state.response = llm.invoke(quiz_prompt)
    state.quiz_in_progress = True
    state.steps_completed.append("generate_quiz")
    return state

def recommend_courses(state: AgentState) -> AgentState:
    """Recommande des cours en fonction des intérêts de l'utilisateur"""
    llm = OllamaLLM(model="llama3", temperature=0.5)
    
    # Extraire les intérêts potentiels de l'entrée utilisateur
    interests_prompt = f"""
    Identifie les sujets d'intérêt mentionnés dans cette entrée utilisateur:
    
    {state.user_input}
    
    Renvoie uniquement une liste de sujets séparés par des virgules. Si aucun sujet spécifique n'est mentionné, réponds "général".
    """
    
    interests = llm.invoke(interests_prompt).strip()
    
    recommendation_prompt = f"""
    Recommande 3 cours ou ressources d'apprentissage sur les sujets suivants: {interests}
    
    Pour chaque recommandation, inclus:
    1. Le titre du cours
    2. Une brève description (30-50 mots)
    3. Pourquoi ce cours serait bénéfique
    4. Le niveau de difficulté
    
    Formate tes recommandations de manière claire et attrayante.
    """
    
    state.response = llm.invoke(recommendation_prompt)
    state.steps_completed.append("recommend_courses")
    return state

def show_progress(state: AgentState) -> AgentState:
    """Montre un résumé de la progression de l'utilisateur"""
    # Dans une implémentation réelle, ceci récupérerait les données de progression
    # Pour l'instant, générons une réponse simulée
    state.response = f"""
    # Résumé de progression pour {state.user_id}
    
    ## Sujets étudiés
    - {state.current_topic or "Aucun sujet étudié pour l'instant"}
    
    ## Activités complétées
    - Étapes complétées: {", ".join(state.steps_completed) if state.steps_completed else "Aucune étape complétée"}
    - Quiz terminés: {"Oui" if "generate_quiz" in state.steps_completed else "Non"}
    
    ## Recommandations
    Continuez à explorer le sujet actuel ou essayez un nouveau quiz pour évaluer vos connaissances!
    """
    
    state.steps_completed.append("show_progress")
    return state

def general_response(state: AgentState) -> AgentState:
    """Génère une réponse générale pour la conversation"""
    llm = OllamaLLM(model="llama3", temperature=0.7)
    
    context = f"Sujet actuel: {state.current_topic}" if state.current_topic else "Aucun sujet spécifique"
    
    response_prompt = f"""
    En tant qu'agent instructeur IntelliPath, réponds à cette entrée utilisateur:
    
    Contexte: {context}
    Entrée utilisateur: {state.user_input}
    
    Sois engageant, informatif et encourageant. Si l'utilisateur semble chercher une fonctionnalité spécifique, guide-le vers les commandes appropriées.
    """
    
    state.response = llm.invoke(response_prompt)
    return state

# Construction du graphe de l'agent
def build_intellipath_agent():
    workflow = g.StateGraph(AgentState)
    
    # Ajouter les nœuds
    workflow.add_node("parse_intent", parse_user_intent)
    workflow.add_node("answer_question", answer_question)
    workflow.add_node("generate_quiz", generate_quiz)
    workflow.add_node("recommend_courses", recommend_courses)
    workflow.add_node("show_progress", show_progress)
    workflow.add_node("general_response", general_response)
    
    # Définir les arêtes
    workflow.add_edge("parse_intent", g.Edge(route_to_next_step, {
        "answer_question": "answer_question",
        "generate_quiz": "generate_quiz",
        "recommend_courses": "recommend_courses",
        "show_progress": "show_progress",
        "general_response": "general_response"
    }))
    
    # Définir le point d'entrée
    workflow.set_entry_point("parse_intent")
    
    # Compiler le graphe
    intellipath_agent = workflow.compile()
    
    return intellipath_agent

# Fonction d'utilisation de l'agent
def use_intellipath_agent(user_input: str, user_id: str = "default_user", 
                          current_topic: str = None, current_syllabus: str = None):
    """Utilise l'agent IntelliPath pour traiter une entrée utilisateur"""
    agent = build_intellipath_agent()
    
    initial_state = AgentState(
        user_input=user_input,
        user_id=user_id,
        current_topic=current_topic,
        current_syllabus=current_syllabus
    )
    
    # Exécuter le workflow
    result = agent.invoke(initial_state)
    
    return result.response