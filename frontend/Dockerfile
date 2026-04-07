# 阶段 1：编译 Vue 代码
FROM node:18-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 阶段 2：使用 Nginx 运行编译后的静态文件
FROM nginx:stable-alpine as production-stage
# 复制编译好的 dist 目录到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html
# 替换自定义的 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5000
CMD ["nginx", "-g", "daemon off;"]
