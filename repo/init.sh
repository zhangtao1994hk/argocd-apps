#!/bin/bash
set -e  # 发生错误时立即退出

################################################################################
# ArgoCD 集群初始化脚本
# 项目: App of Apps 模式 GitOps 平台（管理 GKE 集群）
# 作用: 一键部署 ArgoCD 并配置完整的可观测性和自动化
################################################################################

echo "📦 开始初始化 ArgoCD 集群..."
echo ""

################################################################################
# 第 1 步：添加 ArgoCD Helm 仓库
################################################################################
echo "▶️  步骤 1: 添加 ArgoCD Helm 仓库..."
helm repo add argo-cd https://argoproj.github.io/argo-helm
helm repo update
echo "✅ Helm 仓库添加成功"
echo ""

################################################################################
# 第 2 步：安装 ArgoCD 及其完整配置
################################################################################
echo "▶️  步骤 2: 安装 ArgoCD（包含 Prometheus 集成...）"
echo ""

helm upgrade --install argo-cd argo-cd/argo-cd \
  # 基础配置
  --namespace argocd \
  --create-namespace \
  \
  # Web UI 配置
  --set server.extraArgs={--insecure} \
    `# ⚠️  非生产环境：允许 HTTP。生产环境应启用 HTTPS/TLS` \
  --set server.config.url="https://argocd.zhangtao1994hk.asia" \
    `# ArgoCD UI 访问域名` \
  \
  # 控制器指标收集（用于 Prometheus 监控）
  --set controller.metrics.enabled=true \
  --set controller.metrics.serviceMonitor.enabled=true \
  --set controller.metrics.serviceMonitor.additionalLabels.release="kube-prometheus-stack" \
    `# 应用控制器导出 Prometheus 兼容的指标` \
  \
  # API 服务器指标收集
  --set server.metrics.enabled=true \
  --set server.metrics.serviceMonitor.enabled=true \
  --set server.metrics.serviceMonitor.additionalLabels.release="kube-prometheus-stack" \
    `# API 服务器导出指标（同步状态、API 调用等）` \
  \
  # 仓库服务器指标收集
  --set repoServer.metrics.enabled=true \
  --set repoServer.metrics.serviceMonitor.enabled=true \
  --set repoServer.metrics.serviceMonitor.additionalLabels.release="kube-prometheus-stack" \
    `# Git 仓库同步导出指标` \
  \
  # 管理员认证配置
  --set-string configs.secret.argocdServerAdminPassword='$2y$05$yhe/1TVwGL0QraCYziBz3.FocWUf8n04WzrstF09Fyfu3/St45mci' \
    `# 加密的管理员密码（默认: admin/Laiye@2026）` \
  --set-string configs.secret.argocdServerAdminPasswordMtime="$(date +%FT%TZ)" \
    `# 密码修改时间戳`

echo ""
echo "✅ ArgoCD 安装完成"
echo ""

################################################################################
# 第 3 步：等待 ArgoCD 部署完成
################################################################################
echo "▶️  步骤 3: 等待 ArgoCD 部署完成（约 30-60 秒）..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/argo-cd-argocd-server -n argocd 2>/dev/null || true

echo "✅ ArgoCD 已就绪"
echo ""

################################################################################
# 第 4 步：显示访问信息
################################################################################
echo "▶️  步骤 4: 显示访问信息"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 ArgoCD 安装成功!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📍 访问方式:"
echo "  UI 地址: https://argocd.zhangtao1994hk.asia"
echo "  本地访问: kubectl port-forward svc/argo-cd-argocd-server 8080:443 -n argocd"
echo ""
echo "🔐 默认凭证:"
echo "  用户名: admin"
echo "  密码: Laiye@2026"
echo ""
echo "📊 监控集成:"
echo "  • ArgoCD 指标已导出到 Prometheus ServiceMonitor"
echo "  • 可在 Grafana 中查看来自 kube-prometheus-stack 的仪表板"
echo ""
echo "📖 后续步骤:"
echo "  1. 检查所有 Pod 状态:"
echo "     kubectl get pods -n argocd"
echo ""
echo "  2. 部署根应用（App of Apps）:"
echo "     kubectl apply -f root-app.yaml"
echo ""
echo "  3. 验证应用部署:"
echo "     kubectl get applications -n argocd"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 第 5 步（可选）：初始化 App of Apps
################################################################################
# 取消下面这行注释来自动部署 root-app
# echo "▶️  步骤 5: 部署 Root Application（App of Apps 模式）..."
# kubectl apply -f root-app.yaml
# echo "✅ 根应用已部署，所有子应用将自动开始同步"
################################################################################
