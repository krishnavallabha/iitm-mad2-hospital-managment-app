<template>
  <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1055;">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast show"
      :class="`toast-${toast.type}`"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="toast-header">
        <i :class="getIcon(toast.type)" class="me-2"></i>
        <strong class="me-auto">{{ toast.title }}</strong>
        <button
          type="button"
          class="btn-close"
          @click="removeToast(toast.id)"
          aria-label="Close"
        ></button>
      </div>
      <div class="toast-body">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const toasts = ref([]);
let toastIdCounter = 0;

const getIcon = (type) => {
  const icons = {
    success: 'bi bi-check-circle-fill text-success',
    error: 'bi bi-x-circle-fill text-danger',
    warning: 'bi bi-exclamation-triangle-fill text-warning',
    info: 'bi bi-info-circle-fill text-info'
  };
  return icons[type] || icons.info;
};

const addToast = (type, title, message, duration = 5000) => {
  const id = ++toastIdCounter;
  const toast = {
    id,
    type,
    title,
    message,
    duration
  };
  
  toasts.value.push(toast);
  
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id);
    }, duration);
  }
  
  return id;
};

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id);
  if (index > -1) {
    toasts.value.splice(index, 1);
  }
};

const clearAll = () => {
  toasts.value = [];
};

// Expose methods for use in composable
defineExpose({
  addToast,
  removeToast,
  clearAll
});

// Make methods available globally via provide/inject or window
onMounted(() => {
  window.$toast = {
    success: (title, message, duration) => addToast('success', title, message, duration),
    error: (title, message, duration) => addToast('error', title, message, duration),
    warning: (title, message, duration) => addToast('warning', title, message, duration),
    info: (title, message, duration) => addToast('info', title, message, duration),
    clear: clearAll
  };
});

onBeforeUnmount(() => {
  delete window.$toast;
});
</script>

<style scoped>
.toast-container {
  max-width: 400px;
}

.toast {
  min-width: 300px;
  margin-bottom: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  border-radius: 0.5rem;
}

.toast-header {
  background-color: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.toast-body {
  background-color: rgba(255, 255, 255, 0.98);
}
</style>

