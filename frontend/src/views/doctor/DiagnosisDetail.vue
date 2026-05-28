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
              <el-button v-if="diagnosis.status!=='completed'" size="small" style="margin-left:8px" @click="openEditDialog" :icon="Edit">修改</el-button>
            </el-descriptions-item>
            <el-descriptions-item v-if="diagnosis.ai_confidence !== null && diagnosis.ai_confidence !== undefined" label="置信度">{{ (diagnosis.ai_confidence*100).toFixed(1) }}%</el-descriptions-item>
            <el-descriptions-item v-if="diagnosis.risk_level" label="风险等级">
              <el-tag :type="{high:'danger',medium:'warning',low:'success'}[diagnosis.risk_level]">{{ {high:'高风险',medium:'中风险',low:'低风险'}[diagnosis.risk_level] }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="diagnosis.original_ai_result" label="AI原始分类">
              <el-tag type="info">{{ diagnosis.original_ai_result==='malignant'?'恶性':'良性' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="diagnosis.original_risk_level" label="AI原始风险">
              <el-tag type="info">{{ {high:'高风险',medium:'中风险',low:'低风险'}[diagnosis.original_risk_level] }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <!-- AI诊断按钮 -->
          <el-button v-if="diagnosis.status==='pending' && !diagnosis.ai_result" type="warning" style="margin-top:16px;width:100%" @click="runAI" :loading="aiLoading" size="large">执行AI诊断</el-button>

          <!-- AI参考意见（LLM生成） -->
          <div v-if="diagnosis.ai_opinion" style="margin-top:16px">
            <el-divider />
            <h4>AI参考意见 <el-tag size="small" type="info">由大模型生成，仅供参考</el-tag></h4>
            <div style="background:#f5f7fa;padding:12px;border-radius:6px;white-space:pre-wrap;font-size:13px;color:#606266;max-height:200px;overflow-y:auto">{{ diagnosis.ai_opinion }}</div>
          </div>

          <!-- 医生意见输入 -->
          <el-divider />
          <h4>医生诊断意见</h4>
          <el-input v-model="opinion" type="textarea" placeholder="请输入您的诊断意见" :rows="4" :disabled="diagnosis.status==='completed'" />
          <el-button v-if="diagnosis.status!=='completed'" type="primary" style="margin-top:12px;width:100%" @click="submitDiagnose" :loading="submitLoading" size="large">提交诊断</el-button>
          <el-alert v-if="diagnosis.status==='completed'" type="success" :closable="false" style="margin-top:12px" title="该诊断已完成提交" />
        </el-col>
      </el-row>
    </div>

    <!-- 修改AI结果弹窗 -->
    <el-dialog v-model="showEditAI" title="修改AI诊断结果" width="400px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="良恶性分类">
          <el-select v-model="editForm.ai_result" style="width:100%">
            <el-option label="良性" value="benign" />
            <el-option label="恶性" value="malignant" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="editForm.risk_level" style="width:100%">
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditAI = false">取消</el-button>
        <el-button type="primary" @click="saveAIResult" :loading="editLoading">确认修改</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const diagnosis = ref(null)
const opinion = ref('')
const loading = ref(true)
const aiLoading = ref(false)
const submitLoading = ref(false)
const showEditAI = ref(false)
const editLoading = ref(false)
const editForm = ref({ ai_result: '', risk_level: '' })

const statusText = computed(() => ({ pending: '待诊断', completed: '已完成', reviewed: '已审核' }[diagnosis.value?.status] || ''))
const statusType = computed(() => ({ pending: 'warning', completed: 'success', reviewed: 'info' }[diagnosis.value?.status] || ''))

onMounted(async () => {
  const res = await api.get(`/doctor/diagnoses/${route.params.id}`)
  if (res.code === 200) {
    diagnosis.value = res.data
    opinion.value = res.data.doctor_opinion || res.data.ai_opinion || ''
  }
  loading.value = false
})

function openEditDialog() {
  editForm.value.ai_result = diagnosis.value.ai_result
  editForm.value.risk_level = diagnosis.value.risk_level
  showEditAI.value = true
}

async function saveAIResult() {
  editLoading.value = true
  try {
    const res = await api.put(`/doctor/diagnoses/${route.params.id}/ai-result`, {
      ai_result: editForm.value.ai_result,
      risk_level: editForm.value.risk_level
    })
    if (res.code === 200) {
      diagnosis.value = res.data
      showEditAI.value = false
      ElMessage.success('AI结果已更新')
    } else {
      ElMessage.error(res.msg)
    }
  } catch (e) {
    ElMessage.error('修改失败')
  }
  editLoading.value = false
}

async function runAI() {
  aiLoading.value = true
  try {
    const res = await api.post(`/doctor/diagnose/${route.params.id}`)
    if (res.code === 200) {
      diagnosis.value = res.data
      opinion.value = res.data.doctor_opinion || res.data.ai_opinion || ''
      ElMessage.success('AI诊断完成')
    } else ElMessage.error(res.msg)
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
