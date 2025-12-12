import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega a chave
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERRO: Chave não encontrada no .env")
else:
    genai.configure(api_key=api_key)

    print("--- MODELOS DISPONÍVEIS PARA SUA CHAVE ---")
    try:
        # Lista todos os modelos disponíveis
        for m in genai.list_models():
            # Filtra apenas os que servem para gerar texto (chat)
            if 'generateContent' in m.supported_generation_methods:
                print(f"Nome: {m.name}")
    except Exception as e:
        print(f"Erro ao conectar: {e}")