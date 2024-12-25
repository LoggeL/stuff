<template>
  <div class="locations-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Locations</h1>
      <button 
        v-if="hasPermission('add_locations')" 
        class="btn btn-primary"
        @click="showCreateLocationModal"
      >
        <i class="bi bi-plus-lg"></i> Add Location
      </button>
    </div>

    <!-- Locations Grid -->
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="location in locations" :key="location.id" class="col">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <h5 class="card-title">{{ location.name }}</h5>
              <div class="badge bg-primary">
                {{ location.items?.length || 0 }} Items
              </div>
            </div>
            <div class="mt-3">
              <router-link 
                :to="`/items?location=${location.id}`"
                class="btn btn-outline-primary me-2"
              >
                <i class="bi bi-box"></i> View Items
              </router-link>
              <button 
                v-if="hasPermission('edit_locations')"
                class="btn btn-outline-secondary me-2"
                @click="editLocation(location)"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button 
                v-if="hasPermission('delete_locations')"
                class="btn btn-outline-danger"
                @click="confirmDeleteLocation(location)"
                :disabled="location.items?.length > 0"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
          <div class="card-footer bg-transparent">
            <small class="text-muted">
              <i class="bi bi-clock"></i>
              Created {{ new Date(location.created_at).toLocaleDateString() }}
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && locations.length === 0" class="text-center py-5">
      <i class="bi bi-geo-alt display-1 text-muted"></i>
      <p class="lead mt-3">No locations found</p>
      <button 
        v-if="hasPermission('add_locations')"
        class="btn btn-primary mt-2"
        @click="showCreateLocationModal"
      >
        Create your first location
      </button>
    </div>

    <!-- Location Modal -->
    <div class="modal fade" id="locationModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingLocation ? 'Edit Location' : 'Create Location' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="handleSubmit">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Name</label>
                <input 
                  type="text" 
                  class="form-control"
                  v-model="form.name"
                  required
                >
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingLocation ? 'Update' : 'Create' }}
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
            <h5 class="modal-title">Delete Location</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete location "{{ locationToDelete?.name }}"?
            This action cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger"
              @click="deleteLocation"
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { Modal } from 'bootstrap'

const authStore = useAuthStore()
const hasPermission = (permission) => authStore.hasPermission(permission)

const locations = ref([])
const loading = ref(false)
const editingLocation = ref(null)
const locationToDelete = ref(null)
const locationModal = ref(null)
const deleteModal = ref(null)

const form = ref({
  name: ''
})

onMounted(async () => {
  locationModal.value = new Modal(document.getElementById('locationModal'))
  deleteModal.value = new Modal(document.getElementById('deleteModal'))
  await fetchLocations()
})

const fetchLocations = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/locations')
    locations.value = response.data
  } catch (error) {
    console.error('Failed to fetch locations:', error)
  } finally {
    loading.value = false
  }
}

const showCreateLocationModal = () => {
  editingLocation.value = null
  form.value = { name: '' }
  locationModal.value.show()
}

const editLocation = (location) => {
  editingLocation.value = location
  form.value = { name: location.name }
  locationModal.value.show()
}

const handleSubmit = async () => {
  loading.value = true
  try {
    if (editingLocation.value) {
      await axios.put(`/api/locations/${editingLocation.value.id}`, form.value)
    } else {
      await axios.post('/api/locations', form.value)
    }
    await fetchLocations()
    locationModal.value.hide()
  } catch (error) {
    console.error('Failed to save location:', error)
  } finally {
    loading.value = false
  }
}

const confirmDeleteLocation = (location) => {
  locationToDelete.value = location
  deleteModal.value.show()
}

const deleteLocation = async () => {
  if (!locationToDelete.value) return

  loading.value = true
  try {
    await axios.delete(`/api/locations/${locationToDelete.value.id}`)
    await fetchLocations()
    deleteModal.value.hide()
  } catch (error) {
    console.error('Failed to delete location:', error)
  } finally {
    loading.value = false
    locationToDelete.value = null
  }
}
</script>

<style lang="scss" scoped>
.locations-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-5px);
  }
}
</style> 