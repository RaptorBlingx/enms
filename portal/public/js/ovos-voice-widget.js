/**
 * EnMS OVOS Voice Assistant Widget
 * Floating widget for OVOS voice assistant integration
 * Connects to OVOS via /api/v1/ovos/voice/query
 * 
 * SEPARATE from chatbot-widget.js (Rasa chatbot)
 * 
 * Created: December 1, 2025
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        // API endpoint - works with nginx proxy
        apiUrl: window.location.port === '8001' 
            ? '/api/v1/ovos/voice/query' 
            : '/api/analytics/api/v1/ovos/voice/query',
        healthUrl: window.location.port === '8001' 
            ? '/api/v1/ovos/voice/health' 
            : '/api/analytics/api/v1/ovos/voice/health',
        welcomeMessage: 'Hello! I\'m your EnMS voice assistant. Ask me about energy consumption, machine status, anomalies, forecasts, or say "factory overview" for a summary. Say "Jarvis" to activate hands-free!',
        placeholder: 'Ask about energy, machines, anomalies...',
        title: 'OVOS Voice Assistant',
        subtitle: 'Energy Management',
        sessionPrefix: 'enms_ovos_',
        // Porcupine Wake Word Config
        // Get free key at: https://console.picovoice.ai/
        porcupineAccessKey: 'm5P2rhLwLCydE9xgQLrIUovHrhOaiYXVrxcRHmdPBOMokPUVHbSTaQ==', // User must set this
        wakeWord: 'Jarvis'
    };

    // Session management
    let sessionId = CONFIG.sessionPrefix + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    let isOpen = false;
    let isLoading = false;
    let audioEnabled = true;  // TTS audio playback enabled by default
    let currentAudio = null;  // Track currently playing audio
    
    // Wake word state
    let wakeWordEnabled = false;
    let voicePermissionGranted = false;  // One-time permission flag
    let porcupine = null;
    let webVp = null;  // Web Voice Processor

    // Create floating "Enable Voice" button (shown until user grants permission)
    function createEnableVoiceButton() {
        const btnHTML = `
            <button id="ovos-enable-voice" class="ovos-enable-voice">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                </svg>
                <span>Enable Voice</span>
            </button>
        `;
        const container = document.createElement('div');
        container.innerHTML = btnHTML;
        document.body.appendChild(container.firstElementChild);
    }

    // Create widget HTML
    function createWidget() {
        const widgetHTML = `
            <div id="ovos-voice-widget" class="ovos-closed">
                <!-- Toggle Button -->
                <button id="ovos-toggle" class="ovos-toggle" aria-label="Open OVOS voice assistant" title="OVOS Voice Assistant">
                    <svg class="ovos-icon-open" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                    <svg class="ovos-icon-close" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none">
                        <path d="M18 6L6 18M6 6l12 12"></path>
                    </svg>
                </button>

                <!-- Chat Window -->
                <div id="ovos-window" class="ovos-window">
                    <!-- Header -->
                    <div class="ovos-header">
                        <div class="ovos-header-info">
                            <div class="ovos-avatar">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                </svg>
                            </div>
                            <div>
                                <div class="ovos-title">${CONFIG.title}</div>
                                <div class="ovos-status" id="ovos-status">${CONFIG.subtitle}</div>
                            </div>
                        </div>
                        <button id="ovos-minimize" class="ovos-minimize" aria-label="Minimize">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>

                    <!-- Messages -->
                    <div id="ovos-messages" class="ovos-messages">
                        <div class="ovos-message ovos-bot">
                            <div class="ovos-bubble">${CONFIG.welcomeMessage}</div>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="ovos-quick-actions">
                        <button class="ovos-quick-btn" data-query="factory overview">Overview</button>
                        <button class="ovos-quick-btn" data-query="any anomalies today?">Anomalies</button>
                        <button class="ovos-quick-btn" data-query="top energy consumers">Top Consumers</button>
                        <button id="ovos-wakeword-toggle" class="ovos-wakeword-toggle" title="Enable 'Jarvis' wake word">Jarvis</button>
                        <button id="ovos-audio-toggle" class="ovos-audio-toggle" title="Toggle audio">🔊</button>
                    </div>

                    <!-- Input -->
                    <div class="ovos-input-container">
                        <button id="ovos-mic" class="ovos-mic" aria-label="Voice input" title="Click to speak">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="23"></line>
                            </svg>
                        </button>
                        <input 
                            type="text" 
                            id="ovos-input" 
                            class="ovos-input" 
                            placeholder="${CONFIG.placeholder}"
                            autocomplete="off"
                        >
                        <button id="ovos-send" class="ovos-send" aria-label="Send">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        const container = document.createElement('div');
        container.innerHTML = widgetHTML;
        document.body.appendChild(container.firstElementChild);
    }

    // Create widget styles
    function createStyles() {
        const styles = `
            /* Floating Enable Voice Button */
            .ovos-enable-voice {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4);
                animation: ovos-enable-pulse 2s infinite;
                transition: all 0.3s ease;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            .ovos-enable-voice:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 24px rgba(124, 58, 237, 0.5);
            }

            @keyframes ovos-enable-pulse {
                0%, 100% { box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4); }
                50% { box-shadow: 0 4px 24px rgba(124, 58, 237, 0.6), 0 0 0 8px rgba(124, 58, 237, 0.1); }
            }

            .ovos-enable-voice.loading {
                pointer-events: none;
                opacity: 0.8;
            }

            .ovos-enable-voice.hidden {
                display: none;
            }

            /* Wake Word Active Indicator */
            .ovos-wakeword-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 8px 14px;
                background: rgba(16, 185, 129, 0.9);
                color: white;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                box-shadow: 0 2px 12px rgba(16, 185, 129, 0.3);
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                cursor: pointer;
            }

            .ovos-wakeword-indicator .dot {
                width: 8px;
                height: 8px;
                background: white;
                border-radius: 50%;
                animation: ovos-dot-pulse 1.5s infinite;
            }

            @keyframes ovos-dot-pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.4; }
            }

            #ovos-voice-widget {
                position: fixed;
                bottom: 90px;
                right: 20px;
                z-index: 9999;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            .ovos-toggle {
                width: 52px;
                height: 52px;
                border-radius: 50%;
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
                transition: all 0.3s ease;
                color: white;
            }

            .ovos-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 24px rgba(16, 185, 129, 0.5);
            }

            .ovos-window {
                position: absolute;
                bottom: 65px;
                right: 0;
                width: 380px;
                height: 500px;
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
                display: none;
                flex-direction: column;
                overflow: hidden;
                animation: ovos-slide-up 0.3s ease;
            }

            @keyframes ovos-slide-up {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .ovos-closed .ovos-window { display: none; }
            .ovos-open .ovos-window { display: flex; }
            .ovos-open .ovos-icon-open { display: none; }
            .ovos-open .ovos-icon-close { display: block !important; }

            .ovos-header {
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                color: white;
                padding: 14px 18px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .ovos-header-info {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .ovos-avatar {
                width: 36px;
                height: 36px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .ovos-title {
                font-weight: 600;
                font-size: 15px;
            }

            .ovos-status {
                font-size: 11px;
                opacity: 0.85;
            }

            .ovos-status.online { color: #bbf7d0; }
            .ovos-status.offline { color: #fca5a5; }

            .ovos-minimize {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 8px;
                padding: 6px;
                cursor: pointer;
                color: white;
                transition: background 0.2s;
            }

            .ovos-minimize:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            .ovos-messages {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                background: #f0fdf4;
            }

            .ovos-message {
                display: flex;
                flex-direction: column;
                max-width: 85%;
            }

            .ovos-user { align-self: flex-end; }
            .ovos-bot { align-self: flex-start; }

            .ovos-bubble {
                padding: 10px 14px;
                border-radius: 14px;
                font-size: 13px;
                line-height: 1.5;
                word-wrap: break-word;
                white-space: pre-wrap;
            }

            .ovos-user .ovos-bubble {
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                color: white;
                border-bottom-right-radius: 4px;
            }

            .ovos-bot .ovos-bubble {
                background: white;
                color: #1f2937;
                border-bottom-left-radius: 4px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            }

            .ovos-quick-actions {
                padding: 8px 12px;
                background: white;
                border-top: 1px solid #e5e7eb;
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
            }

            .ovos-quick-btn {
                padding: 5px 10px;
                border: 1px solid #d1fae5;
                border-radius: 14px;
                background: #ecfdf5;
                font-size: 11px;
                cursor: pointer;
                transition: all 0.2s;
                color: #065f46;
            }

            .ovos-quick-btn:hover {
                background: #10B981;
                border-color: #10B981;
                color: white;
            }

            .ovos-wakeword-toggle {
                padding: 5px 10px;
                border: 1px solid #d1fae5;
                border-radius: 14px;
                background: #ecfdf5;
                font-size: 11px;
                cursor: pointer;
                transition: all 0.2s;
                color: #065f46;
            }

            .ovos-wakeword-toggle.active {
                background: #7c3aed;
                border-color: #7c3aed;
                color: white;
                animation: ovos-wakeword-pulse 2s infinite;
            }

            @keyframes ovos-wakeword-pulse {
                0%, 100% { box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.4); }
                50% { box-shadow: 0 0 0 8px rgba(124, 58, 237, 0); }
            }

            .ovos-wakeword-toggle:hover {
                transform: scale(1.05);
            }

            .ovos-audio-toggle {
                padding: 5px 10px;
                border: 1px solid #d1fae5;
                border-radius: 14px;
                background: #ecfdf5;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s;
                margin-left: auto;
            }

            .ovos-audio-toggle.muted {
                background: #fee2e2;
                border-color: #fecaca;
            }

            .ovos-audio-toggle:hover {
                transform: scale(1.1);
            }

            .ovos-input-container {
                padding: 12px;
                background: white;
                border-top: 1px solid #e5e7eb;
                display: flex;
                gap: 10px;
                align-items: center;
            }

            .ovos-mic {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #f0fdf4;
                border: 2px solid #10B981;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #10B981;
                transition: all 0.2s;
                flex-shrink: 0;
            }

            .ovos-mic:hover {
                background: #10B981;
                color: white;
            }

            .ovos-mic.listening {
                background: #dc2626;
                border-color: #dc2626;
                color: white;
                animation: ovos-pulse 1s infinite;
            }

            @keyframes ovos-pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }

            .ovos-mic:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            .ovos-input {
                flex: 1;
                padding: 10px 14px;
                border: 1px solid #d1fae5;
                border-radius: 20px;
                font-size: 13px;
                outline: none;
                transition: border-color 0.2s;
            }

            .ovos-input:focus {
                border-color: #10B981;
            }

            .ovos-send {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                transition: all 0.2s;
            }

            .ovos-send:hover { transform: scale(1.05); }
            .ovos-send:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

            .ovos-typing {
                display: flex;
                align-items: center;
                gap: 4px;
                padding: 10px 14px;
                background: white;
                border-radius: 14px;
                border-bottom-left-radius: 4px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            }

            .ovos-typing-dot {
                width: 6px;
                height: 6px;
                background: #10B981;
                border-radius: 50%;
                animation: ovos-typing 1.4s infinite ease-in-out;
            }

            .ovos-typing-dot:nth-child(1) { animation-delay: 0s; }
            .ovos-typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .ovos-typing-dot:nth-child(3) { animation-delay: 0.4s; }

            @keyframes ovos-typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-4px); }
            }

            .ovos-error {
                background: #fef2f2 !important;
                color: #dc2626 !important;
                border-left: 3px solid #dc2626;
            }

            .ovos-latency {
                font-size: 9px;
                color: #9ca3af;
                margin-top: 3px;
                text-align: right;
            }

            @media (max-width: 480px) {
                .ovos-window {
                    width: calc(100vw - 40px);
                    height: calc(100vh - 160px);
                    bottom: 70px;
                    right: -10px;
                }
            }
        `;

        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    function toggleWidget() {
        const widget = document.getElementById('ovos-voice-widget');
        isOpen = !isOpen;
        widget.className = isOpen ? 'ovos-open' : 'ovos-closed';
        if (isOpen) {
            document.getElementById('ovos-input').focus();
            checkHealth();
        }
    }

    function addMessage(text, isUser = false, isError = false, latencyMs = null, ttsLatencyMs = null) {
        const container = document.getElementById('ovos-messages');
        const msgDiv = document.createElement('div');
        msgDiv.className = `ovos-message ${isUser ? 'ovos-user' : 'ovos-bot'}`;
        
        const bubble = document.createElement('div');
        bubble.className = `ovos-bubble ${isError ? 'ovos-error' : ''}`;
        bubble.textContent = text;
        msgDiv.appendChild(bubble);
        
        if (!isUser && latencyMs !== null) {
            const latency = document.createElement('div');
            latency.className = 'ovos-latency';
            let latencyText = `${latencyMs}ms`;
            if (ttsLatencyMs && ttsLatencyMs > 0) {
                latencyText += ` (TTS: ${ttsLatencyMs}ms)`;
            }
            latency.textContent = latencyText;
            msgDiv.appendChild(latency);
        }
        
        container.appendChild(msgDiv);
        container.scrollTop = container.scrollHeight;
    }

    function showTyping() {
        const container = document.getElementById('ovos-messages');
        const div = document.createElement('div');
        div.id = 'ovos-typing';
        div.className = 'ovos-message ovos-bot';
        div.innerHTML = `<div class="ovos-typing"><div class="ovos-typing-dot"></div><div class="ovos-typing-dot"></div><div class="ovos-typing-dot"></div></div>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function hideTyping() {
        const el = document.getElementById('ovos-typing');
        if (el) el.remove();
    }

    async function checkHealth() {
        const statusEl = document.getElementById('ovos-status');
        try {
            const res = await fetch(CONFIG.healthUrl);
            if (res.ok) {
                const data = await res.json();
                if (data.ovos_connected) {
                    statusEl.textContent = 'Connected';
                    statusEl.className = 'ovos-status online';
                } else {
                    statusEl.textContent = 'OVOS Offline';
                    statusEl.className = 'ovos-status offline';
                }
            } else {
                statusEl.textContent = 'Bridge Offline';
                statusEl.className = 'ovos-status offline';
            }
        } catch (e) {
            statusEl.textContent = 'Offline';
            statusEl.className = 'ovos-status offline';
        }
    }

    async function sendMessage(text) {
        if (!text.trim() || isLoading) return;

        isLoading = true;
        const input = document.getElementById('ovos-input');
        const sendBtn = document.getElementById('ovos-send');
        
        input.disabled = true;
        sendBtn.disabled = true;

        addMessage(text, true);
        input.value = '';
        showTyping();

        // Stop any currently playing audio
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }

        try {
            const res = await fetch(CONFIG.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    utterance: text, 
                    session_id: sessionId,
                    include_audio: audioEnabled
                }),
            });

            hideTyping();
            const data = await res.json();

            if (data.success && data.response) {
                addMessage(data.response, false, false, data.latency_ms, data.tts_latency_ms);
                
                // Play audio if available and enabled
                if (audioEnabled && data.audio_base64) {
                    playAudio(data.audio_base64, data.audio_format || 'wav');
                }
            } else if (data.error) {
                addMessage(data.error, false, true);
            } else {
                addMessage('No response received.', false, true);
            }
        } catch (err) {
            hideTyping();
            console.error('OVOS error:', err);
            addMessage('Connection error. Is OVOS REST Bridge running?', false, true);
        }

        isLoading = false;
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }

    function playAudio(base64Data, format) {
        try {
            // Map format to proper MIME type
            const mimeType = format === 'mp3' ? 'audio/mpeg' : `audio/${format}`;
            const audio = new Audio(`data:${mimeType};base64,${base64Data}`);
            currentAudio = audio;
            
            audio.onended = () => {
                currentAudio = null;
            };
            
            audio.onerror = (e) => {
                console.error('Audio playback error:', e);
                currentAudio = null;
            };
            
            audio.play().catch(err => {
                console.warn('Audio autoplay blocked:', err);
                // Browser may block autoplay - user interaction required
            });
        } catch (err) {
            console.error('Failed to create audio:', err);
        }
    }

    function toggleAudio() {
        audioEnabled = !audioEnabled;
        const btn = document.getElementById('ovos-audio-toggle');
        btn.textContent = audioEnabled ? '🔊' : '🔇';
        btn.classList.toggle('muted', !audioEnabled);
        btn.title = audioEnabled ? 'Audio enabled (click to mute)' : 'Audio muted (click to enable)';
        
        if (!audioEnabled && currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
    }

    // Speech Recognition (Browser STT)
    let recognition = null;
    let isListening = false;

    function initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn('Speech recognition not supported in this browser');
            const micBtn = document.getElementById('ovos-mic');
            if (micBtn) {
                micBtn.style.display = 'none';
            }
            return false;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            const micBtn = document.getElementById('ovos-mic');
            micBtn.classList.add('listening');
            micBtn.title = 'Listening... (click to stop)';
            document.getElementById('ovos-input').placeholder = 'Listening...';
        };

        recognition.onend = () => {
            isListening = false;
            const micBtn = document.getElementById('ovos-mic');
            micBtn.classList.remove('listening');
            micBtn.title = 'Click to speak';
            document.getElementById('ovos-input').placeholder = CONFIG.placeholder;
            
            // Restart wake word listening if enabled
            if (wakeWordEnabled && wakeWordRecognition) {
                // Reset indicator text
                const indicator = document.getElementById('ovos-wakeword-indicator');
                if (indicator) {
                    indicator.style.background = 'rgba(16, 185, 129, 0.9)';
                    indicator.querySelector('span').textContent = 'Say "Jarvis"';
                }
                
                // Restart wake word after a short delay
                setTimeout(() => {
                    if (wakeWordEnabled && !isListening) {
                        try {
                            wakeWordRecognition.start();
                        } catch (e) {}
                    }
                }, 500);
            }
        };

        recognition.onresult = (event) => {
            const input = document.getElementById('ovos-input');
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // Show interim results in input
            input.value = finalTranscript || interimTranscript;

            // Auto-send when final result received
            if (finalTranscript) {
                setTimeout(() => {
                    sendMessage(finalTranscript);
                }, 300);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            isListening = false;
            const micBtn = document.getElementById('ovos-mic');
            micBtn.classList.remove('listening');
            
            if (event.error === 'not-allowed') {
                addMessage('Microphone access denied. Please allow microphone access in your browser settings.', false, true);
            } else if (event.error !== 'aborted') {
                addMessage(`Voice input error: ${event.error}`, false, true);
            }
        };

        return true;
    }

    function toggleListening() {
        if (!recognition) {
            if (!initSpeechRecognition()) {
                addMessage('Voice input not supported in this browser. Try Chrome or Edge.', false, true);
                return;
            }
        }

        if (isListening) {
            recognition.stop();
        } else {
            // Stop any playing audio first
            if (currentAudio) {
                currentAudio.pause();
                currentAudio = null;
            }
            try {
                recognition.start();
            } catch (e) {
                console.error('Failed to start recognition:', e);
            }
        }
    }

    // =========================================================================
    // Wake Word Detection (Using Web Speech API - No external dependencies)
    // =========================================================================
    
    let wakeWordRecognition = null;
    let lastWakeWordTime = 0;  // Debounce wake word detection
    
    function initWakeWord() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            addMessage('Wake word requires a browser with Speech Recognition (Chrome, Edge).', false, true);
            return false;
        }

        try {
            wakeWordRecognition = new SpeechRecognition();
            wakeWordRecognition.continuous = true;  // Keep listening
            wakeWordRecognition.interimResults = true;  // Get partial results
            wakeWordRecognition.lang = 'en-US';
            
            wakeWordRecognition.onresult = (event) => {
                // Check all results for wake word
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript.toLowerCase();
                    
                    // Check for wake word
                    if (transcript.includes('jarvis') || transcript.includes('travis') || transcript.includes('jervis')) {
                        // Debounce - ignore if triggered within last 3 seconds
                        const now = Date.now();
                        if (now - lastWakeWordTime < 3000) {
                            console.log('Wake word debounced (already triggered recently)');
                            return;
                        }
                        lastWakeWordTime = now;
                        
                        console.log('🎯 Wake word detected in:', transcript);
                        
                        // Stop wake word listening temporarily
                        wakeWordRecognition.stop();
                        
                        // Trigger the wake word callback
                        onWakeWordDetected();
                        return;
                    }
                }
            };
            
            wakeWordRecognition.onend = () => {
                // Auto-restart if wake word is enabled (unless we're in query mode)
                if (wakeWordEnabled && !isListening) {
                    setTimeout(() => {
                        if (wakeWordEnabled && !isListening) {
                            try {
                                wakeWordRecognition.start();
                            } catch (e) {
                                // Ignore - might already be started
                            }
                        }
                    }, 100);
                }
            };
            
            wakeWordRecognition.onerror = (event) => {
                if (event.error === 'not-allowed') {
                    addMessage('Microphone access denied. Please allow mic access.', false, true);
                    wakeWordEnabled = false;
                    updateWakeWordUI(false);
                } else if (event.error !== 'aborted' && event.error !== 'no-speech') {
                    console.warn('Wake word recognition error:', event.error);
                }
            };
            
            // Start listening
            wakeWordRecognition.start();
            console.log('✅ Wake word "Jarvis" listening started (Web Speech API)');
            return true;
            
        } catch (error) {
            console.error('Failed to initialize wake word:', error);
            addMessage(`Wake word error: ${error.message}`, false, true);
            return false;
        }
    }
    
    function stopWakeWord() {
        if (wakeWordRecognition) {
            try {
                wakeWordRecognition.stop();
            } catch (e) {}
            wakeWordRecognition = null;
        }
    }
    
    function onWakeWordDetected() {
        console.log('🎯 Wake word activated!');
        
        // Visual feedback on indicator
        const indicator = document.getElementById('ovos-wakeword-indicator');
        if (indicator) {
            indicator.style.background = 'rgba(124, 58, 237, 0.95)';
            indicator.querySelector('span').textContent = 'Listening...';
        }
        
        // Open widget
        if (!isOpen) {
            toggleWidget();
        }
        
        // Add feedback message
        addMessage('Jarvis activated! Listening for your command...', false, false);
        
        // Start query listening
        setTimeout(() => {
            if (!isListening) {
                toggleListening();
            }
        }, 300);
    }
    
    function updateWakeWordUI(enabled) {
        const wakeBtn = document.getElementById('ovos-wakeword-toggle');
        const indicator = document.getElementById('ovos-wakeword-indicator');
        const enableBtn = document.getElementById('ovos-enable-voice');
        
        if (enabled) {
            if (wakeBtn) {
                wakeBtn.classList.add('active');
                wakeBtn.title = 'Wake word active - say "Jarvis" (click to disable)';
            }
            if (enableBtn) enableBtn.classList.add('hidden');
        } else {
            if (wakeBtn) {
                wakeBtn.classList.remove('active');
                wakeBtn.title = 'Enable "Jarvis" wake word';
            }
            if (indicator) indicator.remove();
        }
    }

    // One-time enable function - grants permission and starts background listening
    async function enableVoiceAssistant() {
        const enableBtn = document.getElementById('ovos-enable-voice');
        if (!enableBtn) return;
        
        enableBtn.classList.add('loading');
        enableBtn.innerHTML = '<span>Enabling...</span>';
        
        try {
            // Initialize wake word (this requests mic permission)
            const success = initWakeWord();
            
            if (success) {
                voicePermissionGranted = true;
                wakeWordEnabled = true;
                
                // Hide enable button
                enableBtn.classList.add('hidden');
                
                // Show persistent indicator
                showWakeWordIndicator();
                
                // Update toggle button in widget
                updateWakeWordUI(true);
                
                console.log('✅ Voice assistant enabled - say "Jarvis" anytime!');
            } else {
                enableBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path></svg><span>Enable Voice</span>';
                enableBtn.classList.remove('loading');
            }
        } catch (error) {
            console.error('Failed to enable voice:', error);
            enableBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path></svg><span>Enable Voice</span>';
            enableBtn.classList.remove('loading');
        }
    }

    function showWakeWordIndicator() {
        // Remove enable button if exists
        const enableBtn = document.getElementById('ovos-enable-voice');
        if (enableBtn) enableBtn.remove();
        
        // Create indicator
        const indicatorHTML = `
            <div id="ovos-wakeword-indicator" class="ovos-wakeword-indicator" title="Click to disable voice assistant">
                <div class="dot"></div>
                <span>Say "Jarvis"</span>
            </div>
        `;
        const container = document.createElement('div');
        container.innerHTML = indicatorHTML;
        document.body.appendChild(container.firstElementChild);
        
        // Click to disable
        document.getElementById('ovos-wakeword-indicator').addEventListener('click', disableVoiceAssistant);
    }

    function disableVoiceAssistant() {
        // Stop wake word recognition
        stopWakeWord();
        wakeWordEnabled = false;
        
        // Remove indicator
        const indicator = document.getElementById('ovos-wakeword-indicator');
        if (indicator) indicator.remove();
        
        // Show enable button again
        createEnableVoiceButton();
        document.getElementById('ovos-enable-voice').addEventListener('click', enableVoiceAssistant);
        
        // Update widget button
        updateWakeWordUI(false);
        
        console.log('🔇 Voice assistant disabled');
    }

    function toggleWakeWord() {
        const btn = document.getElementById('ovos-wakeword-toggle');
        
        if (wakeWordEnabled) {
            // Disable wake word
            stopWakeWord();
            wakeWordEnabled = false;
            btn.classList.remove('active');
            btn.textContent = 'Jarvis';
            btn.title = 'Enable "Jarvis" wake word';
            console.log('Wake word disabled');
            
            // Also remove indicator if present
            const indicator = document.getElementById('ovos-wakeword-indicator');
            if (indicator) indicator.remove();
            
            // Show enable button again
            if (!document.getElementById('ovos-enable-voice')) {
                createEnableVoiceButton();
                document.getElementById('ovos-enable-voice').addEventListener('click', enableVoiceAssistant);
            }
            
        } else {
            // Enable wake word
            btn.textContent = 'Enabling...';
            const success = initWakeWord();
            
            if (success) {
                wakeWordEnabled = true;
                btn.classList.add('active');
                btn.textContent = 'Jarvis';
                btn.title = 'Wake word active - say "Jarvis" (click to disable)';
                addMessage('Wake word enabled! Say "Jarvis" to activate voice input.', false, false);
                
                // Hide enable button if visible
                const enableBtn = document.getElementById('ovos-enable-voice');
                if (enableBtn) enableBtn.classList.add('hidden');
                
                // Show indicator
                if (!document.getElementById('ovos-wakeword-indicator')) {
                    showWakeWordIndicator();
                }
            } else {
                btn.textContent = 'Jarvis';
            }
        }
    }

    function init() {
        createStyles();
        createWidget();
        
        // Create floating "Enable Voice" button (for one-time permission)
        createEnableVoiceButton();

        document.getElementById('ovos-toggle').addEventListener('click', toggleWidget);
        document.getElementById('ovos-minimize').addEventListener('click', toggleWidget);
        
        document.getElementById('ovos-send').addEventListener('click', () => {
            sendMessage(document.getElementById('ovos-input').value);
        });

        document.getElementById('ovos-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage(e.target.value);
        });

        document.querySelectorAll('.ovos-quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                if (query) sendMessage(query);
            });
        });

        document.getElementById('ovos-audio-toggle').addEventListener('click', toggleAudio);
        
        // Mic button for voice input
        document.getElementById('ovos-mic').addEventListener('click', toggleListening);
        
        // Wake word toggle (inside widget)
        document.getElementById('ovos-wakeword-toggle').addEventListener('click', toggleWakeWord);
        
        // Enable voice button (floating - one-time permission)
        document.getElementById('ovos-enable-voice').addEventListener('click', enableVoiceAssistant);
        
        // Initialize speech recognition
        initSpeechRecognition();

        console.log('✅ EnMS OVOS Voice Widget loaded (hands-free ready - click "Enable Voice" to start)');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
