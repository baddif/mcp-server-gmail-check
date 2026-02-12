# Gmail Check MCP Server - 版本控制与用户更新指南

## 📋 概述

Gmail Check MCP Server 现已配备完整的版本控制系统，为已安装的用户提供简单、安全的更新机制。

## 🚀 快速更新

### 最简单的更新方法

```bash
# 进入项目目录
cd mcp-server-gmail-check

# 一键自动更新
./update.sh
```

该脚本会：
- 📋 自动备份您的配置文件
- ⬇️ 拉取最新代码
- 📦 更新Python依赖
- ✅ 验证安装完整性
- 🔄 保持现有配置不变

## 🔍 检查版本与更新

### 查看当前版本
```bash
# 显示版本信息
python3 version.py --version

# 显示详细信息
python3 version.py --info

# JSON格式输出（供程序使用）
python3 version.py --json
```

### 检查是否有更新
```bash
# 检查可用更新
python3 version.py --check-updates

# 或使用更新脚本检查
./update.sh --check
```

## 🛠️ 版本管理功能

### 自动版本控制
- **版本跟踪**: 自动识别当前版本和Git状态
- **更新检测**: 自动检查远程仓库的新版本
- **依赖管理**: 自动更新Python包依赖
- **配置保护**: 更新时保护用户配置文件

### 备份与恢复
- **自动备份**: 更新前自动备份配置文件
- **时间戳**: 备份文件夹使用时间戳命名
- **配置保持**: 更新后保持原有配置不变

### 版本兼容性
- **MCP协议**: 2024-11-05版本兼容
- **Python版本**: 3.7+支持
- **向后兼容**: 新版本完全向后兼容

## 📝 版本历史

### v1.1.0 (2026-02-12) - 当前版本
**新增功能：**
- ⏱️ **精确时间控制**: `time_range_hours` 参数支持1-720小时精确控制
- 💾 **缓存管理**: `use_cache` 参数支持缓存控制和完整重扫
- 🔄 **版本控制系统**: 完整的版本管理和自动更新功能
- 📚 **文档增强**: 全面的参数指南和故障排除

**技术改进：**
- 增强的参数验证和JSON Schema定义
- 更好的MCP协议兼容性和错误处理
- 改进的测试覆盖率和示例配置
- 自动更新机制和配置备份

### v1.0.0 (2024-12-12) - 初始版本
- Gmail IMAP集成和应用密码认证
- 智能邮件过滤和缓存机制
- MCP协议支持和AI代理集成
- 多语言支持和安全配置

完整更新历史请查看 [CHANGELOG.md](CHANGELOG.md)

## 🔧 手动更新步骤

如果自动更新失败，可以手动执行以下步骤：

```bash
# 1. 备份配置
cp gmail_config_local.json gmail_config_backup.json

# 2. 检查Git状态
git status

# 3. 暂存未提交的更改（如有）
git stash push -m "Backup before update"

# 4. 拉取最新代码
git fetch origin main
git pull origin main

# 5. 更新依赖
pip3 install -r requirements.txt --upgrade

# 6. 验证安装
python3 mcp_server.py --test

# 7. 恢复配置（如需要）
# 配置文件通常会自动保持
```

## 🚨 故障排除

### 更新脚本失败
```bash
# 检查Git状态
git status

# 强制拉取（小心！）
git fetch origin main
git reset --hard origin/main

# 重新安装依赖
pip3 install -r requirements.txt --force-reinstall
```

### 配置文件丢失
```bash
# 从备份恢复（替换为实际备份文件夹名）
cp backup_20260212_143000/gmail_config_local.json .

# 或从模板重新配置
cp gmail_config_example.json gmail_config_local.json
# 编辑 gmail_config_local.json
```

### 依赖问题
```bash
# 检查Python版本
python3 --version

# 强制重装所有依赖
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt
```

### Claude Desktop未识别更新
```bash
# 重启Claude Desktop
# 1. 完全退出Claude Desktop
# 2. 重新启动应用
# 3. 更新的MCP服务器将自动加载
```

## 💡 最佳实践

### 定期更新
```bash
# 建议每周检查更新
./update.sh --check

# 每月进行更新
./update.sh
```

### 版本管理
```bash
# 查看版本历史
git log --oneline --grep="feat\|fix"

# 查看标签
git tag -l
```

### 配置管理
- 始终使用 `gmail_config_local.json` 存储私人配置
- 定期备份重要配置文件
- 测试配置更改：`python3 test_gmail_skill.py`

## 🔒 安全注意事项

- **配置保护**: 更新过程不会覆盖您的私人配置
- **备份机制**: 所有重要文件在更新前自动备份
- **Git忽略**: 敏感文件已添加到 `.gitignore`
- **权限检查**: 更新脚本会验证仓库权限

## 📞 获取支持

如果更新过程中遇到问题：

1. **检查版本**: `python3 version.py --info`
2. **查看日志**: `./update.sh` 的输出信息
3. **提交Issue**: [GitHub Issues](https://github.com/baddif/mcp-server-gmail-check/issues)
4. **包含信息**:
   - 版本信息 (`python3 version.py --json`)
   - 错误消息
   - 操作系统信息
   - Python版本

---

**✨ 享受简单、安全的自动更新体验！**