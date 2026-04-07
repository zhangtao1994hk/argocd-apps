# 阶段 1：编译 Vue 代码 (注意 AS 大写)
FROM node:22-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
# 使用 npm ci 替代 npm install，在 CI/CD 环境中更稳定
RUN npm ci || npm install
COPY . .
# 打印一下当前的目录结构，如果报错了，去 GitHub Actions 日志里看看有没有缺少文件
RUN ls -la src/views/
# 执行打包
RUN npm run build

# 阶段 2：使用 Nginx 运行编译后的静态文件 (注意 AS 大写)
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5000

CMD ["nginx", "-g", "daemon off;"]
