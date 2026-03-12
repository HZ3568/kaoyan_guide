<template>
  <div
    class="ai-container"
    :class="{ 'dark-mode': isDark }"
  >
    <!-- 侧边栏 -->
    <aside
      class="sidebar"
      :class="{ collapsed: !isSidebarOpen }"
    >
      <div class="sidebar-header">
        <div
          class="brand"
          v-if="isSidebarOpen"
        >
          <img
            src="@/assets/imgs/logo.png"
            alt="Logo"
            class="brand-logo"
            onerror="this.style.display='none'"
          />
          <span class="brand-text">考研咨询助手</span>
        </div>
        <button
          class="icon-btn toggle-btn"
          @click="toggleSidebar"
          title="切换侧边栏"
        >
          <el-icon>
            <Fold v-if="isSidebarOpen" />
            <Expand v-else />
          </el-icon>
        </button>
      </div>

      <div
        class="sidebar-action"
        v-if="isSidebarOpen"
      >
        <button
          class="new-chat-btn"
          @click="createNewChat"
        >
          <el-icon>
            <Plus />
          </el-icon>
          <span>开启新对话</span>
        </button>
      </div>
      <div
        class="sidebar-action-collapsed"
        v-else
      >
        <button
          class="icon-btn new-chat-icon"
          @click="createNewChat"
          title="开启新对话"
        >
          <el-icon>
            <Plus />
          </el-icon>
        </button>
      </div>

      <div class="chat-list-container">
        <transition-group name="list">
          <div
            v-for="(chat, index) in chats"
            :key="chat.id"
            class="chat-item"
            :class="{ active: index === currentChatIndex }"
            @click="switchChat(index)"
          >
            <div class="chat-item-content">
              <el-icon class="chat-icon">
                <ChatDotRound />
              </el-icon>

              <div
                class="chat-info"
                v-if="isSidebarOpen"
              >
                <div class="chat-title-row">
                  <span
                    v-if="editingChatId !== chat.id"
                    class="chat-title"
                    :title="chat.title"
                  >
                    {{ chat.title }}
                  </span>
                  <input
                    v-else
                    ref="renameInput"
                    class="rename-input"
                    v-model="editingTitle"
                    @click.stop
                    @keydown.enter="confirmRename(chat)"
                    @keydown.esc="cancelRename"
                    @blur="confirmRename(chat)"
                  />
                </div>
              </div>

              <div
                class="chat-actions"
                v-if="isSidebarOpen && editingChatId !== chat.id"
              >
                <button
                  class="action-btn"
                  @click.stop="startRename(chat)"
                  title="重命名"
                >
                  <el-icon>
                    <Edit />
                  </el-icon>
                </button>
                <button
                  class="action-btn delete"
                  @click.stop="requestDeleteChat(index)"
                  title="删除"
                >
                  <el-icon>
                    <Delete />
                  </el-icon>
                </button>
              </div>
            </div>
          </div>
        </transition-group>
      </div>

      <div
        class="sidebar-footer"
        v-if="isSidebarOpen"
      >
        <div class="user-profile">
          <!-- 这里的头像可以使用用户的真实头像 -->
          <el-avatar
            :size="32"
            src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
          />
          <span class="username">考生用户</span>
        </div>
      </div>
    </aside>

    <!-- 主界面 -->
    <main class="main-content">
      <!-- 顶部导航 -->
      <header class="top-header">
        <div class="header-left">
          <button
            class="icon-btn mobile-menu-btn"
            @click="toggleSidebar"
          >
            <el-icon>
              <Menu />
            </el-icon>
          </button>
          <span class="current-chat-title">{{ currentChat.title }}</span>
          <span class="chat-count-badge">{{ currentChat.messages.length }} 条对话</span>
        </div>
        <div class="header-right">
          <button
            class="icon-btn theme-btn"
            @click="toggleTheme"
            :title="isDark ? '切换亮色' : '切换深色'"
          >
            <el-icon v-if="!isDark">
              <Moon />
            </el-icon>
            <el-icon v-else>
              <Sunny />
            </el-icon>
          </button>
        </div>
      </header>

      <!-- 聊天区域 -->
      <div
        class="chat-scroll-area"
        ref="chatArea"
      >
        <div class="chat-wrapper">
          <div
            v-for="msg in currentChat.messages"
            :key="msg.id"
            class="message-row"
            :class="msg.role"
          >
            <div class="avatar-col">
              <div
                class="avatar"
                :class="msg.role"
              >
                <img
                  :src="
                    msg.role === 'assistant'
                      ? '/src/assets/imgs/bot-avatar.png'
                      : '/src/assets/imgs/user-avatar.png'
                  "
                  @error="
                    (e) => {
                      e.target.src =
                        msg.role === 'assistant'
                          ? 'https://cdn-icons-png.flaticon.com/512/4712/4712027.png'
                          : 'https://cdn-icons-png.flaticon.com/512/3177/3177440.png';
                    }
                  "
                  alt="avatar"
                />
              </div>
            </div>

            <div class="content-col">
              <div class="message-meta">
                <span class="name">{{
                  msg.role === "assistant" ? "AI 咨询顾问" : "我"
                }}</span>
                <span class="time">{{ formatTime(msg.timestamp) }}</span>
              </div>

              <div class="message-bubble">
                <template v-if="msg.role === 'assistant'">
                  <div
                    class="markdown-body"
                    v-html="renderMarkdown(msg.displayedText || msg.text)"
                  ></div>
                  <span
                    v-if="msg.isStreaming"
                    class="typing-cursor"
                  ></span>
                </template>
                <div
                  v-else
                  class="user-text"
                >{{ msg.text }}</div>
              </div>
            </div>
          </div>

          <!-- 快捷建议区域：仅在对话初期显示 -->
          <div
            class="suggestions-area"
            v-if="currentChat.messages.length <= 1 && !controller"
          >
            <p class="suggestions-title">你可以试着问我：</p>
            <div class="suggestion-chips">
              <div
                v-for="(item, idx) in suggestedQuestions"
                :key="idx"
                class="chip"
                @click="useSuggestion(item)"
              >
                {{ item }}
                <el-icon>
                  <ArrowRight />
                </el-icon>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入框 -->
      <div class="input-wrapper">
        <div
          class="input-box"
          :class="{ 'is-focused': isInputFocused }"
        >
          <textarea
            ref="inputRef"
            v-model="input"
            class="chat-input"
            placeholder="输入你想了解的院校信息，例如：'推荐几所计算机专业的211院校'..."
            rows="1"
            @keydown.enter.prevent="handleEnter"
            @focus="isInputFocused = true"
            @blur="isInputFocused = false"
            @input="adjustHeight"
          ></textarea>
          <div class="input-actions">
            <button
              class="send-btn"
              @click="sendMessage"
              :disabled="!input.trim() || controller !== null"
              :class="{ 'is-sending': controller !== null }"
            >
              <el-icon v-if="!controller">
                <Promotion />
              </el-icon>
              <div
                v-else
                class="loading-dots"
              >
                <span></span><span></span><span></span>
              </div>
            </button>
          </div>
        </div>
        <p class="disclaimer">
          AI 生成内容仅供参考，请以官方发布的招生简章为准。
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
// request 暂时保留引用，但实际核心逻辑是 fetch
import request from "@/utils/request";
import { marked } from "marked";
import DOMPurify from "dompurify";
import hljs from "highlight.js";
import "highlight.js/styles/atom-one-dark.css"; // 更现代的代码高亮风格
import {
  Fold,
  Expand,
  Plus,
  Promotion,
  Moon,
  Sunny,
  Edit,
  Delete,
  ChatDotRound,
  ArrowRight,
  Menu,
} from "@element-plus/icons-vue";

// 状态管理
const isDark = ref(false);
const isSidebarOpen = ref(true);
const input = ref("");
const chatArea = ref(null);
const inputRef = ref(null);
const isInputFocused = ref(false);
let controller = null;
let typingIntervals = {};

// 预设建议问题
const suggestedQuestions = [
  "帮我分析一下西安电子科技大学计算机考研难度",
  "推荐几所位于上海的理工类211院校",
  "专硕和学硕在培养模式上有什么区别？",
  "如何制定考研英语复习计划？",
];

// UUID生成
const createSessionId = () => {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
};

const ensureChatSessionId = (chat) => {
  if (!chat) return createSessionId();
  if (!chat.sessionId) {
    chat.sessionId = createSessionId();
  }
  return chat.sessionId;
};

// 存储管理
const loadChatsFromLocalStorage = () => {
  const savedChats = localStorage.getItem("volunteer-apply-ai-chats");
  if (savedChats) {
    try {
      const parsedChats = JSON.parse(savedChats);
      if (Array.isArray(parsedChats) && parsedChats.length > 0) {
        return parsedChats.map((chat) => ({
          ...chat,
          sessionId: chat.sessionId || createSessionId(),
        }));
      }
    } catch (e) {
      console.error("加载聊天记录失败:", e);
    }
  }
  return null;
};

const chats = ref(
  loadChatsFromLocalStorage() || [
    {
      id: Date.now(),
      sessionId: createSessionId(),
      title: "新的咨询会话",
      messages: [
        {
          id: Date.now(),
          role: "assistant",
          text: "你好！我是你的考研院校咨询助手。我可以帮你查询院校信息、分析录取数据、规划备考方案。请告诉我你想了解什么？",
          displayedText:
            "你好！我是你的考研院校咨询助手。我可以帮你查询院校信息、分析录取数据、规划备考方案。请告诉我你想了解什么？",
          timestamp: new Date().toISOString(),
        },
      ],
    },
  ]
);

const currentChatIndex = ref(0);
const currentChat = computed(() => chats.value[currentChatIndex.value]);

// 操作逻辑
const saveChatsToLocalStorage = () => {
  localStorage.setItem("volunteer-apply-ai-chats", JSON.stringify(chats.value));
};

const editingChatId = ref(null);
const editingTitle = ref("");
const renameInput = ref(null);

function startRename(chat) {
  editingChatId.value = chat.id;
  editingTitle.value = chat.title || "";
  nextTick(() => {
    if (renameInput.value && renameInput.value[0]) {
      renameInput.value[0].focus();
    }
  });
}

function confirmRename(chat) {
  if (!chat || editingChatId.value !== chat.id) return;
  const newTitle = (editingTitle.value || "").trim();
  if (newTitle) {
    chat.title = newTitle;
    saveChatsToLocalStorage();
    ElMessage.success("会话名称已更新");
  }
  editingChatId.value = null;
}

function cancelRename() {
  editingChatId.value = null;
}

async function requestDeleteChat(index) {
  try {
    await ElMessageBox.confirm(
      "确定要删除这条对话记录吗？删除后不可恢复。",
      "删除确认",
      {
        confirmButtonText: "确认删除",
        cancelButtonText: "取消",
        type: "warning",
        buttonSize: "default",
      }
    );
    chats.value.splice(index, 1);
    if (chats.value.length === 0) {
      createNewChat();
    } else {
      if (currentChatIndex.value >= chats.value.length) {
        currentChatIndex.value = chats.value.length - 1;
      }
    }
    saveChatsToLocalStorage();
    ElMessage.success("已删除");
  } catch (e) {
    // cancelled
  }
}

function toggleTheme() {
  isDark.value = !isDark.value;
  localStorage.setItem("darkMode", isDark.value);
}

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value;
}

function scrollToBottom() {
  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight;
    }
  });
}

function useSuggestion(text) {
  input.value = text;
  sendMessage();
}

function handleEnter(e) {
  if (!e.shiftKey) {
    sendMessage();
  }
}

function adjustHeight() {
  const el = inputRef.value;
  if (el) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 150) + "px";
  }
}

// 消息处理逻辑保持核心不变，优化UI反馈
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

  if (typingIntervals[msg.id]) clearInterval(typingIntervals[msg.id]);

  const typingSpeed = Math.max(5, Math.min(20, 20 - Math.floor(len / 100)));

  typingIntervals[msg.id] = setInterval(() => {
    if (i < len) {
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

async function sendMessage() {
  const inputText = input.value.trim();
  if (!inputText) return;

  if (controller) {
    controller.abort();
    controller = null;
  }

  controller = new AbortController();

  // 添加用户消息
  currentChat.value.messages.push({
    id: Date.now(),
    role: "user",
    text: inputText,
    timestamp: new Date().toISOString(),
  });

  input.value = "";
  if (inputRef.value) inputRef.value.style.height = "auto";
  scrollToBottom();

  // 预置AI消息
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
  saveChatsToLocalStorage();

  let timeoutId = null;

  try {
    timeoutId = setTimeout(() => {
      if (controller) controller.abort();
    }, 20000); // 延长超时时间提升体验

    const user = JSON.parse(localStorage.getItem("xm-user") || "{}");
    const activeSessionId = ensureChatSessionId(currentChat.value);

    const response = await fetch(
      `/api/chat?message=${encodeURIComponent(
        inputText
      )}&moduleType=volunteer_apply&sessionId=${encodeURIComponent(
        activeSessionId
      )}`,
      {
        method: "GET",
        headers: {
          Accept: "text/event-stream",
          token: user.token || "",
        },
        signal: controller.signal,
      }
    );

    // 更新会话ID
    const responseSessionId = response.headers.get("X-Session-Id");
    if (responseSessionId) currentChat.value.sessionId = responseSessionId;

    if (!response.ok) throw new Error(`Status: ${response.status}`);
    if (!response.body) throw new Error("Empty body");

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let rawBuffer = "";
    let finalText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      rawBuffer += decoder.decode(value, { stream: true });
      const eventBlocks = rawBuffer.split("\n\n");
      rawBuffer = eventBlocks.pop() || "";

      for (const block of eventBlocks) {
        const lines = block.split("\n");
        const dataLines = lines
          .filter((l) => l.startsWith("data:"))
          .map((l) => {
            let d = l.slice(5);
            return d.startsWith(" ") ? d.slice(1) : d;
          })
          .filter((d) => d !== "[DONE]");

        if (dataLines.length > 0) {
          finalText += dataLines.join("\n");
          assistantMsg.text = finalText;
          // 实时显示，减少打字机延迟感
          assistantMsg.displayedText = finalText;
        }
      }
      scrollToBottom();
      saveChatsToLocalStorage();
    }
  } catch (err) {
    if (err.name !== "AbortError") {
      assistantMsg.text = `### 请求出错\n${
        err.message || "网络连接异常，请稍后重试"
      }`;
      assistantMsg.displayedText = assistantMsg.text;
    }
  } finally {
    clearTimeout(timeoutId);
    assistantMsg.isStreaming = false;
    controller = null;
    scrollToBottom();
    saveChatsToLocalStorage();
  }
}

function createNewChat() {
  const newId = Date.now();
  chats.value.push({
    id: newId,
    sessionId: createSessionId(),
    title: `新对话 ${chats.value.length + 1}`,
    messages: [
      {
        id: newId + 1,
        role: "assistant",
        text: "你好！我是你的考研院校咨询助手。新的会话已创建，随时准备为你解答问题。",
        displayedText:
          "你好！我是你的考研院校咨询助手。新的会话已创建，随时准备为你解答问题。",
        timestamp: new Date().toISOString(),
      },
    ],
  });
  currentChatIndex.value = chats.value.length - 1;
  saveChatsToLocalStorage();
  scrollToBottom();
}

function switchChat(index) {
  if (controller) {
    controller.abort();
    controller = null;
  }
  currentChatIndex.value = index;
  scrollToBottom();
}

// Markdown 配置
marked.setOptions({
  breaks: true,
  gfm: true,
  highlight(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : "plaintext";
    return hljs.highlight(code, { language }).value;
  },
});

const renderer = new marked.Renderer();
// 优化链接渲染，增加样式类
renderer.link = (href, title, text) => {
  return `<a href="${href}" title="${
    title || ""
  }" target="_blank" class="md-link">${text}</a>`;
};

function renderMarkdown(text) {
  const raw = marked.parse(text || "", { renderer });
  return DOMPurify.sanitize(raw);
}

onMounted(() => {
  isDark.value = localStorage.getItem("darkMode") === "true";
  scrollToBottom();
});

function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }
  return date.toLocaleDateString("zh-CN", { month: "short", day: "numeric" });
}

watch(
  chats,
  () => {
    saveChatsToLocalStorage();
  },
  { deep: true }
);
</script>

<style scoped>
/* CSS 变量系统：定义两套主题色 */
.ai-container {
  --bg-primary: #ffffff;
  --bg-secondary: #f9f9fb;
  --bg-sidebar: #f3f4f6;
  --bg-input: #ffffff;
  --bg-bubble-user: #e3f2fd;
  --bg-bubble-ai: #ffffff;

  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;

  --accent-color: #10b981; /* 品牌绿 */
  --accent-hover: #059669;

  --border-light: #e5e7eb;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-float: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);

  display: flex;
  height: 100vh;
  width: 100vw;
  font-family: "Inter", "PingFang SC", sans-serif;
  color: var(--text-primary);
  background-color: var(--bg-secondary);
  transition: background-color 0.3s, color 0.3s;
}

.ai-container.dark-mode {
  --bg-primary: #1f1f1f;
  --bg-secondary: #121212;
  --bg-sidebar: #181818;
  --bg-input: #2a2a2a;
  --bg-bubble-user: #059669;
  --bg-bubble-ai: #2a2a2a;

  --text-primary: #e5e7eb;
  --text-secondary: #9ca3af;
  --text-tertiary: #6b7280;

  --border-light: #374151;
  --accent-color: #10b981;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  background-color: var(--bg-sidebar);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid transparent;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
}

.brand-logo {
  width: 28px;
  height: 28px;
  border-radius: 6px;
}

.toggle-btn {
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
}
.toggle-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--text-primary);
}

.sidebar-action {
  padding: 16px;
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}

.new-chat-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
  box-shadow: var(--shadow-md);
}

.sidebar-action-collapsed {
  padding: 16px 0;
  display: flex;
  justify-content: center;
}

.new-chat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.new-chat-icon:hover {
  color: var(--accent-color);
  border-color: var(--accent-color);
}

.chat-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}

/* 滚动条美化 */
.chat-list-container::-webkit-scrollbar {
  width: 4px;
}
.chat-list-container::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.chat-item {
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  padding: 10px 8px;
  color: var(--text-secondary);
}

.chat-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
  color: var(--text-primary);
}

.chat-item.active {
  background-color: rgba(16, 185, 129, 0.1); /* 品牌色淡背景 */
  color: var(--accent-color);
}

.chat-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 24px;
}

.chat-info {
  flex: 1;
  min-width: 0;
}

.chat-title-row {
  display: flex;
  align-items: center;
}

.chat-title {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.rename-input {
  width: 100%;
  padding: 2px 4px;
  border: 1px solid var(--accent-color);
  border-radius: 4px;
  font-size: 13px;
  outline: none;
}

.chat-actions {
  display: none;
  gap: 4px;
}

.chat-item:hover .chat-actions {
  display: flex;
}

.action-btn {
  padding: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-tertiary);
  border-radius: 4px;
}
.action-btn:hover {
  color: var(--text-primary);
  background-color: rgba(0, 0, 0, 0.08);
}
.action-btn.delete:hover {
  color: #ef4444;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-light);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  min-width: 0;
}

.top-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid var(--border-light);
  background-color: var(--bg-primary);
}

.header-left {
  display: flex;
  align-items: center;
}

.mobile-menu-btn {
  display: none;
  background: transparent;
  border: none;
  font-size: 20px;
  margin-right: 12px;
  cursor: pointer;
  color: var(--text-primary);
  padding: 4px;
}

.current-chat-title {
  font-size: 16px;
  font-weight: 600;
  margin-right: 12px;
}

.chat-count-badge {
  font-size: 12px;
  color: var(--text-tertiary);
  background-color: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 12px;
}

.theme-btn {
  background: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 8px;
  border-radius: 50%;
  transition: background 0.2s;
}
.theme-btn:hover {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

/* 聊天滚动区 */
.chat-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
  scroll-behavior: smooth;
}

.chat-wrapper {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-light);
  flex-shrink: 0;
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.content-col {
  display: flex;
  flex-direction: column;
  max-width: 85%;
}

.message-row.user .content-col {
  align-items: flex-end;
}

.message-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  position: relative;
  word-break: break-word;
  box-shadow: var(--shadow-sm);
}

.message-row.user .message-bubble {
  background-color: var(--bg-bubble-user);
  color: var(--text-primary);
  border-top-right-radius: 2px;
  /* 深色模式下用户气泡文字适配 */
}
.ai-container.dark-mode .message-row.user .message-bubble {
  color: #fff;
}

.message-row.assistant .message-bubble {
  background-color: var(--bg-bubble-ai);
  border: 1px solid var(--border-light);
  border-top-left-radius: 2px;
}

/* 快捷建议 */
.suggestions-area {
  margin-top: 20px;
  animation: fadeIn 0.5s ease;
}

.suggestions-title {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-align: center;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.chip {
  padding: 8px 16px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chip:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* 输入区域 */
.input-wrapper {
  background: linear-gradient(to top, var(--bg-secondary) 80%, transparent);
  position: relative;
  z-index: 5;
  padding-bottom: 64px;
}

.input-box {
  max-width: 950px;
  margin: 0 auto;
  background-color: var(--bg-input);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  box-shadow: var(--shadow-float);
  padding: 2px 16px;
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-box.is-focused {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1), var(--shadow-float);
}

.chat-input {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  padding: 4px;
  font-size: 15px;
  color: var(--text-primary);
  font-family: inherit;
  resize: none;
  min-height: 24px;
  max-height: 150px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 4px;
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  transform: scale(1.05);
}

.send-btn:disabled {
  background-color: var(--border-light);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.disclaimer {
  text-align: center;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 12px;
}

/* Markdown 样式 */
.markdown-body {
  font-size: 15px;
  color: var(--text-primary);
}
.markdown-body :deep(p) {
  margin-bottom: 0.8em;
}
.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}
.markdown-body :deep(pre) {
  background-color: #282c34;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  color: #abb2bf;
}
.markdown-body :deep(code) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}
.ai-container.dark-mode .markdown-body :deep(code) {
  background-color: rgba(255, 255, 255, 0.1);
}
.markdown-body :deep(a) {
  color: var(--accent-color);
  text-decoration: none;
}
.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.typing-cursor {
  display: inline-block;
  width: 6px;
  height: 16px;
  background-color: var(--accent-color);
  margin-left: 4px;
  vertical-align: middle;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.loading-dots span {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: currentColor;
  margin: 0 2px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}
.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .mobile-menu-btn {
    display: block;
  }

  .sidebar {
    position: absolute;
    height: 100%;
    transform: translateX(-100%);
  }
  .sidebar.collapsed {
    width: 280px;
    transform: translateX(0); /* 移动端 collapsed 实际用来表示显示 */
  }
  /* 逻辑反转：移动端默认隐藏，点击展开 */

  .chat-wrapper {
    padding: 0 16px;
  }

  .message-row {
    gap: 10px;
  }

  .avatar {
    width: 32px;
    height: 32px;
  }

  .input-wrapper {
    padding: 12px;
  }
}
</style>

