<template>
  <div class="profile-container">
    <div class="row">
      <div class="col-md-8 mx-auto">
        <div class="card">
          <div class="card-body">
            <h1 class="card-title mb-4">Profile Settings</h1>

            <form @submit.prevent="handleSubmit">
              <!-- Basic Info -->
              <h5 class="mb-3">Basic Information</h5>
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input 
                  type="text" 
                  class="form-control"
                  v-model="form.username"
                  disabled
                >
                <small class="text-muted">Username cannot be changed</small>
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control"
                  v-model="form.email"
                  required
                  :class="{ 'is-invalid': errors.email }"
                >
                <div class="invalid-feedback">{{ errors.email }}</div>
              </div>

              <!-- Change Password -->
              <h5 class="mb-3 mt-4">Change Password</h5>
              <div class="mb-3">
                <label class="form-label">Current Password</label>
                <input 
                  type="password" 
                  class="form-control"
                  v-model="form.currentPassword"
                  :class="{ 'is-invalid': errors.currentPassword }"
                >
                <div class="invalid-feedback">{{ errors.currentPassword }}</div>
              </div>

              <div class="mb-3">
                <label class="form-label">New Password</label>
                <input 
                  type="password" 
                  class="form-control"
                  v-model="form.newPassword"
                  :class="{ 'is-invalid': errors.newPassword }"
                >
                <div class="invalid-feedback">{{ errors.newPassword }}</div>
              </div>

              <div class="mb-4">
                <label class="form-label">Confirm New Password</label>
                <input 
                  type="password" 
                  class="form-control"
                  v-model="form.confirmPassword"
                  :class="{ 'is-invalid': errors.confirmPassword }"
                >
                <div class="invalid-feedback">{{ errors.confirmPassword }}</div>
              </div>

              <!-- Roles and Permissions -->
              <h5 class="mb-3">Roles and Permissions</h5>
              <div class="mb-4">
                <div class="mb-2">
                  <strong>Roles:</strong>
                  <span 
                    v-for="role in user?.roles" 
                    :key="role"
                    class="badge bg-secondary ms-2"
                  >
                    {{ role }}
                  </span>
                </div>
                <div>
                  <strong>Permissions:</strong>
                  <div class="mt-2">
                    <span 
                      v-for="permission in user?.permissions" 
                      :key="permission"
                      class="badge bg-light text-dark me-2 mb-2"
                    >
                      {{ permission }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Success/Error Messages -->
              <div v-if="success" class="alert alert-success mb-4">
                {{ success }}
              </div>

              <div v-if="error" class="alert alert-danger mb-4">
                {{ error }}
              </div>

              <!-- Submit Button -->
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Save Changes
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const user = ref(authStore.user)

const form = ref({
  username: user.value?.username || '',
  email: user.value?.email || '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loading = ref(false)
const success = ref('')
const error = ref('')
const errors = ref({})

const validateForm = () => {
  errors.value = {}

  if (!form.value.email) {
    errors.value.email = 'Email is required'
  }

  if (form.value.newPassword) {
    if (!form.value.currentPassword) {
      errors.value.currentPassword = 'Current password is required'
    }
    if (form.value.newPassword.length < 8) {
      errors.value.newPassword = 'Password must be at least 8 characters'
    }
    if (form.value.newPassword !== form.value.confirmPassword) {
      errors.value.confirmPassword = 'Passwords do not match'
    }
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  success.value = ''
  error.value = ''

  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const data = {
      email: form.value.email
    }

    if (form.value.newPassword) {
      data.current_password = form.value.currentPassword
      data.new_password = form.value.newPassword
    }

    await authStore.updateProfile(data)
    success.value = 'Profile updated successfully'
    
    // Reset password fields
    form.value.currentPassword = ''
    form.value.newPassword = ''
    form.value.confirmPassword = ''
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to update profile'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.badge {
  font-weight: 500;
  letter-spacing: 0.5px;
  padding: 0.5em 0.75em;
}
</style> 