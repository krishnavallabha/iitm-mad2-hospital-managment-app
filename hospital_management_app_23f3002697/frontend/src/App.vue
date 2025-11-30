<template>
  <div class="app-shell bg-light">
    <PwaPrompt />
    <Toast />
    <!-- Show public pages (Home, About) or Login when not authenticated -->
    <HomePage v-if="!isAuthenticated && currentPage === 'home'" @navigate="handleNavigate" />
    <AboutPage v-else-if="!isAuthenticated && currentPage === 'about'" @navigate="handleNavigate" />
    <AuthGate v-else-if="!isAuthenticated && currentPage === 'login'" @navigate="handleNavigate" />
    <!-- Show dashboard when authenticated -->
    <div v-else class="d-flex flex-column flex-lg-row min-vh-100">
      <div class="flex-grow-1 d-flex flex-column">
        <TopBar 
          :user="auth.state.user" 
          @logout="handleLogout" 
          @navigate="handlePatientNavigate"
          @edit-profile="showProfileModal = true"
        />
        <main class="flex-grow-1 p-2 p-md-3 p-lg-4">
          <component :is="currentView" @navigate="handlePatientNavigate" />
        </main>
      </div>
    </div>
    
    <!-- Global Modals -->
    <ProfileModal
      v-if="showProfileModal"
      @close="showProfileModal = false"
      @saved="handleProfileSaved"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import TopBar from './components/TopBar.vue';
import DashboardGrid from './components/dashboard/DashboardGrid.vue';
import AdminDashboard from './views/AdminDashboard.vue';
import DoctorDashboard from './views/DoctorDashboard.vue';
import PatientDashboard from './views/PatientDashboard.vue';
import DepartmentsPage from './views/DepartmentsPage.vue';
import HomePage from './views/HomePage.vue';
import AboutPage from './views/AboutPage.vue';
import PwaPrompt from './components/PwaPrompt.vue';
import AuthGate from './components/auth/AuthGate.vue';
import Toast from './components/common/Toast.vue';
import ProfileModal from './components/patient/ProfileModal.vue';
import { useAuthStore } from './store/auth';

const auth = useAuthStore();

// Current page state for public pages (home, about, login) and patient sub-pages
const currentPage = ref('home');
const patientSubPage = ref('dashboard'); // 'dashboard' or 'departments'
const showProfileModal = ref(false);

const handleProfileSaved = () => {
  showProfileModal.value = false;
  // Optionally trigger a user refresh if needed, though auth store should be updated
};

// Handle navigation between public pages
const handleNavigate = (page) => {
  currentPage.value = page;
};

// Handle logout - clear session and return to home
const handleLogout = () => {
  auth.clearSession();
  currentPage.value = 'home';
};

// Computed property to check if user is authenticated
// Checks both reactive state AND localStorage to be sure
const isAuthenticated = computed(() => {
  // First check reactive state - if no user in state, definitely not authenticated
  if (!auth.state.user) {
    return false;
  }
  
  // Check localStorage for token
  const token = localStorage.getItem('serenity_token');
  if (!token || !token.trim() || !token.startsWith('eyJ')) {
    // Invalid token - clear state and return false
    if (auth.state.user) {
      auth.clearSession();
    }
    return false;
  }
  
  // Check localStorage for user
  const user = localStorage.getItem('serenity_user');
  if (!user || user === 'null') {
    // No user data - clear state and return false
    if (auth.state.user) {
      auth.clearSession();
    }
    return false;
  }
  
  // Both token and user exist, and state has user - authenticated
  return true;
});

// Verify token exists on mount
onMounted(() => {
  const token = localStorage.getItem('serenity_token');
  const user = localStorage.getItem('serenity_user');
  
  // If no token, clear any stale user data and ensure user is null
  if (!token || !token.trim()) {
    console.log(' App.vue: No token found in localStorage - showing home page');
    if (user || auth.state.user) {
      console.log(' App.vue: Clearing stale user data');
      auth.clearSession();
    }
    auth.state.user = null;
    currentPage.value = 'home'; // Ensure we show home page
    return;
  }
  
  // Verify token is valid format (should start with eyJ for JWT)
  if (!token.startsWith('eyJ')) {
    console.log(' App.vue: Invalid token format - clearing session');
    auth.clearSession();
    auth.state.user = null;
    currentPage.value = 'home'; // Show home page
    return;
  }
  
  // If we have both token and user, sync auth store
  if (user) {
    try {
      const userData = JSON.parse(user);
      // Always sync to ensure state is correct
      auth.state.user = userData;
      auth.state.token = token;
    } catch (e) {
      console.error('Error parsing user data:', e);
      auth.clearSession();
      auth.state.user = null;
      currentPage.value = 'home'; // Show home page on error
    }
  } else {
    // No user data but token exists - clear everything
    auth.clearSession();
    auth.state.user = null;
    currentPage.value = 'home'; // Show home page
  }
});

const currentView = computed(() => {
  // CRITICAL: Always check localStorage first, not just reactive state
  const token = localStorage.getItem('serenity_token');
  const user = localStorage.getItem('serenity_user');
  
  // If no token or invalid token, show login screen
  if (!token || !token.trim() || !token.startsWith('eyJ')) {
    return DashboardGrid; // This will show AuthGate instead
  }
  
  // If no user data, show login screen
  if (!user) {
    return DashboardGrid;
  }
  
  // If we have token and user, check reactive state
  if (!auth.state.user) {
    // Try to restore from localStorage
    try {
      const userData = JSON.parse(user);
      auth.setSession(userData, token);
    } catch (e) {
      console.error('Error parsing user data:', e);
      return DashboardGrid;
    }
  }
  
  // Now show appropriate dashboard based on role
  if (!auth.state.user) return DashboardGrid;
  
  // Handle patient sub-pages
  if (auth.state.user.role === 'patient') {
    if (patientSubPage.value === 'departments') {
      return DepartmentsPage;
    }
    return PatientDashboard;
  }
  
  switch (auth.state.user.role) {
    case 'admin':
      return AdminDashboard;
    case 'doctor':
      return DoctorDashboard;
    default:
      return DashboardGrid;
  }
});

const handlePatientNavigate = (page, ...args) => {
  if (page === 'departments') {
    patientSubPage.value = 'departments';
  } else if (page === 'dashboard' || page === 'back') {
    patientSubPage.value = 'dashboard';
  }
  // Handle other events like view-doctor, book-doctor if needed
  // These can be passed to PatientDashboard component
};
</script>

