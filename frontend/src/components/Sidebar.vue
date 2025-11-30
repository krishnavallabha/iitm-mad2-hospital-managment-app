<template>
  <aside class="sidebar d-flex flex-column bg-white">
    <div class="px-4 py-4">
      <div class="d-flex align-items-center gap-2 mb-4">
        <div class="brand-icon rounded-circle d-flex align-items-center justify-content-center">
          <i class="bi bi-heart-pulse text-white fs-4"></i>
        </div>
        <div>
          <p class="mb-0 text-uppercase text-muted small">Welcome to</p>
          <h5 class="mb-0 fw-bold">SerenityCare</h5>
        </div>
      </div>
      <nav class="nav flex-column gap-2">
        <button
          v-for="item in filteredNavItems"
          :key="item.label"
          class="btn btn-light d-flex align-items-center gap-3 rounded-pill text-start shadow-sm"
        >
          <i :class="['bi', item.icon, 'fs-5']"></i>
          <span class="fw-medium">{{ item.label }}</span>
        </button>
      </nav>
    </div>
    <div class="mt-auto p-4">
      <div class="card card-soft rounded-xxl">
        <div class="card-body text-center">
          <img
            src="https://ui-avatars.com/api/?name=Serenity+Admin&background=6c63ff&color=fff"
            alt="Admin Avatar"
            class="rounded-circle mb-3"
            width="72"
            height="72"
          />
          <h6 class="fw-bold mb-1">Serenity Admin</h6>
          <p class="text-muted small mb-3">System Administrator</p>
          <div class="d-grid gap-2">
            <button class="btn btn-primary rounded-pill">View Profile</button>
            <button class="btn btn-outline-secondary rounded-pill" @click="$emit('logout')">Logout</button>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  role: {
    type: String,
    default: 'admin'
  }
});

const navItems = [
  { icon: 'bi-speedometer2', label: 'Dashboard', roles: ['admin', 'doctor', 'patient'] },
  { icon: 'bi-calendar2-week', label: 'Appointments', roles: ['admin', 'doctor', 'patient'] },
  { icon: 'bi-person-heart', label: 'Patients', roles: ['admin', 'doctor'] },
  { icon: 'bi-person-badge', label: 'Doctors', roles: ['admin'] },
  { icon: 'bi-clipboard-pulse', label: 'Treatments', roles: ['doctor'] },
  { icon: 'bi-graph-up', label: 'Analytics', roles: ['admin'] },
  { icon: 'bi-credit-card', label: 'Payments', roles: ['admin', 'patient'] }
];

const filteredNavItems = computed(() =>
  navItems.filter((item) => item.roles.includes(props.role))
);
</script>

<style scoped>
.sidebar {
  width: 290px;
  border-radius: 0 32px 32px 0;
  box-shadow: 20px 0 40px rgba(15, 23, 42, 0.08);
  position: sticky;
  top: 0;
  height: 100vh;
}

.brand-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--serenity-primary), var(--serenity-secondary));
  box-shadow: var(--serenity-shadow);
}

@media (max-width: 991px) {
  .sidebar {
    width: 100%;
    height: auto;
    border-radius: 0 0 32px 32px;
    position: static;
  }
}
</style>

