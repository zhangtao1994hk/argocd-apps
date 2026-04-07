<template>
  <div class="app-container">
    <nav>
      <div class="logo">SRE-Demo 电商</div>
      <div class="links">
        <router-link to="/">商品列表</router-link> |
        <span v-if="!isLoggedIn">
          <router-link to="/login">登录</router-link> |
          <router-link to="/register">注册</router-link>
        </span>
        <span v-else>
          <router-link to="/orders">我的订单</router-link> |
          <a href="#" @click.prevent="logout">退出</a>
        </span>
      </div>
    </nav>
    <main>
      <router-view @login-success="updateAuthStatus" />
    </main>
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
/* 简单样式 */
nav { display: flex; justify-content: space-between; padding: 1rem; background: #333; color: white; }
nav a { color: #42b983; text-decoration: none; margin: 0 10px; }
main { padding: 2rem; }
</style>
