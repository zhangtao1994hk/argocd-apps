# 🎯 快速导航 - 第一次使用请从这里开始

欢迎使用 **ArgoCD Apps** - 一个基于 App of Apps 模式的云原生 GitOps 管理平台！

本项目用于管理 Google Kubernetes Engine (GKE) 集群中的所有应用。

---

## ⚡ 3 分钟快速了解

```bash
# 1. 初始化 ArgoCD
bash init.sh

# 2. 部署所有应用
kubectl apply -f root-app.yaml

# 3. 查看状态
kubectl get applications -n argocd
```

---

## 📚 根据你的需求选择文档

### 👤 我是新用户，刚接触这个项目

**阅读顺序**：

1. **[README.md](./README.md)** (5 分钟)
   - 了解项目是什么
   - 了解三层架构
   - 了解 App of Apps 模式

2. **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** (15 分钟)
   - 一步步初始化集群
   - 各个验证检查点
   - 常见问题解决

3. **[CHEATSHEET.md](./CHEATSHEET.md)** (随时查阅)
   - 快速命令参考
   - 日常操作命令

---

### 🔧 我需要初始化一个新的 GKE 集群

**步骤**：

1. 查看 [SETUP_GUIDE.md](./SETUP_GUIDE.md#-前置条件检查清单) 的前置条件检查
2. 运行 `bash init.sh`
3. 按照 [SETUP_GUIDE.md](./SETUP_GUIDE.md#-验证-argocd-安装) 验证安装
4. 运行 `kubectl apply -f root-app.yaml`

---

### 📊 我想了解系统架构

**查看文档**：

- [README.md](./README.md#-项目架构) - 三层架构设计
- [README.md](./README.md#-数据流和工作流) - 数据流和工作流
- [root-app.yaml](./root-app.yaml) - App of Apps 模式解释

---

### 🎯 我需要常用命令

**查看**：[CHEATSHEET.md](./CHEATSHEET.md)

快速查询：
- [查看应用](./CHEATSHEET.md#-常用命令)
- [调试 Pod](./CHEATSHEET.md#-pod-无法启动)
- [查看日志](./CHEATSHEET.md#-日志查看)
- [故障排查](./CHEATSHEET.md#-应用同步卡住)

---

### 🔐 我要为生产环境准备

**检查清单**：

1. [README.md](./README.md#-安全最佳实践) - 安全最佳实践
2. [SETUP_GUIDE.md](./SETUP_GUIDE.md#-生产环境检查清单) - 生产环境检查清单
3. 修改默认密码（见 [CHEATSHEET.md](./CHEATSHEET.md#-修改管理员密码)）

---

## 📂 项目结构速览

```
argocd-apps/
├── 📄 init.sh                 ← 初始化脚本（第一个运行这个）
├── 📄 root-app.yaml           ← 根应用（App of Apps 模式）
│
├── 📚 文档/
│   ├── README.md              ← 项目总体介绍
│   ├── SETUP_GUIDE.md         ← 详细初始化指南
│   ├── CHEATSHEET.md          ← 快速参考卡
│   └── START_HERE.md          ← 本文件
│
├── 📁 applications/           ← 所有 Application 定义
│   ├── backend-app.yaml
│   ├── frontend-app.yaml
│   ├── mysql-app.yaml
│   └── ... (15+ 个应用)
│
├── 📁 infrastructure/         ← 基础设施配置
│   ├── kube-prometheus-stack/
│   ├── loki/
│   └── ...
│
├── 📁 backend/                ← 后端代码
├── 📁 frontend/               ← 前端代码
└── 📁 dao/                    ← 数据访问层代码
```

---

## 🌟 核心概念

### App of Apps 模式

```
root-app (唯一的根应用)
  ↓
自动发现 applications/ 目录中的所有 Application
  ↓
自动部署和同步 15+ 个子应用
  ↓
用户只需管理根应用，其他都自动搞定
```

### 三层架构

```
Application Layer      Backend、Frontend、DAO 等微服务
         ↓
Infrastructure Layer   MySQL、Redis、ArgoCD、Traefik 等
         ↓
Observability Layer    Prometheus、Grafana、Loki、Tempo 等
```

### GitOps 工作流

```
Git 提交代码
  ↓
GitHub Actions 构建镜像
  ↓
更新 Git 中的镜像 tag
  ↓
ArgoCD 检测变化
  ↓
自动同步到 Kubernetes
  ↓
应用部署完成
```

---

## 🎓 学习路径

### 第 1 天：了解和初始化

- 早上：阅读 README.md（20 分钟）
- 中午：按照 SETUP_GUIDE.md 初始化（30 分钟）
- 下午：验证所有组件正常运行（20 分钟）

### 第 2 天：实操和调试

- 查看 ArgoCD UI 中的应用状态
- 修改一个应用配置并观察自动同步
- 使用 CHEATSHEET.md 中的命令进行日常操作

### 第 3 天：深入了解

- 研究 root-app.yaml 的 App of Apps 模式
- 查看 applications/ 目录中的应用定义
- 研究 Prometheus 和 Grafana 的集成

---

## 🆘 遇到问题？

### 问题排查流程

1. **查看相关文档**
   - 初始化问题 → [SETUP_GUIDE.md](./SETUP_GUIDE.md)
   - 命令问题 → [CHEATSHEET.md](./CHEATSHEET.md)
   - 架构问题 → [README.md](./README.md#-故障排查)

2. **查看日志**（最常用的调试方法）
   ```bash
   kubectl logs -f deployment/argo-cd-argocd-server -n argocd
   ```

3. **查看 Pod 事件**
   ```bash
   kubectl describe pod <pod-name> -n argocd
   ```

4. **查看应用状态**
   ```bash
   kubectl describe application <app-name> -n argocd
   ```

---

## 📞 获取帮助

1. ❓ 不知道怎么开始？→ 阅读 [README.md](./README.md)
2. 🔧 不知道怎么初始化？→ 按照 [SETUP_GUIDE.md](./SETUP_GUIDE.md)
3. 💻 不知道命令？→ 查询 [CHEATSHEET.md](./CHEATSHEET.md)
4. 🐛 应用部署失败？→ [SETUP_GUIDE.md#-常见问题排查](./SETUP_GUIDE.md#-常见问题排查)

---

## ✨ 关键特性速览

| 特性 | 说明 |
|------|------|
| **App of Apps** | 单点管理 15+ 个应用 |
| **自动同步** | Git 变化自动部署到集群 |
| **自我修复** | 集群漂移自动恢复 |
| **可视化** | Grafana 仪表板展示所有指标 |
| **可观测性** | Prometheus + Loki + Tempo 完整链路 |
| **GitOps** | 所有配置都在 Git（版本控制） |
| **灰度发布** | 支持 Argo Rollouts 金丝雀部署 |
| **企业级安全** | RBAC、SecurityContext、审计日志 |

---

## 🚀 下一步

### 现在就开始

```bash
# 花费 5 分钟，你将拥有一个完整的 Kubernetes 管理平台
bash init.sh
kubectl apply -f root-app.yaml
```

### 然后阅读

- [README.md](./README.md) - 深入了解系统
- [CHEATSHEET.md](./CHEATSHEET.md) - 掌握日常命令

### 最后配置生产环境

- [README.md](./README.md#-安全最佳实践) 中的安全建议
- [SETUP_GUIDE.md](./SETUP_GUIDE.md#-生产环境检查清单) 中的生产清单

---

## 📊 项目统计

- 📁 总文件数：50+ 个
- 🎯 Applications 总数：15+ 个
- 📚 文档行数：3000+ 行
- 🏗️ 基础设施组件：10+ 个

---

## 🎉 欢迎加入

现在一切就绪。你已经拥有一个**企业级的 GitOps 管理平台**！

**下一步** → 运行 `bash init.sh` 🚀

---

**项目**: ArgoCD Apps - App of Apps GKE 管理平台  
**文档版本**: 1.0  
**最后更新**: 2026-05-17
