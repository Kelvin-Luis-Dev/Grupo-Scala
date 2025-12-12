/* ==========================================================================
   1. LÓGICA DE ANIMAÇÃO (SCROLL REVEAL)
   Faz os elementos aparecerem suavemente ao rolar a página
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
    const reveals = document.querySelectorAll('.reveal, .reveal-left');

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        const elementVisible = 100; // Distância do topo para ativar a animação

        reveals.forEach((reveal) => {
            const elementTop = reveal.getBoundingClientRect().top;

            if (elementTop < windowHeight - elementVisible) {
                reveal.classList.add('active');
            }
            // Se quiser que a animação repita ao subir a tela, descomente a linha abaixo:
            // else { reveal.classList.remove('active'); }
        });
    };

    window.addEventListener('scroll', revealOnScroll);
    // Chama uma vez ao carregar para mostrar o que já está visível
    revealOnScroll();
});

/* ==========================================================================
   2. NAVEGAÇÃO DOS PROJETOS
   Redireciona para a página de detalhes do projeto
   ========================================================================== */
function openProject(id) {
    window.location.href = `/project/${id}`;
}

/* ==========================================================================
   3. MODAL DE IA E CHAT (GEMINI)
   Controla a abertura do modal e o envio de mensagens para o Python
   ========================================================================== */

// Abre o modal
function openAiModal(event) {
    // Impede que o clique no botão ative outros eventos (como o accordion)
    if(event) event.stopPropagation();

    const modal = document.getElementById('ai-modal');
    modal.classList.add('active');

    // Foca no campo de input automaticamente
    setTimeout(() => document.getElementById('user-input').focus(), 100);
}

// Fecha o modal
function closeAiModal() {
    document.getElementById('ai-modal').classList.remove('active');
}

// Fecha o modal se clicar na parte escura (fora da janela)
const modalElement = document.getElementById('ai-modal');
if (modalElement) {
    modalElement.addEventListener('click', function(e) {
        if (e.target === this) closeAiModal();
    });
}

// Envia mensagem ao apertar Enter
function handleEnter(e) {
    if (e.key === 'Enter') sendMessage();
}
async function sendMessage() {
    const input = document.getElementById('user-input');
    // PEGA O MODELO ESCOLHIDO NO MENU
    const modelSelect = document.getElementById('model-selector');
    const selectedModel = modelSelect ? modelSelect.value : 'gemini-2.0-flash';

    const message = input.value.trim();
    const chatBox = document.getElementById('chat-box');

    if (!message) return;

    // 1. Mostra mensagem do usuário
    chatBox.innerHTML += `<div class="ai-message ai-message-user">${message}</div>`;
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // 2. Mostra "Digitando..."
    const loadingId = 'loading-' + Date.now();
    chatBox.innerHTML += `<div id="${loadingId}" class="ai-message ai-message-bot">Conectando ao ${selectedModel}...</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // 3. Envia para o Flask COM O MODELO ESCOLHIDO
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                model: selectedModel // <--- AQUI ESTÁ O SEGREDO
            })
        });

        const data = await response.json();

        // Remove "Digitando..."
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();

        if (data.error) {
            chatBox.innerHTML += `<div class="ai-message ai-message-bot" style="color: #ff5555">Erro: ${data.error}</div>`;
        } else {
            // Formata a resposta
            let formattedText = data.response
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');

            chatBox.innerHTML += `<div class="ai-message ai-message-bot">${formattedText}</div>`;
        }
    } catch (err) {
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();
        chatBox.innerHTML += `<div class="ai-message ai-message-bot" style="color: #ff5555">Erro de conexão.</div>`;
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}
/* --- LÓGICA DO SLIDER DE PROJETOS --- */
document.addEventListener('DOMContentLoaded', () => {
    const sliderContainer = document.querySelector('.slider-container');
    const prevBtn = document.querySelector('.nav-btn.prev');
    const nextBtn = document.querySelector('.nav-btn.next');

    // Distância para rolar (largura do card + gap)
    // 320px do card + 25px do gap = 345px aprox
    const scrollAmount = 350;

    if (sliderContainer && prevBtn && nextBtn) {
        nextBtn.addEventListener('click', () => {
            sliderContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        });

        prevBtn.addEventListener('click', () => {
            sliderContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        });
    }
});