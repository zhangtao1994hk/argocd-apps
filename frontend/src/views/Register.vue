啊，这是我的疏忽！我在 router/index.js 里配置了注册页面的路由，但是前面漏掉了 Register.vue 文件的代码，导致 Vite 编译时找不到这个文件报错了。

请在 src/views/ 目录下新建一个 Register.vue 文件，并填入以下代码：

src/views/Register.vue
<template>
  <div class="auth-form">
    <h2>用户注册</h2>
    <input v-model="username" placeholder="请输入用户名" />
    <input v-model="password" type="password" placeholder="请输入密码" />
    <input v-model="confirmPassword" type="password" placeholder="请确认密码" />
    <button @click="handleRegister">注册</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const confirmPassword = ref('')

const handleRegister = async () => {
  if (!username.value || !password.value) {
    alert('用户名和密码不能为空！')
    return
  }
  if (password.value !== confirmPassword.value) {
    alert('两次输入的密码不一致！')
    return
  }

  // 实际演练这里会调用 axios.post('/api/register', { username, password })
  alert(`注册成功！欢迎你，${username.value}。请登录。`)
  router.push('/login') // 注册成功后跳转到登录页
}
</script>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  width: 300px;
  gap: 15px;
  margin: 0 auto;
  margin-top: 50px;
}
input {
  padding: 8px;
  font-size: 16px;
}
button {
  padding: 10px;
  font-size: 16px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover {
  background-color: #33a06f;
}
</style>
