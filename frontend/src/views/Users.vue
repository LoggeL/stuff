<template>
  <div class="users-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>User Management</h1>
      <button class="btn btn-primary" @click="showCreateUserModal">
        <i class="bi bi-person-plus"></i> Add User
      </button>
    </div>

    <!-- Users Table -->
    <div class="card">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Roles</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span 
                  v-for="role in user.roles" 
                  :key="role"
                  class="badge bg-secondary me-1"
                >
                  {{ role }}
                </span>
              </td>
              <td>
                <span 
                  class="badge"
                  :class="user.is_active ? 'bg-success' : 'bg-danger'"
                >
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <div class="btn-group">
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="editUser(user)"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmDeleteUser(user)"
                    :disabled="user.id === currentUser?.id"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit User Modal -->
    <div class="modal fade" id="userModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingUser ? 'Edit User' : 'Create User' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="handleSubmit">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input 
                  type="text" 
                  class="form-control"
                  v-model="form.username"
                  :disabled="editingUser"
                  required
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control"
                  v-model="form.email"
                  required
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input 
                  type="password" 
                  class="form-control"
                  v-model="form.password"
                  :required="!editingUser"
                >
                <small class="text-muted" v-if="editingUser">
                  Leave blank to keep current password
                </small>
              </div>
              <div class="mb-3">
                <label class="form-label">Roles</label>
                <div class="form-check" v-for="role in availableRoles" :key="role">
                  <input 
                    class="form-check-input" 
                    type="checkbox"
                    :value="role"
                    v-model="form.roles"
                  >
                  <label class="form-check-label">{{ role }}</label>
                </div>
              </div>
              <div class="mb-3">
                <div class="form-check form-switch">
                  <input 
                    class="form-check-input" 
                    type="checkbox"
                    v-model="form.is_active"
                  >
                  <label class="form-check-label">Active</label>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingUser ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Delete User</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete user "{{ userToDelete?.username }}"?
            This action cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger"
              @click="deleteUser"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { Modal } from 'bootstrap'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

const users = ref([])
const loading = ref(false)
const editingUser = ref(null)
const userToDelete = ref(null)
const userModal = ref(null)
const deleteModal = ref(null)

const form = ref({
  username: '',
  email: '',
  password: '',
  roles: [],
  is_active: true
})

const availableRoles = ['admin', 'manager', 'user']

onMounted(async () => {
  userModal.value = new Modal(document.getElementById('userModal'))
  deleteModal.value = new Modal(document.getElementById('deleteModal'))
  await fetchUsers()
})

const fetchUsers = async () => {
  try {
    const response = await axios.get('/api/users')
    users.value = response.data
  } catch (error) {
    console.error('Failed to fetch users:', error)
  }
}

const showCreateUserModal = () => {
  editingUser.value = null
  form.value = {
    username: '',
    email: '',
    password: '',
    roles: ['user'],
    is_active: true
  }
  userModal.value.show()
}

const editUser = (user) => {
  editingUser.value = user
  form.value = {
    username: user.username,
    email: user.email,
    password: '',
    roles: [...user.roles],
    is_active: user.is_active
  }
  userModal.value.show()
}

const handleSubmit = async () => {
  loading.value = true
  try {
    if (editingUser.value) {
      await axios.put(`/api/users/${editingUser.value.id}`, form.value)
    } else {
      await axios.post('/api/users', form.value)
    }
    await fetchUsers()
    userModal.value.hide()
  } catch (error) {
    console.error('Failed to save user:', error)
  } finally {
    loading.value = false
  }
}

const confirmDeleteUser = (user) => {
  userToDelete.value = user
  deleteModal.value.show()
}

const deleteUser = async () => {
  if (!userToDelete.value) return

  loading.value = true
  try {
    await axios.delete(`/api/users/${userToDelete.value.id}`)
    await fetchUsers()
    deleteModal.value.hide()
  } catch (error) {
    console.error('Failed to delete user:', error)
  } finally {
    loading.value = false
    userToDelete.value = null
  }
}
</script>

<style lang="scss" scoped>
.users-container {
  max-width: 1200px;
  margin: 0 auto;
}

.table {
  th, td {
    vertical-align: middle;
  }
}

.badge {
  text-transform: capitalize;
}
</style> 