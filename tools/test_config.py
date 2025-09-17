#!/usr/bin/env python3
"""
配置验证测试脚本
用于测试配置文件的加载和验证逻辑
"""

import sys
import os
import yaml

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.validators import DataValidator

def test_config_loading():
    """测试配置文件加载"""
    print("🔍 测试配置文件加载和验证...")
    
    # 模拟main.py中的load_config函数
    config = {}
    config_dir = "config/"
    
    config_files = {
        'sources': 'sources.yaml',
        'classification_prompts': 'classification_prompts.yaml', 
        'llm_config': 'llm_config.yaml'
    }
    
    for key, filename in config_files.items():
        file_path = os.path.join(config_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                config[key] = yaml.safe_load(f)
            print(f"✅ 加载配置文件: {filename}")
        else:
            print(f"❌ 配置文件不存在: {file_path}")
    
    print(f"\n📊 配置结构:")
    for key in config.keys():
        print(f"   - {key}: {type(config[key])}")
        if key == 'sources' and 'data_sources' in config[key]:
            sources = list(config[key]['data_sources'].keys())
            print(f"     数据源: {sources}")
        elif key == 'classification_prompts' and 'categories' in config[key]:
            categories = list(config[key]['categories'].keys())
            print(f"     分类数: {len(categories)}")
        elif key == 'llm_config':
            providers = [k for k in config[key].keys() if k not in ['default_classifier', 'classifier_priority', 'batch_processing', 'error_handling', 'quality_control']]
            print(f"     LLM提供商: {providers}")
    
    # 测试验证器
    print(f"\n🧪 测试配置验证...")
    validator = DataValidator()
    
    try:
        is_valid = validator.validate_config(config)
        if is_valid:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            
        return is_valid
        
    except Exception as e:
        print(f"❌ 配置验证出错: {e}")
        return False

def test_specific_validations():
    """测试具体的验证逻辑"""
    print(f"\n🔍 测试具体验证逻辑...")
    
    # 加载sources配置
    with open('config/sources.yaml', 'r', encoding='utf-8') as f:
        sources_config = yaml.safe_load(f)
    
    # 加载llm配置
    with open('config/llm_config.yaml', 'r', encoding='utf-8') as f:
        llm_config = yaml.safe_load(f)
    
    validator = DataValidator()
    
    sources_valid = True  # 默认值
    
    # 测试数据源验证
    if 'data_sources' in sources_config:
        print("📝 测试数据源配置验证...")
        sources_valid = validator.validate_data_sources_config(sources_config['data_sources'])
        print(f"   数据源配置验证: {'✅ 通过' if sources_valid else '❌ 失败'}")
    
    # 测试LLM配置验证
    print("📝 测试LLM配置验证...")
    llm_valid = validator.validate_llm_config(llm_config)
    print(f"   LLM配置验证: {'✅ 通过' if llm_valid else '❌ 失败'}")
    
    return sources_valid and llm_valid

def main():
    print("🚀 配置验证测试")
    print("=" * 50)
    
    # 检查工作目录
    if not os.path.exists('config/'):
        print("❌ 错误: config/ 目录不存在")
        sys.exit(1)
    
    # 测试配置加载
    config_valid = test_config_loading()
    
    # 测试具体验证
    specific_valid = test_specific_validations()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"   配置加载和验证: {'✅ 通过' if config_valid else '❌ 失败'}")
    print(f"   具体验证逻辑: {'✅ 通过' if specific_valid else '❌ 失败'}")
    
    if config_valid and specific_valid:
        print("\n🎉 所有配置验证测试通过！")
        return 0
    else:
        print("\n❌ 配置验证存在问题，请检查配置文件")
        return 1

if __name__ == "__main__":
    sys.exit(main())