<template>
  <div
    v-if="visible"
    class="modal fade show d-block"
    tabindex="-1"
    role="dialog"
    style="background-color: rgba(0, 0, 0, 0.5);"
    @click.self="handleCancel"
  >
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content rounded-4 shadow-lg">
        <div class="modal-header border-0 pb-0">
          <div class="d-flex align-items-center gap-3">
            <div
              class="rounded-circle d-flex align-items-center justify-content-center"
              :class="iconClass"
              style="width: 48px; height: 48px;"
            >
              <i :class="icon" class="fs-5"></i>
            </div>
            <h5 class="modal-title fw-bold mb-0">{{ title }}</h5>
          </div>
          <button
            type="button"
            class="btn-close"
            @click="handleCancel"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body pt-3">
          <p class="mb-0">{{ message }}</p>
          <p v-if="details" class="text-muted small mt-2 mb-0">{{ details }}</p>
        </div>
        <div class="modal-footer border-0 pt-0">
          <button
            type="button"
            class="btn btn-outline-secondary rounded-pill"
            @click="handleCancel"
          >
            {{ cancelText }}
          </button>
          <button
            type="button"
            class="btn rounded-pill"
            :class="confirmButtonClass"
            @click="handleConfirm"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    required: true
  },
  details: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'warning', // 'warning', 'danger', 'info', 'success'
    validator: (value) => ['warning', 'danger', 'info', 'success'].includes(value)
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['confirm', 'cancel', 'update:visible']);

const icon = computed(() => {
  const icons = {
    warning: 'bi bi-exclamation-triangle-fill',
    danger: 'bi bi-exclamation-circle-fill',
    info: 'bi bi-info-circle-fill',
    success: 'bi bi-check-circle-fill'
  };
  return icons[props.type] || icons.warning;
});

const iconClass = computed(() => {
  const classes = {
    warning: 'bg-warning-subtle text-warning',
    danger: 'bg-danger-subtle text-danger',
    info: 'bg-info-subtle text-info',
    success: 'bg-success-subtle text-success'
  };
  return classes[props.type] || classes.warning;
});

const confirmButtonClass = computed(() => {
  const classes = {
    warning: 'btn-warning',
    danger: 'btn-danger',
    info: 'btn-info',
    success: 'btn-success'
  };
  return classes[props.type] || 'btn-primary';
});

const handleConfirm = () => {
  emit('confirm');
  emit('update:visible', false);
};

const handleCancel = () => {
  emit('cancel');
  emit('update:visible', false);
};
</script>

<style scoped>
.modal {
  backdrop-filter: blur(2px);
}
</style>

