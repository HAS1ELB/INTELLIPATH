import os
from typing import List, Dict, Any, Tuple
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("La clé API Groq n'est pas définie. Veuillez la définir dans le fichier .env")

class TeachingAgent:
    def __init__(self, temperature: float = 0.7):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY, 
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=temperature
        )
        
        self.syllabus = ""
        self.topic = ""
        self.conversation_history = []
        self.modules = []
        self.extracted_concepts = {}
        
        self._setup_prompt_templates()
        
    def _setup_prompt_templates(self):
        self.system_prompt = """
        Tu es un professeur expert spécialisé en {topic}, doté d'une vaste expérience pédagogique. Ta mission est d'accompagner l'apprenant dans son parcours d'étude du syllabus fourni, en adaptant ton enseignement à ses besoins spécifiques.
        
        SYLLABUS DU COURS:
        {syllabus_summary}
        
        PROFIL PÉDAGOGIQUE:
        1. PERSONNALISATION: Adapte tes explications au niveau démontré par l'apprenant
        2. SOCRATIQUE: Utilise des questions pour guider la réflexion de l'apprenant
        3. PRATIQUE: Propose systématiquement des exemples concrets et applications réelles
        4. MÉTACOGNITION: Encourage la conscience du processus d'apprentissage
        5. PROGRESSION: Structure tes réponses du simple au complexe
        6. ANALOGIQUE: Utilise des métaphores et analogies pour concepts abstraits
        
        DIRECTIVES SPÉCIFIQUES:
        - Réponds en français avec précision et clarté
        - Base tes réponses sur le syllabus mais enrichis avec ton expertise
        - Pour chaque concept complexe: commence par une explication simple, puis approfondie  
        - Inclus toujours des exemples pratiques et applications concrètes
        - Si une question est hors syllabus, précise-le et oriente vers les ressources appropriées
        - Utilise la notation markdown pour la clarté (code, formules, listes)
        - Termine tes explications longues par une synthèse des points clés
        
        CONTEXTE DE CONVERSATION:
        {conversation_context}
        
        MODULE PERTINENT POUR LA QUESTION ACTUELLE:
        {relevant_module_content}
        
        CONCEPTS CLÉS LIÉS À LA QUESTION:
        {relevant_concepts}
        """
        
        self.user_prompt = "{user_input}"
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", self.user_prompt)
        ])
        
        self.chain = self.prompt_template | self.llm | StrOutputParser()
    
    def load_syllabus(self, syllabus: str, topic: str) -> None:
        """Charge le syllabus et initialise l'agent"""
        self.syllabus = syllabus
        self.topic = topic
        self.conversation_history = []
        
        self._extract_modules_from_syllabus()
        self._extract_concepts_from_syllabus()
    
    def set_modules(self, modules: List[Dict]) -> None:
        """Définit les modules depuis la base de données"""
        self.modules = []
        for module in modules:
            self.modules.append({
                "title": module.get('title', ''),
                "content": module.get('content', ''),
                "index": module.get('order_index', 0) + 1
            })
    
    def set_conversation_history(self, history: List[Dict]) -> None:
        """Définit l'historique de conversation"""
        self.conversation_history = history
    
    def _extract_modules_from_syllabus(self) -> None:
        """Extrait les modules du syllabus"""
        module_pattern = r'#+\s+(Module\s+\d+[.:]\s+.+|Partie\s+\d+[.:]\s+.+|Chapitre\s+\d+[.:]\s+.+|Section\s+\d+[.:]\s+.+)'
        module_titles = re.findall(module_pattern, self.syllabus, re.IGNORECASE)
        
        if not module_titles and "##" in self.syllabus:
            module_pattern = r'##\s+(.+)'
            module_titles = re.findall(module_pattern, self.syllabus)
        
        self.modules = []
        
        for i, title in enumerate(module_titles):
            start_marker = f"## {title}" if not title.startswith("##") else title
            start_index = self.syllabus.find(start_marker)
            
            if start_index == -1:
                continue
                
            if i < len(module_titles) - 1:
                next_title = module_titles[i + 1]
                next_marker = f"## {next_title}" if not next_title.startswith("##") else next_title
                end_index = self.syllabus.find(next_marker, start_index)
                if end_index == -1:
                    end_index = len(self.syllabus)
            else:
                end_index = len(self.syllabus)
            
            content = self.syllabus[start_index:end_index].strip()
            
            self.modules.append({
                "title": title if not title.startswith("##") else title[2:].strip(),
                "content": content,
                "index": i + 1
            })
    
    def _extract_concepts_from_syllabus(self) -> None:
        """Extrait les concepts clés du syllabus"""
        self.extracted_concepts = {}
        
        # Extraction des concepts à différents niveaux
        concept_patterns = [
            (r'(?:Concepts clés|Points essentiels|Notions importantes)[^\n]*\n(?:\s*[\*\-]\s*([^\n]+)\n)+', "global"),
            (r'Module\s+\d+[^\n]*\n(?:[^\n]*\n)*?(?:Concepts clés|Points essentiels)[^\n]*\n(?:\s*[\*\-]\s*([^\n]+)\n)+', "module")
        ]
        
        for pattern, scope in concept_patterns:
            matches = re.finditer(pattern, self.syllabus, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                match_text = match.group(0)
                concept_lines = re.findall(r'[\*\-]\s*([^\n]+)', match_text)
                
                if scope == "global":
                    if "global_concepts" not in self.extracted_concepts:
                        self.extracted_concepts["global_concepts"] = []
                    self.extracted_concepts["global_concepts"].extend(concept_lines)
                elif scope == "module":
                    module_title_match = re.search(r'(Module\s+\d+[^\n]*)', match_text)
                    if module_title_match:
                        module_title = module_title_match.group(1)
                        if module_title not in self.extracted_concepts:
                            self.extracted_concepts[module_title] = []
                        self.extracted_concepts[module_title].extend(concept_lines)
        
        # Extraction des termes en gras et italique comme concepts potentiels
        emphasis_concepts = re.findall(r'\*\*([^*]+)\*\*|\*([^*]+)\*', self.syllabus)
        unique_emphasis = set()
        
        for bold, italic in emphasis_concepts:
            if bold and len(bold.split()) <= 5:
                unique_emphasis.add(bold)
            if italic and len(italic.split()) <= 5:
                unique_emphasis.add(italic)
        
        if "emphasis_concepts" not in self.extracted_concepts:
            self.extracted_concepts["emphasis_concepts"] = []
        self.extracted_concepts["emphasis_concepts"] = list(unique_emphasis)
    
    def _find_relevant_module(self, query: str) -> Dict[str, Any]:
        """Trouve le module le plus pertinent pour une requête"""
        if not self.modules:
            return {"title": "", "content": "", "relevance": 0}
        
        best_match = {"title": "", "content": "", "relevance": 0}
        
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        
        for module in self.modules:
            module_text = module["title"].lower() + " " + module["content"].lower()
            module_words = set(re.findall(r'\b\w{3,}\b', module_text))
            
            common_words = query_words & module_words
            relevance = len(common_words) / max(len(query_words), 1)
            
            if relevance > best_match["relevance"]:
                best_match = {
                    "title": module["title"],
                    "content": module["content"],
                    "relevance": relevance
                }
        
        return best_match
    
    def _find_relevant_concepts(self, query: str) -> List[str]:
        """Trouve les concepts pertinents pour une requête"""
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        relevant_concepts = []
        
        # Check global concepts
        if "global_concepts" in self.extracted_concepts:
            for concept in self.extracted_concepts["global_concepts"]:
                concept_words = set(re.findall(r'\b\w{3,}\b', concept.lower()))
                common_words = query_words & concept_words
                if common_words:
                    relevant_concepts.append(concept)
        
        # Check module-specific concepts
        for module_key, concepts in self.extracted_concepts.items():
            if module_key != "global_concepts" and module_key != "emphasis_concepts":
                for concept in concepts:
                    concept_words = set(re.findall(r'\b\w{3,}\b', concept.lower()))
                    common_words = query_words & concept_words
                    if common_words and concept not in relevant_concepts:
                        relevant_concepts.append(concept)
        
        # Check emphasized concepts
        if "emphasis_concepts" in self.extracted_concepts:
            for concept in self.extracted_concepts["emphasis_concepts"]:
                concept_words = set(re.findall(r'\b\w{3,}\b', concept.lower()))
                common_words = query_words & concept_words
                if common_words and concept not in relevant_concepts:
                    relevant_concepts.append(concept)
        
        return relevant_concepts[:7]  # Limiter à 7 concepts les plus pertinents
    
    def _analyze_question(self, query: str) -> str:
        """Analyse le type de question posée"""
        question_types = [
            (r'\b(c\'est quoi|qu\'est[\s-]ce que|définition|signifie)\b', "définition"),
            (r'\b(comment|méthode|procédure|étape|manière)\b', "méthode"),
            (r'\b(différence|comparaison|versus|vs|distinguer|entre)\b', "comparaison"),
            (r'\b(exemple|illustration|cas|pratique|concret|application)\b', "exemple"),
            (r'\b(pourquoi|raison|cause|explication)\b', "explication"),
            (r'\b(avantage|inconvénient|bénéfice|limite|problème)\b', "évaluation"),
            (r'\b(niveau|complexité|difficulté|comprendre|confusion)\b', "difficulté")
        ]
        
        context = []
        for pattern, q_type in question_types:
            if re.search(pattern, query.lower()):
                context.append(f"L'apprenant pose une question de type '{q_type}'.")
        
        # Analyse du niveau de complexité basée sur la longueur et le vocabulaire
        words = re.findall(r'\b\w+\b', query.lower())
        advanced_terms = ['avancé', 'complexe', 'approfondi', 'détaillé', 'spécifique']
        
        if len(query.split()) > 20 or any(term in query.lower() for term in advanced_terms):
            context.append("La question semble demander une réponse approfondie et technique.")
        else:
            context.append("La question semble demander une explication claire et accessible.")
            
        return " ".join(context)
    
    def _prepare_conversation_context(self, query: str) -> str:
        """Prépare le contexte de conversation"""
        # Limiter l'historique aux 5 derniers échanges pour économiser des tokens
        recent_history = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
        
        formatted_history = ""
        for message in recent_history:
            role = "Apprenant" if message["role"] == "user" else "Professeur"
            formatted_history += f"{role}: {message['content']}\n\n"
        
        # Analyse de la question actuelle
        question_analysis = self._analyze_question(query)
        
        return f"Analyse de la question: {question_analysis}\n\nHistorique récent:\n{formatted_history}"
    
    def _get_syllabus_summary(self) -> str:
        """Retourne un résumé du syllabus"""
        if not self.syllabus:
            return "Aucun syllabus disponible."
            
        # Extraire les titres des modules
        modules_titles = [f"- {module['title']}" for module in self.modules]
        modules_list = "\n".join(modules_titles)
        
        # Extraire l'introduction et les objectifs si présents
        intro_match = re.search(r'(?:## |#)Introduction\s+([^\n#]+(?:\n[^\n#]+)*)', self.syllabus, re.IGNORECASE)
        intro = intro_match.group(1).strip() if intro_match else ""
        
        objectives_match = re.search(r'(?:## |#)Objectifs[^\n]*\s+([^\n#]+(?:\n[^\n#]+)*)', self.syllabus, re.IGNORECASE)
        objectives = objectives_match.group(1).strip() if objectives_match else ""
        
        summary = f"""SUJET: {self.topic}\n\nSTRUCTURE DU COURS:\n{modules_list}\n\n"""
        if intro:
            summary += f"INTRODUCTION:\n{intro}\n\n"
            
        if objectives:
            summary += f"OBJECTIFS:\n{objectives}\n\n"
            
        return summary
    
    def respond(self, user_input: str) -> str:
        """Génère une réponse à la question de l'utilisateur"""
        if not self.syllabus or not self.topic:
            return "Veuillez d'abord initialiser l'agent avec un syllabus et un sujet."
        
        # Trouver le module le plus pertinent pour la question
        relevant_module = self._find_relevant_module(user_input)
        module_content = relevant_module["content"] if relevant_module["relevance"] > 0.2 else ""
        
        # Trouver les concepts pertinents
        relevant_concepts = self._find_relevant_concepts(user_input)
        concepts_text = "\n".join([f"- {concept}" for concept in relevant_concepts])
        
        # Préparer le contexte de conversation
        conversation_context = self._prepare_conversation_context(user_input)
        
        # Préparer le résumé du syllabus
        syllabus_summary = self._get_syllabus_summary()
        
        # Générer la réponse
        response = self.chain.invoke({
            "user_input": user_input,
            "syllabus_summary": syllabus_summary,
            "topic": self.topic,
            "conversation_context": conversation_context,
            "relevant_module_content": module_content[:1500] if len(module_content) > 1500 else module_content,
            "relevant_concepts": concepts_text if concepts_text else "Aucun concept clé spécifique identifié pour cette question."
        })
        
        # Mise à jour de l'historique de conversation
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response