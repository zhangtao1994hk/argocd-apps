# Cloud-Native Observability Stack (LGTM + GitOps)

这是一个基于 **GitOps (ArgoCD)** 部署的云原生可观测性平台。它实现了日志、指标、链路追踪的三位一体，提供全链路的监控与排错能力。

## 架构概览

本系统采用 **LGTM** 栈，并通过 OpenTelemetry 进行统一的数据采集：

*   **Loki**: 日志聚合存储。
*   **Grafana**: 统一的可视化仪表盘。
*   **Tempo**: 分布式链路追踪存储。
*   **Prometheus**: 指标数据存储。
*   **OTel Collector**: 数据统一收集、处理与路由中心。

### 数据流向
`App (OTel SDK)` -> `OTel Collector` -> `[Tempo (Traces) / Prometheus (Metrics)]`
`App (Stdout)` -> `Promtail` -> `Loki (Logs)`

## 目录结构

*   `/applications/`: ArgoCD 应用定义文件 (`Application` manifests)。
*   `/infrastructure/`: 各个组件的 Helm `values.yaml` 配置文件。
*   `/frontend/`: 示例应用程序（带 OpenTelemetry 无侵入埋点）。

## 核心组件与配置

| 组件 | 功能 | 部署方式 |
| :--- | :--- | :--- |
| **ArgoCD** | GitOps 控制器 | 负责集群自动化部署 |
| **Prometheus** | 指标监控 | 通过 kube-prometheus-stack 部署 |
| **Loki** | 日志采集与存储 | 存储应用日志，支持 TraceID 关联 |
| **Tempo** | 链路追踪 | 基于对象存储/本地存储的 Trace 存储 |
| **OTel Collector** | 统一数据网关 | 接收 OTLP 数据并分流 |

## 快速开始

### 1. 部署顺序
虽然 ArgoCD 通过 `SyncWaves` 管理，但建议按以下逻辑查看状态：
1. 确保集群已安装 `ArgoCD`。
2. 部署 `kube-prometheus-stack` (合并版，已包含 CRDs)。
3. 部署 `loki-app`。
4. 部署 `tempo-app`。
5. 部署 `otel-collector-app`。

### 2. 访问方式
*   **Grafana**: `http://grafana.local` (需配置本地 hosts)
*   **Prometheus**: 内部服务 `prometheus-kube-prometheus-stack-prometheus:9090`
*   **Loki**: 内部服务 `loki-app:3100`
*   **Tempo**: 内部服务 `tempo-app:3200`

### 3. 如何关联日志与链路
在 Grafana 中，我们配置了 `derivedFields`。只要你的应用日志中包含 `trace_id=...`，在日志详情页点击 ID 即可直接跳转到对应的 Tempo 链路追踪页面。

## 维护手册

### 如何更新配置
修改 `/infrastructure/` 下对应的 `values.yaml`，然后提交并推送：
```bash
git add .
git commit -m "update: config change"
git push
