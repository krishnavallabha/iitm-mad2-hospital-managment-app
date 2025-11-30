<template>
  <div class="card card-soft">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div class="d-flex gap-3">
          <img
            src="https://ui-avatars.com/api/?name=Serenity+Care&background=5bc0eb&color=fff"
            class="rounded-circle"
            alt="Profile"
            width="64"
            height="64"
          />
          <div>
            <h6 class="fw-bold mb-1">SerenityCare Admin</h6>
            <p class="text-muted small mb-1">Central Coordinator</p>
            <span class="badge bg-primary-subtle text-primary rounded-pill">Online</span>
          </div>
        </div>
        <div class="btn-group">
          <button class="btn btn-sm btn-outline-secondary rounded-pill">Message</button>
          <button class="btn btn-sm btn-primary rounded-pill">Call</button>
        </div>
      </div>

      <ul class="nav nav-tabs mb-3">
        <li class="nav-item" v-for="tab in tabs" :key="tab">
          <button
            class="nav-link"
            :class="{ active: activeTab === tab }"
            @click="activeTab = tab"
          >
            {{ tab }}
          </button>
        </li>
      </ul>

      <div v-if="activeTab === 'Contacts'">
        <div class="d-flex align-items-center mb-3">
          <i class="bi bi-envelope text-primary me-2"></i>
          <span>support@serenitycare.com</span>
        </div>
        <div class="d-flex align-items-center">
          <i class="bi bi-telephone text-primary me-2"></i>
          <span>+1 (312) 555-0189</span>
        </div>
      </div>

	<div v-else>
        <p class="text-muted small mb-2">Key Highlights</p>
        <ul class="list-unstyled mb-0">
          <li class="d-flex justify-content-between mb-2">
            <span>Active Patients</span>
            <strong>184</strong>
          </li>
          <li class="d-flex justify-content-between mb-2">
            <span>Doctor Roster</span>
            <strong>62</strong>
          </li>
          <li class="d-flex justify-content-between">
            <span>Satisfaction</span>
            <strong>96%</strong>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const tabs = ['Contacts', 'Insights'];
const activeTab = ref('Contacts');
</script>

