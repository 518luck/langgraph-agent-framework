-- 建库：默认只建一个，需要多个照抄这段
-- 账号用镜像默认创建的 root@'%'，它已带有全部权限，因此这里不需要再写 GRANT。
CREATE DATABASE IF NOT EXISTS app
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;
