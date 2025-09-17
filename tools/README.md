# LLM4Cybersecurity 文档自动更新工具

## 🎯 功能介绍

这是一个为 Awesome-LLM4Cybersecurity 项目设计的自动化文档更新工具，能够：

- 🔍 从多个学术数据源（arXiv、ACM、IEEE等）自动获取最新论文
- 🤖 使用大语言模型对论文进行智能分类
- 📝 自动更新 README.md 文件的分类内容
- ⚙️ 支持配置化的分类提示词和数据源
- 💾 支持缓存机制避免重复处理
- 📊 提供详细的处理日志和统计信息

## 🏗️ 架构设计

```
tools/
├── main.py                  # 主程序入口
├── config/                  # 配置文件目录
│   ├── classification_prompts.yaml  # 分类提示词配置
│   ├── sources.yaml                # 数据源配置
│   └── llm_config.yaml             # LLM配置
├── crawlers/               # 爬虫模块
│   └── arxiv_crawler.py    # arXiv爬虫
├── classifiers/            # 分类器模块
│   └── openai_classifier.py # OpenAI分类器
├── processors/             # 处理器模块
│   ├── paper_processor.py  # 论文处理器
│   └── readme_updater.py   # README更新器
├── utils/                  # 工具模块
│   ├── cache_manager.py    # 缓存管理
│   ├── logger.py          # 日志系统
│   └── validators.py      # 数据验证
├── requirements.txt        # 依赖包
├── run.sh                 # 快速启动脚本
└── test_tool.py           # 测试工具
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 进入工具目录
cd tools

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

编辑 `config/llm_config.yaml` 文件，添加你的 OpenAI API 密钥：

```yaml
openai:
  api_key: "your-api-key-here"
  model: "gpt-3.5-turbo"
  base_url: "https://api.openai.com/v1"
```

### 3. 运行工具

```bash
# 基本运行（获取最近7天的论文）
python main.py

# 预览模式（不实际更新文件）
python main.py --dry-run

# 指定数据源和时间范围
python main.py --sources arxiv --days 3

# 使用快速启动脚本
./run.sh
```

## 📖 详细用法

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config` | 配置文件目录 | `config/` |
| `--sources` | 指定数据源 | 所有可用源 |
| `--days` | 获取最近N天的论文 | 7 |
| `--max-papers` | 每个数据源最大论文数 | 100 |
| `--dry-run` | 预览模式，不实际更新文件 | - |
| `--log-level` | 日志级别 | INFO |
| `--readme-path` | README文件路径 | `../README.md` |
| `--clear-cache` | 清空缓存后再运行 | - |

### 使用示例

```bash
# 获取最近3天的arXiv论文
python main.py --sources arxiv --days 3

# 高详细度日志
python main.py --log-level DEBUG

# 使用自定义配置
python main.py --config ./my_config/

# 清空缓存重新处理
python main.py --clear-cache
```

## ⚙️ 配置文件

### 1. 分类提示词配置 (classification_prompts.yaml)

定义了论文分类的详细规则：

- **RQ1**: 大模型在网络安全中的应用
- **RQ2**: 大模型自身的安全问题  
- **RQ3**: 大模型与传统安全技术的结合

每个分类包含：
- 详细的分类描述
- 关键词列表
- 分类示例
- 置信度标准

### 2. 数据源配置 (sources.yaml)

配置各个学术数据源的参数：

```yaml
arxiv:
  enabled: true
  query: "cat:cs.CR OR cat:cs.AI"
  max_results: 100
  delay: 1.0
```

### 3. LLM配置 (llm_config.yaml)

配置大语言模型参数：

```yaml
openai:
  api_key: "your-api-key"
  model: "gpt-3.5-turbo"
  temperature: 0.1
  max_tokens: 1000
```

## 🔧 开发和测试

### 运行测试

```bash
# 运行完整测试套件
python test_tool.py

# 测试特定模块（示例）
python -c "from crawlers.arxiv_crawler import ArxivCrawler; print('导入成功')"
```

### 日志调试

工具会在 `logs/` 目录下生成详细的日志文件：

- `app.log`: 主要日志文件
- `debug.log`: 调试级别日志
- `error.log`: 错误日志

### 缓存管理

- 缓存文件存储在 `cache/` 目录
- 使用 `--clear-cache` 清空缓存
- 缓存包括API响应和处理状态

## 🎨 自定义扩展

### 添加新的数据源

1. 在 `crawlers/` 目录创建新的爬虫类
2. 继承基础爬虫接口
3. 在 `config/sources.yaml` 中添加配置
4. 在主程序中注册新的爬虫

### 添加新的分类器

1. 在 `classifiers/` 目录创建新的分类器
2. 实现统一的分类接口
3. 在配置文件中添加相关配置

### 自定义分类规则

编辑 `config/classification_prompts.yaml` 文件：

1. 修改现有分类的描述和关键词
2. 添加新的子分类
3. 调整置信度阈值

## 📊 输出说明

工具运行后会输出：

1. **处理统计**: 获取论文数、分类成功数、更新条目数
2. **分类分布**: 各个分类的论文分布情况
3. **处理日志**: 详细的处理过程记录
4. **错误报告**: 失败的论文和原因

## ❓ 常见问题

### Q: API配额不足怎么办？
A: 可以调整 `max_papers` 参数限制处理数量，或使用缓存避免重复处理。

### Q: 分类结果不准确怎么办？
A: 可以编辑 `classification_prompts.yaml` 文件优化提示词和关键词。

### Q: 如何添加新的论文来源？
A: 参考 `arxiv_crawler.py` 实现新的爬虫类，并在配置中启用。

### Q: 工具运行很慢怎么办？
A: 可以调整数据源的 `delay` 参数，或限制 `max_papers` 数量。

## 🤝 贡献指南

欢迎提交 Pull Request 或 Issue！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

遵循项目主仓库的许可证。