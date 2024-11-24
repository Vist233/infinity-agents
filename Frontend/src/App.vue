<template>
  <div class="app-container">
    <!-- 左侧对话页面 -->
    <div class="chat-section">
      <div class="chat-messages" ref="chatMessages">
        <!-- 气泡样式的消息框 -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.type]"
        >
          <div class="bubble">{{ msg.text }}</div>
        </div>
      </div>
      <!-- 输入框 -->
      <div class="chat-input">
        <input
          v-model="userInput"
          type="text"
          placeholder="输入内容..."
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage">发送</button>
      </div>
    </div>

    <!-- 右侧功能区 -->
    <div class="side-section">
      <!-- 文件上传区 -->
      <div class="file-upload">
        <h3>FILES:</h3>
        <input type="file" @change="handleFileUpload" />
        <ul>
          <li v-for="(file, index) in uploadedFiles" :key="index">{{ file.name }}</li>
        </ul>
      </div>
      <!-- 调试信息区 -->
      <div class="debug-logger">
        <h3>LOG:</h3>
        <p v-for="(log, index) in logger" :key="index">{{ log }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AIChatAgent",
  data() {
    return {
      messages: [], // 聊天记录
      userInput: "", // 用户输入
      uploadedFiles: [], // 上传的文件
      logger: ["系统初始化完成"], // Logger 信息
    };
  },
  methods: {
    // 发送消息
    sendMessage() {
      if (this.userInput.trim()) {
        this.messages.push({ type: "user", text: this.userInput });
        this.logger.push(`用户发送: ${this.userInput}`);
        this.userInput = ""; // 清空输入框

        // 模拟 AI 回复
        setTimeout(() => {
          const aiResponse = "这是 AI 的回复。";
          this.messages.push({ type: "ai", text: aiResponse });
          this.logger.push(`AI 回复: ${aiResponse}`);
        }, 1000);
      }
    },
    // 处理文件上传
    handleFileUpload(event) {
      const files = event.target.files;
      for (let i = 0; i < files.length; i++) {
        this.uploadedFiles.push(files[i]);
        this.logger.push(`上传文件: ${files[i].name}`);
      }
    },
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background-color: #1e1e1e;
  color: white;
  font-family: Arial, sans-serif;
}

/* 左侧聊天区域 */
.chat-section {
  flex: 3;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #333;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  display: flex;
  margin-bottom: 15px;
}

.message.user {
  justify-content: flex-end;
}

.message.ai {
  justify-content: flex-start;
}

.bubble {
  max-width: 60%;
  padding: 10px 15px;
  border-radius: 20px;
  background-color: #333;
  color: white;
  word-wrap: break-word;
}

.message.user .bubble {
  background-color: #262726;
}

.message.ai .bubble {
  background-color: #262726;
}

.chat-input {
  display: flex;
  padding: 10px;
  background-color: #333;
  border-top: 1px solid #444;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  background-color: #444;
  border: none;
  color: white;
  border-radius: 5px 0 0 5px;
}

.chat-input button {
  padding: 10px;
  background-color: #000000;
  border: none;
  color: white;
  border-radius: 0 5px 5px 0;
  cursor: pointer;
}

.chat-input button:hover {
  background-color: #000000;
}

/* 右侧功能区 */
.side-section {
  flex: 2;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.file-upload,
.debug-logger {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  background-color: #333;
  border-radius: 5px;
  overflow-y: auto;
}

.file-upload h3,
.debug-logger h3 {
  margin-bottom: 10px;
  border-bottom: 1px solid #444;
  padding-bottom: 5px;
}

.file-upload ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.file-upload li {
  margin: 5px 0;
  font-size: 14px;
}

.debug-logger p {
  font-size: 13px;
  margin: 5px 0;
}
</style>
