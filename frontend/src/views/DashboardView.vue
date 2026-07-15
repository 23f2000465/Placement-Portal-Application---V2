<template>
  <h2>{{ user.role }} Dashboard</h2>
  <div class="alert alert-info">Welcome {{ user.email }}. Dashboard features are added milestone by milestone.</div>
</template>
<script setup>
const user = JSON.parse(localStorage.getItem('user') || '{}')
</script>
