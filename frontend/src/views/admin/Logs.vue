<template>
  <el-card header="操作日志">
    <el-table :data="logs" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户" width="100" />
      <el-table-column prop="action" label="操作" width="120" />
      <el-table-column prop="detail" label="详情" />
      <el-table-column prop="ip_address" label="IP" width="130" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>
    <el-pagination style="margin-top:16px" :total="total" v-model:current-page="page" :page-size="20" @current-change="fetchData" layout="total, prev, pager, next" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const logs = ref([]), total = ref(0), page = ref(1), loading = ref(false)

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  const res = await api.get('/admin/logs', { params: { page: page.value, per_page: 20 } })
  if (res.code === 200) { logs.value = res.data.items; total.value = res.data.total }
  loading.value = false
}
</script>
