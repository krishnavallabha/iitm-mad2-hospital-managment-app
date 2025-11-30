<template>
  <div class="doctor-dashboard">
    <section class="row g-4 mb-4">
      <div class="col-12 col-lg-3" v-for="stat in stats" :key="stat.label">
        <div class="card card-soft h-100">
          <div class="card-body">
            <p class="text-muted text-uppercase small mb-2">{{ stat.label }}</p>
            <div class="d-flex align-items-center justify-content-between">
              <h3 class="fw-bold mb-0">{{ stat.value }}</h3>
              <i :class="['bi', stat.icon, 'fs-3 text-primary']"></i>
            </div>
            <small class="text-muted">{{ stat.meta }}</small>
          </div>
        </div>
      </div>
    </section>

    <section class="row g-4">
      <div class="col-12 col-xl-8">
        <div class="card card-soft mb-4">
          <div class="card-body">
            <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
              <div>
                <h5 class="fw-bold mb-1">Today's Appointments</h5>
                <p class="text-muted small mb-0">SerenityCare schedule overview</p>
              </div>
              <div class="d-flex gap-2">
                <input
                  type="date"
                  class="form-control rounded-pill"
                  v-model="appointmentFilters.date"
                  @change="fetchAppointments"
                />
                <select
                  class="form-select rounded-pill"
                  v-model="appointmentFilters.status"
                  @change="fetchAppointments"
                >
                  <option value="">All Status</option>
                  <option value="Booked">Booked</option>
                  <option value="Completed">Completed</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </div>
            </div>
            <div class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in appointments" :key="apt.id">
                    <td>{{ apt.appointment_time }}</td>
                    <td>
                      <div class="fw-semibold">{{ apt.patient_name }}</div>
                      <small class="text-muted">SerenityCare ID: {{ apt.patient_id }}</small>
                    </td>
                    <td>{{ apt.reason || 'General Consultation' }}</td>
                    <td>
                      <span class="badge rounded-pill" :class="statusBadge(apt.status)">
                        {{ apt.status }}
                      </span>
                    </td>
                    <td class="text-end">
                      <div class="d-flex gap-2">
                        <button
                          class="btn btn-sm btn-outline-success rounded-pill"
                          @click="completeAppointment(apt)"
                          :disabled="apt.status !== 'Booked'"
                        >
                          Complete
                        </button>
                        <button
                          class="btn btn-sm btn-outline-danger rounded-pill"
                          @click="cancelAppointment(apt)"
                          :disabled="apt.status !== 'Booked'"
                        >
                          Cancel
                        </button>
                        <button
                          class="btn btn-sm btn-outline-primary rounded-pill"
                          @click="openTreatmentModal(apt)"
                        >
                          Treatment
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card card-soft mb-4">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold mb-0">Assigned Patients</h5>
              <input
                type="text"
                class="form-control rounded-pill w-auto"
                placeholder="Search..."
                v-model="patientSearch"
              />
            </div>
            <div class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Contact</th>
                    <th>Latest Diagnosis</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="patient in filteredPatients" :key="patient.id">
                    <td>
                      <div class="fw-semibold">{{ patient.full_name }}</div>
                      <small class="text-muted">{{ patient.gender || 'N/A' }}</small>
                    </td>
                    <td>{{ patient.phone || 'N/A' }}</td>
                    <td>
                      <span v-if="patient.latest_diagnosis" class="text-primary fw-semibold">
                        {{ patient.latest_diagnosis }}
                      </span>
                      <span v-else class="text-muted">No records</span>
                    </td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-primary rounded-pill" @click="viewPatientHistory(patient)">
                        View History
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-xl-4">
        <div class="card card-soft mb-4">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold mb-0">Availability (Next 7 days)</h5>
              <button class="btn btn-sm btn-outline-primary rounded-pill" @click="openAvailabilityModal">
                Update
              </button>
            </div>
            <div v-if="availability.length" class="d-flex flex-column gap-3">
              <div v-for="slot in availability" :key="slot.id" class="p-3 rounded-4 bg-light">
                <div class="d-flex justify-content-between">
                  <div>
                    <p class="fw-semibold mb-0">{{ formatDate(slot.date) }}</p>
                    <small class="text-muted">{{ slot.start_time }} - {{ slot.end_time }}</small>
                  </div>
                  <span class="badge bg-success-subtle text-success" v-if="slot.is_available">Open</span>
                  <span class="badge bg-secondary-subtle text-secondary" v-else>Blocked</span>
                </div>
                <div class="text-end mt-2">
                  <button class="btn btn-sm btn-outline-secondary rounded-pill me-2" @click="editAvailability(slot)">
                    Edit
                  </button>
                  <button class="btn btn-sm btn-outline-danger rounded-pill" @click="deleteAvailability(slot)">
                    Delete
                  </button>
                </div>
              </div>
            </div>
            <p v-else class="text-muted mb-0">No availability set. Please add slots.</p>
          </div>
        </div>

        <div class="card card-soft">
          <div class="card-body">
            <h5 class="fw-bold mb-3">Treatment Summary</h5>
            <div class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Diagnosis</th>
                    <th>Follow-up</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="treatment in treatments" :key="treatment.id">
                    <td>{{ treatment.patient_name }}</td>
                    <td>{{ treatment.diagnosis }}</td>
                    <td>{{ treatment.follow_up_date || 'N/A' }}</td>
                  </tr>
                  <tr v-if="treatments.length === 0">
                    <td colspan="3" class="text-center text-muted py-4">
                      <i class="bi bi-clipboard-check fs-4 d-block mb-2"></i>
                      No completed treatments yet
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>

    <AvailabilityModal
      v-if="showAvailabilityModal"
      :current-slots="availability"
      @close="showAvailabilityModal = false"
      @saved="handleAvailabilitySaved"
    />
    <TreatmentModal
      v-if="showTreatmentModal"
      :appointment="selectedAppointment"
      @close="closeTreatmentModal"
      @saved="handleTreatmentSaved"
    />
    <HistoryModal
      v-if="showHistoryModal"
      :patient-id="selectedPatient.id"
      :patient-name="selectedPatient.full_name"
      @close="closeHistoryModal"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../services/api';
import AvailabilityModal from '../components/doctor/AvailabilityModal.vue';
import TreatmentModal from '../components/doctor/TreatmentModal.vue';
import HistoryModal from '../components/doctor/HistoryModal.vue';

const stats = ref([]);
const appointments = ref([]);
const patients = ref([]);
const treatments = ref([]);
const availability = ref([]);

const appointmentFilters = reactive({
  date: new Date().toISOString().split('T')[0],
  status: ''
});

const patientSearch = ref('');
const showAvailabilityModal = ref(false);
const showTreatmentModal = ref(false);
const showHistoryModal = ref(false);
const selectedAppointment = ref(null);
const selectedPatient = ref(null);

const fetchDashboardStats = async () => {
  const { data } = await api.get('/dashboard/doctor');
  stats.value = [
    {
      label: 'Appointments Today',
      value: data.statistics.appointments_today,
      icon: 'bi-calendar2-week',
      meta: 'SerenityCare schedule'
    },
    {
      label: 'Patients Assigned',
      value: data.statistics.total_patients,
      icon: 'bi-people',
      meta: 'Active roster'
    },
    {
      label: 'Completed Today',
      value: data.statistics.completed_today,
      icon: 'bi-check2-circle',
      meta: 'Status updates'
    }
  ];
};

const fetchAppointments = async () => {
  const { data } = await api.get('/doctor/appointments', {
    params: {
      status: appointmentFilters.status || undefined,
      date_from: appointmentFilters.date,
      date_to: appointmentFilters.date
    }
  });
  appointments.value = data.appointments;
};

const fetchAssignedPatients = async () => {
  const { data } = await api.get('/doctor/patients');
  patients.value = data.patients.map((patient) => ({
    ...patient,
    full_name: patient.full_name || `${patient.first_name} ${patient.last_name}`
  }));
};

const fetchAvailability = async () => {
  const { data } = await api.get('/doctor/availability');
  availability.value = data.availability;
};

const fetchTreatmentSummary = async () => {
  try {
    // Get all appointments for this doctor (we'll filter completed ones with treatments)
    const { data } = await api.get('/doctor/appointments');
    
    // Extract treatments from completed appointments
    const treatmentsList = [];
    if (data.appointments) {
      data.appointments.forEach(apt => {
        // Only include completed appointments with treatments
        if (apt.status === 'Completed' && apt.treatment) {
          treatmentsList.push({
            id: apt.treatment.id || apt.id,
            diagnosis: apt.treatment.diagnosis,
            follow_up_date: apt.treatment.follow_up_date,
            appointment: apt,
            patient_name: apt.patient_name || (apt.patient ? `${apt.patient.first_name} ${apt.patient.last_name}` : 'Patient')
          });
        }
      });
    }
    
    // Sort by appointment date (most recent first)
    treatmentsList.sort((a, b) => {
      const dateA = new Date(a.appointment?.appointment_date || 0);
      const dateB = new Date(b.appointment?.appointment_date || 0);
      return dateB - dateA;
    });
    
    treatments.value = treatmentsList;
  } catch (error) {
    console.error('Error fetching treatment summary:', error);
    treatments.value = [];
  }
};

const completeAppointment = async (appointment) => {
  try {
    await api.put(`/doctor/appointments/${appointment.id}/complete`);
    // Refresh all relevant data
    await Promise.all([
      fetchAppointments(),
      fetchTreatmentSummary(),
      fetchAssignedPatients()
    ]);
  } catch (error) {
    console.error('Error completing appointment:', error);
  }
};

const cancelAppointment = async (appointment) => {
  if (!confirm('Cancel this appointment?')) return;
  await api.put(`/doctor/appointments/${appointment.id}/cancel`);
  fetchAppointments();
};

const openAvailabilityModal = () => {
  showAvailabilityModal.value = true;
};

const handleAvailabilitySaved = () => {
  showAvailabilityModal.value = false;
  fetchAvailability();
};

const editAvailability = (slot) => {
  showAvailabilityModal.value = true;
  // modal handles editing via props
};

const deleteAvailability = async (slot) => {
  if (!confirm('Delete this availability slot?')) return;
  await api.delete(`/doctor/availability/${slot.id}`);
  fetchAvailability();
};

const openTreatmentModal = (appointment) => {
  selectedAppointment.value = appointment;
  showTreatmentModal.value = true;
};

const closeTreatmentModal = () => {
  showTreatmentModal.value = false;
  selectedAppointment.value = null;
};

const handleTreatmentSaved = () => {
  closeTreatmentModal();
  fetchAppointments();
  fetchTreatmentSummary();
  fetchAssignedPatients(); // Refresh to update latest diagnosis
};

const viewPatientHistory = (patient) => {
  selectedPatient.value = patient;
  showHistoryModal.value = true;
};

const closeHistoryModal = () => {
  showHistoryModal.value = false;
  selectedPatient.value = null;
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });
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

const filteredPatients = computed(() => {
  const query = patientSearch.value.toLowerCase();
  return patients.value.filter((patient) =>
    patient.full_name?.toLowerCase().includes(query)
  );
});

onMounted(async () => {
  await Promise.all([
    fetchDashboardStats(),
    fetchAppointments(),
    fetchAssignedPatients(),
    fetchAvailability(),
    fetchTreatmentSummary()
  ]);
});
</script>

<style scoped>
.doctor-dashboard {
  animation: fadeIn 0.3s ease-in;
}

@media (max-width: 767.98px) {
  .doctor-dashboard .table-responsive {
    font-size: 0.875rem;
  }
  
  .doctor-dashboard .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }
  
  .doctor-dashboard .d-flex.gap-2 {
    flex-wrap: wrap;
  }
  
  .doctor-dashboard .form-control,
  .doctor-dashboard .form-select {
    font-size: 16px; /* Prevents zoom on iOS */
  }
}

@media (max-width: 575.98px) {
  .doctor-dashboard .card-body {
    padding: 1rem;
  }
  
  .doctor-dashboard h5 {
    font-size: 1.1rem;
  }
  
  .doctor-dashboard .d-flex.gap-2 {
    flex-direction: column;
  }
  
  .doctor-dashboard .d-flex.gap-2 > * {
    width: 100%;
  }
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
</style>

