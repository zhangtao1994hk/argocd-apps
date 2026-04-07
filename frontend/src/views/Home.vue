<template>
  <section class="hero-card">
    <div>
      <p class="eyebrow">热门精选</p>
      <h1>体验现代化云原生电商演示</h1>
      <p class="hero-copy">查看架构书籍、练习订单流程，并体验 ArgoCD/Kubernetes 端到端的运维场景。</p>
      <div class="hero-actions">
        <button @click="buy(products[0].id)">立即抢购</button>
        <router-link to="/login" class="link-secondary">登录查看订单</router-link>
      </div>
    </div>

    <div class="hero-stats">
      <div>
        <strong>3</strong>
        <span>本精选书籍</span>
      </div>
      <div>
        <strong>100%</strong>
        <span>演示可用性</span>
      </div>
      <div>
        <strong>1</strong>
        <span>站式体验</span>
      </div>
    </div>
  </section>

  <section class="product-section">
    <div class="section-header">
      <div>
        <p class="eyebrow">商品列表</p>
        <h2>当前热销商品</h2>
      </div>
      <p>结合 SRE、Kubernetes 和 ArgoCD 的演示型电子商务商品体验。</p>
    </div>

    <div class="product-grid">
      <article v-for="item in products" :key="item.id" class="product-card">
        <div class="product-badge">热销</div>
        <h3>{{ item.name }}</h3>
        <p class="price">¥{{ item.price }}</p>
        <button @click="buy(item.id)">加入购物车</button>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const products = ref([])
const router = useRouter()

const fetchProducts = async () => {
  products.value = [
    { id: 1, name: 'SRE 架构指南', price: 99 },
    { id: 2, name: 'K8s 权威指南', price: 129 },
    { id: 3, name: 'ArgoCD 实践', price: 89 }
  ]
}

const buy = (id) => {
  if (!localStorage.getItem('token')) {
    alert('请先登录！')
    router.push('/login')
  } else {
    alert(`购买请求已发送 (商品ID: ${id})`)
  }
}

onMounted(fetchProducts)
</script>

<style scoped>
.hero-card {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: 1.5rem;
  padding: 2rem;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: var(--shadow);
  margin-bottom: 2rem;
}

.eyebrow {
  margin: 0 0 0.75rem;
  color: var(--accent);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.82rem;
}

.hero-card h1 {
  margin: 0;
  font-size: clamp(2rem, 2.7vw, 3.2rem);
  line-height: 1.05;
}

.hero-copy {
  max-width: 42rem;
  color: var(--muted);
  margin: 1.2rem 0 1.8rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.hero-actions button,
.hero-actions .link-secondary {
  border-radius: 999px;
  padding: 0.95rem 1.5rem;
  font-weight: 600;
}

.hero-actions button {
  border: none;
  background: linear-gradient(135deg, #4fd6ff, #7de2ff);
  color: #08101f;
  cursor: pointer;
}

.hero-actions button:hover {
  filter: brightness(1.05);
}

.link-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.13);
  text-decoration: none;
}

.hero-stats {
  display: grid;
  gap: 1rem;
  align-content: center;
}

.hero-stats div {
  padding: 1.2rem 1.4rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-stats strong {
  display: block;
  font-size: 1.75rem;
  margin-bottom: 0.25rem;
}

.product-section {
  display: grid;
  gap: 1.4rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.section-header h2 {
  margin: 0;
  font-size: 1.9rem;
}

.section-header p {
  margin: 0;
  max-width: 32rem;
  color: var(--muted);
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.4rem;
}

.product-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 1.6rem;
  box-shadow: var(--shadow);
  display: grid;
  gap: 1.2rem;
}

.product-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: rgba(125, 226, 255, 0.14);
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 700;
}

.product-card h3 {
  margin: 0;
  font-size: 1.25rem;
}

.price {
  margin: 0;
  color: #d0e8ff;
  font-size: 1rem;
}

.product-card button {
  margin-top: auto;
  border: none;
  padding: 0.95rem 1.2rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #4fd6ff, #7de2ff);
  color: #08101f;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.product-card button:hover {
  transform: translateY(-2px);
}
</style>
