<template>
  <div class="auth-gate min-vh-100 d-flex align-items-center justify-content-center p-3">
    <div class="card card-soft w-100" style="max-width: 420px;">
      <div class="card-body">
        <div class="text-center mb-4">
          <div class="brand-icon rounded-circle d-inline-flex align-items-center justify-content-center mb-3">
            <i class="bi bi-heart-pulse text-white fs-2"></i>
          </div>
          <h3 class="fw-bold mb-3">{{ isRegistering ? 'Join SerenityCare' : 'Welcome Back' }}</h3>
          <div v-if="isRegistering" class="text-muted">
            <p class="mb-2">Create your account, step into the system, and make your hospital visits a little more organized and a lot more peaceful.</p>
            <p class="mb-0 small">We keep everything neat and tidy so you can focus on what matters.</p>
          </div>
          <div v-else class="text-muted">
            <p class="mb-2">Please sign in to continue.</p>
            <p class="mb-2 small">Your dashboard, appointments, and records are ready for you just as you left them.</p>
            <p class="mb-0 small">We keep your experience smooth, secure, and uninterrupted.</p>
          </div>
        </div>
        
        <div class="text-center mb-3">
          <button 
            type="button" 
            class="btn btn-link text-decoration-none text-muted small" 
            @click="$emit('navigate', 'home')"
          >
            <i class="bi bi-arrow-left me-1"></i>Back to Home
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit" novalidate>
          <!-- Login Fields -->
          <div v-if="!isRegistering">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input
                type="text"
                class="form-control rounded-pill"
                v-model.trim="credentials.username"
                required
              />
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input
                type="password"
                class="form-control rounded-pill"
                v-model.trim="credentials.password"
                autocomplete="current-password"
                required
              />
            </div>
          </div>

          <!-- Registration Fields -->
          <div v-else>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label">First Name</label>
                <input type="text" class="form-control rounded-pill" v-model.trim="registerData.first_name" required />
              </div>
              <div class="col-6">
                <label class="form-label">Last Name</label>
                <input type="text" class="form-control rounded-pill" v-model.trim="registerData.last_name" required />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control rounded-pill" v-model.trim="registerData.email" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input type="text" class="form-control rounded-pill" v-model.trim="registerData.username" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control rounded-pill" v-model.trim="registerData.password" autocomplete="new-password" required minlength="6" />
              <div class="form-text">Must be at least 6 characters</div>
            </div>
          </div>

          <button
            class="btn btn-primary w-100 rounded-pill mb-3"
            type="submit"
            :disabled="auth.state.loading"
          >
            <span v-if="auth.state.loading" class="spinner-border spinner-border-sm me-2" />
            {{ isRegistering ? 'Create Account' : 'Sign In' }}
          </button>

          <div class="text-center">
            <button 
              type="button" 
              class="btn btn-link text-decoration-none" 
              @click="toggleMode"
            >
              {{ isRegistering ? 'Already have an account? Sign In' : 'New patient? Create Account' }}
            </button>
          </div>

          <p v-if="auth.state.error" class="text-danger small mt-3 mb-0 text-center">{{ auth.state.error }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useAuthStore } from '../../store/auth';

defineEmits(['navigate']);

const auth = useAuthStore();
const isRegistering = ref(false);

const credentials = reactive({
  username: '',
  password: ''
});

const registerData = reactive({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: ''
});

const toggleMode = () => {
  isRegistering.value = !isRegistering.value;
  auth.state.error = '';
};

const handleSubmit = async () => {
  try {
    if (isRegistering.value) {
      if (!registerData.username || !registerData.password || !registerData.email) return;
      await auth.register(registerData);
      // Wait a moment to ensure token is stored
      await new Promise(resolve => setTimeout(resolve, 100));
      // After successful registration, reload to show dashboard
      window.location.reload();
    } else {
      if (!credentials.username || !credentials.password) return;
      await auth.login(credentials);
      
      // Wait for token to be stored
      await new Promise(resolve => setTimeout(resolve, 150));
      
      // Verify token exists before reload
      const token = localStorage.getItem('serenity_token');
      console.error('[AUTH] AuthGate: Token stored:', token ? 'YES' : 'NO', token);
      
      if (!token) {
        console.error('[ERROR] Token not stored properly after login');
        alert('Login failed: Could not store session');
        return;
      }
      
      console.error('[INFO] Reloading page now...');
      // Reload page to initialize with new token
      window.location.replace('/');
    }
  } catch (error) {
    console.error('Login/Register error:', error);
    // Error is already handled by auth store
  }
};
</script>

<style scoped>
.auth-gate {
  background: linear-gradient(135deg, rgba(108, 99, 255, 0.2), rgba(91, 192, 235, 0.2));
}

.brand-icon {
  width: 72px;
  height: 72px;
  background: var(--serenity-primary);
  box-shadow: var(--serenity-shadow);
}
</style>

