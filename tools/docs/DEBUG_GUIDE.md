# 调试日志使用指南

## 🎯 概述

LLM4Cybersecurity 工具支持详细的调试日志功能，可以帮助你：
- 🔍 **监控实时状态**: 跟踪论文获取、分类、更新的每个步骤
- 🐛 **排查问题**: 快速定位网络请求、API调用、数据验证等问题
- 📊 **性能分析**: 了解各个环节的耗时和效率
- 🎯 **优化配置**: 根据日志调整搜索词、分类规则等参数

## 🚀 启用调试日志

### 基本用法

```bash
# 启用DEBUG级别日志
python main.py --log-level DEBUG

# 结合预览模式，查看详细过程但不实际更新
python main.py --log-level DEBUG --dry-run

# 限制论文数量，快速测试
python main.py --log-level DEBUG --max-papers 5 --days 1
```

### 日志级别说明

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| `ERROR` | 仅显示错误信息 | 生产环境，只关注错误 |
| `WARNING` | 显示警告和错误 | 一般监控 |
| `INFO` | 显示关键流程信息 | 日常使用，了解主要进展 |
| `DEBUG` | 显示详细调试信息 | 开发调试，问题排查 |

## 📋 调试日志内容

### 1. 论文获取阶段

```
🔍 搜索配置信息:
2025-01-17 10:30:15 - main - DEBUG - 搜索截止日期: 2025-01-10 10:30:15
2025-01-17 10:30:15 - main - DEBUG - 使用爬虫配置: {'base_url': '...', 'max_results': 50}

🔍 网络请求详情:
2025-01-17 10:30:16 - arxiv_crawler - DEBUG - 发送请求到: http://export.arxiv.org/api/query
2025-01-17 10:30:16 - arxiv_crawler - DEBUG - 请求参数: search_query='cybersecurity AND LLM', max_results=50
2025-01-17 10:30:17 - arxiv_crawler - DEBUG - 收到响应，状态码: 200
2025-01-17 10:30:17 - arxiv_crawler - DEBUG - 响应内容长度: 25467 字符

🔍 数据处理过程:
2025-01-17 10:30:17 - arxiv_crawler - DEBUG - 开始解析XML响应...
2025-01-17 10:30:17 - arxiv_crawler - DEBUG - XML解析完成，获得 12 篇论文
2025-01-17 10:30:17 - arxiv_crawler - DEBUG - 开始过滤网络安全相关论文...
2025-01-17 10:30:17 - arxiv_crawler - DEBUG -   ✅ 第1篇相关: Large Language Models for Vulnerability...
2025-01-17 10:30:17 - arxiv_crawler - DEBUG -   ❌ 第2篇不相关: Computer Vision Applications...
```

### 2. 缓存管理

```
🔍 缓存状态:
2025-01-17 10:30:18 - main - DEBUG - 缓存统计 - 已处理: 15, 已失败: 3, 新论文: 8
2025-01-17 10:30:18 - main - DEBUG - 跳过已处理论文: Advanced Persistent Threats...
2025-01-17 10:30:18 - main - DEBUG - 跳过失败论文: Malformed Paper Title...
2025-01-17 10:30:18 - main - DEBUG - 新论文待处理: GPT-4 for Cybersecurity...
```

### 3. 数据验证过程

```
🔍 论文验证:
2025-01-17 10:30:19 - main - DEBUG - 验证论文 1/8: Large Language Models for...
2025-01-17 10:30:19 - main - DEBUG -   ✅ 验证通过
2025-01-17 10:30:19 - main - DEBUG - 验证论文 2/8: Short Title...
2025-01-17 10:30:19 - main - DEBUG -   ❌ 验证失败
2025-01-17 10:30:19 - main - DEBUG - 验证统计 - 通过: 7, 失败: 1
```

### 4. 分类过程详情

```
🔍 分类处理:
2025-01-17 10:30:20 - main - DEBUG - 加载分类配置: 29 个类别
2025-01-17 10:30:20 - main - INFO - 分类论文 1/7: Large Language Models for Cybersecurity...
2025-01-17 10:30:20 - main - DEBUG -   论文作者: John Smith, Alice Johnson, Bob Wilson...
2025-01-17 10:30:20 - main - DEBUG -   发布日期: 2025-01-16
2025-01-17 10:30:20 - main - DEBUG -   摘要长度: 1245 字符
2025-01-17 10:30:20 - main - DEBUG -   开始调用分类器...
2025-01-17 10:30:25 - main - DEBUG -   分类器返回结果: RQ1/Vulnerabilities Detection
2025-01-17 10:30:25 - main - DEBUG -   论文处理完成
2025-01-17 10:30:25 - main - INFO -   -> 分类为: Vulnerabilities Detection (置信度: 0.85)
2025-01-17 10:30:25 - main - DEBUG -   -> 分类推理: The paper focuses on using large language models...
```

### 5. API调用监控

```
🔍 API调用详情:
2025-01-17 10:30:25 - openai_classifier - DEBUG - 发送分类请求到OpenAI API
2025-01-17 10:30:25 - openai_classifier - DEBUG - 请求参数: model=gpt-3.5-turbo, temperature=0.1
2025-01-17 10:30:30 - openai_classifier - DEBUG - API响应成功，用时: 4.8秒
2025-01-17 10:30:30 - openai_classifier - DEBUG - 使用token数: 1250
2025-01-17 10:30:30 - main - DEBUG - 等待0.5秒避免API调用过于频繁...
```

## 🛠️ 常见问题排查

### 1. 网络连接问题

**症状**: 获取论文失败
```bash
2025-01-17 10:30:15 - arxiv_crawler - ERROR - arXiv请求超时: HTTPSConnectionPool...
```

**排查方法**:
```bash
# 启用详细网络日志
python main.py --log-level DEBUG --sources arxiv --max-papers 1

# 检查日志中的网络请求详情
grep "发送请求到" logs/debug.log
grep "收到响应" logs/debug.log
```

### 2. API调用问题

**症状**: 分类失败
```bash
2025-01-17 10:30:25 - openai_classifier - ERROR - OpenAI API调用失败: 401 Unauthorized
```

**排查方法**:
```bash
# 检查API密钥配置
echo $OPENAI_API_KEY

# 查看API调用详情
python main.py --log-level DEBUG --dry-run
grep "API" logs/debug.log
```

### 3. 数据验证失败

**症状**: 很多论文被过滤掉
```bash
2025-01-17 10:30:19 - main - DEBUG - 验证统计 - 通过: 2, 失败: 15
```

**排查方法**:
```bash
# 查看具体的验证失败原因
python main.py --log-level DEBUG --max-papers 5
grep "验证失败" logs/debug.log
```

### 4. 分类效果不佳

**症状**: 置信度普遍较低
```bash
2025-01-17 10:30:25 - main - INFO - -> 分类为: General Application (置信度: 0.45)
```

**排查方法**:
```bash
# 查看分类推理过程
python main.py --log-level DEBUG --max-papers 3
grep "分类推理" logs/debug.log

# 检查分类配置
grep "加载分类配置" logs/debug.log
```

## 📁 日志文件管理

### 日志文件位置

```
logs/
├── update_20250117.log          # 主日志文件
├── debug_test.log               # 调试测试日志
├── test_info.log               # INFO级别测试
└── test_debug.log              # DEBUG级别测试
```

### 日志文件大小管理

```bash
# 查看日志文件大小
ls -lh logs/

# 清理旧日志文件
find logs/ -name "*.log" -mtime +7 -delete

# 压缩大日志文件
gzip logs/update_*.log
```

## 🎯 最佳实践

### 1. 开发调试

```bash
# 快速测试新功能
python main.py --log-level DEBUG --dry-run --max-papers 3 --days 1

# 测试特定搜索词效果
python main.py --log-level DEBUG --sources arxiv --max-papers 10
```

### 2. 生产监控

```bash
# 正常运行时使用INFO级别
python main.py --log-level INFO

# 定期检查错误日志
grep "ERROR" logs/update_*.log

# 监控API使用情况
grep "API" logs/update_*.log | grep "token"
```

### 3. 性能优化

```bash
# 分析响应时间
grep "用时" logs/debug.log

# 检查缓存命中率
grep "缓存统计" logs/debug.log

# 监控网络请求效率
grep "响应内容长度" logs/debug.log
```

## 🔧 自定义日志配置

### 创建自定义日志配置

```python
# custom_debug.py
from utils.logger import setup_logger

# 创建专门的调试记录器
debug_logger = setup_logger("custom_debug", "DEBUG", "logs/custom_debug.log")

# 在代码中使用
debug_logger.debug("自定义调试信息")
debug_logger.info("重要信息")
```

### 过滤特定模块日志

```bash
# 只查看爬虫相关日志
grep "arxiv_crawler" logs/debug.log

# 只查看分类相关日志
grep "classifier" logs/debug.log

# 只查看API调用日志
grep "API" logs/debug.log
```

## 📊 日志分析脚本

创建简单的日志分析脚本：

```bash
#!/bin/bash
# analyze_logs.sh

echo "🔍 日志分析报告"
echo "=================="

echo "📊 论文处理统计:"
grep "获取到.*篇论文" logs/update_*.log | tail -5

echo "📊 分类成功率:"
grep "分类完成" logs/update_*.log | tail -5

echo "📊 API调用情况:"
grep "API响应成功" logs/debug.log | wc -l
echo "成功调用次数: $(grep "API响应成功" logs/debug.log | wc -l)"

echo "📊 错误统计:"
grep "ERROR" logs/update_*.log | wc -l
echo "错误数量: $(grep "ERROR" logs/update_*.log | wc -l)"
```

使用方法：
```bash
chmod +x analyze_logs.sh
./analyze_logs.sh
```

---

通过详细的调试日志，你可以完全掌控工具的运行状态，快速发现和解决问题，持续优化工具的性能和效果！🎉