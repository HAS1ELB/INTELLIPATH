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
import numpy as np

# Importation du gestionnaire d'utilisateurs
from user_manager import UserManager

# Importation sécurisée des modules personnalisés
def import_modules():
    from generating_syllabus import generate_syllabus
    from teaching_agent import teaching_agent
    from quiz_generator import QuizGenerator
    from progress_tracker import ProgressTracker
    from course_recommender_offline import CourseRecommenderOffline
    from skills_analyzer import SkillsAnalyzer
    
    return {
        "generate_syllabus": generate_syllabus,
        "teaching_agent": teaching_agent,
        "QuizGenerator": QuizGenerator,
        "ProgressTracker": ProgressTracker,
        "CourseRecommender": CourseRecommenderOffline,
        "SkillsAnalyzer": SkillsAnalyzer
    }

# Initialisation du gestionnaire d'utilisateurs
@st.cache_resource
def initialize_user_manager():
    return UserManager()

user_manager = initialize_user_manager()

# Chargement des modules
modules = import_modules()

# Initialisation des composants
@st.cache_resource
def initialize_components():
    quiz_generator = modules["QuizGenerator"]()
    progress_tracker = modules["ProgressTracker"](db_path="user_progress.db")
    course_recommender = modules["CourseRecommender"](progress_tracker)
    skills_analyzer = modules["SkillsAnalyzer"](progress_tracker)
    return None, quiz_generator, progress_tracker, course_recommender, skills_analyzer

vector_store, quiz_generator, progress_tracker, course_recommender, skills_analyzer = initialize_components()

# CSS personnalisé pour l'interface d'authentification
st.markdown("""
<style>
    /* Personnalisation générale */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Personnalisation des formulaires */
    div[data-testid="stForm"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Personnalisation des boutons */
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* Style pour les messages d'erreur et de succès */
    div.stAlert {
        border-radius: 8px;
    }
    
    /* Personnalisation du header utilisateur */
    .user-header {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
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
if "skills" not in st.session_state:
    st.session_state.skills = {}
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"  # login ou register

# Fonctions d'authentification pour les callbacks
def login_callback():
    username_or_email = st.session_state.login_username
    password = st.session_state.login_password
    
    success, result = user_manager.login_user(username_or_email, password)
    
    if success:
        st.session_state.authenticated = True
        st.session_state.user_id = result["user_id"]
        st.session_state.session_id = result["session_id"]
        
        # Récupérer les informations utilisateur
        user_info_success, user_info = user_manager.get_user_info(result["user_id"])
        if user_info_success:
            st.session_state.username = user_info["username"]
        
        st.rerun()
    else:
        st.session_state.login_error = result

def register_callback():
    username = st.session_state.register_username
    email = st.session_state.register_email
    password = st.session_state.register_password
    confirm_password = st.session_state.register_confirm_password
    
    if password != confirm_password:
        st.session_state.register_error = "Les mots de passe ne correspondent pas"
        return
    
    success, result = user_manager.register_user(username, email, password)
    
    if success:
        st.session_state.auth_page = "login"
        st.session_state.register_success = "Inscription réussie! Vous pouvez maintenant vous connecter."
        st.rerun()
    else:
        st.session_state.register_error = result

def logout_callback():
    if st.session_state.session_id:
        user_manager.logout_user(st.session_state.session_id)
    
    # Réinitialiser les variables de session
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.session_id = None
    st.session_state.auth_page = "login"
    
    # Redirection vers la page de connexion
    st.rerun()

def switch_to_register():
    st.session_state.auth_page = "register"
    st.rerun()

def switch_to_login():
    st.session_state.auth_page = "login"
    st.rerun()

# Page d'authentification ou application principale
if not st.session_state.authenticated:
    st.title("IntelliPath - Apprentissage Personnalisé")
    
    # Conteneur central pour le formulaire d'authentification
    auth_container = st.container()
    
    with auth_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.image("https://img.freepik.com/free-vector/online-education-banner_107791-3647.jpg?w=826&t=st=1703175295~exp=1703175895~hmac=85b2a42ad67d1ff12ac2b5d072d1a24ca7fa8d95b04ce96f2bcf69c1caaaed65", width=400)
            
            if st.session_state.auth_page == "login":
                st.subheader("Connexion à IntelliPath")
                
                # Afficher le message de succès d'inscription si disponible
                if "register_success" in st.session_state and st.session_state.register_success:
                    st.success(st.session_state.register_success)
                    st.session_state.register_success = None
                
                # Afficher l'erreur de connexion si disponible
                if "login_error" in st.session_state and st.session_state.login_error:
                    st.error(st.session_state.login_error)
                    st.session_state.login_error = None
                
                # Formulaire de connexion
                with st.form("login_form", clear_on_submit=True):
                    st.text_input("Nom d'utilisateur ou email", key="login_username")
                    st.text_input("Mot de passe", type="password", key="login_password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.form_submit_button("Se connecter", on_click=login_callback)
                    with col2:
                        st.form_submit_button("Créer un compte", on_click=switch_to_register)
            
            elif st.session_state.auth_page == "register":
                st.subheader("Créer un compte IntelliPath")
                
                # Afficher l'erreur d'inscription si disponible
                if "register_error" in st.session_state and st.session_state.register_error:
                    st.error(st.session_state.register_error)
                    st.session_state.register_error = None
                
                # Formulaire d'inscription
                with st.form("register_form", clear_on_submit=True):
                    st.text_input("Nom d'utilisateur", key="register_username")
                    st.text_input("Email", key="register_email")
                    st.text_input("Mot de passe", type="password", key="register_password")
                    st.text_input("Confirmer le mot de passe", type="password", key="register_confirm_password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.form_submit_button("S'inscrire", on_click=register_callback)
                    with col2:
                        st.form_submit_button("Retour à la connexion", on_click=switch_to_login)
            
            # Footer
            st.markdown("---")
            st.markdown("© 2025 IntelliPath - Votre assistant d'apprentissage personnalisé")

else:
    # Sidebar
    with st.sidebar:
        st.title("IntelliPath")
        st.subheader("Votre assistant d'apprentissage personnalisé")
        
        # Section d'identification
        st.sidebar.subheader("Profil utilisateur")
        st.write(f"Connecté en tant que: **{st.session_state.username}**")
        
        # Bouton de déconnexion
        if st.button("Déconnexion", key="logout_button"):
            logout_callback()
        
        # Navigation
        st.sidebar.subheader("Navigation")
        page = st.radio(
            "Choisissez une page:",
            ["Accueil", "Cours", "Quiz", "Progression", "Recommandations"],
            key="navigation_radio"
        )

    # Page d'accueil
    if page == "Accueil":
        st.title(f"Bienvenue sur IntelliPath, {st.session_state.username}!")
        st.subheader("Votre parcours d'apprentissage personnalisé")
        
        st.markdown("""
        ### 🚀 Commencez votre parcours d'apprentissage
        
        IntelliPath est un agent intelligent d'apprentissage personnalisé qui vous accompagne dans votre parcours éducatif.
        
        Pour commencer, rendez-vous sur la page "Cours" et sélectionnez un sujet d'étude!
        """)
        
        # Statistiques utilisateur
        st.subheader("Votre tableau de bord")
        
        # Récupérer les statistiques de l'utilisateur
        conn = sqlite3.connect(progress_tracker.db_path)
        
        # Quiz complétés
        quiz_count = pd.read_sql(f"""
        SELECT COUNT(*) as count FROM quiz_results 
        WHERE user_id = '{st.session_state.user_id}'
        """, conn).iloc[0]['count']
        
        # Temps d'étude total
        study_time = pd.read_sql(f"""
        SELECT SUM(duration_minutes) as total FROM study_sessions 
        WHERE user_id = '{st.session_state.user_id}'
        """, conn).iloc[0]['total']
        
        # Compétences acquises
        skills_count = pd.read_sql(f"""
        SELECT COUNT(*) as count FROM skills 
        WHERE user_id = '{st.session_state.user_id}'
        """, conn).iloc[0]['count']
        
        conn.close()
        
        # Afficher les statistiques
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Quiz complétés", quiz_count or 0)
        
        with col2:
            st.metric("Temps d'étude", f"{study_time or 0} min")
        
        with col3:
            st.metric("Compétences", skills_count or 0)
        
        st.image("https://img.freepik.com/free-vector/gradient-online-courses-landing-page_23-2149128214.jpg", caption="Apprentissage personnalisé")

    # Page Cours
    elif page == "Cours":
        st.title("Créez votre parcours d'apprentissage")
        
        # Formulaire pour générer un nouveau syllabus
        with st.expander("Générer un nouveau programme de cours", expanded=st.session_state.current_syllabus is None):
            topic_input = st.text_input("Sujet que vous souhaitez apprendre:", key="course_topic_input")
            
            if st.button("Générer le programme", key="generate_syllabus_button") and topic_input:
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
            user_input = st.chat_input("Posez une question à votre instructeur...", key="chat_input")
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
                    
                # Enregistrer la session d'étude (temps passé à discuter avec l'instructeur)
                if st.session_state.current_topic:
                    current_time = datetime.now()
                    study_duration = (current_time - st.session_state.study_start_time).total_seconds() / 60
                    if study_duration >= 1:  # Enregistrer seulement si au moins 1 minute s'est écoulée
                        progress_tracker.record_study_session(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            int(study_duration)
                        )
                        st.session_state.study_start_time = current_time  # Réinitialiser le compteur

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
                    index=1,
                    key="quiz_difficulty_select"
                )
                
                num_questions = st.number_input(
                    "Nombre de questions:",
                    min_value=1,
                    max_value=10,
                    value=5,
                    key="quiz_num_questions_input"
                )
                
                if st.button("Générer un nouveau quiz", key="generate_quiz_button"):
                    with st.spinner("Génération du quiz en cours..."):
                        # Essayer jusqu'à obtenir le bon nombre de questions
                        max_tries = 3
                        for attempt in range(max_tries):
                            current_quiz = quiz_generator.generate_quiz(
                                st.session_state.current_topic, 
                                difficulty=difficulty,
                                num_questions=int(num_questions)
                            )
                            
                            if len(current_quiz) >= int(num_questions):
                                break
                                
                            if attempt == max_tries - 1:
                                st.warning(f"Impossible de générer {num_questions} questions. Seulement {len(current_quiz)} questions ont été créées.")
                        
                        st.session_state.current_quiz = current_quiz
                        st.session_state.quiz_active = True
                        st.session_state.current_question_idx = 0
                        st.session_state.quiz_score = 0
                        st.session_state.quiz_feedback = ""
                        st.session_state.answers_submitted = []
                        st.success(f"Quiz sur {st.session_state.current_topic} généré avec {len(current_quiz)} questions!")
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
                    
                    # Mettre à jour les compétences en fonction des résultats du quiz
                    if st.session_state.current_topic:
                        # Calculer le niveau de compétence (1-5) en fonction du score
                        score_percentage = st.session_state.quiz_score / len(st.session_state.current_quiz) * 100
                        proficiency_level = min(5, max(1, int(score_percentage / 20) + 1))  # 1-5 échelle
                        
                        # Mettre à jour la compétence dans le tracker de progression
                        progress_tracker.update_skill(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            proficiency_level
                        )
                        
                        st.session_state.skills[st.session_state.current_topic] = proficiency_level
                    
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
                    
                    if st.button("Créer un nouveau quiz", key="create_new_quiz_button"):
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
                    if st.button("Soumettre la réponse", key=f"submit_answer_{st.session_state.current_question_idx}"):
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
                    
    # Page Progression
    elif page == "Progression":
        st.title("Suivi de la progression")
        
        if not st.session_state.user_id:
            st.warning("Identifiant utilisateur non détecté. Veuillez vous identifier.")
        else:
            # Créer les onglets pour les différentes vues de progression
            tabs = st.tabs(["Résumé", "Quiz", "Temps d'étude", "Compétences", "Analyse"])
            
            with tabs[0]:  # Résumé
                st.subheader("Résumé de votre progression")
                
                # Récupérer les données de progression
                conn = sqlite3.connect(progress_tracker.db_path)
                
                # Récupérer les quiz complétés
                quiz_results = pd.read_sql(f"""
                SELECT topic, score, max_score, completion_time 
                FROM quiz_results 
                WHERE user_id = '{st.session_state.user_id}'
                ORDER BY completion_time DESC
                """, conn)
                
                # Récupérer les sessions d'étude
                study_sessions = pd.read_sql(f"""
                SELECT topic, duration_minutes, session_date 
                FROM study_sessions 
                WHERE user_id = '{st.session_state.user_id}'
                ORDER BY session_date DESC
                """, conn)
                
                # Récupérer les compétences
                skills = pd.read_sql(f"""
                SELECT skill_name, proficiency_level, last_updated 
                FROM skills 
                WHERE user_id = '{st.session_state.user_id}'
                ORDER BY proficiency_level DESC
                """, conn)
                
                conn.close()
                
                # Afficher les statistiques générales
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_quiz = len(quiz_results)
                    st.metric("Quiz complétés", total_quiz)
                
                with col2:
                    total_time = study_sessions['duration_minutes'].sum() if not study_sessions.empty else 0
                    st.metric("Temps d'étude total", f"{total_time} min")
                
                with col3:
                    avg_score = quiz_results['score'].sum() / quiz_results['max_score'].sum() * 100 if not quiz_results.empty else 0
                    st.metric("Score moyen aux quiz", f"{avg_score:.1f}%")
                
                # Afficher un graphique résumé
                if not quiz_results.empty or not study_sessions.empty:
                    st.subheader("Aperçu des activités récentes")
                    
                    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
                    
                    # Graphique des performances par sujet
                    if not quiz_results.empty:
                        quiz_summary = quiz_results.groupby('topic').apply(
                            lambda x: (x['score'].sum() / x['max_score'].sum()) * 100
                        ).reset_index(name='percentage')
                        
                        if not quiz_summary.empty:
                            quiz_summary.plot(kind='bar', x='topic', y='percentage', ax=ax[0], color='skyblue')
                            ax[0].set_title('Performance par sujet (%)')
                            ax[0].set_ylabel('Score moyen (%)')
                            ax[0].set_xlabel('Sujet')
                            ax[0].set_ylim(0, 100)
                            
                    # Graphique du temps d'étude par sujet
                    if not study_sessions.empty:
                        study_summary = study_sessions.groupby('topic')['duration_minutes'].sum().reset_index()
                        
                        if not study_summary.empty:
                            study_summary.plot(kind='pie', y='duration_minutes', labels=study_summary['topic'], 
                                            autopct='%1.1f%%', ax=ax[1], startangle=90)
                            ax[1].set_title('Répartition du temps d\'étude')
                            ax[1].set_ylabel('')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Génération du tableau de bord
                    if st.button("Générer un tableau de bord complet"):
                        with st.spinner("Génération du tableau de bord en cours..."):
                            dashboard_path = progress_tracker.generate_dashboard(
                                st.session_state.user_id,
                                output_dir="dashboard"
                            )
                            
                            if dashboard_path and os.path.exists(dashboard_path):
                                st.success("Tableau de bord généré avec succès!")
                                st.image(dashboard_path, caption="Tableau de bord de progression")
                            else:
                                st.error("Erreur lors de la génération du tableau de bord.")
                else:
                    st.info("Aucune donnée de progression disponible. Complétez des quiz et des sessions d'étude pour voir votre progression.")
            
            with tabs[1]:  # Quiz
                st.subheader("Historique des quiz")
                
                if not quiz_results.empty:
                    # Convertir la colonne de date
                    quiz_results['completion_time'] = pd.to_datetime(quiz_results['completion_time'])
                    quiz_results['score_percentage'] = (quiz_results['score'] / quiz_results['max_score']) * 100
                    quiz_results['date'] = quiz_results['completion_time'].dt.strftime('%d/%m/%Y %H:%M')
                    
                    # Afficher le tableau des résultats
                    st.dataframe(
                        quiz_results[['topic', 'score', 'max_score', 'score_percentage', 'date']]
                        .rename(columns={
                            'topic': 'Sujet',
                            'score': 'Score',
                            'max_score': 'Score max',
                            'score_percentage': 'Pourcentage (%)',
                            'date': 'Date'
                        }),
                        hide_index=True
                    )
                    
                    # Graphique d'évolution des scores
                    st.subheader("Évolution de vos performances")
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    quiz_results.sort_values('completion_time').plot(
                        x='completion_time', 
                        y='score_percentage', 
                        kind='line', 
                        marker='o',
                        ax=ax
                    )
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Score (%)')
                    ax.set_ylim(0, 100)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    
                    st.pyplot(fig)
                else:
                    st.info("Aucun historique de quiz disponible. Complétez des quiz pour voir votre progression.")
            
            with tabs[2]:  # Temps d'étude
                st.subheader("Historique des sessions d'étude")
                
                if not study_sessions.empty:
                    # Convertir la colonne de date
                    study_sessions['session_date'] = pd.to_datetime(study_sessions['session_date'])
                    study_sessions['date'] = study_sessions['session_date'].dt.strftime('%d/%m/%Y %H:%M')
                    
                    # Afficher le tableau des sessions
                    st.dataframe(
                        study_sessions[['topic', 'duration_minutes', 'date']]
                        .rename(columns={
                            'topic': 'Sujet',
                            'duration_minutes': 'Durée (min)',
                            'date': 'Date'
                        }),
                        hide_index=True
                    )
                    
                    # Graphique du temps d'étude quotidien
                    st.subheader("Temps d'étude quotidien")
                    
                    daily_study = study_sessions.copy()
                    daily_study['date'] = daily_study['session_date'].dt.date
                    daily_summary = daily_study.groupby('date')['duration_minutes'].sum().reset_index()
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    daily_summary.plot(x='date', y='duration_minutes', kind='bar', ax=ax, color='green')
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Temps d\'étude (minutes)')
                    ax.set_title('Temps d\'étude quotidien')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Statistiques de temps d'étude
                    st.subheader("Statistiques de temps d'étude")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total", f"{study_sessions['duration_minutes'].sum()} min")
                    with col2:
                        st.metric("Moyenne par session", f"{study_sessions['duration_minutes'].mean():.1f} min")
                    with col3:
                        st.metric("Sessions", f"{len(study_sessions)}")
                else:
                    st.info("Aucun historique de session d'étude disponible. Interagissez avec le cours pour enregistrer votre temps d'étude.")
            
            with tabs[3]:  # Compétences
                st.subheader("Niveau de compétences")
                
                if not skills.empty:
                    # Afficher un graphique des compétences
                    fig, ax = plt.subplots(figsize=(10, max(6, len(skills) * 0.5)))
                    
                    # Trier par niveau de compétence
                    skills_sorted = skills.sort_values('proficiency_level')
                    
                    # Créer un graphique à barres horizontales
                    bars = ax.barh(skills_sorted['skill_name'], skills_sorted['proficiency_level'], color='purple')
                    
                    # Ajouter les valeurs sur les barres
                    for bar in bars:
                        width = bar.get_width()
                        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:.1f}', 
                                ha='left', va='center')
                    
                    ax.set_xlabel('Niveau de compétence (1-5)')
                    ax.set_xlim(0, 5.5)
                    ax.set_title('Niveaux de compétence par sujet')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Tableau des compétences avec date de mise à jour
                    skills['last_updated'] = pd.to_datetime(skills['last_updated'])
                    skills['date_maj'] = skills['last_updated'].dt.strftime('%d/%m/%Y %H:%M')
                    
                    st.dataframe(
                        skills[['skill_name', 'proficiency_level', 'date_maj']]
                        .rename(columns={
                            'skill_name': 'Compétence',
                            'proficiency_level': 'Niveau (1-5)',
                            'date_maj': 'Dernière mise à jour'
                        }),
                        hide_index=True
                    )
                    
                    # Section pour mettre à jour manuellement une compétence
                    st.subheader("Mettre à jour une compétence")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        selected_skill = st.selectbox(
                            "Sélectionnez une compétence:",
                            skills['skill_name'].tolist() + ["Nouvelle compétence"]
                        )
                        
                        if selected_skill == "Nouvelle compétence":
                            new_skill_name = st.text_input("Nom de la nouvelle compétence:")
                            selected_skill = new_skill_name if new_skill_name else None
                    
                    with col2:
                        skill_level = st.slider(
                            "Niveau de compétence:", 
                            min_value=1, 
                            max_value=5, 
                            value=3,
                            help="1 = Débutant, 5 = Expert"
                        )
                    
                    if st.button("Mettre à jour la compétence") and selected_skill:
                        progress_tracker.update_skill(
                            st.session_state.user_id,
                            selected_skill,
                            skill_level
                        )
                        st.success(f"Compétence '{selected_skill}' mise à jour avec le niveau {skill_level}.")
                        st.rerun()
                else:
                    st.info("Aucune compétence enregistrée. Complétez des quiz pour enregistrer votre niveau de compétence dans différents domaines.")
                    
                    # Formulaire pour ajouter une nouvelle compétence
                    st.subheader("Ajouter une compétence")
                    
                    new_skill = st.text_input("Nom de la compétence:")
                    skill_level = st.slider(
                        "Niveau de compétence:", 
                        min_value=1, 
                        max_value=5, 
                        value=3,
                        help="1 = Débutant, 5 = Expert"
                    )
                    
                    if st.button("Ajouter la compétence") and new_skill:
                        progress_tracker.update_skill(
                            st.session_state.user_id,
                            new_skill,
                            skill_level
                        )
                        st.success(f"Compétence '{new_skill}' ajoutée avec le niveau {skill_level}.")
                        st.rerun()
            
            with tabs[4]:  # Analyse
                st.subheader("Analyse de vos forces et faiblesses")
                
                if not skills.empty or not quiz_results.empty:
                    # Analyse des performances
                    performance_analysis = skills_analyzer.analyze_quiz_performance(st.session_state.user_id)
                    
                    # Afficher les forces et faiblesses
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 💪 Points forts")
                        
                        if performance_analysis["strengths"]:
                            for strength in performance_analysis["strengths"]:
                                st.success(strength)
                        else:
                            st.info("Aucun point fort identifié pour l'instant.")
                    
                    with col2:
                        st.markdown("### 🎯 Points à améliorer")
                        
                        if performance_analysis["weaknesses"]:
                            for weakness in performance_analysis["weaknesses"]:
                                st.warning(weakness)
                        else:
                            st.info("Aucun point faible identifié pour l'instant.")
                    
                    # Analyse détaillée
                    st.markdown("### Analyse détaillée")
                    st.markdown(performance_analysis["analysis"])
                    
                    # Analyse des écarts de compétences pour un objectif professionnel
                    st.subheader("Analyse des écarts de compétences")
                    
                    career_goal = st.text_input("Entrez votre objectif professionnel ou domaine d'intérêt:")
                    
                    if career_goal:
                        with st.spinner("Analyse en cours..."):
                            gap_analysis = skills_analyzer.skill_gap_analysis(
                                st.session_state.user_id,
                                target_career=career_goal
                            )
                            
                            # Afficher l'analyse des écarts
                            st.markdown(f"### Analyse pour: {career_goal}")
                            
                            # Compétences requises
                            st.markdown("#### Compétences requises")
                            if "required_skills" in gap_analysis and gap_analysis["required_skills"]:
                                for skill in gap_analysis["required_skills"]:
                                    st.markdown(f"- {skill}")
                            else:
                                st.info("Aucune compétence requise spécifique identifiée.")
                            
                            # Compétences existantes
                            st.markdown("#### Compétences que vous possédez déjà")
                            if "existing_skills" in gap_analysis and gap_analysis["existing_skills"]:
                                for skill in gap_analysis["existing_skills"]:
                                    st.markdown(f"- {skill}")
                            else:
                                st.info("Aucune compétence existante identifiée.")
                            
                            # Compétences manquantes
                            st.markdown("#### Compétences à acquérir")
                            if "missing_skills" in gap_analysis and gap_analysis["missing_skills"]:
                                for skill in gap_analysis["missing_skills"]:
                                    st.markdown(f"- {skill}")
                            else:
                                st.info("Aucune compétence manquante identifiée.")
                            
                            # Parcours d'apprentissage recommandé
                            st.markdown("#### Parcours d'apprentissage recommandé")
                            if "learning_path" in gap_analysis:
                                st.markdown(gap_analysis["learning_path"])
                else:
                    st.info("Pas assez de données pour effectuer une analyse approfondie. Complétez plus de quiz et enregistrez vos compétences pour obtenir une analyse détaillée.")
                    
                    # Option pour ajouter des compétences manuellement
                    st.subheader("Ajouter une compétence pour commencer")
                    
                    #new_skill = st.text_input("Nom de la compétence:")
                    new_skill = st.text_input("Nom de la compétence:", key="new_skill_input")
                    skill_level = st.slider(
                        "Niveau actuel:", 
                        min_value=1, 
                        max_value=5, 
                        value=3,
                        help="1 = Débutant, 5 = Expert"
                    )
                    
                    if st.button("Ajouter") and new_skill:
                        progress_tracker.update_skill(
                            st.session_state.user_id,
                            new_skill,
                            skill_level
                        )
                        st.success(f"Compétence '{new_skill}' ajoutée avec le niveau {skill_level}.")
                        st.rerun()

    # Page Recommandations
    # Page Recommandations
    elif page == "Recommandations":
        st.title("Recommandations personnalisées")
        
        if not st.session_state.user_id:
            st.warning("Identifiant utilisateur non détecté. Veuillez vous identifier.")
        else:
            # Récupérer le profil utilisateur
            user_profile = course_recommender.get_user_profile(st.session_state.user_id)
            
            # Afficher le profil utilisateur avec une meilleure mise en page
            st.subheader("Votre profil d'apprentissage")
            
            profile_col1, profile_col2 = st.columns(2)
            
            with profile_col1:
                st.markdown("### 💪 Points forts")
                if user_profile["strengths"]:
                    for strength in user_profile["strengths"]:
                        st.success(f"**{strength}**")
                else:
                    st.info("Aucun point fort identifié pour l'instant. Complétez des quiz pour les découvrir.")
            
            with profile_col2:
                st.markdown("### 🎯 Points à améliorer")
                if user_profile["weaknesses"]:
                    for weakness in user_profile["weaknesses"]:
                        st.warning(f"**{weakness}**")
                else:
                    st.info("Aucun point à améliorer identifié pour l'instant. Complétez des quiz pour les découvrir.")
            
            # Sujets déjà étudiés avec une meilleure visualisation
            st.markdown("### 📚 Sujets déjà étudiés")
            if user_profile["studied_topics"]:
                # Créer une grille de sujets
                topics_per_row = 3
                rows = [user_profile["studied_topics"][i:i+topics_per_row] for i in range(0, len(user_profile["studied_topics"]), topics_per_row)]
                
                for row in rows:
                    topic_cols = st.columns(topics_per_row)
                    for i, topic in enumerate(row):
                        with topic_cols[i]:
                            st.markdown(f"""
                            <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; text-align: center;">
                                {topic}
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("Aucun sujet étudié pour l'instant. Explorez des cours pour commencer votre parcours!")
            
            # Séparateur visuel
            st.markdown("---")
            
            # Formulaire pour obtenir des recommandations personnalisées
            st.subheader("🔍 Obtenir des recommandations personnalisées")
            
            with st.container():
                st.markdown("""
                Précisez vos centres d'intérêt et vos objectifs pour obtenir des recommandations plus pertinentes.
                """)
                
                interests = st.text_input("🌟 Centres d'intérêt (séparés par des virgules):", 
                                        placeholder="Ex: Intelligence artificielle, Statistiques, Programmation web...")
                
                career_goal = st.text_input("🚀 Objectif professionnel ou académique:", 
                                        placeholder="Ex: Data scientist, Développeur web, Certification en IA...")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    generate_button = st.button("📋 Générer des recommandations", use_container_width=True)
            
            # Générer et afficher les recommandations
            if generate_button:
                with st.spinner("Génération des recommandations en cours..."):
                    try:
                        # Utiliser CourseRecommenderOffline - pas besoin d'appel à Ollama
                        recommendations = course_recommender.recommend_courses(
                            st.session_state.user_id,
                            interests=interests,
                            career_goal=career_goal
                        )
                        
                        # Afficher les recommandations avec un design amélioré
                        if recommendations:
                            st.subheader("✨ Recommandations de cours")
                            
                            for i, course in enumerate(recommendations, 1):
                                with st.expander(f"{i}. {course.get('title', 'Cours recommandé')}"):
                                    cols = st.columns([3, 1])
                                    
                                    with cols[0]:
                                        if 'description' in course:
                                            st.markdown(f"**Description**: {course['description']}")
                                        
                                        if 'reason' in course:
                                            st.markdown(f"**Pourquoi ce cours?** {course['reason']}")
                                    
                                    with cols[1]:
                                        if 'level' in course:
                                            level = course['level']
                                            level_colors = {
                                                "débutant": "#28a745",
                                                "intermédiaire": "#fd7e14",
                                                "avancé": "#dc3545"
                                            }
                                            color = level_colors.get(level.lower(), "#17a2b8")
                                            
                                            st.markdown(f"""
                                            <div style="padding: 10px; border-radius: 5px; background-color: {color}; color: white; text-align: center; margin-bottom: 10px;">
                                                <b>Niveau:</b> {level}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        
                                        if 'skills' in course:
                                            st.markdown("**Compétences développées**:")
                                            for skill in course['skills']:
                                                st.markdown(f"- {skill}")
                            
                            # Suggestions supplémentaires
                            st.markdown("---")
                            st.markdown("""
                            ### 💡 Comment utiliser ces recommandations?
                            
                            1. **Explorez les cours**: Cliquez sur chaque recommandation pour en savoir plus
                            2. **Tenez compte du niveau**: Choisissez un cours adapté à votre niveau actuel
                            3. **Commencez par vos points faibles**: Priorisez les cours qui renforcent vos domaines à améliorer
                            4. **Suivez votre progression**: Après avoir suivi un cours, revenez faire un quiz pour mesurer votre progression
                            """)
                        else:
                            st.warning("Aucune recommandation n'a pu être générée en fonction de vos critères. Essayez d'autres intérêts ou objectifs.")
                    
                    except Exception as e:
                        st.error(f"Une erreur s'est produite lors de la génération des recommandations: {str(e)}")
                        st.markdown("""
                        Nous rencontrons des difficultés techniques avec notre système de recommandation. 
                        Voici quelques cours populaires que vous pourriez trouver intéressants:
                        """)
                        
                        # Recommandations par défaut en cas d'erreur
                        fallback_courses = [
                            {"title": "Python pour débutants", "description": "Les bases de la programmation Python."},
                            {"title": "Introduction au Machine Learning", "description": "Concepts fondamentaux de l'apprentissage automatique."},
                            {"title": "Développement Web avec HTML/CSS", "description": "Créez vos premiers sites web."}
                        ]
                        
                        for course in fallback_courses:
                            st.markdown(f"**{course['title']}**: {course['description']}")

            # Afficher les tendances d'apprentissage populaires si aucune recommandation n'est demandée
            if not generate_button:
                st.markdown("### 🔥 Tendances populaires")
                
                # Exemple de tendances (dans une implémentation réelle, ces données viendraient d'une vraie source)
                popular_topics = [
                    {"name": "Intelligence Artificielle", "icon": "🤖", "description": "Fondamentaux de l'IA et apprentissage automatique"},
                    {"name": "Science des Données", "icon": "📊", "description": "Analyse et visualisation de données"},
                    {"name": "Développement Web", "icon": "🌐", "description": "HTML, CSS, JavaScript et frameworks modernes"},
                    {"name": "Cloud Computing", "icon": "☁️", "description": "AWS, Azure, Google Cloud et infrastructure cloud"},
                    {"name": "Cybersécurité", "icon": "🔒", "description": "Protection des systèmes et détection des menaces"},
                    {"name": "Blockchain", "icon": "🔗", "description": "Bases de la blockchain et des contrats intelligents"}
                ]
                
                # Afficher les tendances en grille
                col1, col2 = st.columns(2)
                
                for i, topic in enumerate(popular_topics):
                    with col1 if i % 2 == 0 else col2:
                        st.markdown(f"""
                        <div style="padding: 15px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 15px;">
                            <h4 style="margin:0;">{topic['icon']} {topic['name']}</h4>
                            <p style="margin-top: 5px;">{topic['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Ajouter un bouton pour explorer tous les cours
                st.markdown("""
                <div style="display: flex; justify-content: center; margin-top: 20px;">
                    <a href="https://www.coursera.org/" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #4CAF50; border: none; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px;">
                            Explorer plus de cours en ligne
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
            
# Pied de page
st.markdown("---")
st.markdown("© 2025 IntelliPath - Votre assistant d'apprentissage personnalisé")