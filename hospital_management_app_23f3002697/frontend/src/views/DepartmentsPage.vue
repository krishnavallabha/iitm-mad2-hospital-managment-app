<template>
  <div class="departments-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <button class="btn btn-link text-decoration-none p-0 mb-2" @click="$emit('navigate', 'dashboard')">
          <i class="bi bi-arrow-left me-2"></i>Back to Dashboard
        </button>
        <h4 class="fw-bold mb-1">SerenityCare Departments</h4>
        <p class="text-muted small mb-0">Explore our medical specialties and find the right care for you</p>
      </div>
    </div>

    <div class="row g-4">
      <div
        v-for="dept in departments"
        :key="dept.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <div class="card card-soft h-100 department-card">
          <div class="card-body">
            <div class="d-flex align-items-start justify-content-between mb-3">
              <div class="department-icon rounded-circle d-flex align-items-center justify-content-center">
                <i :class="getDepartmentIcon(dept.name)" class="fs-4"></i>
              </div>
              <span class="badge bg-primary-subtle text-primary rounded-pill">
                {{ dept.active_doctors_count || 0 }} Doctors
              </span>
            </div>
            <h5 class="fw-bold mb-2">{{ dept.name }}</h5>
            <p class="text-muted small mb-3">{{ dept.description || 'Hospital specialty' }}</p>
            <button
              class="btn btn-primary rounded-pill w-100"
              @click="viewDepartment(dept)"
            >
              View Department
            </button>
          </div>
        </div>
      </div>
    </div>

    <DepartmentDetailsModal
      v-if="showDepartmentModal"
      :departmentId="selectedDepartmentId"
      @close="closeDepartmentModal"
      @view-doctor="handleViewDoctor"
      @book-doctor="handleBookDoctor"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import DepartmentDetailsModal from '../components/patient/DepartmentDetailsModal.vue';

const emit = defineEmits(['navigate', 'view-doctor', 'book-doctor']);

const departments = ref([]);
const showDepartmentModal = ref(false);
const selectedDepartmentId = ref(null);

const getDepartmentIcon = (name) => {
  const icons = {
    'Cardiology': 'bi-heart-pulse',
    'Neurology': 'bi-brain',
    'Orthopedics': 'bi-bone',
    'Pediatrics': 'bi-heart',
    'Dermatology': 'bi-droplet',
    'General Medicine': 'bi-clipboard-pulse',
    'Psychiatry': 'bi-people',
    'Oncology': 'bi-shield-check'
  };
  return icons[name] || 'bi-hospital';
};

const fetchDepartments = async () => {
  const { data } = await api.get('/patient/departments');
  departments.value = data.departments;
};

const viewDepartment = (dept) => {
  selectedDepartmentId.value = dept.id;
  showDepartmentModal.value = true;
};

const closeDepartmentModal = () => {
  showDepartmentModal.value = false;
  selectedDepartmentId.value = null;
};

const handleViewDoctor = (doctor) => {
  closeDepartmentModal();
  // Navigate back to dashboard - the dashboard will handle showing doctor details
  emit('navigate', 'dashboard');
};

const handleBookDoctor = (doctor) => {
  closeDepartmentModal();
  // Navigate back to dashboard - the dashboard will handle booking
  emit('navigate', 'dashboard');
};

onMounted(fetchDepartments);
</script>

<style scoped>
.departments-page {
  max-width: 1400px;
  margin: 0 auto;
}

.department-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.department-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
}

.department-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--serenity-primary), var(--serenity-secondary));
  color: white;
}
</style>

