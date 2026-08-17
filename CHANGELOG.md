# Changelog

All notable changes to UploadSentinel will be documented in this file.

## [1.1.0] - 2026-08-17

### 中文

#### Added

- 文件上传测试用例扩展至 **56 项**
- 新增 **低 / 中 / 高** 三档累计测试强度
  - 低档：15 项
  - 中档新增：21 项，执行时累计为 36 项
  - 高档新增：20 项，执行时累计为 56 项
- 扫描器新增测试档位选择和当前执行数量提示
- 测试用例页面新增档位列与档位筛选
- 自定义无害用例支持选择 Low / Medium / High
- CLI 新增 `--level low|medium|high`
- `.usproj` 保存和恢复测试档位

#### Improved

- 扩展文件名边界测试
- 扩展 MIME / 内容不一致测试
- 扩展常见文件类型和内容边界测试
- 左侧品牌区域改为透明背景排版，移除矩形底色感

#### Safety

- 三档仅表示测试覆盖范围和输入变异程度，**不是漏洞等级**
- 所有新增内置内容仍为无害、不可执行测试数据

---

### English

#### Added

- Expanded the built-in upload test library to **56 benign cases**
- Added cumulative **Low / Medium / High** test levels
  - Low: 15 cases
  - Medium: 21 additional cases, 36 cumulative
  - High: 20 additional cases, 56 cumulative
- Added test-level selection and execution-count summary to the scanner
- Added level column and filtering to the test-case page
- Custom benign cases can select Low / Medium / High
- Added CLI option `--level low|medium|high`
- Project files now save and restore the selected test level

#### Improved

- Expanded filename boundary coverage
- Expanded MIME/content mismatch coverage
- Expanded benign file-type and content edge cases
- Refined the sidebar brand area with transparent typography

#### Safety

- Levels describe testing breadth and input variation, **not vulnerability severity**
- All new built-in cases remain benign and non-executable

---

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
