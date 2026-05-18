<template>
  <el-container style="height:100vh">
    <el-aside width="220px" style="background:#304156">
      <div class="logo">甲状腺诊断系统</div>
      <el-menu :default-active="route.path" :router="true" background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <template v-if="user?.role === 'doctor'">
          <el-menu-item index="/doctor"><el-icon><House /></el-icon><span>工作台</span></el-menu-item>
          <el-menu-item index="/doctor/pending"><el-icon><Bell /></el-icon><span>待诊断</span></el-menu-item>
          <el-menu-item index="/doctor/upload"><el-icon><Upload /></el-icon><span>主动诊断</span></el-menu-item>
          <el-menu-item index="/doctor/history"><el-icon><Document /></el-icon><span>历史记录</span></el-menu-item>
        </template>
        <template v-if="user?.role === 'patient'">
          <el-menu-item index="/patient"><el-icon><House /></el-icon><span>我的主页</span></el-menu-item>
          <el-menu-item index="/patient/upload"><el-icon><Upload /></el-icon><span>上传检查</span></el-menu-item>
          <el-menu-item index="/patient/records"><el-icon><Document /></el-icon><span>诊断记录</span></el-menu-item>
        </template>
        <template v-if="user?.role === 'admin'">
          <el-menu-item index="/admin"><el-icon><House /></el-icon><span>系统概览</span></el-menu-item>
          <el-menu-item index="/admin/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
          <el-menu-item index="/admin/data"><el-icon><Folder /></el-icon><span>数据管理</span></el-menu-item>
          <el-menu-item index="/admin/logs"><el-icon><Notebook /></el-icon><span>操作日志</span></el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;align-items:center;justify-content:flex-end;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,0.1)">
        <span style="margin-right:16px">{{ user?.real_name || user?.username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
      </el-header>
      <el-main style="background:#f0f2f5;padding:20px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { House, Upload, Document, User, Folder, Notebook, Bell } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const user = userStore.user

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.logo { color:#fff; text-align:center; padding:20px 0; font-size:16px; font-weight:bold; border-bottom:1px solid #3a4a5b; }
</style>
