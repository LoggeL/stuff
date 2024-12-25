<template>
  <div class="items-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Items</h1>
      <button 
        v-if="hasPermission('add_items')" 
        class="btn btn-primary"
        @click="showCreateItemModal"
      >
        <i class="bi bi-plus-lg"></i> Add Item
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search items..."
                v-model="filters.search"
              >
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filters.location">
              <option value="">All Locations</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                {{ loc.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filters.type">
              <option value="">All Types</option>
              <option v-for="type in itemTypes" :key="type.id" :value="type.id">
                {{ type.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              Reset
            </button>
          </div>
        </div>

        <!-- Property Filters -->
        <div v-if="selectedType" class="row g-3 mt-3">
          <div class="col-12">
            <h6 class="mb-3">Property Filters:</h6>
          </div>
          <div v-for="prop in selectedType.properties" :key="prop.id" class="col-md-3">
            <label class="form-label">{{ prop.name }}</label>
            <!-- Text/Number Input -->
            <input 
              v-if="['text', 'number'].includes(prop.property_type)"
              :type="prop.property_type"
              class="form-control"
              v-model="propertyFilters[prop.id]"
              :placeholder="'Filter by ' + prop.name"
            >
            <!-- Select Input -->
            <select 
              v-else-if="prop.property_type === 'select'"
              class="form-select"
              v-model="propertyFilters[prop.id]"
            >
              <option value="">All {{ prop.name }}</option>
              <option v-for="option in prop.options" :key="option" :value="option">
                {{ option }}
              </option>
            </select>
            <!-- Boolean Input -->
            <select 
              v-else-if="prop.property_type === 'boolean'"
              class="form-select"
              v-model="propertyFilters[prop.id]"
            >
              <option value="">All</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
            <!-- Date Input -->
            <input 
              v-else-if="prop.property_type === 'date'"
              type="date"
              class="form-control"
              v-model="propertyFilters[prop.id]"
            >
          </div>
        </div>
      </div>
    </div>

    <!-- Items Grid -->
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="item in items" :key="item.id" class="col">
        <div class="card h-100">
          <div class="item-image" v-if="item.files && item.files.length > 0">
            <img :src="`${staticUrl}/${item.files[0].filename}`" :alt="item.name">
          </div>
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <h5 class="card-title">{{ item.name }}</h5>
              <span class="badge bg-primary">{{ item.item_type.name }}</span>
            </div>
            <p class="card-text text-muted" v-if="item.location">
              <i class="bi bi-geo-alt"></i> {{ item.location.name }}
            </p>
            <div class="mt-3">
              <button 
                class="btn btn-outline-primary me-2"
                @click="viewItem(item)"
              >
                <i class="bi bi-eye"></i> View
              </button>
              <button 
                v-if="hasPermission('edit_items')"
                class="btn btn-outline-secondary me-2"
                @click="editItem(item)"
              >
                <i class="bi bi-pencil"></i> Edit
              </button>
              <button 
                v-if="hasPermission('delete_items')"
                class="btn btn-outline-danger"
                @click="confirmDeleteItem(item)"
              >
                <i class="bi bi-trash"></i> Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="text-center my-5">
      <p class="text-muted">No items found. Try adjusting your filters or create a new item.</p>
    </div>

    <!-- View Item Modal -->
    <div class="modal fade" id="viewItemModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedItem?.name }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedItem">
            <div class="item-details">
              <dl class="row">
                <dt class="col-sm-4">Type</dt>
                <dd class="col-sm-8">{{ selectedItem.item_type.name }}</dd>

                <dt class="col-sm-4">Location</dt>
                <dd class="col-sm-8">{{ selectedItem.location?.name || 'Not specified' }}</dd>

                <dt class="col-sm-4">Properties</dt>
                <dd class="col-sm-8">
                  <dl class="row mb-0">
                    <template v-for="value in selectedItem.property_values" :key="value.property_id">
                      <dt class="col-sm-4">{{ value.property_name }}</dt>
                      <dd class="col-sm-8">
                        <template v-if="value.property_type === 'boolean'">
                          <i class="bi" :class="value.value ? 'bi-check-lg text-success' : 'bi-x-lg text-danger'"></i>
                          {{ value.value ? 'Yes' : 'No' }}
                        </template>
                        <template v-else-if="value.property_type === 'date'">
                          {{ new Date(value.value).toLocaleDateString() }}
                        </template>
                        <template v-else>
                          {{ value.value }}
                        </template>
                      </dd>
                    </template>
                  </dl>
                </dd>

                <template v-if="selectedItem.files && selectedItem.files.length > 0">
                  <dt class="col-sm-4">Files</dt>
                  <dd class="col-sm-8">
                    <div class="list-group">
                      <div v-for="file in selectedItem.files" :key="file.filename" 
                           class="list-group-item d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                          <i class="bi me-2" :class="getFileIcon(file.mime_type)"></i>
                          {{ file.original_filename }}
                          <small class="text-muted ms-2">({{ formatFileSize(file.size) }})</small>
                        </div>
                        <div class="btn-group">
                          <a :href="`${staticUrl}/${file.filename}`" 
                             class="btn btn-sm btn-outline-primary" 
                             target="_blank"
                             download>
                            <i class="bi bi-download"></i>
                          </a>
                          <button v-if="hasPermission('edit_items')"
                                  type="button" 
                                  class="btn btn-sm btn-outline-danger"
                                  @click="deleteFile(file)">
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </dd>
                </template>
              </dl>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button 
              v-if="hasPermission('edit_items')" 
              type="button" 
              class="btn btn-primary"
              @click="editItem(selectedItem)"
            >
              Edit Item
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Item Modal -->
    <div class="modal fade" id="createItemModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedItem ? 'Edit Item' : 'Create New Item' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="selectedItem ? updateItem() : createItem()">
              <div class="mb-3">
                <label class="form-label">Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="itemName"
                  required
                >
              </div>
              
              <!-- Image Upload -->
              <div class="mb-3">
                <label class="form-label">Image</label>
                <div class="d-flex align-items-center gap-3">
                  <div v-if="selectedItem?.files?.length > 0 || previewImage" 
                       class="item-image-preview">
                    <img :src="previewImage || `${staticUrl}/${selectedItem.files[0].filename}`" 
                         class="img-fluid" 
                         alt="Item preview">
                  </div>
                  <div class="d-flex flex-column gap-2">
                    <input 
                      type="file" 
                      class="form-control" 
                      accept="image/*"
                      @change="handleImageUpload"
                      ref="fileInput"
                    >
                    <button 
                      v-if="selectedItem?.files?.length > 0 || previewImage"
                      type="button" 
                      class="btn btn-outline-danger"
                      @click="removeImage"
                    >
                      Remove Image
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Location</label>
                <select 
                  class="form-select" 
                  v-model="itemLocation"
                >
                  <option value="">Select Location</option>
                  <option 
                    v-for="location in locations" 
                    :key="location.id" 
                    :value="location.id"
                  >
                    {{ location.name }}
                  </option>
                </select>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Item Type</label>
                <select 
                  class="form-select" 
                  v-model="itemType"
                  required
                  :disabled="selectedItem"
                >
                  <option value="">Select Type</option>
                  <option 
                    v-for="type in itemTypes" 
                    :key="type.id" 
                    :value="type.id"
                  >
                    {{ type.name }}
                  </option>
                </select>
              </div>
              
              <!-- Dynamic Properties -->
              <template v-if="itemType">
                <div 
                  v-for="prop in getDynamicProperties" 
                  :key="prop.id" 
                  class="mb-3"
                >
                  <label class="form-label">
                    {{ prop.name }}
                    <span v-if="prop.required" class="text-danger">*</span>
                  </label>
                  
                  <!-- Text Input -->
                  <input 
                    v-if="prop.property_type === 'text' && !prop.options" 
                    type="text" 
                    class="form-control"
                    :required="prop.required"
                    :value="getPropertyValue(prop, selectedItem || newItem)"
                    @input="updatePropertyValue(prop.id, $event.target.value)"
                  >
                  
                  <!-- Number Input -->
                  <input 
                    v-else-if="prop.property_type === 'number'" 
                    type="number" 
                    class="form-control"
                    :required="prop.required"
                    :value="getPropertyValue(prop, selectedItem || newItem)"
                    @input="updatePropertyValue(prop.id, parseFloat($event.target.value))"
                  >
                  
                  <!-- Date Input -->
                  <input 
                    v-else-if="prop.property_type === 'date'" 
                    type="date" 
                    class="form-control"
                    :required="prop.required"
                    :value="getPropertyValue(prop, selectedItem || newItem)"
                    @input="updatePropertyValue(prop.id, $event.target.value)"
                  >
                  
                  <!-- Boolean Input -->
                  <div v-else-if="prop.property_type === 'boolean'" class="form-check">
                    <input 
                      type="checkbox" 
                      class="form-check-input"
                      :required="prop.required"
                      :checked="getPropertyValue(prop, selectedItem || newItem)"
                      @change="updatePropertyValue(prop.id, $event.target.checked)"
                    >
                  </div>
                  
                  <!-- Select Input for properties with options -->
                  <select 
                    v-else-if="prop.options" 
                    class="form-select"
                    :required="prop.required"
                    :value="getPropertyValue(prop, selectedItem || newItem)"
                    @change="updatePropertyValue(prop.id, $event.target.value)"
                  >
                    <option value="">Select {{ prop.name }}</option>
                    <option 
                      v-for="option in prop.options" 
                      :key="option" 
                      :value="option"
                    >
                      {{ option }}
                    </option>
                  </select>
                </div>
              </template>
              
              <!-- Files -->
              <div class="mb-3">
                <label class="form-label">Files</label>
                <div class="dropzone-container border rounded p-4 text-center" 
                     @dragover.prevent 
                     @drop.prevent="handleFileDrop">
                  <div class="dropzone-message">
                    <i class="bi bi-cloud-upload fs-2"></i>
                    <p class="mb-2">Drag and drop files here or</p>
                    <input 
                      type="file" 
                      ref="fileInput" 
                      multiple 
                      class="d-none" 
                      @change="handleFileSelect"
                      :accept="allowedExtensions"
                    >
                    <button type="button" class="btn btn-outline-primary" @click="$refs.fileInput.click()">
                      Browse Files
                    </button>
                  </div>
                </div>
                
                <!-- File List -->
                <div v-if="selectedItem?.files?.length > 0 || uploadedFiles.length > 0" class="mt-3">
                  <h6>Attached Files:</h6>
                  <div class="list-group">
                    <!-- Existing Files -->
                    <div v-for="file in selectedItem?.files" :key="file.id" 
                         class="list-group-item d-flex justify-content-between align-items-center">
                      <div>
                        <i class="bi bi-file-earmark me-2"></i>
                        {{ file.original_filename }}
                      </div>
                      <div class="btn-group">
                        <a :href="`${staticUrl}/${file.filename}`" 
                           class="btn btn-sm btn-outline-primary" 
                           target="_blank">
                          <i class="bi bi-download"></i>
                        </a>
                        <button type="button" 
                                class="btn btn-sm btn-outline-danger"
                                @click="deleteFile(file)">
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </div>
                    <!-- Newly Uploaded Files -->
                    <div v-for="file in uploadedFiles" :key="file.name" 
                         class="list-group-item d-flex justify-content-between align-items-center">
                      <div>
                        <i class="bi bi-file-earmark me-2"></i>
                        {{ file.name }}
                        <div class="progress" style="height: 2px;" v-if="file.uploading">
                          <div class="progress-bar" :style="{ width: file.progress + '%' }"></div>
                        </div>
                      </div>
                      <button type="button" 
                              class="btn btn-sm btn-outline-danger"
                              @click="removeUploadedFile(file)">
                        <i class="bi bi-x-lg"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">
                  {{ selectedItem ? 'Update' : 'Create' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { Modal } from 'bootstrap'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const hasPermission = (permission) => auth.hasPermission(permission)

const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5000'
const staticUrl = `${backendUrl}/static`

const items = ref([])
const locations = ref([])
const itemTypes = ref([])
const loading = ref(false)
const viewItemModal = ref(null)
const createItemModal = ref(null)
const selectedItem = ref(null)
const newItem = ref({
  name: '',
  location_id: '',
  item_type_id: '',
  property_values: []
})

const filters = ref({
  search: '',
  location: '',
  type: ''
})

const itemName = computed({
  get: () => selectedItem.value ? selectedItem.value.name : newItem.value.name,
  set: (value) => {
    if (selectedItem.value) {
      selectedItem.value.name = value
    } else {
      newItem.value.name = value
    }
  }
})

const itemLocation = computed({
  get: () => selectedItem.value ? selectedItem.value.location_id : newItem.value.location_id,
  set: (value) => {
    if (selectedItem.value) {
      selectedItem.value.location_id = value
    } else {
      newItem.value.location_id = value
    }
  }
})

const itemType = computed({
  get: () => {
    if (selectedItem.value) {
      return selectedItem.value.item_type_id
    }
    return newItem.value.item_type_id || ''
  },
  set: (value) => {
    if (selectedItem.value) {
      selectedItem.value.item_type_id = value
      // Reset property values when changing item type
      selectedItem.value.property_values = []
    } else {
      newItem.value.item_type_id = value
      newItem.value.property_values = []
    }
  }
})

const fileInput = ref(null)
const previewImage = ref(null)
const selectedFile = ref(null)

const propertyFilters = ref({})

// Add computed for selected type
const selectedType = computed(() => {
  if (!filters.value.type) return null
  return itemTypes.value.find(t => t.id === parseInt(filters.value.type))
})

const uploadedFiles = ref([])
const allowedExtensions = '.png,.jpg,.jpeg,.gif,.pdf,.doc,.docx'

const allowedFile = (file) => {
  const extension = file.name.split('.').pop().toLowerCase()
  const allowed = allowedExtensions.split(',').map(ext => ext.replace('.', ''))
  return allowed.includes(extension)
}

const handleFileDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  handleFiles(files)
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  handleFiles(files)
}

const handleFiles = (files) => {
  files.forEach(file => {
    if (allowedFile(file)) {
      uploadedFiles.value.push({
        file,
        name: file.name,
        uploading: false,
        progress: 0
      })
    } else {
      alert(`File type not allowed: ${file.name}\nAllowed types: ${allowedExtensions}`)
    }
  })
}

const uploadFiles = async (itemId) => {
  const files = uploadedFiles.value
  if (!files.length) return

  const formData = new FormData()
  files.forEach(fileObj => {
    formData.append('files[]', fileObj.file)
    fileObj.uploading = true
  })

  try {
    const response = await axios.post(`/api/items/${itemId}/files`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        files.forEach(file => file.progress = progress)
      }
    })
    uploadedFiles.value = []
    return response.data.files
  } catch (error) {
    console.error('Failed to upload files:', error)
    throw error
  }
}

const deleteFile = async (file) => {
  if (!confirm('Are you sure you want to delete this file?')) return

  try {
    await axios.delete(`/api/items/${selectedItem.value.id}/files/${encodeURIComponent(file.original_filename)}`)
    const index = selectedItem.value.files.findIndex(f => f.original_filename === file.original_filename)
    if (index !== -1) {
      selectedItem.value.files.splice(index, 1)
    }
  } catch (error) {
    console.error('Failed to delete file:', error)
    alert('Failed to delete file. Please try again.')
  }
}

const removeUploadedFile = (file) => {
  const index = uploadedFiles.value.findIndex(f => f === file)
  if (index !== -1) {
    uploadedFiles.value.splice(index, 1)
  }
}

onMounted(async () => {
  viewItemModal.value = new Modal(document.getElementById('viewItemModal'))
  createItemModal.value = new Modal(document.getElementById('createItemModal'))
  await Promise.all([
    fetchItems(),
    fetchLocations(),
    fetchItemTypes()
  ])
})

const fetchItems = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.location) params.location_id = filters.value.location
    if (filters.value.type) params.item_type_id = filters.value.type

    // Add property filters to params
    if (selectedType.value) {
      for (const [propId, value] of Object.entries(propertyFilters.value)) {
        if (value) {
          params[`property_${propId}`] = value
        }
      }
    }

    const response = await axios.get('/api/items', { params })
    items.value = response.data
  } catch (error) {
    console.error('Failed to fetch items:', error)
  } finally {
    loading.value = false
  }
}

const fetchLocations = async () => {
  try {
    const response = await axios.get('/api/locations')
    locations.value = response.data
  } catch (error) {
    console.error('Failed to fetch locations:', error)
  }
}

const fetchItemTypes = async () => {
  try {
    const response = await axios.get('/api/item_types')
    itemTypes.value = response.data
  } catch (error) {
    console.error('Failed to fetch item types:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    location: '',
    type: ''
  }
  propertyFilters.value = {}
}

// Add watchers for filters
watch(filters, () => {
  fetchItems()
}, { deep: true })

const viewItem = async (item) => {
  selectedItem.value = item
  // Fetch files for the item
  try {
    const response = await axios.get(`/api/items/${item.id}/files`)
    selectedItem.value.files = response.data.files
  } catch (error) {
    console.error('Failed to fetch files:', error)
  }
  viewItemModal.value.show()
}

const editItem = (item) => {
  selectedItem.value = { 
    ...item,
    id: item.id,
    item_type_id: item.item_type_id,
    location_id: item.location_id || '',
    property_values: item.property_values.map(pv => ({
      ...pv,
      property_id: pv.property_id,
      value: pv.value
    }))
  }
  // Close view modal if it's open
  if (viewItemModal.value) {
    viewItemModal.value.hide()
  }
  // Show edit modal
  createItemModal.value.show()
}

const confirmDeleteItem = async (item) => {
  if (confirm(`Are you sure you want to delete "${item.name}"?`)) {
    try {
      await axios.delete(`/api/items/${item.id}`)
      const index = items.value.findIndex(i => i.id === item.id)
      if (index !== -1) {
        items.value.splice(index, 1)
      }
    } catch (error) {
      console.error('Failed to delete item:', error)
      alert('Failed to delete item. Please try again.')
    }
  }
}

const showCreateItemModal = () => {
  resetForm()
  createItemModal.value.show()
}

const createItem = async () => {
  try {
    if (!newItem.value.name || !newItem.value.item_type_id) {
      alert('Name and Item Type are required')
      return
    }

    // Validate required properties
    const selectedType = itemTypes.value.find(t => t.id === parseInt(newItem.value.item_type_id))
    const requiredProps = selectedType.properties.filter(p => p.required)
    const missingProps = requiredProps.filter(p => {
      const value = newItem.value.property_values.find(v => v.property_id === p.id)?.value
      return !value && value !== false && value !== 0
    })

    if (missingProps.length > 0) {
      alert(`Please fill in the following required properties: ${missingProps.map(p => p.name).join(', ')}`)
      return
    }

    const response = await axios.post('/api/items', newItem.value)
    const createdItem = response.data

    // Upload files if any
    if (uploadedFiles.value.length > 0) {
      const uploadedFileData = await uploadFiles(createdItem.id)
      createdItem.files = uploadedFileData
    }

    items.value.push(createdItem)
    createItemModal.value.hide()
    resetForm()
  } catch (error) {
    console.error('Failed to create item:', error)
    alert('Failed to create item. Please try again.')
  }
}

const updateItem = async () => {
  try {
    const itemId = selectedItem.value.id
    const formData = new FormData()
    
    // Add basic fields
    formData.append('name', itemName.value)
    formData.append('location_id', itemLocation.value || '')
    
    // Add property values as JSON string
    formData.append('property_values', JSON.stringify(selectedItem.value.property_values.map(pv => ({
      property_id: pv.property_id,
      value: pv.value
    }))))
    
    // Add image if selected
    if (selectedFile.value) {
      formData.append('image', selectedFile.value)
    }
    
    const response = await axios.put(`/api/items/${itemId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    const updatedItem = response.data

    // Upload new files if any
    if (uploadedFiles.value.length > 0) {
      const uploadedFileData = await uploadFiles(itemId)
      updatedItem.files = [...(updatedItem.files || []), ...uploadedFileData]
    }

    const index = items.value.findIndex(item => item.id === itemId)
    if (index !== -1) {
      items.value[index] = updatedItem
    }

    createItemModal.value.hide()
  } catch (error) {
    console.error('Failed to update item:', error)
    alert('Failed to update item. Please try again.')
  }
}

const updatePropertyValue = (propertyId, value) => {
  // Find the property definition to check its type
  const property = itemTypes.value
    .find(t => t.id === (selectedItem.value ? selectedItem.value.item_type_id : itemType.value))
    ?.properties.find(p => p.id === propertyId)

  // Format the value based on property type
  let formattedValue = value
  if (property && property.property_type === 'date' && value) {
    try {
      // Handle different date formats
      let date;
      if (value instanceof Date) {
        date = value;
      } else if (typeof value === 'string') {
        if (value.includes('GMT')) {
          // Handle GMT date string
          date = new Date(value);
        } else {
          // Handle YYYY-MM-DD format
          date = new Date(value + 'T00:00:00');
        }
      }
      if (!isNaN(date)) {
        formattedValue = date.toISOString().split('T')[0];
      }
    } catch (e) {
      console.error('Error formatting date:', e);
      formattedValue = value;
    }
  }

  if (selectedItem.value) {
    const existingValue = selectedItem.value.property_values.find(v => v.property_id === propertyId)
    if (existingValue) {
      existingValue.value = formattedValue
    } else {
      selectedItem.value.property_values.push({
        property_id: propertyId,
        value: formattedValue
      })
    }
  } else {
    const existingValue = newItem.value.property_values.find(v => v.property_id === propertyId)
    if (existingValue) {
      existingValue.value = formattedValue
    } else {
      newItem.value.property_values.push({
        property_id: propertyId,
        value: formattedValue
      })
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date)) return dateString;
  return date.toLocaleDateString('de-DE');
}

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removeImage = () => {
  previewImage.value = null
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const resetForm = () => {
  selectedItem.value = null
  newItem.value = {
    name: '',
    location_id: '',
    item_type_id: '',
    property_values: []
  }
  uploadedFiles.value = []
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Update the date input value binding
const getPropertyValue = (prop, item) => {
  const value = item.property_values.find(v => v.property_id === prop.id)?.value
  if (prop.property_type === 'date' && value) {
    try {
      const date = new Date(value)
      if (!isNaN(date)) {
        return date.toISOString().split('T')[0]
      }
    } catch (e) {
      console.error('Error formatting date for input:', e)
    }
  }
  return value
}

// Update the template section for dynamic properties
const getDynamicProperties = computed(() => {
  const typeId = selectedItem.value ? selectedItem.value.item_type_id : itemType.value
  return itemTypes.value.find(t => t.id === typeId)?.properties || []
})

// Watch property filters
watch(propertyFilters, () => {
  fetchItems()
}, { deep: true })

// Watch type filter to reset property filters when type changes
watch(() => filters.value.type, () => {
  propertyFilters.value = {}
})

const getFileIcon = (mimeType) => {
  if (!mimeType) return 'bi-file'
  if (mimeType.startsWith('image/')) return 'bi-file-image'
  if (mimeType.startsWith('video/')) return 'bi-file-play'
  if (mimeType.startsWith('audio/')) return 'bi-file-music'
  if (mimeType.includes('pdf')) return 'bi-file-pdf'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'bi-file-word'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'bi-file-excel'
  return 'bi-file'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style lang="scss" scoped>
.items-container {
  max-width: 1400px;
  margin: 0 auto;
}

.dropzone-container {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border: 2px dashed #dee2e6 !important;
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    border-color: #0d6efd !important;
    background-color: #f1f4f9;
  }

  .dropzone-message {
    text-align: center;
    color: #6c757d;

    i {
      font-size: 2.5rem;
      margin-bottom: 1rem;
      color: #0d6efd;
    }
  }
}

.progress {
  margin-top: 0.5rem;
  background-color: #e9ecef;
  
  .progress-bar {
    background-color: #0d6efd;
    transition: width 0.3s ease;
  }
}

.item-image {
  height: 200px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.card {
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-5px);
  }
}

.item-image-preview {
  width: 200px;
  height: 150px;
  overflow: hidden;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}
</style> 