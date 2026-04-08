-- 初始化数据
USE appdb;

-- 插入示例产品
INSERT INTO products (sku, name, price_cents) VALUES
('SKU001', 'iPhone 15', 599900),
('SKU002', 'MacBook Pro', 1999900),
('SKU003', 'iPad Air', 299900),
('SKU004', 'Apple Watch', 199900),
('SKU005', 'AirPods', 99900);

-- 插入库存数据
INSERT INTO inventory (product_id, quantity) VALUES
(1, 50),
(2, 20),
(3, 30),
(4, 40),
(5, 100);

-- 插入示例用户（密码都是 'password123' 的哈希）
INSERT INTO users (username, password_hash) VALUES
('admin', 'pbkdf2:sha256:600000$example$salt$hashed_password'),
('user1', 'pbkdf2:sha256:600000$example$salt$hashed_password'),
('user2', 'pbkdf2:sha256:600000$example$salt$hashed_password');