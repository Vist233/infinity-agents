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
  const viewToggles = document.querySelectorAll('.view-toggle');
  const viewPanels = document.querySelectorAll('.view-panel');
  const chatPanel = document.getElementById('chat-panel');
  const packagerPanel = document.getElementById('packager-panel');

  // Trait packager elements
  const traitImageInput = document.getElementById('traitImageInput');
  const traitImageLabel = document.getElementById('traitImageLabel');
  const traitPreviewBox = document.getElementById('traitPreviewBox');
  const traitImagePreview = document.getElementById('traitImagePreview');
  const clearTraitImage = document.getElementById('clearTraitImage');
  const generateExeButton = document.getElementById('generateExeButton');
  const packagerStatus = document.getElementById('packagerStatus');
  const packagerProgress = document.getElementById('packagerProgress');
  const packagerProgressFill = document.getElementById('packagerProgressFill');

  // --- State Variables ---
  let currentAiMessageId = null; // Variable to store the ID of the message being generated
  let currentView = 'chat-panel';
  const packagerState = {
    traitDataUrl: null,
    traitExt: null
  };
  let progressTimer = null;

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

  function activateView(targetId) {
    if (!targetId || currentView === targetId) {
      return;
    }
    currentView = targetId;
    viewToggles.forEach(button => {
      const isTarget = button.dataset.target === targetId;
      button.classList.toggle('active', isTarget);
      button.setAttribute('aria-pressed', isTarget ? 'true' : 'false');
    });
    viewPanels.forEach(panel => {
      const isTarget = panel.id === targetId;
      panel.classList.toggle('active', isTarget);
      if (isTarget) {
        panel.removeAttribute('hidden');
      } else {
        panel.setAttribute('hidden', 'true');
      }
    });
    if (targetId === 'chat-panel') {
      scrollToBottom();
    }
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

  function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error);
      reader.readAsDataURL(file);
    });
  }

  function resetTraitImage() {
    packagerState.traitDataUrl = null;
    packagerState.traitExt = null;
    if (traitImageInput) {
      traitImageInput.value = '';
    }
    if (traitPreviewBox) {
      traitPreviewBox.hidden = true;
    }
    if (traitImagePreview) {
      traitImagePreview.removeAttribute('src');
    }
    if (traitImageLabel) {
      traitImageLabel.textContent = '选择或拖拽图片';
    }
    if (packagerStatus) {
      packagerStatus.textContent = '请先上传性状示例图。';
    }
    updateProgressFill(0);
    if (packagerProgress) {
      packagerProgress.hidden = true;
    }
    clearProgressTimer();
  }

  function showProgress() {
    clearProgressTimer();
    if (packagerProgress) {
      packagerProgress.hidden = false;
    }
    updateProgressFill(8);
    progressTimer = window.setInterval(() => {
      if (!packagerProgressFill) {
        return;
      }
      const currentWidth = parseFloat(packagerProgressFill.dataset.progress || '0');
      if (currentWidth >= 90) {
        return;
      }
      const nextWidth = Math.min(90, currentWidth + Math.random() * 6);
      updateProgressFill(nextWidth);
    }, 800);
  }

  function updateProgressFill(value) {
    if (!packagerProgressFill) {
      return;
    }
    const clamped = Math.max(0, Math.min(100, value));
    packagerProgressFill.style.width = `${clamped}%`;
    packagerProgressFill.dataset.progress = String(clamped);
  }

  function completeProgress(success = true) {
    clearProgressTimer();
    updateProgressFill(success ? 100 : 0);
    if (packagerProgress) {
      if (success) {
        window.setTimeout(() => {
          packagerProgress.hidden = true;
          updateProgressFill(0);
        }, 1200);
      } else {
        window.setTimeout(() => {
          packagerProgress.hidden = true;
          updateProgressFill(0);
        }, 1600);
      }
    }
  }

  function clearProgressTimer() {
    if (progressTimer) {
      window.clearInterval(progressTimer);
      progressTimer = null;
    }
  }

  // --- Event Listeners ---
  viewToggles.forEach(button => {
    button.addEventListener('click', () => activateView(button.dataset.target));
  });

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

  if (traitImageInput) {
    traitImageInput.addEventListener('change', async (event) => {
      const file = event.target.files && event.target.files[0];
      if (!file) {
        resetTraitImage();
        return;
      }
      const ext = (file.name.split('.').pop() || '').toLowerCase();
      try {
        const dataUrl = await readFileAsDataURL(file);
        packagerState.traitDataUrl = dataUrl;
        packagerState.traitExt = ext || 'jpeg';
        if (traitImagePreview) {
          traitImagePreview.src = dataUrl;
        }
        if (traitPreviewBox) {
          traitPreviewBox.hidden = false;
        }
        if (traitImageLabel) {
          traitImageLabel.textContent = file.name;
        }
        if (packagerStatus) {
          packagerStatus.textContent = `已选择性状图：${file.name}`;
        }
      } catch (error) {
        console.error('Failed to read trait image:', error);
        resetTraitImage();
        if (packagerStatus) {
          packagerStatus.textContent = '读取性状示例图失败，请重试。';
        }
      }
    });
  }

  if (clearTraitImage) {
    clearTraitImage.addEventListener('click', () => {
      resetTraitImage();
      if (packagerStatus) {
        packagerStatus.textContent = '已移除性状示例图。';
      }
    });
  }

  async function generateExecutable() {
    if (!packagerState.traitDataUrl || !packagerState.traitExt) {
      if (packagerStatus) {
        packagerStatus.textContent = '请先上传性状示例图。';
      }
      return;
    }
    if (generateExeButton) {
      generateExeButton.disabled = true;
    }
    if (packagerStatus) {
      packagerStatus.textContent = '正在生成可执行文件，请稍候...';
    }
    showProgress();

    try {
      const payload = {
        trait_image_base64: packagerState.traitDataUrl,
        trait_image_ext: packagerState.traitExt
      };

      const response = await fetch('/generate_exe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        let errorDetails = '';
        try {
          const errorJson = await response.json();
          errorDetails = errorJson.error || errorJson.details || '';
        } catch (jsonError) {
          console.warn('Failed to parse error JSON:', jsonError);
          errorDetails = response.statusText;
        }
        throw new Error(errorDetails || `请求失败，状态码 ${response.status}`);
      }

      const disposition = response.headers.get('content-disposition') || '';
      let downloadName = 'traitRecognizePackager.exe';
      const filenameMatch = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)["']?/i);
      if (filenameMatch && filenameMatch[1]) {
        downloadName = decodeURIComponent(filenameMatch[1]);
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = downloadName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);

      if (packagerStatus) {
        packagerStatus.textContent = `生成成功，已下载 ${downloadName}`;
      }
      completeProgress(true);
    } catch (error) {
      console.error('Failed to generate executable:', error);
      if (packagerStatus) {
        packagerStatus.textContent = `生成失败：${error.message || '请检查网络或稍后重试'}`;
      }
      completeProgress(false);
    } finally {
      if (generateExeButton) {
        generateExeButton.disabled = false;
      }
      clearProgressTimer();
    }
  }

  if (generateExeButton && packagerStatus) {
    generateExeButton.addEventListener('click', generateExecutable);
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
  activateView('chat-panel');
  scrollToBottom();
});
