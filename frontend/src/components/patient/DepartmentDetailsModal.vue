<template>
  <div class="modal-backdrop show d-flex align-items-center justify-content-center">
    <div class="card card-soft w-100" style="max-width: 800px; max-height: 90vh;">
      <div class="card-body d-flex flex-column h-100">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h5 class="fw-bold mb-0">{{ department?.name }}</h5>
            <p class="text-muted small mb-0">{{ department?.description }}</p>
          </div>
          <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="$emit('close')">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="flex-grow-1 overflow-auto">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div v-else-if="doctors.length === 0" class="text-center py-5 text-muted">
            <i class="bi bi-people fs-1 mb-2"></i>
            <p>No doctors found in this department.</p>
          </div>

          <div v-else class="d-flex flex-column gap-3">
            <div v-for="doctor in doctors" :key="doctor.id" class="card bg-light border-0">
              <div class="card-body d-flex align-items-center justify-content-between">
                <div>
                  <h6 class="fw-bold mb-1">Dr. {{ doctor.first_name }} {{ doctor.last_name }}</h6>
                  <p class="text-muted small mb-1">{{ doctor.experience_years }} years experience</p>
                  <p class="text-muted small mb-0">{{ doctor.bio || 'No bio available' }}</p>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn btn-sm btn-outline-primary rounded-pill" @click="$emit('view-doctor', doctor)">
                    View Details
                  </button>
                  <button class="btn btn-sm btn-primary rounded-pill" @click="$emit('book-doctor', doctor)">
                    Book Appointment
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const props = defineProps({
  departmentId: {
    type: Number,
    required: true
  }
});

defineEmits(['close', 'view-doctor', 'book-doctor']);

const loading = ref(true);
const department = ref(null);
const doctors = ref([]);

const fetchDetails = async () => {
  loading.value = true;
  try {
    const { data } = await api.get(`/patient/departments/${props.departmentId}`);
    department.value = data.department;
    doctors.value = data.department.doctors;
  } catch (error) {
    console.error('Failed to fetch department details:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchDetails);
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.75) !important;
  backdrop-filter: blur(4px);
  z-index: 999;
  padding: 1.5rem;
}
</style>
