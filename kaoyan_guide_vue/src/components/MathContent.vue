<template>
  <div ref="containerRef" class="math-content" :class="{ inline: inline }"></div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from "vue";
import renderMathInElement from "katex/contrib/auto-render";
import "katex/dist/katex.min.css";

const props = defineProps({
  content: {
    type: [String, Number],
    default: "",
  },
  inline: {
    type: Boolean,
    default: false,
  },
});

const containerRef = ref();

const render = async () => {
  await nextTick();
  if (!containerRef.value) {
    return;
  }
  const value = props.content == null ? "" : String(props.content);
  containerRef.value.textContent = value;
  renderMathInElement(containerRef.value, {
    throwOnError: false,
    strict: "ignore",
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "\\[", right: "\\]", display: true },
      { left: "\\(", right: "\\)", display: false },
      { left: "$", right: "$", display: false },
    ],
  });
};

onMounted(render);
watch(() => props.content, render);
</script>

<style scoped>
.math-content {
  color: inherit;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.math-content.inline {
  display: inline;
  white-space: normal;
  line-height: inherit;
}

.math-content :deep(.katex-display) {
  margin: 0.6em 0;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 4px;
  max-width: 100%;
}

.math-content :deep(.katex-display > .katex) {
  white-space: nowrap;
}

.math-content :deep(.katex) {
  max-width: 100%;
}
</style>
