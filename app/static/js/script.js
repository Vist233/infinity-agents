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
  const statusArea = document.getElementById('statusArea');

  // RAG Elements
  const fileInput = document.getElementById('fileInput');
  const selectFileButton = document.getElementById('selectFileButton');
  const uploadButton = document.getElementById('uploadButton');
  const clearRagButton = document.getElementById('clearRagButton');
  let selectedFile = null; // For RAG file

  // Sidebar Elements
  const traitSidebar = document.getElementById('traitSidebar');
  const toggleSidebarButton = document.getElementById('toggleSidebarButton');
  const closeSidebarButton = document.getElementById('closeSidebarButton');

  // Trait Recognizer Elements (inside sidebar)
  const traitFileInput = document.getElementById('traitFileInput');
  const traitStatus = document.getElementById('traitStatus');
  const traitError = document.getElementById('traitError');
  const traitUploadLabel = document.querySelector('.trait-upload-label span');
  const programsList = document.getElementById('programsList');

  // --- State Variables ---
  let currentAiMessageId = null; // Variable to store the ID of the message being generated

  // --- Helper Functions ---

  // Scroll chat area to bottom
  function scrollToBottom() {
    messageArea.scrollTop = messageArea.scrollHeight;
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
    messageArea.appendChild(messageDiv);

    // Render markdown immediately if it's an AI message
    if (type === 'ai') {
      renderMarkdownInElement(bubbleDiv);
    }
  }

  // Function to display RAG status messages
  function showStatus(message, type = 'info') {
    statusArea.textContent = message;
    statusArea.className = `status-area status-${type}`; // Add class for styling
  }

  // Function to display Trait Recognizer status/error messages
  function showTraitStatus(message, isError = false) {
      if (isError) {
          traitError.textContent = message;
          traitError.style.display = 'block';
          traitStatus.textContent = ''; // Clear status
      } else {
          traitStatus.innerHTML = message; // Allow HTML for loading spinner
          traitError.style.display = 'none';
      }
  }

  // --- Event Listeners ---

  // Sidebar Toggle
  toggleSidebarButton.addEventListener('click', () => {
    traitSidebar.classList.toggle('open');
    document.body.classList.toggle('sidebar-open'); // Optional: for body styling adjustments
  });

  closeSidebarButton.addEventListener('click', () => {
    traitSidebar.classList.remove('open');
    document.body.classList.remove('sidebar-open');
  });

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

  // RAG File Selection Trigger
  selectFileButton.addEventListener('click', () => {
    fileInput.click();
  });

  // RAG File Selection Handling
  fileInput.addEventListener('change', (event) => {
    selectedFile = event.target.files[0];
    if (selectedFile) {
      uploadButton.disabled = false;
      showStatus(`Selected: ${selectedFile.name}`, 'info');
    } else {
      uploadButton.disabled = true;
      showStatus('');
    }
  });

  // RAG File Upload
  uploadButton.addEventListener('click', async () => {
    if (!selectedFile) {
      showStatus('No file selected!', 'error');
      return;
    }
    const formData = new FormData();
    formData.append('file', selectedFile);
    showStatus(`Uploading ${selectedFile.name}...`, 'info');
    uploadButton.disabled = true;

    try {
      const response = await fetch('/upload', { method: 'POST', body: formData });
      const result = await response.json();
      if (response.ok && result.success) {
        showStatus(`✅ ${selectedFile.name} processed. RAG active for Chater.`, 'success');
        fileInput.value = '';
        selectedFile = null;
      } else {
        showStatus(`❌ Error: ${result.error || 'Upload failed'}`, 'error');
      }
    } catch (error) {
      console.error('Upload error:', error);
      showStatus(`❌ Network or server error during upload.`, 'error');
    } finally {
      uploadButton.disabled = true; // Keep disabled after attempt
    }
  });

  // Clear RAG Context
  clearRagButton.addEventListener('click', async () => {
    showStatus('Clearing RAG context...', 'info');
    try {
      const response = await fetch('/clear_rag', { method: 'POST' });
      const result = await response.json();
      if (response.ok && result.success) {
        showStatus('RAG context cleared.', 'success');
      } else {
        showStatus('Failed to clear RAG context.', 'error');
      }
    } catch (error) {
      console.error('Clear RAG error:', error);
      showStatus('Error clearing RAG context.', 'error');
    }
  });

  // --- Trait Recognizer Event Listeners ---

  // Trait Recognizer File Input Change
  traitFileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) {
          traitUploadLabel.textContent = '选择标准图片';
          showTraitStatus('请选择一张图片文件。');
          return;
      }

      if (!file.type.startsWith('image/')) {
          showTraitStatus('错误：请选择图片文件 (PNG, JPG, JPEG)。', true);
          traitFileInput.value = ''; // Reset file input
          traitUploadLabel.textContent = '选择标准图片';
          return;
      }

      traitUploadLabel.textContent = `已选: ${file.name}`;
      showTraitStatus('<div class="loading"></div> 上传并生成程序... (可能需1-2分钟)');

      const formData = new FormData();
      formData.append('file', file);

      try {
          const response = await fetch('/upload_trait_standard', {
              method: 'POST',
              body: formData
          });

          if (!response.ok) {
              let errorText = `HTTP error ${response.status}`;
              try {
                  const errorData = await response.json();
                  errorText = errorData.error || errorText;
              } catch (jsonError) {
                  errorText = await response.text() || errorText;
              }
              if (errorText.length > 200) {
                  errorText = errorText.substring(0, 200) + "...";
              }
              throw new Error(errorText);
          }

          const blob = await response.blob();
          const contentDisposition = response.headers.get('Content-Disposition');
          let filename = 'spade.exe'; // Default filename
          if (contentDisposition) {
              const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
              if (filenameMatch && filenameMatch.length > 1) {
                  filename = filenameMatch[1];
              }
          }

          const downloadUrl = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = downloadUrl;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(downloadUrl);
          document.body.removeChild(a);

          showTraitStatus(`✅ 程序 '${filename}' 生成成功并已下载。`);
          setTimeout(() => {
              showTraitStatus('可选择新图片再次生成。');
              traitUploadLabel.textContent = '选择标准图片';
          }, 5000);

      } catch (err) {
          console.error("Trait Upload/Generation Error:", err);
          showTraitStatus(`生成失败：${err.message}`, true);
          traitUploadLabel.textContent = '选择标准图片';
      } finally {
          traitFileInput.value = ''; // Reset file input
      }
  });

  // Function to load fixed programs (called on page load now)
  async function loadFixedPrograms() {
      programsList.innerHTML = '<div class="loading-text"><div class="loading"></div> 加载预置程序...</div>';
      try {
          const response = await fetch('/get_fixed_programs');
          const data = await response.json();

          if (!response.ok || !data.success) {
              programsList.innerHTML = `<div class="error-text">加载失败: ${data.error || '无法连接服务器'}</div>`;
              return;
          }

          if (data.programs && data.programs.length > 0) {
              programsList.innerHTML = data.programs.map(prog => `
                  <div class="program-item">
                      <span class="program-name" title="${prog}">${prog}</span>
                      <button class="download-btn" data-filename="${prog}">
                          下载
                      </button>
                  </div>
              `).join('');
              // Add event listeners to new download buttons
              programsList.querySelectorAll('.download-btn').forEach(button => {
                  button.addEventListener('click', () => {
                      downloadFixedProgram(button.dataset.filename);
                  });
              });
          } else {
              programsList.innerHTML = '<div class="loading-text">没有找到预置程序。</div>';
          }
      } catch (err) {
          console.error("Load Fixed Programs Error:", err);
          programsList.innerHTML = `<div class="error-text">加载失败: ${err.message}</div>`;
      }
  }

  // Function to download a fixed program
  function downloadFixedProgram(filename) {
      window.open(`/download_fixed/${encodeURIComponent(filename)}`, '_blank');
  }

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
  loadFixedPrograms(); // Load fixed programs when the page loads
});