# grok-register → codex-console 壳骨架映射

这份文档专门说明：你之前发来的 `grok-register` 压缩包，应该怎么塞进当前仓库的壳里。

当前壳的关键入口文件：
- `src/core/register.py`

你发来的注册机关键文件：
- `grok.py`
- `g/email_service.py`
- `g/turnstile_service.py`
- `api_solver.py`
- `browser_configs.py`
- `db_results.py`

---

## 一、最重要的映射关系

| 你的 grok-register 文件 | 应该塞进壳里的位置 | 作用 |
|---|---|---|
| `grok.py` 里的主流程 | `src/core/register.py` 的 `_perform_registration()` | 真正的注册执行主流程 |
| `grok.py` 里页面参数抓取 | `src/core/register.py` 的 `_prepare_registration_context()` | 抓 `site_key` / `state_tree` / `action_id` |
| `g/email_service.py` | `src/services/` 新增一个对应邮箱服务，或直接在 `_perform_registration()` 中调用 | 创建邮箱、收验证码 |
| `g/turnstile_service.py` | `src/services/` 或 `src/core/` 新建 Grok captcha 服务模块 | 取 Turnstile token |
| `api_solver.py` | 独立工具服务，建议不要硬塞进 Web 壳主流程 | 本地起 solver 服务 |
| `browser_configs.py` / `db_results.py` | 仅当你保留本地 solver 时再带上 | 本地 solver 辅助模块 |

---

## 二、当前 `src/core/register.py` 里每个方法该填什么

### 1. `_prepare_registration_context()`
你应该把 `grok.py` 里这部分逻辑搬进来：

- 访问 `https://accounts.x.ai/sign-up`
- 抓：
  - `site_key`
  - `state_tree`
  - `action_id`
- 准备 session / headers / proxy
- 准备邮箱地址（如果你想在这里先创建邮箱也可以）

### 建议返回结构
```python
return {
    "site_url": "https://accounts.x.ai",
    "site_key": "...",
    "state_tree": "...",
    "action_id": "...",
    "proxy_url": self.proxy_url,
    "session": session,
}
```

---

### 2. `_perform_registration(context)`
这是最核心的方法。

你应该把 `grok.py` 的主流程按顺序搬进来：

1. 创建邮箱
2. 发送验证码
3. 轮询收验证码
4. 校验验证码
5. 获取 Turnstile token
6. 提交注册
7. 提取 `sso` / cookies
8. 组装 `RegistrationArtifacts`

### 建议最终返回
```python
return RegistrationArtifacts(
    email=email,
    password=password,
    session_token=sso,
    cookies=f"sso={sso}; ...",
    metadata={
        "provider": "grok",
        "site_key": context.get("site_key"),
        "action_id": context.get("action_id"),
        "register_source": "grok-register-port",
    },
)
```

---

### 3. `_normalize_artifacts(artifacts)`
这个方法不用写复杂逻辑。

你只要统一：
- `metadata.provider = grok`
- `metadata.adapter = grok-shell-skeleton`
- 如果你还有 `sso`、`cookies`、`turnstile_mode` 等，也可以在这里补齐

---

## 三、哪些文件建议你新增到当前仓库

建议新增目录：

```text
src/core/grok_register/
    email_service.py
    turnstile_service.py
    solver_client.py   # 如果你要连 api_solver.py
```

### 推荐原因
不要把你发来的 `grok-register` 原样散贴到一堆老文件里，最好把它单独收口到：
- `src/core/grok_register/*`

这样以后：
- 壳层还是壳层
- Grok 注册内核还是 Grok 注册内核
- 结构更清楚

---

## 四、`api_solver.py` 建议怎么处理

### 最佳做法
不要把它硬塞进 FastAPI 主应用里。

建议保留为：
- 独立命令行工具
- 或独立服务

然后在主注册流程里通过 HTTP 调它。

### 原因
`api_solver.py` 本质是：
- Quart 服务
- 浏览器自动化
- 本地 solver 工具

它跟当前主 Web 壳不是一类东西，硬揉进去会很乱。

---

## 五、你现在最省力的迁移方式

### 第一步
先只把 `grok.py` 的主流程移到 `_perform_registration()`，不要一开始就追求优雅拆分。

### 第二步
等跑通一次后，再把这些拆出去：
- 邮箱
- 验证码
- Turnstile
- solver client

### 第三步
最后再补数据库字段、账号展示、状态页。

---

## 六、最短可跑路径

1. 保持当前 Web 壳不动
2. 在 `src/core/register.py` 里填 `_prepare_registration_context()`
3. 在 `src/core/register.py` 里填 `_perform_registration()`
4. 让它至少能返回：
   - `email`
   - `password`
   - `session_token` 或 `cookies`
5. 验证前端能看到：
   - running
   - 日志滚动
   - completed / failed

只要这条通了，壳就活了。

---

## 七、一句话总结

### 当前壳负责：
- 网页
- 任务
- 日志
- 状态
- 数据库存储

### 你自己的 `grok-register` 负责：
- 真正的注册动作
- 邮箱验证码
- Turnstile
- 最终 SSO / cookies 提取

### 最佳接法：
> 把 `grok.py` 的主逻辑塞进 `src/core/register.py` 的 `_perform_registration()`，把参数抓取塞进 `_prepare_registration_context()`。
