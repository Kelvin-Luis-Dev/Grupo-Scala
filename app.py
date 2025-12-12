import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime # <--- Importante para a data funcionar

# 1. Load environment variables
load_dotenv()

# 2. Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"Erro ao configurar API: {e}")
else:
    print("⚠️ AVISO: Chave GEMINI_API_KEY não encontrada no arquivo .env")

app = Flask(__name__)

# --- PROJECT DATA ---
PROJECTS = [
    {
        "id": 1,
        "title": "Portal Corporativo",
        "subtitle": "Soluções Contábeis & B2B",
        "category": "Back-end & Business",
        "description": "Desenvolvimento de um portal completo para escritório de contabilidade, permitindo gestão de documentos e comunicação direta com clientes.",
        "challenge": "O cliente precisava de uma forma segura de trocar documentos sensíveis e reduzir o tempo de atendimento no WhatsApp. O sistema precisava ser intuitivo para usuários leigos.",
        "tags": ["Python", "Flask", "PostgreSQL", "Jinja2"],
        "img": "project1.png",
        "github_link": "https://github.com/seu-usuario/projeto1",
        "demo_link": "https://site-cliente.com",
        "color": "#e63946"
    },
    {
        "id": 2,
        "title": "Landing Page Institucional",
        "subtitle": "Design de UI e Alta Performance",
        "category": "Front-end & Design",
        "description": "Página de aterrissagem focada em conversão, com animações leves e carregamento instantâneo para campanhas de marketing.",
        "challenge": "Criar uma experiência visual impactante sem comprometer a velocidade de carregamento (Core Web Vitals) para melhorar o ranqueamento no Google.",
        "tags": ["HTML5", "CSS3", "JavaScript", "Animation"],
        "img": "project2.png",
        "github_link": "https://github.com/seu-usuario/projeto2",
        "demo_link": "https://usevenere.com.br/blog/",
        "color": "#4cc9f0"
    },
    {
        "id": 3,
        "title": "E-commerce Store",
        "subtitle": "Plataforma de Vendas Fullstack",
        "category": "Fullstack App",
        "description": "Loja virtual completa com carrinho de compras, integração de pagamentos e painel administrativo para gestão de estoque.",
        "challenge": "Gerenciar o estado do carrinho de compras em tempo real e garantir a segurança nas transações e dados dos usuários.",
        "tags": ["React", "Django", "Rest API", "Stripe"],
        "img": "project3.png",
        "github_link": "https://github.com/seu-usuario/projeto3",
        "demo_link": None,
        "color": "#FF5E00"
    },
]


# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html', projects=PROJECTS)


@app.route('/project/<int:pid>')
def project(pid):
    proj = next((p for p in PROJECTS if p['id'] == pid), None)
    if not proj:
        return "Projeto não encontrado", 404
    return render_template('project.html', project=proj)


# --- ROTA: API DO GEMINI (COM DATA E SISTEMA ANTI-FALHA) ---
@app.route('/api/chat', methods=['POST'])
def chat_gemini():
    if not API_KEY:
        return jsonify({'error': 'Configuração de API pendente no servidor.'}), 503

    data = request.json
    user_message = data.get('message', '')

    # Modelo escolhido no site (Padrão agora é o 2.5 que sabemos que funciona bem pra você)
    chosen_model = data.get('model', 'gemini-2.5-flash')

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'}), 400

    # --- INJEÇÃO DE DATA E HORA ---
    # 1. Pega a hora atual do servidor
    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # 2. Cria o prompt "secreto" com a instrução de sistema
    prompt_completo = f"""
    Instrução de Sistema: Você é uma IA assistente no portfólio de um Desenvolvedor Fullstack.
    Data e hora atual: {data_atual}.
    Se perguntarem a data ou hora, use a informação acima. Seja breve e profissional.

    Mensagem do usuário: {user_message}
    """
    # ------------------------------

    try:
        # TENTATIVA 1: Usa o modelo escolhido com o prompt de data
        model = genai.GenerativeModel(chosen_model)
        response = model.generate_content(prompt_completo)
        return jsonify({'response': response.text})

    except Exception as e:
        error_msg = str(e)

        # SE O ERRO FOR COTA (429) OU MODELO NÃO ENCONTRADO (404)
        if "429" in error_msg or "404" in error_msg:
            print(f"⚠️ Erro no modelo {chosen_model} ({error_msg}). Tentando backup...")

            # TENTATIVA 2: Backup Automático (Gemini 1.5 Flash)
            try:
                backup_model = genai.GenerativeModel('gemini-1.5-flash')
                # Também enviamos a data no backup
                response = backup_model.generate_content(prompt_completo)

                # Avisa no final da resposta que foi usado o backup
                aviso = f"\n\n*(Nota: O {chosen_model} estava ocupado, respondi usando o Gemini 1.5 Flash)*"
                return jsonify({'response': response.text + aviso})

            except Exception as e2:
                return jsonify({'error': 'Todos os modelos estão ocupados. Tente daqui 5 minutos.'}), 429

        # Outros erros
        return jsonify({'error': f'Erro interno: {error_msg}'}), 500


# --- SERVER STARTUP ---
if __name__ == '__main__':
    print("🚀 Servidor iniciando em http://127.0.0.1:5001")
    app.run(debug=True, port=5001, use_reloader=False)