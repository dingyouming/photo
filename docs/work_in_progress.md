# Rclone 云存储管理系统实施清单

## 1. Rclone 安装和基础配置
- [x] 安装 Rclone
  - [x] 下载最新版本
  - [x] 验证安装
  - [x] 检查版本信息
- [ ] 配置 OneDrive（主存储）
  - [x] 创建专用 OneDrive 账号
    - [x] 在 E3 管理中心创建新用户
    - [x] 分配 OneDrive 许可证
    - [x] 设置存储配额
  - [x] 获取 OneDrive API 凭证
    - [x] 在 Azure AD 中注册应用
    - [x] 配置应用权限
    - [x] 获取 Client ID 和 Secret
  - [ ] 运行 rclone config
  - [ ] 测试连接
- [ ] 配置其他云存储
  - [ ] Google Drive
  - [ ] 百度网盘

## 2. 存储结构设置
- [ ] 在 OneDrive 创建基础目录结构
```
OneDrive/
├── Documents/
│   ├── Work/
│   └── Personal/
├── Media/
│   ├── Photos/
│   ├── Videos/
│   └── Music/
├── Backups/
│   ├── PC_Backup/
│   ├── Google_Drive/
│   └── BaiduPan/
└── Archive/
    └── Old_Files/
```

## 3. 自动化脚本开发
- [ ] 创建脚本目录结构
- [ ] 开发同步脚本
  - [ ] 日常同步
  - [ ] 增量备份
  - [ ] 错误处理
- [ ] 开发监控脚本
  - [ ] 存储空间检查
  - [ ] 同步状态监控
  - [ ] 错误日志收集

## 4. 数据库优化和升级
- [x] SQLAlchemy 2.0 兼容性
  - [x] 更新 as_declarative 导入路径
  - [x] 使用新式 API
  - [x] 修复弃用警告
- [x] 时间戳处理优化
  - [x] 使用 timezone-aware datetime
  - [x] 替换 utcnow 为 now(UTC)
- [x] 异步关系加载优化
  - [x] 实现 selectinload 模式
  - [x] 优化多对多关系查询
  - [x] 减少 N+1 查询问题
- [ ] 性能监控
  - [ ] 添加查询性能日志
  - [ ] 实现慢查询分析
  - [ ] 设置性能基准
- [ ] 数据迁移
  - [ ] 创建版本控制迁移脚本
  - [ ] 实现自动化迁移流程
  - [ ] 添加回滚机制

## 5. 系统集成
- [ ] 设置定时任务
  - [ ] 配置 crontab
  - [ ] 设置日志轮转
- [ ] 配置系统监控
  - [ ] 资源使用监控
  - [ ] 告警机制

## 6. 测试和验证
- [ ] 基础功能测试
  - [ ] 文件上传/下载
  - [ ] 同步功能
  - [ ] 错误恢复
- [ ] 性能测试
  - [ ] 带宽使用
  - [ ] 资源消耗
- [ ] 自动化测试
  - [ ] 脚本运行
  - [ ] 错误处理

## 7. 文档更新
- [ ] 更新配置文档
- [ ] 编写使用手册
- [ ] 记录注意事项

## Azure AD 应用配置详细步骤

### 1. 访问 Azure Portal
- 打开浏览器，访问 https://portal.azure.com
- 使用 E3 管理员账号登录

### 2. 进入 Azure Active Directory
- 在顶部搜索栏中输入 "Azure Active Directory"
- 点击搜索结果中的 "Azure Active Directory"

### 3. 注册新应用
- 在左侧菜单中点击 "应用注册"
- 点击顶部的 "+ 新注册" 按钮
- 填写注册信息：
  * 名称：`Rclone Storage Manager`
  * 支持的账户类型：选择 "仅限此组织目录中的帐户"
  * 重定向 URI：
    - 平台选择 "Web"
    - URI 填写：`http://localhost:53682/`
- 点击 "注册" 按钮

### 4. 配置 API 权限
- 在应用页面左侧菜单中点击 "API 权限"
- 点击 "+ 添加权限"
- 选择 "Microsoft Graph"
- 选择 "委托的权限"
- 添加以下权限：
  * Files.Read.All
  * Files.ReadWrite.All
  * offline_access
  * User.Read
- 点击 "添加权限"
- 点击 "代表 xxx 授予管理员同意"
- 确认授权

### 5. 创建客户端密码
- 点击左侧 "证书和密码"
- 在 "客户端密码" 部分点击 "+ 新客户端密码"
- 设置：
  * 描述：`Rclone Access`
  * 过期时间：24 个月
- 点击 "添加"
- **立即保存生成的密码值！**（只显示一次）

### 6. 获取应用程序 ID
- 在应用 "概述" 页面
- 复制 "应用程序(客户端) ID"

## 进度记录

### 当前任务
- 运行 rclone config 配置 OneDrive
- 测试连接

### 已完成任务
- [x] 安装 Rclone
  - [x] 下载最新版本 (v1.68.2)
  - [x] 验证安装
  - [x] 检查版本信息
- [x] 创建专用 OneDrive 账号
  - [x] 在 E3 管理中心创建新用户
  - [x] 分配 OneDrive 许可证
  - [x] 设置存储配额
- [x] 获取 OneDrive API 凭证
  - [x] 在 Azure AD 中注册应用
  - [x] 配置应用权限
  - [x] 获取并安全保存 Client ID 和 Secret

### 遇到的问题
无

### 解决方案
无
