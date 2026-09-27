-- 数仓表结构：4 张维度表 + 1 张事实表（星型模型）
-- 必须声明客户端编码：容器初始化时的 mysql 客户端默认按 latin1 解释文件字节，
-- 少了这行，下面 COMMENT 里的中文会被存成乱码（数据本身不受影响，03 脚本已有此行）
SET NAMES utf8mb4;
USE dw;

CREATE TABLE dim_region (
  region_id   VARCHAR(64) NOT NULL COMMENT '地区唯一标识',
  region_name VARCHAR(64)          COMMENT '订单所属的大区名称，如华东、华南等',
  province    VARCHAR(64)          COMMENT '订单所属的省份名称',
  country     VARCHAR(64)          COMMENT '地区所属国家名称',
  PRIMARY KEY (region_id)
) ENGINE = InnoDB COMMENT = '地区维度表，用于描述订单发生的地理区域信息';

CREATE TABLE dim_customer (
  customer_id   VARCHAR(64) NOT NULL COMMENT '客户唯一标识',
  customer_name VARCHAR(128)         COMMENT '客户名称',
  gender        VARCHAR(16)          COMMENT '客户性别',
  member_level  VARCHAR(32)          COMMENT '客户会员等级',
  PRIMARY KEY (customer_id)
) ENGINE = InnoDB COMMENT = '客户维度表，描述下单客户的基本属性';

CREATE TABLE dim_product (
  product_id   VARCHAR(64) NOT NULL COMMENT '商品唯一标识',
  product_name VARCHAR(128)         COMMENT '商品名称',
  brand        VARCHAR(64)          COMMENT '商品品牌名称',
  category     VARCHAR(64)          COMMENT '商品所属品类',
  PRIMARY KEY (product_id)
) ENGINE = InnoDB COMMENT = '商品维度表，描述商品的基本属性信息';

CREATE TABLE dim_date (
  date_id INT         NOT NULL COMMENT '日期唯一标识，格式 yyyyMMdd',
  year    INT                  COMMENT '年份',
  month   INT                  COMMENT '月份',
  day     INT                  COMMENT '日',
  quarter VARCHAR(8)           COMMENT '季度',
  PRIMARY KEY (date_id)
) ENGINE = InnoDB COMMENT = '时间维度表，用于多时间粒度分析';

CREATE TABLE fact_order (
  order_id       VARCHAR(64)   NOT NULL COMMENT '订单唯一标识',
  customer_id    VARCHAR(64)            COMMENT '关联客户维度的外键',
  product_id     VARCHAR(64)            COMMENT '关联商品维度的外键',
  region_id      VARCHAR(64)            COMMENT '关联地区维度的外键',
  date_id        INT                    COMMENT '关联时间维度的外键',
  order_quantity INT                    COMMENT '订单中商品的购买数量',
  order_amount   DECIMAL(10, 2)         COMMENT '订单金额',
  PRIMARY KEY (order_id),
  KEY idx_customer_id (customer_id),
  KEY idx_product_id (product_id),
  KEY idx_region_id (region_id),
  KEY idx_date_id (date_id)
) ENGINE = InnoDB COMMENT = '订单事实表，记录订单数量和金额等核心指标';
