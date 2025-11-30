<template>
  <div class="patient-dashboard">
    <!-- Welcome Header -->
    <div class="text-center mb-4">
      <h4 class="fw-bold mb-1">Welcome, {{ patientName }}</h4>
      <p class="text-muted small mb-0">Manage your appointments and health records</p>
    </div>

    <section class="row g-4 mb-4">
      <div class="col-12">
        <div class="card card-soft border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-3">
              <h5 class="fw-bold mb-0">Available Specialists</h5>
              <div class="d-flex gap-2 align-items-center flex-wrap">
                <div class="input-group" style="width: 200px;">
                  <span class="input-group-text bg-white border-end-0" style="padding: 0.375rem 0.75rem;">
                    <i class="bi bi-search"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control form-control-sm border-start-0 rounded-end-pill"
                    placeholder="Search doctors..."
                    v-model="doctorFilters.search"
                    @keyup.enter="fetchDoctors"
                  />
                </div>
                <select class="form-select form-select-sm rounded-pill" style="width: 140px;" v-model="doctorFilters.specialization_id" @change="fetchDoctors">
                  <option value="">All Specialties</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                    {{ dept.name }}
                  </option>
                </select>
                <span class="badge bg-primary-subtle text-primary rounded-pill d-flex align-items-center">{{ doctors.length }} Doctors</span>
              </div>
            </div>
            <div class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Specialization</th>
                    <th>Availability</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="doctor in doctors" :key="doctor.id">
                    <td>
                      <div class="fw-semibold">{{ doctor.full_name }}</div>
                      <small class="text-muted">{{ doctor.email }}</small>
                    </td>
                    <td>{{ doctor.specialization }}</td>
                    <td>
                      <small class="text-muted">
                        {{ doctor.availability?.length ? `${doctor.availability.length} slots` : 'No slots' }}
                      </small>
                    </td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-primary rounded-pill me-2" @click="viewDoctor(doctor)">
                        Details
                      </button>
                      <button class="btn btn-sm btn-primary rounded-pill" @click="openBookingModal(doctor)">
                        Book
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="row g-4">
      <div class="col-12 col-xl-8">
        <div class="card card-soft mb-4 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold mb-0">Upcoming Appointments</h5>
              <button class="btn btn-outline-secondary rounded-pill" @click="fetchAppointments">Refresh</button>
            </div>
            <div v-if="upcomingAppointments.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-calendar-x fs-1 mb-3 d-block"></i>
              <p class="mb-0">No upcoming appointments scheduled.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle table-hover">
                <thead class="table-light">
                  <tr>
                    <th>Doctor</th>
                    <th>Date & Time</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in upcomingAppointments" :key="apt.id">
                    <td>{{ apt.doctor_name }}</td>
                    <td>{{ apt.appointment_date }} {{ apt.appointment_time }}</td>
                    <td>{{ apt.reason || 'General Consultation' }}</td>
                    <td>
                      <span class="badge rounded-pill" :class="statusBadge(apt.status)">
                        {{ apt.status }}
                      </span>
                    </td>
                    <td class="text-end">
                      <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary rounded-pill" @click="openRescheduleModal(apt)" :disabled="apt.status !== 'Booked'">
                          Reschedule
                        </button>
                        <button class="btn btn-sm btn-outline-danger rounded-pill" @click="cancelAppointment(apt)" :disabled="apt.status !== 'Booked'">
                          Cancel
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card card-soft border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 class="fw-bold mb-1">Treatment History</h5>
                <p class="text-muted small mb-0">Your medical records and visit history</p>
              </div>
              <div class="d-flex gap-2">
                <button class="btn btn-outline-primary rounded-pill" @click="triggerExport('pdf')" :disabled="loading.export">
                  <span v-if="loading.export" class="spinner-border spinner-border-sm me-2" />
                  Export PDF
                </button>
                <button class="btn btn-outline-success rounded-pill" @click="triggerExport('csv')" :disabled="loading.export">
                  <span v-if="loading.export" class="spinner-border spinner-border-sm me-2" />
                  Export CSV
                </button>
              </div>
            </div>
            <div v-if="treatmentHistory.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-file-medical fs-1 mb-3 d-block"></i>
              <p class="mb-0">No treatment history available yet.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle table-hover">
                <thead class="table-light">
                  <tr>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Diagnosis</th>
                    <th>Follow-up</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in treatmentHistory" :key="record.id">
                    <td>{{ record.appointment?.doctor_name || 'N/A' }}</td>
                    <td>{{ record.appointment?.appointment_date || 'N/A' }}</td>
                    <td>{{ record.diagnosis }}</td>
                    <td>{{ record.follow_up_date || 'N/A' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="exportStatus" class="alert mt-3" :class="exportStatusClass">
              <div>{{ exportStatusMessage }}</div>
              <button
                v-if="exportStatus === 'completed' && exportDownloadUrl"
                @click="downloadExport"
                class="btn btn-sm btn-primary d-inline-flex align-items-center gap-2 mt-2"
              >
                <i class="bi bi-download"></i> Download PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-xl-4">
        <div class="card card-soft border-0 shadow-sm">
          <div class="card-body">
            <h5 class="fw-bold mb-3">Past Appointments</h5>
            <div v-if="pastAppointments.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-clock-history fs-1 mb-3 d-block"></i>
              <p class="mb-0">No past appointments to display.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle table-hover">
                <thead class="table-light">
                  <tr>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in pastAppointments" :key="apt.id">
                    <td>{{ apt.doctor_name }}</td>
                    <td>{{ apt.appointment_date }}</td>
                    <td>
                      <span class="badge rounded-pill" :class="statusBadge(apt.status)">
                        {{ apt.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>

    <AppointmentModal
      v-if="showAppointmentModal"
      :doctor="selectedDoctor"
      :appointment="editingAppointment"
      @close="closeAppointmentModal"
      @saved="handleAppointmentSaved"
    />
    
    <DoctorDetailsModal
      v-if="showDoctorDetailsModal"
      :doctor="selectedDoctorDetails"
      @close="closeDoctorDetailsModal"
      @book="handleBookFromDetails"
    />

    <DepartmentDetailsModal
      v-if="showDepartmentModal"
      :departmentId="selectedDepartmentId"
      @close="closeDepartmentModal"
      @view-doctor="handleViewDoctorFromDept"
      @book-doctor="handleBookDoctorFromDept"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../services/api';
import { useAuthStore } from '../store/auth';
import AppointmentModal from '../components/patient/AppointmentModal.vue';
import DoctorDetailsModal from '../components/patient/DoctorDetailsModal.vue';
import DepartmentDetailsModal from '../components/patient/DepartmentDetailsModal.vue';

const auth = useAuthStore();

const patientName = computed(() => {
  const user = auth.state.user;
  if (user && user.first_name) {
    return `${user.first_name} ${user.last_name || ''}`.trim();
  }
  return user?.username || 'Patient';
});

const departments = ref([]);
const doctors = ref([]);
const appointments = ref([]);
const treatmentHistory = ref([]);

const doctorFilters = reactive({
  search: '',
  specialization_id: '',
  available_date: ''
});

const showAppointmentModal = ref(false);
const showDoctorDetailsModal = ref(false);
const selectedDoctor = ref(null);
const selectedDoctorDetails = ref(null);
const editingAppointment = ref(null);
const showDepartmentModal = ref(false);
const selectedDepartmentId = ref(null);

const exportTaskId = ref('');
const exportStatus = ref('');
const exportDownloadUrl = ref('');

const loading = reactive({
  doctors: false,
  export: false
});

const fetchDepartments = async () => {
  const { data } = await api.get('/patient/departments');
  departments.value = data.departments;
};

const fetchDoctors = async () => {
  loading.doctors = true;
  try {
    // Fetch all doctors first, then filter locally for better UX
    const { data } = await api.get('/patient/doctors');
    let filteredDoctors = data.doctors.map((doc) => ({
      ...doc,
      full_name: doc.full_name || `${doc.first_name} ${doc.last_name}`
    }));

    if (doctorFilters.search) {
      const searchLower = doctorFilters.search.toLowerCase();
      filteredDoctors = filteredDoctors.filter(doc => 
        doc.full_name.toLowerCase().includes(searchLower) ||
        doc.specialization.toLowerCase().includes(searchLower)
      );
    }

    if (doctorFilters.specialization_id) {
      filteredDoctors = filteredDoctors.filter(doc => 
        doc.specialization_id === doctorFilters.specialization_id
      );
    }

    // Note: Date filtering usually requires backend support or complex logic, 
    // keeping it simple for now or relying on backend if needed later.
    
    doctors.value = filteredDoctors;
  } finally {
    loading.doctors = false;
  }
};

const fetchAppointments = async () => {
  const { data } = await api.get('/patient/appointments');
  appointments.value = data.appointments;
};

const fetchHistory = async () => {
  const { data } = await api.get('/history/treatments/my-treatments');
  treatmentHistory.value = data.treatments.slice(0, 10);
};

const upcomingAppointments = computed(() =>
  appointments.value.filter((apt) => apt.status !== 'Completed' && apt.status !== 'Cancelled')
);

const pastAppointments = computed(() =>
  appointments.value.filter((apt) => apt.status !== 'Booked')
);

const openBookingModal = (doctor) => {
  selectedDoctor.value = doctor;
  editingAppointment.value = null;
  showAppointmentModal.value = true;
};

const openRescheduleModal = (appointment) => {
  selectedDoctor.value = null;
  editingAppointment.value = appointment;
  showAppointmentModal.value = true;
};

const closeAppointmentModal = () => {
  showAppointmentModal.value = false;
  selectedDoctor.value = null;
  editingAppointment.value = null;
};

const handleAppointmentSaved = () => {
  closeAppointmentModal();
  fetchAppointments();
};

const cancelAppointment = async (appointment) => {
  if (!confirm('Cancel this appointment?')) return;
  await api.delete(`/patient/appointments/${appointment.id}`);
  fetchAppointments();
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

const triggerExport = async (format = 'pdf') => {
  loading.export = true;
  exportStatus.value = '';
  exportDownloadUrl.value = '';
  exportTaskId.value = null;
  try {
    const { data } = await api.post('/exports/treatment-history', { format });
    
    // Handle synchronous response (completed immediately)
    if (data.status === 'completed' && data.result?.download_url) {
      exportStatus.value = 'completed';
      exportDownloadUrl.value = data.result.download_url;
      loading.export = false;
    } 
    // Handle asynchronous response (with task_id)
    else if (data.task_id) {
      exportTaskId.value = data.task_id;
      exportStatus.value = data.status || 'processing';
      pollExportStatus();
    } else {
      exportStatus.value = 'failed';
      loading.export = false;
    }
  } catch (error) {
    console.error('Export error:', error);
    exportStatus.value = 'failed';
    loading.export = false;
  }
};

const pollExportStatus = async () => {
  if (!exportTaskId.value) return;
  const { data } = await api.get(`/exports/status/${exportTaskId.value}`);
  exportStatus.value = data.status;
  if (data.status === 'completed' && data.result?.download_url) {
    exportDownloadUrl.value = data.result.download_url;
  } else if (data.status === 'pending' || data.status === 'processing') {
    setTimeout(pollExportStatus, 3000);
  }
};

const downloadExport = async () => {
  if (!exportDownloadUrl.value) return;
  
  try {
    // Extract filename from download URL (format: /api/exports/download/filename)
    const urlParts = exportDownloadUrl.value.split('/');
    const filename = urlParts[urlParts.length - 1];
    
    // Remove /api prefix if present since api service already has baseURL with /api
    let downloadPath = exportDownloadUrl.value;
    if (downloadPath.startsWith('/api/')) {
      downloadPath = downloadPath.substring(4); // Remove '/api'
    }
    
    // Download the file using the API
    const response = await api.get(downloadPath, {
      responseType: 'blob'
    });
    
    // Create a blob URL and trigger download
    const blob = new Blob([response.data], { 
      type: filename.endsWith('.pdf') ? 'application/pdf' : 'text/csv' 
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download error:', error);
    alert('Failed to download file. Please try again.');
  }
};

const exportStatusClass = computed(() => {
  if (exportStatus.value === 'completed') return 'alert-success';
  if (exportStatus.value === 'failed') return 'alert-danger';
  return 'alert-info';
});

const exportStatusMessage = computed(() => {
  switch (exportStatus.value) {
    case 'completed':
      return exportDownloadUrl.value ? 'Export ready. Use the download link below.' : 'Export completed.';
    case 'failed':
      return 'Export failed. Please try again.';
    case 'pending':
    case 'processing':
      return 'Export in progress...';
    default:
      return '';
  }
});

const viewDoctor = (doctor) => {
  selectedDoctorDetails.value = doctor;
  showDoctorDetailsModal.value = true;
};

const closeDoctorDetailsModal = () => {
  showDoctorDetailsModal.value = false;
  selectedDoctorDetails.value = null;
};

const handleBookFromDetails = (doctor) => {
  closeDoctorDetailsModal();
  openBookingModal(doctor);
};

const viewDepartment = (dept) => {
  selectedDepartmentId.value = dept.id;
  showDepartmentModal.value = true;
};

const closeDepartmentModal = () => {
  showDepartmentModal.value = false;
  selectedDepartmentId.value = null;
};

const handleViewDoctorFromDept = (doctor) => {
  closeDepartmentModal();
  viewDoctor(doctor);
};

const handleBookDoctorFromDept = (doctor) => {
  closeDepartmentModal();
  openBookingModal(doctor);
};

onMounted(async () => {
  await Promise.all([fetchDepartments(), fetchDoctors(), fetchAppointments(), fetchHistory()]);
});
</script>

<style scoped>
.patient-dashboard .card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.patient-dashboard .card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1) !important;
}

.patient-dashboard .table-hover tbody tr {
  transition: background-color 0.2s;
}

.patient-dashboard .table-hover tbody tr:hover {
  background-color: rgba(108, 99, 255, 0.05);
}

.patient-dashboard .table thead th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
}

@media (max-width: 767.98px) {
  .patient-dashboard .table-responsive {
    font-size: 0.875rem;
  }
  
  .patient-dashboard .table thead th {
    font-size: 0.7rem;
    padding: 0.5rem 0.25rem;
  }
  
  .patient-dashboard .table td {
    padding: 0.5rem 0.25rem;
  }
  
  .patient-dashboard .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }
  
  .patient-dashboard .d-flex.gap-2 {
    flex-wrap: wrap;
  }
  
  .patient-dashboard .input-group {
    width: 100% !important;
  }
  
  .patient-dashboard .form-select {
    width: 100% !important;
  }
}

@media (max-width: 575.98px) {
  .patient-dashboard .card-body {
    padding: 1rem;
  }
  
  .patient-dashboard h5 {
    font-size: 1.1rem;
  }
  
  .patient-dashboard .d-flex.gap-2 {
    flex-direction: column;
  }
  
  .patient-dashboard .d-flex.gap-2 > * {
    width: 100%;
  }
  
  .patient-dashboard .table {
    font-size: 0.8rem;
  }
}
</style>

