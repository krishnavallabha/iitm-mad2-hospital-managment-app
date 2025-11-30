<template>
  <div class="modal fade show d-block" tabindex="-1" style="background: #6c757d !important; opacity: 1 !important;">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content border-0 shadow-lg rounded-4">
        <div class="modal-header border-0 pb-0">
          <h5 class="modal-title fw-bold">Patient History: {{ patientName }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body bg-light">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else>
            <!-- Filters -->
            <div class="row g-2 mb-3">
              <div class="col-md-6">
                <input type="text" class="form-control rounded-pill" placeholder="Search diagnosis, doctor, notes..." v-model="searchQuery">
              </div>
              <div class="col-md-3">
                <select class="form-select rounded-pill" v-model="filterType">
                  <option value="">All Records</option>
                  <option value="Diagnosis">Diagnosis</option>
                  <option value="Prescription">Prescription</option>
                </select>
              </div>
              <div class="col-md-3">
                <input type="date" class="form-control rounded-pill" v-model="filterDate">
              </div>
            </div>

            <div v-if="filteredHistory.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-journal-x fs-1 mb-2 d-block"></i>
              No records found matching your criteria.
            </div>
            
            <div v-else class="d-flex flex-column gap-3">
              <div v-for="record in filteredHistory" :key="record.id" class="card border-0 shadow-sm rounded-4">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <h6 class="fw-bold mb-0">{{ record.diagnosis }}</h6>
                      <small class="text-muted">{{ formatDate(record.appointment_date) }} • Dr. {{ record.doctor_name }}</small>
                    </div>
                    <span class="badge bg-primary-subtle text-primary rounded-pill">Treatment</span>
                  </div>
                  
                  <div v-if="record.prescription" class="mb-2">
                    <small class="text-uppercase text-muted fw-bold" style="font-size: 0.7rem;">Prescription</small>
                    <p class="mb-0 small">{{ record.prescription }}</p>
                  </div>
                  
                  <div v-if="record.notes" class="mb-2">
                    <small class="text-uppercase text-muted fw-bold" style="font-size: 0.7rem;">Notes</small>
                    <p class="mb-0 small text-muted">{{ record.notes }}</p>
                  </div>

                  <div v-if="record.attachments && record.attachments.length" class="mt-2 pt-2 border-top">
                    <small class="text-uppercase text-muted fw-bold" style="font-size: 0.7rem;">Attachments</small>
                    <div class="d-flex flex-wrap gap-2 mt-1">
                      <span v-for="(file, idx) in record.attachments" :key="idx" class="badge bg-light text-dark border">
                        <i class="bi bi-paperclip me-1"></i>{{ file.name || file }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer border-0">
          <button type="button" class="btn btn-primary rounded-pill" @click="$emit('close')">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../../services/api';

const props = defineProps({
  patientId: {
    type: Number,
    required: true
  },
  patientName: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['close']);
const loading = ref(true);
const history = ref([]);

const searchQuery = ref('');
const filterType = ref('');
const filterDate = ref('');

const fetchHistory = async () => {
  loading.value = true;
  try {
    const { data } = await api.get(`/history/appointments/patient/${props.patientId}`);
    history.value = data.appointments.map(apt => ({
      id: apt.id,
      appointment_date: apt.appointment_date,
      doctor_name: apt.doctor_name,
      diagnosis: apt.treatment?.diagnosis || 'N/A',
      prescription: apt.treatment?.prescription,
      notes: apt.treatment?.notes,
      attachments: apt.treatment?.attachments ? JSON.parse(apt.treatment.attachments) : []
    })).filter(apt => apt.diagnosis !== 'N/A');
  } catch (error) {
    console.error('Failed to fetch history', error);
  } finally {
    loading.value = false;
  }
};

const filteredHistory = computed(() => {
  return history.value.filter(record => {
    const matchesSearch = 
      record.diagnosis.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      record.doctor_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (record.notes && record.notes.toLowerCase().includes(searchQuery.value.toLowerCase()));
      
    const matchesType = !filterType.value || 
      (filterType.value === 'Diagnosis' && record.diagnosis) ||
      (filterType.value === 'Prescription' && record.prescription);
      
    const matchesDate = !filterDate.value || record.appointment_date === filterDate.value;
    
    return matchesSearch && matchesType && matchesDate;
  });
});

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

onMounted(() => {
  fetchHistory();
});
</script>
