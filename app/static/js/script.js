document.addEventListener("DOMContentLoaded", () => {
  const messageArea = document.getElementById("messageArea");
  const userInput = document.getElementById("userInput");
  const sendButton = document.getElementById("sendButton");
  const fileInput = document.getElementById("fileInput");
  const fileList = document.getElementById("fileList");
  const logArea = document.getElementById("logArea");

  const logger = ["系统初始化完成"];
  const messages = [];

  // 更新日志
  function log(message) {
    logger.push(message);
    const logItem = document.createElement("div");
    logItem.textContent = message;
    logItem.classList.add("text-white-50");
    logArea.appendChild(logItem);
    logArea.scrollTop = logArea.scrollHeight;
  }

  // 添加消息
  function addMessage(type, text) {
    messages.push({ type, text });

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", type);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.textContent = text;

    messageDiv.appendChild(bubble);
    messageArea.appendChild(messageDiv);
    messageArea.scrollTop = messageArea.scrollHeight;
  }

  // 发送消息
  function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage("user", text);
    log(`用户发送: ${text}`);
    userInput.value = "";

    // 模拟 AI 回复
    setTimeout(() => {
      const aiResponse = "这是 AI 的回复。";
      addMessage("ai", aiResponse);
      log(`AI 回复: ${aiResponse}`);
    }, 1000);
  }

  // 处理文件上传
  function handleFileUpload(event) {
    const files = event.target.files;
    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // 添加到文件列表
      const fileItem = document.createElement("li");
      fileItem.textContent = file.name;
      fileItem.classList.add("list-group-item");
      fileList.appendChild(fileItem);

      log(`上传文件: ${file.name}`);
    }
  }

  // 绑定事件
  sendButton.addEventListener("click", sendMessage);
  userInput.addEventListener("keyup", (e) => {
    if (e.key === "Enter") sendMessage();
  });
  fileInput.addEventListener("change", handleFileUpload);

  // 初始化日志
  logArea.textContent = logger.join("\n");
});
