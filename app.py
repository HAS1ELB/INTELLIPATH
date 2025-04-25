import os
import time
import streamlit as st
from dotenv import load_dotenv

# Chargement des modules personnalisés
from modules.syllabus_generator import generate_syllabus
from modules.teaching_agent import TeachingAgent

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

# Initialisation des variables de session
if "teaching_agent" not in st.session_state:
    st.session_state.teaching_agent = TeachingAgent()
if "syllabus" not in st.session_state:
    st.session_state.syllabus = ""
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""

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
        st.experimental_rerun()

# Corps principal de l'application
st.title("IntelliPath - Assistant d'apprentissage IA")

# Créer des onglets pour les différentes fonctionnalités
tab1, tab2 = st.tabs(["📚 Générer un syllabus", "👨‍🏫 Discuter avec l'instructeur"])

with tab1:
    st.markdown("""
    ### Générez un syllabus de cours personnalisé
    
    Entrez le sujet que vous souhaitez apprendre, et notre IA générera un syllabus détaillé 
    pour vous guider dans votre parcours d'apprentissage.
    """)
    
    # Formulaire pour générer un nouveau syllabus
    with st.form("syllabus_form"):
        topic = st.text_input("Sujet à étudier:", placeholder="ex: Machine Learning, Python avancé, etc.")
        level = st.select_slider("Niveau de difficulté:", options=["Débutant", "Intermédiaire", "Avancé"])
        duration = st.select_slider("Durée approximative:", options=["1-2 semaines", "1 mois", "3 mois", "6 mois"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            include_projects = st.checkbox("Inclure des projets pratiques", value=True)
        with col2:
            include_resources = st.checkbox("Inclure des ressources", value=True)
        with col3:
            include_assessments = st.checkbox("Inclure des évaluations", value=True)
        
        submit_button = st.form_submit_button("Générer le syllabus", use_container_width=True)
        
    if submit_button and topic:
        with st.spinner("Génération de votre syllabus personnalisé..."):
            task = f"Générer un syllabus de cours {level.lower()} pour enseigner {topic} sur une durée de {duration}."
            if include_projects:
                task += " Inclure des projets pratiques."
            if include_resources:
                task += " Inclure des ressources d'apprentissage."
            if include_assessments:
                task += " Inclure des méthodes d'évaluation."
            
            # Appel à la fonction de génération de syllabus
            syllabus = generate_syllabus(topic, task, temperature)
            
            # Enregistrer le syllabus dans la session
            st.session_state.syllabus = syllabus
            st.session_state.current_topic = topic
            
            # Initialiser l'agent d'enseignement avec le nouveau syllabus
            st.session_state.teaching_agent.seed_agent(syllabus, topic)
            
            # Afficher le syllabus avec une mise en forme markdown
            st.markdown("### Votre syllabus personnalisé")
            st.markdown(syllabus)
            
            # Option pour télécharger le syllabus
            st.download_button(
                label="Télécharger le syllabus (Markdown)",
                data=syllabus,
                file_name=f"syllabus_{topic.replace(' ', '_').lower()}.md",
                mime="text/markdown",
            )
    
    # Afficher le syllabus déjà généré
    if st.session_state.syllabus and not submit_button:
        st.markdown("### Syllabus actuel")
        st.markdown(st.session_state.syllabus)
        
        # Option pour télécharger le syllabus
        st.download_button(
            label="Télécharger le syllabus (Markdown)",
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
        # Afficher l'historique des conversations
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
        
        # Zone de saisie pour la question de l'utilisateur
        user_question = st.chat_input("Posez une question sur le sujet...")
        
        if user_question:
            # Ajouter la question de l'utilisateur à l'historique
            st.session_state.conversation_history.append({"role": "user", "content": user_question})
            st.chat_message("user").write(user_question)
            
            # Obtenir la réponse de l'agent d'enseignement
            with st.chat_message("assistant"):
                with st.spinner("L'instructeur réfléchit..."):
                    response = st.session_state.teaching_agent.respond(user_question)
                    
                    # Simuler une réponse progressive pour une meilleure expérience utilisateur
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in response.split():
                        full_response += chunk + " "
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.05)
                    
                    message_placeholder.markdown(full_response)
            
            # Ajouter la réponse à l'historique
            st.session_state.conversation_history.append({"role": "assistant", "content": response})
            
        # Afficher des suggestions de questions
        if len(st.session_state.conversation_history) < 2:
            st.markdown("### Suggestions de questions:")
            suggestions = [
                "Pouvez-vous m'expliquer davantage le premier module?",
                "Quels sont les prérequis pour ce cours?",
                "Comment puis-je appliquer ces connaissances dans des projets réels?"
            ]
            
            cols = st.columns(len(suggestions))
            for i, col in enumerate(cols):
                if col.button(suggestions[i]):
                    st.session_state.conversation_history.append({"role": "user", "content": suggestions[i]})
                    st.rerun()

# Footer
st.divider()
st.caption("IntelliPath - Propulsé par Groq API et meta-llama/llama-4-scout-17b-16e-instruct")
