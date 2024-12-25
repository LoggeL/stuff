<template>
  <div class="tags-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Tags</h1>
      <button 
        v-if="hasPermission('add_tags')" 
        class="btn btn-primary"
        @click="showCreateTagModal"
      >
        <i class="bi bi-plus-lg"></i> Add Tag
      </button>
    </div>

    <!-- Tags Grid -->
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="tag in tags" :key="tag.id" class="col">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <h5 class="card-title">
                <span 
                  class="badge me-2"
                  :class="`bg-${tag.color}`"
                >
                  {{ tag.name }}
                </span>
              </h5>
              <div class="badge bg-secondary">
                {{ tag.items?.length || 0 }} Items
              </div>
            </div>
            <div class="mt-3">
              <router-link 
                :to="`/items?tag=${tag.name}`"
                class="btn btn-outline-primary me-2"
              >
                <i class="bi bi-box"></i> View Items
              </router-link>
              <button 
                v-if="hasPermission('edit_tags')"
                class="btn btn-outline-secondary me-2"
                @click="editTag(tag)"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button 
                v-if="hasPermission('delete_tags')"
                class="btn btn-outline-danger"
                @click="confirmDeleteTag(tag)"
                :disabled="tag.items?.length > 0"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
          <div class="card-footer bg-transparent">
            <small class="text-muted">
              <i class="bi bi-clock"></i>
              Created {{ new Date(tag.created_at).toLocaleDateString() }}
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
    <div v-if="!loading && tags.length === 0" class="text-center py-5">
      <i class="bi bi-tags display-1 text-muted"></i>
      <p class="lead mt-3">No tags found</p>
      <button 
        v-if="hasPermission('add_tags')"
        class="btn btn-primary mt-2"
        @click="showCreateTagModal"
      >
        Create your first tag
      </button>
    </div>

    <!-- Tag Modal -->
    <div class="modal fade" id="tagModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingTag ? 'Edit Tag' : 'Create Tag' }}
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
              <div class="mb-3">
                <label class="form-label">Color</label>
                <div class="d-flex flex-wrap gap-2">
                  <button
                    v-for="color in availableColors"
                    :key="color"
                    type="button"
                    class="btn color-swatch"
                    :class="[
                      `btn-${color}`,
                      form.color === color ? 'active' : ''
                    ]"
                    @click="form.color = color"
                  >
                    <i v-if="form.color === color" class="bi bi-check"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingTag ? 'Update' : 'Create' }}
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
            <h5 class="modal-title">Delete Tag</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete tag "{{ tagToDelete?.name }}"?
            This action cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger"
              @click="deleteTag"
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

const tags = ref([])
const loading = ref(false)
const editingTag = ref(null)
const tagToDelete = ref(null)
const tagModal = ref(null)
const deleteModal = ref(null)

const form = ref({
  name: '',
  color: 'primary'
})

const availableColors = [
  'primary',
  'secondary',
  'success',
  'danger',
  'warning',
  'info',
  'dark'
]

onMounted(async () => {
  tagModal.value = new Modal(document.getElementById('tagModal'))
  deleteModal.value = new Modal(document.getElementById('deleteModal'))
  await fetchTags()
})

const fetchTags = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/tags')
    tags.value = response.data
  } catch (error) {
    console.error('Failed to fetch tags:', error)
  } finally {
    loading.value = false
  }
}

const showCreateTagModal = () => {
  editingTag.value = null
  form.value = { name: '', color: 'primary' }
  tagModal.value.show()
}

const editTag = (tag) => {
  editingTag.value = tag
  form.value = { 
    name: tag.name,
    color: tag.color || 'primary'
  }
  tagModal.value.show()
}

const handleSubmit = async () => {
  loading.value = true
  try {
    if (editingTag.value) {
      await axios.put(`/api/tags/${editingTag.value.id}`, form.value)
    } else {
      await axios.post('/api/tags', form.value)
    }
    await fetchTags()
    tagModal.value.hide()
  } catch (error) {
    console.error('Failed to save tag:', error)
  } finally {
    loading.value = false
  }
}

const confirmDeleteTag = (tag) => {
  tagToDelete.value = tag
  deleteModal.value.show()
}

const deleteTag = async () => {
  if (!tagToDelete.value) return

  loading.value = true
  try {
    await axios.delete(`/api/tags/${tagToDelete.value.id}`)
    await fetchTags()
    deleteModal.value.hide()
  } catch (error) {
    console.error('Failed to delete tag:', error)
  } finally {
    loading.value = false
    tagToDelete.value = null
  }
}
</script>

<style lang="scss" scoped>
.tags-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-5px);
  }
}

.color-swatch {
  width: 40px;
  height: 40px;
  padding: 0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border: 2px solid transparent;

  &.active {
    border-color: rgba(0, 0, 0, 0.2);
  }

  &:hover {
    opacity: 0.9;
  }
}
</style> 