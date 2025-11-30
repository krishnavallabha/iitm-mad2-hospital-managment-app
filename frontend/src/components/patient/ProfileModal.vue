<template>
  <div class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.75) !important; backdrop-filter: blur(4px);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow-lg rounded-4">
        <div class="modal-header border-0 pb-0">
          <h5 class="modal-title fw-bold">Edit Profile</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveProfile">
            <div class="row g-3">
              <div class="col-6">
                <label class="form-label">First Name</label>
                <input type="text" class="form-control rounded-pill" v-model="form.first_name" required />
              </div>
              <div class="col-6">
                <label class="form-label">Last Name</label>
                <input type="text" class="form-control rounded-pill" v-model="form.last_name" required />
              </div>
              <div class="col-12">
                <label class="form-label">Email</label>
                <input type="email" class="form-control rounded-pill" v-model="form.email" required />
              </div>
              <div class="col-12">
                <label class="form-label">Phone</label>
                <input type="tel" class="form-control rounded-pill" v-model="form.phone" />
              </div>
              <div class="col-12">
                <label class="form-label">Address</label>
                <textarea class="form-control rounded-4" rows="2" v-model="form.address"></textarea>
              </div>
              <div class="col-6">
                <label class="form-label">Date of Birth</label>
                <input type="date" class="form-control rounded-pill" v-model="form.dob" />
              </div>
              <div class="col-6">
                <label class="form-label">Gender</label>
                <select class="form-select rounded-pill" v-model="form.gender">
                  <option value="">Select</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            
            <div class="d-flex justify-content-end gap-2 mt-4">
              <button type="button" class="btn btn-light rounded-pill" @click="$emit('close')">Cancel</button>
              <button type="submit" class="btn btn-primary rounded-pill" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import api from '../../services/api';
import { useAuthStore } from '../../store/auth';

const emit = defineEmits(['close', 'saved']);
const auth = useAuthStore();
const loading = ref(false);

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  address: '',
  dob: '',
  gender: ''
});

onMounted(() => {
  // Pre-fill form with current user data
  const user = auth.state.user;
  if (user) {
    Object.keys(form).forEach(key => {
      if (user[key]) form[key] = user[key];
    });
  }
});

const saveProfile = async () => {
  loading.value = true;
  try {
    const { data } = await api.put('/patient/profile', form);
    // Update local user state
    auth.setSession({ ...auth.state.user, ...data.patient }, auth.state.token);
    emit('saved');
  } catch (error) {
    alert('Failed to update profile');
  } finally {
    loading.value = false;
  }
};
</script>
