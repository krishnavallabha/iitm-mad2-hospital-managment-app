<template>
  <div class="enhanced-search">
    <div class="d-flex gap-2 mb-3 flex-wrap">
      <div class="flex-grow-1" style="min-width: 200px;">
        <div class="input-group">
          <span class="input-group-text bg-white border-end-0">
            <i class="bi bi-search"></i>
          </span>
          <input
            type="text"
            class="form-control border-start-0 rounded-end-pill"
            :placeholder="placeholder"
            v-model="searchQuery"
            @input="handleSearch"
            @keyup.enter="handleSearch"
          />
          <button
            v-if="searchQuery"
            class="btn btn-outline-secondary rounded-start-0 rounded-end-pill"
            type="button"
            @click="clearSearch"
          >
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
      
      <button
        v-if="showAdvanced"
        class="btn btn-outline-primary rounded-pill"
        @click="toggleAdvanced"
      >
        <i class="bi bi-funnel me-2"></i>
        {{ showAdvancedFilters ? 'Hide Filters' : 'Advanced Filters' }}
      </button>
      
      <div v-if="searchQuery || hasActiveFilters" class="d-flex align-items-center">
        <span class="badge bg-primary-subtle text-primary me-2">
          {{ resultCount }} {{ resultLabel }}
        </span>
        <button
          class="btn btn-sm btn-outline-secondary rounded-pill"
          @click="clearAll"
        >
          Clear All
        </button>
      </div>
    </div>

    <div v-if="showAdvancedFilters" class="card card-soft mb-3">
      <div class="card-body">
        <div class="row g-3">
          <slot name="filters">
            <!-- Custom filters will be inserted here -->
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Search...'
  },
  resultCount: {
    type: Number,
    default: 0
  },
  resultLabel: {
    type: String,
    default: 'results'
  },
  showAdvanced: {
    type: Boolean,
    default: true
  },
  modelValue: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:modelValue', 'search', 'clear', 'filter-change']);

const searchQuery = ref(props.modelValue);
const showAdvancedFilters = ref(false);

const hasActiveFilters = computed(() => {
  // This will be computed based on active filters
  return false;
});

const handleSearch = () => {
  emit('update:modelValue', searchQuery.value);
  emit('search', searchQuery.value);
};

const clearSearch = () => {
  searchQuery.value = '';
  emit('update:modelValue', '');
  emit('clear');
};

const clearAll = () => {
  clearSearch();
  emit('filter-change', {});
};

const toggleAdvanced = () => {
  showAdvancedFilters.value = !showAdvancedFilters.value;
};

watch(() => props.modelValue, (newVal) => {
  searchQuery.value = newVal;
});
</script>

<style scoped>
.enhanced-search .input-group-text {
  border-color: #dee2e6;
}

.enhanced-search .form-control:focus {
  border-color: #dee2e6;
  box-shadow: none;
}
</style>

