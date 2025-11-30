<template>
  <div class="modal-backdrop show d-flex align-items-center justify-content-center">
    <div class="card card-soft w-100" style="max-width: 640px;">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-bold mb-0">Update Availability</h5>
          <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="$emit('close')">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <p class="text-muted small">
          Manage SerenityCare availability slots for the next 7 days. This helps patients
          see real-time booking windows.
        </p>
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="availability-list mb-3">
            <div v-for="(slot, index) in slots" :key="index" class="p-3 rounded-4 bg-light mb-3">
              <div class="row g-3 align-items-end">
                <div class="col-md-4">
                  <label class="form-label">Date</label>
                  <input type="date" class="form-control" v-model="slot.date" required />
                </div>
                <div class="col-md-3">
                  <label class="form-label">Start</label>
                  <input type="time" class="form-control" v-model="slot.start_time" required />
                </div>
                <div class="col-md-3">
                  <label class="form-label">End</label>
                  <input type="time" class="form-control" v-model="slot.end_time" required />
                </div>
                <div class="col-md-2 text-end">
                  <label class="form-label d-block">Status</label>
                  <div class="form-check form-switch">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      v-model="slot.is_available"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="d-flex justify-content-between">
            <button class="btn btn-outline-secondary rounded-pill" type="button" @click="addSlot">
              Add Slot
            </button>
            <div class="d-flex gap-2">
              <button class="btn btn-outline-secondary rounded-pill" type="button" @click="$emit('close')">
                Cancel
              </button>
              <button class="btn btn-primary rounded-pill" type="submit">Save Availability</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import api from '../../services/api';

const props = defineProps({
  currentSlots: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['close', 'saved']);

const slots = reactive(
  props.currentSlots.length
    ? props.currentSlots.map((slot) => ({
        date: slot.date,
        start_time: slot.start_time,
        end_time: slot.end_time,
        is_available: slot.is_available
      }))
    : [
        {
          date: new Date().toISOString().split('T')[0],
          start_time: '09:00',
          end_time: '13:00',
          is_available: true
        }
      ]
);

const addSlot = () => {
  slots.push({
    date: new Date().toISOString().split('T')[0],
    start_time: '09:00',
    end_time: '13:00',
    is_available: true
  });
};

const handleSubmit = async () => {
  await api.post('/doctor/availability', slots);
  emit('saved');
};
</script>

<style scoped>
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
</style>

