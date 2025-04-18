# main.py
import os
import argparse

# Configuration pour utiliser les modèles locaux ou en ligne
def configure_environment():
    parser = argparse.ArgumentParser(description='IntelliPath - Agent d\'apprentissage personnalisé')
    parser.add_argument('--model', type=str, default='llama3', help='Modèle à utiliser (llama3, llama3:70b, etc.)')
    parser.add_argument('--interface', type=str, default='streamlit', choices=['gradio', 'streamlit'], help='Interface utilisateur à utiliser')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    
    args = parser.parse_args()
    
    os.environ['INTELLIPATH_MODEL'] = args.model
    os.environ['INTELLIPATH_DEBUG'] = str(args.debug).lower()
    
    print(f"Configuration: Modèle={args.model}, Interface={args.interface}, Debug={args.debug}")
    
    return args

if __name__ == "__main__":
    args = configure_environment()
    
    # Lancer l'interface appropriée
    if args.interface == 'streamlit':
        os.system("streamlit run streamlit_app.py")
    else:
        import run  # Lancer l'interface Gradio existante
