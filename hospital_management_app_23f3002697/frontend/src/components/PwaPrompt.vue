<template>
  <transition name="fade">
    <div
      v-if="showPrompt"
      class="p-3 p-lg-4 position-fixed bottom-0 end-0 m-3 m-lg-4 card card-soft"
      style="max-width: 320px; z-index: 20;"
    >
      <div class="card-body">
        <h6 class="fw-bold">Install SerenityCare</h6>
        <p class="text-muted small mb-3">
          Add SerenityCare to your home screen for a faster, app-like experience.
        </p>
        <div class="d-flex gap-2">
          <button class="btn btn-outline-secondary btn-sm rounded-pill flex-grow-1" @click="dismiss">
            Later
          </button>
          <button class="btn btn-primary btn-sm rounded-pill flex-grow-1" @click="install">
            Add to Home
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const deferredPrompt = ref(null);
const showPrompt = ref(false);

const handleBeforeInstall = (event) => {
  event.preventDefault();
  deferredPrompt.value = event;
  showPrompt.value = true;
};

const install = async () => {
  if (!deferredPrompt.value) return;
  deferredPrompt.value.prompt();
  const choiceResult = await deferredPrompt.value.userChoice;
  if (choiceResult.outcome === 'accepted') {
    showPrompt.value = false;
    deferredPrompt.value = null;
  }
};

const dismiss = () => {
  showPrompt.value = false;
};

onMounted(() => {
  window.addEventListener('beforeinstallprompt', handleBeforeInstall);
});

onBeforeUnmount(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

