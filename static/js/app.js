/**
 * お母さんスイッチ - メインJavaScript
 * 音声認識・録音・UI制御を統合管理
 */

// ========== グローバル変数 ==========
let recognition = null;
let mediaRecorder = null;
let audioChunks = [];
let isListening = false;
let isRecording = false;
let startTime = Date.now();
let syncRate = 0;
let audioStream = null;

// ========== DOM要素 ==========
const elements = {
    micButton: document.getElementById('mic-button'),
    systemStatus: document.getElementById('system-status'),
    speakerDisplay: document.getElementById('speaker-display'),
    syncRateValue: document.getElementById('sync-rate-value'),
    syncRateBar: document.getElementById('sync-rate-bar'),
    syncMessage: document.getElementById('sync-message'),
    voiceInput: document.getElementById('voice-input'),
    conversationLog: document.getElementById('conversation-log'),
    resetButton: document.getElementById('reset-button'),
    clearLogButton: document.getElementById('clear-log'),
    uptime: document.getElementById('uptime')
};

// ========== 初期化 ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 お母さんスイッチ システム起動');
    initEventListeners();
    updateUptime();
    setInterval(updateUptime, 1000);
});

// ========== イベントリスナー設定 ==========
function initEventListeners() {
    elements.micButton.addEventListener('click', toggleListening);
    elements.resetButton.addEventListener('click', resetSystem);
    elements.clearLogButton.addEventListener('click', clearLog);
}

// ========== アップタイム更新 ==========
function updateUptime() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const hours = Math.floor(elapsed / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
    const seconds = (elapsed % 60).toString().padStart(2, '0');
    elements.uptime.textContent = `${hours}:${minutes}:${seconds}`;
}

// ========== シンクロ率更新 ==========
function updateSyncRate(rate) {
    syncRate = rate;
    elements.syncRateValue.textContent = `${rate}%`;
    elements.syncRateBar.style.width = `${rate}%`;
    
    let color, message;
    if (rate < 30) {
        color = '#3b82f6';
        message = 'Low authority - User level access';
    } else if (rate < 60) {
        color = '#eab308';
        message = 'Moderate authority - Elevated privileges';
    } else if (rate < 90) {
        color = '#f97316';
        message = 'High authority - Administrative access';
    } else {
        color = '#ef4444';
        message = 'MAXIMUM AUTHORITY - Full system control';
    }
    
    elements.syncRateBar.style.backgroundColor = color;
    elements.syncMessage.textContent = message;
    elements.syncMessage.style.color = color;
}

// ========== 話者表示更新 ==========
function updateSpeaker(speaker) {
    if (speaker === 'MOTHER') {
        elements.speakerDisplay.innerHTML = `
            <div class="text-6xl mb-2">👩</div>
            <div class="orbitron text-2xl font-bold text-red-500">MOTHER</div>
            <div class="text-xs text-red-400 mt-2">Admin Authority Detected</div>
        `;
    } else if (speaker === 'CHILD') {
        elements.speakerDisplay.innerHTML = `
            <div class="text-6xl mb-2">🧒</div>
            <div class="orbitron text-2xl font-bold text-blue-500">CHILD</div>
            <div class="text-xs text-blue-400 mt-2">User Level Access</div>
        `;
    } else {
        elements.speakerDisplay.innerHTML = `
            <div class="text-6xl mb-2">👤</div>
            <div class="orbitron text-2xl font-bold text-gray-500">UNKNOWN</div>
            <div class="text-xs text-gray-400 mt-2">Waiting for input...</div>
        `;
    }
}

// ========== ログエントリー追加 ==========
function addLogEntry(userText, speaker, response, timestamp, hasAudio = false) {
    if (elements.conversationLog.querySelector('.text-gray-600')) {
        elements.conversationLog.innerHTML = '';
    }
    
    const entry = document.createElement('div');
    entry.className = 'log-entry border-l-4 pl-3 py-2';
    entry.style.borderColor = speaker === 'MOTHER' ? '#ef4444' : '#3b82f6';
    
    const time = new Date(timestamp).toLocaleTimeString('ja-JP');
    const speakerColor = speaker === 'MOTHER' ? 'text-red-400' : 'text-blue-400';
    const audioIndicator = hasAudio ? '<span class="text-xs text-purple-400 ml-2">🎤 音声データ送信済</span>' : '';
    
    entry.innerHTML = `
        <div class="flex justify-between items-start mb-1">
            <span class="orbitron text-xs ${speakerColor}">${speaker}</span>
            <span class="text-xs text-gray-500">${time}</span>
        </div>
        <div class="text-sm text-gray-300 mb-1">
            <span class="text-gray-500">INPUT:</span> ${escapeHtml(userText)}${audioIndicator}
        </div>
        <div class="text-sm text-green-400">
            <span class="text-gray-500">OUTPUT:</span> ${escapeHtml(response)}
        </div>
    `;
    
    elements.conversationLog.insertBefore(entry, elements.conversationLog.firstChild);
    
    while (elements.conversationLog.children.length > 10) {
        elements.conversationLog.removeChild(elements.conversationLog.lastChild);
    }
}

// ========== HTMLエスケープ ==========
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== 音声認識初期化 ==========
function initSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert('このブラウザは音声認識に対応していません。Google Chromeをご利用ください。');
        return false;
    }
    
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'ja-JP';
    recognition.continuous = true;
    recognition.interimResults = true;
    
    recognition.onstart = () => {
        console.log('🎤 音声認識開始');
        elements.systemStatus.textContent = 'LISTENING';
        elements.systemStatus.style.color = '#3b82f6';
        elements.voiceInput.innerHTML = '<span class="text-blue-400 animate-pulse">● LISTENING...</span>';
    };
    
    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        if (interimTranscript) {
            elements.voiceInput.innerHTML = `<span class="text-gray-400">${escapeHtml(interimTranscript)}</span>`;
        }
        
        if (finalTranscript) {
            elements.voiceInput.innerHTML = `<span class="text-white">${escapeHtml(finalTranscript)}</span>`;
            stopRecording(finalTranscript);
        }
    };
    
    recognition.onerror = (event) => {
        console.error('❌ 音声認識エラー:', event.error);
        if (event.error === 'no-speech') {
            elements.voiceInput.innerHTML = '<span class="text-yellow-400">音声が検出されませんでした</span>';
        } else {
            elements.voiceInput.innerHTML = `<span class="text-red-400">エラー: ${event.error}</span>`;
        }
    };
    
    recognition.onend = () => {
        console.log('🛑 音声認識終了');
        if (isListening) {
            recognition.start();
        } else {
            elements.systemStatus.textContent = 'IDLE';
            elements.systemStatus.style.color = '#00ff41';
            elements.voiceInput.innerHTML = '<span class="text-gray-600">Stopped</span>';
        }
    };
    
    return true;
}

// ========== 録音開始 ==========
async function startRecording() {
    try {
        if (!audioStream) {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        }
        
        audioChunks = [];
        mediaRecorder = new MediaRecorder(audioStream, {
            mimeType: 'audio/webm'
        });
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.start();
        isRecording = true;
        console.log('🔴 録音開始');
        
        // 録音インジケーターを追加
        const indicator = '<span class="recording-indicator ml-2"></span>';
        if (!elements.voiceInput.innerHTML.includes('recording-indicator')) {
            elements.voiceInput.innerHTML += indicator;
        }
        
    } catch (error) {
        console.error('❌ 録音開始エラー:', error);
        alert('マイクへのアクセスが拒否されました。ブラウザの設定を確認してください。');
    }
}

// ========== 録音停止 ==========
function stopRecording(recognizedText) {
    if (!isRecording || !mediaRecorder) {
        return;
    }
    
    mediaRecorder.onstop = () => {
        console.log('⏹️ 録音停止');
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        processVoiceCommand(recognizedText, audioBlob);
        isRecording = false;
    };
    
    mediaRecorder.stop();
}

// ========== 音声コマンド処理 ==========
async function processVoiceCommand(text, audioBlob) {
    elements.systemStatus.textContent = 'PROCESSING';
    elements.systemStatus.style.color = '#eab308';
    
    try {
        const formData = new FormData();
        formData.append('text', text);
        formData.append('audio', audioBlob, 'input.webm');
        
        console.log('📤 送信データ:', {
            text: text,
            audioSize: audioBlob.size,
            audioType: audioBlob.type
        });
        
        const response = await fetch('/api/command', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        console.log('📥 受信データ:', data);
        
        updateSpeaker(data.speaker);
        updateSyncRate(data.sync_rate);
        addLogEntry(text, data.speaker, data.response, data.timestamp, true);
        
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(data.response);
            utterance.lang = 'ja-JP';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            
            utterance.onstart = () => {
                elements.systemStatus.textContent = 'SPEAKING';
                elements.systemStatus.style.color = '#a855f7';
            };
            
            utterance.onend = () => {
                elements.systemStatus.textContent = 'LISTENING';
                elements.systemStatus.style.color = '#3b82f6';
            };
            
            speechSynthesis.speak(utterance);
        }
        
    } catch (error) {
        console.error('❌ API呼び出しエラー:', error);
        elements.voiceInput.innerHTML = '<span class="text-red-400">サーバーエラーが発生しました</span>';
    }
}

// ========== リスニング開始/停止 ==========
async function toggleListening() {
    if (!recognition) {
        if (!initSpeechRecognition()) {
            return;
        }
    }
    
    if (!isListening) {
        // リスニング開始
        await startRecording();
        recognition.start();
        isListening = true;
        
        elements.micButton.classList.add('active');
        elements.micButton.innerHTML = `
            <span class="text-2xl">🎤</span>
            <div class="text-sm mt-1">STOP LISTENING</div>
        `;
        elements.micButton.classList.remove('bg-red-600', 'hover:bg-red-700');
        elements.micButton.classList.add('bg-green-600', 'hover:bg-green-700');
    } else {
        // リスニング停止
        recognition.stop();
        if (isRecording && mediaRecorder) {
            mediaRecorder.stop();
        }
        isListening = false;
        
        elements.micButton.classList.remove('active');
        elements.micButton.innerHTML = `
            <span class="text-2xl">🎤</span>
            <div class="text-sm mt-1">START LISTENING</div>
        `;
        elements.micButton.classList.remove('bg-green-600', 'hover:bg-green-700');
        elements.micButton.classList.add('bg-red-600', 'hover:bg-red-700');
    }
}

// ========== システムリセット ==========
async function resetSystem() {
    if (confirm('システムをリセットしますか？')) {
        try {
            await fetch('/api/reset', { method: 'POST' });
            updateSyncRate(0);
            updateSpeaker('UNKNOWN');
            elements.conversationLog.innerHTML = '<div class="text-gray-600 text-sm text-center py-8">No conversation history yet.</div>';
            startTime = Date.now();
            console.log('🔄 システムリセット完了');
        } catch (error) {
            console.error('❌ リセットエラー:', error);
        }
    }
}

// ========== ログクリア ==========
function clearLog() {
    elements.conversationLog.innerHTML = '<div class="text-gray-600 text-sm text-center py-8">No conversation history yet.</div>';
    console.log('🗑️ ログクリア完了');
}
