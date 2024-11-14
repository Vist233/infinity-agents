<template>
  <div class="flex flex-col items-center h-screen bg-gray-100 p-4">
    <!-- Header -->
    <div class="w-full max-w-3xl">
      <h1 class="text-2xl font-bold text-center text-blue-600 mb-4">AI Agent Chat</h1>
    </div>

    <!-- Chat Container -->
    <div class="w-full max-w-3xl bg-white rounded-lg shadow-lg overflow-hidden flex flex-col flex-grow">
      <!-- Message Display Area -->
      <div class="flex-grow p-4 overflow-y-auto space-y-4" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="index" class="flex">
          <div
            :class="{
              'bg-blue-500 text-white self-end': message.sender === 'user',
              'bg-gray-200 text-black self-start': message.sender === 'agent'
            }"
            class="rounded-lg px-4 py-2 max-w-xs"
          >
            {{ message.text }}
          </div>
        </div>
      </div>

      <!-- File Upload & Input Area -->
      <div class="border-t p-4 flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-4">
        <!-- File Upload Button -->
        <input
          type="file"
          @change="handleFileUpload"
          class="hidden"
          ref="fileInput"
        />
        <button @click="triggerFileInput" class="px-4 py-2 bg-green-500 text-white rounded-lg shadow-md">
          上传文档/图片
        </button>

        <!-- Message Input -->
        <input
          v-model="userInput"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="输入消息..."
          class="flex-grow border border-gray-300 rounded-lg px-4 py-2 focus:outline-none"
        />
        <button @click="sendMessage" class="px-4 py-2 bg-blue-500 text-white rounded-lg shadow-md">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      messages: [
        { sender: 'agent', text: '您好！请问有什么我可以帮您的吗？' },
      ],
      userInput: '',
    };
  },
  methods: {
    sendMessage() {
      if (this.userInput.trim() === '') return;
      // 将用户的输入添加到消息列表
      this.messages.push({ sender: 'user', text: this.userInput });

      // 模拟 agent 的回复（可以用实际 API 调用来替代此部分）
      setTimeout(() => {
        this.messages.push({ sender: 'agent', text: '这是 AI 的回复内容。' });
        this.scrollToBottom();
      }, 1000);

      this.userInput = '';
      this.scrollToBottom();
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.messages.push({
          sender: 'user',
          text: `上传了文件：${file.name}`,
        });

        // 在这里可以添加上传文件到后台或 AI 的功能
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const messagesContainer = this.$refs.messagesContainer;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      });
    },
  },
};
</script>

<style scoped>
/* 统一页面背景色 */
body {
  background-color: #f7fafc;
  font-family: 'Arial', sans-serif;
  color: #333;
  margin: 0;
  padding: 0;
}

/* 页面容器 */
.flex {
  display: flex;
}
.flex-col {
  flex-direction: column;
}
.items-center {
  align-items: center;
}
.h-screen {
  height: 100vh;
}
.bg-gray-100 {
  background-color: #f7fafc;
}
.p-4 {
  padding: 1rem;
}

/* Header 样式 */
h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #2b6cb0;
  margin-bottom: 1rem;
  text-align: center;
}

/* Chat Container */
.bg-white {
  background-color: #ffffff;
}
.rounded-lg {
  border-radius: 0.75rem;
}
.shadow-lg {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.overflow-hidden {
  overflow: hidden;
}
.flex-grow {
  flex-grow: 1;
}

/* Message Display Area */
.p-4 {
  padding: 1rem;
}
.space-y-4 {
  margin-bottom: 1rem;
}
.overflow-y-auto {
  overflow-y: auto;
}
.flex {
  display: flex;
}
.self-end {
  align-self: flex-end;
}
.self-start {
  align-self: flex-start;
}
.bg-blue-500 {
  background-color: #4299e1;
}
.bg-gray-200 {
  background-color: #edf2f7;
}
.text-white {
  color: #ffffff;
}
.text-black {
  color: #2d3748;
}
.max-w-xs {
  max-width: 16rem;
}
.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}
.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}
.rounded-lg {
  border-radius: 0.5rem;
}

/* File Upload and Input Area */
.border-t {
  border-top: 1px solid #e2e8f0;
}
.space-y-2 {
  margin-bottom: 0.5rem;
}
.sm\:space-y-0 {
  margin-bottom: 0;
}
.sm\:space-x-4 {
  margin-right: 1rem;
}
.sm\:flex-row {
  flex-direction: row;
}
.sm\:items-center {
  align-items: center;
}

/* File Upload Button */
input[type="file"] {
  display: none;
}
button {
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease;
}

/* Upload Button */
button:hover {
  background-color: #38a169;
}

button:focus {
  outline: none;
}

button.bg-green-500 {
  background-color: #48bb78;
}

button.bg-blue-500 {
  background-color: #3182ce;
}

button:active {
  background-color: #2b6cb0;
}

/* Message Input Field */
input[type="text"] {
  border: 1px solid #e2e8f0;
  padding: 0.75rem;
  border-radius: 0.375rem;
  width: 100%;
  font-size: 1rem;
  margin-right: 0.5rem;
  transition: border-color 0.3s ease;
}

input[type="text"]:focus {
  outline: none;
  border-color: #3182ce;
}

input[type="text"]:placeholder {
  color: #a0aec0;
}

</style>

