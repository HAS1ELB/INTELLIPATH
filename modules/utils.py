import re
import markdown
import pandas as pd
from typing import List, Dict, Any

def markdown_to_html(markdown_text: str) -> str:
    return markdown.markdown(markdown_text, extensions=['tables', 'fenced_code', 'codehilite', 'attr_list', 'md_in_html'])

def extract_modules_from_syllabus(syllabus: str) -> List[Dict[str, Any]]:
    module_pattern = r'#{2,3}\s+((?:Module|Partie|Section|Chapitre|Unité)\s+\d+[.:]\s+.+)'
    module_titles = re.findall(module_pattern, syllabus)
    
    if not module_titles:
        generic_title_pattern = r'#{2}\s+(.+)'
        module_titles = re.findall(generic_title_pattern, syllabus)
    
    modules = []
    
    for i, title in enumerate(module_titles):
        start_index = syllabus.find(title) - 3
        if start_index < 0:
            continue
        
        if i < len(module_titles) - 1:
            next_title = module_titles[i + 1]
            end_index = syllabus.find(next_title, start_index) - 3
        else:
            end_index = len(syllabus)
        
        module_content = syllabus[start_index:end_index].strip()
        
        module = {
            "title": title,
            "content": module_content,
            "index": i + 1,
            "sub_sections": extract_subsections(module_content)
        }
        
        modules.append(module)
    
    return modules

def extract_subsections(module_content: str) -> List[Dict[str, str]]:
    subsection_pattern = r'#{3,4}\s+(.+)'
    subsection_titles = re.findall(subsection_pattern, module_content)
    
    subsections = []
    
    for i, title in enumerate(subsection_titles):
        start_index = module_content.find(title)
        if start_index == -1:
            continue
        
        if i < len(subsection_titles) - 1:
            next_title = subsection_titles[i + 1]
            end_index = module_content.find(next_title, start_index)
        else:
            end_index = len(module_content)
        
        subsection_content = module_content[start_index:end_index].strip()
        
        subsection = {
            "title": title,
            "content": subsection_content
        }
        
        subsections.append(subsection)
    
    return subsections

def extract_key_concepts(syllabus: str) -> List[str]:
    concepts_patterns = [
        r'[Cc]oncepts? clés?.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)',
        r'[Cc]ompétences? à acquérir.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)',
        r'[Pp]rincipaux concepts.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)',
        r'[Nn]otions? importantes?.*?[\r\n]+((?:\*\s+.*?[\r\n]+)+)'
    ]
    
    all_concepts = []
    
    for pattern in concepts_patterns:
        matches = re.findall(pattern, syllabus, re.DOTALL)
        for match in matches:
            concepts = re.findall(r'\*\s+(.*?)[\r\n]', match)
            all_concepts.extend(concepts)
    
    clean_concepts = []
    for concept in all_concepts:
        concept = concept.strip()
        if concept and concept not in clean_concepts:
            clean_concepts.append(concept)
    
    return clean_concepts

def extract_resources(syllabus: str) -> Dict[str, List[str]]:
    resources_section_pattern = r'(?:### |## )(?:Ressources|Bibliographie|Références).*?(?=###|##|$)'
    resources_sections = re.findall(resources_section_pattern, syllabus, re.DOTALL)
    
    resource_types = {
        "Livres": [r'[Ll]ivres?', r'[Oo]uvrages?'],
        "Articles": [r'[Aa]rticles?', r'[Pp]ublications?'],
        "Vidéos": [r'[Vv]idéos?', r'[Tt]utoriels? vidéo'],
        "Sites Web": [r'[Ss]ites? [Ww]eb', r'[Ll]iens'],
        "Outils": [r'[Oo]utils', r'[Ll]ogiciels', r'[Aa]pplications'],
    }
    
    extracted_resources = {k: [] for k in resource_types}
    
    for section in resources_sections:
        for res_type, patterns in resource_types.items():
            for pattern in patterns:
                subsection_pattern = f"(?:#### |### ){pattern}.*?(?=####|###|$)"
                subsections = re.findall(subsection_pattern, section, re.DOTALL)
                
                for subsection in subsections:
                    resources = re.findall(r'\*\s+(.*?)[\r\n]', subsection)
                    extracted_resources[res_type].extend([r.strip() for r in resources if r.strip()])
    
    return extracted_resources

def create_progress_tracker(modules: List[Dict[str, Any]]) -> pd.DataFrame:
    data = {
        "Module": [m["title"] for m in modules],
        "Terminé": [False for _ in modules],
        "Notes": ["" for _ in modules],
        "Date de complétion": ["" for _ in modules],
        "Temps estimé (heures)": [2 for _ in modules]
    }
    
    return pd.DataFrame(data)

def estimate_reading_time(text: str) -> int:
    words = len(re.findall(r'\w+', text))
    minutes = words / 225  # Vitesse de lecture moyenne
    return max(1, round(minutes))

def generate_study_plan(syllabus: str, duration_weeks: int) -> Dict[str, List[Dict[str, Any]]]:
    modules = extract_modules_from_syllabus(syllabus)
    total_modules = len(modules)
    
    if total_modules == 0:
        return {"weeks": []}
    
    # Distribution des modules par semaine
    modules_per_week = max(1, round(total_modules / duration_weeks))
    
    study_plan = {"weeks": []}
    
    for week_num in range(1, duration_weeks + 1):
        start_module_idx = (week_num - 1) * modules_per_week
        end_module_idx = min(start_module_idx + modules_per_week, total_modules)
        
        if start_module_idx >= total_modules:
            break
        
        week_modules = modules[start_module_idx:end_module_idx]
        
        week_plan = {
            "week_number": week_num,
            "modules": [],
            "estimated_hours": 0
        }
        
        for module in week_modules:
            # Estimer le temps de lecture du module
            reading_time = estimate_reading_time(module["content"])
            
            # Ajouter 1-3 heures pour les exercices et projets
            practice_time = min(3, max(1, reading_time // 2))
            
            total_time = reading_time + practice_time
            
            module_plan = {
                "title": module["title"],
                "reading_time": reading_time,
                "practice_time": practice_time,
                "total_time": total_time
            }
            
            week_plan["modules"].append(module_plan)
            week_plan["estimated_hours"] += total_time
        
        study_plan["weeks"].append(week_plan)
    
    return study_plan

def generate_quiz_questions(module_content: str, num_questions: int = 3) -> List[Dict[str, Any]]:
    """
    Génère des questions de quiz basées sur le contenu d'un module.
    Cette fonction est une simulation simplifiée - dans une implémentation réelle, 
    nous utiliserions un modèle LLM pour générer les questions.
    """
    # Dans une implémentation complète, appeler un LLM pour générer des questions pertinentes
    
    # Exemple statique de retour (pour démonstration)
    sample_questions = [
        {
            "question": "Quelle est l'importance principale de ce module?",
            "type": "text"
        },
        {
            "question": "Quelles sont les applications pratiques des concepts présentés?",
            "type": "text"
        },
        {
            "question": "Comment évalueriez-vous votre compréhension de ce module?",
            "type": "scale",
            "options": ["Faible", "Basique", "Intermédiaire", "Avancé", "Expert"]
        }
    ]
    
    return sample_questions[:min(num_questions, len(sample_questions))]

def format_syllabus_for_print(syllabus: str) -> str:
    """
    Formate le syllabus pour une impression plus lisible
    """
    # Améliorer les titres
    syllabus = re.sub(r'# (.*)', r'# 📚 \1', syllabus)
    syllabus = re.sub(r'## (Module \d+:.*)', r'## 📘 \1', syllabus)
    syllabus = re.sub(r'## (.*)', r'## ✨ \1', syllabus)
    syllabus = re.sub(r'### (.*)', r'### 📋 \1', syllabus)
    
    # Améliorer les listes
    syllabus = re.sub(r'(\* )(.*)', r'• \2', syllabus)
    
    # Ajouter des séparateurs entre les sections
    syllabus = re.sub(r'(## .*)\n', r'\1\n\n---\n\n', syllabus)
    
    return syllabus