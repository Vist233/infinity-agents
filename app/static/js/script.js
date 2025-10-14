document.addEventListener("DOMContentLoaded", () => {
  // Configure marked
  marked.setOptions({
    breaks: true,
    gfm: true,
  });

  // Render initial markdown content loaded from session
  renderAllMarkdown();

  // --- SocketIO Setup ---
  const socket = io(); // Connect to the server
  // --- DOM Elements ---
  // Chat Elements
  const messageForm = document.getElementById('messageForm');
  const userInput = document.getElementById('userInput');
  const agentSelect = document.getElementById('agentSelect');
  const messageArea = document.getElementById('messageArea');
  const sendButton = document.getElementById('sendButton');
  const stopButton = document.getElementById('stopButton'); // Get stop button
  const welcomeBanner = document.getElementById('welcomeBanner');
  const welcomeClose = document.getElementById('welcomeClose');

  // --- State Variables ---
  let currentAiMessageId = null; // Variable to store the ID of the message being generated

  // --- Helper Functions ---

  // Scroll chat area to bottom
  function scrollToBottom() {
    if (messageArea) {
      messageArea.scrollTop = messageArea.scrollHeight;
    }
  }

  // Render markdown in a specific element
  function renderMarkdownInElement(element, isFinal = false) {
    const rawMarkdown = element.dataset.rawMarkdown ?? element.textContent ?? '';
    if (!element.classList.contains('message-complete') || isFinal) {
      element.innerHTML = marked.parse(rawMarkdown);
    }
  }

  // Render markdown in all elements with the .markdown-content class
  function renderAllMarkdown() {
    const markdownElements = document.querySelectorAll('.markdown-content');
    markdownElements.forEach(element => {
      renderMarkdownInElement(element);
    });
  }

  function dismissWelcomeBanner(options = {}) {
    if (!welcomeBanner || welcomeBanner.dataset.dismissed === 'true') {
      return;
    }
    const immediate = options.immediate ?? false;
    welcomeBanner.dataset.dismissed = 'true';
    if (immediate) {
      welcomeBanner.style.display = 'none';
    } else {
      welcomeBanner.classList.add('hidden');
      setTimeout(() => {
        if (welcomeBanner) {
          welcomeBanner.style.display = 'none';
        }
      }, 200);
    }
  }

  // Appends a message bubble to the chat area
  function appendMessage(type, text, id = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', type);

    const bubbleDiv = document.createElement('div');
    bubbleDiv.classList.add('bubble');
    if (type === 'ai') {
      bubbleDiv.classList.add('markdown-content');
      if (id) {
        bubbleDiv.id = id; // Assign the unique ID
      }
    }
    bubbleDiv.textContent = text; // Set initial text

    messageDiv.appendChild(bubbleDiv);
    messageArea.appendChild(messageDiv);    // Render markdown immediately if it's an AI message
    if (type === 'ai') {
      renderMarkdownInElement(bubbleDiv);
    }
  }

  function sanitizeChunk(chunk) {
    if (chunk === null || chunk === undefined) {
      return '';
    }
    const normalized = typeof chunk === 'string' ? chunk : String(chunk);
    if (normalized.trim().toLowerCase() === 'none') {
      return '';
    }
    return normalized;
  }
  // --- Event Listeners ---
  if (welcomeClose) {
    welcomeClose.addEventListener('click', () => dismissWelcomeBanner());
  }

  // Chat Form Submission
  messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const messageText = userInput.value.trim();
    const agent = agentSelect.value;

    if (messageText && sendButton.style.display !== 'none') {
      dismissWelcomeBanner();
      appendMessage('user', messageText);
      scrollToBottom();
      socket.emit('send_message', { userInput: messageText, agent: agent });
      userInput.value = '';
    }
  });
  // Stop Generation Button
  stopButton.addEventListener('click', () => {
    if (currentAiMessageId) {
      console.log(`Requesting stop for message ID: ${currentAiMessageId}`);
      socket.emit('stop_generation', { id: currentAiMessageId });
    }
  });

  // --- SocketIO Event Listeners ---

  socket.on('connect', () => {
    console.log('Connected to server via WebSocket');
  });

  socket.on('disconnect', () => {
    console.log('Disconnected from server');
  });

  socket.on('error_message', (data) => {
    console.error('Server Error:', data.error);
    appendMessage('error', `Error: ${data.error}`);
    scrollToBottom();
  });

  socket.on('ai_message_start', (data) => {
    console.log('AI message start:', data.id);
    currentAiMessageId = data.id;
    dismissWelcomeBanner();
    stopButton.style.display = 'inline-block';
    sendButton.style.display = 'none';
    appendMessage('ai', '', data.id);
    const aiBubble = document.getElementById(data.id);
    if (aiBubble) {
      aiBubble.dataset.rawMarkdown = '';
    }
    scrollToBottom();
  });

  socket.on('ai_message_chunk', (data) => {
    const aiBubble = document.getElementById(data.id);
    if (aiBubble) {
      const safeChunk = sanitizeChunk(data.chunk);
      if (safeChunk) {
        aiBubble.dataset.rawMarkdown = (aiBubble.dataset.rawMarkdown || '') + safeChunk;
        renderMarkdownInElement(aiBubble);
      }
      scrollToBottom();
    } else {
      console.warn(`Could not find AI message bubble with ID: ${data.id}`);
    }
  });

  socket.on('ai_message_end', (data) => {
    console.log('AI message end:', data.id);
    const aiBubble = document.getElementById(data.id);
    if (aiBubble) {
      renderMarkdownInElement(aiBubble, true);
      aiBubble.classList.add('message-complete');
    }
    stopButton.style.display = 'none';
    sendButton.style.display = 'inline-block';
    currentAiMessageId = null;
    scrollToBottom();
  });
  // --- Initial Setup Calls ---
  renderAllMarkdown();
  if (messageArea && messageArea.children.length > 0) {
    dismissWelcomeBanner({ immediate: true });
  }
  scrollToBottom();
});
