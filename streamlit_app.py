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
    from quiz_generator import QuizGenerator
    from progress_tracker import ProgressTracker
    from course_recommender import CourseRecommender
    
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
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "answers_submitted" not in st.session_state:
    st.session_state.answers_submitted = []
if "quiz_feedback" not in st.session_state:
    st.session_state.quiz_feedback = ""
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

# Page Quiz
elif page == "Quiz":
    st.title("Quiz et exercices interactifs")
    
    if not st.session_state.current_topic:
        st.warning("Veuillez d'abord sélectionner un sujet d'étude dans la page Cours.")
    else:
        # Initialisation ou réinitialisation du quiz
        col1, col2 = st.columns([3, 1])
        
        with col2:
            difficulty = st.selectbox(
                "Niveau de difficulté:",
                ["facile", "moyen", "difficile"],
                index=1
            )
            
            num_questions = st.number_input(
                "Nombre de questions:",
                min_value=1,
                max_value=10,
                value=5
            )
            
            if st.button("Générer un nouveau quiz"):
                with st.spinner("Génération du quiz en cours..."):
                    st.session_state.current_quiz = quiz_generator.generate_quiz(
                        st.session_state.current_topic, 
                        difficulty=difficulty,
                        num_questions=int(num_questions)
                    )
                    st.session_state.quiz_active = True
                    st.session_state.current_question_idx = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_feedback = ""
                    st.session_state.answers_submitted = []
                    st.success(f"Quiz sur {st.session_state.current_topic} généré avec succès!")
                    st.rerun()
        
        with col1:
            if not st.session_state.quiz_active and len(st.session_state.current_quiz) == 0:
                st.info("Cliquez sur 'Générer un nouveau quiz' pour commencer.")
            
        # Affichage du quiz actif
        if st.session_state.quiz_active and len(st.session_state.current_quiz) > 0:
            # Vérifier si toutes les questions ont été répondues
            if 'current_question_idx' in st.session_state and st.session_state.current_question_idx >= len(st.session_state.current_quiz):
                st.success(f"Quiz terminé! Votre score final: {st.session_state.quiz_score}/{len(st.session_state.current_quiz)}")
                
                # Enregistrer les résultats du quiz
                progress_tracker.record_quiz_result(
                    st.session_state.user_id,
                    st.session_state.current_topic,
                    st.session_state.quiz_score,
                    len(st.session_state.current_quiz)
                )
                
                # Afficher le feedback pour toutes les questions
                if 'answers_submitted' in st.session_state:
                    for i, (question_idx, user_answer) in enumerate(st.session_state.answers_submitted):
                        question = st.session_state.current_quiz[question_idx]
                        is_correct = question["correct_answer"] == user_answer
                        st.markdown(f"**Question {i+1}**: {question['question']}")
                        
                        # Afficher les options avec la bonne réponse et celle de l'utilisateur
                        for j, option in enumerate(question["options"]):
                            if j == question["correct_answer"] and j == user_answer:
                                st.markdown(f"✅ **{option}** (Votre réponse - Correcte)")
                            elif j == question["correct_answer"]:
                                st.markdown(f"✅ **{option}** (Réponse correcte)")
                            elif j == user_answer:
                                st.markdown(f"❌ **{option}** (Votre réponse)")
                            else:
                                st.markdown(f"- {option}")
                        
                        st.markdown(f"**Explication**: {question['explanation']}")
                        st.markdown("---")
                
                if st.button("Créer un nouveau quiz"):
                    st.session_state.quiz_active = False
                    st.rerun()
            else:
                # Afficher la question courante
                if 'current_question_idx' not in st.session_state:
                    st.session_state.current_question_idx = 0
                
                question = st.session_state.current_quiz[st.session_state.current_question_idx]
                
                st.subheader(f"Question {st.session_state.current_question_idx + 1}/{len(st.session_state.current_quiz)}")
                st.markdown(f"**{question['question']}**")
                
                # Créer des boutons radio pour les options
                user_answer = st.radio(
                    "Choisissez votre réponse:",
                    range(len(question["options"])),
                    format_func=lambda i: question["options"][i],
                    key=f"q_{st.session_state.current_question_idx}"
                )
                
                # Bouton pour soumettre la réponse
                if st.button("Soumettre la réponse"):
                    # Évaluer la réponse
                    evaluation = quiz_generator.evaluate_answer(question, user_answer)
                    
                    # Mettre à jour le score
                    if evaluation["is_correct"]:
                        st.session_state.quiz_score += 1
                        st.success("✅ Correct! " + evaluation["feedback"])
                    else:
                        st.error("❌ Incorrect. " + evaluation["feedback"])
                    
                    # Enregistrer la réponse soumise
                    if 'answers_submitted' not in st.session_state:
                        st.session_state.answers_submitted = []
                    st.session_state.answers_submitted.append((st.session_state.current_question_idx, user_answer))
                    
                    # Passer à la question suivante
                    st.session_state.current_question_idx += 1
                    
                    # Recharger la page pour afficher la question suivante ou le résultat final
                    st.rerun()
                
                # Afficher la progression
                st.progress(st.session_state.current_question_idx / len(st.session_state.current_quiz))
                st.markdown(f"Score actuel: {st.session_state.quiz_score}/{st.session_state.current_question_idx}")

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
