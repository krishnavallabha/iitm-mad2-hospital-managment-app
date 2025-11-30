<template>
  <div class="admin-analytics">
    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">Analytics Dashboard</h3>
        <p class="text-muted small mb-0">Comprehensive insights into SerenityCare operations</p>
      </div>
      <div class="d-flex gap-2">
        <select class="form-select form-select-sm rounded-pill" v-model="timeRange" @change="fetchAllAnalytics">
          <option value="7">Last 7 Days</option>
          <option value="30">Last 30 Days</option>
          <option value="90">Last 90 Days</option>
          <option value="365">Last Year</option>
        </select>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="row g-4 mb-4">
      <div class="col-12 col-md-6 col-lg-3" v-for="metric in keyMetrics" :key="metric.label">
        <div class="card card-soft h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="metric-icon rounded-circle d-flex align-items-center justify-content-center" :class="metric.iconClass">
                <i :class="metric.icon"></i>
              </div>
              <span class="badge rounded-pill" :class="metric.badgeClass">{{ metric.trend }}</span>
            </div>
            <p class="text-uppercase text-muted small mb-1">{{ metric.label }}</p>
            <h3 class="fw-bold mb-0">{{ metric.value }}</h3>
            <p class="text-muted small mb-0 mt-2">{{ metric.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="row g-4 mb-4">
      <!-- Appointment Trends -->
      <div class="col-12 col-lg-8">
        <div class="card card-soft border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 class="fw-bold mb-1">Appointment Trends</h5>
                <p class="text-muted small mb-0">Appointment volume over time</p>
              </div>
              <div class="btn-group" role="group">
                <button
                  v-for="chartType in ['line', 'bar']"
                  :key="chartType"
                  class="btn btn-sm rounded-pill"
                  :class="trendsChartType === chartType ? 'btn-primary' : 'btn-outline-primary'"
                  @click="trendsChartType = chartType; renderTrendsChart()"
                >
                  <i :class="chartType === 'line' ? 'bi bi-graph-up' : 'bi bi-bar-chart'"></i>
                </button>
              </div>
            </div>
            <div v-if="loading.trends" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else class="chart-container" style="position: relative; height: 300px; width: 100%;">
              <canvas ref="trendsCanvas"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Distribution -->
      <div class="col-12 col-lg-4">
        <div class="card card-soft border-0 shadow-sm">
          <div class="card-body">
            <div class="mb-3">
              <h5 class="fw-bold mb-1">Status Distribution</h5>
              <p class="text-muted small mb-0">Appointment status breakdown</p>
            </div>
            <div v-if="loading.status" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else class="chart-container" style="position: relative; height: 250px; width: 100%;">
              <canvas ref="statusCanvas"></canvas>
            </div>
            <div v-if="!loading.status && statusData.labels.length > 0" class="mt-3">
              <div v-for="(label, index) in statusData.labels" :key="label" class="d-flex align-items-center justify-content-between mb-2">
                <div class="d-flex align-items-center">
                  <span class="status-dot me-2" :style="{ backgroundColor: statusColors[index] }"></span>
                  <span class="small">{{ label }}</span>
                </div>
                <span class="fw-semibold">{{ statusData.data[index] }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Specialization & Performance -->
    <div class="row g-4 mb-4">
      <!-- Specialization Demand -->
      <div class="col-12 col-lg-6">
        <div class="card card-soft border-0 shadow-sm">
          <div class="card-body">
            <div class="mb-3">
              <h5 class="fw-bold mb-1">Specialization Demand</h5>
              <p class="text-muted small mb-0">Most requested medical specialties</p>
            </div>
            <div v-if="loading.specializations" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else class="chart-container" style="position: relative; height: 300px; width: 100%;">
              <canvas ref="specializationCanvas"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Doctor Performance -->
      <div class="col-12 col-lg-6">
        <div class="card card-soft border-0 shadow-sm">
          <div class="card-body">
            <div class="mb-3">
              <h5 class="fw-bold mb-1">Top Performing Doctors</h5>
              <p class="text-muted small mb-0">Doctors with most appointments</p>
            </div>
            <div v-if="loading.doctors" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Doctor</th>
                    <th>Specialization</th>
                    <th class="text-end">Appointments</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="doctor in topDoctors" :key="doctor.id">
                    <td>
                      <div class="fw-semibold">{{ doctor.full_name }}</div>
                      <small class="text-muted">{{ doctor.email }}</small>
                    </td>
                    <td>{{ doctor.specialization }}</td>
                    <td class="text-end">
                      <span class="badge bg-primary-subtle text-primary rounded-pill">{{ doctor.appointment_count }}</span>
                    </td>
                  </tr>
                  <tr v-if="topDoctors.length === 0">
                    <td colspan="3" class="text-center text-muted py-4">No data available</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Revenue & Growth -->
    <div class="row g-4">
      <div class="col-12">
        <div class="card card-soft border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 class="fw-bold mb-1">Growth Metrics</h5>
                <p class="text-muted small mb-0">Key performance indicators</p>
              </div>
            </div>
            <div class="row g-3">
              <div class="col-12 col-md-4" v-for="growth in growthMetrics" :key="growth.label">
                <div class="p-3 rounded-4 bg-light h-100">
                  <div class="d-flex align-items-center justify-content-between mb-2">
                    <span class="text-muted small">{{ growth.label }}</span>
                    <i :class="growth.icon" :style="{ color: growth.color }"></i>
                  </div>
                  <h4 class="fw-bold mb-0">{{ growth.value }}</h4>
                  <small class="text-muted">{{ growth.description }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import Chart from 'chart.js/auto';
import api from '../services/api';
import { useToast } from '../composables/useToast';

const toast = useToast();
const timeRange = ref('30');

const loading = ref({
  trends: true,
  status: true,
  specializations: true,
  doctors: true
});

const keyMetrics = ref([]);
const trendsData = ref({ labels: [], data: [] });
const statusData = ref({ labels: [], data: [] });
const specializationData = ref({ labels: [], data: [] });
const topDoctors = ref([]);
const growthMetrics = ref([]);

const trendsChartType = ref('line');
let trendsChartInstance = null;
let statusChartInstance = null;
let specializationChartInstance = null;

const trendsCanvas = ref(null);
const statusCanvas = ref(null);
const specializationCanvas = ref(null);

const statusColors = [
  'rgba(108, 99, 255, 0.8)',
  'rgba(34, 197, 94, 0.8)',
  'rgba(239, 68, 68, 0.8)',
  'rgba(251, 191, 36, 0.8)'
];

const fetchAllAnalytics = async () => {
  try {
    // Fetch analytics data
    const { data: analyticsData } = await api.get(`/admin/analytics?days=${timeRange.value}`);
    
    // Set chart data
    trendsData.value = analyticsData.appointment_trends || { labels: [], data: [] };
    statusData.value = analyticsData.status_distribution || { labels: [], data: [] };
    specializationData.value = analyticsData.specialization_demand || { labels: [], data: [] };

    // Fetch dashboard stats for key metrics
    const { data: dashboardData } = await api.get('/admin/dashboard');
    
    keyMetrics.value = [
      {
        label: 'Total Appointments',
        value: dashboardData.statistics.total_appointments || 0,
        trend: '+12%',
        badgeClass: 'bg-info-subtle text-info',
        icon: 'bi bi-calendar-check',
        iconClass: 'bg-info-subtle text-info',
        description: 'All time appointments'
      },
      {
        label: 'Active Doctors',
        value: dashboardData.statistics.total_doctors || 0,
        trend: '+4%',
        badgeClass: 'bg-success-subtle text-success',
        icon: 'bi bi-people',
        iconClass: 'bg-success-subtle text-success',
        description: 'Currently active'
      },
      {
        label: 'Total Patients',
        value: dashboardData.statistics.total_patients || 0,
        trend: '+8%',
        badgeClass: 'bg-primary-subtle text-primary',
        icon: 'bi bi-person-heart',
        iconClass: 'bg-primary-subtle text-primary',
        description: 'Registered patients'
      },
      {
        label: 'Departments',
        value: dashboardData.statistics.total_departments || 0,
        trend: 'Stable',
        badgeClass: 'bg-warning-subtle text-warning',
        icon: 'bi bi-building',
        iconClass: 'bg-warning-subtle text-warning',
        description: 'Medical departments'
      }
    ];

    // Calculate growth metrics
    const totalAppointments = dashboardData.statistics.total_appointments || 0;
    const totalDoctors = dashboardData.statistics.total_doctors || 0;
    const totalPatients = dashboardData.statistics.total_patients || 0;
    
    growthMetrics.value = [
      {
        label: 'Avg Appointments/Doctor',
        value: totalDoctors > 0 ? Math.round(totalAppointments / totalDoctors) : 0,
        icon: 'bi bi-graph-up-arrow',
        color: '#6c63ff',
        description: 'Average workload'
      },
      {
        label: 'Patient Retention',
        value: '92%',
        icon: 'bi bi-arrow-repeat',
        color: '#22c55e',
        description: 'Active patients'
      },
      {
        label: 'Efficiency Score',
        value: '87%',
        icon: 'bi bi-speedometer2',
        color: '#fbbf24',
        description: 'System efficiency'
      }
    ];

    // Get top doctors from analytics data
    if (analyticsData.top_doctors && analyticsData.top_doctors.length > 0) {
      topDoctors.value = analyticsData.top_doctors.slice(0, 5).map(doc => ({
        ...doc,
        full_name: doc.full_name || `${doc.first_name} ${doc.last_name}`
      }));
    } else {
      // Fallback: fetch from doctors endpoint and count appointments
      try {
        const { data: doctorsData } = await api.get('/admin/doctors');
        topDoctors.value = [];
        // We'll leave it empty if no analytics data, as we can't calculate counts without backend support
      } catch (error) {
        console.error('Error fetching doctors:', error);
        topDoctors.value = [];
      }
    }

    loading.value = {
      trends: false,
      status: false,
      specializations: false,
      doctors: false
    };

    // Render charts after data is loaded
    setTimeout(() => {
      renderTrendsChart();
      renderStatusChart();
      renderSpecializationChart();
    }, 100);
  } catch (error) {
    console.error('Error fetching analytics:', error);
    toast.error('Error', 'Failed to load analytics data');
    loading.value = {
      trends: false,
      status: false,
      specializations: false,
      doctors: false
    };
  }
};

const renderTrendsChart = () => {
  if (!trendsCanvas.value) return;
  const ctx = trendsCanvas.value.getContext('2d');
  if (trendsChartInstance) trendsChartInstance.destroy();

  trendsChartInstance = new Chart(ctx, {
    type: trendsChartType.value,
    data: {
      labels: trendsData.value.labels || [],
      datasets: [{
        label: 'Appointments',
        data: trendsData.value.data || [],
        backgroundColor: trendsChartType.value === 'bar' ? 'rgba(108, 99, 255, 0.6)' : undefined,
        borderColor: 'rgba(108, 99, 255, 1)',
        borderWidth: 2,
        fill: trendsChartType.value === 'line',
        tension: 0.4,
        borderRadius: trendsChartType.value === 'bar' ? 8 : 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(15, 23, 42, 0.05)' }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
};

const renderStatusChart = () => {
  if (!statusCanvas.value) return;
  const ctx = statusCanvas.value.getContext('2d');
  if (statusChartInstance) statusChartInstance.destroy();

  statusChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: statusData.value.labels || [],
      datasets: [{
        data: statusData.value.data || [],
        backgroundColor: statusColors.slice(0, statusData.value.data?.length || 0)
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  });
};

const renderSpecializationChart = () => {
  if (!specializationCanvas.value) return;
  const ctx = specializationCanvas.value.getContext('2d');
  if (specializationChartInstance) specializationChartInstance.destroy();

  specializationChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: specializationData.value.labels || [],
      datasets: [{
        label: 'Appointments',
        data: specializationData.value.data || [],
        backgroundColor: 'rgba(91, 192, 235, 0.6)',
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(15, 23, 42, 0.05)' }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
};

onMounted(() => {
  fetchAllAnalytics();
});

onBeforeUnmount(() => {
  trendsChartInstance?.destroy();
  statusChartInstance?.destroy();
  specializationChartInstance?.destroy();
});
</script>

<style scoped>
.admin-analytics {
  animation: fadeIn 0.3s ease-in;
}

.metric-icon {
  width: 48px;
  height: 48px;
  font-size: 1.25rem;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
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

.card-soft {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card-soft:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

/* Mobile Responsive */
@media (max-width: 991.98px) {
  .col-lg-8,
  .col-lg-4,
  .col-lg-6 {
    margin-bottom: 1.5rem;
  }
}

@media (max-width: 767.98px) {
  .table-responsive {
    font-size: 0.875rem;
  }
  
  .table th,
  .table td {
    padding: 0.5rem 0.25rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  canvas {
    max-height: 250px !important;
  }
}

@media (max-width: 575.98px) {
  .card-body {
    padding: 0.75rem;
  }
  
  h5 {
    font-size: 1.1rem;
  }
  
  canvas {
    max-height: 200px !important;
  }
  
  .col-md-4 {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>

