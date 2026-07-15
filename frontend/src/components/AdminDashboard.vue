<template>
  <h2>Admin Dashboard</h2>
  <div v-if="message" class="alert alert-info">{{ message }}</div>
  <div class="row g-3 mb-4">
    <div v-for="(value, label) in stats" :key="label" class="col-6 col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ value }}</h3><span class="text-capitalize">{{ label }}</span></div></div></div>
  </div>
  <ul class="nav nav-tabs mb-3">
    <li v-for="name in ['companies','students','drives','applications']" :key="name" class="nav-item"><button class="nav-link text-capitalize" :class="{active: tab===name}" @click="tab=name">{{ name }}</button></li>
  </ul>

  <div v-if="tab==='companies'">
    <input v-model="search" @input="loadCompanies" class="form-control mb-2" placeholder="Search name or industry">
    <div class="table-responsive"><table class="table table-bordered"><thead><tr><th>Name</th><th>Industry</th><th>Status</th><th>Actions</th></tr></thead><tbody><tr v-for="c in companies" :key="c.id"><td>{{c.name}}</td><td>{{c.industry}}</td><td>{{c.status}}</td><td><button class="btn btn-success btn-sm me-1" @click="companyStatus(c.id,'Approved')">Approve</button><button class="btn btn-danger btn-sm me-1" @click="companyStatus(c.id,'Rejected')">Reject</button><button class="btn btn-outline-dark btn-sm" @click="active(c.user_id,!c.active)">{{c.active?'Deactivate':'Activate'}}</button></td></tr></tbody></table></div>
  </div>
  <div v-if="tab==='students'">
    <input v-model="search" @input="loadStudents" class="form-control mb-2" placeholder="Search name, ID or contact">
    <div class="table-responsive"><table class="table table-bordered"><thead><tr><th>Name</th><th>ID</th><th>Branch</th><th>Action</th></tr></thead><tbody><tr v-for="s in students" :key="s.id"><td>{{s.name}}</td><td>{{s.student_code}}</td><td>{{s.branch}}</td><td><button class="btn btn-outline-dark btn-sm" @click="active(s.user_id,!s.active)">{{s.active?'Deactivate':'Activate'}}</button></td></tr></tbody></table></div>
  </div>
  <div v-if="tab==='drives'" class="table-responsive"><table class="table table-bordered"><thead><tr><th>Company</th><th>Title</th><th>Status</th><th>Actions</th></tr></thead><tbody><tr v-for="d in drives" :key="d.id"><td>{{d.company}}</td><td>{{d.title}}</td><td>{{d.status}}</td><td><button class="btn btn-success btn-sm me-1" @click="driveStatus(d.id,'Approved')">Approve</button><button class="btn btn-danger btn-sm" @click="driveStatus(d.id,'Rejected')">Reject</button></td></tr></tbody></table></div>
  <div v-if="tab==='applications'" class="table-responsive"><table class="table table-bordered"><thead><tr><th>Student</th><th>Company</th><th>Drive</th><th>Status</th></tr></thead><tbody><tr v-for="a in applications" :key="a.id"><td>{{a.student}}</td><td>{{a.company}}</td><td>{{a.drive}}</td><td>{{a.status}}</td></tr></tbody></table></div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'
const stats=ref({}); const companies=ref([]); const students=ref([]); const drives=ref([]); const applications=ref([]); const tab=ref('companies'); const search=ref(''); const message=ref('')
async function load(){ stats.value=(await api.get('/admin/dashboard')).data; await Promise.all([loadCompanies(),loadStudents(),loadDrives(),loadApplications()]) }
async function loadCompanies(){ companies.value=(await api.get('/admin/companies',{params:{q:search.value}})).data.companies }
async function loadStudents(){ students.value=(await api.get('/admin/students',{params:{q:search.value}})).data.students }
async function loadDrives(){ drives.value=(await api.get('/admin/drives')).data.drives }
async function loadApplications(){ applications.value=(await api.get('/admin/applications')).data.applications }
async function companyStatus(id,status){ message.value=(await api.patch(`/admin/companies/${id}/status`,{status})).data.message; await loadCompanies() }
async function driveStatus(id,status){ message.value=(await api.patch(`/admin/drives/${id}/status`,{status})).data.message; await loadDrives() }
async function active(id,value){ message.value=(await api.patch(`/admin/users/${id}/active`,{active:value})).data.message; await load() }
onMounted(load)
</script>
