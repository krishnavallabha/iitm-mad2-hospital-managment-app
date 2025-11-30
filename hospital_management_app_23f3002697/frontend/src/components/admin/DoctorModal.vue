<template>
  <div class="modal fade show d-block" tabindex="-1" style="background: rgba(50, 50, 50, 0.95); z-index: 1055;">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow-lg rounded-4 bg-white">
        <div class="modal-header border-0 pb-0">
          <h5 class="modal-title fw-bold">{{ doctor ? 'Edit Doctor' : 'Add Doctor' }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit" novalidate>
            <div class="row g-3">
              <div class="col-6">
                <label class="form-label">First Name</label>
                <input type="text" class="form-control rounded-3" v-model.trim="form.first_name" required />
              </div>
              <div class="col-6">
                <label class="form-label">Last Name</label>
                <input type="text" class="form-control rounded-3" v-model.trim="form.last_name" required />
              </div>
              <div class="col-12">
                <label class="form-label">Email</label>
                <input type="email" class="form-control rounded-3" v-model.trim="form.email" required />
              </div>
              <div class="col-6">
                <label class="form-label">Username</label>
                <input type="text" class="form-control rounded-3" v-model.trim="form.username" required />
              </div>
              <div class="col-6" v-if="!doctor">
                <label class="form-label">Password</label>
                <input type="password" class="form-control rounded-3" v-model.trim="form.password" autocomplete="new-password" required />
              </div>
              <div class="col-12">
                <label class="form-label">Specialization <span class="text-danger">*</span></label>
                <select 
                  class="form-select rounded-3" 
                  v-model="form.specialization_id" 
                  required
                  :key="`specialization-${departments.length}-${doctor?.id || 'new'}`"
                >
                  <option value="" disabled>Select specialization</option>
                  <optgroup label="Existing Departments" v-if="departments.length > 0">
                    <option v-for="dept in departments" :key="dept.id" :value="String(dept.id)">
                      {{ dept.name }}
                    </option>
                  </optgroup>
                  <optgroup label="Organ / System Specialists">
                    <option value="nephrologist">Nephrologist</option>
                    <option value="urologist">Urologist</option>
                    <option value="cardiologist">Cardiologist</option>
                    <option value="cardiothoracic-surgeon">Cardiothoracic Surgeon</option>
                    <option value="neurologist">Neurologist</option>
                    <option value="neurosurgeon">Neurosurgeon</option>
                    <option value="orthopedic-surgeon">Orthopedic Surgeon / Orthopedist</option>
                    <option value="rheumatologist">Rheumatologist</option>
                    <option value="pulmonologist">Pulmonologist</option>
                    <option value="thoracic-surgeon">Thoracic Surgeon</option>
                    <option value="gastroenterologist">Gastroenterologist</option>
                    <option value="hepatologist">Hepatologist</option>
                    <option value="dermatologist">Dermatologist</option>
                    <option value="ophthalmologist">Ophthalmologist</option>
                    <option value="optometrist">Optometrist</option>
                    <option value="ent-specialist">ENT Specialist (Otolaryngologist)</option>
                    <option value="dentist">Dentist</option>
                    <option value="oral-surgeon">Oral Surgeon</option>
                    <option value="periodontist">Periodontist</option>
                    <option value="orthodontist">Orthodontist</option>
                    <option value="endocrinologist">Endocrinologist</option>
                    <option value="hematologist">Hematologist</option>
                    <option value="oncologist">Oncologist</option>
                    <option value="gynecologist">Gynecologist</option>
                    <option value="obstetrician">Obstetrician</option>
                    <option value="andrologist">Andrologist</option>
                    <option value="immunologist">Immunologist</option>
                    <option value="palliative-care">Palliative Care Specialist</option>
                  </optgroup>
                  <optgroup label="Age-Based">
                    <option value="pediatrician">Pediatrician</option>
                    <option value="neonatologist">Neonatologist</option>
                    <option value="geriatrician">Geriatrician</option>
                  </optgroup>
                  <optgroup label="Surgical">
                    <option value="general-surgeon">General Surgeon</option>
                    <option value="plastic-surgeon">Plastic Surgeon</option>
                    <option value="orthopedic-surgeon-surgical">Orthopedic Surgeon</option>
                    <option value="cardiothoracic-surgeon-surgical">Cardiothoracic Surgeon</option>
                    <option value="neurosurgeon-surgical">Neurosurgeon</option>
                    <option value="vascular-surgeon">Vascular Surgeon</option>
                    <option value="colorectal-surgeon">Colorectal Surgeon</option>
                    <option value="trauma-surgeon">Trauma Surgeon</option>
                  </optgroup>
                  <optgroup label="Cancer">
                    <option value="medical-oncologist">Medical Oncologist</option>
                    <option value="surgical-oncologist">Surgical Oncologist</option>
                    <option value="radiation-oncologist">Radiation Oncologist</option>
                  </optgroup>
                  <optgroup label="Diagnostic / Lab">
                    <option value="radiologist">Radiologist</option>
                    <option value="pathologist">Pathologist</option>
                  </optgroup>
                  <optgroup label="Mental Health">
                    <option value="psychiatrist">Psychiatrist</option>
                    <option value="psychologist">Psychologist</option>
                  </optgroup>
                </select>
              </div>
              <div class="col-6">
                <label class="form-label">Phone</label>
                <input type="tel" class="form-control rounded-3" v-model.trim="form.phone" />
              </div>
              <div class="col-6">
                <label class="form-label">License</label>
                <input type="text" class="form-control rounded-3" v-model.trim="form.license_number" />
              </div>
              <div class="col-6">
                <label class="form-label">Experience (Years)</label>
                <input type="number" class="form-control rounded-3" v-model.number="form.experience_years" min="0" />
              </div>
              <div class="col-12">
                <label class="form-label">Bio</label>
                <textarea class="form-control rounded-4" rows="3" v-model.trim="form.bio" placeholder="Brief biography about the doctor..."></textarea>
              </div>
              <div class="col-12">
                <label class="form-label">Positives / Highlights</label>
                <textarea class="form-control rounded-4" rows="3" v-model.trim="form.positives" placeholder="Key highlights, achievements, or positive points about this doctor (e.g., 'Board certified, 20+ years experience, published researcher')"></textarea>
                <small class="text-muted">This will be displayed in department overviews and doctor listings</small>
              </div>
              <div class="col-12">
                <div class="form-check form-switch">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="isActive" 
                    v-model="form.is_active"
                  />
                  <label class="form-check-label" for="isActive">
                    <strong>{{ form.is_active ? 'Active' : 'Inactive' }}</strong>
                    <small class="text-muted d-block">Toggle doctor status</small>
                  </label>
                </div>
              </div>
            </div>
            <div class="d-flex gap-2 mt-4">
              <button class="btn btn-outline-secondary rounded-pill flex-grow-1" type="button" @click="$emit('close')">
                Cancel
              </button>
              <button class="btn btn-primary rounded-pill flex-grow-1" type="submit">
                Save Doctor
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue';
import api from '../../services/api';

const props = defineProps({
  departments: {
    type: Array,
    default: () => []
  },
  doctor: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'saved', 'refresh-departments']);

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  password: '',
  phone: '',
  license_number: '',
  experience_years: 0,
  specialization_id: '',
  bio: '',
  positives: '',
  is_active: true
});

watch(
  () => props.doctor,
  (doc) => {
    if (doc) {
      Object.assign(form, {
        first_name: doc.first_name || '',
        last_name: doc.last_name || '',
        email: doc.email || '',
        username: doc.username || '',
        password: '',
        phone: doc.phone || '',
        license_number: doc.license_number || '',
        experience_years: doc.experience_years || 0,
        specialization_id: doc.specialization_id ? String(doc.specialization_id) : '',
        bio: doc.bio || '',
        positives: doc.positives || '',
        is_active: doc.is_active !== undefined && doc.is_active !== null ? !!doc.is_active : true
      });
    } else {
      Object.assign(form, {
        first_name: '',
        last_name: '',
        email: '',
        username: '',
        password: '',
        phone: '',
        license_number: '',
        experience_years: 0,
        specialization_id: '',
        bio: '',
        positives: '',
        is_active: true
      });
    }
  },
  { immediate: true }
);

// Watch departments to ensure form updates when departments are loaded
watch(
  () => props.departments,
  (newDepts) => {
    // If editing and specialization_id is set but not matching any option, try to find it
    if (props.doctor && form.specialization_id && newDepts.length > 0) {
      const specId = parseInt(form.specialization_id);
      if (!isNaN(specId)) {
        const dept = newDepts.find(d => d.id === specId);
        if (dept) {
          form.specialization_id = String(specId);
        }
      }
    }
  },
  { immediate: true, deep: true }
);

// Map of specialization strings to display names
const specializationMap = {
  'nephrologist': 'Nephrologist',
  'urologist': 'Urologist',
  'cardiologist': 'Cardiologist',
  'cardiothoracic-surgeon': 'Cardiothoracic Surgeon',
  'neurologist': 'Neurologist',
  'neurosurgeon': 'Neurosurgeon',
  'orthopedic-surgeon': 'Orthopedic Surgeon / Orthopedist',
  'rheumatologist': 'Rheumatologist',
  'pulmonologist': 'Pulmonologist',
  'thoracic-surgeon': 'Thoracic Surgeon',
  'gastroenterologist': 'Gastroenterologist',
  'hepatologist': 'Hepatologist',
  'dermatologist': 'Dermatologist',
  'ophthalmologist': 'Ophthalmologist',
  'optometrist': 'Optometrist',
  'ent-specialist': 'ENT Specialist (Otolaryngologist)',
  'dentist': 'Dentist',
  'oral-surgeon': 'Oral Surgeon',
  'periodontist': 'Periodontist',
  'orthodontist': 'Orthodontist',
  'endocrinologist': 'Endocrinologist',
  'hematologist': 'Hematologist',
  'oncologist': 'Oncologist',
  'gynecologist': 'Gynecologist',
  'obstetrician': 'Obstetrician',
  'andrologist': 'Andrologist',
  'immunologist': 'Immunologist',
  'palliative-care': 'Palliative Care Specialist',
  'pediatrician': 'Pediatrician',
  'neonatologist': 'Neonatologist',
  'geriatrician': 'Geriatrician',
  'general-surgeon': 'General Surgeon',
  'plastic-surgeon': 'Plastic Surgeon',
  'orthopedic-surgeon-surgical': 'Orthopedic Surgeon',
  'cardiothoracic-surgeon-surgical': 'Cardiothoracic Surgeon',
  'neurosurgeon-surgical': 'Neurosurgeon',
  'vascular-surgeon': 'Vascular Surgeon',
  'colorectal-surgeon': 'Colorectal Surgeon',
  'trauma-surgeon': 'Trauma Surgeon',
  'medical-oncologist': 'Medical Oncologist',
  'surgical-oncologist': 'Surgical Oncologist',
  'radiation-oncologist': 'Radiation Oncologist',
  'radiologist': 'Radiologist',
  'pathologist': 'Pathologist',
  'psychiatrist': 'Psychiatrist',
  'psychologist': 'Psychologist'
};

const findOrCreateDepartment = async (specValue) => {
  if (!specValue || specValue === '') {
    throw new Error('Please select a specialization');
  }
  
  // If it's already a number (existing department ID), return it
  const numValue = parseInt(specValue);
  if (!isNaN(numValue) && String(numValue) === String(specValue)) {
    // It's a numeric ID
    const dept = props.departments.find(d => d.id === numValue);
    if (dept) {
      return numValue;
    }
    // If not found in props, it might be a valid ID from database
    return numValue;
  }
  
  // If it's a string specialization key, find existing department by name or create it
  const deptName = specializationMap[specValue];
  if (!deptName) {
    throw new Error(`Invalid specialization: ${specValue}`);
  }
  
  // Check if department already exists in the database
  const existing = props.departments.find(d => 
    d.name.toLowerCase() === deptName.toLowerCase()
  );
  
  if (existing) {
    return existing.id;
  }
  
  // Create new department
  try {
    console.error('[INFO] Creating new department:', deptName);
    const { data } = await api.post('/admin/departments', {
      name: deptName,
      description: `${deptName} specialization`
    });
    // Emit event to refresh departments in parent
    emit('refresh-departments');
    return data.department.id;
  } catch (error) {
    console.error('Failed to create department:', error);
    const errorMsg = error.response?.data?.error || 'Failed to create department';
    throw new Error(errorMsg);
  }
};

const handleSubmit = async () => {
  try {
    // Validate required fields
    if (!form.first_name || !form.last_name || !form.email || !form.username) {
      if (window.$toast) {
        window.$toast.warning('Validation', 'Please fill in all required fields');
      } else {
        alert('Please fill in all required fields');
      }
      return;
    }
    
    if (!props.doctor && !form.password) {
      if (window.$toast) {
        window.$toast.warning('Validation', 'Password is required for new doctors');
      } else {
        alert('Password is required for new doctors');
      }
      return;
    }
    
    if (!form.specialization_id) {
      if (window.$toast) {
        window.$toast.warning('Validation', 'Please select a specialization');
      } else {
        alert('Please select a specialization');
      }
      return;
    }
    
    // Convert specialization string to department ID if needed
    let specializationId;
    try {
      specializationId = await findOrCreateDepartment(form.specialization_id);
    } catch (error) {
      alert(error.message || 'Failed to process specialization');
      return;
    }
    
    // Prepare submit data
    const submitData = {
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      email: form.email.trim(),
      username: form.username.trim(),
      phone: form.phone ? form.phone.trim() : null,
      license_number: form.license_number ? form.license_number.trim() : null,
      experience_years: form.experience_years || 0,
      specialization_id: specializationId,
      bio: form.bio ? form.bio.trim() : null,
      positives: form.positives ? form.positives.trim() : null,
      is_active: form.is_active
    };
    
    // Only include password for new doctors
    if (!props.doctor && form.password) {
      submitData.password = form.password;
    }
    
    if (props.doctor) {
      await api.put(`/admin/doctors/${props.doctor.id}`, submitData);
    } else {
      await api.post('/admin/doctors', submitData);
    }
    
    emit('saved');
  } catch (error) {
    console.error('Error saving doctor:', error);
    const errorMsg = error.response?.data?.error || error.message || 'Failed to save doctor';
    if (window.$toast) {
      window.$toast.error('Error', errorMsg);
    } else {
      alert(errorMsg);
    }
  }
};
</script>

<style scoped>
@media (max-width: 767.98px) {
  .modal-dialog {
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
  }
  
  .modal-content {
    border-radius: 16px !important;
  }
  
  .modal-body {
    padding: 1rem;
    max-height: calc(100vh - 120px);
    overflow-y: auto;
  }
  
  .modal-body .row {
    margin: 0;
  }
  
  .modal-body .col-6,
  .modal-body .col-12 {
    padding: 0.5rem;
  }
  
  .form-control,
  .form-select {
    font-size: 16px; /* Prevents zoom on iOS */
  }
  
  .btn {
    width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .btn:last-child {
    margin-bottom: 0;
  }
}

@media (max-width: 575.98px) {
  .modal-dialog {
    margin: 0.25rem;
    max-width: calc(100% - 0.5rem);
  }
  
  .modal-header {
    padding: 1rem 0.75rem 0.5rem 0.75rem;
  }
  
  .modal-title {
    font-size: 1.1rem;
  }
  
  .modal-body {
    padding: 0.75rem;
  }
}
</style>


