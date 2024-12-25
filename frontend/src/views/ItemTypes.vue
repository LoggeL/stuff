# The entire content of the previous Categories.vue file
<template>
  <div class="item-types-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Item Types</h1>
      <button 
        v-if="hasPermission('edit_items')" 
        class="btn btn-primary"
        @click="showCreateItemTypeModal"
      >
        <i class="bi bi-plus-lg"></i> Add Item Type
      </button>
    </div>

    <!-- Item Types Grid -->
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="itemType in itemTypes" :key="itemType.id" class="col">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <h5 class="card-title">
                <i :class="`bi bi-${itemType.icon || 'box'} me-2 text-${itemType.color || 'primary'}`"></i>
                {{ itemType.name }}
              </h5>
            </div>
            <p class="card-text text-muted">{{ itemType.description }}</p>
            
            <!-- Properties List -->
            <div class="properties-list mt-3">
              <h6 class="mb-2">Properties:</h6>
              <ul class="list-unstyled">
                <li v-for="prop in itemType.properties" :key="prop.id" class="mb-1">
                  <small>
                    <i class="bi bi-dot"></i>
                    {{ prop.name }}
                    <span class="text-muted">({{ prop.property_type }})</span>
                    <span v-if="prop.required" class="badge bg-danger ms-1">Required</span>
                  </small>
                </li>
              </ul>
            </div>

            <div class="mt-3">
              <router-link 
                :to="`/items?type=${itemType.id}`"
                class="btn btn-outline-primary me-2"
              >
                <i class="bi bi-box"></i> View Items
              </router-link>
              <button 
                v-if="hasPermission('edit_items')"
                class="btn btn-outline-secondary me-2"
                @click="editItemType(itemType)"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button 
                v-if="hasPermission('delete_items')"
                class="btn btn-outline-danger"
                @click="confirmDeleteItemType(itemType)"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
          <div class="card-footer bg-transparent">
            <small class="text-muted">
              <i class="bi bi-clock"></i>
              Created {{ new Date(itemType.created_at).toLocaleDateString() }}
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
    <div v-if="!loading && itemTypes.length === 0" class="text-center py-5">
      <i class="bi bi-box display-1 text-muted"></i>
      <p class="lead mt-3">No item types found</p>
      <button 
        v-if="hasPermission('edit_items')"
        class="btn btn-primary mt-2"
        @click="showCreateItemTypeModal"
      >
        Create your first item type
      </button>
    </div>

    <!-- Item Type Modal -->
    <div class="modal fade" id="itemTypeModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingItemType ? 'Edit Item Type' : 'Create Item Type' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="handleSubmit">
            <div class="modal-body">
              <!-- Basic Info -->
              <div class="mb-4">
                <h6 class="mb-3">Basic Information</h6>
                <div class="mb-3">
                  <label class="form-label">Name</label>
                  <input 
                    type="text" 
                    class="form-control"
                    v-model="form.name"
                    required
                  >
                </div>
                <div class="mb-3">
                  <label class="form-label">Description</label>
                  <textarea 
                    class="form-control"
                    v-model="form.description"
                    rows="2"
                  ></textarea>
                </div>
              </div>

              <!-- Properties -->
              <div class="mb-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h6 class="mb-0">Properties</h6>
                  <button 
                    type="button"
                    class="btn btn-sm btn-outline-primary"
                    @click="addProperty"
                  >
                    <i class="bi bi-plus"></i> Add Property
                  </button>
                </div>
                
                <div v-for="(prop, index) in form.properties" :key="index" class="card mb-3">
                  <div class="card-body">
                    <div class="row g-3">
                      <div class="col-md-4">
                        <label class="form-label">Name</label>
                        <input 
                          type="text" 
                          class="form-control"
                          v-model="prop.name"
                          required
                        >
                      </div>
                      <div class="col-md-3">
                        <label class="form-label">Type</label>
                        <select class="form-select" v-model="prop.property_type" required>
                          <option value="text">Text</option>
                          <option value="number">Number</option>
                          <option value="date">Date</option>
                          <option value="boolean">Boolean</option>
                          <option value="select">Select</option>
                        </select>
                      </div>
                      <div class="col-md-3">
                        <label class="form-label">Required</label>
                        <div class="form-check form-switch mt-2">
                          <input 
                            class="form-check-input" 
                            type="checkbox"
                            v-model="prop.required"
                          >
                        </div>
                      </div>
                      <div class="col-md-2">
                        <label class="form-label d-block">&nbsp;</label>
                        <button 
                          type="button" 
                          class="btn btn-outline-danger btn-sm"
                          @click="removeProperty(index)"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                      <!-- Options for select type -->
                      <div class="col-12" v-if="prop.property_type === 'select'">
                        <label class="form-label">Options (comma-separated)</label>
                        <input 
                          type="text" 
                          class="form-control"
                          v-model="prop.options"
                          placeholder="Option 1, Option 2, Option 3"
                        >
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingItemType ? 'Update' : 'Create' }}
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
            <h5 class="modal-title">Delete Item Type</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete item type "{{ itemTypeToDelete?.name }}"?
            This action cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger"
              @click="deleteItemType"
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

const itemTypes = ref([])
const loading = ref(false)
const editingItemType = ref(null)
const itemTypeToDelete = ref(null)
const itemTypeModal = ref(null)
const deleteModal = ref(null)

const form = ref({
  name: '',
  description: '',
  properties: []
})

onMounted(async () => {
  itemTypeModal.value = new Modal(document.getElementById('itemTypeModal'))
  deleteModal.value = new Modal(document.getElementById('deleteModal'))
  await fetchItemTypes()
})

const fetchItemTypes = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/item_types')
    itemTypes.value = response.data
  } catch (error) {
    console.error('Failed to fetch item types:', error)
  } finally {
    loading.value = false
  }
}

const showCreateItemTypeModal = () => {
  editingItemType.value = null
  form.value = { 
    name: '',
    description: '',
    properties: []
  }
  itemTypeModal.value.show()
}

const editItemType = (itemType) => {
  editingItemType.value = itemType
  form.value = { 
    name: itemType.name,
    description: itemType.description,
    properties: itemType.properties.map(prop => ({
      ...prop,
      options: Array.isArray(prop.options) ? prop.options.join(', ') : prop.options
    }))
  }
  itemTypeModal.value.show()
}

const addProperty = () => {
  form.value.properties.push({
    name: '',
    property_type: 'text',
    required: false,
    options: ''
  })
}

const removeProperty = (index) => {
  form.value.properties.splice(index, 1)
}

const handleSubmit = async () => {
  loading.value = true
  try {
    // Process properties to convert options string to array
    const processedForm = {
      ...form.value,
      properties: form.value.properties.map(prop => ({
        ...prop,
        options: prop.property_type === 'select' && prop.options 
          ? prop.options.split(',').map(opt => opt.trim())
          : undefined
      }))
    }

    if (editingItemType.value) {
      await axios.put(`/api/item_types/${editingItemType.value.id}`, processedForm)
    } else {
      await axios.post('/api/item_types', processedForm)
    }
    await fetchItemTypes()
    itemTypeModal.value.hide()
  } catch (error) {
    console.error('Failed to save item type:', error)
  } finally {
    loading.value = false
  }
}

const confirmDeleteItemType = (itemType) => {
  itemTypeToDelete.value = itemType
  deleteModal.value.show()
}

const deleteItemType = async () => {
  if (!itemTypeToDelete.value) return

  loading.value = true
  try {
    await axios.delete(`/api/item_types/${itemTypeToDelete.value.id}`)
    await fetchItemTypes()
    deleteModal.value.hide()
  } catch (error) {
    console.error('Failed to delete item type:', error)
  } finally {
    loading.value = false
    itemTypeToDelete.value = null
  }
}
</script>

<style lang="scss" scoped>
.item-types-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-5px);
  }
}

.properties-list {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.25rem;
}
</style> 