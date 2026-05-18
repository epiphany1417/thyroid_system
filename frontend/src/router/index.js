import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
  {
    path: '/doctor',
    component: () => import('../views/Layout.vue'),
    meta: { role: 'doctor' },
    children: [
      { path: '', name: 'DoctorHome', component: () => import('../views/doctor/Dashboard.vue') },
      { path: 'pending', name: 'DoctorPending', component: () => import('../views/doctor/Pending.vue') },
      { path: 'upload', name: 'DoctorUpload', component: () => import('../views/doctor/Upload.vue') },
      { path: 'history', name: 'DoctorHistory', component: () => import('../views/doctor/History.vue') },
      { path: 'diagnosis/:id', name: 'DoctorDiagnosis', component: () => import('../views/doctor/DiagnosisDetail.vue') }
    ]
  },
  {
    path: '/patient',
    component: () => import('../views/Layout.vue'),
    meta: { role: 'patient' },
    children: [
      { path: '', name: 'PatientHome', component: () => import('../views/patient/Dashboard.vue') },
      { path: 'records', name: 'PatientRecords', component: () => import('../views/patient/Records.vue') },
      { path: 'upload', name: 'PatientUpload', component: () => import('../views/patient/Upload.vue') }
    ]
  },
  {
    path: '/admin',
    component: () => import('../views/Layout.vue'),
    meta: { role: 'admin' },
    children: [
      { path: '', name: 'AdminHome', component: () => import('../views/admin/Dashboard.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('../views/admin/Users.vue') },
      { path: 'data', name: 'AdminData', component: () => import('../views/admin/Data.vue') },
      { path: 'logs', name: 'AdminLogs', component: () => import('../views/admin/Logs.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  
  if (to.path === '/login' || to.path === '/register') {
    next()
    return
  }
  
  if (!token) {
    next('/login')
    return
  }
  
  if (to.meta.role && user && user.role !== to.meta.role) {
    next(`/${user.role}`)
    return
  }
  
  next()
})

export default router
