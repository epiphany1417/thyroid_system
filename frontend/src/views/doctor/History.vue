<template>
  <el-card header="历史诊断记录">
    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="patient_name" label="患者" width="100" />
      <el-table-column label="AI结果" width="100">
        <template #default="{row}">
          <el-tag :type="row.ai_result==='malignant'?'danger':'success'">{{ row.ai_result==='malignant'?'恶性':'良性' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="置信度" width="100">
        <template #default="{row}">{{ (row.ai_confidence*100).toFixed(1) }}%</template>
      </el-table-column>
      <el-table-column prop="risk_level" label="风险" width="80">
        <template #default="{row}">
          <el-tag size="small" :type="row.risk_level==='high'?'danger':row.risk_level==='medium'?'warning':'success'">
            {{ {high:'高',medium:'中',low:'低'}[row.risk_level] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90" />
      <el-table-column prop="created_at" label="时间" />
      <el-table-column label="操作" width="120">
        <template #default="{row}">
          <el-button size="small" type="primary" @click="viewDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:16px" :total="total" v-model:current-page="page" :page-size="10" @current-change="fetchData" layout="total, prev, pager, next" />

    <!-- 详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="诊断详情" width="700px">
      <div v-if="current">
        <el-row :gutter="16">
          <el-col :span="12">
            <img :src="'/api/doctor/image/' + current.result_image_path" style="width:100%;border-radius:8px" />
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="AI结果">{{ current.ai_result==='malignant'?'恶性':'良性' }}</el-descriptions-item>
              <el-descriptions-item label="置信度">{{ (current.ai_confidence*100).toFixed(1) }}%</el-descriptions-item>
              <el-descriptions-item label="风险等级">{{ {high:'高风险',medium:'中风险',low:'低风险'}[current.risk_level] }}</el-descriptions-item>
              <el-descriptions-item label="医生意见">{{ current.doctor_opinion || '暂无' }}</el-descriptions-item>
            </el-descriptions>
            <el-input v-model="opinion" type="textarea" placeholder="输入诊断意见" style="margin-top:12px" :rows="3" />
            <el-button type="primary" style="margin-top:8px" @click="submitOpinion">提交意见</el-button>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import { ElMessage } from 'element-plus'

const list = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const dialogVisible = ref(false)
const current = ref(null)
const opinion = ref('')

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  const res = await api.get('/doctor/diagnoses', { params: { page: page.value, per_page: 10 } })
  if (res.code === 200) { list.value = res.data.items; total.value = res.data.total }
  loading.value = false
}

function viewDetail(row) { current.value = row; opinion.value = row.doctor_opinion || ''; dialogVisible.value = true }

async function submitOpinion() {
  const res = await api.put(`/doctor/diagnoses/${current.value.id}/opinion`, { opinion: opinion.value })
  if (res.code === 200) { ElMessage.success('已提交'); dialogVisible.value = false; fetchData() }
}
</script>
