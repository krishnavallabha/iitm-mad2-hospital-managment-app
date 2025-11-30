<template>
  <div class="container-fluid px-0">
    <div class="row g-4">
      <div class="col-12 col-lg-3">
        <ProgressCard />
        <div class="mt-4">
          <button class="btn btn-lg w-100 rounded-pill btn-outline-primary fw-semibold shadow-sm">
            Quick Action
          </button>
        </div>
      </div>

      <div class="col-12 col-lg-6">
        <AnalyticsCard />
        <div class="mt-4">
          <DataTabsTable />
        </div>
        <div class="mt-4">
          <AppointmentHistory />
        </div>
      </div>

      <div class="col-12 col-lg-3">
        <ProfileHighlights />
        <div class="mt-4">
          <ScheduleCard />
        </div>
        <div class="mt-4">
          <PaymentModule />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ProgressCard from './ProgressCard.vue';
import AnalyticsCard from './AnalyticsCard.vue';
import DataTabsTable from './DataTabsTable.vue';
import ProfileHighlights from './ProfileHighlights.vue';
import ScheduleCard from './ScheduleCard.vue';
import AppointmentHistory from './AppointmentHistory.vue';
import PaymentModule from './PaymentModule.vue';
</script>

