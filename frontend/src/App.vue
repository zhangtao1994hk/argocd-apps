<template>
  <div class="app-shell">
    <div class="page-bg"></div>

    <header class="topbar">
      <div class="brand">
        <div class="brand-mark">SRE</div>
        <div>
          <div class="brand-title">SRE-Demo 电商</div>
          <div class="brand-subtitle">现代运维与云原生演示平台</div>
        </div>
      </div>

      <nav class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/orders" v-if="isLoggedIn">我的订单</router-link>
        <router-link to="/login" v-if="!isLoggedIn">登录</router-link>
        <router-link to="/register" v-if="!isLoggedIn">注册</router-link>
        <button v-if="isLoggedIn" class="ghost-btn" @click="logout">退出</button>
      </nav>
    </header>

    <main class="content">
      <router-view @login-success="updateAuthStatus" />
    </main>

    <footer class="footer">© 2026 SRE-Demo 电商 · 现代云原生 SRE 演示</footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = ref(false)

const updateAuthStatus = () => {
  isLoggedIn.value = !!localStorage.getItem('token')
}

const logout = () => {
  localStorage.removeItem('token')
  updateAuthStatus()
  router.push('/')
}

onMounted(() => {
  updateAuthStatus()
})
</script>

<style>
:root {
  color-scheme: dark;
  --bg: #08101f;
  --panel: rgba(18, 30, 48, 0.92);
  --surface: rgba(255, 255, 255, 0.07);
  --surface-strong: rgba(255, 255, 255, 0.12);
  --text: #f3f8ff;
  --muted: #9cb1dc;
  --accent: #7de2ff;
  --accent-strong: #4fd6ff;
  --border: rgba(255, 255, 255, 0.14);
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.25);
  --font-family: "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
}

* {
  box-sizing: border-box;
}

html,
body,
#app {
  min-height: 100%;
}

body {
  margin: 0;
  background: radial-gradient(circle at 10% 10%, rgba(125, 226, 255, 0.15), transparent 18%),
    radial-gradient(circle at 80% 20%, rgba(52, 211, 153, 0.12), transparent 16%),
    linear-gradient(180deg, #0b1321 0%, #08101f 100%);
  color: var(--text);
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  line-height: 1.6;
}

button,
input {
  font-family: inherit;
}

.app-shell {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.page-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 15% 15%, rgba(125, 226, 255, 0.18), transparent 18%),
    radial-gradient(circle at 92% 18%, rgba(52, 211, 153, 0.14), transparent 16%),
    radial-gradient(circle at 50% 92%, rgba(99, 102, 241, 0.10), transparent 22%);
  pointer-events: none;
  z-index: 0;
}

.topbar {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 2rem;
  backdrop-filter: blur(18px);
  background: rgba(10, 16, 28, 0.82);
  border-bottom: 1px solid var(--border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(135deg, #4fd6ff, #7de2ff);
  display: grid;
  place-items: center;
  color: #08101f;
  font-weight: 800;
  font-size: 0.95rem;
  letter-spacing: 0.12em;
}

.brand-title {
  font-size: 1.05rem;
  font-weight: 700;
}

.brand-subtitle {
  color: var(--muted);
  font-size: 0.9rem;
  margin-top: 0.15rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  flex-wrap: wrap;
}

.nav-links a,
.nav-links button {
  color: var(--text);
  text-decoration: none;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid transparent;
  padding: 0.76rem 1.1rem;
  border-radius: 999px;
  transition: all 0.2s ease;
}

.nav-links a:hover,
.nav-links button:hover {
  background: rgba(125, 226, 255, 0.14);
  border-color: rgba(125, 226, 255, 0.28);
}

.ghost-btn {
  cursor: pointer;
}

.content {
  position: relative;
  z-index: 1;
  max-width: 1180px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 3rem;
}

.footer {
  position: relative;
  z-index: 1;
  text-align: center;
  color: var(--muted);
  padding: 1.25rem 1.5rem 2rem;
  font-size: 0.95rem;
}
</style>
