<template>
  <div>
    <h2>我的订单</h2>
    <ul>
      <li v-for="order in orders" :key="order.id">
        订单号: {{ order.id }} - 商品: {{ order.itemName }} - 状态: <b>{{ order.status }}</b>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const orders = ref([])

onMounted(() => {
  // 模拟从后端拉取订单
  orders.value = [
    { id: 'ORD-001', itemName: 'SRE 架构指南', status: '已发货' },
    { id: 'ORD-002', itemName: 'K8s 权威指南', status: '待付款' }
  ]
})
</script>
