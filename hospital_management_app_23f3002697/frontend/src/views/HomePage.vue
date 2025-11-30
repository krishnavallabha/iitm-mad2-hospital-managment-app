<template>
  <div class="home-page min-vh-100 d-flex flex-column">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
      <div class="container">
        <div class="d-flex align-items-center gap-2">
          <div class="brand-icon rounded-circle d-flex align-items-center justify-content-center">
            <i class="bi bi-heart-pulse text-white fs-4"></i>
          </div>
          <span class="navbar-brand mb-0 fw-bold">SerenityCare</span>
        </div>
        <div class="d-flex gap-3">
          <button class="btn btn-link text-decoration-none" @click="$emit('navigate', 'about')">
            About
          </button>
          <button class="btn btn-primary rounded-pill px-4" @click="$emit('navigate', 'login')">
            Sign In
          </button>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="flex-grow-1 d-flex align-items-center justify-content-center p-4">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6 mb-4 mb-lg-0">
            <div class="text-center text-lg-start">
              <h1 class="display-4 fw-bold mb-4 text-primary">
                Welcome to <span class="text-gradient">SerenityCare</span>
              </h1>
              <p class="lead text-muted mb-4">
                SerenityCare is a modern, efficient, and reliable web platform created to simplify the daily operations of hospitals. It brings together Admins, Doctors, and Patients into a unified system where appointments, medical records, and treatment workflows can be managed smoothly.
              </p>
              <p class="text-muted mb-4">
                The system is designed with a strong focus on accuracy, performance, and user experience. It helps hospitals reduce manual record-keeping, avoid scheduling conflicts, and maintain a complete digital history of patient treatments.
              </p>
              <div class="d-flex gap-3 justify-content-center justify-content-lg-start">
                <button class="btn btn-primary btn-lg rounded-pill px-5" @click="$emit('navigate', 'login')">
                  Get Started
                </button>
                <button class="btn btn-outline-primary btn-lg rounded-pill px-5" @click="$emit('navigate', 'about')">
                  Learn More
                </button>
              </div>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="text-center">
              <div class="hero-image p-5">
                <i class="bi bi-hospital text-primary" style="font-size: 12rem; opacity: 0.1;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="bg-light py-5">
      <div class="container">
        <div class="row g-4">
          <div class="col-md-4">
            <div class="text-center p-4">
              <div class="feature-icon rounded-circle d-inline-flex align-items-center justify-content-center mb-3">
                <i class="bi bi-people-fill text-white fs-3"></i>
              </div>
              <h5 class="fw-bold">Role-Based Access</h5>
              <p class="text-muted mb-0">Separate dashboards for Admins, Doctors, and Patients with appropriate permissions.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="text-center p-4">
              <div class="feature-icon rounded-circle d-inline-flex align-items-center justify-content-center mb-3">
                <i class="bi bi-calendar-check text-white fs-3"></i>
              </div>
              <h5 class="fw-bold">Appointment Management</h5>
              <p class="text-muted mb-0">Efficient scheduling system that prevents conflicts and manages appointments seamlessly.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="text-center p-4">
              <div class="feature-icon rounded-circle d-inline-flex align-items-center justify-content-center mb-3">
                <i class="bi bi-file-medical text-white fs-3"></i>
              </div>
              <h5 class="fw-bold">Digital Records</h5>
              <p class="text-muted mb-0">Complete digital history of patient treatments and medical records.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-white border-top py-4">
      <div class="container text-center text-muted">
        <p class="mb-0">&copy; 2025 SerenityCare. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
defineEmits(['navigate']);
</script>

<style scoped>
.home-page {
  background: linear-gradient(135deg, rgba(108, 99, 255, 0.05), rgba(91, 192, 235, 0.05));
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--serenity-primary), var(--serenity-secondary));
  box-shadow: var(--serenity-shadow);
}

.text-gradient {
  background: linear-gradient(135deg, var(--serenity-primary), var(--serenity-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.feature-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--serenity-primary), var(--serenity-secondary));
  margin: 0 auto;
}

.hero-image {
  position: relative;
}
</style>

