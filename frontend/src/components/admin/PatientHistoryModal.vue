<template>
  <div class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.85); z-index: 1055;">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content border-0 shadow-lg rounded-4" style="max-height: 90vh;">
        <div class="modal-header border-0 pb-0">
          <div>
            <h5 class="modal-title fw-bold">Patient History</h5>
            <p class="text-muted small mb-0" v-if="patient">
              {{ patient.full_name }} ({{ patient.gender }}, {{ calculateAge(patient.date_of_birth) }} yrs)
            </p>
          </div>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body d-flex flex-column overflow-hidden">
          <div class="flex-grow-1 overflow-auto px-2">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="history.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-clipboard-x fs-1 mb-2"></i>
              <p>No medical history records found.</p>
            </div>

            <div v-else class="d-flex flex-column gap-3">
              <div v-for="record in history" :key="record.id" class="card bg-light border-0">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <h6 class="fw-bold mb-1">
                        {{ formatDate(record.appointment?.appointment_date) }}
                        <span v-if="record.appointment?.appointment_time" class="text-muted small ms-2">
                          {{ record.appointment.appointment_time }}
                        </span>
                      </h6>
                      <small class="text-muted">
                        <i class="bi bi-person-badge me-1"></i>
                        Dr. {{ record.appointment?.doctor_name || 'N/A' }}
                        <span v-if="record.appointment?.visit_type" class="badge bg-secondary-subtle text-secondary ms-2">
                          {{ record.appointment.visit_type }}
                        </span>
                      </small>
                    </div>
                  </div>
                  
                  <div class="row g-3">
                    <div class="col-12">
                      <label class="fw-semibold small text-muted d-block">Diagnosis</label>
                      <div>{{ record.diagnosis }}</div>
                    </div>
                    
                    <div class="col-md-6" v-if="record.tests_done">
                      <label class="fw-semibold small text-muted d-block">Tests Done</label>
                      <div>{{ record.tests_done }}</div>
                    </div>
                    
                    <div class="col-md-6" v-if="record.medicines">
                      <label class="fw-semibold small text-muted d-block">Medicines</label>
                      <div style="white-space: pre-line;">{{ record.medicines }}</div>
                    </div>
                    
                    <div class="col-12" v-if="record.prescription">
                      <label class="fw-semibold small text-muted d-block">Prescription / Notes</label>
                      <div>{{ record.prescription }}</div>
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
  patient: {
    type: Object,
    required: true
  }
});

defineEmits(['close']);

const loading = ref(true);
const history = ref([]);

const calculateAge = (dob) => {
  if (!dob) return 'N/A';
  const birthDate = new Date(dob);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const m = today.getMonth() - birthDate.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  } catch (e) {
    return dateString;
  }
};

const fetchHistory = async () => {
  loading.value = true;
  try {
    // Fetch treatment history for the patient
    const { data } = await api.get(`/history/treatments/patient/${props.patient.id}`);
    history.value = data.treatments || [];
  } catch (error) {
    console.error('Failed to fetch history:', error);
    history.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(fetchHistory);
</script>

<style scoped>
@media (max-width: 767.98px) {
  .modal-dialog {
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
  }
  
  .modal-content {
    max-height: 95vh !important;
    border-radius: 16px !important;
  }
  
  .modal-body {
    padding: 1rem !important;
    max-height: calc(95vh - 80px);
    overflow-y: auto;
  }
  
  .col-md-6 {
    flex: 0 0 100%;
    max-width: 100%;
    margin-bottom: 0.5rem;
  }
}

@media (max-width: 575.98px) {
  .modal-dialog {
    margin: 0.25rem;
    max-width: calc(100% - 0.5rem);
  }
  
  .modal-header {
    padding: 0.75rem;
  }
  
  .modal-title {
    font-size: 1rem;
  }
  
  .modal-body {
    padding: 0.75rem !important;
  }
  
  .card-body {
    padding: 0.75rem !important;
  }
  
  h6 {
    font-size: 0.9rem;
  }
}
</style>

