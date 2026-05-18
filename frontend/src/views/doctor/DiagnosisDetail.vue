<template>
  <el-card v-loading="loading">
    <template #header>
      <span>诊断工作台</span>
      <el-tag style="margin-left:10px" :type="statusType">{{ statusText }}</el-tag>
    </template>
    <div v-if="diagnosis">
      <el-row :gutter="20">
        <el-col :span="12">
          <h4>原始图像</h4>
          <el-image :src="'/api/doctor/image/' + diagnosis.image_path" style="width:100%;border-radius:8px" fit="contain" />
          <div v-if="diagnosis.result_image_path" style="margin-top:16px">
            <h4>AI标注结果图</h4>
            <el-image :src="'/api/doctor/image/' + diagnosis.result_image_path" style="width:100%;border-radius:8px" fit="contain" />
          </div>
        </el-col>
        <el-col :span="12">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="患者">{{ diagnosis.patient_name || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="提交时间">{{ diagnosis.created_at }}</el-descriptions-item>
            <el-descriptions-item v-if="diagnosis.ai_result" label="AI分类">
              <el-tag :type="diagnosis.ai_result==='malignant'?'danger':'success'">
                {{ diagnosis.ai_result==='malignant'?'恶性':'良性' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="diagnosis.ai_confidence" label="置信度">{{ (diagnosis.ai_confidence*100).toFixed(1) }}%</el-descriptions-item>
            <el-descriptions-item v-if="diagnosis.risk_level" label="风险等级">
              <el-tag :type="{high:'danger',medium:'warning',low:'success'}[diagnosis.risk_level]">{{ {high:'高风险',medium:'中风险',low:'低风险'}[diagnosis.risk_level] }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <!-- AI诊断按钮 -->
          <el-button v-if="diagnosis.status==='pending' && !diagnosis.ai_result" type="warning" style="margin-top:16px;width:100%" @click="runAI" :loading="aiLoading" size="large">执行AI诊断</el-button>

          <!-- 医生意见输入 -->
          <el-divider />
          <h4>医生诊断意见</h4>
          <el-input v-model="opinion" type="textarea" placeholder="请输入您的诊断意见" :rows="4" :disabled="diagnosis.status==='completed'" />
          <el-button v-if="diagnosis.status!=='completed'" type="primary" style="margin-top:12px;width:100%" @click="submitDiagnose" :loading="submitLoading" size="large">提交诊断</el-button>
          <el-alert v-if="diagnosis.status==='completed'" type="success" :closable="false" style="margin-top:12px" title="该诊断已完成提交" />
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const diagnosis = ref(null)
const opinion = ref('')
const loading = ref(true)
const aiLoading = ref(false)
const submitLoading = ref(false)

const statusText = computed(() => ({ pending: '待诊断', completed: '已完成', reviewed: '已审核' }[diagnosis.value?.status] || ''))
const statusType = computed(() => ({ pending: 'warning', completed: 'success', reviewed: 'info' }[diagnosis.value?.status] || ''))

onMounted(async () => {
  const res = await api.get(`/doctor/diagnoses/${route.params.id}`)
  if (res.code === 200) { diagnosis.value = res.data; opinion.value = res.data.doctor_opinion || '' }
  loading.value = false
})

async function runAI() {
  aiLoading.value = true
  try {
    const res = await api.post(`/doctor/diagnose/${route.params.id}`)
    if (res.code === 200) { diagnosis.value = res.data; ElMessage.success('AI诊断完成') }
    else ElMessage.error(res.msg)
  } catch (e) { ElMessage.error('AI诊断失败') }
  aiLoading.value = false
}

async function submitDiagnose() {
  if (!opinion.value.trim()) return ElMessage.warning('请输入诊断意见')
  submitLoading.value = true
  try {
    const res = await api.post(`/doctor/diagnose/${route.params.id}/submit`, { opinion: opinion.value })
    if (res.code === 200) { diagnosis.value = res.data; ElMessage.success('诊断已提交'); router.push('/doctor/history') }
    else ElMessage.error(res.msg)
  } catch (e) { ElMessage.error('提交失败') }
  submitLoading.value = false
}
</script>
