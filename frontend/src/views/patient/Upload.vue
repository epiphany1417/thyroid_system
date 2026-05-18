<template>
  <el-card header="上传检查图像">
    <el-alert type="info" :closable="false" style="margin-bottom:16px">
      上传您的甲状腺超声检查图像，选择医生后提交，医生将对图像进行AI辅助诊断并给出意见。
    </el-alert>
    <el-form label-width="80px" style="margin-bottom:16px">
      <el-form-item label="选择医生">
        <el-select v-model="doctorId" placeholder="请选择医生" style="width:100%">
          <el-option v-for="d in doctors" :key="d.id" :label="d.real_name" :value="d.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <el-upload ref="uploadRef" :auto-upload="false" :limit="1" accept=".jpg,.jpeg,.png"
      :on-change="handleFileChange" list-type="picture" drag>
      <el-icon style="font-size:40px;color:#909399"><Upload /></el-icon>
      <div>将超声图像拖到此处，或<em>点击上传</em></div>
    </el-upload>
    <el-button type="primary" style="margin-top:16px" @click="handleSubmit" :loading="loading" size="large">提交图像</el-button>

    <el-result v-if="submitted" icon="success" title="图像上传成功" sub-title="请等待医生进行诊断，您可在「诊断记录」中查看结果" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const file = ref(null)
const loading = ref(false)
const submitted = ref(false)
const doctorId = ref(null)
const doctors = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/patient/doctors')
    if (res.code === 200) doctors.value = res.data
  } catch (e) {}
})

function handleFileChange(f) { file.value = f.raw }

async function handleSubmit() {
  if (!doctorId.value) return ElMessage.warning('请选择医生')
  if (!file.value) return ElMessage.warning('请上传图像')
  loading.value = true
  const formData = new FormData()
  formData.append('image', file.value)
  formData.append('doctor_id', doctorId.value)
  try {
    const res = await api.post('/patient/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (res.code === 200) { submitted.value = true; ElMessage.success('上传成功') }
    else ElMessage.error(res.msg)
  } catch (e) { ElMessage.error('上传失败') }
  loading.value = false
}
</script>
