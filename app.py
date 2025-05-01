import os
import time
import streamlit as st
from dotenv import load_dotenv

# Chargement des modules personnalisés
from modules.syllabus_generator import generate_syllabus
from modules.teaching_agent import TeachingAgent
from modules.utils import extract_modules_from_syllabus, markdown_to_html
from modules.quiz_generator import QuizGenerator  # Nouvel import

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page Streamlit
st.set_page_config(
    page_title="IntelliPath - Assistant d'apprentissage IA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application de CSS personnalisé
def load_css():
    with open("assets/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except:
    st.warning("Fichier CSS non trouvé. L'interface utilisera le style par défaut.")
    
st.markdown("""
<style>
    /* Force le thème sombre */
    :root {
        --background-color: #1a1a2e;
        --text-color: #f0f0f0;
        --font-size: 16px;
    }
    
    /* Amélioration du contraste des étiquettes de formulaire */
    label {
        color: #c0c0c0 !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
        display: block !important;
    }
    
    /* Amélioration de l'espacement général */
    .main > div {
        padding: 2em;
    }
    
    /* Meilleur affichage des titres principaux */
    .main h1:first-child {
        background: linear-gradient(90deg, #4fd1c5, #63b3ed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        margin-bottom: 1.5rem;
        text-align: center;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
if "teaching_agent" not in st.session_state:
    st.session_state.teaching_agent = TeachingAgent()
if "syllabus" not in st.session_state:
    st.session_state.syllabus = ""
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""
if "modules" not in st.session_state:
    st.session_state.modules = []
if "quiz_generator" not in st.session_state:  # Nouvelle variable de session
    st.session_state.quiz_generator = QuizGenerator()
if "current_quiz" not in st.session_state:  # Pour stocker le quiz actuel
    st.session_state.current_quiz = []
if "quiz_results" not in st.session_state:  # Pour stocker les résultats
    st.session_state.quiz_results = []
if "quiz_history" not in st.session_state:  # Pour stocker l'historique des quiz
    st.session_state.quiz_history = []

# Sidebar pour les informations et paramètres
with st.sidebar:
    st.image("assets/logo.png", width=100)
    st.title("IntelliPath")
    st.subheader("Votre parcours d'apprentissage personnalisé")
    
    st.divider()
    
    # Paramètres du modèle
    st.subheader("Paramètres")
    temperature = st.slider("Créativité de l'IA", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    if st.button("Réinitialiser la conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()
    
    # Affichage des modules du syllabus si disponibles
    if st.session_state.modules:
        st.divider()
        st.subheader("Modules du syllabus")
        for module in st.session_state.modules:
            module_title = module["title"].split(":", 1)[1].strip() if ":" in module["title"] else module["title"]
            if st.sidebar.button(f"📘 {module_title}", key=f"module_{module['index']}", use_container_width=True):
                # Préparer une question sur ce module spécifique
                question = f"Pouvez-vous me détailler le contenu du module: {module_title}?"
                st.session_state.conversation_history.append({"role": "user", "content": question})
                st.rerun()

# Corps principal de l'application
st.title("IntelliPath - Assistant d'apprentissage IA")

# Créer des onglets pour les différentes fonctionnalités
tab1, tab2, tab3 = st.tabs(["📚 Générer un syllabus", "👨‍🏫 Discuter avec l'instructeur", "📝 Quiz d'évaluation"])

with tab1:
    st.markdown("""
    ### Générez un syllabus de cours personnalisé
    
    Entrez le sujet que vous souhaitez apprendre, et notre IA générera un syllabus détaillé 
    pour vous guider dans votre parcours d'apprentissage.
    """)
    
    # Formulaire pour générer un nouveau syllabus
    with st.form("syllabus_form"):
        topic = st.text_input("Sujet à étudier:", placeholder="ex: Machine Learning, Python avancé, etc.")
        col1, col2 = st.columns(2)
        
        with col1:
            level = st.select_slider("Niveau de difficulté:", options=["Débutant", "Intermédiaire", "Avancé"])
        with col2:
            duration = st.select_slider("Durée approximative:", options=["1-2 semaines", "1 mois", "3 mois", "6 mois"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            include_projects = st.checkbox("Inclure des projets pratiques", value=True)
        with col2:
            include_resources = st.checkbox("Inclure des ressources", value=True)
        with col3:
            include_assessments = st.checkbox("Inclure des évaluations", value=True)
            
        learning_style = st.radio("Style d'apprentissage préféré:", 
                                 ["Visuel", "Auditif", "Lecture/Écriture", "Pratique"], 
                                 horizontal=True)
        
        submit_button = st.form_submit_button("Générer le syllabus", use_container_width=True)
        
    if submit_button and topic:
        with st.spinner("Génération de votre syllabus personnalisé..."):
            task = f"Générer un syllabus de cours {level.lower()} pour enseigner {topic} sur une durée de {duration}."
            task += f" Adapter le contenu pour un apprenant au style d'apprentissage {learning_style.lower()}."
            
            if include_projects:
                task += " Inclure des projets pratiques."
            if include_resources:
                task += " Inclure des ressources d'apprentissage variées (livres, articles, vidéos, podcasts)."
            if include_assessments:
                task += " Inclure des méthodes d'évaluation progressives."
            
            # Appel à la fonction de génération de syllabus
            syllabus = generate_syllabus(topic, task, temperature)
            
            # Enregistrer le syllabus dans la session
            st.session_state.syllabus = syllabus
            st.session_state.current_topic = topic
            
            # Extraire les modules du syllabus
            st.session_state.modules = extract_modules_from_syllabus(syllabus)
            
            # Initialiser l'agent d'enseignement avec le nouveau syllabus
            st.session_state.teaching_agent.seed_agent(syllabus, topic)
            
            # Réinitialiser les quiz et résultats associés
            st.session_state.current_quiz = []
            st.session_state.quiz_results = []
            
            # Afficher le syllabus avec une mise en forme markdown
            st.markdown("### Votre syllabus personnalisé")
            st.markdown(syllabus)
            
            # Option pour télécharger le syllabus
            col1, col2 = st.columns([1, 2])
            with col1:
                st.download_button(
                    label="📥 Télécharger le syllabus (Markdown)",
                    data=syllabus,
                    file_name=f"syllabus_{topic.replace(' ', '_').lower()}.md",
                    mime="text/markdown",
                )
    
    # Afficher le syllabus déjà généré
    if st.session_state.syllabus and not submit_button:
        st.markdown("### Syllabus actuel")
        with st.expander("Afficher le syllabus complet", expanded=True):
            st.markdown(st.session_state.syllabus)
        
        # Option pour télécharger le syllabus
        col1, col2 = st.columns([1, 2])
        with col1:
            st.download_button(
                label="📥 Télécharger le syllabus (Markdown)",
                data=st.session_state.syllabus,
                file_name=f"syllabus_{st.session_state.current_topic.replace(' ', '_').lower()}.md",
                mime="text/markdown",
            )

with tab2:
    st.markdown("""
    ### Discutez avec votre instructeur IA
    
    Posez des questions sur le contenu du syllabus, demandez des explications supplémentaires,
    ou explorez des aspects spécifiques du sujet avec votre instructeur IA personnalisé.
    """)
    
    # Vérifier si un syllabus a été généré
    if not st.session_state.syllabus:
        st.info("Veuillez d'abord générer un syllabus dans l'onglet précédent.")
    else:
        # Afficher un résumé du sujet actuel
        st.markdown(f"""
        **Sujet actuel**: {st.session_state.current_topic}  
        **Nombre de modules**: {len(st.session_state.modules)}
        """)
        
        # Afficher l'historique des conversations
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                with st.chat_message("user", avatar="🧑‍🎓"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="👨‍🏫"):
                    st.write(message["content"])
        
        # Zone de saisie pour la question de l'utilisateur
        user_question = st.chat_input("Posez une question sur le sujet...")
        
        if user_question:
            # Ajouter la question de l'utilisateur à l'historique
            st.session_state.conversation_history.append({"role": "user", "content": user_question})
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.write(user_question)
            
            # Obtenir la réponse de l'agent d'enseignement
            with st.chat_message("assistant", avatar="👨‍🏫"):
                with st.spinner("L'instructeur réfléchit..."):
                    response = st.session_state.teaching_agent.respond(user_question)
                    
                    # Simuler une réponse progressive pour une meilleure expérience utilisateur
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Diviser par phrases plutôt que par mots pour un affichage plus naturel
                    for chunk in response.split(". "):
                        if not chunk.endswith("."):
                            chunk += "."
                        full_response += chunk + " "
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.1)
                    
                    message_placeholder.markdown(full_response)
            
            # Ajouter la réponse à l'historique
            st.session_state.conversation_history.append({"role": "assistant", "content": response})
            
        # Afficher des suggestions de questions personnalisées basées sur le syllabus
        if st.session_state.modules and len(st.session_state.conversation_history) < 2:
            st.markdown("### Suggestions de questions:")
            
            # Générer des suggestions basées sur les modules
            suggestions = [
                f"Pouvez-vous m'expliquer davantage le module sur {st.session_state.modules[0]['title'].split(':', 1)[1].strip() if ':' in st.session_state.modules[0]['title'] else st.session_state.modules[0]['title']} ?",
                f"Quels sont les prérequis pour apprendre {st.session_state.current_topic} ?",
                f"Comment puis-je appliquer ces connaissances en {st.session_state.current_topic} dans des projets réels ?",
                f"Quelles sont les meilleures ressources pour approfondir {st.session_state.current_topic} ?",
                f"Pourriez-vous me suggérer un parcours d'apprentissage plus court pour {st.session_state.current_topic} ?"
            ]
            
            # Créer des lignes de 2 boutons chacune
            for i in range(0, len(suggestions), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(suggestions):
                        if col.button(suggestions[i + j], key=f"suggestion_{i+j}", use_container_width=True):
                            st.session_state.conversation_history.append({"role": "user", "content": suggestions[i + j]})
                            st.rerun()

with tab3:
    st.markdown("""
    ### Testez vos connaissances avec des quiz personnalisés
    
    Choisissez un module du syllabus et générez un quiz personnalisé pour évaluer votre compréhension.
    """)
    
    # Vérifier si un syllabus a été généré
    if not st.session_state.syllabus:
        st.info("Veuillez d'abord générer un syllabus dans l'onglet précédent.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Sélection du module pour le quiz
            module_options = [f"Module {m['index']}: {m['title'].split(':', 1)[1].strip() if ':' in m['title'] else m['title']}" 
                             for m in st.session_state.modules]
            selected_module = st.selectbox("Choisissez un module pour le quiz:", 
                                         ["Tous les modules"] + module_options)
        
        with col2:
            # Nombre de questions
            num_questions = st.slider("Nombre de questions:", min_value=3, max_value=10, value=5, step=1)
            
            # Niveau de difficulté
            difficulty = st.select_slider("Niveau de difficulté:", 
                                       options=["facile", "moyen", "difficile"])
        
        # Bouton pour générer le quiz
        if st.button("Générer un quiz", key="generate_quiz_button", use_container_width=True):
            with st.spinner("Génération du quiz en cours..."):
                # Déterminer le sujet du quiz en fonction de la sélection
                if selected_module == "Tous les modules":
                    quiz_topic = st.session_state.current_topic
                else:
                    # Extraire l'index du module sélectionné
                    module_idx = int(selected_module.split(":")[0].replace("Module ", "")) - 1
                    module_content = st.session_state.modules[module_idx]["content"]
                    quiz_topic = selected_module
                
                # Générer le quiz
                st.session_state.current_quiz = st.session_state.quiz_generator.generate_quiz(
                    topic=quiz_topic,
                    difficulty=difficulty,
                    num_questions=num_questions
                )
                st.session_state.quiz_results = []
        
        # Afficher le quiz s'il est disponible
        if st.session_state.current_quiz:
            st.markdown("## Quiz")
            
            # Créer un formulaire pour le quiz
            with st.form("quiz_form"):
                for i, question in enumerate(st.session_state.current_quiz):
                    st.markdown(f"### Question {i+1}")
                    st.markdown(question.question)
                    
                    # Afficher les options avec des boutons radio
                    answer_key = f"question_{i}"
                    user_answer = st.radio(
                        "Choisissez votre réponse:",
                        options=question.options,
                        key=answer_key
                    )
                    
                    # Stocker l'index de la réponse choisie
                    selected_idx = question.options.index(user_answer) if user_answer in question.options else -1
                    
                    st.write("---")
                
                submit_button = st.form_submit_button("Soumettre les réponses", use_container_width=True)
            
            # Traiter les réponses soumises
            if submit_button:
                score = 0
                results = []
                
                for i, question in enumerate(st.session_state.current_quiz):
                    answer_key = f"question_{i}"
                    user_answer = st.session_state[answer_key]
                    selected_idx = question.options.index(user_answer) if user_answer in question.options else -1
                    
                    is_correct = (selected_idx == question.correct_answer)
                    if is_correct:
                        score += 1
                    
                    results.append({
                        "question": question.question,
                        "user_answer": user_answer,
                        "correct_answer": question.options[question.correct_answer],
                        "is_correct": is_correct,
                        "explanation": question.explanation
                    })
                
                st.session_state.quiz_results = results
                
                # Afficher les résultats
                st.markdown(f"## Résultats du quiz: {score}/{len(st.session_state.current_quiz)} points")
                
                for i, result in enumerate(st.session_state.quiz_results):
                    with st.expander(f"Question {i+1} - {'✅ Correct' if result['is_correct'] else '❌ Incorrect'}"):
                        st.markdown(f"**Question:** {result['question']}")
                        st.markdown(f"**Votre réponse:** {result['user_answer']}")
                        st.markdown(f"**Réponse correcte:** {result['correct_answer']}")
                        st.markdown(f"**Explication:** {result['explanation']}")
                
                # Ajouter ce score à l'historique des progrès
                current_quiz_id = f"{selected_module}_{difficulty}_{num_questions}"
                if not any(h["id"] == current_quiz_id for h in st.session_state.quiz_history):
                    st.session_state.quiz_history.append({
                        "id": current_quiz_id,
                        "module": selected_module,
                        "difficulty": difficulty,
                        "score": (score / len(st.session_state.current_quiz)) * 100,
                        "date": time.strftime("%Y-%m-%d %H:%M")
                    })
                
                # Afficher un graphique des progrès si plusieurs quiz ont été complétés
                if len(st.session_state.quiz_history) > 1:
                    st.markdown("## Vos progrès")
                    
                    import matplotlib.pyplot as plt
                    import pandas as pd
                    import numpy as np
                    
                    # Créer un dataframe avec l'historique des quiz
                    df = pd.DataFrame(st.session_state.quiz_history)
                    
                    # Créer un graphique
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(df["date"], df["score"], marker='o', linestyle='-', linewidth=2)
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Score (%)")
                    ax.set_title("Évolution de vos scores aux quiz")
                    ax.grid(True, alpha=0.3)
                    
                    # Améliorer l'affichage
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    # Afficher le graphique
                    st.pyplot(fig)
                
                # Ajouter un bouton pour retourner au syllabus et poursuivre l'apprentissage
                if st.button("Retourner à l'étude du syllabus", use_container_width=True):
                    st.switch_page("app.py")  # Cette fonction nécessite une organisation multi-pages

# Footer
st.divider()
with st.container():
    cols = st.columns(3)
    with cols[1]:
        st.caption("IntelliPath - Propulsé par Groq API et meta-llama/llama-4-scout-17b-16e-instruct")
