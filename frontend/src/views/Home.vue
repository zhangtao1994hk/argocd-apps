<template>
  <div>
    <h2>最新商品</h2>
    <div class="product-grid">
      <div v-for="item in products" :key="item.id" class="product-card">
        <h3>{{ item.name }}</h3>
        <p>价格: ¥{{ item.price }}</p>
        <button @click="buy(item.id)">立即购买</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const products = ref([])
const router = useRouter()

// 模拟从后端拉取商品
const fetchProducts = async () => {
  try {
    // 实际演练中，这里会请求 /api/products
    // const res = await axios.get('/api/products')
    // products.value = res.data
    
    // 假数据做展示
    products.value = [
      { id: 1, name: 'SRE 架构指南', price: 99 },
      { id: 2, name: 'K8s 权威指南', price: 129 },
      { id: 3, name: 'ArgoCD 实践', price: 89 }
    ]
  } catch (error) {
    console.error("Failed to fetch products", error)
  }
}

const buy = (id) => {
  if (!localStorage.getItem('token')) {
    alert('请先登录！')
    router.push('/login')
  } else {
    alert(`购买请求已发送 (商品ID: ${id})`)
    // 实际演练中这里调用后端创单接口
  }
}

onMounted(fetchProducts)
</script>

<style>
.product-grid { display: flex; gap: 20px; }
.product-card { border: 1px solid #ccc; padding: 15px; border-radius: 8px; }
</style>
