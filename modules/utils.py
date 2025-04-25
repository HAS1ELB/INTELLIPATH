import re
import markdown
import pandas as pd
from typing import List, Dict, Any

def markdown_to_html(markdown_text: str) -> str:
    """
    Convertit un texte Markdown en HTML
    
    Args:
        markdown_text: Texte au format Markdown
        
    Returns:
        str: Le HTML généré
    """
    return markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])

def extract_modules_from_syllabus(syllabus: str) -> List[Dict[str, Any]]:
    """
    Extrait les modules d'un syllabus au format Markdown
    
    Args:
        syllabus: Syllabus au format Markdown
        
    Returns:
        List[Dict[str, Any]]: Liste des modules extraits
    """
    # Pattern pour trouver les titres de modules (## Module X ou ### Module X)
    module_pattern = r'#{2,3}\s+(Module\s+\d+[.:]\s+.+)'
    module_titles = re.findall(module_pattern, syllabus)
    
    modules = []
    
    # Extraction du contenu de chaque module
    for i, title in enumerate(module_titles):
        start_index = syllabus.find(title)
        if start_index == -1:
            continue
        
        # Trouver la fin du module (début du module suivant ou fin du texte)
        if i < len(module_titles) - 1:
            end_index = syllabus.find(module_titles[i + 1], start_index)
        else:
            end_index = len(syllabus)
        
        # Extraire le contenu du module
        module_content = syllabus[start_index:end_index].strip()
        
        # Créer un dictionnaire pour le module
        module = {
            "title": title,
            "content": module_content,
            "index": i + 1
        }
        
        modules.append(module)
    
    return modules

def create_progress_tracker(modules: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Crée un tableau de suivi de progression basé sur les modules du syllabus
    
    Args:
        modules: Liste des modules extraits du syllabus
        
    Returns:
        pd.DataFrame: DataFrame pour le suivi de progression
    """
    data = {
        "Module": [m["title"] for m in modules],
        "Terminé": [False for _ in modules],
        "Notes": ["" for _ in modules],
        "Date de complétion": ["" for _ in modules]
    }
    
    return pd.DataFrame(data)
