# 服务器硬件配置信息

## CPU 信息
- 处理器型号：AMD EPYC 7551 32-Core Processor
- CPU 架构：x86_64
- CPU 核心数：2（1个物理核心，支持2线程）
- 虚拟化支持：AMD-V
- 虚拟化类型：KVM（全虚拟化）
- 缓存信息：
  - L1d 缓存：64 KiB
  - L1i 缓存：64 KiB
  - L2 缓存：512 KiB
  - L3 缓存：16 MiB

## 内存信息
- 总内存：956 MB
- 已使用：722 MB
- 可用内存：234 MB
- 缓存：256 MB
- SWAP：未配置

## 存储信息
主硬盘 (/dev/sda)：
- 总容量：46.58 GB
- 磁盘型号：BlockVolume
- 分区情况：
  - /dev/sda1：45.6G (Linux filesystem)
  - /dev/sda14：4M (BIOS boot)
  - /dev/sda15：106M (EFI System)
  - /dev/sda16：913M (Linux extended boot)
- 扇区大小：逻辑 512 bytes / 物理 4096 bytes
- I/O 大小：最小 4096 bytes / 最优 1048576 bytes

## PC 配置信息
### 系统信息
- 操作系统：Windows 10 Pro
- 系统版本：10.0.19045
- 系统架构：64-bit

### 处理器
- 型号：Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz
- 物理核心数：4
- 逻辑处理器数：8

### 内存
- 总内存：16 GB RAM

### 存储空间
- C盘（系统盘）
  - 总容量：237.30 GB
  - 可用空间：15.10 GB
  - 文件系统：NTFS
- D盘（数据盘）
  - 总容量：931.51 GB
  - 可用空间：435.62 GB
  - 文件系统：NTFS

### 存储资源
- 本地存储：约 1.17 TB (C盘 + D盘)
- Google Drive：15 GB
- OneDrive：5 TB
- 百度网盘：[容量待确认]

## 性能注意事项
1. CPU 限制：
   - 仅有 2 个虚拟核心，适合轻量级应用
   - 支持主流虚拟化技术，可用于容器化部署

2. 内存限制：
   - 总内存较小（956MB），需要注意内存密集型应用的使用
   - 未配置 SWAP，需要谨慎监控内存使用

3. 存储限制：
   - 系统盘容量适中（46.58GB）
   - 使用 SSD 块存储，I/O 性能较好

## 服务器用途更新
### 主要功能
- Rclone 云存储管理服务器
- 统一管理各个云存储平台
- 自动化文件同步和整理

### 资源分配
1. CPU 使用：
   - Rclone 同步任务
   - 文件处理和整理
   - 自动化脚本运行

2. 内存使用（总计 956MB）：
   - Rclone 服务：约 200MB
   - 系统保留：约 400MB
   - 其他进程：约 356MB
   - Swap空间：2GB（已配置）

3. 存储使用（总计 46.58GB）：
   - 系统占用：约 5GB
   - Rclone 缓存：约 10GB
   - 临时文件：约 5GB
   - 预留空间：约 26.58GB

### 网络使用
- 主要用于云存储之间的数据传输
- 支持多线程传输
- 带宽限制设置防止占用过多资源

## 建议用途
- Web 服务托管
- 开发环境
- 小型应用部署
- 测试环境

## 最后更新
- 日期：2024-01-09
- 备注：首次硬件信息收集
