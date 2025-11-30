<template>
  <div class="about-page min-vh-100 d-flex flex-column">
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
          <button class="btn btn-link text-decoration-none" @click="$emit('navigate', 'home')">
            Home
          </button>
          <button class="btn btn-primary rounded-pill px-4" @click="$emit('navigate', 'login')">
            Sign In
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1 py-5">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-10">
            <div class="card border-0 shadow-sm mb-4">
              <div class="card-body p-5">
                <h1 class="display-5 fw-bold mb-4 text-primary">About This Project</h1>
                
                <p class="lead text-muted mb-4">
                  Hospital Management System V2 is an academic project developed as part of the Modern Application Development 2 course under the BS in Data Science and Applications program. The objective of this project is to design a role-based hospital management platform using only the mandated technologies and a structured backend-driven architecture.
                </p>

                <p class="text-muted mb-5">
                  The project aims to simulate real hospital operations through digital workflows while meeting strict development requirements such as programmatic database creation, caching, background job execution, and frontend-backend separation.
                </p>

                <h2 class="h3 fw-bold mb-3">Purpose of the Project</h2>
                <p class="text-muted mb-4">
                  This system is created to demonstrate a practical understanding of:
                </p>
                <ul class="list-unstyled mb-5">
                  <li class="mb-2">
                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                    Full stack application development
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                    API design and role-based authentication
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                    Caching and performance optimization
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                    Asynchronous processing with Celery
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                    Scheduled jobs
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                    Database modeling and programmatic schema creation
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                    Separation of concerns between backend, frontend, and caching layers
                  </li>
                </ul>
                <p class="text-muted mb-5">
                  It mirrors the functioning of a real medical software environment, where multiple stakeholders interact using clearly defined permissions.
                </p>

                <h2 class="h3 fw-bold mb-3">Design Philosophy</h2>
                <p class="text-muted mb-3">
                  The system is built around the following principles:
                </p>
                <div class="row g-3 mb-5">
                  <div class="col-md-6">
                    <div class="p-3 bg-light rounded">
                      <i class="bi bi-lightbulb-fill text-warning me-2"></i>
                      <strong>Simplicity</strong> with clear user flows
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="p-3 bg-light rounded">
                      <i class="bi bi-shield-check-fill text-success me-2"></i>
                      <strong>Accuracy</strong> and consistent handling of medical data
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="p-3 bg-light rounded">
                      <i class="bi bi-speedometer2 text-primary me-2"></i>
                      <strong>Performance</strong> through optimized queries and caching
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="p-3 bg-light rounded">
                      <i class="bi bi-gear-fill text-info me-2"></i>
                      <strong>Automation</strong> of repetitive tasks
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="p-3 bg-light rounded">
                      <i class="bi bi-arrow-up-circle-fill text-success me-2"></i>
                      <strong>Expandable</strong> structure suitable for future enhancements
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="p-3 bg-light rounded">
                      <i class="bi bi-lock-fill text-danger me-2"></i>
                      <strong>Security</strong> practices and validation
                    </div>
                  </div>
                </div>

                <h2 class="h3 fw-bold mb-3">Frameworks and Tools Used</h2>
                <div class="row g-3 mb-5">
                  <div class="col-md-4">
                    <div class="p-3 border rounded text-center">
                      <i class="bi bi-code-slash text-primary fs-2 mb-2"></i>
                      <div class="fw-bold">Flask</div>
                      <small class="text-muted">Backend APIs</small>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="p-3 border rounded text-center">
                      <i class="bi bi-bootstrap text-primary fs-2 mb-2"></i>
                      <div class="fw-bold">VueJS</div>
                      <small class="text-muted">Frontend Framework</small>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="p-3 border rounded text-center">
                      <i class="bi bi-palette text-primary fs-2 mb-2"></i>
                      <div class="fw-bold">Bootstrap</div>
                      <small class="text-muted">Interface Styling</small>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="p-3 border rounded text-center">
                      <i class="bi bi-database text-primary fs-2 mb-2"></i>
                      <div class="fw-bold">SQLite</div>
                      <small class="text-muted">Database</small>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="p-3 border rounded text-center">
                      <i class="bi bi-hdd-stack text-primary fs-2 mb-2"></i>
                      <div class="fw-bold">Redis</div>
                      <small class="text-muted">Caching</small>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="p-3 border rounded text-center">
                      <i class="bi bi-clock-history text-primary fs-2 mb-2"></i>
                      <div class="fw-bold">Celery</div>
                      <small class="text-muted">Background Tasks</small>
                    </div>
                  </div>
                </div>
                <p class="text-muted mb-5">
                  <strong>Note:</strong> No external or unapproved frameworks have been used.
                </p>

                <h2 class="h3 fw-bold mb-3">What This System Demonstrates</h2>
                <div class="row g-3 mb-4">
                  <div class="col-md-6">
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi bi-check2-circle text-success mt-1"></i>
                      <div>
                        <strong>Complete appointment lifecycle management</strong>
                        <p class="text-muted small mb-0">From booking to completion</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi bi-check2-circle text-success mt-1"></i>
                      <div>
                        <strong>Prevention of double booking</strong>
                        <p class="text-muted small mb-0">Same doctor and time slot validation</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi bi-check2-circle text-success mt-1"></i>
                      <div>
                        <strong>Role-based access control</strong>
                        <p class="text-muted small mb-0">Admins, Doctors, and Patients</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi bi-check2-circle text-success mt-1"></i>
                      <div>
                        <strong>Treatment history maintenance</strong>
                        <p class="text-muted small mb-0">Digital medical records</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi bi-check2-circle text-success mt-1"></i>
                      <div>
                        <strong>Automated monthly reports</strong>
                        <p class="text-muted small mb-0">For doctors via Celery</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi bi-check2-circle text-success mt-1"></i>
                      <div>
                        <strong>Daily appointment reminders</strong>
                        <p class="text-muted small mb-0">Automated notifications</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi bi-check2-circle text-success mt-1"></i>
                      <div>
                        <strong>Background CSV export</strong>
                        <p class="text-muted small mb-0">Patient treatment history</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi bi-check2-circle text-success mt-1"></i>
                      <div>
                        <strong>Clean separation</strong>
                        <p class="text-muted small mb-0">Frontend UI and backend logic</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="alert alert-info mt-4 mb-0">
                  <i class="bi bi-info-circle me-2"></i>
                  This project meets the academic requirements while reflecting professional software development practices.
                </div>
              </div>
            </div>

            <div class="text-center">
              <button class="btn btn-primary rounded-pill px-5" @click="$emit('navigate', 'home')">
                <i class="bi bi-arrow-left me-2"></i>Back to Home
              </button>
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
.about-page {
  background: linear-gradient(135deg, rgba(108, 99, 255, 0.05), rgba(91, 192, 235, 0.05));
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--serenity-primary), var(--serenity-secondary));
  box-shadow: var(--serenity-shadow);
}
</style>

