<template>
  <div class="card mx-auto" style="max-width: 650px"><div class="card-body">
    <h2>{{ title }} Registration</h2>
    <div v-if="message" class="alert" :class="success ? 'alert-success' : 'alert-danger'">{{ message }}</div>
    <form @submit.prevent="register">
      <div class="row">
        <div class="col-md-6"><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-control mb-2" required></div>
        <div class="col-md-6"><label class="form-label">Password</label><input v-model="form.password" type="password" minlength="6" class="form-control mb-2" required></div>
        <template v-if="role === 'student'">
          <div class="col-md-6" v-for="field in studentFields" :key="field.key"><label class="form-label">{{ field.label }}</label><input v-model="form[field.key]" :type="field.type || 'text'" :step="field.type==='number'?'any':undefined" class="form-control mb-2" required></div>
        </template>
        <template v-else>
          <div class="col-md-6" v-for="field in companyFields" :key="field.key"><label class="form-label">{{ field.label }}</label><input v-model="form[field.key]" class="form-control mb-2" :required="field.key !== 'website'"></div>
        </template>
      </div>
      <button class="btn btn-primary mt-3">Register</button>
    </form>
  </div></div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import api from '../api'
const props = defineProps({ role: String })
const form = reactive({})
const message = ref('')
const success = ref(false)
const title = computed(() => props.role === 'student' ? 'Student' : 'Company')
const studentFields = [{key:'full_name',label:'Full Name'},{key:'student_code',label:'Student ID'},{key:'contact',label:'Contact'},{key:'branch',label:'Branch'},{key:'cgpa',label:'CGPA',type:'number'},{key:'graduation_year',label:'Graduation Year',type:'number'}]
const companyFields = [{key:'name',label:'Company Name'},{key:'industry',label:'Industry'},{key:'location',label:'Location'},{key:'hr_contact',label:'HR Contact'},{key:'website',label:'Website (optional)'}]
watch(() => props.role, () => { Object.keys(form).forEach(key => delete form[key]); message.value = '' }, { immediate: true })
async function register() {
  try { const { data } = await api.post(`/auth/register/${props.role}`, form); message.value = data.message; success.value = true }
  catch (error) { message.value = error.response?.data?.message || 'Registration failed'; success.value = false }
}
</script>
