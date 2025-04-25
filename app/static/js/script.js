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

  const messageForm = document.getElementById('messageForm');
  const userInput = document.getElementById('userInput');
  const agentSelect = document.getElementById('agentSelect');
  const messageArea = document.getElementById('messageArea');

  // Scroll to bottom function
  function scrollToBottom() {
    messageArea.scrollTop = messageArea.scrollHeight;
  }

  // Initial scroll to bottom
  scrollToBottom();

  // Handle form submission
  messageForm.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevent traditional form submission
    const messageText = userInput.value.trim();
    const agent = agentSelect.value;

    if (messageText) {
      // Emit the message to the server
      socket.emit('send_message', { userInput: messageText, agent: agent });

      // Clear input field
      userInput.value = '';
    }
  });

  // --- SocketIO Event Listeners ---

  socket.on('connect', () => {
    console.log('Connected to server via WebSocket');
  });

  socket.on('disconnect', () => {
    console.log('Disconnected from server');
    // Optionally display a message to the user
  });

  socket.on('error_message', (data) => {
    console.error('Server Error:', data.error);
    // Display error to the user (e.g., in a temporary div or alert)
    appendMessage('error', `Error: ${data.error}`);
  });

  // Handle user message confirmation from server (optional, good for consistency)
  socket.on('user_message', (data) => {
    console.log('User message confirmed:', data.text);
    appendMessage('user', data.text);
    scrollToBottom();
  });

  // Handle start of AI message stream
  socket.on('ai_message_start', (data) => {
    console.log('AI message start:', data.id);
    // Create a placeholder for the AI message
    appendMessage('ai', '', data.id); // Pass ID to identify the bubble
    scrollToBottom();
  });

  // Handle incoming AI message chunks
  socket.on('ai_message_chunk', (data) => {
    // console.log('AI message chunk:', data.id, data.chunk);
    const aiBubble = document.getElementById(data.id);
    if (aiBubble) {
      // Append the chunk and re-render markdown for this bubble
      aiBubble.textContent += data.chunk; // Use textContent for raw appending
      renderMarkdownInElement(aiBubble); // Re-render markdown
      scrollToBottom(); // Keep scrolled to bottom as content grows
    } else {
      console.warn(`Could not find AI message bubble with ID: ${data.id}`);
    }
  });

   // Handle end of AI message stream
   socket.on('ai_message_end', (data) => {
    console.log('AI message end:', data.id);
    const aiBubble = document.getElementById(data.id);
    if (aiBubble) {
      // Final render to ensure everything is correct
      renderMarkdownInElement(aiBubble);
      // Optionally add a class or attribute to indicate completion
      aiBubble.classList.add('message-complete');
    }
     scrollToBottom();
  });


  // --- Helper Functions ---

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
    bubbleDiv.textContent = text; // Set initial text (will be replaced by markdown rendering if needed)

    messageDiv.appendChild(bubbleDiv);
    messageArea.appendChild(messageDiv);

    // Render markdown immediately if it's an AI message (or user if needed)
    if (type === 'ai') {
      renderMarkdownInElement(bubbleDiv);
    }
  }

  // Renders markdown within a specific element
  function renderMarkdownInElement(element) {
    // Use textContent to get the raw markdown, avoiding potential HTML injection
    const rawMarkdown = element.textContent || '';
    // Only render if it hasn't been marked as fully rendered by the streaming end event
    if (!element.classList.contains('message-complete')) {
        element.innerHTML = marked.parse(rawMarkdown);
        element.dataset.rendered = 'true'; // Mark as rendered (might be overwritten by stream)
    } else {
        // If message is complete, ensure final render uses the full text
        // This handles cases where the last chunk might not have triggered a render
        const finalMarkdown = element.textContent || ''; // Get potentially updated text content
        element.innerHTML = marked.parse(finalMarkdown);
    }
  }

  // Renders markdown in all elements with the .markdown-content class
  function renderAllMarkdown() {
    const markdownElements = document.querySelectorAll('.markdown-content');
    markdownElements.forEach(element => {
      renderMarkdownInElement(element);
    });
  }

  // --- MutationObserver (Optional - might not be needed with direct updates) ---
  // If dynamic additions outside of the socket handlers occur, this might be useful.
  // For now, direct updates in socket handlers are likely sufficient.
  /*
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(mutation => {
      if (mutation.addedNodes.length > 0) {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === 1 && node.querySelector('.markdown-content')) {
            renderAllMarkdown(); // Re-render if new messages with markdown are added
            scrollToBottom();
          } else if (node.nodeType === 1 && node.classList.contains('markdown-content')) {
             renderMarkdownInElement(node);
             scrollToBottom();
          }
        });
      }
    });
  });
  observer.observe(messageArea, { childList: true });
  */
});