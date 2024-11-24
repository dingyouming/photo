# 智能照片管理系统

基于第一性原理设计的照片管理系统，使用 OneDrive 作为核心存储，提供可靠的备份机制和智能管理功能。

## 系统特点

### 1. 可靠存储
- OneDrive 作为主存储（5TB）
- 可选备份云盘支持
- 自动同步和备份策略

### 2. 智能管理
- 自动元数据提取
- 智能标签系统
- 基于内容的检索

### 3. 灵活架构
- 模块化设计
- 多云盘备份支持
- 统一管理接口

## 系统架构
```
Core
├── Storage/          # 存储层
│   ├── OneDrive/     # 主存储
│   ├── Backup/       # 备份存储
│   └── Interface/    # 统一接口
├── Photo/            # 照片核心
│   ├── Metadata/     # 元数据
│   └── Content/      # 内容分析
└── Collection/       # 集合管理
```

## 存储策略

### 主存储 (OneDrive)
```
OneDrive/
├── Photos/           # 照片存储
│   ├── Original/     # 原始文件
│   └── Processed/    # 处理后文件
├── Metadata/         # 元数据存储
└── System/           # 系统配置
```

### 备份存储
- 支持配置第二个云盘作为备份
- 自动同步重要数据
- 定期验证数据完整性

## 功能路线图

### 第一阶段：基础功能
- [x] OneDrive 集成
- [x] 基本元数据提取
- [ ] 文件组织结构

### 第二阶段：增强功能
- [ ] 备份云盘集成
- [ ] 智能分析和标签
- [ ] 高级搜索功能

### 第三阶段：高级功能
- [ ] 自动备份策略
- [ ] AI 辅助整理
- [ ] 多设备同步

## 快速开始

1. 环境准备
```bash
# 安装 Python 3.9+
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. OneDrive 配置
```bash
# 配置 OneDrive 连接
python manage.py configure_onedrive
```

3. 运行应用
```bash
python manage.py runserver
```

## 开发指南

- [开发环境搭建](docs/development.md)
- [OneDrive 集成指南](docs/onedrive.md)
- [备份策略说明](docs/backup.md)
- [API 文档](docs/api.md)

## 维护说明

- 监控 OneDrive 同步状态
- 验证备份完整性
- 检查存储空间使用
- 更新系统依赖
- 查看错误日志
