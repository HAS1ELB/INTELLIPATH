import streamlit as st

# Configuration de la page - DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT
st.set_page_config(
    page_title="IntelliPath - Apprentissage Personnalisé",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import des modules standards
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
import sqlite3

# Importation sécurisée des modules personnalisés
def import_modules():
    from generating_syllabus import generate_syllabus
    from teaching_agent import teaching_agent
    
    # Définition des classes dont nous avons besoin
    class QuizGenerator:
        def __init__(self):
            self.llm = None  # À initialiser plus tard
            
        def generate_quiz(self, topic, difficulty="medium", num_questions=5):
            # Simulation en attendant l'implémentation réelle
            return [
                {
                    "question": f"Question exemple sur {topic}?",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": 0,
                    "explanation": "Explication de la réponse"
                }
            ]
    
    class ProgressTracker:
        def __init__(self, db_path="user_progress.db"):
            self.db_path = db_path
            
        def record_quiz_result(self, user_id, topic, score, max_score):
            pass  # À implémenter
            
        def record_study_session(self, user_id, topic, duration_minutes):
            pass  # À implémenter
            
        def generate_dashboard(self, user_id, output_dir="dashboard"):
            return None  # À implémenter
    
    class CourseRecommender:
        def __init__(self, progress_tracker):
            self.progress_tracker = progress_tracker
            
        def recommend_courses(self, user_id, interests=None, career_goal=None):
            return []  # À implémenter
            
        def get_user_profile(self, user_id):
            return {
                "strengths": [],
                "weaknesses": [],
                "studied_topics": []
            }
    
    return {
        "generate_syllabus": generate_syllabus,
        "teaching_agent": teaching_agent,
        "QuizGenerator": QuizGenerator,
        "ProgressTracker": ProgressTracker,
        "CourseRecommender": CourseRecommender
    }

# Chargement des modules
modules = import_modules()

# Initialisation des composants
@st.cache_resource
def initialize_components():
    quiz_generator = modules["QuizGenerator"]()
    progress_tracker = modules["ProgressTracker"](db_path="user_progress.db")
    course_recommender = modules["CourseRecommender"](progress_tracker)
    return None, quiz_generator, progress_tracker, course_recommender

vector_store, quiz_generator, progress_tracker, course_recommender = initialize_components()

# Initialisation des variables de session
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_" + datetime.now().strftime("%Y%m%d%H%M%S")
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "current_syllabus" not in st.session_state:
    st.session_state.current_syllabus = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = []
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "study_start_time" not in st.session_state:
    st.session_state.study_start_time = datetime.now()

# Sidebar
with st.sidebar:
    st.title("IntelliPath")
    st.subheader("Votre assistant d'apprentissage personnalisé")
    
    # Section d'identification
    st.sidebar.subheader("Profil utilisateur")
    user_name = st.text_input("Nom d'utilisateur", value="Étudiant")
    
    # Navigation
    st.sidebar.subheader("Navigation")
    page = st.radio(
        "Choisissez une page:",
        ["Accueil", "Cours", "Quiz", "Progression", "Recommandations"]
    )

# Page d'accueil
if page == "Accueil":
    st.title("Bienvenue sur IntelliPath!")
    st.subheader("Votre parcours d'apprentissage personnalisé")
    
    st.markdown("""
    ### 🚀 Commencez votre parcours d'apprentissage
    
    IntelliPath est un agent intelligent d'apprentissage personnalisé qui vous accompagne dans votre parcours éducatif.
    
    Pour commencer, rendez-vous sur la page "Cours" et sélectionnez un sujet d'étude!
    """)
    
    st.image("https://img.freepik.com/free-vector/gradient-online-courses-landing-page_23-2149128214.jpg", caption="Apprentissage personnalisé")

# Page Cours
elif page == "Cours":
    st.title("Créez votre parcours d'apprentissage")
    
    # Formulaire pour générer un nouveau syllabus
    with st.expander("Générer un nouveau programme de cours", expanded=st.session_state.current_syllabus is None):
        topic_input = st.text_input("Sujet que vous souhaitez apprendre:")
        
        if st.button("Générer le programme") and topic_input:
            with st.spinner("Génération du programme en cours..."):
                task = f"Generate a course syllabus to teach the topic: {topic_input}"
                syllabus = modules["generate_syllabus"](topic_input, task)
                st.session_state.current_syllabus = syllabus
                st.session_state.current_topic = topic_input
                modules["teaching_agent"].seed_agent(syllabus, topic_input)
                st.session_state.study_start_time = datetime.now()  # Démarrer le compteur de temps
                st.success(f"Programme pour {topic_input} généré avec succès!")
    
    # Affichage du syllabus actuel
    if st.session_state.current_syllabus:
        st.subheader(f"Programme de cours: {st.session_state.current_topic}")
        st.markdown(st.session_state.current_syllabus)
        
        # Section de conversation avec l'agent
        st.subheader("Discutez avec votre instructeur")
        
        # Affichage de l'historique des messages
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
        
        # Zone de saisie pour les nouveaux messages
        user_input = st.chat_input("Posez une question à votre instructeur...")
        if user_input:
            # Ajouter le message de l'utilisateur à l'historique
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)
            
            # Traiter le message avec l'agent intelligent
            with st.spinner("L'instructeur réfléchit..."):
                modules["teaching_agent"].human_step(user_input)
                response = modules["teaching_agent"].instructor_step().rstrip("<END_OF_TURN>")
                
                # Ajouter la réponse à l'historique
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)

# Page Quiz (version simplifiée)
elif page == "Quiz":
    st.title("Quiz et exercices interactifs")
    
    if not st.session_state.current_topic:
        st.warning("Veuillez d'abord sélectionner un sujet d'étude dans la page Cours.")
    else:
        st.info("Fonctionnalité de quiz en cours de développement...")

# Page Progression (version simplifiée)
elif page == "Progression":
    st.title("Suivi de la progression")
    
    if not st.session_state.current_topic:
        st.warning("Veuillez d'abord sélectionner un sujet d'étude dans la page Cours.")
    else:
        st.info("Fonctionnalité de suivi de progression en cours de développement...")

# Page Recommandations (version simplifiée)
elif page == "Recommandations":
    st.title("Recommandations personnalisées")
    st.info("Fonctionnalité de recommandations en cours de développement...")

# Pied de page
st.markdown("---")
st.markdown("© 2025 IntelliPath - Votre assistant d'apprentissage personnalisé")
