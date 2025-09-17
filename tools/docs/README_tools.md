# LLM4Cybersecurity 文档自动更新工具

## 📋 项目简介

本工具是为 Awesome-LLM4Cybersecurity 项目开发的自动化文档更新系统，能够从多个学术数据源自动获取最新论文，使用大语言模型进行智能分类，并自动更新到 README.md 的相应分类中。

## 🏗️ 架构设计

```
tools/
├── config/                           # 配置文件目录
│   ├── sources.yaml                 # 数据源配置
│   ├── classification_prompts.yaml  # 分类提示词配置  
│   ├── llm_config.yaml             # LLM API配置
│   └── classification_examples.yaml # 分类示例和测试用例
├── crawlers/                        # 爬虫模块
│   ├── base_crawler.py             # 爬虫基类
│   ├── arxiv_crawler.py            # arXiv爬虫
│   ├── acm_crawler.py              # ACM Digital Library爬虫
│   └── ieee_crawler.py             # IEEE Xplore爬虫
├── classifiers/                     # 分类器模块
│   ├── base_classifier.py          # 分类器基类
│   └── openai_classifier.py        # OpenAI分类器
├── processors/                     # 处理器模块
│   ├── paper_processor.py          # 论文数据处理
│   └── readme_updater.py           # README更新器
├── utils/                          # 工具模块
│   ├── logger.py                   # 日志工具
│   ├── cache.py                    # 缓存工具
│   └── validators.py               # 数据验证工具
├── main.py                         # 主程序入口
├── requirements.txt                # 依赖包列表
└── README_tools.md                # 本文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <项目地址>
cd Awesome-LLM4Cybersecurity/tools

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export OPENAI_API_KEY="your-openai-api-key"
export IEEE_API_KEY="your-ieee-api-key"  # 可选
```

### 2. 配置设置

编辑 `config/llm_config.yaml` 文件，确保API密钥正确配置：

```yaml
openai:
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-3.5-turbo"
  temperature: 0.1
  max_tokens: 800
```

### 3. 运行工具

```bash
# 获取最近7天的论文并自动分类更新
python main.py

# 仅从arXiv获取最近3天的论文
python main.py --sources arxiv --days 3

# 预览模式，查看分类结果但不更新文件
python main.py --dry-run

# 指定自定义配置目录
python main.py --config ./my_config/
```

## 📊 分类系统详解

### 主要分类 (RQ1-RQ3)

#### RQ1: 如何构建面向网络安全的领域专用大语言模型？

- **网络安全评估基准** (Cybersecurity Evaluation Benchmarks)
  - 创建评估数据集和基准测试
  - CTF、渗透测试评估
  - 安全知识评估框架

- **面向网络安全的微调领域大语言模型** (Fine-tuned Domain LLMs for Cybersecurity)
  - 网络安全领域模型微调
  - 专门的安全模型训练
  - 指令调优和参数优化

#### RQ2: 大语言模型在网络安全中有哪些潜在应用？

- **威胁情报** (Threat Intelligence)
  - 威胁分析和情报收集
  - 恶意软件分析
  - 攻击归因和溯源

- **模糊测试** (FUZZ)
  - 智能测试用例生成
  - 协议模糊测试
  - API安全测试

- **漏洞检测** (Vulnerabilities Detection)
  - 代码漏洞自动检测
  - 智能合约安全分析
  - 二进制漏洞发现

- **不安全代码生成** (Insecure code Generation)
  - 代码生成安全性评估
  - 恶意代码检测
  - 安全编码实践

- **程序修复** (Program Repair)
  - 自动漏洞修复
  - 代码缺陷修补
  - 安全补丁生成

- **异常检测** (Anomaly Detection)
  - 网络异常监测
  - 日志异常分析
  - 入侵检测系统

- **大语言模型辅助攻击** (LLM Assisted Attack)
  - 渗透测试自动化
  - 攻击模拟
  - 社会工程学攻击

- **其他应用** (Others)
  - 网络安全教育
  - 合规性检查
  - 数字取证

#### RQ3: 进一步研究方向

- **网络安全智能体研究** (Further Research: Agent4Cybersecurity)
  - 多智能体协作安全系统
  - 自主安全决策
  - 智能体安全框架

### 分类算法特点

1. **多层次分类**：先确定主分类(RQ1-3)，再细化到具体子分类
2. **置信度评估**：每个分类结果都有置信度分数
3. **关键词优先级**：基于预定义关键词进行优先级调整
4. **智能后处理**：应用规则过滤和验证机制
5. **人工审核**：低置信度结果可标记为需要人工审核

## 🔧 配置文件详解

### 1. 数据源配置 (sources.yaml)

```yaml
data_sources:
  arxiv:
    enabled: true
    base_url: "http://export.arxiv.org/api/query"
    search_terms:
      - "cybersecurity AND large language model"
      - "LLM AND vulnerability detection"
    max_results: 50
    update_frequency: "daily"
```

### 2. 分类提示词配置 (classification_prompts.yaml)

详细定义了每个分类的：
- 描述信息
- 关键词列表  
- 示例论文
- 分类指导原则

### 3. LLM配置 (llm_config.yaml)

```yaml
openai:
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-3.5-turbo"
  temperature: 0.1
  max_tokens: 800
  timeout: 30
  max_retries: 3
```

## 📈 使用示例

### 1. 基础使用

```bash
# 每日更新 - 获取最近1天的论文
python main.py --days 1

# 周更新 - 获取最近7天的论文
python main.py --days 7

# 月更新 - 获取最近30天的论文  
python main.py --days 30
```

### 2. 高级功能

```bash
# 仅测试分类效果，不实际更新文件
python main.py --dry-run --days 3

# 从特定数据源获取
python main.py --sources arxiv acm --days 5

# 使用自定义配置
python main.py --config /path/to/custom/config --days 7
```

### 3. 定期自动化

设置 cron 任务进行定期更新：

```bash
# 每天凌晨2点自动更新
0 2 * * * cd /path/to/project/tools && python main.py --days 1 >> logs/daily_update.log 2>&1

# 每周日凌晨进行全面更新
0 3 * * 0 cd /path/to/project/tools && python main.py --days 7 >> logs/weekly_update.log 2>&1
```

## 🎯 分类质量保证

### 1. 质量指标

- **准确率目标**: 总体85%以上
- **置信度目标**: 平均70%以上  
- **一致性目标**: 多次运行95%以上一致

### 2. 质量控制机制

- **多轮验证**: 低置信度结果会触发重新分类
- **关键词过滤**: 基于预定义规则进行后处理
- **人工审核**: 复杂情况标记为需要人工确认
- **测试用例**: 基于已知论文进行算法验证

### 3. 错误处理

- **API失败**: 自动重试和降级处理
- **分类失败**: 回退到关键词分类
- **格式错误**: 自动修复和标准化
- **重复检测**: 基于URL和标题去重

## 🔍 监控与日志

### 日志级别

- **INFO**: 正常运行信息
- **WARNING**: 需要注意的问题
- **ERROR**: 错误和异常情况
- **DEBUG**: 详细调试信息

### 监控指标

- 论文获取成功率
- 分类准确率和置信度分布
- API调用成功率和响应时间
- 文件更新状态

## 🤝 贡献指南

### 1. 添加新数据源

1. 继承 `BaseCrawler` 类
2. 实现 `search_papers` 和 `get_paper_details` 方法
3. 在 `sources.yaml` 中添加配置
4. 在 `main.py` 中注册新爬虫

### 2. 改进分类算法

1. 更新 `classification_prompts.yaml` 中的提示词
2. 添加新的关键词和规则
3. 在 `classification_examples.yaml` 中添加测试用例
4. 运行测试验证改进效果

### 3. 扩展功能

- 添加新的LLM API支持
- 改进README更新逻辑
- 增加统计分析功能
- 优化缓存和性能

## 📞 技术支持

如有问题或建议，请：

1. 查看日志文件了解详细错误信息
2. 检查配置文件设置是否正确
3. 确认API密钥和网络连接
4. 提交Issue描述问题和复现步骤

## 📄 许可证

本工具遵循与主项目相同的开源许可证。