<template>
  <div class="app-container" :class="{ 'dark-theme': isDarkTheme }">
    <nav v-if="isAuthenticated" class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/">
          <div class="brand-container">
            <AppLogo />
            <span class="brand-text">
              <span class="letter">S</span><span class="letter-text">ystem für</span>
              <span class="letter">T</span><span class="letter-text">heater-</span>
              <span class="letter">U</span><span class="letter-text">tensilien, </span>
              <span class="letter">F</span><span class="letter-text">undus und</span>
              <span class="letter">F</span><span class="letter-text">ummel</span>
            </span>
          </div>
        </router-link>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/items">
                <i class="bi bi-box"></i> Items
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/locations">
                <i class="bi bi-geo-alt"></i> Locations
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/tags">
                <i class="bi bi-tags"></i> Tags
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/item-types">
                <i class="bi bi-box"></i> Item Types
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/scanner">
                <i class="bi bi-qr-code-scan"></i> Scanner
              </router-link>
            </li>
            <li v-if="hasPermission('manage_users')" class="nav-item">
              <router-link class="nav-link" to="/users">
                <i class="bi bi-people"></i> Users
              </router-link>
            </li>
          </ul>

          <div class="navbar-nav">
            <div class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" id="userDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="bi bi-person-circle"></i>
                {{ user?.username }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li>
                  <router-link class="dropdown-item" to="/profile">
                    <i class="bi bi-person"></i> Profile
                  </router-link>
                </li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="toggleTheme">
                    <i class="bi" :class="isDarkTheme ? 'bi-sun' : 'bi-moon'"></i>
                    {{ isDarkTheme ? 'Light Theme' : 'Dark Theme' }}
                  </a>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="logout">
                    <i class="bi bi-box-arrow-right"></i> Logout
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="container-fluid py-4">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import * as bootstrap from 'bootstrap'
import AppLogo from '@/components/AppLogo.vue'

const authStore = useAuthStore()
const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
const isDarkTheme = ref(localStorage.getItem('theme') === 'dark')

const hasPermission = (permission) => {
  return authStore.hasPermission(permission)
}

const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value
  localStorage.setItem('theme', isDarkTheme.value ? 'dark' : 'light')
  document.documentElement.setAttribute('data-bs-theme', isDarkTheme.value ? 'dark' : 'light')
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  // Initialize theme from localStorage
  if (isDarkTheme.value) {
    document.documentElement.setAttribute('data-bs-theme', 'dark')
  }

  // Initialize the dropdown manually
  const dropdownElement = document.querySelector('[data-bs-toggle="dropdown"]')
  if (dropdownElement) {
    new bootstrap.Dropdown(dropdownElement)
  }
})
</script>

<style lang="scss">
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;

  &.dark-theme {
    background-color: #212529;
    color: #f8f9fa;
  }
}

main {
  flex: 1;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 1rem;

  .brand-logo {
    height: 40px;
    width: auto;
    transition: transform 0.3s ease;
  }

  &:hover .brand-logo {
    transform: scale(1.1);
  }

  .brand-container {
    position: relative;
    display: inline-flex;
    align-items: center;

    .brand-text {
      display: inline-block;
      overflow: hidden;
      white-space: nowrap;
    }
  }

  .brand-text .letter {
    display: inline;
    overflow: hidden;
    display: inline-block;
  }

  .brand-text .letter-text {
    max-width: 0;
    transition: max-width 1s ease;
    overflow: hidden;
    display: inline;
    display: inline-block;
  }
  
  &:hover {
    .brand-text .letter-text {
      max-width: 100%;
    }

    .brand-text .letter {
      max-width: 100%;
      font-weight: bold;
      margin-left: 10px;
    }
  }
}

.navbar {
  .navbar-collapse {
    transition: padding-left 0.3s ease;
  }
}
</style>