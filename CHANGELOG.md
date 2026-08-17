# Changelog

All notable changes to UploadSentinel will be documented in this file.

## [1.0.0] - 2026-08-17

### 中文

首个 GitHub 正式发布版本。

#### Added

- PySide6 / Qt 中文桌面界面
- 深色 / 浅色主题
- 自定义主题配色
- Burp Raw Request 导入
- multipart 文件字段识别
- Raw Request 本地预检
- 内置无害文件上传测试用例
- 测试用例搜索与分类
- 响应基线比较
- 响应相似度分析
- 响应聚类
- 自定义 Success / Reject 规则
- 返回 URL / Path 提取
- 同源 URL 二次检查
- Manual review 状态
- 扫描历史
- Project 保存 / 恢复
- JSON / CSV / HTML 报告
- Windows 启动 / Debug BAT
- Startup self-check
- Core self-test

#### Security

- 返回 URL 检查默认限制为同源
- 不自动跟随跨域重定向
- 内置测试 Payload 均为无害、不可执行内容

---

### English

First official GitHub release.

#### Added

- PySide6 / Qt Chinese desktop UI
- dark/light themes
- custom color themes
- Burp raw request import
- multipart file-field detection
- local raw-request preflight
- built-in benign upload test cases
- test-case search and category filters
- baseline response comparison
- response similarity analysis
- response clustering
- configurable success/reject rules
- returned URL/path extraction
- same-origin reference validation
- manual review states
- scan history
- project save/restore
- JSON/CSV/HTML reports
- Windows launch/debug scripts
- startup self-check
- core self-test
