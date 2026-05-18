<template>
  <div class="login-container">
    <div class="login-card">
      <h2>用户注册</h2>
      <el-form :model="form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.real_name" placeholder="真实姓名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="form.role" placeholder="选择角色" size="large" style="width:100%">
            <el-option label="患者" value="patient" />
            <el-option label="医生" value="doctor" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.phone" placeholder="手机号（选填）" size="large" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width:100%" @click="handleRegister" :loading="loading">注 册</el-button>
        </el-form-item>
        <div class="link-row">
          <router-link to="/login">已有账号？去登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const form = ref({ username: '', password: '', real_name: '', role: 'patient', phone: '' })

async function handleRegister() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await api.post('/auth/register', form.value)
    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } else {
      ElMessage.error(res.msg || '注册失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '注册失败')
  }
  loading.value = false
}
</script>

<style scoped>
.login-container { display:flex; justify-content:center; align-items:center; min-height:100vh; background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); }
.login-card { background:#fff; padding:40px; border-radius:12px; width:400px; box-shadow:0 20px 60px rgba(0,0,0,0.3); }
.login-card h2 { text-align:center; margin-bottom:30px; color:#333; }
.link-row { text-align:center; }
.link-row a { color:#667eea; text-decoration:none; }
</style>
