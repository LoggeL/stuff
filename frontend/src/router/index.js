import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy-loaded components
const Login = () => import('@/views/Login.vue')
const Items = () => import('@/views/Items.vue')
const Locations = () => import('@/views/Locations.vue')
const Tags = () => import('@/views/Tags.vue')
const ItemTypes = () => import('@/views/ItemTypes.vue')
const Scanner = () => import('@/views/Scanner.vue')
const Users = () => import('@/views/Users.vue')
const Profile = () => import('@/views/Profile.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/items'
  },
  {
    path: '/items',
    name: 'Items',
    component: Items,
    meta: { requiresAuth: true, permission: 'view_items' }
  },
  {
    path: '/locations',
    name: 'Locations',
    component: Locations,
    meta: { requiresAuth: true, permission: 'view_locations' }
  },
  {
    path: '/tags',
    name: 'Tags',
    component: Tags,
    meta: { requiresAuth: true, permission: 'view_tags' }
  },
  {
    path: '/item-types',
    name: 'ItemTypes',
    component: ItemTypes,
    meta: { requiresAuth: true, permission: 'view_items' }
  },
  {
    path: '/scanner',
    name: 'Scanner',
    component: Scanner,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: Users,
    meta: { requiresAuth: true, permission: 'manage_users' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiredPermission = to.meta.permission

  if (!requiresAuth) {
    // Route doesn't require auth
    if (authStore.isAuthenticated && to.path === '/login') {
      // Redirect authenticated users away from login
      next({ path: '/' })
    } else {
      next()
    }
    return
  }

  if (!authStore.isAuthenticated) {
    // Route requires auth but user isn't authenticated
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (!authStore.user) {
    try {
      // Fetch user data if not available
      await authStore.fetchUser()
    } catch (error) {
      next({ path: '/login' })
      return
    }
  }

  if (requiredPermission && !authStore.hasPermission(requiredPermission)) {
    // User doesn't have required permission
    next({ path: '/' })
    return
  }

  next()
})

export default router 