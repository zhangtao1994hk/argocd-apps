<template>
  <div class="auth-form">
    <h2>用户登录</h2>
    <input v-model="username" placeholder="用户名 (admin)" />
    <input v-model="password" type="password" placeholder="密码 (123456)" />
    <button @click="handleLogin">登录</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['login-success'])
const router = useRouter()
const username = ref('')
const password = ref('')

const handleLogin = async () => {
  // 实际演练这里会调用 axios.post('/api/login', { username, password })
  if (username.value === 'admin' && password.value === '123456') {
    localStorage.setItem('token', 'fake-jwt-token-123')
    emit('login-success')
    router.push('/orders') // 登录成功跳去订单页
  } else {
    alert('用户名或密码错误！(提示: admin / 123456)')
  }
}
</script>
