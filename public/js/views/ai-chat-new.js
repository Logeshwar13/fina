import { apiFetch } from '../utils.js';
import { authState } from '../auth.js';

export default function() {
    const html = `
        <div class="page-header ai-chat-header">
            <div class="header-content">
                <div class="header-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        <circle cx="9" cy="10" r="1" fill="currentColor"></circle>
                        <circle cx="12" cy="10" r="1" fill="currentColor"></circle>
                        <circle cx="15" cy="10" r="1" fill="currentColor"></circle>
                    </svg>
                </div>
                <div>
                    <h1 class="page-title">AI Financial Advisor</h1>
                    <p class="page-subtitle">Chat with our multi-agent AI system powered by RAG</p>
                </div>
            </div>
            <div class="page-actions">
                <button id="clear-history-btn" class="btn btn-secondary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="1 4 1 10 7 10"></polyline>
                        <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
                    </svg>
                    Clear History
                </button>
            </div>
        </div>

        <div class="ai-chat-container">
            <!-- Main Content Area -->
            <div class="chat-main-area">
                <!-- Chat Panel -->
                <div class="chat-panel">
                <div class="chat-messages" id="chat-messages">
                    <div class="welcome-message">
                        <div class="welcome-icon">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </div>
                        <h3>Welcome to AI Financial Advisor!</h3>
                        <p>I'm powered by a multi-agent system with RAG capabilities. Ask me anything about:</p>
                        <div class="suggestion-chips">
                            <button class="chip" data-query="What is my budget status?">Budget Status</button>
                            <button class="chip" data-query="Analyze my spending patterns">Spending Analysis</button>
                            <button class="chip" data-query="What is my risk score?">Risk Score</button>
                            <button class="chip" data-query="Do I have any fraudulent transactions?">Fraud Check</button>
                            <button class="chip" data-query="What insurance do I need?">Insurance Needs</button>
                            <button class="chip" data-query="Should I invest more?">Investment Advice</button>
                        </div>
                    </div>
                </div>

                <div class="chat-input-container">
                    <div class="chat-input-wrapper">
                        <textarea 
                            id="chat-input" 
                            placeholder="Ask about your finances, budgets, risks, investments, or insurance..."
                            rows="1"
                        ></textarea>
                        <button id="send-btn" class="send-btn">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Stats Panel -->
            <div class="stats-panel">
                <h3 class="panel-title">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="20" x2="12" y2="10"></line>
                        <line x1="18" y1="20" x2="18" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="16"></line>
                    </svg>
                    System Stats
                </h3>
                <div id="system-stats" class="stats-list">
                    <div class="stat-item">
                        <span class="stat-label">Total Queries:</span>
                        <span class="stat-value" id="total-queries">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Avg Response Time:</span>
                        <span class="stat-value" id="avg-response-time">-</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Success Rate:</span>
                        <span class="stat-value" id="success-rate">-</span>
                    </div>
                </div>

                <div class="guardrails-info">
                    <h4>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        </svg>
                        Guardrails Active
                    </h4>
                    <ul>
                        <li>Input validation</li>
                        <li>Output sanitization</li>
                        <li>Sensitive data masking</li>
                        <li>XSS/SQL injection prevention</li>
                    </ul>
                </div>
            </div>
            </div>
        </div>

        <style>
            /* AI Chat Page Specific Styles */
            .ai-chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                border-radius: 16px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
            }

            .ai-chat-header .header-content {
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .ai-chat-header .header-icon {
                width: 56px;
                height: 56px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
            }

            .ai-chat-header .page-title {
                color: white;
                margin: 0;
            }

            .ai-chat-header .page-subtitle {
                color: rgba(255, 255, 255, 0.9);
                margin: 0.25rem 0 0 0;
            }

            .ai-chat-header .btn-secondary {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(10px);
            }

            .ai-chat-header .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }

            .ai-chat-container {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                height: calc(100vh - 220px);
                min-height: 700px;
            }

            .chat-main-area {
                display: grid;
                grid-template-columns: 1fr 320px;
                gap: 1.5rem;
                flex: 1;
                min-height: 0;
            }

            @media (max-width: 1200px) {
                .chat-main-area {
                    grid-template-columns: 1fr;
                }
                .stats-panel {
                    display: none;
                }
            }

            .stats-panel {
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                overflow-y: auto;
                border: 1px solid var(--border-color);
            }

            .panel-title {
                font-size: 0.875rem;
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: 1.25rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding-bottom: 0.75rem;
                border-bottom: 2px solid var(--border-color);
            }

            .agent-list {
                display: flex;
                flex-direction: column;
                gap: 0.875rem;
            }

            .agent-card {
                padding: 1rem;
                border-radius: 12px;
                background: var(--bg-secondary);
                border: 2px solid var(--border-color);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
            }

            .agent-card:hover {
                border-color: var(--primary);
                box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
                transform: translateY(-2px);
            }

            .agent-card.active {
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border-color: var(--primary);
                box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
            }

            .agent-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 0.5rem;
            }

            .agent-name {
                font-weight: 600;
                font-size: 0.875rem;
                color: var(--text-primary);
            }

            .agent-status {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: var(--success);
                box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% {
                    opacity: 1;
                }
                50% {
                    opacity: 0.5;
                }
            }

            .agent-role {
                font-size: 0.75rem;
                color: var(--text-secondary);
            }

            .agent-info-box, .rag-info-box, .guardrails-info {
                margin-top: 1.5rem;
                padding: 1.25rem;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
                border-radius: 12px;
                border-left: 4px solid var(--primary);
            }

            .agent-info-box h4, .rag-info-box h4, .guardrails-info h4 {
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 0.75rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: var(--primary);
            }

            .agent-info-box p, .rag-info-box p {
                font-size: 0.75rem;
                color: var(--text-secondary);
                margin-bottom: 0.75rem;
                line-height: 1.5;
            }

            .agent-info-box ul, .guardrails-info ul {
                font-size: 0.75rem;
                color: var(--text-secondary);
                padding-left: 1.25rem;
                margin: 0;
                line-height: 1.6;
            }

            .agent-info-box li, .guardrails-info li {
                margin-bottom: 0.5rem;
            }

            .message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom-right-radius: 4px;
            }

            .chat-panel {
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                border: 1px solid var(--border-color);
                min-height: 500px;
            }

            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 2rem;
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                background: linear-gradient(to bottom, #fafafa 0%, #ffffff 100%);
            }

            .chat-messages::-webkit-scrollbar {
                width: 8px;
            }

            .chat-messages::-webkit-scrollbar-track {
                background: transparent;
            }

            .chat-messages::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 4px;
            }

            .chat-messages::-webkit-scrollbar-thumb:hover {
                background: #94a3b8;
            }

            .welcome-message {
                text-align: center;
                padding: 3rem 2rem;
            }

            .welcome-icon {
                width: 80px;
                height: 80px;
                margin: 0 auto 1.5rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
            }

            .welcome-message h3 {
                font-size: 1.5rem;
                margin-bottom: 0.75rem;
                color: var(--text-primary);
            }

            .welcome-message p {
                color: var(--text-secondary);
                margin-bottom: 2rem;
                font-size: 1rem;
            }

            .suggestion-chips {
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
                justify-content: center;
                max-width: 600px;
                margin: 0 auto;
            }

            .chip {
                padding: 0.625rem 1.25rem;
                border-radius: 24px;
                border: 2px solid var(--border-color);
                background: white;
                font-size: 0.875rem;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                font-weight: 500;
            }

            .chip:hover {
                border-color: var(--primary);
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                color: var(--primary);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            }

            .message {
                display: flex;
                gap: 1rem;
                animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .message.user {
                flex-direction: row-reverse;
            }

            .message-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 0.875rem;
                flex-shrink: 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .message.user .message-avatar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .message.assistant .message-avatar {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
            }

            .message-content {
                flex: 1;
                padding: 1rem 1.25rem;
                border-radius: 16px;
                max-width: 85%;
                line-height: 1.8;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                white-space: pre-wrap;
                word-wrap: break-word;
            }

            .message.assistant .message-content {
                background: white;
                color: var(--text-primary);
                border-bottom-left-radius: 4px;
                border: 1px solid var(--border-color);
            }

            /* Format AI responses with proper spacing */
            .message.assistant .message-content strong {
                display: block;
                margin-top: 1rem;
                margin-bottom: 0.5rem;
                color: var(--primary);
            }

            .message.assistant .message-content strong:first-child {
                margin-top: 0;
            }

            .message-meta {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-top: 0.75rem;
                font-size: 0.75rem;
                color: var(--text-tertiary);
            }

            .message.user .message-meta {
                justify-content: flex-end;
            }

            .agents-used {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .agent-badge {
                padding: 0.25rem 0.75rem;
                border-radius: 16px;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
                color: var(--primary);
                font-size: 0.625rem;
                font-weight: 600;
                border: 1px solid rgba(102, 126, 234, 0.3);
            }

            .typing-indicator {
                display: flex;
                gap: 0.375rem;
                padding: 1rem 1.25rem;
                align-items: center;
            }

            .typing-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: var(--primary);
                animation: typing 1.4s infinite ease-in-out;
            }

            .typing-dot:nth-child(2) {
                animation-delay: 0.2s;
            }

            .typing-dot:nth-child(3) {
                animation-delay: 0.4s;
            }

            @keyframes typing {
                0%, 60%, 100% {
                    transform: translateY(0);
                    opacity: 0.7;
                }
                30% {
                    transform: translateY(-12px);
                    opacity: 1;
                }
            }

            .chat-input-container {
                border-top: 2px solid var(--border-color);
                padding: 1.5rem;
                background: white;
            }

            .chat-input-wrapper {
                display: flex;
                gap: 1rem;
                align-items: flex-end;
            }

            #chat-input {
                flex: 1;
                padding: 1rem 1.25rem;
                border: 2px solid var(--border-color);
                border-radius: 16px;
                font-family: inherit;
                font-size: 0.9375rem;
                resize: none;
                max-height: 120px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                line-height: 1.5;
            }

            #chat-input:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            }

            .send-btn {
                width: 48px;
                height: 48px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                flex-shrink: 0;
                box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
            }

            .send-btn:hover:not(:disabled) {
                transform: scale(1.1) rotate(15deg);
                box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
            }

            .send-btn:active:not(:disabled) {
                transform: scale(0.95);
            }

            .send-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }

            .stats-list {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            .stat-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.875rem 1rem;
                background: var(--bg-secondary);
                border-radius: 10px;
                border: 1px solid var(--border-color);
                transition: all 0.2s;
            }

            .stat-item:hover {
                border-color: var(--primary);
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
            }

            .stat-label {
                font-size: 0.75rem;
                color: var(--text-secondary);
                font-weight: 500;
            }

            .stat-value {
                font-size: 1rem;
                font-weight: 700;
                color: var(--primary);
            }

            .loading-spinner {
                text-align: center;
                padding: 2rem;
                color: var(--text-secondary);
                font-size: 0.875rem;
            }

            /* Smooth scrollbar for panels */
            .agent-status-panel::-webkit-scrollbar,
            .stats-panel::-webkit-scrollbar {
                width: 6px;
            }

            .agent-status-panel::-webkit-scrollbar-track,
            .stats-panel::-webkit-scrollbar-track {
                background: transparent;
            }

            .agent-status-panel::-webkit-scrollbar-thumb,
            .stats-panel::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 3px;
            }

            .agent-status-panel::-webkit-scrollbar-thumb:hover,
            .stats-panel::-webkit-scrollbar-thumb:hover {
                background: #94a3b8;
            }
        </style>
    `;
    
    // Initialize after returning HTML
    setTimeout(() => {
        initAIChat();
    }, 100);
    
    return html;
}

// Initialize AI Chat
function initAIChat() {
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const { user } = authState.get();

    if (!chatMessages || !chatInput || !sendBtn) return;

    // Ensure inputs are enabled when initializing
    sendBtn.disabled = false;
    chatInput.disabled = false;

    // Load chat history from localStorage
    loadChatHistory();

    // Load system stats
    loadSystemStats();

    // Handle suggestion chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.getAttribute('data-query');
            chatInput.value = query;
            sendMessage();
        });
    });

    // Handle send button
    sendBtn.addEventListener('click', sendMessage);

    // Handle enter key
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = chatInput.scrollHeight + 'px';
    });

    // Clear history
    clearHistoryBtn?.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear chat history?')) return;
        
        try {
            await apiFetch(`/ai/chat/history/${user.id}`, { method: 'DELETE' });
            
            // Clear localStorage
            localStorage.removeItem('ai_chat_history');
            
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                    </div>
                    <h3>Chat history cleared!</h3>
                    <p>Start a new conversation with your AI financial advisor.</p>
                </div>
            `;
        } catch (error) {
            console.error('Error clearing history:', error);
            alert('Failed to clear history. Please try again.');
        }
    });

    async function sendMessage() {
        const query = chatInput.value.trim();
        if (!query || sendBtn.disabled) return;

        // Add user message
        addMessage('user', query);
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Disable input
        sendBtn.disabled = true;
        chatInput.disabled = true;

        // Add typing indicator
        const typingId = 'typing-' + Date.now();
        addTypingIndicator(typingId);

        try {
            const startTime = Date.now();
            
            // Use multi-agent endpoint
            const response = await apiFetch('/ai/chat', {
                method: 'POST',
                body: JSON.stringify({
                    query,
                    user_id: user.id
                })
            });

            const responseTime = ((Date.now() - startTime) / 1000).toFixed(2);

            // Remove typing indicator
            document.getElementById(typingId)?.remove();

            // Add assistant message
            addMessage('assistant', response.response, {
                agents: response.agents_used || [],
                time: responseTime,
                success: response.success
            });

            // Update stats
            updateStats(response);

        } catch (error) {
            console.error('Chat error:', error);
            document.getElementById(typingId)?.remove();
            addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            sendBtn.disabled = false;
            chatInput.disabled = false;
            chatInput.focus();
        }
    }

    function addMessage(type, content, meta = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = type === 'user' ? (user.name?.[0] || 'U') : 'AI';
        
        // Format content for better readability
        let formattedContent = content;
        if (type === 'assistant') {
            // Preserve existing line breaks and add HTML formatting
            formattedContent = content
                .replace(/\*\*/g, '') // Remove markdown bold
                .replace(/\n\n\n+/g, '\n\n') // Normalize multiple line breaks to double
                .replace(/\n\n/g, '<br><br>') // Convert double newlines to double breaks
                .replace(/\n/g, '<br>') // Convert single newlines to breaks
                .replace(/•/g, '•') // Preserve bullets
                .replace(/(\d+\.)\s/g, '<br>$1 ') // Format numbered lists with breaks
                .trim();
        }
        
        let metaHTML = '';
        if (meta.agents && meta.agents.length > 0) {
            const agentBadges = meta.agents.map(agent => 
                `<span class="agent-badge">${agent}</span>`
            ).join('');
            metaHTML = `
                <div class="message-meta">
                    <div class="agents-used">${agentBadges}</div>
                    <span>•</span>
                    <span>${meta.time}s</span>
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div>
                <div class="message-content">${formattedContent}</div>
                ${metaHTML}
            </div>
        `;

        // Remove welcome message if exists
        const welcomeMsg = chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Save to localStorage
        saveChatHistory();
    }

    function addTypingIndicator(id) {
        const typingDiv = document.createElement('div');
        typingDiv.id = id;
        typingDiv.className = 'message assistant';
        typingDiv.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function loadSystemStats() {
        try {
            const response = await apiFetch('/ai/stats');
            
            document.getElementById('total-queries').textContent = response.total_queries || 0;
            document.getElementById('avg-response-time').textContent = 
                response.avg_response_time ? `${response.avg_response_time.toFixed(2)}s` : '-';
            document.getElementById('success-rate').textContent = 
                response.success_rate ? `${(response.success_rate * 100).toFixed(1)}%` : '-';
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    function updateStats(response) {
        // Update stats after each query
        loadSystemStats();
    }
    
    function saveChatHistory() {
        const messages = [];
        chatMessages.querySelectorAll('.message').forEach(msg => {
            const type = msg.classList.contains('user') ? 'user' : 'assistant';
            const content = msg.querySelector('.message-content')?.textContent || '';
            const agentBadges = Array.from(msg.querySelectorAll('.agent-badge')).map(b => b.textContent);
            const time = msg.querySelector('.message-meta span:last-child')?.textContent || '';
            
            messages.push({
                type,
                content,
                agents: agentBadges,
                time
            });
        });
        
        localStorage.setItem('ai_chat_history', JSON.stringify(messages));
    }
    
    function loadChatHistory() {
        const saved = localStorage.getItem('ai_chat_history');
        if (!saved) return;
        
        try {
            const messages = JSON.parse(saved);
            
            // Remove welcome message
            const welcomeMsg = chatMessages.querySelector('.welcome-message');
            if (welcomeMsg) welcomeMsg.remove();
            
            // Restore messages
            messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.type}`;
                
                const avatar = msg.type === 'user' ? (user.name?.[0] || 'U') : 'AI';
                
                // Apply formatting to assistant messages
                let formattedContent = msg.content;
                if (msg.type === 'assistant') {
                    // Preserve existing line breaks and add HTML formatting
                    formattedContent = msg.content
                        .replace(/\*\*/g, '') // Remove markdown bold
                        .replace(/\n\n\n+/g, '\n\n') // Normalize multiple line breaks to double
                        .replace(/\n\n/g, '<br><br>') // Convert double newlines to double breaks
                        .replace(/\n/g, '<br>') // Convert single newlines to breaks
                        .replace(/•/g, '•') // Preserve bullets
                        .replace(/(\d+\.)\s/g, '<br>$1 ') // Format numbered lists with breaks
                        .trim();
                }
                
                let metaHTML = '';
                if (msg.agents && msg.agents.length > 0) {
                    const agentBadges = msg.agents.map(agent => 
                        `<span class="agent-badge">${agent}</span>`
                    ).join('');
                    metaHTML = `
                        <div class="message-meta">
                            <div class="agents-used">${agentBadges}</div>
                            <span>•</span>
                            <span>${msg.time}</span>
                        </div>
                    `;
                }
                
                messageDiv.innerHTML = `
                    <div class="message-avatar">${avatar}</div>
                    <div>
                        <div class="message-content">${formattedContent}</div>
                        ${metaHTML}
                    </div>
                `;
                
                chatMessages.appendChild(messageDiv);
            });
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
}
