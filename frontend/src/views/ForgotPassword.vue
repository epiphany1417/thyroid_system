<template>
  <div class="login-container">
    <div class="login-card">
      <h2 style="text-align:center;margin-bottom:24px;color:#303133">重置密码</h2>
      <el-form :model="form" @submit.prevent>
        <el-form-item>
          <el-input v-model="form.contact" placeholder="请输入注册手机号或邮箱" size="large" :prefix-icon="Phone" />
        </el-form-item>

        <el-form-item>
          <el-input v-model="form.code" placeholder="请输入6位验证码" size="large" :prefix-icon="Key" style="width:60%">
            <template #append>
              <el-button :disabled="countdown > 0" @click="sendCode" :loading="sending">
                {{ countdown > 0 ? countdown + 's后重发' : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-input v-model="form.new_password" type="password" placeholder="请输入新密码（至少6位）" size="large" :prefix-icon="Lock" show-password />
        </el-form-item>

        <el-form-item>
          <el-input v-model="form.confirm_password" type="password" placeholder="请确认新密码" size="large" :prefix-icon="Lock" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" style="width:100%" @click="handleReset" :loading="loading">重置密码</el-button>
        </el-form-item>
      </el-form>
      <div style="text-align:center">
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Phone, Key, Lock } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const sending = ref(false)
const countdown = ref(0)
const form = reactive({
  contact: '',
  code: '',
  new_password: '',
  confirm_password: ''
})

async function sendCode() {
  if (!form.contact.trim()) {
    ElMessage.warning('请输入手机号或邮箱')
    return
  }
  sending.value = true
  try {
    const res = await api.post('/auth/send-code', { contact: form.contact.trim() })
    if (res.code === 200) {
      ElMessage.success(res.data?.code ? `验证码: ${res.data.code}` : '验证码已发送')
      // 60秒倒计时
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) clearInterval(timer)
      }, 1000)
    } else {
      ElMessage.error(res.msg || '发送失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '发送失败')
  } finally {
    sending.value = false
  }
}

async function handleReset() {
  if (!form.contact.trim() || !form.code.trim() || !form.new_password || !form.confirm_password) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (form.new_password.length < 6) {
    ElMessage.warning('密码长度不能少于6位')
    return
  }
  if (form.new_password !== form.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    const res = await api.post('/auth/reset-password', {
      contact: form.contact.trim(),
      code: form.code.trim(),
      new_password: form.new_password
    })
    if (res.code === 200) {
      ElMessage.success('密码重置成功，请登录')
      router.push('/login')
    } else {
      ElMessage.error(res.msg || '重置失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '重置失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  background: #fff;
  padding: 40px;
  border-radius: 12px;
  width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}
</style>
