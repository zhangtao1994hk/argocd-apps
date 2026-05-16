# 🎯 快速参考卡 (Cheat Sheet)

## ⚡ 5 分钟快速部署

```bash
# 1. 克隆项目
git clone https://github.com/zhangtao1994hk/argocd-apps.git
cd argocd-apps

# 2. 运行初始化脚本
bash init.sh

# 3. 等待 2-3 分钟，然后部署根应用
kubectl apply -f root-app.yaml

# 4. 验证部署
kubectl get applications -n argocd
```

---

## 🔐 常用命令

### 访问 ArgoCD

```bash
# Port Forward 到本地（推荐）
kubectl port-forward svc/argo-cd-argocd-server 8080:443 -n argocd
# 访问 https://localhost:8080 (接受自签名证书)

# 通过域名（如果配置了 DNS）
https://argocd.zhangtao1994hk.asia

# 默认凭证
# 用户名: admin
# 密码: Laiye@2026
```

### 查看各个应用

```bash
# 所有应用
argocd app list

# 应用详情
argocd app get backend-app

# Kubernetes 资源查看
kubectl get application -n argocd
kubectl get application -n argocd -o wide
```

### 应用管理

```bash
# 同步单个应用
argocd app sync backend-app

# 同步所有应用
argocd app sync -l app=all

# 强制同步（忽略 diff）
argocd app sync backend-app --force

# 刷新应用状态
argocd app refresh backend-app

# 删除应用
argocd app delete backend-app
```

### 查看 Pod 状态

```bash
# ArgoCD Pods
kubectl get pods -n argocd

# 所有应用的 Pods
kubectl get pods --all-namespaces

# 搜索失败的 Pods
kubectl get pods --all-namespaces --field-selector=status.phase=Failed
```

### 日志查看

```bash
# ArgoCD 服务器日志
kubectl logs -f deployment/argo-cd-argocd-server -n argocd

# 控制器日志
kubectl logs -f deployment/argo-cd-argocd-controller-manager -n argocd

# 仓库服务器日志
kubectl logs -f deployment/argo-cd-argocd-repo-server -n argocd

# 特定 Pod 日志
kubectl logs -f pod/backend-xxxxxx

# 查看之前的日志（Pod 已重启）
kubectl logs pod/backend-xxxxxx --previous
```

---

## 📊 监控和调试

### 查看集群资源使用

```bash
# Node 资源
kubectl top nodes

# Pod 资源
kubectl top pods -n argocd

# 所有 namespace 的资源
kubectl top pods --all-namespaces
```

### Prometheus 指标查询

```bash
# 端口转发 Prometheus
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090

# 常用查询 (在 Prometheus 中)
# ArgoCD 应用数量
argocd_app_info

# 应用同步时间
argocd_app_sync_duration_seconds

# API 请求耗时
argocd_server_http_request_duration_seconds

# 协调耗时
argocd_reconcile_duration_seconds
```

### Grafana 仪表板

```bash
# 端口转发 Grafana
kubectl port-forward -n monitoring svc/grafana 3000:80

# 访问 http://localhost:3000
# 默认凭证通常在 kube-prometheus-stack 中定义
```

### 事件日志

```bash
# 最近的事件
kubectl get events -n argocd --sort-by='.lastTimestamp'

# 实时监控事件
kubectl get events -n argocd -w

# 特定资源的事件
kubectl describe pod pod-name -n namespace
```

---

## 🔍 故障排查

### 应用同步卡住

```bash
# 查看应用状态
kubectl describe application backend-app -n argocd

# 查看具体错误
kubectl get application backend-app -n argocd -o yaml | grep -A 10 "error\|message"

# 强制刷新
kubectl patch application backend-app -n argocd \
  --type merge -p '{"status":{"reconciledAt":null}}'
```

### Pod 无法启动

```bash
# 查看 Pod 事件（常见错误）
kubectl describe pod pod-name

# 查看 Pod 日志
kubectl logs pod-name

# 查看之前的日志
kubectl logs pod-name --previous

# 进入 Pod shell（调试）
kubectl exec -it pod-name -- /bin/bash
```

### 集群连接问题

```bash
# 测试集群连接
kubectl cluster-info

# 查看节点状态
kubectl get nodes

# 查看组件状态
kubectl get componentstatus

# DNS 检查
kubectl run -it --image=nicolaka/netcat -- bash
# 在 Pod 中运行: nslookup kubernetes.default
```

---

## 🗑️ 清理和重置

### 删除单个应用

```bash
argocd app delete backend-app
# 或
kubectl delete application backend-app -n argocd
```

### 删除所有应用（保留 ArgoCD）

```bash
kubectl delete application -n argocd --all
```

### 完全卸载 ArgoCD

```bash
helm uninstall argo-cd -n argocd
kubectl delete namespace argocd
```

### 完全重置集群

```bash
# 删除所有应用和命名空间
kubectl delete namespace --all

# 或仅删除 app 的命名空间
kubectl delete ns default monitoring argocd
```

---

## 🔐 安全相关

### 修改管理员密码

```bash
# 使用 CLI
argocd account update-password --account admin

# 或通过 Kubernetes secret
kubectl -n argocd patch secret argocd-secret \
  -p '{"data": {"admin.password": "'$(htpasswd -nbBC 10 admin new_password | cut -d: -f2 | base64 -w0)'"}}' \
  -p '{"data": {"admin.passwordMtime": "'$(date +%FT%TZ | base64 -w0)'"}}'
```

### 查看默认凭证

```bash
# 获取初始管理员密码
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

### SSH 密钥配置

```bash
# 创建 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""

# 添加公钥到 GitHub

# 在 ArgoCD 中配置私钥
kubectl create secret generic git-ssh-key \
  --from-file=id_ed25519=$HOME/.ssh/id_ed25519 \
  -n argocd
```

---

## 📋 健康检查清单

### 部署后的验证

```bash
# 1. ArgoCD 所有 Pod 正在运行
kubectl get pods -n argocd | grep Running

# 2. 所有应用已同步
kubectl get application -n argocd -o jsonpath='{.items[*].status.sync.status}'

# 3. 可以访问 UI
curl -k https://localhost:8080/api/version

# 4. Git 仓库已连接
argocd repo list

# 5. 所有 Service 正在运行
kubectl get svc --all-namespaces
```

### 生产环境检查

```bash
# 1. HTTPS/TLS 已启用 (不再使用 --insecure)
# 2. 管理员密码已更改
# 3. RBAC 已配置
# 4. 网络策略已启用
# 5. 监控和告警已设置
# 6. 备份策略已制定
# 7. 高可用已配置（多个副本）
```

---

## 📚 常用链接

- [本项目 README](./README.md) - 项目概览
- [详细初始化指南](./SETUP_GUIDE.md) - 一步步初始化
- [官方 init.sh](./init.sh) - 初始化脚本
- [根应用配置](./root-app.yaml) - App of Apps 根应用
- [ArgoCD 官方文档](https://argo-cd.readthedocs.io/)
- [GKE 文档](https://cloud.google.com/kubernetes-engine/docs)

---

## ⚡ 快速技巧

### 1️⃣ 快速设置 CLI 别名

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias a='argocd'
alias k='kubectl'
alias ka='kubectl -n argocd'

# 然后使用
a app list
k get pods
ka get all
```

### 2️⃣ 自动完成密码输入

```bash
# 创建 ArgoCD 配置
export ARGOCD_PASSWORD='Laiye@2026'
export ARGOCD_USERNAME='admin'

# 然后 CLI 会自动使用这些凭证
argocd login localhost:8080 --insecure
```

### 3️⃣ 快速访问多个 Service

```bash
# 创建脚本来快速端口转发多个服务
#!/bin/bash
kubectl port-forward svc/argo-cd-argocd-server 8080:443 -n argocd &
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090 &
kubectl port-forward -n monitoring svc/grafana 3000:80 &

# 访问这些地址
# ArgoCD: https://localhost:8080
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

### 4️⃣ 查看应用树

```bash
# 使用 ArgoCD CLI
argocd app get root-app --refresh

# 使用 kubectl
kubectl get application root-app -n argocd -o yaml
```

---

## 🆘 紧急联系方式

遇到问题？

1. 查看日志：`kubectl logs -f deployment/argo-cd-argocd-server -n argocd`
2. 检查事件：`kubectl get events -n argocd`
3. 查看文档：[SETUP_GUIDE.md](./SETUP_GUIDE.md)
4. 检查官方文档：https://argo-cd.readthedocs.io/

---

**最后更新**: 2026-05-17
**项目**: ArgoCD Apps - App of Apps GKE 管理平台

