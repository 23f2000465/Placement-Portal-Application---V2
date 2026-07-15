<template>
  <nav class="navbar navbar-dark bg-dark">
    <div class="container">
      <RouterLink class="navbar-brand" to="/">Placement Portal</RouterLink>
      <button v-if="user" class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
    </div>
  </nav>
  <main class="container py-4"><RouterView /></main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from './api'

const router = useRouter()
const user = ref(localStorage.getItem('user'))
router.afterEach(() => { user.value = localStorage.getItem('user') })
async function logout() {
  await api.post('/auth/logout')
  localStorage.removeItem('user')
  user.value = null
  router.push('/')
}
</script>
