/**
 * Arquivo JavaScript principal para o Assistente IA Corporativo
 */

// Função para formatar texto com markdown simples
function formatMarkdown(text) {
    if (!text) return '';
    
    // Substituir quebras de linha por <br>
    let formatted = text.replace(/\n/g, '<br>');
    
    // Formatar negrito: **texto** ou __texto__
    formatted = formatted.replace(/\*\*(.*?)\*\*|__(.*?)__/g, '<strong>$1$2</strong>');
    
    // Formatar itálico: *texto* ou _texto_
    formatted = formatted.replace(/\*(.*?)\*|_(.*?)_/g, '<em>$1$2</em>');
    
    // Formatar código inline: `código`
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Formatar listas não ordenadas
    formatted = formatted.replace(/^\s*[-*+]\s+(.*?)(?=<br>|$)/gm, '<li>$1</li>');
    formatted = formatted.replace(/<li>(.*?)(?=<li>|$)/gs, '<ul><li>$1</ul>');
    
    // Formatar listas ordenadas
    formatted = formatted.replace(/^\s*\d+\.\s+(.*?)(?=<br>|$)/gm, '<li>$1</li>');
    formatted = formatted.replace(/<li>(.*?)(?=<li>|$)/gs, '<ol><li>$1</ol>');
    
    return formatted;
}

// Função para escapar HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Função para adicionar mensagem ao chat (versão global)
function addMessageToChat(content, isUser = false, chatMessagesSelector = '#chat-messages') {
    const chatMessages = $(chatMessagesSelector);
    if (!chatMessages.length) return;
    
    const messageClass = isUser ? 'user-message' : 'assistant-message';
    const escapedContent = isUser ? escapeHtml(content) : formatMarkdown(content);
    
    const messageHtml = `
        <div class="message ${messageClass}">
            <div class="message-content">
                <p>${escapedContent}</p>
            </div>
        </div>
    `;
    
    chatMessages.append(messageHtml);
    chatMessages.scrollTop(chatMessages[0].scrollHeight);
}

// Função para mostrar notificações
function showNotification(message, type = 'info', duration = 3000) {
    // Verificar se o container de notificações existe, senão criar
    let notifContainer = $('#notification-container');
    if (!notifContainer.length) {
        $('body').append('<div id="notification-container" style="position: fixed; top: 20px; right: 20px; z-index: 9999;"></div>');
        notifContainer = $('#notification-container');
    }
    
    // Criar notificação
    const notifId = 'notif-' + Date.now();
    const notifHtml = `
        <div id="${notifId}" class="alert alert-${type} alert-dismissible fade show" role="alert" style="min-width: 300px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Adicionar ao container
    notifContainer.append(notifHtml);
    
    // Auto-remover após duração
    setTimeout(() => {
        $(`#${notifId}`).alert('close');
    }, duration);
}

// Função para copiar texto para a área de transferência
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = 0;
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        const successful = document.execCommand('copy');
        document.body.removeChild(textarea);
        return successful;
    } catch (err) {
        document.body.removeChild(textarea);
        return false;
    }
}

// Inicialização quando o documento estiver pronto
$(document).ready(function() {
    // Adicionar botões de copiar para blocos de código
    $('pre code').each(function() {
        const codeBlock = $(this);
        const copyBtn = $('<button class="btn btn-sm btn-outline-secondary copy-btn">Copiar</button>');
        copyBtn.css({
            'position': 'absolute',
            'top': '5px',
            'right': '5px',
            'opacity': '0.7'
        });
        
        // Adicionar botão ao bloco de código
        codeBlock.parent().css('position', 'relative').append(copyBtn);
        
        // Manipulador de clique
        copyBtn.on('click', function() {
            const code = codeBlock.text();
            if (copyToClipboard(code)) {
                showNotification('Código copiado para a área de transferência!', 'success');
                copyBtn.text('Copiado!').removeClass('btn-outline-secondary').addClass('btn-success');
                setTimeout(() => {
                    copyBtn.text('Copiar').removeClass('btn-success').addClass('btn-outline-secondary');
                }, 2000);
            } else {
                showNotification('Falha ao copiar o código', 'danger');
            }
        });
    });
    
    // Adicionar tooltips para todos os elementos com data-bs-toggle="tooltip"
    $('[data-bs-toggle="tooltip"]').tooltip();
});