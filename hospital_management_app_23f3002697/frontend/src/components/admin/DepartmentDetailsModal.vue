<template>
  <div class="modal-backdrop show d-flex align-items-center justify-content-center" @click.self="$emit('close')">
    <div class="card card-soft w-100 modal-card">
      <div class="card-body d-flex flex-column modal-body">
        <!-- Header Section - Fixed -->
        <div class="d-flex justify-content-between align-items-center mb-3 flex-shrink-0">
          <div>
            <h5 class="fw-bold mb-0">{{ department?.name }}</h5>
            <p class="text-muted small mb-0">{{ department?.description || 'No description available' }}</p>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-primary rounded-pill" @click="$emit('edit', department)" title="Edit Department">
              <i class="bi bi-pencil me-1"></i>Edit
            </button>
            <button 
              class="btn btn-sm btn-outline-danger rounded-pill" 
              @click="handleDelete" 
              title="Delete Department"
              :disabled="!department || !department.id"
            >
              <i class="bi bi-trash me-1"></i>Delete
            </button>
            <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="$emit('close')">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>

        <!-- Scrollable Content -->
        <div class="modal-content-scroll">
          <!-- Overview Section -->
          <div class="mb-4">
            <h6 class="fw-bold mb-3">Overview</h6>
            <div class="row g-3">
              <div class="col-md-4">
                <div class="card bg-light border-0">
                  <div class="card-body text-center">
                    <div class="fs-3 fw-bold text-primary">{{ department?.doctors?.length || 0 }}</div>
                    <div class="text-muted small">Total Doctors</div>
                  </div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="card bg-light border-0">
                  <div class="card-body text-center">
                    <div class="fs-3 fw-bold text-success">{{ department?.doctors_count || 0 }}</div>
                    <div class="text-muted small">Active Doctors</div>
                  </div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="card bg-light border-0">
                  <div class="card-body text-center">
                    <div class="fs-3 fw-bold text-info">{{ department?.id }}</div>
                    <div class="text-muted small">Department ID</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Doctors Section -->
          <div>
            <h6 class="fw-bold mb-3">Available Doctors</h6>
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="!department?.doctors || department.doctors.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-people fs-1 mb-2 d-block"></i>
              <p>No doctors found in this department.</p>
            </div>

            <div v-else class="d-flex flex-column gap-3">
              <div v-for="doctor in department.doctors" :key="doctor.id" class="card bg-light border-0">
                <div class="card-body">
                  <div class="d-flex align-items-center justify-content-between">
                    <div class="flex-grow-1">
                      <h6 class="fw-bold mb-1">Dr. {{ doctor.full_name || `${doctor.first_name} ${doctor.last_name}` }}</h6>
                      <p class="text-muted small mb-1" v-if="doctor.experience_years">
                        <i class="bi bi-briefcase me-1"></i>{{ doctor.experience_years }} years of experience
                      </p>
                      <p class="text-muted small mb-1" v-if="doctor.email">
                        <i class="bi bi-envelope me-1"></i>{{ doctor.email }}
                      </p>
                      <p class="text-muted small mb-0" v-if="doctor.phone">
                        <i class="bi bi-telephone me-1"></i>{{ doctor.phone }}
                      </p>
                    <p class="text-muted small mb-0 mt-2" v-if="doctor.bio">
                      {{ doctor.bio }}
                    </p>
                    <div v-if="doctor.positives" class="mt-2">
                      <span class="badge bg-success-subtle text-success rounded-pill me-1 mb-1" v-for="(positive, idx) in doctor.positives.split(',').filter(p => p.trim())" :key="idx">
                        <i class="bi bi-star-fill me-1"></i>{{ positive.trim() }}
                      </span>
                    </div>
                  </div>
                  <div class="ms-3">
                    <span class="badge bg-primary-subtle text-primary rounded-pill mb-2 d-block" v-if="doctor.license_number">
                      License: {{ doctor.license_number }}
                    </span>
                    <span class="badge rounded-pill d-block" :class="doctor.is_active ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">
                      {{ doctor.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </div>
                  </div>
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

const emit = defineEmits(['close', 'edit', 'delete']);

const loading = ref(true);
const department = ref(null);

const fetchDetails = async () => {
  loading.value = true;
  try {
    const { data } = await api.get(`/admin/departments/${props.departmentId}`);
    department.value = data.department;
  } catch (error) {
    console.error('Failed to fetch department details:', error);
  } finally {
    loading.value = false;
  }
};

const handleDelete = () => {
  console.log('Delete button clicked, department:', department.value);
  if (department.value && department.value.id) {
    console.log('Emitting delete event with department:', department.value);
    emit('delete', department.value);
  } else {
    console.error('Cannot delete: department data is incomplete', department.value);
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
  background: #6c757d !important; /* Solid opaque grey - 100% opacity */
  opacity: 1 !important; /* Force 100% opacity */
  z-index: 1055;
  padding: 1.5rem;
}

.modal-backdrop::before {
  display: none; /* Remove any pseudo-elements that might affect opacity */
}

.modal-card {
  max-width: 900px;
  max-height: 90vh;
  background: white !important;
  opacity: 1 !important;
  display: flex;
  flex-direction: column;
}

.modal-body {
  display: flex;
  flex-direction: column;
  min-height: 0; /* Important for flex scrolling */
  padding: 1.5rem;
}

.modal-content-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0; /* Important for flex scrolling */
  padding-right: 0.5rem; /* Space for scrollbar */
}

/* Custom scrollbar styling */
.modal-content-scroll::-webkit-scrollbar {
  width: 8px;
}

.modal-content-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.modal-content-scroll::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.modal-content-scroll::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Mobile Responsive */
@media (max-width: 767.98px) {
  .modal-backdrop {
    padding: 0.5rem !important;
  }
  
  .modal-card {
    max-width: 100% !important;
    max-height: 95vh !important;
  }
  
  .modal-body {
    padding: 1rem !important;
  }
  
  .modal-content-scroll {
    padding-right: 0.25rem;
  }
  
  .row.g-3 > * {
    margin-bottom: 0.75rem;
  }
  
  .col-md-4 {
    flex: 0 0 100%;
    max-width: 100%;
  }
}

@media (max-width: 575.98px) {
  .modal-backdrop {
    padding: 0.25rem !important;
  }
  
  .modal-card {
    max-height: 98vh !important;
  }
  
  .modal-body {
    padding: 0.75rem !important;
  }
  
  h5, h6 {
    font-size: 1rem;
  }
  
  .card-body {
    padding: 0.75rem !important;
  }
}
</style>

