<template>
  <div class="modal-backdrop show d-flex align-items-center justify-content-center">
    <div class="card card-soft w-100" style="max-width: 520px;">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <p class="text-muted small mb-1">
              {{ appointment ? 'Reschedule Appointment' : 'Book With SerenityCare Doctor' }}
            </p>
            <h5 class="fw-bold mb-0">
              {{ doctor?.full_name || appointment?.doctor_name }}
            </h5>
          </div>
          <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="$emit('close')">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="mb-3">
            <label class="form-label">Date</label>
            <input type="date" class="form-control rounded-pill" v-model="form.appointment_date" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Time</label>
            <input type="time" class="form-control rounded-pill" v-model="form.appointment_time" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Reason</label>
            <textarea class="form-control rounded-4" rows="3" v-model.trim="form.reason" />
          </div>
          <div class="alert alert-info rounded-4" v-if="doctor?.availability?.length && !appointment">
            <p class="fw-semibold mb-1">Available Slots</p>
            <div class="d-flex flex-wrap gap-2">
              <button
                v-for="slot in doctor.availability"
                :key="slot.id"
                type="button"
                class="btn btn-outline-primary btn-sm rounded-pill"
                @click="selectSlot(slot)"
              >
                {{ slot.date }} · {{ slot.start_time }} - {{ slot.end_time }}
              </button>
            </div>
          </div>
          <div v-if="error" class="alert alert-danger rounded-4 mb-3">
            {{ error }}
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary rounded-pill flex-grow-1" type="button" @click="$emit('close')" :disabled="loading">
              Cancel
            </button>
            <button class="btn btn-primary rounded-pill flex-grow-1" type="submit" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ appointment ? 'Save Changes' : 'Book Appointment' }}
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

const props = defineProps({
  doctor: {
    type: Object,
    default: null
  },
  appointment: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'saved']);

const form = reactive({
  doctor_id: '',
  appointment_date: '',
  appointment_time: '',
  reason: ''
});

watch(
  () => props.doctor,
  (doc) => {
    if (doc) form.doctor_id = doc.id;
  },
  { immediate: true }
);

watch(
  () => props.appointment,
  (apt) => {
    if (apt) {
      Object.assign(form, {
        doctor_id: apt.doctor_id,
        appointment_date: apt.appointment_date,
        appointment_time: apt.appointment_time,
        reason: apt.reason
      });
    } else {
      form.appointment_date = '';
      form.appointment_time = '';
      form.reason = '';
    }
  },
  { immediate: true }
);

const selectSlot = (slot) => {
  form.appointment_date = slot.date;
  form.appointment_time = slot.start_time;
};

const error = ref('');
const loading = ref(false);

const handleSubmit = async () => {
  error.value = '';
  loading.value = true;
  try {
    if (props.appointment) {
      await api.put(`/patient/appointments/${props.appointment.id}`, form);
    } else {
      await api.post('/patient/appointments', form);
    }
    emit('saved');
  } catch (err) {
    console.error('Booking failed:', err);
    error.value = err.response?.data?.error || 'Failed to book appointment. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@media (max-width: 767.98px) {
  .modal-backdrop {
    padding: 0.5rem !important;
  }
  
  .modal-backdrop .card {
    max-width: 100% !important;
    margin: 0 !important;
  }
  
  .card-body {
    padding: 1rem !important;
  }
  
  .form-control,
  .form-select {
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
  
  .d-flex.flex-wrap.gap-2 .btn-sm {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
}

@media (max-width: 575.98px) {
  .modal-backdrop {
    padding: 0.25rem !important;
  }
  
  .card-body {
    padding: 0.75rem !important;
  }
  
  h5 {
    font-size: 1rem;
  }
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  background: #6c757d !important;
  opacity: 1 !important;
  z-index: 999;
  padding: 1.5rem;
  overflow-y: auto;
}
.card-soft {
  background-color: #f4f2f2 !important;
}

</style>

