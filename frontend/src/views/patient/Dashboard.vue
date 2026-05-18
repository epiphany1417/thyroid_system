<template>
  <div>
    <el-card header="我的诊断概览">
      <el-empty v-if="records.length === 0" description="暂无诊断记录" />
      <el-row :gutter="16" v-else>
        <el-col :span="8">
          <el-statistic title="总检查次数" :value="total" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="良性" :value="records.filter(r=>r.ai_result==='benign').length" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="恶性" :value="records.filter(r=>r.ai_result==='malignant').length" />
        </el-col>
      </el-row>
    </el-card>
    <el-card style="margin-top:20px" header="最近记录">
      <el-timeline>
        <el-timeline-item v-for="r in records.slice(0,5)" :key="r.id" :timestamp="r.created_at" placement="top">
          <el-tag :type="r.ai_result==='malignant'?'danger':'success'" size="small">{{ r.ai_result==='malignant'?'恶性':'良性' }}</el-tag>
          置信度: {{ (r.ai_confidence*100).toFixed(1) }}% | 风险: {{ {high:'高',medium:'中',low:'低'}[r.risk_level] }}
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const records = ref([])
const total = ref(0)

onMounted(async () => {
  const res = await api.get('/patient/diagnoses', { params: { per_page: 10 } })
  if (res.code === 200) { records.value = res.data.items; total.value = res.data.total }
})
</script>
