<template>
  <section class="orders-page">
    <header class="orders-header">
      <div>
        <p class="eyebrow">订单中心</p>
        <h2>你的最近订单</h2>
      </div>
      <p class="orders-summary">查看你的订单状态与发货信息，体验演示环境中的订单管理。</p>
    </header>

    <div class="orders-grid">
      <article v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-title">
          <div>
            <p class="order-id">订单号 {{ order.id }}</p>
            <p class="order-item">{{ order.itemName }}</p>
          </div>
          <span :class="['status-chip', order.status === '已发货' ? 'status-success' : 'status-pending']">{{ order.status }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const orders = ref([])

const fetchOrders = async () => {
  const sessionId = localStorage.getItem('session_id')
  if (!sessionId) {
    alert('请先登录！')
    return
  }

  try {
    const response = await fetch('/api/orders', {
      headers: {
        'Authorization': `Bearer ${sessionId}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      orders.value = data.map(order => ({
        id: order.id,
        itemName: order.item_name,
        status: order.status
      }))
    } else {
      console.error('Failed to fetch orders')
      // 回退到示例数据
      orders.value = [
        { id: 'ORD-001', itemName: 'SRE 架构指南', status: '已发货' },
        { id: 'ORD-002', itemName: 'K8s 权威指南', status: '待付款' }
      ]
    }
  } catch (error) {
    console.error('Error fetching orders:', error)
    // 回退到示例数据
    orders.value = [
      { id: 'ORD-001', itemName: 'SRE 架构指南', status: '已发货' },
      { id: 'ORD-002', itemName: 'K8s 权威指南', status: '待付款' }
    ]
  }
}

onMounted(fetchOrders)
</script>

<style scoped>
.orders-page {
  display: grid;
  gap: 1.5rem;
}

.orders-header {
  display: grid;
  gap: 0.45rem;
}

.orders-header h2 {
  margin: 0;
}

.orders-summary {
  margin: 0;
  max-width: 52rem;
  color: var(--muted);
}

.orders-grid {
  display: grid;
  gap: 1.3rem;
}

.order-card {
  padding: 1.5rem;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: var(--shadow);
}

.order-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.order-id {
  margin: 0 0 0.4rem;
  color: var(--muted);
}

.order-item {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
}

.status-chip {
  padding: 0.55rem 0.95rem;
  border-radius: 999px;
  font-size: 0.92rem;
  font-weight: 700;
}

.status-success {
  background: rgba(52, 211, 153, 0.14);
  color: #7ef5c7;
}

.status-pending {
  background: rgba(59, 130, 246, 0.14);
  color: #a5d8ff;
}
</style>
