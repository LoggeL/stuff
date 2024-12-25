<template>
  <div class="scanner-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>QR Scanner</h1>
    </div>

    <div class="row">
      <div class="col-md-8 mx-auto">
        <div class="card">
          <div class="card-body">
            <!-- QR Scanner -->
            <div id="reader" class="mb-4"></div>

            <!-- Result -->
            <div id="result" class="mt-3">
              <div v-if="scannedItem" class="alert alert-success">
                <h4>Item Found!</h4>
                <div class="d-flex align-items-center mt-3">
                  <img 
                    :src="scannedItem.properties.Bild ? `/static/${scannedItem.properties.Bild}` : '/placeholder.png'"
                    :alt="scannedItem.name"
                    class="me-3"
                    style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;"
                  >
                  <div>
                    <h5>{{ scannedItem.name }}</h5>
                    <p class="mb-1">{{ scannedItem.type.name }}</p>
                    <p v-if="scannedItem.location" class="mb-0">
                      <i class="bi bi-geo-alt"></i>
                      {{ scannedItem.location.name }}
                    </p>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link 
                    :to="`/items/${scannedItem.id}`"
                    class="btn btn-primary"
                  >
                    <i class="bi bi-box-arrow-in-right"></i>
                    View Details
                  </router-link>
                </div>
              </div>

              <div v-if="scannedLocation" class="alert alert-success">
                <h4>Location Found!</h4>
                <div class="d-flex align-items-center mt-3">
                  <div>
                    <h5>{{ scannedLocation.name }}</h5>
                    <p class="mb-0">
                      {{ scannedLocation.items?.length || 0 }} Items
                    </p>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link 
                    :to="`/locations/${scannedLocation.id}/items`"
                    class="btn btn-primary"
                  >
                    <i class="bi bi-box-arrow-in-right"></i>
                    View Items
                  </router-link>
                </div>
              </div>

              <div v-if="error" class="alert alert-danger">
                {{ error }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Html5QrcodeScanner } from 'html5-qrcode'
import axios from 'axios'

const scannedItem = ref(null)
const scannedLocation = ref(null)
const error = ref(null)
let scanner = null

onMounted(() => {
  scanner = new Html5QrcodeScanner('reader', {
    fps: 10,
    qrbox: 250,
    aspectRatio: 1.0
  })

  scanner.render(onScanSuccess, onScanError)
})

onBeforeUnmount(() => {
  if (scanner) {
    scanner.clear()
  }
})

const onScanSuccess = async (decodedText) => {
  try {
    // Reset previous results
    scannedItem.value = null
    scannedLocation.value = null
    error.value = null

    // Parse QR code content
    const [type, id] = decodedText.split(':')

    if (type === 'item') {
      const response = await axios.get(`/api/items/${id}`)
      scannedItem.value = response.data
      playBeep()
    } else if (type === 'location') {
      const response = await axios.get(`/api/locations/${id}`)
      scannedLocation.value = response.data
      playBeep()
    } else {
      error.value = 'Invalid QR code format'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load scanned item/location'
  }
}

const onScanError = (err) => {
  // Ignore errors during scanning
  console.debug('QR Scan Error:', err)
}

const playBeep = () => {
  const audio = new Audio('/static/sounds/beep.mp3')
  audio.play().catch(e => console.log('Audio playback failed:', e))
}
</script>

<style lang="scss" scoped>
.scanner-container {
  max-width: 1200px;
  margin: 0 auto;
}

#reader {
  width: 100%;
  
  video {
    border-radius: 8px;
  }
}

::v-deep(#reader__scan_region) {
  background: white;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

::v-deep(#reader__dashboard) {
  padding: 1rem;
  margin-top: 1rem;
  border-radius: 8px;
  background: #f8f9fa;
}
</style> 