/**
 * NutriTrack 3D - AI Fitness Assistant Chat Interface
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('ai-chat-form');
    const chatInput = document.getElementById('ai-chat-input');
    const chatMessages = document.getElementById('ai-chat-messages');
    const promptPills = document.querySelectorAll('.prompt-pill');

    if (!chatForm || !chatInput || !chatMessages) return;

    function appendMessage(sender, text, isMarkdown = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-msg ${sender === 'user' ? 'msg-user' : 'msg-ai'}`;

        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        avatar.innerHTML = sender === 'user'
            ? '<i class="fa-solid fa-user"></i>'
            : '<i class="fa-solid fa-microchip text-neon"></i>';

        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble glass-card';

        if (isMarkdown) {
            // Simple markdown parser for headers, bold, bullets
            let formatted = text
                .replace(/^### (.*$)/gim, '<h4 class="text-neon mb-2">$1</h4>')
                .replace(/\*\*(.*?)\*\*/gim, '<strong class="text-white">$1</strong>')
                .replace(/^\* (.*$)/gim, '<li class="ml-3">$1</li>')
                .replace(/^- (.*$)/gim, '<li class="ml-3">$1</li>')
                .replace(/\n\n/g, '<br><br>');
            bubble.innerHTML = formatted;
        } else {
            bubble.textContent = text;
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'chat-msg msg-ai typing-indicator';
        indicator.id = 'typing-indicator-box';
        indicator.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid fa-microchip text-neon"></i></div>
            <div class="msg-bubble glass-card">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const ind = document.getElementById('typing-indicator-box');
        if (ind) ind.remove();
    }

    function sendMessage(text) {
        if (!text.trim()) return;
        appendMessage('user', text);
        chatInput.value = '';
        showTypingIndicator();

        fetch('/api/assistant/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => {
            removeTypingIndicator();
            appendMessage('ai', data.reply, true);
        })
        .catch(err => {
            removeTypingIndicator();
            appendMessage('ai', 'An error occurred while connecting to NutriTrack AI. Please try again.');
        });
    }

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage(chatInput.value);
    });

    // Suggestion pills
    promptPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const prompt = pill.dataset.prompt || pill.textContent.trim();
            sendMessage(prompt);
        });
    });
});
