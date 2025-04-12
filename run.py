import os
import time

import gradio as gr
from generating_syllabus import generate_syllabus  # Assurez-vous que ce fichier a été mis à jour pour Llama 3
from teaching_agent import teaching_agent  # Assurez-vous que ce fichier a été mis à jour pour Llama 3

# Pour Llama 3 via Ollama, nous n'avons pas besoin de clé API comme avec OpenAI
# Mais vérifions si le fichier .env existe pour d'autres configurations éventuelles
try:
    with open(".env", "r") as f:
        env_file = f.readlines()
    envs_dict = {
        key.strip("'"): value.strip("\n")
        for key, value in [(i.split("=")) for i in env_file]
    }
    # Vous pourriez stocker d'autres variables d'environnement ici si nécessaire
except FileNotFoundError:
    # Si le fichier .env n'existe pas, continuez sans lui
    envs_dict = {}

with gr.Blocks() as demo:
    gr.Markdown("# Your AI Instructor")
    gr.Markdown("#### Powered by Llama 3")  # Mise à jour pour indiquer l'utilisation de Llama 3
    
    with gr.Tab("Input Your Information"):
        def perform_task(input_text):
            # Perform the desired task based on the user input
            task = (
                "Generate a course syllabus to teach the topic: " + input_text
            )
            syllabus = generate_syllabus(input_text, task)
            teaching_agent.seed_agent(syllabus, task)
            return syllabus

        text_input = gr.Textbox(
            label="State the name of topic you want to learn:"
        )
        text_output = gr.Textbox(label="Your syllabus will be showed here:")
        text_button = gr.Button("Build the Bot!!!")
        text_button.click(perform_task, text_input, text_output)
    
    with gr.Tab("AI Instructor"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="What do you concern about?")
        clear = gr.Button("Clear")

        def user(user_message, history):
            teaching_agent.human_step(user_message)
            return "", history + [[user_message, None]]

        def bot(history):
            bot_message = teaching_agent.instructor_step()
            history[-1][1] = ""
            # Ralentissement de l'affichage pour une expérience plus naturelle
            # Vous pouvez ajuster le délai selon les performances de Llama 3
            for character in bot_message:
                history[-1][1] += character
                time.sleep(0.05)
                yield history

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)

# Ajout d'un message d'information sur le terminal
print("Starting Gradio interface with Llama 3 model...")
print("Note: First response may be slower as the model is loaded")

demo.queue().launch(debug=True, share=True)
