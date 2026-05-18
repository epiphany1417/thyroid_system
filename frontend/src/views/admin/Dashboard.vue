<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="总用户数" :value="stats.total_users" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="医生数" :value="stats.total_doctors" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="患者数" :value="stats.total_patients" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="诊断总数" :value="stats.total_diagnoses" /></el-card></el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card header="诊断结果分布">
          <div style="display:flex;align-items:center;gap:30px;padding:20px">
            <div style="text-align:center">
              <div style="font-size:36px;color:#67c23a;font-weight:bold">{{ stats.benign_count }}</div>
              <div>良性</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:36px;color:#f56c6c;font-weight:bold">{{ stats.malignant_count }}</div>
              <div>恶性</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const stats = ref({ total_users:0, total_doctors:0, total_patients:0, total_diagnoses:0, benign_count:0, malignant_count:0 })

onMounted(async () => {
  const res = await api.get('/admin/stats')
  if (res.code === 200) stats.value = res.data
})
</script>
