<template>
  <el-card header="主动诊断 - 上传超声图像">
    <el-form :model="form" label-width="100px">
      <el-form-item label="选择患者">
        <el-select v-model="form.patient_id" placeholder="请选择患者" filterable style="width:100%">
          <el-option v-for="p in patients" :key="p.id" :label="p.real_name || p.username" :value="p.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="超声图像">
        <el-upload ref="uploadRef" :auto-upload="false" :limit="1" accept=".jpg,.jpeg,.png"
          :on-change="handleFileChange" list-type="picture" drag>
          <el-icon style="font-size:40px;color:#909399"><Upload /></el-icon>
          <div>将图像拖到此处，或<em>点击上传</em></div>
        </el-upload>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="loading" size="large">上传并进入诊断</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const router = useRouter()
const form = ref({ patient_id: '' })
const patients = ref([])
const file = ref(null)
const loading = ref(false)

onMounted(async () => {
  const res = await api.get('/doctor/patients')
  if (res.code === 200) patients.value = res.data
})

function handleFileChange(f) { file.value = f.raw }

async function handleSubmit() {
  if (!form.value.patient_id) return ElMessage.warning('请选择患者')
  if (!file.value) return ElMessage.warning('请上传图像')

  loading.value = true
  const formData = new FormData()
  formData.append('image', file.value)
  formData.append('patient_id', form.value.patient_id)

  try {
    const res = await api.post('/doctor/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (res.code === 200) {
      ElMessage.success('上传成功，进入诊断页面')
      router.push('/doctor/diagnosis/' + res.data.id)
    } else {
      ElMessage.error(res.msg)
    }
  } catch (e) {
    ElMessage.error('上传失败')
  }
  loading.value = false
}
</script>
