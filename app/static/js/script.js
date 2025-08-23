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
  function renderMarkdownInElement(element) {
    const rawMarkdown = element.dataset.rawMarkdown || element.textContent || '';
    if (!element.classList.contains('message-complete') || event.type === 'ai_message_end') {
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
  // --- Event Listeners ---

  // Chat Form Submission
  messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const messageText = userInput.value.trim();
    const agent = agentSelect.value;

    if (messageText && sendButton.style.display !== 'none') {
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
      aiBubble.dataset.rawMarkdown += data.chunk;
      renderMarkdownInElement(aiBubble);
      scrollToBottom();
    } else {
      console.warn(`Could not find AI message bubble with ID: ${data.id}`);
    }
  });

  socket.on('ai_message_end', (data) => {
    console.log('AI message end:', data.id);
    const aiBubble = document.getElementById(data.id);
    if (aiBubble) {
      renderMarkdownInElement(aiBubble);
      aiBubble.classList.add('message-complete');
    }
    stopButton.style.display = 'none';
    sendButton.style.display = 'inline-block';
    currentAiMessageId = null;
    scrollToBottom();
  });
  // --- Initial Setup Calls ---
  renderAllMarkdown();
  scrollToBottom();
});