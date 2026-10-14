# 英语翻译工具

本地 + 云端双模式的中英翻译/查词工具。前端是纯静态页面（可部署到 GitHub Pages），后端通过 Python 本地服务或 Cloudflare Worker 中转 DeepSeek API。

## 本地运行（无需部署）

1. 用记事本打开 `config.json`，填入 DeepSeek 的 `api_key`
2. 双击 `启动.bat`（或命令行执行 `python server.py`）

> 本地模式下 `index.html` 里的 `API_BASE` 保持空字符串即可。

## 云端部署（GitHub Pages + Cloudflare Worker）

### 第 1 步：部署中转 Worker

1. 安装 Wrangler（需先装 Node.js）：`npm install -g wrangler`
2. 登录 Cloudflare：`npx wrangler login`
3. 把 DeepSeek key 存为 Worker 的环境变量（不会进代码库）：
   ```
   npx wrangler secret put DEEPSEEK_API_KEY
   ```
   回车后粘贴你的 key 再回车。
4. 部署：
   ```
   npx wrangler deploy
   ```
   成功后终端会打印一个 `https://deepseek-proxy.你的账号.workers.dev` 的地址。

### 第 2 步：让前端指向 Worker

编辑 `index.html`，把脚本顶部的 `API_BASE` 改成你的 Worker 地址：

```js
const API_BASE = 'https://deepseek-proxy.你的账号.workers.dev';
```

### 第 3 步：部署前端到 GitHub Pages

1. 把这个仓库推到 GitHub（`config.json` 已被 `.gitignore` 排除，key 不会上传）
2. 仓库页面 Settings → Pages → Source 选 `main` 分支根目录 → Save
3. 稍等几分钟，访问 `https://你的账号.github.io/仓库名/`

## 安全提示

`config.json` 里的 API key 仅用于本地运行，切勿提交到公开仓库（已通过 `.gitignore` 排除）。云端部署时 key 只存在 Worker 环境变量里，不会出现在代码或前端页面中。
