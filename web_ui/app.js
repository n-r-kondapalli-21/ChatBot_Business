// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// DOM Elements
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const faqList = document.getElementById('faqList');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkConnection();
    loadFAQs();

    // Allow Enter key to send
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuestion();
        }
    });
});

// Check API connection
async function checkConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            statusIndicator.className = 'status-indicator connected';
            statusText.textContent = `Connected - ${data.faq_count} FAQs loaded`;
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        statusIndicator.className = 'status-indicator disconnected';
        statusText.textContent = 'Disconnected - Please start the API server';
    }
}

// Load FAQs
async function loadFAQs() {
    try {
        const response = await fetch(`${API_BASE_URL}/faqs`);
        if (!response.ok) throw new Error('Failed to load FAQs');

        const data = await response.json();
        displayFAQs(data.data);
    } catch (error) {
        faqList.innerHTML = `<div class="error">Failed to load FAQs: ${error.message}</div>`;
    }
}

// Display FAQs
function displayFAQs(faqs) {
    if (!faqs || faqs.length === 0) {
        faqList.innerHTML = '<p>No FAQs available</p>';
        return;
    }

    faqList.innerHTML = faqs.map(faq => `
        <div class="faq-item" onclick="askFAQ('${faq.question.replace(/'/g, "\\'")}')">
            <div class="question">${escapeHtml(faq.question)}</div>
            <div class="category">${escapeHtml(faq.category)}</div>
        </div>
    `).join('');
}

// Send question to API
async function sendQuestion() {
    const question = questionInput.value.trim();

    if (!question) {
        alert('Please enter a question');
        return;
    }

    // Disable input while processing
    questionInput.disabled = true;
    sendButton.disabled = true;

    // Add user message to chat
    addMessage(question, 'user');
    questionInput.value = '';

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question }),
        });

        if (!response.ok) throw new Error('Failed to get response');

        const data = await response.json();
        addMessage(data.answer, 'bot', data.matched ? data.similarity_score : null);
    } catch (error) {
        addMessage(`Error: ${error.message}`, 'bot');
    } finally {
        questionInput.disabled = false;
        sendButton.disabled = false;
        questionInput.focus();
    }
}

// Add message to chat
function addMessage(content, type, similarity = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const paragraph = document.createElement('p');
    paragraph.textContent = content;
    contentDiv.appendChild(paragraph);

    if (similarity !== null) {
        const similaritySpan = document.createElement('span');
        similaritySpan.className = 'similarity';
        similaritySpan.textContent = `Similarity: ${(similarity * 100).toFixed(1)}%`;
        contentDiv.appendChild(similaritySpan);
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Ask a FAQ question (clicked from FAQ list)
function askFAQ(question) {
    questionInput.value = question;
    sendQuestion();
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
