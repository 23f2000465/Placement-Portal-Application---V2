<template>
  <div class="card mx-auto" style="max-width: 430px">
    <div class="card-body">
      <h2>Login</h2>
      <div v-if="message" class="alert alert-danger">{{ message }}</div>
      <form @submit.prevent="login">
        <label class="form-label">Email</label><input v-model="form.email" class="form-control mb-3" type="email" required>
        <label class="form-label">Password</label><input v-model="form.password" class="form-control mb-3" type="password" required>
        <button class="btn btn-primary">Login</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
const router = useRouter()
const form = reactive({ email: '', password: '' })
const message = ref('')
async function login() {
  try {
    const { data } = await api.post('/auth/login', form)
    localStorage.setItem('user', JSON.stringify(data.user))
    router.push('/dashboard')
  } catch (error) { message.value = error.response?.data?.message || 'Login failed' }
}
</script>
