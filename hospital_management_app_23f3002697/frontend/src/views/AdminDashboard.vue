<template>
  <div class="admin-dashboard">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading dashboard...</p>
    </div>

    <!-- Main Content -->
    <div v-else>
     <!-- Navigation Tabs -->
    <div class="admin-nav-tabs mb-3 mb-md-4">
      <div class="card card-soft border-0 shadow-sm">
        <div class="card-body p-2 p-md-3">
          <ul class="nav nav-pills nav-fill gap-1 gap-md-2 flex-wrap">
            <li class="nav-item flex-fill">
              <button
                class="nav-link rounded-pill w-100"
                :class="{ active: activeTab === 'overview' }"
                @click="activeTab = 'overview'"
              >
                <i class="bi bi-speedometer2 me-1 me-md-2"></i>
                <span class="d-none d-sm-inline">Overview</span>
                <span class="d-sm-none">Overview</span>
              </button>
            </li>
            <li class="nav-item flex-fill">
              <button
                class="nav-link rounded-pill w-100"
                :class="{ active: activeTab === 'analytics' }"
                @click="activeTab = 'analytics'"
              >
                <i class="bi bi-graph-up me-1 me-md-2"></i>
                <span class="d-none d-sm-inline">Analytics</span>
                <span class="d-sm-none">Analytics</span>
              </button>
            </li>
            <li class="nav-item flex-fill">
              <button
                class="nav-link rounded-pill w-100"
                :class="{ active: activeTab === 'departments' }"
                @click="activeTab = 'departments'"
              >
                <i class="bi bi-building me-1 me-md-2"></i>
                <span class="d-none d-sm-inline">Departments</span>
                <span class="d-sm-none">Dept</span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Overview Tab Content -->
    <div v-if="activeTab === 'overview'" class="overview-content">
      <!-- Key Metrics -->
      <div class="row g-4 mb-4">
        <div class="col-12 col-lg-3" v-for="metric in metrics" :key="metric.label">
          <div class="card card-soft border-0 shadow-sm h-100 metric-card">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <div class="metric-icon rounded-circle d-flex align-items-center justify-content-center" :class="metric.iconClass">
                  <i :class="metric.icon"></i>
                </div>
                <span class="badge rounded-pill" :class="metric.badgeClass">{{ metric.trend }}</span>
              </div>
              <p class="text-uppercase text-muted small mb-1">{{ metric.label }}</p>
              <h3 class="fw-bold mb-0">{{ metric.value }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="row g-4">
        <!-- Doctors Section -->
        <div class="col-12 col-lg-6">
          <div class="card card-soft border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <h5 class="fw-bold mb-1">Doctors</h5>
                  <p class="text-muted small mb-0">Manage SerenityCare medical staff</p>
                </div>
                <button class="btn btn-primary rounded-pill btn-sm" @click="showDoctorModal = true">
                  <i class="bi bi-plus-lg me-2"></i>Add Doctor
                </button>
              </div>
              <EnhancedSearch
                v-model="doctorFilters.search"
                :result-count="doctors.length"
                result-label="doctors"
                @search="fetchDoctors"
                @clear="fetchDoctors"
              >
                <template #filters>
                  <div class="col-md-6">
                    <label class="form-label small">Specialization</label>
                    <select
                      class="form-select form-select-sm"
                      v-model="doctorFilters.specialization_id"
                      @change="fetchDoctors"
                    >
                      <option value="">All Specializations</option>
                      <option
                        v-for="dept in departments"
                        :key="dept.id"
                        :value="dept.id"
                      >
                        {{ dept.name }}
                      </option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small">Status</label>
                    <select
                      class="form-select form-select-sm"
                      v-model="doctorFilters.status"
                      @change="fetchDoctors"
                    >
                      <option value="">All Status</option>
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </template>
              </EnhancedSearch>
              <div class="table-responsive mt-3">
                <table class="table align-middle table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Name</th>
                      <th>Specialization</th>
                      <th>Status</th>
                      <th class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="doctor in doctors.slice(0, 5)" :key="doctor.id">
                      <td>
                        <div class="fw-semibold">{{ doctor.full_name }}</div>
                        <small class="text-muted">{{ doctor.email }}</small>
                      </td>
                      <td>{{ doctor.specialization }}</td>
                      <td>
                        <span class="badge rounded-pill" :class="doctor.is_active ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">
                          {{ doctor.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary rounded-pill me-2" @click="editDoctor(doctor)">
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          class="btn btn-sm btn-outline-danger rounded-pill" 
                          @click.stop="deleteDoctor(doctor)"
                          type="button"
                          title="Permanently delete doctor"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </td>
                    </tr>
                    <tr v-if="doctors.length === 0">
                      <td colspan="4" class="text-center text-muted py-4">No doctors found</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-if="doctors.length > 5" class="text-center mt-3">
                <button class="btn btn-outline-primary rounded-pill btn-sm" @click="activeTab = 'departments'">
                  View All Doctors
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Patients Section -->
        <div class="col-12 col-lg-6">
          <div class="card card-soft border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <h5 class="fw-bold mb-1">Patients</h5>
                  <p class="text-muted small mb-0">Manage patient records</p>
                </div>
              </div>
              <EnhancedSearch
                v-model="patientSearch"
                :result-count="patients.length"
                result-label="patients"
                @search="fetchPatients"
                @clear="fetchPatients"
              >
                <template #filters>
                  <div class="col-md-12">
                    <label class="form-label small">Status</label>
                    <select
                      class="form-select form-select-sm"
                      v-model="patientFilters.status"
                      @change="fetchPatients"
                    >
                      <option value="">All Status</option>
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </template>
              </EnhancedSearch>
              <div class="table-responsive mt-3">
                <table class="table align-middle table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Name</th>
                      <th>Contact</th>
                      <th>Status</th>
                      <th class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="patient in patients.slice(0, 5)" :key="patient.id">
                      <td>
                        <div class="fw-semibold">{{ patient.full_name }}</div>
                        <small class="text-muted">{{ patient.email }}</small>
                      </td>
                      <td>{{ patient.phone || 'N/A' }}</td>
                      <td>
                        <span class="badge rounded-pill" :class="patient.is_active ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">
                          {{ patient.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary rounded-pill me-2" @click="editPatient(patient)">
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          class="btn btn-sm btn-outline-danger rounded-pill me-2" 
                          @click.stop="deletePatient(patient)"
                          type="button"
                          title="Permanently delete patient"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info rounded-pill" @click="viewPatientHistory(patient)">
                          <i class="bi bi-clock-history"></i>
                        </button>
                      </td>
                    </tr>
                    <tr v-if="patients.length === 0">
                      <td colspan="4" class="text-center text-muted py-4">No patients found</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-if="patients.length > 5" class="text-center mt-3">
                <button class="btn btn-outline-primary rounded-pill btn-sm">
                  View All Patients
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Appointments Section -->
      <div class="row g-4 mt-2">
        <div class="col-12">
          <div class="card card-soft border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <h5 class="fw-bold mb-1">Recent Appointments</h5>
                  <p class="text-muted small mb-0">Latest appointment activity</p>
                </div>
                <div class="d-flex gap-2">
                  <button
                    class="btn rounded-pill btn-sm"
                    :class="showCalendarView ? 'btn-outline-primary' : 'btn-primary'"
                    @click="showCalendarView = false"
                  >
                    <i class="bi bi-list me-2"></i>List
                  </button>
                  <button
                    class="btn rounded-pill btn-sm"
                    :class="showCalendarView ? 'btn-primary' : 'btn-outline-primary'"
                    @click="showCalendarView = true"
                  >
                    <i class="bi bi-calendar3 me-2"></i>Calendar
                  </button>
                  <select class="form-select form-select-sm rounded-pill w-auto" v-model="appointmentStatus" @change="fetchAppointments">
                    <option value="">All Status</option>
                    <option value="Booked">Booked</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                  </select>
                </div>
              </div>
              
              <AppointmentCalendar
                v-if="showCalendarView"
                :appointments="formattedAppointments"
                @appointment-selected="handleAppointmentSelected"
              />
              
              <div v-else class="table-responsive">
                <table class="table align-middle table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Patient</th>
                      <th>Doctor</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="apt in appointments.slice(0, 10)" :key="apt.id">
                      <td>{{ apt.patient_name || 'N/A' }}</td>
                      <td>{{ apt.doctor_name ? `Dr. ${apt.doctor_name}` : 'N/A' }}</td>
                      <td>{{ apt.appointment_date ? new Date(apt.appointment_date).toLocaleDateString() : 'N/A' }}</td>
                      <td>{{ apt.appointment_time || 'N/A' }}</td>
                      <td>
                        <span class="badge rounded-pill" :class="statusBadge(apt.status)">
                          {{ apt.status }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="appointments.length === 0">
                      <td colspan="5" class="text-center text-muted py-4">No appointments found</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Tab Content -->
    <AdminAnalytics v-if="activeTab === 'analytics'" />

    <!-- Departments Tab Content -->
    <AdminDepartments v-if="activeTab === 'departments'" />

    <!-- Modals -->
    <DoctorModal
      v-if="showDoctorModal"
      :departments="departments"
      :doctor="editingDoctor"
      @close="closeDoctorModal"
      @saved="handleDoctorSaved"
      @refresh-departments="fetchDepartments"
    />

    <PatientModal
      v-if="showPatientModal"
      :patient="editingPatient"
      @close="closePatientModal"
      @saved="handlePatientSaved"
    />

    <PatientHistoryModal
      v-if="showHistoryModal"
      :patient="selectedPatientHistory"
      @close="closeHistoryModal"
    />

    <ConfirmationDialog
      v-model:visible="confirm.state.visible"
      :title="confirm.state.title"
      :message="confirm.state.message"
      :details="confirm.state.details"
      :type="confirm.state.type"
      :confirm-text="confirm.state.confirmText"
      :cancel-text="confirm.state.cancelText"
      :loading="confirm.state.loading"
      @confirm="confirm.confirm"
      @cancel="confirm.hide"
    />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../services/api';
import DoctorModal from '../components/admin/DoctorModal.vue';
import PatientModal from '../components/admin/PatientModal.vue';
import PatientHistoryModal from '../components/admin/PatientHistoryModal.vue';
import EnhancedSearch from '../components/common/EnhancedSearch.vue';
import AppointmentCalendar from '../components/common/AppointmentCalendar.vue';
import ConfirmationDialog from '../components/common/ConfirmationDialog.vue';
import AdminAnalytics from './AdminAnalytics.vue';
import AdminDepartments from './AdminDepartments.vue';
import { useConfirm } from '../composables/useConfirm';
import { useToast } from '../composables/useToast';

const activeTab = ref('overview');
const metrics = ref([]);
const doctors = ref([]);
const patients = ref([]);
const appointments = ref([]);
const departments = ref([]);
const analyticsError = ref(null);
const loading = ref(true);

const doctorFilters = reactive({
  search: '',
  specialization_id: '',
  status: ''
});
const patientSearch = ref('');
const patientFilters = reactive({
  status: ''
});
const appointmentStatus = ref('');
const showDoctorModal = ref(false);
const editingDoctor = ref(null);
const showPatientModal = ref(false);
const editingPatient = ref(null);
const showHistoryModal = ref(false);
const selectedPatientHistory = ref(null);
const showCalendarView = ref(false);

const confirm = useConfirm();
const toast = useToast();

const fetchDashboard = async () => {
  try {
    const { data } = await api.get('/admin/dashboard');
    metrics.value = [
      {
        label: 'Doctors',
        value: data.statistics.total_doctors,
        trend: '+4%',
        badgeClass: 'bg-success-subtle text-success',
        icon: 'bi bi-people',
        iconClass: 'bg-success-subtle text-success'
      },
      {
        label: 'Patients',
        value: data.statistics.total_patients,
        trend: '+8%',
        badgeClass: 'bg-primary-subtle text-primary',
        icon: 'bi bi-person-heart',
        iconClass: 'bg-primary-subtle text-primary'
      },
      {
        label: 'Appointments',
        value: data.statistics.total_appointments,
        trend: '+12%',
        badgeClass: 'bg-info-subtle text-info',
        icon: 'bi bi-calendar-check',
        iconClass: 'bg-info-subtle text-info'
      },
      {
        label: 'Departments',
        value: data.statistics.total_departments || departments.value.length,
        trend: 'Stable',
        badgeClass: 'bg-warning-subtle text-warning',
        icon: 'bi bi-building',
        iconClass: 'bg-warning-subtle text-warning'
      }
    ];
  } catch (error) {
    console.error('[ERROR] Dashboard fetch failed:', error);
    toast.error('Error', 'Failed to load dashboard data');
  }
};

const fetchDoctors = async () => {
  try {
    const params = {};
    if (doctorFilters.search) params.search = doctorFilters.search;
    if (doctorFilters.specialization_id) params.specialization_id = doctorFilters.specialization_id;
    if (doctorFilters.status) params.is_active = doctorFilters.status === 'active';
    
    const { data } = await api.get('/admin/doctors', { params });
    const allDoctors = data.doctors.map((doc) => ({
      ...doc,
      full_name: doc.full_name || `${doc.first_name} ${doc.last_name}`
    }));
    
    let filtered = allDoctors;
    if (doctorFilters.search) {
      const searchLower = doctorFilters.search.toLowerCase();
      filtered = filtered.filter(doc => 
        doc.full_name.toLowerCase().includes(searchLower) ||
        doc.email.toLowerCase().includes(searchLower) ||
        doc.specialization?.toLowerCase().includes(searchLower)
      );
    }
    
    doctors.value = filtered;
  } catch (error) {
    toast.error('Error', 'Failed to fetch doctors');
    console.error('Error fetching doctors:', error);
  }
};

const fetchPatients = async () => {
  try {
    const params = {};
    if (patientSearch.value) params.search = patientSearch.value;
    if (patientFilters.status) params.is_active = patientFilters.status === 'active';
    
    const { data } = await api.get('/admin/patients', { params });
    const allPatients = data.patients.map((patient) => ({
      ...patient,
      full_name: patient.full_name || `${patient.first_name} ${patient.last_name}`
    }));

    let filtered = allPatients;
    if (patientSearch.value) {
      const searchLower = patientSearch.value.toLowerCase();
      filtered = filtered.filter(patient => 
        patient.full_name.toLowerCase().includes(searchLower) ||
        patient.email?.toLowerCase().includes(searchLower)
      );
    }
    
    patients.value = filtered;
  } catch (error) {
    toast.error('Error', 'Failed to fetch patients');
    console.error('Error fetching patients:', error);
  }
};

const fetchAppointments = async () => {
  try {
    const { data } = await api.get('/admin/appointments', {
      params: {
        status: appointmentStatus.value || undefined
      }
    });
    appointments.value = data.appointments;
  } catch (error) {
    toast.error('Error', 'Failed to fetch appointments');
    console.error('Error fetching appointments:', error);
  }
};

const formattedAppointments = computed(() => {
  return appointments.value.map(apt => ({
    id: apt.id,
    date: apt.appointment_date,
    appointment_date: apt.appointment_date,
    time: apt.appointment_time,
    appointment_time: apt.appointment_time,
    status: apt.status,
    patient_name: apt.patient_name || (apt.patient ? `${apt.patient.first_name} ${apt.patient.last_name}` : 'N/A'),
    doctor_name: apt.doctor_name || (apt.doctor ? `Dr. ${apt.doctor.first_name} ${apt.doctor.last_name}` : 'N/A'),
    reason: apt.reason
  }));
});

const handleAppointmentSelected = (appointment) => {
  console.log('Appointment selected:', appointment);
};

const fetchDepartments = async () => {
  try {
    const { data } = await api.get('/admin/departments');
    departments.value = data.departments;
  } catch (error) {
    console.error('Error fetching departments:', error);
  }
};

const editDoctor = (doctor) => {
  editingDoctor.value = doctor;
  showDoctorModal.value = true;
};

const closeDoctorModal = () => {
  showDoctorModal.value = false;
  editingDoctor.value = null;
};

const handleDoctorSaved = () => {
  closeDoctorModal();
  fetchDoctors();
  toast.success('Success', 'Doctor saved successfully');
};

const deleteDoctor = async (doctor) => {
  console.log('Delete doctor button clicked:', doctor);
  
  if (!doctor || !doctor.id) {
    console.error('Invalid doctor object:', doctor);
    toast.error('Error', 'Invalid doctor information');
    return;
  }
  
  // Use browser confirm directly
  const confirmed = window.confirm(
    `WARNING: Are you sure you want to PERMANENTLY DELETE ${doctor.full_name || doctor.first_name + ' ' + doctor.last_name}?\n\nThis action cannot be undone! This will permanently delete the doctor account and all associated data including appointments and availability.`
  );
  
  if (!confirmed) {
    console.log('User cancelled deletion');
    return;
  }
  
  // User confirmed - proceed with deletion
  try {
    console.log('Calling API to delete doctor:', doctor.id);
    const response = await api.delete(`/admin/doctors/${doctor.id}`);
    console.log('Delete response:', response);
    const doctorName = doctor.full_name || `${doctor.first_name} ${doctor.last_name}`;
    toast.success('Success', `${doctorName} has been deleted permanently`);
    await fetchDoctors();
  } catch (error) {
    console.error('Error deleting doctor:', error);
    console.error('Error details:', error.response);
    const errorMsg = error.response?.data?.error || error.message || 'Failed to delete doctor';
    toast.error('Error', errorMsg);
  }
};

const editPatient = (patient) => {
  editingPatient.value = patient;
  showPatientModal.value = true;
};

const closePatientModal = () => {
  showPatientModal.value = false;
  editingPatient.value = null;
};

const handlePatientSaved = () => {
  const wasEdit = !!editingPatient.value;
  closePatientModal();
  fetchPatients();
  toast.success('Success', wasEdit ? 'Patient updated successfully' : 'Patient added successfully');
};

const deletePatient = async (patient) => {
  console.log('Delete patient button clicked:', patient);
  
  if (!patient || !patient.id) {
    console.error('Invalid patient object:', patient);
    toast.error('Error', 'Invalid patient information');
    return;
  }
  
  // Use browser confirm directly
  const confirmed = window.confirm(
    `WARNING: Are you sure you want to PERMANENTLY DELETE ${patient.full_name || patient.first_name + ' ' + patient.last_name}?\n\nThis action cannot be undone! This will permanently delete the patient account and all associated data including appointments and treatment history.`
  );
  
  if (!confirmed) {
    console.log('User cancelled deletion');
    return;
  }
  
  // User confirmed - proceed with deletion
  try {
    console.log('Calling API to delete patient:', patient.id);
    const response = await api.delete(`/admin/patients/${patient.id}`);
    console.log('Delete response:', response);
    const patientName = patient.full_name || `${patient.first_name} ${patient.last_name}`;
    toast.success('Success', `${patientName} has been deleted permanently`);
    await fetchPatients();
  } catch (error) {
    console.error('Error deleting patient:', error);
    console.error('Error details:', error.response);
    const errorMsg = error.response?.data?.error || error.message || 'Failed to delete patient';
    toast.error('Error', errorMsg);
  }
};

const viewPatientHistory = (patient) => {
  selectedPatientHistory.value = patient;
  showHistoryModal.value = true;
};

const closeHistoryModal = () => {
  showHistoryModal.value = false;
  selectedPatientHistory.value = null;
};

const statusBadge = (status) => {
  switch (status) {
    case 'Completed':
      return 'bg-success-subtle text-success';
    case 'Cancelled':
      return 'bg-danger-subtle text-danger';
    default:
      return 'bg-warning-subtle text-warning';
  }
};

onMounted(async () => {
  try {
    loading.value = true;
    const token = localStorage.getItem('serenity_token');
    const user = localStorage.getItem('serenity_user');
    
    if (!token || !token.trim()) {
      console.error('[ERROR] AdminDashboard: No valid token - REDIRECTING TO LOGIN');
      localStorage.clear();
      window.location.href = '/';
      return;
    }
    
    if (!user) {
      console.error('[ERROR] AdminDashboard: No user data - REDIRECTING TO LOGIN');
      localStorage.clear();
      window.location.href = '/';
      return;
    }
    
    await Promise.all([
      fetchDashboard(),
      fetchDoctors(),
      fetchPatients(),
      fetchAppointments(),
      fetchDepartments()
    ]);
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    toast.error('Error', 'Failed to load dashboard. Please refresh the page.');
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/';
      return;
    }
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.admin-dashboard {
  animation: fadeIn 0.3s ease-in;
}

.admin-nav-tabs .nav-pills .nav-link {
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.admin-nav-tabs .nav-pills .nav-link:hover {
  background-color: rgba(108, 99, 255, 0.1);
  border-color: rgba(108, 99, 255, 0.2);
}

.admin-nav-tabs .nav-pills .nav-link.active {
  background: linear-gradient(135deg, #6c63ff 0%, #5b5bc7 100%);
  border-color: #6c63ff;
  color: white;
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
}

.metric-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

.metric-icon {
  width: 48px;
  height: 48px;
  font-size: 1.25rem;
}

.card-soft {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card-soft:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Mobile Responsive Styles */
@media (max-width: 767.98px) {
  .admin-nav-tabs .nav-pills {
    flex-direction: column;
  }
  
  .admin-nav-tabs .nav-item {
    width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .admin-nav-tabs .nav-link {
    text-align: center;
    padding: 0.75rem;
  }
  
  .metric-card {
    margin-bottom: 1rem;
  }
  
  .metric-icon {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .table-responsive {
    font-size: 0.875rem;
  }
  
  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }
}

@media (max-width: 575.98px) {
  .admin-nav-tabs .nav-link i {
    margin-right: 0.25rem;
  }
  
  .metric-card .card-body {
    padding: 1rem;
  }
  
  h3 {
    font-size: 1.5rem;
  }
}
</style>
