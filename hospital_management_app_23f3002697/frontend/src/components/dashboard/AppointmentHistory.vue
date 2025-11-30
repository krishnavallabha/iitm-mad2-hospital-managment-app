<template>
  <div class="card card-soft">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="fw-bold mb-0">Appointment History</h6>
        <button class="btn btn-sm btn-outline-secondary rounded-pill">View All</button>
      </div>
      <div class="table-responsive">
        <table class="table align-middle">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in history" :key="record.id">
              <td>
                <div class="fw-semibold">{{ record.patient }}</div>
                <small class="text-muted">{{ record.department }}</small>
              </td>
              <td>{{ record.doctor }}</td>
              <td>{{ record.date }}</td>
              <td>
                <span class="badge rounded-pill" :class="record.badgeClass">{{ record.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
const history = [
  {
    id: 1,
    patient: 'Olivia Mason',
    department: 'Cardiology',
    doctor: 'Dr. Rivera',
    date: 'Jan 12',
    status: 'Completed',
    badgeClass: 'bg-success-subtle text-success'
  },
  {
    id: 2,
    patient: 'Ethan Shah',
    department: 'Dermatology',
    doctor: 'Dr. Chang',
    date: 'Jan 11',
    status: 'Cancelled',
    badgeClass: 'bg-danger-subtle text-danger'
  },
  {
    id: 3,
    patient: 'Sophia Patel',
    department: 'Neurology',
    doctor: 'Dr. Lemaire',
    date: 'Jan 10',
    status: 'Booked',
    badgeClass: 'bg-warning-subtle text-warning'
  }
];
</script>

