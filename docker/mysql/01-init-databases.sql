-- 建库：meta 存元数据（表/字段/指标），dw 模拟业务数仓
-- 账号用镜像默认创建的 root@'%'，它已带有全部权限，
-- 因此这里不需要再写 GRANT。
CREATE DATABASE IF NOT EXISTS meta
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

CREATE DATABASE IF NOT EXISTS dw
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;
