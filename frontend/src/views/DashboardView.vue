<template>
  <AdminDashboard v-if="user.role === 'Admin'" />
  <div v-else>
    <h2>{{ user.role }} Dashboard</h2>
    <div class="alert alert-info">Welcome {{ user.email }}. Dashboard features are added milestone by milestone.</div>
  </div>
</template>
<script setup>
import AdminDashboard from '../components/AdminDashboard.vue'
const user = JSON.parse(localStorage.getItem('user') || '{}')
</script>
