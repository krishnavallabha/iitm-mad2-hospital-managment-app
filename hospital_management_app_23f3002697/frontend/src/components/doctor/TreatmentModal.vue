<template>
  <div class="modal-backdrop show d-flex align-items-center justify-content-center">
    <div class="card card-soft modal-content-wrapper">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <p class="text-muted small mb-1">SerenityCare Appointment</p>
            <h5 class="fw-bold mb-0">{{ appointment.patient_name }}</h5>
          </div>
          <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="$emit('close')">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="mb-3">
            <label class="form-label">Visit Type</label>
            <select class="form-select rounded-4" v-model="form.visit_type">
              <option value="In-person">In-person</option>
              <option value="Online">Online</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Diagnosis</label>
            <textarea class="form-control rounded-4" rows="2" v-model.trim="form.diagnosis" required></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Tests Done</label>
            <textarea class="form-control rounded-4" rows="2" v-model.trim="form.tests_done" placeholder="e.g. Blood Test, X-Ray"></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Medicines</label>
            <textarea class="form-control rounded-4" rows="3" v-model.trim="form.medicines" placeholder="List medicines..."></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Prescription / Notes</label>
            <textarea class="form-control rounded-4" rows="2" v-model.trim="form.prescription"></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Treatment Notes (Internal)</label>
            <textarea class="form-control rounded-4" rows="2" v-model.trim="form.notes"></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Attachments <span class="text-muted small">(Optional)</span></label>
            <div class="input-group">
              <input type="file" class="form-control rounded-pill" @change="handleFileUpload" multiple />
            </div>
            <div v-if="form.attachments && form.attachments.length" class="mt-2">
              <small class="text-muted d-block mb-1">Attached files:</small>
              <ul class="list-unstyled small mb-0">
                <li v-for="(file, index) in form.attachments" :key="index" class="d-flex align-items-center text-primary">
                  <i class="bi bi-paperclip me-2"></i>{{ file.name || file }}
                  <button type="button" class="btn btn-link btn-sm text-danger p-0 ms-2" @click="removeAttachment(index)">
                    <i class="bi bi-x"></i>
                  </button>
                </li>
              </ul>
            </div>
          </div>
          <div class="mb-3 row">
            <div class="col-6">
              <label class="form-label">Follow-up Date <span class="text-muted small">(Optional)</span></label>
              <input type="date" class="form-control rounded-4" v-model="form.follow_up_date" />
            </div>
            <div class="col-6">
              <label class="form-label">Follow-up Notes <span class="text-muted small">(Optional)</span></label>
              <input type="text" class="form-control rounded-4" v-model.trim="form.follow_up_notes" />
            </div>
          </div>
          <div v-if="error" class="alert alert-danger rounded-4 mb-3">
            {{ error }}
          </div>
          <div class="d-flex gap-2">
            <button 
              class="btn btn-outline-danger rounded-pill flex-grow-1" 
              type="button" 
              @click="handleCancel"
              :disabled="loading"
            >
              Cancel
            </button>
            <button 
              class="btn btn-success rounded-pill flex-grow-1" 
              type="submit"
              :disabled="loading || !form.diagnosis.trim()"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ loading ? 'Saving...' : 'Completed' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch, ref } from 'vue';
import api from '../../services/api';
import { useToast } from '../../composables/useToast';

const props = defineProps({
  appointment: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'saved']);

const toast = useToast();
const loading = ref(false);
const error = ref('');

const form = reactive({
  diagnosis: '',
  prescription: '',
  notes: '',
  follow_up_date: '',
  follow_up_notes: '',
  visit_type: 'In-person',
  tests_done: '',
  medicines: '',
  attachments: []
});

watch(
  () => props.appointment,
  (apt) => {
    if (apt?.treatment) {
      Object.assign(form, {
        diagnosis: apt.treatment.diagnosis || '',
        prescription: apt.treatment.prescription || '',
        notes: apt.treatment.notes || '',
        follow_up_date: apt.treatment.follow_up_date || '',
        follow_up_notes: apt.treatment.follow_up_notes || '',
        visit_type: apt.visit_type || 'In-person',
        tests_done: apt.treatment.tests_done || '',
        medicines: apt.treatment.medicines || '',
        attachments: apt.treatment.attachments ? JSON.parse(apt.treatment.attachments) : []
      });
    } else {
      Object.assign(form, {
        diagnosis: '',
        prescription: '',
        notes: '',
        follow_up_date: '',
        follow_up_notes: '',
        visit_type: apt.visit_type || 'In-person',
        tests_done: '',
        medicines: '',
        attachments: []
      });
    }
  },
  { immediate: true }
);

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files);
  // In a real app, we would upload these to a server and get URLs.
  // Here we'll just store the filenames for demonstration.
  const newAttachments = files.map(f => ({ name: f.name, size: f.size, type: f.type }));
  form.attachments = [...(form.attachments || []), ...newAttachments];
};

const removeAttachment = (index) => {
  form.attachments.splice(index, 1);
};

const handleCancel = () => {
  if (!loading.value) {
    emit('close');
  }
};

const handleSubmit = async () => {
  // Validate required fields
  if (!form.diagnosis.trim()) {
    error.value = 'Diagnosis is required';
    return;
  }

  error.value = '';
  loading.value = true;

  try {
    // Prepare payload - only include non-empty optional fields
    const payload = {
      diagnosis: form.diagnosis.trim(),
      visit_type: form.visit_type,
      prescription: form.prescription.trim() || null,
      notes: form.notes.trim() || null,
      tests_done: form.tests_done.trim() || null,
      medicines: form.medicines.trim() || null,
      attachments: form.attachments && form.attachments.length > 0 ? JSON.stringify(form.attachments) : null,
      follow_up_date: form.follow_up_date || null,
      follow_up_notes: form.follow_up_notes.trim() || null
    };

    const endpoint = `/doctor/appointments/${props.appointment.id}/treatment`;
    
    if (props.appointment.treatment) {
      await api.put(endpoint, payload);
      toast.success('Success', 'Treatment updated successfully');
    } else {
      await api.post(endpoint, payload);
      toast.success('Success', 'Treatment added successfully');
    }
    
    emit('saved');
    emit('close');
  } catch (err) {
    console.error('Treatment save failed:', err);
    error.value = err.response?.data?.error || 'Failed to save treatment. Please try again.';
    toast.error('Error', error.value);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  background: rgba(108, 117, 125, 1) !important;
  opacity: 1 !important;
  z-index: 999;
  padding: 1rem;
  overflow-y: auto;
  backdrop-filter: none !important;
}

.modal-backdrop::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(108, 117, 125, 1) !important;
  opacity: 1 !important;
  z-index: -1;
}

.modal-content-wrapper {
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  margin: auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-content-wrapper .card-body {
  overflow-y: auto;
  max-height: calc(90vh - 120px);
  padding: 1.5rem;
}

/* Smooth scrolling */
.modal-content-wrapper .card-body::-webkit-scrollbar {
  width: 8px;
}

.modal-content-wrapper .card-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.modal-content-wrapper .card-body::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

.modal-content-wrapper .card-body::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Responsive adjustments */
@media (max-width: 767.98px) {
  .modal-backdrop {
    padding: 0.5rem !important;
  }
  
  .modal-content-wrapper {
    max-width: 100% !important;
    max-height: 95vh !important;
    margin: 0 !important;
  }
  
  .modal-content-wrapper .card-body {
    max-height: calc(95vh - 100px);
    padding: 1rem !important;
    overflow-y: auto;
  }
  
  .form-control,
  .form-select,
  textarea {
    font-size: 16px; /* Prevents zoom on iOS */
  }
  
  .d-flex.gap-2 {
    flex-direction: column;
  }
  
  .d-flex.gap-2 .btn {
    width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .d-flex.gap-2 .btn:last-child {
    margin-bottom: 0;
  }
}

@media (max-width: 575.98px) {
  .modal-backdrop {
    padding: 0.25rem !important;
  }
  
  .modal-content-wrapper .card-body {
    padding: 0.75rem !important;
    max-height: calc(98vh - 80px);
  }
  
  h5 {
    font-size: 1rem;
  }
  
  .form-control,
  textarea {
    font-size: 16px;
  }
}
</style>
