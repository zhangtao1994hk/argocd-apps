<template>
  <section class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <p class="eyebrow">创建账户</p>
        <h2>开始你的 SRE 电商之旅</h2>
        <p class="auth-intro">填写信息后即可体验现代化运维与购物流程。</p>
      </div>

      <div class="form-field">
        <label>用户名</label>
        <input v-model="username" placeholder="请输入用户名" autocomplete="username" />
      </div>
      <div class="form-field">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="请输入密码" autocomplete="new-password" />
      </div>
      <div class="form-field">
        <label>确认密码</label>
        <input v-model="confirmPassword" type="password" placeholder="请再次输入密码" autocomplete="new-password" />
      </div>

      <button class="primary-btn" @click="handleRegister">注册</button>
      <p class="auth-footnote">注册后请使用登录页进入系统。</p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const confirmPassword = ref('')

const handleRegister = () => {
  if (!username.value || !password.value) {
    alert('用户名和密码不能为空！')
    return
  }
  if (password.value !== confirmPassword.value) {
    alert('两次输入的密码不一致！')
    return
  }

  alert(`注册成功！欢迎你，${username.value}。请登录。`)
  router.push('/login')
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
