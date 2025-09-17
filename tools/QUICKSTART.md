# 快速开始指南

## 🚀 一键安装和配置

```bash
# 进入工具目录
cd tools

# 运行安装脚本（自动配置环境和依赖）
./setup.sh
```

## ⚙️ 配置API密钥

编辑配置文件添加你的OpenAI API密钥：

```bash
# 复制示例配置
cp config/llm_config.yaml.example config/llm_config.yaml

# 编辑配置文件
vi config/llm_config.yaml
```

在文件中找到以下行并替换API密钥：
```yaml
openai:
  api_key: "your-openai-api-key-here"  # 替换为你的API密钥
```

## 🎯 开始使用

```bash
# 预览模式（不实际更新文件）
python main.py --dry-run

# 获取最近3天的论文
python main.py --days 3

# 正式运行（获取最近7天的论文并更新README）
python main.py

# 只从arXiv获取论文
python main.py --sources arxiv

# 清空缓存重新处理
python main.py --clear-cache
```

## 📊 主要功能

- ✅ **自动爬取**: 从arXiv等学术数据源获取最新论文
- ✅ **智能分类**: 使用GPT等大模型对论文进行智能分类
- ✅ **自动更新**: 将分类结果自动更新到README.md文件
- ✅ **配置化**: 支持自定义分类规则和数据源
- ✅ **缓存机制**: 避免重复处理，提高效率

## 🔧 高级用法

```bash
# 查看所有选项
python main.py --help

# 使用自定义配置目录
python main.py --config ./my_config/

# 设置最大论文数量
python main.py --max-papers 50

# 设置日志级别
python main.py --log-level DEBUG

# 指定README文件路径
python main.py --readme-path ../README.md
```

## 🧪 测试和演示

```bash
# 运行功能测试
python test_tool.py

# 查看演示
python demo.py
```

## 📖 详细文档

- `README.md` - 完整使用文档
- `PROJECT_SUMMARY.md` - 项目总结和技术细节
- `config/` - 配置文件说明

## ❓ 常见问题

**Q: API调用失败怎么办？**
A: 检查API密钥是否正确配置，确保有足够的配额

**Q: 分类结果不准确怎么办？**
A: 可以编辑 `config/classification_prompts.yaml` 优化分类规则

**Q: 如何添加新的论文来源？**
A: 参考 `arxiv_crawler.py` 实现新的爬虫类

---
🎉 **恭喜！你已经成功配置了LLM4Cybersecurity自动化文档更新工具！**