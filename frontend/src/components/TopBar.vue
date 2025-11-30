<template>
  <header class="topbar bg-transparent px-2 px-md-3 px-lg-4 py-2 py-md-3">
    <div class="d-flex flex-column flex-md-row gap-2 gap-md-3 align-items-md-center justify-content-md-end">
      <div class="d-flex align-items-center gap-2 gap-md-3 flex-wrap">
        <!-- Patient Actions -->
        <div v-if="user?.role === 'patient'" class="d-flex gap-2">
          <button class="btn btn-outline-secondary rounded-pill btn-sm" @click="$emit('edit-profile')">
            <i class="bi bi-person-gear me-1 d-none d-sm-inline"></i>
            <span class="d-sm-none">Profile</span>
            <span class="d-none d-sm-inline">Edit Profile</span>
          </button>
        </div>

        <div class="text-end d-none d-sm-block">
          <p class="mb-0 fw-semibold small">{{ user?.username }}</p>
          <small class="text-muted text-uppercase" style="font-size: 0.7rem;">{{ user?.role }}</small>
        </div>
        <div class="text-end d-sm-none">
          <p class="mb-0 fw-semibold" style="font-size: 0.875rem;">{{ user?.username }}</p>
        </div>
        <button class="btn btn-light rounded-circle shadow-sm" @click="$emit('logout')" title="Logout" style="min-width: 40px; min-height: 40px;">
          <i class="bi bi-box-arrow-right fs-5 text-danger"></i>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  user: {
    type: Object,
    default: () => null
  }
});
</script>

<style scoped>
.topbar {
  background: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 10;
  width: 100%;
}

@media (max-width: 575.98px) {
  .topbar {
    padding: 0.5rem !important;
  }
  
  .topbar .btn-sm {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
}
</style>

