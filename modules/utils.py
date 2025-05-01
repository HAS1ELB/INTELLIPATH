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
    return markdown.markdown(markdown_text, extensions=['tables', 'fenced_code', 'codehilite', 'attr_list', 'md_in_html'])

def extract_modules_from_syllabus(syllabus: str) -> List[Dict[str, Any]]:
    """
    Extrait les modules d'un syllabus au format Markdown
    
    Args:
        syllabus: Syllabus au format Markdown
        
    Returns:
        List[Dict[str, Any]]: Liste des modules extraits
    """
    # Pattern amélioré pour trouver les titres de modules (## Module X ou ### Module X)
    # Prend en compte différents formats possibles (Module X, Partie X, Section X, etc.)
    module_pattern = r'#{2,3}\s+((?:Module|Partie|Section|Chapitre|Unité)\s+\d+[.:]\s+.+)'
    module_titles = re.findall(module_pattern, syllabus)
    
    # Si aucun module n'est trouvé avec le pattern spécifique, chercher des titres de niveau 2 génériques
    if not module_titles:
        generic_title_pattern = r'#{2}\s+(.+)'
        module_titles = re.findall(generic_title_pattern, syllabus)
    
    modules = []
    
    # Extraction du contenu de chaque module
    for i, title in enumerate(module_titles):
        start_index = syllabus.find(title) - 3  # Pour inclure les # du titre
        if start_index < 0:
            continue
        
        # Trouver la fin du module (début du module suivant ou fin du texte)
        if i < len(module_titles) - 1:
            next_title = module_titles[i + 1]
            end_index = syllabus.find(next_title, start_index) - 3  # Pour exclure les # du titre suivant
        else:
            end_index = len(syllabus)
        
        # Extraire le contenu du module
        module_content = syllabus[start_index:end_index].strip()
        
        # Créer un dictionnaire pour le module
        module = {
            "title": title,
            "content": module_content,
            "index": i + 1,
            # Extraire les sous-sections du module
            "sub_sections": extract_subsections(module_content)
        }
        
        modules.append(module)
    
    return modules

def extract_subsections(module_content: str) -> List[Dict[str, str]]:
    """
    Extrait les sous-sections d'un module
    
    Args:
        module_content: Contenu du module au format Markdown
        
    Returns:
        List[Dict[str, str]]: Liste des sous-sections extraites
    """
    # Pattern pour trouver les titres de sous-sections (#### ou ###)
    # Selon le niveau du titre du module, les sous-sections peuvent être de niveau différent
    subsection_pattern = r'#{3,4}\s+(.+)'
    subsection_titles = re.findall(subsection_pattern, module_content)
    
    subsections = []
    
    # Extraction du contenu de chaque sous-section
    for i, title in enumerate(subsection_titles):
        start_index = module_content.find(title)
        if start_index == -1:
            continue
        
        # Trouver la fin de la sous-section (début de la sous-section suivante ou fin du module)
        if i < len(subsection_titles) - 1:
            next_title = subsection_titles[i + 1]
            end_index = module_content.find(next_title, start_index)
        else:
            end_index = len(module_content)
        
        # Extraire le contenu de la sous-section
        subsection_content = module_content[start_index:end_index].strip()
        
        # Créer un dictionnaire pour la sous-section
        subsection = {
            "title": title,
            "content": subsection_content
        }
        
        subsections.append(subsection)
    
    return subsections

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
        "Date de complétion": ["" for _ in modules],
        "Temps estimé (heures)": [2 for _ in modules]  # Valeur par défaut arbitraire
    }
    
    return pd.DataFrame(data)

def extract_key_concepts(syllabus: str) -> List[str]:
    """
    Extrait les concepts clés mentionnés dans le syllabus
    
    Args:
        syllabus: Le syllabus au format Markdown
        
    Returns:
        List[str]: Liste des concepts clés
    """
    # Pattern pour trouver les listes à puces avec des concepts clés
    concepts_patterns = [
        r'[Cc]oncepts? clés?.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)',
        r'[Cc]ompétences? à acquérir.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)',
        r'[Pp]rincipaux concepts.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)',
        r'[Nn]otions? importantes?.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)'
    ]
    
    all_concepts = []
    
    # Recherche des concepts clés selon différents patterns
    for pattern in concepts_patterns:
        matches = re.findall(pattern, syllabus, re.DOTALL)
        for match in matches:
            # Extraire chaque concept de la liste à puces
            concepts = re.findall(r'\*\s+(.*?)[\r\n]', match)
            all_concepts.extend(concepts)
    
    # Éliminer les doublons et nettoyer les concepts
    clean_concepts = []
    for concept in all_concepts:
        concept = concept.strip()
        if concept and concept not in clean_concepts:
            clean_concepts.append(concept)
    
    return clean_concepts

def extract_resources(syllabus: str) -> Dict[str, List[str]]:
    """
    Extrait les ressources recommandées dans le syllabus
    
    Args:
        syllabus: Le syllabus au format Markdown
        
    Returns:
        Dict[str, List[str]]: Dictionnaire des ressources par type
    """
    # Pattern pour trouver les sections de ressources
    resources_section_pattern = r'(?:### |## )(?:Ressources|Bibliographie|Références).*?(?=###|##|$)'
    resources_sections = re.findall(resources_section_pattern, syllabus, re.DOTALL)
    
    # Types de ressources à rechercher
    resource_types = {
        "Livres": [r'[Ll]ivres?', r'[Oo]uvrages?'],
        "Articles": [r'[Aa]rticles?', r'[Pp]ublications?'],
        "Vidéos": [r'[Vv]idéos?', r'[Tt]utoriels? vidéo'],
        "Sites Web": [r'[Ss]ites? [Ww]eb', r'[Ll]iens?', r'[Ww]eb'],
        "Cours en ligne": [r'[Cc]ours en ligne', r'[Mm]ooc', r'[Ff]ormations?'],
        "Outils": [r'[Oo]utils?', r'[Ll]ogiciels?', r'[Aa]pplications?']
    }
    
    # Dictionnaire pour stocker les ressources par type
    resources = {resource_type: [] for resource_type in resource_types}
    
    # Si aucune section de ressources n'est trouvée, chercher dans tout le document
    if not resources_sections:
        resources_sections = [syllabus]
    
    # Parcourir chaque section de ressources
    for section in resources_sections:
        # Chercher les ressources par type
        for resource_type, patterns in resource_types.items():
            for pattern in patterns:
                # Chercher une sous-section avec ce type de ressource
                subsection_pattern = f'(?:### |#### ){pattern}.*?(?=###|####|$)'
                subsections = re.findall(subsection_pattern, section, re.DOTALL)
                
                for subsection in subsections:
                    # Extraire les ressources de la liste à puces
                    items = re.findall(r'\*\s+(.*?)[\r\n]', subsection)
                    for item in items:
                        if item.strip() and item.strip() not in resources[resource_type]:
                            resources[resource_type].append(item.strip())
                
                # Si pas de sous-section, chercher les listes à puces précédées par le type de ressource
                if not subsections:
                    list_pattern = f'{pattern}.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)'
                    lists = re.findall(list_pattern, section, re.DOTALL)
                    
                    for list_items in lists:
                        items = re.findall(r'\*\s+(.*?)[\r\n]', list_items)
                        for item in items:
                            if item.strip() and item.strip() not in resources[resource_type]:
                                resources[resource_type].append(item.strip())
    
    # Nettoyer les types de ressources vides
    resources = {k: v for k, v in resources.items() if v}
    
    return resources
