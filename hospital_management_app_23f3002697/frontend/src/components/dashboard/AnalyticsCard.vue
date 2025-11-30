<template>
  <div class="card card-soft">
    <div class="card-body">
      <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
        <div>
          <p class="text-muted text-uppercase small mb-1">SerenityCare Analytics</p>
          <h5 class="mb-0 fw-bold">{{ chartTitles[activeTab] }}</h5>
        </div>
        <ul class="nav nav-pills gap-2">
          <li class="nav-item" v-for="tab in tabs" :key="tab">
            <button
              class="nav-link rounded-pill py-1 px-3"
              :class="{ active: activeTab === tab }"
              @click="activeTab = tab"
            >
              {{ tab }}
            </button>
          </li>
        </ul>
      </div>
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <canvas v-else ref="chartCanvas" height="160"></canvas>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import Chart from 'chart.js/auto';
import api from '../../services/api';

const tabs = ['Trends', 'Specializations', 'Status'];
const activeTab = ref('Trends');
const chartCanvas = ref(null);
const loading = ref(true);
let chartInstance;

const chartTitles = {
  'Trends': 'Appointment Trends',
  'Specializations': 'Specialization Demand',
  'Status': 'Status Distribution'
};

const analyticsData = ref({
  appointment_trends: { labels: [], data: [] },
  specialization_demand: { labels: [], data: [] },
  status_distribution: { labels: [], data: [] }
});

const fetchAnalytics = async () => {
  try {
    loading.value = true;
    const { data } = await api.get('/admin/analytics?days=30');
    analyticsData.value = data;
    renderChart();
  } catch (error) {
    console.error('Error fetching analytics:', error);
    // Use empty data on error
    analyticsData.value = {
      appointment_trends: { labels: [], data: [] },
      specialization_demand: { labels: [], data: [] },
      status_distribution: { labels: [], data: [] }
    };
    renderChart();
  } finally {
    loading.value = false;
  }
};

const renderChart = () => {
  if (!chartCanvas.value) return;
  const ctx = chartCanvas.value.getContext('2d');
  if (chartInstance) chartInstance.destroy();

  let chartData, chartLabels, chartType, backgroundColor;

  switch (activeTab.value) {
    case 'Trends':
      chartLabels = analyticsData.value.appointment_trends.labels || [];
      chartData = analyticsData.value.appointment_trends.data || [];
      chartType = 'line';
      backgroundColor = 'rgba(108, 99, 255, 0.6)';
      break;
    case 'Specializations':
      chartLabels = analyticsData.value.specialization_demand.labels || [];
      chartData = analyticsData.value.specialization_demand.data || [];
      chartType = 'bar';
      backgroundColor = 'rgba(91, 192, 235, 0.6)';
      break;
    case 'Status':
      chartLabels = analyticsData.value.status_distribution.labels || [];
      chartData = analyticsData.value.status_distribution.data || [];
      chartType = 'doughnut';
      backgroundColor = [
        'rgba(108, 99, 255, 0.6)',
        'rgba(91, 192, 235, 0.6)',
        'rgba(34, 197, 94, 0.6)',
        'rgba(239, 68, 68, 0.6)'
      ];
      break;
    default:
      chartLabels = [];
      chartData = [];
      chartType = 'bar';
      backgroundColor = 'rgba(108, 99, 255, 0.6)';
  }

  chartInstance = new Chart(ctx, {
    type: chartType,
    data: {
      labels: chartLabels,
      datasets: [
        {
          label: activeTab.value === 'Trends' ? 'Appointments' : 'Count',
          data: chartData,
          backgroundColor: Array.isArray(backgroundColor) ? backgroundColor : backgroundColor,
          borderRadius: chartType === 'bar' ? 12 : 0,
          borderColor: chartType === 'line' ? 'rgba(108, 99, 255, 1)' : undefined,
          borderWidth: chartType === 'line' ? 2 : 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: chartType !== 'doughnut' ? {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(15, 23, 42, 0.05)' }
        },
        x: {
          grid: { display: false }
        }
      } : {},
      plugins: {
        legend: {
          display: chartType === 'doughnut',
          position: 'bottom'
        }
      }
    }
  });
};

watch(activeTab, renderChart);

onMounted(() => {
  fetchAnalytics();
});

onBeforeUnmount(() => chartInstance?.destroy());
</script>

