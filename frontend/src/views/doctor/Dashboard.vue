<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover"><el-statistic title="总诊断数" :value="stats.total" /></el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover"><el-statistic title="良性结节" :value="stats.benign" /></el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover"><el-statistic title="恶性结节" :value="stats.malignant" /></el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:20px" header="最近诊断记录">
      <el-table :data="recentList" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="patient_name" label="患者" width="100" />
        <el-table-column prop="ai_result" label="AI结果" width="100">
          <template #default="{row}">
            <el-tag :type="row.ai_result==='malignant'?'danger':'success'">{{ row.ai_result==='malignant'?'恶性':'良性' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ai_confidence" label="置信度" width="100">
          <template #default="{row}">{{ (row.ai_confidence*100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="created_at" label="时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const stats = ref({ total: 0, benign: 0, malignant: 0 })
const recentList = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/doctor/diagnoses', { params: { per_page: 5 } })
    if (res.code === 200) {
      recentList.value = res.data.items
      stats.value.total = res.data.total
      stats.value.benign = res.data.items.filter(d => d.ai_result === 'benign').length
      stats.value.malignant = res.data.items.filter(d => d.ai_result === 'malignant').length
    }
  } catch (e) { console.error(e) }
})
</script>
