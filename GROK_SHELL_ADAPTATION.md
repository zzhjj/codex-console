# Grok Shell Adaptation Guide

> 这份文档只讲 `codex-console` 这个 **Web 壳** 在做 Grok 适配时，哪些可以直接复用，哪些必须自己重写。

## 已帮你处理好的

- 页面主文案改为 **Grok 注册控制台**
- 导航里移除了 **支付 / 卡池 / 自动进 team**
- `src/web/app.py` 中对应页面入口已移除
- `src/web/routes/__init__.py` 中已取消挂载 `payment_router`
- 新增网页说明页：`/adaptation-guide`
- 已删除：`src/web/routes/payment.py`、`src/core/openai/payment.py`、`src/core/openai/browser_bind.py`、`static/js/payment.js`、`templates/payment.html`、`templates/card_pool.html`、`templates/auto_team.html`

## 可以直接复用的壳层

### 1. Web 服务启动
- `webui.py`

### 2. FastAPI + 页面壳
- `src/web/app.py`
- `templates/*.html`
- `static/js/*.js`

### 3. 后台任务与实时日志
- `src/web/task_manager.py`
- `src/web/routes/websocket.py`

### 4. 数据库存储
- `src/database/models.py`
- `src/database/crud.py`
- `src/database/init_db.py`

### 5. 通用 HTTP 封装
- `src/core/http_client.py`

## 必须自己改的 OpenAI 强绑定文件

### 核心必改
- `src/core/register.py`
  - 当前是 OpenAI 注册总流程
  - 你要把它替换成调用你自己的 Grok 注册逻辑

- `src/config/constants.py`
  - 里面的 `OPENAI_API_ENDPOINTS`、`OPENAI_PAGE_TYPES`、验证码匹配规则都要重写

### 不能直接用
- `src/core/openai/oauth.py`
- `src/core/openai/token_refresh.py`
- `src/core/openai/overview.py`
- `src/core/openai/payment.py`
- `src/core/openai/browser_bind.py`

这些都是 OpenAI / ChatGPT / Codex 页面、Token、订阅、支付专用。

## 按需保留的文件

### 任务入口（可复用结构）
- `src/web/routes/registration.py`
  - 保留任务创建、状态更新、日志推送
  - 把其中 `RegistrationEngine(...)` 的调用替换成你的 Grok 引擎

### 账号管理（可复用页面）
- `src/web/routes/accounts.py`
  - 可以继续用来展示账号/凭证
  - 但字段含义要自己调整（例如 `session_token` / `access_token` / `cookies`）

### 邮箱服务（看你用不用）
- `src/services/*`
  - 如果你只用 Mail.tm，就保留对应服务即可
  - Outlook / IMAP / 绑卡相关都可以后续删掉

## 推荐改造顺序

1. 先确认单任务流程：
   - 点按钮
   - 创建任务
   - 后台执行
   - 日志上屏

2. 再替换注册内核：
   - 从 `src/core/register.py` 下手
   - 先让它只跑一条 Grok 注册链路

3. 再清理模型与字段：
   - 账号表字段命名
   - 设置项命名
   - 页面文案

4. 最后再删多余模块：
   - `src/web/routes/payment.py`
   - `src/core/openai/payment.py`
   - `templates/payment.html`
   - `templates/card_pool.html`
   - `templates/auto_team.html`

## 你当前最该看的文件

- `webui.py`
- `src/web/app.py`
- `src/web/task_manager.py`
- `src/web/routes/websocket.py`
- `src/web/routes/registration.py`
- `src/core/register.py`

## 一句话总结

这个仓库最值钱的是：

**网页发任务 → 后台线程跑 → WebSocket 推日志 → 页面实时显示**

你真正要换掉的，只是里面那颗 **OpenAI 注册内核**。
