<template>
  <el-card header="用户管理">
    <div style="margin-bottom:16px;display:flex;gap:10px">
      <el-select v-model="filterRole" placeholder="筛选角色" clearable @change="fetchData" style="width:120px">
        <el-option label="医生" value="doctor" /><el-option label="患者" value="patient" /><el-option label="管理员" value="admin" />
      </el-select>
      <el-button type="primary" @click="showCreate = true">创建用户</el-button>
    </div>
    <el-table :data="users" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="real_name" label="姓名" width="100" />
      <el-table-column prop="role" label="角色" width="80">
        <template #default="{row}">{{ {doctor:'医生',patient:'患者',admin:'管理员'}[row.role] }}</template>
      </el-table-column>
      <el-table-column prop="phone" label="手机" width="130" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{row}"><el-tag :type="row.is_active?'success':'danger'" size="small">{{ row.is_active?'正常':'禁用' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="150">
        <template #default="{row}">
          <el-button v-if="row.is_active" size="small" type="danger" @click="toggleUser(row.id, false)">禁用</el-button>
          <el-button v-else size="small" type="success" @click="toggleUser(row.id, true)">启用</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:16px" :total="total" v-model:current-page="page" :page-size="10" @current-change="fetchData" layout="total, prev, pager, next" />

    <el-dialog v-model="showCreate" title="创建用户" width="400px">
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="newUser.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="newUser.password" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="newUser.real_name" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="newUser.role"><el-option label="医生" value="doctor" /><el-option label="患者" value="patient" /></el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="showCreate=false">取消</el-button><el-button type="primary" @click="createUser">创建</el-button></template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import { ElMessage } from 'element-plus'

const users = ref([]), total = ref(0), page = ref(1), loading = ref(false), filterRole = ref('')
const showCreate = ref(false)
const newUser = ref({ username:'', password:'123456', real_name:'', role:'patient' })

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  const params = { page: page.value, per_page: 10 }
  if (filterRole.value) params.role = filterRole.value
  const res = await api.get('/admin/users', { params })
  if (res.code === 200) { users.value = res.data.items; total.value = res.data.total }
  loading.value = false
}

async function toggleUser(id, activate) {
  if (activate) await api.put(`/admin/users/${id}/activate`)
  else await api.delete(`/admin/users/${id}`)
  fetchData()
}

async function createUser() {
  const res = await api.post('/admin/users', newUser.value)
  if (res.code === 200) { ElMessage.success('创建成功'); showCreate.value = false; fetchData() }
  else ElMessage.error(res.msg)
}
</script>
