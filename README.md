# App Store Price Watcher

一个基于 GitHub Actions 的 App Store 应用价格监控工具。无需服务器，完全免费。

## 功能特性

- 🕒 **自动化监控**：GitHub Actions 每天上午 10:00 (北京时间) 执行一次。
- 💰 **价格变动通知**：即时发送价格变动通知（邮件/Webhook）。
- 📅 **周报汇总**：每周日发送过去一周的价格历史汇总邮件。
- 📊 **历史记录**：自动记录每日价格到 `data/timeline.json`。
- ⚙️ **配置简单**：通过 YAML 文件管理监控的应用列表。

## 快速开始

### 1. Fork 本仓库

点击右上角的 **Fork** 按钮，将本项目复制到你的 GitHub 账号下。

### 2. 配置监控应用

修改 `config/apps.yaml` 文件，添加你想要监控的应用：

```yaml
apps:
  - id: "1443988620"       # App Store ID (必填)
    name: "Example App"    # 应用名称 (备注用)
    country: "cn"          # 商店区域 (cn, us, jp 等)
```

**如何获取 App Store ID?**
在浏览器打开应用的 App Store 链接，URL 中的数字即为 ID。
例如：`https://apps.apple.com/cn/app/shadowrocket/id932747118` -> ID 是 `932747118`。

### 3. 配置通知 (GitHub Secrets)

进入仓库的 **Settings** -> **Secrets and variables** -> **Actions**，点击 **New repository secret** 添加以下变量（按需配置）：

| Secret Name   | 说明                                      |<br>
| `EMAIL_HOST`  | SMTP 服务器地址 (如 smtp.qq.com)           |<br>
| `EMAIL_PORT`  | SMTP 端口 (默认 465 SSL)                  |<br>
| `EMAIL_USER`  | 发件人邮箱账号                             |<br>
| `EMAIL_PASS`  | 邮箱授权码/密码                            |<br>
| `EMAIL_TO`    | 接收通知的邮箱 (多个用逗号分隔)               |<br>
| `WEBHOOK_URL` | IM 工具的 Webhook 地址 (飞书/钉钉/Slack 等) |<br>

### 4. 启用 Workflow

进入仓库的 **Actions** 页面，确保 Workflow 已启用。它会按照预定的时间表运行，你也可以点击 **Run workflow** 手动触发测试。

## 本地运行

如果你想在本地测试或运行：

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量 (可选，用于测试通知)：
   ```bash
   export WEBHOOK_URL="https://your-webhook-url"
   ```

3. 运行脚本：
   ```bash
   python src/main.py
   ```

## 数据存储

- **实时状态**：`data/history.json` 存储最近一次检测的价格，用于比对变动。
- **历史时间轴**：`data/timeline.json` 存储每日的价格快照，用于生成周报。

每次运行结束后，GitHub Actions 会自动将数据变更提交回仓库。

## 许可证

MIT License
