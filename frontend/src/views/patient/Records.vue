<template>
  <el-card header="我的诊断记录">
    <el-table :data="records" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="状态" width="110">
        <template #default="{row}">
          <el-tag v-if="row.status==='pending'" type="warning">待医生诊断</el-tag>
          <el-tag v-else-if="row.status==='completed'" type="success">已完成</el-tag>
          <el-tag v-else type="info">已审核</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="AI结果" width="100">
        <template #default="{row}">
          <template v-if="row.ai_result">
            <el-tag :type="row.ai_result==='malignant'?'danger':'success'">{{ row.ai_result==='malignant'?'恶性':'良性' }}</el-tag>
          </template>
          <span v-else style="color:#999">-</span>
        </template>
      </el-table-column>
      <el-table-column label="风险" width="80">
        <template #default="{row}">
          <template v-if="row.risk_level">
            <el-tag size="small" :type="row.risk_level==='high'?'danger':row.risk_level==='medium'?'warning':'success'">
              {{ {high:'高',medium:'中',low:'低'}[row.risk_level] }}
            </el-tag>
          </template>
          <span v-else style="color:#999">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="doctor_name" label="医生" width="100" />
      <el-table-column prop="created_at" label="时间" />
      <el-table-column label="操作" width="100">
        <template #default="{row}">
          <el-button size="small" @click="viewDetail(row)" :disabled="row.status==='pending'">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:16px" :total="total" v-model:current-page="page" :page-size="10" @current-change="fetchData" layout="total, prev, pager, next" />

    <el-dialog v-model="dialogVisible" title="诊断详情" width="650px">
      <div v-if="current">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-image v-if="current.result_image_path" :src="'/api/doctor/image/' + current.result_image_path" style="width:100%;border-radius:8px" fit="contain" />
            <el-image v-else :src="'/api/doctor/image/' + current.image_path" style="width:100%;border-radius:8px" fit="contain" />
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="AI结果">{{ current.ai_result==='malignant'?'恶性':'良性' }}</el-descriptions-item>
              <el-descriptions-item label="置信度">{{ (current.ai_confidence*100).toFixed(1) }}%</el-descriptions-item>
              <el-descriptions-item label="风险等级">{{ {high:'高风险',medium:'中风险',low:'低风险'}[current.risk_level] }}</el-descriptions-item>
              <el-descriptions-item label="医生意见">{{ current.doctor_opinion || '暂无' }}</el-descriptions-item>
              <el-descriptions-item label="结果解释">{{ explanation }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../api'

const records = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const dialogVisible = ref(false)
const current = ref(null)

const explanation = computed(() => {
  if (!current.value) return ''
  if (current.value.risk_level === 'high') return '风险较高，建议尽快就医进一步检查'
  if (current.value.risk_level === 'medium') return '存在一定风险，建议定期复查'
  return '风险较低，建议定期体检观察'
})

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  const res = await api.get('/patient/diagnoses', { params: { page: page.value, per_page: 10 } })
  if (res.code === 200) { records.value = res.data.items; total.value = res.data.total }
  loading.value = false
}

function viewDetail(row) { current.value = row; dialogVisible.value = true }
</script>
