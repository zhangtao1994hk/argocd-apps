# 🏗️ ArgoCD Apps - App of Apps 多集群管理平台

一个生产级的 **App of Apps** 模式 GitOps 平台，用 ArgoCD 管理 Google Kubernetes Engine (GKE) 集群中的所有应用组件。

## 📋 项目概述

本项目采用 **App of Apps** 模式（也称为 Applicationset 模式），通过一个根 Application (`root-app.yaml`) 管理所有子应用，实现：

- ✅ **声明式基础设施** - Kubernetes 资源即代码
- ✅ **GitOps 工作流** - Git 是单一信源，自动同步到集群
- ✅ **分层应用管理** - 微服务、基础设施、监控分离部署
- ✅ **自动化和自愈** - 支持 Rollouts 金丝雀部署、自动回滚
- ✅ **完整的可观测性** - Prometheus、Grafana、Loki、Tempo 集成
- ✅ **多应用编排** - 统一管理 15+ 个应用

---

## 🚀 快速开始

### 前置条件

- GKE 集群已启动并可访问（kubeconfig 已配置）
- `helm` 和 `kubectl` 已安装
- 对 Kubernetes 和 Git 有基本了解

### 初始化步骤（5 分钟）

#### 1️⃣ 添加 ArgoCD Helm 仓库

```bash
helm repo add argo-cd https://argoproj.github.io/argo-helm
helm repo update
```

#### 2️⃣ 安装 ArgoCD 并配置

```bash
bash init.sh
```

**init.sh 中的关键配置**（自动执行）：

```yaml
# Helm 安装配置
- 命名空间: argocd（新建）
- 不安全模式: --insecure（适合测试环境）
- 服务地址: https://argocd.zhangtao1994hk.asia
- 管理员账密: admin / Laiye@2026
- Prometheus 集成: ServiceMonitor for kube-prometheus-stack
- 控制器、服务器、仓库服务器都启用了指标收集
```

#### 3️⃣ 等待 ArgoCD 部署完成

```bash
kubectl wait --for=condition=available --timeout=300s \
  deployment/argo-cd-argocd-server -n argocd

# 查看部署状态
kubectl get all -n argocd
```

#### 4️⃣ 初始化 Root App（App of Apps）

```bash
kubectl apply -f root-app.yaml
```

**结果**：root-app 会自动：
- 发现 `applications/` 目录中的所有 Application
- 自动部署所有子应用（如果启用了自动同步）
- 代级删除管理所有依赖资源

#### 5️⃣ 验证所有应用已部署

```bash
kubectl get applications -n argocd

# 查看具体应用状态
kubectl get applications -n argocd -o wide
```

---

## 🏛️ 项目架构

### App of Apps 架构模式

```
┌─────────────────────────────────────────────────────┐
│         root-app (Root Application)                 │
│   指向: applications/ 目录                           │
│   同步策略: 自动删除已移除的资源                     │
└────────────────┬────────────────────────────────────┘
                 │ 自动发现和管理
                 │
    ┌────────────┴─────────────────────────────────┐
    │ 15+ 个子应用                                  │
    │                                              │
    ├─ Infrastructure                             │
    │  ├─ argocd-monitor-app                      │
    │  ├─ kube-prometheus-stack-app               │
    │  ├─ loki-app                                │
    │  ├─ tempo-app                               │
    │  ├─ otel-collector-app                      │
    │  ├─ mysql-app                               │
    │  ├─ redis-app                               │
    │  ├─ kafka-app                               │
    │  ├─ argo-rollouts-app                       │
    │  └─ ...                                     │
    │                                              │
    ├─ Platform Services                          │
    │  ├─ backend-app                             │
    │  ├─ dao-app                                 │
    │  └─ frontend-app                            │
    │                                              │
    └─ Networking                                 │
       ├─ traefik-app (Ingress)                   │
       ├─ ingress-app                             │
       └─ prometheus-ingress                      │
└─────────────────────────────────────────────────────┘
```

### 三层架构设计

```
┌─────────────────────────────────────────────┐
│        Application Layer (应用层)            │
│                                             │
│  ┌──────────────┬────────┬──────────────┐   │
│  │   Backend    │  DAO   │  Frontend    │   │
│  │ (REST APIs)  │(DB Layer) │(Vue.js)  │   │
│  └──────────────┴────────┴──────────────┘   │
├─────────────────────────────────────────────┤
│     Infrastructure Layer (基础设施层)        │
│                                             │
│  ┌──────┬──────┬───────┬────────┬─────────┐   │
│  │MySQL │Redis │Kafka  │ArgoCD  │Traefik  │   │
│  │(DB)  │(Cache)│(MQ)  │(GitOps)│(Ingress)│   │
│  └────────┴────────┴─────────┴──────────┘   │
├─────────────────────────────────────────────┤
│   Observability Layer (可观测性层)           │
│                                             │
│  ┌──────────┬────────────┬────────┬──────┐  │
│  │Prometheus│  Grafana   │  Loki  │Tempo │  │
│  │(Metrics) │(Dashboards)│(Logs)  │(APM) │  │
│  └──────────┴────────────┴────────┴──────┘  │
└─────────────────────────────────────────────┘
```

### Git 仓库结构

```
argocd-apps/
│
├── init.sh                          ← 集群初始化脚本
├── root-app.yaml                    ← Root Application (App of Apps)
├── schema.sql & init-data.sql       ← 数据库初始化
│
├── applications/                    ← 所有 ArgoCD Application 定义
│   ├── backend-app.yaml
│   ├── frontend-app.yaml
│   ├── prometheus-app.yaml
│   ├── grafana-dashboards-app.yaml
│   ├── mysql-app.yaml
│   ├── redis-app.yaml
│   ├── kafka-app.yaml
│   ├── loki-app.yaml
│   ├── tempo-app.yaml
│   ├── otel-collector-app.yaml
│   ├── argocd-monitor.yaml
│   ├── argo-rollouts-app.yaml
│   ├── traefik-app.yaml
│   ├── ingress-app.yaml
│   ├── prometheus-ingress.yaml
│   └── [更多应用...]
│
├── infrastructure/                  ← 基础设施 Helm 配置
│   ├── argo-rollouts/              (Argo Rollouts 金丝雀部署)
│   ├── kube-prometheus-stack/      (Prometheus + Grafana)
│   ├── loki/                       (日志存储)
│   ├── promtail/                   (日志收集)
│   ├── tempo/                      (链路追踪存储)
│   ├── otel-collector/ (optional)  (OpenTelemetry 中心)
│   ├── redis/                      (Redis 缓存)
│   └── private-mysql-chart/        (MySQL 数据库)
│
├── base/                            ← 应用基础配置 (Kustomize)
│   ├── backend-rollout.yaml
│   ├── frontend-rollout.yaml
│   ├── dao-rollout.yaml
│   ├── hpa.yaml
│   ├── backend-service.yaml
│   ├── frontend-service.yaml
│   └── kustomization.yaml
│
├── overlays/                        ← 环境特定配置 (Kustomize)
│   └── k3s/
│       └── kustomization.yaml       (GKE 特定配置)
│
├── backend/                         ← 后端应用代码
│   ├── app.py                       (Flask 应用)
│   ├── requirements.txt             (Python 依赖)
│   └── Dockerfile
│
├── frontend/                        ← 前端应用代码
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── dao/                             ← 数据访问层
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── repo/                            ← 初始化脚本及参考配置
│   ├── init.sh
│   └── argocd-values.yaml
│
└── ingress/                         ← Ingress 配置
    ├── traefik.yaml
    ├── frontend-ingress.yaml
    ├── prometheus-ingress.yaml
    └── ...
```

---

## 📊 数据流和工作流

### GitOps 工作流

```
1. 开发者 Push 代码到 Git
           ↓
2. GitHub Actions 构建镜像
           ↓
3. 更新 Git 中的镜像 tag
           ↓
4. ArgoCD 检测到变化
           ↓
5. 自动同步到 Kubernetes
           ↓
6. 新应用在 GKE 部署
```

### 应用通信流

```
用户请求
   ↓
Traefik Ingress
   ↓
Frontend Service (Vue.js)
   ├─→ Backend Service (Python Flask)
   │      ├─→ DAO Service (数据访问)
   │      │      ├─→ MySQL (数据存储)
   │      │      └─→ Redis (缓存)
   │      ├─→ Kafka (异步消息)
   │      └─→ OpenTelemetry Collector
   │              ├─→ Prometheus (指标)
   │              └─→ Tempo (链路追踪)
   │
   └─→ Prometheus Scrape
          ↓
       Grafana Dashboard (可视化)
```

---

## 🔧 关键配置详解

### init.sh 配置解析

```bash
# 1. Helm 仓库
helm repo add argo-cd https://argoproj.github.io/argo-helm

# 2. 核心配置
--set server.config.url="https://argocd.zhangtao1994hk.asia"
    └─ ArgoCD UI 访问地址

--set server.extraArgs={--insecure}
    └─ 使用 HTTP（生产环境应改为 HTTPS + TLS）

# 3. 指标收集集成
--set controller.metrics.enabled=true
--set controller.metrics.serviceMonitor.enabled=true
--set controller.metrics.serviceMonitor.additionalLabels.release="kube-prometheus-stack"
    └─ ArgoCD 控制器指标导出到 Prometheus

# 4. 管理员认证
--set-string configs.secret.argocdServerAdminPassword='$2y$05$yhe/1TVwGL0QraCYziBz3.FocWUf8n04WzrstF09Fyfu3/St45mci'
    └─ admin 用户的加密密码
    └─ 默认用户名: admin，密码: Laiye@2026
```

### Root App 配置

```yaml
# root-app.yaml 关键字段
metadata:
  finalizers:
    - resources-finalizer.argocd.argoproj.io  # 删除 root-app 时级联删除所有子应用

spec:
  source:
    path: applications/  # 自动发现该目录下的所有 Application

  syncPolicy:
    automated:
      prune: true       # 自动删除 Git 中已移除的资源
      selfHeal: true    # 自动修复集群与 Git 的差异
    syncOptions:
      - CreateNamespace=true  # 自动创建必要的命名空间
```

---

## 🛠️ 常用命令

### 查看应用状态

```bash
# 查看所有应用
kubectl get applications -n argocd

# 查看特定应用的详细信息
kubectl describe application backend-app -n argocd

# 查看应用同步状态
kubectl get application -n argocd -o json | jq '.items[].status.sync.status'
```

### 手动同步应用

```bash
# 同步单个应用
argocd app sync backend-app

# 同步所有应用
argocd app sync -l app=all

# 强制同步（忽略 diff）
argocd app sync backend-app --force
```

### 访问 ArgoCD UI

```bash
# Port Forward
kubectl port-forward svc/argo-cd-argocd-server 8080:443 -n argocd

# 访问 UI
https://localhost:8080

# 或使用配置的域名
https://argocd.zhangtao1994hk.asia
```

### 查看应用日志

```bash
# 查看应用控制器日志
kubectl logs -f deployment/argo-cd-argocd-controller-manager -n argocd

# 查看仓库服务器日志
kubectl logs -f deployment/argo-cd-argocd-repo-server -n argocd

# 查看 API 服务器日志
kubectl logs -f deployment/argo-cd-argocd-server -n argocd
```

---

## 📈 监控和可观测性

### 三层可观测性架构

```
应用层
  ├─ 应用日志 → Promtail → Loki
  ├─ 分布式追踪 → OpenTelemetry → Tempo
  └─ 业务指标 → Prometheus
    
基础设施层
  ├─ Node 指标 (CPU, Memory, Disk) → Prometheus
  ├─ Kubernetes 资源指标 → kube-state-metrics
  └─ 网络监控 → Traefik metrics
    
ArgoCD 层
  ├─ 同步状态 → ArgoCD Metrics → Prometheus
  ├─ 应用部署健康状态
  └─ 仓库同步状态
    
可视化
  └─ Grafana Dashboard (展示所有指标)
```

### 常见监控查询

```bash
# 查看集群 Node 信息
kubectl top nodes

# 查看 Pod 资源使用
kubectl top pods -n default

# 查看 ArgoCD 应用同步状态
kubectl get application -n argocd -o jsonpath='{.items[*].status.sync.status}'

# 查看所有失败的 Pod
kubectl get pods --all-namespaces --field-selector=status.phase=Failed
```

---

## 🔐 安全最佳实践

### 当前配置注意事项

⚠️ **非生产环境配置**：
- `--insecure` 标志允许 HTTP 连接
- 默认管理员密码未更改
- ServiceMonitor 自动暴露 Prometheus 指标

✅ **生产环境建议**：

```bash
# 1. 启用 HTTPS/TLS
--set server.certificate.enabled=true

# 2. 配置 RBAC
--set server.rbac.enabled=true

# 3. 启用网络策略
--set server.networkPolicy.enabled=true

# 4. 修改默认管理员密码
argocd account update-password

# 5. 配置 SSO (OAuth2, LDAP等)
--set server.config.oidc.enabled=true
```

---

## 🚨 故障排查

### ArgoCD 无法连接到 Git 仓库

```bash
# 查看仓库连接日志
kubectl logs -f deployment/argo-cd-argocd-repo-server -n argocd

# 检查 Git 凭证
kubectl get secret -n argocd | grep repository

# 验证仓库 URL 和分支
kubectl get application backend-app -n argocd -o yaml | grep -A 5 "source:"
```

### 应用同步卡住

```bash
# 查看同步状态
kubectl describe application backend-app -n argocd

# 强制刷新同步状态
kubectl patch application backend-app -n argocd \
  --type merge -p '{"status":{"reconciledAt":null}}'
```

### Pod 无法启动

```bash
# 查看 Pod 事件
kubectl describe pod <pod-name>

# 查看 Pod 日志
kubectl logs <pod-name>

# 如果日志丢失，查看之前的日志
kubectl logs <pod-name> --previous
```

---

## 📚 项目特色

### ✅ App of Apps 模式

- **单点管理**：通过 root-app 管理所有应用
- **自动发现**：Git 中的新 Application 自动被部署
- **级联删除**：删除 root-app 时自动清理所有资源
- **版本控制**：所有配置都在 Git，支持完整的变更历史

### ✅ 完整的 CI/CD 流水线

- GitHub Actions 自动构建镜像
- Git commit 自动触发部署
- 支持金丝雀部署（Argo Rollouts）
- 自动回滚机制

### ✅ 多应用协调

- 15+ 个应用统一管理
- 自动处理依赖关系
- 统一的健康检查和告警

### ✅ 企业级可观测性

- **日志**：Loki + Promtail 集中收集
- **指标**：Prometheus + Grafana 实时仪表板
- **链路追踪**：Tempo + Jaeger 分布式追踪
- **APM**：OpenTelemetry 插装化

---

## 🎯 后续操作

### 短期（初始化后）

1. 修改 ArgoCD 默认管理员密码
   ```bash
   argocd account update-password
   ```

2. 配置 Git 仓库和 SSH 密钥

3. 部署应用（自动通过 root-app）
   ```bash
   kubectl apply -f root-app.yaml
   ```

### 中期（生产部署前）

1. 启用 HTTPS/TLS
2. 配置身份验证（OAuth2/LDAP）
3. 设置网络策略和 RBAC
4. 配置监控告警规则
5. 建立备份和恢复程序

### 长期（运维管理）

1. 定期更新 Helm Chart 版本
2. 监控集群健康状态
3. 优化资源使用和成本
4. 扩展到多集群管理

---

## 📖 相关资源

- [ArgoCD 官方文档](https://argo-cd.readthedocs.io/)
- [App of Apps 模式](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/#app-of-apps-pattern)
- [Kubernetes GitOps 最佳实践](https://cloud.google.com/architecture/devops-patterns-kubernetes-gitops)
- [GKE 管理指南](https://cloud.google.com/kubernetes-engine/docs)

---

## 📞 支持

如有问题，请查看：
1. init.sh 脚本日志
2. ArgoCD 应用同步状态
3. Kubernetes 事件日志：`kubectl get events -n argocd`

**项目准备就绪！🚀**

