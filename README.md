<div align="center">

# 🚀 ArgoCD Apps — Cloud-Native Observability Stack

![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-orange?style=for-the-badge&logo=argo)
![Kubernetes](https://img.shields.io/badge/Kubernetes-GKE-blue?style=for-the-badge&logo=kubernetes)
![Grafana](https://img.shields.io/badge/Grafana-LGTM-F46800?style=for-the-badge&logo=grafana)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Collector-425CC7?style=for-the-badge&logo=opentelemetry)

**一套基于 GitOps 的云原生全链路可观测性平台，覆盖日志、指标与链路追踪。**

</div>

---

## 📖 项目简介

本项目通过 **ArgoCD** 实现 GitOps 自动化部署，在 Kubernetes（GKE）集群上构建了一套完整的 **LGTM 可观测性栈**，并集成了 **Argo Rollouts** 实现渐进式发布能力。所有配置均以代码形式管理，推送即部署，无需手动操作集群。

本项目采用 **App of Apps** 模式管理所有子应用——只需部署一个根 Application，ArgoCD 便会自动递归发现并部署 `applications/` 目录下的所有子应用。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                    (Single Source of Truth)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ GitOps Sync
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        ArgoCD                                │
│              (Continuous Deployment Controller)              │
│                                                              │
│   Root App  ──►  applications/  ──►  子 Application 清单    │
└──────┬──────────┬────────┬──────────┬───────────┬───────────┘
       │          │        │          │           │
       ▼          ▼        ▼          ▼           ▼
    Prometheus   Loki   Tempo   OTel Collector  Argo Rollouts
    (Metrics)  (Logs) (Traces)  (Data Gateway)  (Progressive
                                                 Delivery)
       └──────────┴────────┴──────────┘
                      │
                      ▼
                  Grafana
             (Unified Dashboard)
```

### 数据流向

```
App (OTel SDK)  ──────────►  OTel Collector  ──►  Tempo      (Traces)
                                              └──►  Prometheus (Metrics)

App (Stdout)    ──►  Promtail  ──────────────────►  Loki       (Logs)

All Data  ──────────────────────────────────────►  Grafana    (Visualization)
```

---

## 🧩 核心组件

| 组件 | 版本/方式 | 职责 |
|:---|:---|:---|
| **ArgoCD** | GitOps Controller | 监听 Git 仓库，自动同步集群状态 |
| **Prometheus** | kube-prometheus-stack | 采集并存储 Kubernetes 及应用指标 |
| **Loki** | Helm Chart | 日志聚合存储，支持 TraceID 关联 |
| **Promtail** | DaemonSet | 采集节点日志并推送至 Loki |
| **Tempo** | Helm Chart | 分布式链路追踪存储 |
| **OTel Collector** | Deployment | 统一接收 OTLP 数据并分流路由 |
| **Grafana** | 内置于 kube-prometheus-stack | 统一可视化仪表盘 |
| **Argo Rollouts** | Helm Chart | 渐进式发布（Canary / Blue-Green） |
| **Backend App** | 自定义应用 | 示例后端服务，集成 OTel SDK |
| **Frontend App** | 自定义应用 | 示例前端服务，无侵入埋点 |

---

## 📁 目录结构

```
argocd-apps/
├── applications/                  # ArgoCD Application 定义清单（由 Root App 管理）
│   ├── argocd-monitor.yaml        # ArgoCD 自身监控
│   ├── argorollouts-app.yaml      # Argo Rollouts 渐进式发布
│   ├── backend-app.yaml           # 后端应用
│   ├── loki-app.yaml              # 日志存储
│   ├── otel-collector-app.yaml    # OpenTelemetry 数据网关
│   ├── prometheus-app.yaml        # 指标监控栈
│   ├── promtail-app.yaml          # 日志采集 Agent
│   └── tempo-app.yaml             # 链路追踪存储
│
├── infrastructure/                # Helm values 配置文件
│   ├── loki/                      # Loki 配置
│   ├── prometheus/                # Prometheus 配置
│   └── promtail/                  # Promtail 配置
│
├── grafana-dashboards/            # Grafana 仪表盘 JSON
│   ├── kustomization.yaml         # Kustomize 配置
│   ├── lgtm-dashboard.json        # LGTM 全栈仪表盘
│   └── node-exporter-full.json    # Node 资源监控仪表盘
│
├── argo-rollouts/                 # Argo Rollouts Helm 配置
├── argocd-monitor/                # ArgoCD 监控配置
├── backend/                       # 后端应用 K8s 清单
├── frontend/                      # 前端应用 K8s 清单
├── base/                          # Kustomize base 配置
├── overlays/                      # Kustomize overlays（环境差异）
├── nginx-demo/                    # Nginx 示例应用
└── README.md
```

---

## ⚡ 快速开始

### 前置条件

- Kubernetes 集群（推荐 GKE）已就绪
- 已安装并配置 `kubectl`
- 已安装 ArgoCD（`argocd` CLI）
- 已安装 `helm` v3.0+

### 1. 安装 ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 2. 部署根 Application（App of Apps）

本项目采用 **App of Apps** 模式，只需 apply 一个根 Application，ArgoCD 会自动递归发现并部署 `applications/` 目录下的所有子应用，无需逐一手动操作。

```bash
kubectl apply -f root-app.yaml -n argocd
```

> 部署完成后，ArgoCD 将自动同步以下所有子应用：
> - `prometheus-app` — 指标监控栈
> - `loki-app` — 日志存储
> - `promtail-app` — 日志采集
> - `tempo-app` — 链路追踪
> - `otel-collector-app` — 数据网关
> - `argorollouts-app` — 渐进式发布控制器
> - `backend-app` — 后端业务应用

### 3. 访问服务

| 服务 | 访问地址 | 说明 |
|:---|:---|:---|
| **Grafana** | `http://grafana.local` | 需配置本地 hosts |
| **ArgoCD UI** | `https://argocd.local` | 需配置本地 hosts |
| **Prometheus** | `prometheus-kube-prometheus-stack-prometheus:9090` | 集群内部 |
| **Loki** | `loki-app:3100` | 集群内部 |
| **Tempo** | `tempo-app:3200` | 集群内部 |
| **OTel Collector** | `otel-collector:4317` (gRPC) / `4318` (HTTP) | 集群内部 |

---

## 📊 Grafana 仪表盘

项目内置两套仪表盘，通过 Kustomize ConfigMap 自动挂载至 Grafana：

| 仪表盘 | 文件 | 内容 |
|:---|:---|:---|
| **LGTM Full Stack** | `lgtm-dashboard.json` | 日志、指标、链路追踪联动视图 |
| **Node Exporter Full** | `node-exporter-full.json` | 节点 CPU / 内存 / 磁盘 / 网络 |

### 日志与链路追踪关联

在 Grafana 中配置了 `derivedFields`，当应用日志包含 `trace_id=...` 字段时，点击日志详情中的 TraceID 即可**一键跳转**至 Tempo 对应的链路追踪页面。

---

## 🔄 渐进式发布（Argo Rollouts）

本项目集成 **Argo Rollouts**，支持以下发布策略：

- **Canary Release**：逐步将流量切换至新版本
- **Blue-Green Deployment**：零停机蓝绿切换

```bash
# 查看 Rollout 状态
kubectl argo rollouts get rollout <rollout-name> -n <namespace>

# 手动推进 Canary 步骤
kubectl argo rollouts promote <rollout-name> -n <namespace>
```

---

## 🔧 配置更新

所有配置均通过 Git 管理，修改后推送即可触发 ArgoCD 自动同步：

```bash
# 修改对应组件的 values.yaml
vim infrastructure/prometheus/values.yaml

# 提交并推送
git add .
git commit -m "update: adjust prometheus retention to 30d"
git push

# ArgoCD 将在下一个同步周期自动应用变更（默认 3 分钟）
# 或手动触发同步
argocd app sync prometheus-app
```

---

## 🛠️ 常见问题

### ConfigMap 超过 262KB 限制

Grafana Dashboard ConfigMap 过大时，`kubectl apply` 会因 annotation 超限失败。解决方案：

```yaml
# 在 ArgoCD Application 中添加
spec:
  syncPolicy:
    syncOptions:
      - Replace=true
      - ServerSideApply=true
```

### ArgoCD 同步失败

```bash
# 查看同步详情
argocd app get <app-name>

# 强制同步
argocd app sync <app-name> --force
```

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交变更：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

---

## 🙏 致谢

本项目的构建与运行离不开以下平台和工具的强力支持：

### ☁️ Google Cloud

感谢 **Google Cloud** 提供稳定、高性能的 **GKE（Google Kubernetes Engine）** 托管集群服务，使本项目得以在生产级 Kubernetes 环境中顺畅运行。Google Cloud 强大的基础设施为整个可观测性平台提供了坚实的底座。

> 🔗 [cloud.google.com](https://cloud.google.com)

### 🤖 Claude AI (Anthropic)

感谢 **Claude AI** 在项目开发过程中提供的智能辅助，包括架构设计建议、配置调试、问题排查以及文档编写等方面的支持。AI 辅助极大地提升了开发效率与代码质量。

> 🔗 [claude.ai](https://claude.ai)

---

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

Made with ❤️ by [zhangtao1994hk](https://github.com/zhangtao1994hk)

⭐ 如果本项目对你有帮助，欢迎 Star！

</div>
