<template>
  <div class="login-container">
    <div class="login-card">
      <h2>甲状腺结节辅助诊断系统</h2>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width:100%" @click="handleLogin" :loading="loading">登 录</el-button>
        </el-form-item>
        <div class="link-row">
          <router-link to="/register">没有账号？去注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import api from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await api.post('/auth/login', form.value)
    if (res.code === 200) {
      userStore.setUser(res.data.user, res.data.token)
      ElMessage.success('登录成功')
      router.push(`/${res.data.user.role}`)
    } else {
      ElMessage.error(res.msg || '登录失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '登录失败')
  }
  loading.value = false
}
</script>

<style scoped>
.login-container { display:flex; justify-content:center; align-items:center; min-height:100vh; background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); }
.login-card { background:#fff; padding:40px; border-radius:12px; width:380px; box-shadow:0 20px 60px rgba(0,0,0,0.3); }
.login-card h2 { text-align:center; margin-bottom:30px; color:#333; }
.link-row { text-align:center; }
.link-row a { color:#667eea; text-decoration:none; }
</style>
