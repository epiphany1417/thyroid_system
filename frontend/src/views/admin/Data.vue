<template>
  <el-card header="数据管理 - 诊断记录">
    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="patient_name" label="患者" width="100" />
      <el-table-column prop="doctor_name" label="医生" width="100" />
      <el-table-column label="AI结果" width="100">
        <template #default="{row}">
          <el-tag :type="row.ai_result==='malignant'?'danger':'success'">{{ row.ai_result==='malignant'?'恶性':'良性' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="置信度" width="100">
        <template #default="{row}">{{ row.ai_confidence ? (row.ai_confidence*100).toFixed(1)+'%' : '-' }}</template>
      </el-table-column>
      <el-table-column prop="risk_level" label="风险" width="80" />
      <el-table-column prop="status" label="状态" width="90" />
      <el-table-column prop="created_at" label="时间" />
      <el-table-column label="操作" width="100">
        <template #default="{row}">
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference><el-button size="small" type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:16px" :total="total" v-model:current-page="page" :page-size="10" @current-change="fetchData" layout="total, prev, pager, next" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import { ElMessage } from 'element-plus'

const list = ref([]), total = ref(0), page = ref(1), loading = ref(false)

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  const res = await api.get('/admin/diagnoses', { params: { page: page.value, per_page: 10 } })
  if (res.code === 200) { list.value = res.data.items; total.value = res.data.total }
  loading.value = false
}

async function handleDelete(id) {
  await api.delete(`/admin/diagnoses/${id}`)
  ElMessage.success('已删除')
  fetchData()
}
</script>
