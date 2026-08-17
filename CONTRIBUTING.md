# Contributing / 贡献指南

感谢你考虑为 UploadSentinel 做贡献。

Thank you for considering contributing to UploadSentinel.

## 可以贡献什么 / What to contribute

欢迎：

- Bug 修复 / bug fixes
- UI 改进 / UI improvements
- 文档 / documentation
- 测试 / tests
- 无害文件测试用例 / benign upload test cases
- 响应分析算法 / response-analysis improvements
- 兼容性改进 / compatibility improvements

## 安全限制 / Safety requirements

Pull Request 不应默认加入：

- WebShell
- 命令执行 Payload
- 反弹连接
- 破坏性文件
- 自动化未授权攻击代码

Pull requests should not introduce by default:

- webshell payloads
- command-execution payloads
- reverse shells
- destructive files
- automated unauthorized exploitation

## 开发环境 / Development

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

Run:

```bash
python uploadsentinel_qt.py
```

Tests:

```bash
python startup_check.py
python selftest.py
```

## Pull Request

提交 PR 前请确保：

Before submitting a PR:

1. 程序可正常启动 / the application starts correctly.
2. `startup_check.py` 通过 / passes.
3. `selftest.py` 通过 / passes.
4. 不破坏现有 `.usproj` 兼容性 / project compatibility is preserved when possible.
5. 新增功能提供简要说明 / new features are documented.
