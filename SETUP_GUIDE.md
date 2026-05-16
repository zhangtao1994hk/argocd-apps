# 🚀 集群初始化完整指南

本文档提供一步步的集群初始化指南，包含详细的验证步骤和常见问题解决。

---

## 📋 前置条件检查清单

```bash
# 1. 检查 kubectl 是否已安装
kubectl version --client

# 2. 检查 kubeconfig 是否正确配置
kubectl cluster-info

# 3. 检查连接是否正常
kubectl get nodes

# 4. 检查有无必要权限（需要 cluster-admin）
kubectl auth can-i create clusterrolebinding --as=system:serviceaccount:default:default
```

---

## 🔧 详细的初始化步骤

### 步骤 1：环境准备

```bash
# 创建项目目录
mkdir -p argocd-gke-platform
cd argocd-gke-platform

# Clone 本项目
git clone https://github.com/zhangtao1994hk/argocd-apps.git
cd argocd-apps

# 设置环境变量（可选）
export ARGOCD_DOMAIN="argocd.zhangtao1994hk.asia"
export GKE_CLUSTER_NAME="my-gke-cluster"
export GKE_ZONE="asia-east1-a"
export GKE_PROJECT_ID="my-gcp-project"
```

### 步骤 2：验证 GKE 集群

```bash
# 查看集群信息
kubectl cluster-info

# 查看所有节点
kubectl get nodes -o wide

# 验证集群资源
kubectl top nodes  # 如果返回错误，等待 metrics-server 初始化

# 查看 API 服务器状态
kubectl get componentstatus
```

### 步骤 3：运行初始化脚本

```bash
# 给脚本执行权限
chmod +x init.sh

# 运行初始化
bash init.sh

# 该脚本会完成以下操作：
# 1. 添加 ArgoCD Helm 仓库
# 2. 安装 ArgoCD（包含 Prometheus 集成）
# 3. 等待部署完成
# 4. 显示访问信息
```

**初始化过程预计时间**: 2-3 分钟

---

## ✅ 验证 ArgoCD 安装

### 检查 1：验证所有 Pod 都在运行中

```bash
# 查看 argocd 命名空间中的所有 Pod
kubectl get pods -n argocd

# 预期输出应包含：
# - argo-cd-argocd-server (Deployment)
# - argo-cd-argocd-controller-manager (Deployment)
# - argo-cd-argocd-repo-server (Deployment)  
# - argo-cd-argocd-redis (StatefulSet)
# - argo-cd-argocd-application-controller (Deployment)
```

### 检查 2：验证 Service 已创建

```bash
# 查看 ArgoCD 的 Service
kubectl get svc -n argocd

# 关键的 Service：
# - argo-cd-argocd-server: ClusterIP (UI 和 API)
# - argo-cd-argocd-redis: ClusterIP (缓存)
# - argo-cd-argocd-repo-server: ClusterIP (Git 仓库访问)
```

### 检查 3：验证 ServiceMonitor 已创建（Prometheus 集成）

```bash
# 查看是否成功创建了 ServiceMonitor
kubectl get servicemonitor -n argocd

# 预期输出应包含 ArgoCD 相关的 ServiceMonitor
# 可以在 Prometheus 中查看这些指标

# 验证 Prometheus 能访问 ArgoCD 指标
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
# 访问 http://localhost:9090
# 搜索 "argocd_" 前缀的指标
```

### 检查 4：访问 ArgoCD UI

#### 方式 1：通过已配置的域名（如果 DNS 解析正确）

```bash
# 打开浏览器访问
https://argocd.zhangtao1994hk.asia

# 登录凭证
# 用户名: admin
# 密码: Laiye@2026
```

#### 方式 2：通过 Port Forward（推荐本地测试）

```bash
# 端口转发
kubectl port-forward svc/argo-cd-argocd-server 8080:443 -n argocd

# 打开浏览器
https://localhost:8080

# 接受自签名证书警告（开发环境）
```

#### 方式 3：通过 kubectl proxy

```bash
# 启动 proxy
kubectl proxy

# 访问
http://localhost:8001/api/v1/namespaces/argocd/services/argo-cd-argocd-server/proxy/
```

### 检查 5：验证 ArgoCD CLI 连接

```bash
# 安装 argocd CLI（如果还未安装）
# macOS
brew install argocd

# Linux
curl -sLO https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd-linux-amd64
sudo mv argocd-linux-amd64 /usr/local/bin/argocd

# 登录到 ArgoCD
argocd login localhost:8080 --insecure --username admin --password Laiye@2026

# 查看集群信息
argocd cluster list

# 查看应用列表（初始化后为空）
argocd app list
```

---

## 🎯 初始化后的下一步

### 步骤 1：修改默认密码（强烈推荐）

```bash
# 使用 CLI 修改
argocd account update-password \
  --account admin \
  --current-password Laiye@2026 \
  --new-password your-new-strong-password

# 或通过 UI 修改
# 登录 UI → User Info → Change Password
```

### 步骤 2：配置 Git 仓库连接

```bash
# 通过 CLI 添加 Git 仓库
argocd repo add https://github.com/zhangtao1994hk/argocd-apps.git \
  --username your-github-username \
  --password your-github-token

# 或通过 UI
# Settings → Repositories → Connect Repo
```

### 步骤 3：部署根应用（App of Apps）

```bash
# 部署根应用
kubectl apply -f root-app.yaml

# 验证根应用已创建
kubectl get application root-app -n argocd -o wide

# 查看所有自动创建的子应用
kubectl get applications -n argocd

# 在 ArgoCD UI 中查看应用树
# 主页 → Applications → root-app 
# (会显示所有子应用的依赖关系)
```

### 步骤 4：监控应用部署进度

```bash
# 查看应用同步状态
kubectl get application -n argocd -o jsonpath='{.items[*].metadata.name}' | xargs -I {} kubectl get application {} -n argocd -o jsonpath='{.metadata.name}: {.status.sync.status}\n'

# 或使用 argocd CLI
argocd app list

# 查看特定应用的详细信息
argocd app get backend-app

# 实时监控应用状态
watch kubectl get application -n argocd
```

### 步骤 5：验证所有应用均已成功部署

```bash
# 查看所有命名空间中的 Pod
kubectl get pods --all-namespaces

# 查看所有 Service
kubectl get svc --all-namespaces

# 查看所有 Ingress
kubectl get ingress --all-namespaces

# 检查是否有失败的 Pod
kubectl get pods --all-namespaces --field-selector=status.phase=Failed
```

---

## 🔍 常见问题排查

### 问题 1：ArgoCD Pod 无法启动（CrashLoopBackOff）

```bash
# 查看 Pod 日志
kubectl logs -f deployment/argo-cd-argocd-server -n argocd

# 获取详细的 Pod 事件
kubectl describe pod <pod-name> -n argocd

# 常见原因：
# 1. 集群资源不足（CPU/内存）- 增加节点
# 2. PVC 无法绑定 - 检查存储类
# 3. 镜像拉取失败 - 检查镜像仓库凭证
```

### 问题 2：无法访问 ArgoCD UI

```bash
# 检查 Service 是否正确运行
kubectl get svc argo-cd-argocd-server -n argocd

# 检查 Ingress/Loadbalancer
kubectl get ingress -n argocd
kubectl get svc -n argocd -o wide

# 如果使用自定义域名，检查 DNS
nslookup argocd.zhangtao1994hk.asia

# 测试连接（使用 curl，忽略 SSL）
curl -k https://argocd.zhangtao1994hk.asia
```

### 问题 3：应用同步失败

```bash
# 查看应用详细信息
kubectl describe application backend-app -n argocd

# 查看仓库连接错误
kubectl logs -f deployment/argo-cd-argocd-repo-server -n argocd

# 检查 Git 凭证是否正确
kubectl get secret -n argocd | grep repository

# 常见原因：
# 1. Git SSH 密钥未正确配置
# 2. 仓库 URL 错误
# 3. 所需的命名空间未创建
```

### 问题 4：Prometheus 无法收集 ArgoCD 指标

```bash
# 检查 ServiceMonitor 是否存在
kubectl get servicemonitor -n argocd

# 检查 Prometheus 配置
kubectl get prometheus -n monitoring -o yaml | grep -A 10 serviceMonitorSelector

# 验证 ArgoCD 指标端点是否可访问
kubectl port-forward svc/argo-cd-argocd-metrics 8082 -n argocd
curl http://localhost:8082/metrics

# 检查 kube-prometheus-stack 是否正确标记了 ServiceMonitor
kubectl get servicemonitor argo-cd-argocd-metrics -n argocd -o yaml | grep release
```

---

## 📊 初始化后的核心组件

### ArgoCD 的核心组件

```
argo-cd-argocd-server
  └─ Kubernetes API Server 和 UI 服务

argo-cd-argocd-controller-manager
  └─ 主控制器，处理应用同步逻辑

argo-cd-argocd-repo-server
  └─ Git 仓库访问和 Kubernetes 清单解析

argo-cd-argocd-redis
  └─ 缓存和会话存储

argo-cd-argocd-application-controller
  └─ 应用状态监控（可选）
```

### 初始化后的文件

```bash
# 创建的主要资源
kubectl get all -n argocd

# 创建的自定义资源
kubectl get applicationset,application -n argocd

# 创建的配置
kubectl get cm,secret -n argocd
```

---

## 🏭 生产环境检查清单

部署到生产环境前，完成以下检查：

- [ ] 修改默认管理员密码
- [ ] 启用 HTTPS/TLS 证书（移除 `--insecure`）
- [ ] 配置 OAuth2 或 LDAP 认证
- [ ] 启用 RBAC 权限控制
- [ ] 配置网络策略
- [ ] 设置资源限制和请求
- [ ] 配置持久化存储备份
- [ ] 启用审计日志
- [ ] 配置监控告警
- [ ] 设置 Git 仓库备份和 webhook

---

## 📈 监控和日志

### 查看 ArgoCD 日志

```bash
# 实时日志
kubectl logs -f deployment/argo-cd-argocd-server -n argocd

# 特定组件日志
kubectl logs -f deployment/argo-cd-argocd-controller-manager -n argocd
kubectl logs -f deployment/argo-cd-argocd-repo-server -n argocd

# 查看历史日志（如果 Pod 已重启）
kubectl logs deployment/argo-cd-argocd-server -n argocd --previous
```

### 查看 ArgoCD 指标

```bash
# Prometheus 查询
# 打开 Prometheus UI：kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
# 查询以下指标：
# - argocd_app_info
# - argocd_app_sync_duration_seconds
# - argocd_server_http_request_duration_seconds
# - argocd_reconcile_duration_seconds
```

### 查看 ArgoCD 事件

```bash
# Kubernetes 事件
kubectl get events -n argocd --sort-by='.lastTimestamp'

# 实时监控
kubectl get events -n argocd -w
```

---

## 🎉 初始化完成！

此时，你的 GKE 集群上应该已经有：

✅ **ArgoCD 完整部署**
  - UI 服务正在运行
  - Git 仓库连接就绪
  - webhooks 可配置

✅ **Prometheus 集成**
  - ArgoCD 指标已导出
  - ServiceMonitor 已创建
  - 可在 Grafana 中查看

✅ **准备好部署应用**
  - 运行 `kubectl apply -f root-app.yaml` 即可部署所有应用
  - 所有子应用将自动同步

**下一步**：[部署应用 (App of Apps)](../README.md#-初始化-root-app应用-of-apps)

