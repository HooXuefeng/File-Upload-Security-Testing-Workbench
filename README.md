# UploadSentinel v1.0

> 文件上传安全测试工作台 / File Upload Security Testing Workbench

UploadSentinel 是一个面向**授权安全测试、Web 安全评估和文件上传接口复核**的桌面工具。  
UploadSentinel is a desktop workbench for **authorized security testing, web security assessment, and file-upload endpoint validation**.

它的目标不是简单地“HTTP 200 = 漏洞”，而是通过正常上传基线、响应相似度、返回地址验证、规则判断和人工复核状态，帮助测试人员更准确地筛选需要进一步验证的上传行为。

Instead of treating every `HTTP 200` response as a vulnerability, UploadSentinel uses baseline comparison, response similarity, returned-file reference checks, configurable verdict rules, clustering, and manual review states to help testers prioritize results that require further verification.

---

## ✨ 功能 / Features

### 文件上传测试 / Upload testing

- Burp 原始 HTTP 请求导入  
  Import raw HTTP requests captured from Burp Suite
- 自动识别 multipart 文件字段  
  Detect multipart file fields
- 提取普通表单字段  
  Extract regular multipart form fields
- HTTP / HTTPS Scheme 选择  
  HTTP / HTTPS scheme selection
- 自定义 Header / Cookie / 表单参数  
  Custom headers, cookies, and form fields
- HTTP 代理支持  
  HTTP proxy support
- 请求间隔与超时配置  
  Configurable request delay and timeout

### 无害测试用例 / Benign test cases

内置测试内容均为无害、不可执行内容。  
All built-in test contents are benign and non-executable.

覆盖：

- 大小写扩展名 / case-variant extensions
- 双后缀与多后缀 / double and multiple extensions
- Unicode 文件名 / Unicode filenames
- 长文件名 / long filenames
- MIME 与真实内容不一致 / MIME-content mismatch
- 无扩展名 / no-extension files
- 未知扩展名 / unknown extensions
- PNG / GIF / TXT / JSON / CSV / SVG / PDF
- 空文件与极小文件 / empty and tiny files
- 无害文件尾部数据 / harmless trailing file data

### 分析能力 / Analysis

- 正常上传基线比较  
  Baseline comparison
- 动态响应内容归一化  
  Dynamic response normalization
- 响应相似度  
  Response similarity scoring
- 响应自动聚类  
  Response clustering
- 返回文件 URL / Path 提取  
  Returned file URL/path extraction
- 同源 URL HEAD / GET 检查  
  Same-origin HEAD/GET validation
- 不自动跟随跨域重定向  
  No automatic cross-origin redirect following
- 自定义 Success / Reject Regex  
  Custom success/reject regex rules
- 自定义 HTTP 状态码规则  
  Custom HTTP status rules
- `HIGH_REVIEW / REVIEW / REJECTED / BLOCKED / ERROR` 分类
- 人工标记 `CONFIRMED / FALSE_POSITIVE / UNREVIEWED`

### 桌面 UI / Desktop UI

- PySide6 / Qt
- 中文界面 / Chinese UI
- English documentation
- 深色 / 浅色主题  
  Dark / light themes
- 自定义主题配色  
  Custom color themes
- 平面编辑式低饱和 UI  
  Flat, low-saturation editorial UI
- 测试用例搜索与分类筛选  
  Test-case search and category filtering
- 扫描实时日志  
  Live scan log
- 结果统计摘要  
  Result summary
- 扫描历史  
  Scan history
- 项目保存 / 恢复  
  Project save / restore
- JSON / CSV / HTML 报告导出  
  JSON / CSV / HTML export

---

## 🖥️ 截图 / Screenshots

建议在 GitHub 仓库中新建：

```text
docs/screenshots/
```

并放入：

```text
dashboard.png
scanner.png
request.png
results.png
theme.png
```

README 中即可引用：

```markdown
![Dashboard](docs/screenshots/dashboard.png)
```

---

## 🚀 安装 / Installation

推荐 Python 3.10+。  
Python 3.10+ is recommended.

```bash
git clone https://github.com/YOUR_USERNAME/UploadSentinel.git
cd UploadSentinel

pip install -r requirements.txt
```

---

## ▶️ 启动 / Run

### Windows

```powershell
python uploadsentinel_qt.py
```

也可以双击：

```text
start_uploadsentinel.bat
```

如果启动失败，需要查看完整错误：

```text
debug_uploadsentinel.bat
```

### CLI

```bash
python uploadsentinel.py --url https://example.com/upload -f file
```

导入 Burp 原始请求：

```bash
python uploadsentinel.py \
  --raw-request request.txt \
  --scheme https
```

经过 Burp Proxy：

```bash
python uploadsentinel.py \
  --raw-request request.txt \
  --proxy http://127.0.0.1:8080 \
  -k
```

---

## 🧪 自检 / Self-test

不会请求任何真实网络目标。  
The self-test does not contact any real network target.

```bash
python startup_check.py
python selftest.py
```

当前自检包括：

- 自定义规则优先级
- Reject 优先于 Success
- HTTP 状态规则
- 响应聚类
- 历史序列化
- 旧项目读取
- multipart 字段解析
- GUI 主题初始化顺序

Current checks cover:

- custom rule priority
- reject-before-success handling
- HTTP status rules
- response clustering
- history serialization
- project compatibility
- multipart parsing
- GUI theme initialization order

---

## 🔎 推荐工作流 / Suggested Workflow

```text
Burp 抓取正常上传
        ↓
导入 Raw Request
        ↓
本地预检请求
        ↓
执行无害测试用例
        ↓
基线 / 规则 / 相似度 / 聚类分析
        ↓
筛选 HIGH_REVIEW / REVIEW
        ↓
查看 Response / Diff / Returned URLs
        ↓
回到 Burp Repeater 人工复核
        ↓
标记 CONFIRMED / FALSE_POSITIVE
```

---

## 🎯 Verdict 说明

| Verdict | 中文说明 | Meaning |
|---|---|---|
| `BASELINE` | 正常基线 | Normal baseline request |
| `REJECTED` | 明确拒绝 | Explicitly rejected |
| `BLOCKED` | 被鉴权/WAF/限流阻止 | Blocked by auth/WAF/rate limit |
| `UNKNOWN` | 证据不足 | Insufficient evidence |
| `REVIEW` | 建议人工复核 | Manual review recommended |
| `HIGH_REVIEW` | 优先人工复核 | High-priority manual review |
| `ERROR` | 请求/服务器错误 | Request/server error |

> `HIGH_REVIEW` **不代表漏洞已经成立**。  
> `HIGH_REVIEW` **does not mean a vulnerability is confirmed**.

---

## 🔐 安全边界 / Safety Scope

UploadSentinel 设计用于：

- 已获得授权的渗透测试
- 内部安全测试
- 自有系统
- CTF / 靶场
- 开发与测试环境

UploadSentinel is intended for:

- authorized penetration testing
- internal security testing
- systems you own
- CTF/lab environments
- development and staging systems

本项目**不内置**：

- WebShell
- 命令执行 Payload
- 反弹连接
- 恶意宏
- 破坏性文件
- 未授权利用自动化

This project does **not** ship with:

- webshell payloads
- command-execution payloads
- reverse shells
- malicious macros
- destructive files
- unauthorized exploitation automation

---

## 🧩 项目结构 / Repository Structure

```text
UploadSentinel/
├── uploadsentinel_qt.py        # PySide6 GUI
├── uploadsentinel.py           # Core / CLI
├── selftest.py                 # Core tests
├── startup_check.py            # Startup checks
├── requirements.txt
├── start_uploadsentinel.bat
├── debug_uploadsentinel.bat
├── UploadSentinel.spec
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
└── .gitignore
```

---

## 📦 Windows EXE

安装 PyInstaller：

```powershell
pip install pyinstaller
```

打包：

```powershell
pyinstaller UploadSentinel.spec
```

输出目录：

```text
dist/UploadSentinel/
```

---

## 🤝 贡献 / Contributing

欢迎提交：

- Bug 修复
- UI 改进
- 无害测试用例
- 响应分析改进
- 文档
- 测试代码

Contributions are welcome, including:

- bug fixes
- UI improvements
- benign test cases
- response-analysis improvements
- documentation
- tests

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 🛡️ Security

如果发现 UploadSentinel 本身存在安全问题，请不要直接公开完整利用细节。  
If you discover a security issue in UploadSentinel itself, please avoid immediately publishing full exploitation details.

参见 [SECURITY.md](SECURITY.md)。

---

## 📜 License

MIT License. See [LICENSE](LICENSE).

---

## ⚠️ Disclaimer / 免责声明

本工具仅用于合法、授权的安全测试。使用者应自行确保测试行为符合当地法律法规和目标系统授权范围。

This tool is intended solely for lawful and authorized security testing. Users are responsible for ensuring that all testing complies with applicable laws and the authorization scope of the target system.
