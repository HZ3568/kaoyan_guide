<template>
  <div class="container" :class="{ dark: isDark }">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ collapsed: !isSidebarOpen }">
      <!-- 侧边栏头部 - 始终可见的切换按钮 -->
      <div class="sidebar-header" :class="{ collapsed: !isSidebarOpen }">
        <!-- 折叠/展开按钮 -->
        <button
          class="sidebar-toggle-btn"
          @click="toggleSidebar"
          title="折叠/展开侧边栏"
        >
          <el-icon v-if="isSidebarOpen"><Fold /></el-icon>
          <el-icon v-else><Expand /></el-icon>
        </button>

        <!-- 展开状态下的标题和新建按钮 -->
        <template v-if="isSidebarOpen">
          <h2>聊天记录</h2>
        </template>
      </div>

      <!-- 侧边栏内容 - 使用过渡动画 -->
      <transition name="sidebar-content">
        <div v-if="isSidebarOpen" class="chat-list">
          <button class="new-chat-btn" @click="createNewChat" title="新建聊天">
            <el-icon><Plus /></el-icon>
            <span>新建聊天</span>
          </button>
          <div
            v-for="(chat, index) in chats"
            :key="chat.id"
            class="chat-item"
            :class="{ active: index === currentChatIndex }"
            @click="switchChat(index)"
          >
            <div class="chat-item-row">
              <span class="chat-title" v-if="editingChatId !== chat.id">
                {{ chat.title }}
              </span>
              <input
                v-else
                ref="renameInput"
                class="chat-rename-input"
                v-model="editingTitle"
                @click.stop
                @keydown.enter="confirmRename(chat)"
                @keydown.esc="cancelRename"
                @blur="confirmRename(chat)"
              />
              <div class="chat-actions">
                <button
                  class="icon-btn"
                  title="重命名"
                  @click.stop="startRename(chat)"
                >
                  <el-icon><Edit /></el-icon>
                </button>
                <button
                  class="icon-btn danger"
                  title="删除"
                  @click.stop="requestDeleteChat(index)"
                >
                  <el-icon><Delete /></el-icon>
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 主区域 -->
    <div class="main-area">
      <!-- 顶部标题栏 -->
      <div class="top-bar">
        <h2>{{ currentChat.title }}</h2>
        <button class="toggle-theme-btn" @click="toggleTheme">
          <el-icon v-if="!isDark"><Moon /></el-icon>
          <el-icon v-else><Sunny /></el-icon>
        </button>
      </div>

      <!-- 聊天内容区 -->
      <div class="chat-area" ref="chatArea">
        <div
          v-for="msg in currentChat.messages"
          :key="msg.id"
          class="message"
          :class="[
            msg.role === 'assistant' ? 'assistant' : 'user',
            msg.role === 'assistant' && msg.isStreaming ? 'typing' : '',
          ]"
        >
          <div class="avatar">
            <img
              :src="
                msg.role === 'assistant'
                  ? '/src/assets/imgs/bot-avatar.png'
                  : '/src/assets/imgs/user-avatar.png'
              "
              :alt="msg.role === 'assistant' ? '机器人' : '用户'"
            />
          </div>
          <div class="message-content">
            <div class="message-text">
              <!-- 统一结构：assistant 使用 Markdown + 光标；用户使用纯文本 -->
              <template v-if="msg.role === 'assistant'">
                <div
                  class="markdown-body"
                  v-html="renderMarkdown(msg.displayedText || msg.text)"
                ></div>
                <span
                  v-if="msg.isStreaming"
                  :class="['cursor', typingConfig?.paused ? 'paused' : '']"
                  >|</span
                >
              </template>
              <p v-else>{{ msg.text }}</p>
            </div>
            <div class="message-time">
              {{ formatTime(msg.timestamp) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入区 -->
      <div class="input-area" :style="floatingInputStyle">
        <div class="input-container">
          <textarea
            v-model="input"
            placeholder="输入你的问题..."
            @keydown.enter.prevent="sendMessage"
          ></textarea>
          <button
            class="send-btn"
            @click="sendMessage"
            :disabled="controller !== null"
          >
            <el-icon><Promotion /></el-icon>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import request from "@/utils/request";
import { marked } from "marked";
import DOMPurify from "dompurify";
import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import {
  Fold,
  Expand,
  Plus,
  Promotion,
  Moon,
  Sunny,
  Edit,
  Delete,
} from "@element-plus/icons-vue";

const isDark = ref(false);
const isSidebarOpen = ref(true); // 控制侧边栏展开/收起
const input = ref("");
const chatArea = ref(null);
let controller = null; // 用于取消请求的控制器
let typingIntervals = {}; // 每条消息独立的打字 interval

// 从本地存储加载聊天记录
const loadChatsFromLocalStorage = () => {
  const savedChats = localStorage.getItem("college-ai-chats");
  if (savedChats) {
    try {
      const parsedChats = JSON.parse(savedChats);
      if (Array.isArray(parsedChats) && parsedChats.length > 0) {
        return parsedChats;
      }
    } catch (e) {
      console.error("加载聊天记录失败:", e);
    }
  }
  return null;
};

// 初始化聊天记录
const chats = ref(
  loadChatsFromLocalStorage() || [
    {
      id: Date.now(),
      title: "院校咨询",
      messages: [
        {
          id: Date.now(),
          role: "assistant",
          text: "你好，我是院校咨询助手！请问有什么可以帮到你？",
          displayedText: "你好，我是院校咨询助手！请问有什么可以帮到你？",
          timestamp: new Date().toISOString(),
        },
      ],
    },
  ]
);

const currentChatIndex = ref(0);

// 当前聊天
const currentChat = computed(() => chats.value[currentChatIndex.value]);

// 固定底部输入框：根据侧栏展开状态动态设置左侧偏移
const floatingInputStyle = computed(() => ({
  left: isSidebarOpen.value ? "280px" : "60px",
  right: "0",
  bottom: "0",
}));

// 保存聊天记录到本地存储
const saveChatsToLocalStorage = () => {
  localStorage.setItem("college-ai-chats", JSON.stringify(chats.value));
};

// 重命名与删除：编辑状态
const editingChatId = ref(null);
const editingTitle = ref("");
const renameInput = ref(null);

function startRename(chat) {
  editingChatId.value = chat.id;
  editingTitle.value = chat.title || "";
  nextTick(() => {
    if (renameInput.value && typeof renameInput.value.focus === "function") {
      renameInput.value.focus();
      renameInput.value.select?.();
    }
  });
}

function confirmRename(chat) {
  if (!chat || editingChatId.value !== chat.id) return;
  const newTitle = (editingTitle.value || "").trim();
  if (!newTitle) {
    ElMessage.warning("名称不能为空");
    editingChatId.value = null;
    editingTitle.value = "";
    return;
  }
  chat.title = newTitle;
  editingChatId.value = null;
  editingTitle.value = "";
  saveChatsToLocalStorage();
  ElMessage.success("名称已更新");
}

function cancelRename() {
  editingChatId.value = null;
  editingTitle.value = "";
}

async function requestDeleteChat(index) {
  const chat = chats.value[index];
  if (!chat) return;
  try {
    await ElMessageBox.confirm(
      `确认删除该聊天「${chat.title || "未命名聊天"}」？此操作不可恢复。`,
      "删除确认",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    // 执行删除
    chats.value.splice(index, 1);

    // 调整当前选中索引
    if (chats.value.length === 0) {
      createNewChat();
      currentChatIndex.value = chats.value.length - 1;
    } else {
      if (currentChatIndex.value === index) {
        currentChatIndex.value = Math.max(0, index - 1);
      } else if (currentChatIndex.value > index) {
        currentChatIndex.value -= 1;
      }
    }

    saveChatsToLocalStorage();
    ElMessage.success("已删除");
  } catch (e) {
    // 用户取消
  }
}

// 切换主题
function toggleTheme() {
  isDark.value = !isDark.value;
  localStorage.setItem("darkMode", isDark.value);
}

// 切换侧边栏
function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value;
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight;
    }
  });
}

// 验证用户输入
const validateUserInput = (inputText) => {
  if (!inputText || inputText.trim() === "") {
    return { valid: false, message: "请输入消息内容" };
  }

  if (inputText.length > 500) {
    return { valid: false, message: "消息长度不能超过500字符" };
  }

  return { valid: true };
};

// 模拟逐字打印效果
const startTypingEffect = (msg) => {
  if (!msg.isStreaming) return;
  const len = msg.text.length;
  msg.displayedText = msg.displayedText || "";
  let i = msg.displayedText.length;

  if (i >= len) {
    msg.isStreaming = false;
    clearInterval(typingIntervals[msg.id]);
    return;
  }

  // 清除之前的interval以避免多个计时器同时运行
  if (typingIntervals[msg.id]) {
    clearInterval(typingIntervals[msg.id]);
  }

  // 根据文本长度动态调整打字速度，文本越长速度越快
  const typingSpeed = Math.max(5, Math.min(20, 20 - Math.floor(len / 100)));

  typingIntervals[msg.id] = setInterval(() => {
    if (i < len) {
      // 每次添加1-3个字符，加快显示速度
      const charsToAdd = Math.min(3, len - i);
      msg.displayedText += msg.text.substring(i, i + charsToAdd);
      i += charsToAdd;
      scrollToBottom();
    } else {
      msg.isStreaming = false;
      clearInterval(typingIntervals[msg.id]);
    }
  }, typingSpeed);
};

// 发送消息
async function sendMessage() {
  const inputText = input.value.trim();

  // 输入验证
  const validation = validateUserInput(inputText);
  if (!validation.valid || !inputText) {
    ElMessage.warning(validation.message || "请输入消息内容");
    return;
  }

  // 防止重复发送
  if (controller) {
    controller.abort();
  }
  controller = new AbortController();

  // 用户消息
  const userMsg = {
    id: Date.now(),
    role: "user",
    text: inputText,
    timestamp: new Date().toISOString(),
  };
  currentChat.value.messages.push(userMsg);
  input.value = "";
  scrollToBottom();

  // 机器人响应消息
  const assistantMsg = {
    id: Date.now() + 1,
    role: "assistant",
    text: "",
    displayedText: "",
    isStreaming: true,
    timestamp: new Date().toISOString(),
  };
  currentChat.value.messages.push(assistantMsg);
  scrollToBottom();

  // 保存聊天记录
  saveChatsToLocalStorage();

  try {
    // 添加调试输出，帮助定位问题
    console.log("开始发送消息:", inputText);
    console.log("聊天ID:", currentChat.value.id);

    // 设置超时
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5秒超时

    // 使用正确的API路径，添加/api前缀以便正确代理到后端
    // 读取本地登录信息，注入后端拦截器需要的 token
    const user = JSON.parse(localStorage.getItem("xm-user") || "{}");
    const token = user.token || "";

    const response = await fetch(
      `/api/chat?message=${encodeURIComponent(inputText)}&memoryId=${
        currentChat.value.id
      }`,
      {
        method: "GET",
        headers: {
          Accept: "text/html;charset=UTF-8",
          token: token,
        },
        signal: controller.signal,
      }
    );

    clearTimeout(timeoutId);

    // 添加更详细的错误处理
    if (!response.ok) {
      console.error("HTTP错误:", response.status, response.statusText);
      throw new Error(
        `HTTP error! status: ${response.status}, ${response.statusText}`
      );
    }

    console.log("收到响应:", response.status);

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    // 先清除之前的打字效果
    if (typingIntervals[assistantMsg.id]) {
      clearInterval(typingIntervals[assistantMsg.id]);
      typingIntervals[assistantMsg.id] = null;
    }

    // 开始流式处理
    console.log("开始流式处理响应");
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log("流式响应完成");
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      console.log("收到数据块:", chunk.length, "字节");
      buffer += chunk;

      // 直接更新内容
      assistantMsg.text = buffer;

      // 启动打字效果
      if (!typingIntervals[assistantMsg.id]) {
        typingIntervals[assistantMsg.id] = setInterval(() => {
          startTypingEffect(assistantMsg);
        }, 20); // 调整这个值可以改变打字速度
      }

      scrollToBottom();
      saveChatsToLocalStorage();
    }
  } catch (err) {
    if (err.name === "AbortError") {
      console.log("请求被用户中止或超时");
      // 统一以 Markdown 呈现超时信息
      const mdTimeout = [
        "### 请求超时",
        "- 原因：网络波动或后端响应缓慢",
        "- 建议：稍后重试或检查网络连接",
      ].join("\n");
      assistantMsg.text = mdTimeout;
      assistantMsg.displayedText = "";
      assistantMsg.isStreaming = true; // 继续通过打字效果显示Markdown内容
      ElMessage.warning("请求超时");
    } else {
      console.error("请求出错:", err);
      // 统一以 Markdown 呈现错误信息，移除非Markdown纯文本提示
      const mdError = [
        "### 请求失败",
        `- 类型：${err.name || "未知错误"}`,
        `- 信息：${err && err.message ? err.message : "无"}`,
        "- 建议：检查网络或稍后重试",
      ].join("\n");

      assistantMsg.text = mdError;
      assistantMsg.displayedText = "";
      assistantMsg.isStreaming = true; // 打字机渲染Markdown错误内容

      // 保留轻量提示，但删除冗余纯文本细节
      ElMessage.error("请求错误");

      // 移除将聊天标题改为纯文本的逻辑
      // if (currentChat.value.messages.length <= 2) {
      //   currentChat.value.title = "请求失败的聊天";
      // }

      saveChatsToLocalStorage();
    }
  } finally {
    const lastMessage =
      currentChat.value.messages[currentChat.value.messages.length - 1];
    lastMessage.isStreaming = false;

    // 确保所有字符都可见
    if (
      lastMessage.displayedText &&
      lastMessage.displayedText.length < lastMessage.text.length
    ) {
      lastMessage.displayedText = lastMessage.text;
    }

    controller = null;

    if (typingIntervals[assistantMsg.id]) {
      clearInterval(typingIntervals[assistantMsg.id]);
      typingIntervals[assistantMsg.id] = null;
    }

    scrollToBottom();
  }
}

// 新建聊天
function createNewChat() {
  const newId = Date.now();
  chats.value.push({
    id: newId,
    title: `新建聊天 ${chats.value.length + 1}`,
    messages: [
      {
        id: newId + 1,
        role: "assistant",
        text: "新聊天已创建，你好！我是院校咨询助手，请问有什么可以帮到你？",
        displayedText:
          "新聊天已创建，你好！我是院校咨询助手，请问有什么可以帮到你？",
        timestamp: new Date().toISOString(),
      },
    ],
  });
  currentChatIndex.value = chats.value.length - 1;
  saveChatsToLocalStorage();
  scrollToBottom();
}

// 切换聊天
function switchChat(index) {
  // 如果有正在进行的请求，取消它
  if (controller) {
    controller.abort();
    controller = null;
  }

  currentChatIndex.value = index;
  scrollToBottom();
}

// 初始化
onMounted(() => {
  // 暗黑模式
  isDark.value =
    localStorage.getItem("darkMode") === "true" ||
    (window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  // 如果没有聊天记录，创建默认聊天
  if (chats.value.length === 0) {
    createNewChat();
  }

  scrollToBottom();
});

// 格式化时间
function formatTime(timestamp) {
  if (!timestamp) return "";

  const date = new Date(timestamp);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();

  if (isToday) {
    return date.toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } else {
    return (
      date.toLocaleDateString("zh-CN", { month: "short", day: "numeric" }) +
      " " +
      date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })
    );
  }
}

// 监听聊天记录变化，自动滚动
watch(
  chats,
  () => {
    scrollToBottom();
    saveChatsToLocalStorage();
  },
  { deep: true }
);

// 高亮与换行配置
marked.setOptions({
  breaks: true,
  gfm: true,
  langPrefix: "hljs language-",
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
});

// 自定义渲染器：为链接增加安全属性，图片alt/title处理
const renderer = new marked.Renderer();
renderer.link = (href, title, text) => {
  const safeHref = DOMPurify.sanitize(href || "");
  const safeTitle = title ? DOMPurify.sanitize(title) : "";
  return `<a href="${safeHref}"${
    safeTitle ? ` title="${safeTitle}"` : ""
  } target="_blank" rel="noopener noreferrer">${text}</a>`;
};
renderer.image = (href, title, text) => {
  const safeSrc = DOMPurify.sanitize(href || "");
  const safeTitle = title ? DOMPurify.sanitize(title) : "";
  const safeAlt = text ? DOMPurify.sanitize(text) : "";
  return `<img src="${safeSrc}" alt="${safeAlt}"${
    safeTitle ? ` title="${safeTitle}"` : ""
  } />`;
};

function renderMarkdown(text) {
  const raw = marked.parse(text || "", { renderer });
  // 过滤潜在的恶意HTML，但保留必要的class属性用于高亮
  return DOMPurify.sanitize(raw, {
    ALLOWED_ATTR: [
      "href",
      "title",
      "target",
      "rel",
      "src",
      "alt",
      "class",
      "id",
      "align",
    ],
  });
}
</script>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
  color: #333;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background-color: #fff;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
  z-index: 10;
  position: relative;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  min-height: 60px;
}

.sidebar-header.collapsed {
  justify-content: center;
  padding: 16px 8px;
}

.new-chat-btn {
  background-color: #4caf50;
  color: #fff;
  border: none;
  height: 44px;
  width: 100%;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 15px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: background-color 0.2s, box-shadow 0.2s;
  margin-bottom: 8px;
}

.new-chat-btn:hover {
  background-color: #388e3c;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-item {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  flex-direction: column;
}

.chat-item:hover {
  background-color: #f0f0f0;
}

.chat-item.active {
  background-color: #e8f5e9;
  font-weight: 500;
}

.chat-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.chat-time {
  font-size: 12px;
  color: #757575;
}

/* 主区域样式 */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  position: relative;
  margin-left: 0;
}

/* 顶部标题栏 */
.top-bar {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 5;
}

.toggle-sidebar-btn,
.toggle-theme-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #555;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.toggle-sidebar-btn:hover,
.toggle-theme-btn:hover {
  background-color: #f0f0f0;
}

.top-bar h2 {
  margin: 0 auto 0 0;
  font-size: 18px;
  font-weight: 500;
}

/* 聊天内容区 */
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: #f9f9f9;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9e9e9e;
  font-size: 18px;
}

.message {
  display: flex;
  margin-bottom: 16px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.assistant {
  align-self: flex-start;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 12px;
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  display: flex;
  flex-direction: column;
}

.message-text {
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  word-break: break-word;
  line-height: 1.5;
}

.user .message-text {
  background-color: #dcf8c6;
  border-top-right-radius: 4px;
}

.assistant .message-text {
  background-color: #fff;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-time {
  font-size: 12px;
  color: #757575;
  margin-top: 4px;
  align-self: flex-end;
}

.user .message-time {
  margin-right: 8px;
}

.assistant .message-time {
  margin-left: 8px;
}

.typing-indicator {
  display: inline-block;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%,
  100% {
    opacity: 0.2;
  }
  50% {
    opacity: 1;
  }
}

.message.typing .message-text {
  background-color: #f0f0f0;
}

/* 底部输入区 */
.input-area {
  padding: 16px;
  background-color: #fff;
  border-top: 1px solid #e0e0e0;
}

.input-container {
  display: flex;
  align-items: center;
  background-color: #15d696;
  border-radius: 24px;
  padding: 8px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

textarea {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px 0;
  max-height: 120px;
  min-height: 24px;
  resize: none;
  outline: none;
  font-family: inherit;
  font-size: 15px;
}

.send-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-left: 8px;
}

.send-btn:hover {
  background-color: #388e3c;
}

.send-btn:disabled {
  background-color: #9e9e9e;
  cursor: not-allowed;
}

/* 深色模式 */
.container.dark {
  background-color: #1e1e1e;
  color: #e0e0e0;
}

.container.dark .sidebar {
  background-color: #2d2d2d;
  border-right-color: #444;
}

.container.dark .sidebar-header {
  border-bottom-color: #444;
}

.container.dark .chat-item:hover {
  background-color: #3a3a3a;
}

.container.dark .chat-item.active {
  background-color: #3a5a3e;
}

.container.dark .top-bar {
  background-color: #2d2d2d;
  border-bottom-color: #444;
}

.container.dark .toggle-sidebar-btn,
.container.dark .toggle-theme-btn {
  color: #e0e0e0;
}

.container.dark .toggle-sidebar-btn:hover,
.container.dark .toggle-theme-btn:hover {
  background-color: #3a3a3a;
}

.container.dark .chat-area {
  background-color: #1e1e1e;
}

.container.dark .user .message-text {
  background-color: #3a5a3e;
  color: #e0e0e0;
}

.container.dark .assistant .message-text {
  background-color: #2d2d2d;
  color: #e0e0e0;
}

/* Markdown 样式与代码高亮 */
.markdown-body {
  font-size: 14px;
}

.markdown-body pre code {
  white-space: pre;
}

.markdown-body p {
  margin: 0.5em 0;
}

.markdown-body code {
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
  padding: 0.2em 0.4em;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", "Courier New", monospace;
}

.container.dark .markdown-body code {
  background-color: rgba(110, 118, 129, 0.4);
}

.markdown-body pre {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 6px;
  overflow: auto;
}

.container.dark .markdown-body pre {
  background-color: #2d333b;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin: 0.6em 0 0.4em;
}

.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.6em 0;
}

.markdown-body th,
.markdown-body td {
  border: 1px solid #e1e4e8;
  padding: 6px 8px;
  text-align: left;
}

.container.dark .markdown-body th,
.container.dark .markdown-body td {
  border-color: #444c56;
}

.markdown-body a {
  color: #0366d6;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

/* 光标闪烁 */
.cursor {
  display: inline-block;
  margin-left: 2px;
  width: 6px;
  animation: cursor-blink 1s steps(2, start) infinite;
}

.cursor.paused {
  animation-play-state: paused;
}

@keyframes cursor-blink {
  0% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
/* 统一：标题与图标同栏、图标背景透明、优化间距与响应式 */
.chat-item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px; /* 标题与图标组的基础间距 */
}

/* 标题占满剩余空间并做省略处理 */
.chat-title {
  flex: 1;
  min-width: 0;
  margin: 0; /* 去掉额外垂直间距，确保与图标同一行视觉居中 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 图标按钮分组与间距 */
.chat-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px; /* 图标之间的间距 */
  flex-shrink: 0;
}

/* 透明图标按钮：去除背景色与阴影 */
.chat-actions .icon-btn {
  background-color: transparent !important;
  border: none;
  padding: 4px; /* 控制命中面积，同时不过度占位 */
  margin: 0;
  border-radius: 4px;
  line-height: 1;
  color: #666;
  box-shadow: none;
}
/* 统一图标尺寸与颜色继承 */
.chat-actions .icon-btn .el-icon {
  font-size: 18px;
  color: inherit;
}

/* 悬停/激活/聚焦：只改变前景色，移除背景效果 */
.chat-actions .icon-btn:hover,
.chat-actions .icon-btn:active,
.chat-actions .icon-btn:focus {
  background-color: transparent !important;
  color: #333;
  box-shadow: none;
  outline: none;
}

/* 危险态颜色，与原逻辑保持一致 */
.chat-actions .icon-btn.danger {
  color: #e53935;
}
.chat-actions .icon-btn.danger:hover,
.chat-actions .icon-btn.danger:active,
.chat-actions .icon-btn.danger:focus {
  background-color: transparent !important;
  color: #c62828;
}

/* 折叠/展开按钮 */
.sidebar-toggle-btn {
  position: absolute;
  top: 8px;
  right: 8px; /* 展开状态固定在右上角 */
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #555;
  padding: 4px;
  border-radius: 4px;
}
.sidebar-header.collapsed .sidebar-toggle-btn {
  right: auto;
  left: 50%;
  transform: translateX(-50%); /* 收起状态居中显示在顶部 */
}
.sidebar-toggle-btn:hover {
  background-color: transparent;
  color: #333;
}

/* 侧栏内容过渡动画（300ms，X轴轻微滑动+淡入淡出） */
.sidebar-content-enter-active,
.sidebar-content-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.sidebar-content-enter-from,
.sidebar-content-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

/* 响应式优化：在小屏收紧间距与内边距，保持视觉平衡 */
@media (max-width: 768px) {
  .chat-actions {
    gap: 6px;
  }
  .chat-actions .icon-btn {
    padding: 2px;
  }
  .chat-title {
    font-size: 14px;
  }
}
@media (max-width: 480px) {
  .sidebar.collapsed {
    width: 48px;
  }
  .chat-actions {
    gap: 4px;
  }
  .chat-title {
    font-size: 13px;
  }
}
/* 悬浮输入框（固定底部） */
.input-area {
  position: fixed;
  left: 280px; /* 与侧栏宽度一致，JS 计算将覆盖 */
  right: 0;
  bottom: 0;
  z-index: 1000;
  background-color: #fff;
  border-top: 1px solid #e0e0e0;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.06);
  padding: 10px 16px;
  transition: left 0.3s ease, box-shadow 0.2s ease, background-color 0.2s ease,
    border-color 0.2s ease;
}

.input-area .input-container {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 960px; /* 限制最大宽度，居中更美观 */
  margin: 0 auto; /* 居中 */
}

.input-area textarea {
  flex: 1;
  min-width: 0; /* 允许在flex容器中正确收缩 */
  box-sizing: border-box;
  min-height: 44px;
  max-height: 120px;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background-color: #fff;
}

.input-area textarea:focus {
  border-color: #4caf50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15);
}

/* 发送按钮：尺寸与交互效果 */
.input-area .send-btn {
  height: 44px;
  min-width: 44px;
  padding: 0 16px;
  background-color: #4caf50;
  color: #fff;
  border: none;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.06s ease,
    box-shadow 0.2s ease, opacity 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.input-area .send-btn:hover {
  background-color: #43a047;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
}

.input-area .send-btn:active {
  transform: translateY(1px);
}

.input-area .send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

/* 深色模式协调 */
.container.dark .input-area {
  background-color: #1f1f1f;
  border-color: #333;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.35);
}

.container.dark .input-area textarea {
  background-color: #2a2a2a;
  color: #eee;
  border-color: #444;
}

.container.dark .input-area textarea:focus {
  border-color: #66bb6a;
  box-shadow: 0 0 0 3px rgba(102, 187, 106, 0.25);
}

.container.dark .input-area .send-btn {
  background-color: #43a047;
}

.container.dark .input-area .send-btn:hover {
  background-color: #388e3c;
}

/* 避免聊天内容被悬浮输入框遮挡 */
.chat-area {
  padding-bottom: 96px;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .input-area {
    left: 0 !important; /* 移动端铺满屏宽 */
    padding: 8px 12px;
  }
  .input-area .input-container {
    gap: 8px;
  }
  .input-area .send-btn {
    height: 40px;
    min-width: 40px;
    padding: 0 12px;
    border-radius: 6px;
  }
  .chat-area {
    padding-bottom: 84px;
  }
}
</style>
