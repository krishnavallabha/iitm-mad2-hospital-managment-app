<template>
  <div class="card card-soft">
    <div class="card-body">
      <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
        <h6 class="fw-bold mb-0">Department Snapshot</h6>
        <ul class="nav nav-tabs border-0 gap-2">
          <li class="nav-item" v-for="tab in tabs" :key="tab">
            <button
              class="nav-link rounded-pill"
              :class="{ active: activeTab === tab }"
              @click="activeTab = tab"
            >
              {{ tab }}
            </button>
          </li>
        </ul>
      </div>
      <div class="table-responsive">
        <table class="table align-middle">
          <thead>
            <tr>
              <th>Specialization</th>
              <th>Doctors</th>
              <th>Pending</th>
              <th>Completed</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredRows" :key="row.department">
              <td>
                <div class="fw-semibold">{{ row.department }}</div>
                <small class="text-muted">{{ row.description }}</small>
              </td>
              <td>{{ row.doctors }}</td>
              <td>{{ row.pending }}</td>
              <td>{{ row.completed }}</td>
              <td>
                <span class="badge rounded-pill" :class="row.statusClass">{{ row.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const tabs = ['Tab A', 'Tab B', 'Tab C'];
const activeTab = ref('Tab A');

const rows = [
  {
    department: 'Cardiology',
    description: 'Heart & vascular care',
    doctors: 12,
    pending: 8,
    completed: 42,
    status: 'Stable',
    statusClass: 'bg-success-subtle text-success',
    tab: 'Tab A'
  },
  {
    department: 'Neurology',
    description: 'Brain & nervous system',
    doctors: 9,
    pending: 5,
    completed: 33,
    status: 'Busy',
    statusClass: 'bg-warning-subtle text-warning',
    tab: 'Tab A'
  },
  {
    department: 'Orthopedics',
    description: 'Bones & joints',
    doctors: 7,
    pending: 4,
    completed: 28,
    status: 'Stable',
    statusClass: 'bg-success-subtle text-success',
    tab: 'Tab B'
  },
  {
    department: 'Pediatrics',
    description: 'Children care',
    doctors: 10,
    pending: 6,
    completed: 35,
    status: 'Focus',
    statusClass: 'bg-info-subtle text-info',
    tab: 'Tab C'
  }
];

const filteredRows = computed(() =>
  rows.filter((row) => row.tab === activeTab.value)
);
</script>

