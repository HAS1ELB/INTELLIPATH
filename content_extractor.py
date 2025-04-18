# Ajout dans un nouveau fichier: content_extractor.py
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from langchain_ollama import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ContentExtractor:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = OllamaLLM(model="llama3", temperature=0.1)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    def extract_from_url(self, url):
        """Extrait le contenu d'une URL et l'ajoute à la base vectorielle"""
        try:
            # Détection du type de contenu
            parsed_url = urlparse(url)
            
            # YouTube
            if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
                content = self._extract_youtube(url)
            # PDF
            elif url.endswith('.pdf'):
                content = self._extract_pdf(url)
            # Page web
            else:
                content = self._extract_webpage(url)
            
            # Analyse et ajout à la base vectorielle
            if content:
                # Analyse du contenu avec LLM
                analysis_prompt = f"""
                Analyse le contenu éducatif suivant et extrait-en les concepts clés, les définitions, 
                et les informations importantes. Formatte ta réponse de manière structurée.
                
                CONTENU:
                {content[:5000]}  # Limiter la taille pour éviter les problèmes
                
                ANALYSE STRUCTURÉE:
                """
                
                analysis = self.llm.invoke(analysis_prompt)
                
                # Préparation pour la base vectorielle
                texts = self.text_splitter.split_text(content)
                self.vector_store.add_texts(texts)
                
                return {
                    "source": url,
                    "content_length": len(content),
                    "analysis": analysis,
                    "chunks_added": len(texts)
                }
            else:
                return {"error": "Contenu vide ou inaccessible"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_youtube(self, url):
        """Extrait la transcription d'une vidéo YouTube"""
        # Obtenir l'ID de la vidéo
        if 'youtube.com' in url:
            query = parse_qs(urlparse(url).query)
            video_id = query.get('v', [None])[0]
        elif 'youtu.be' in url:
            video_id = urlparse(url).path[1:]
        else:
            return None
        
        if not video_id:
            return None
        
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = ' '.join([item['text'] for item in transcript_list])
            
            return transcript
        except Exception as e:
            print(f"Erreur lors de l'extraction YouTube: {e}")
            return None
    
    def _extract_pdf(self, url):
        """Extrait le texte d'un PDF en ligne"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Lire le PDF
                pdf_file = io.BytesIO(response.content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # Extraire le texte de chaque page
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
                
                return text
            else:
                return None
        except Exception as e:
            print(f"Erreur lors de l'extraction PDF: {e}")
            return None
    
    def _extract_webpage(self, url):
        """Extrait le contenu d'une page web"""
        try:
            # Simuler un navigateur pour éviter les blocages
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Supprimer les balises de script et de style
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Extraire le texte principal
                main_content = soup.find('main') or soup.find('article') or soup.find('body')
                
                if main_content:
                    text = main_content.get_text(separator='\n')
                else:
                    text = soup.get_text(separator='\n')
                
                # Nettoyer le texte
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
            else:
                return None
        except Exception as e:
            print(f"Erreur lors de l'extraction de la page web: {e}")
            return None