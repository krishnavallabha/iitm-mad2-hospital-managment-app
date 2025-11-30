<template>
  <div class="admin-departments">
    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">Department Management</h3>
        <p class="text-muted small mb-0">Manage SerenityCare medical departments and specializations</p>
      </div>
      <button class="btn btn-primary rounded-pill" @click="showDepartmentModal = true">
        <i class="bi bi-plus-lg me-2"></i>Add Department
      </button>
    </div>

    <!-- Departments Grid -->
    <div class="row g-4 mb-4">
      <div class="col-12 col-md-6 col-lg-4" v-for="dept in departments" :key="dept.id">
        <div class="card card-soft border-0 shadow-sm h-100 department-card" @click="viewDepartmentDetails(dept)" style="cursor: pointer;">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="department-icon rounded-circle d-flex align-items-center justify-content-center bg-primary-subtle text-primary">
                <i class="bi bi-hospital fs-4"></i>
              </div>
              <div class="dropdown" @click.stop>
                <button class="btn btn-sm btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                  <i class="bi bi-three-dots-vertical"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li><a class="dropdown-item" href="#" @click.prevent="editDepartment(dept)"><i class="bi bi-pencil me-2"></i>Edit</a></li>
                  <li><a class="dropdown-item text-danger" href="#" @click.prevent="deleteDepartment(dept)"><i class="bi bi-trash me-2"></i>Delete</a></li>
                </ul>
              </div>
            </div>
            <h5 class="fw-bold mb-2">{{ dept.name }}</h5>
            <p class="text-muted small mb-3">{{ dept.description || 'No description available' }}</p>
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <span class="badge bg-primary-subtle text-primary rounded-pill me-2">
                  <i class="bi bi-people me-1"></i>{{ dept.doctors_count || 0 }} Doctors
                </span>
                <span class="badge bg-success-subtle text-success rounded-pill" v-if="dept.is_active !== false">
                  Active
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="departments.length === 0 && !loading" class="col-12">
        <div class="card card-soft border-0 text-center py-5">
          <div class="card-body">
            <i class="bi bi-hospital fs-1 text-muted mb-3 d-block"></i>
            <h5 class="fw-bold mb-2">No Departments</h5>
            <p class="text-muted mb-3">Get started by adding your first department</p>
            <button class="btn btn-primary rounded-pill" @click="showDepartmentModal = true">
              <i class="bi bi-plus-lg me-2"></i>Add Department
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Department Details Modal -->
    <DepartmentDetailsModal
      v-if="showDepartmentDetailsModal"
      :department-id="selectedDepartmentId"
      @close="closeDepartmentDetailsModal"
      @edit="handleEditFromDetails"
      @delete="handleDeleteFromDetails"
    />

    <!-- Add/Edit Department Modal -->
    <div v-if="showDepartmentModal" class="modal-backdrop show d-flex align-items-center justify-content-center" @click.self="closeDepartmentModal">
      <div class="card card-soft w-100" style="max-width: 500px;">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h5 class="fw-bold mb-0">{{ editingDepartment ? 'Edit Department' : 'Add New Department' }}</h5>
              <p class="text-muted small mb-0">Manage department information</p>
            </div>
            <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="closeDepartmentModal">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          <form @submit.prevent="saveDepartment">
            <div class="mb-3">
              <label class="form-label">Department Name <span class="text-danger">*</span></label>
              <input
                type="text"
                class="form-control rounded-pill"
                v-model.trim="departmentForm.name"
                placeholder="e.g., Cardiology"
                required
              />
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea
                class="form-control rounded-4"
                rows="3"
                v-model.trim="departmentForm.description"
                placeholder="Brief description of the department..."
              ></textarea>
            </div>
            <div class="d-flex gap-2">
              <button type="button" class="btn btn-outline-secondary rounded-pill flex-grow-1" @click="closeDepartmentModal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary rounded-pill flex-grow-1" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingDepartment ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:visible="confirm.state.visible"
      :title="confirm.state.title"
      :message="confirm.state.message"
      :details="confirm.state.details"
      :type="confirm.state.type"
      :confirm-text="confirm.state.confirmText"
      :cancel-text="confirm.state.cancelText"
      :loading="confirm.state.loading"
      @confirm="confirm.confirm"
      @cancel="confirm.hide"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../services/api';
import { useConfirm } from '../composables/useConfirm';
import { useToast } from '../composables/useToast';
import ConfirmationDialog from '../components/common/ConfirmationDialog.vue';
import DepartmentDetailsModal from '../components/admin/DepartmentDetailsModal.vue';

const confirm = useConfirm();
const toast = useToast();

const departments = ref([]);
const loading = ref(true);
const showDepartmentModal = ref(false);
const showDepartmentDetailsModal = ref(false);
const selectedDepartmentId = ref(null);
const editingDepartment = ref(null);
const saving = ref(false);

const departmentForm = reactive({
  name: '',
  description: ''
});

const fetchDepartments = async () => {
  try {
    loading.value = true;
    const { data } = await api.get('/admin/departments');
    
    // Fetch doctor counts for each department
    const departmentsWithCounts = await Promise.all(
      (data.departments || []).map(async (dept) => {
        try {
          const { data: doctorsData } = await api.get('/admin/doctors', {
            params: { specialization_id: dept.id }
          });
          return {
            ...dept,
            doctors_count: doctorsData.doctors?.length || 0
          };
        } catch {
          return { ...dept, doctors_count: 0 };
        }
      })
    );
    
    departments.value = departmentsWithCounts;
  } catch (error) {
    console.error('Error fetching departments:', error);
    toast.error('Error', 'Failed to fetch departments');
  } finally {
    loading.value = false;
  }
};

const closeDepartmentModal = () => {
  showDepartmentModal.value = false;
  editingDepartment.value = null;
  departmentForm.name = '';
  departmentForm.description = '';
};

const editDepartment = (dept) => {
  editingDepartment.value = dept;
  departmentForm.name = dept.name;
  departmentForm.description = dept.description || '';
  showDepartmentModal.value = true;
};

const saveDepartment = async () => {
  if (!departmentForm.name.trim()) {
    toast.error('Error', 'Department name is required');
    return;
  }

  try {
    saving.value = true;
    if (editingDepartment.value) {
      // Update department - Note: API might not support PUT, adjust if needed
      await api.put(`/admin/departments/${editingDepartment.value.id}`, departmentForm);
      toast.success('Success', 'Department updated successfully');
    } else {
      await api.post('/admin/departments', departmentForm);
      toast.success('Success', 'Department created successfully');
    }
    closeDepartmentModal();
    await fetchDepartments();
  } catch (error) {
    toast.error('Error', error.response?.data?.error || 'Failed to save department');
  } finally {
    saving.value = false;
  }
};

const viewDepartmentDetails = (dept) => {
  selectedDepartmentId.value = dept.id;
  showDepartmentDetailsModal.value = true;
};

const closeDepartmentDetailsModal = () => {
  showDepartmentDetailsModal.value = false;
  selectedDepartmentId.value = null;
};

const handleEditFromDetails = (dept) => {
  closeDepartmentDetailsModal();
  editDepartment(dept);
};

const handleDeleteFromDetails = async (dept) => {
  console.log('handleDeleteFromDetails called with:', dept);
  
  // Ensure we have a valid department object with id and name
  if (!dept || !dept.id) {
    console.warn('Department missing id, trying to find from list');
    // Try to find the department from the list
    const departmentFromList = departments.value.find(d => d.id === dept?.id);
    if (departmentFromList) {
      closeDepartmentDetailsModal();
      await deleteDepartment(departmentFromList);
    } else {
      toast.error('Error', 'Department information not found');
      closeDepartmentDetailsModal();
    }
    return;
  }
  
  closeDepartmentDetailsModal();
  await deleteDepartment(dept);
};

const deleteDepartment = async (dept) => {
  console.log('Delete department called with:', dept);
  
  if (!dept || !dept.id) {
    console.error('Invalid department:', dept);
    toast.error('Error', 'Invalid department information');
    return;
  }

  // Use window.confirm as primary method for reliability
  const confirmed = window.confirm(
    `WARNING: Are you sure you want to delete "${dept.name || 'this department'}"?\n\n` +
    `This action cannot be undone. All associated doctors will need to be reassigned.`
  );

  if (!confirmed) {
    console.log('User cancelled deletion');
    return;
  }

  // User confirmed - proceed with deletion
  try {
    console.log('Calling API to delete department:', dept.id);
    const response = await api.delete(`/admin/departments/${dept.id}`);
    console.log('Delete response:', response);
    toast.success('Success', 'Department deleted successfully');
    await fetchDepartments();
  } catch (error) {
    console.error('Error deleting department:', error);
    console.error('Error details:', error.response);
    const errorMessage = error.response?.data?.error || error.message || 'Failed to delete department';
    toast.error('Error', errorMessage);
  }
};

onMounted(() => {
  fetchDepartments();
});
</script>

<style scoped>
.admin-departments {
  animation: fadeIn 0.3s ease-in;
}

.department-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.department-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

.department-icon {
  width: 56px;
  height: 56px;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #6c757d !important; /* Solid opaque grey - 100% opacity */
  opacity: 1 !important; /* Force 100% opacity */
  z-index: 1055;
  padding: 1.5rem;
}

.modal-backdrop::before {
  display: none; /* Remove any pseudo-elements that might affect opacity */
}

.modal-backdrop .card {
  background: white !important;
  opacity: 1 !important;
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

/* Mobile Responsive */
@media (max-width: 991.98px) {
  .col-md-6,
  .col-lg-4 {
    margin-bottom: 1rem;
  }
}

@media (max-width: 767.98px) {
  .modal-backdrop {
    padding: 0.5rem !important;
  }
  
  .modal-backdrop .card {
    max-width: 100% !important;
    margin: 0 !important;
  }
  
  .card-body {
    padding: 1rem !important;
  }
  
  .form-control,
  .form-select,
  textarea {
    font-size: 16px; /* Prevents zoom on iOS */
  }
  
  .department-card {
    margin-bottom: 1rem;
  }
  
  .department-icon {
    width: 48px;
    height: 48px;
  }
}

@media (max-width: 575.98px) {
  .modal-backdrop {
    padding: 0.25rem !important;
  }
  
  .card-body {
    padding: 0.75rem !important;
  }
  
  h5 {
    font-size: 1.1rem;
  }
  
  .col-12 {
    padding: 0;
  }
  
  .d-flex.gap-2 {
    flex-direction: column;
  }
  
  .d-flex.gap-2 .btn {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}
</style>

