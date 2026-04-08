<template>
  <section class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <p class="eyebrow">欢迎回来</p>
        <h2>登录你的账户</h2>
        <p class="auth-intro">使用演示账号登录，体验完整 SRE 电商流程。</p>
      </div>

      <div class="form-field">
        <label>用户名</label>
        <input v-model="username" placeholder="请输入用户名" autocomplete="username" />
      </div>
      <div class="form-field">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="请输入密码" autocomplete="current-password" />
      </div>

      <button class="primary-btn" @click="handleLogin">登录</button>
      <p class="auth-footnote">没有账户？<router-link to="/register">注册新账户</router-link></p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['login-success'])
const router = useRouter()
const username = ref('')
const password = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    alert('用户名和密码不能为空！')
    return
  }

  try {
    const response = await fetch('/api/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    })

    const data = await response.json()

    if (response.ok) {
      const sessionId = data.session_id || data.id || ''
      localStorage.setItem('session_id', sessionId)
      localStorage.setItem('token', 'fake-jwt-token-123')
      emit('login-success')
      router.push('/orders')
    } else {
      alert(data.error || '登录失败！')
    }
  } catch (error) {
    console.error('Login error:', error)
    alert('网络错误，请稍后重试！')
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  padding: 2.5rem 0;
}

.auth-card {
  width: min(520px, 100%);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
  box-shadow: var(--shadow);
  padding: 2rem;
}

.auth-header {
  margin-bottom: 1.8rem;
}

.auth-header h2 {
  margin: 0.4rem 0 0.6rem;
}

.auth-intro {
  margin: 0;
  color: var(--muted);
}

.form-field {
  display: grid;
  gap: 0.55rem;
  margin-bottom: 1.2rem;
}

.form-field label {
  color: var(--muted);
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.95rem 1rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus {
  border-color: rgba(125, 226, 255, 0.8);
  box-shadow: 0 0 0 4px rgba(125, 226, 255, 0.12);
}

.primary-btn {
  width: 100%;
  border: none;
  border-radius: 999px;
  padding: 1rem 1.2rem;
  background: linear-gradient(135deg, #4fd6ff, #7de2ff);
  color: #08101f;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.primary-btn:hover {
  transform: translateY(-1px);
}

.auth-footnote {
  margin: 1rem 0 0;
  color: var(--muted);
  font-size: 0.95rem;
}
</style>
