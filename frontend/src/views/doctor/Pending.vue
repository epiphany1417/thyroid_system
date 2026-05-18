<template>
  <el-card header="待诊断列表">
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="patient_name" label="患者" width="120">
        <template #default="{row}">{{ row.patient_name || '未知' }}</template>
      </el-table-column>
      <el-table-column label="原始图像" width="120">
        <template #default="{row}">
          <el-image :src="'/api/doctor/image/' + row.image_path" style="width:80px;height:60px" fit="cover" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="提交时间" width="180" />
      <el-table-column label="操作">
        <template #default="{row}">
          <el-button type="primary" size="small" @click="$router.push('/doctor/diagnosis/' + row.id)">进入诊断</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-if="total > 10" style="margin-top:16px" :total="total" v-model:current-page="page" :page-size="10" @current-change="fetchList" layout="prev, pager, next" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const list = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/doctor/pending', { params: { page: page.value, per_page: 10 } })
    if (res.code === 200) { list.value = res.data.items; total.value = res.data.total }
  } catch (e) {}
  loading.value = false
}

onMounted(fetchList)
</script>
