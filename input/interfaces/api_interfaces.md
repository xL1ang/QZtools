# 关联模块接口

## 1. 库存服务

### 查询库存
- 接口：GET /api/inventory/check
- 入参：{ "product_id": "string", "quantity": int }
- 出参：{ "available": bool, "stock": int }

### 扣减库存
- 接口：POST /api/inventory/deduct
- 入参：{ "product_id": "string", "quantity": int, "order_id": "string" }
- 出参：{ "success": bool, "message": "string" }

## 2. 支付服务

### 创建支付单
- 接口：POST /api/payment/create
- 入参：{ "order_id": "string", "amount": float, "method": "wechat|alipay" }
- 出参：{ "payment_url": "string", "payment_id": "string" }

### 查询支付状态
- 接口：GET /api/payment/status
- 入参：{ "payment_id": "string" }
- 出参：{ "status": "pending|success|failed", "paid_at": "datetime" }

## 3. 物流服务

### 创建运单
- 接口：POST /api/logistics/create
- 入参：{ "order_id": "string", "address": "string", "items": [...] }
- 出参：{ "tracking_no": "string", "carrier": "string" }
