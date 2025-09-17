#!/usr/bin/env python3
"""
简单的配置检查脚本
"""

import sys
import os
import yaml
import traceback

def test_basic_config_loading():
    """测试基础配置加载"""
    print("🔍 测试基础配置加载...")
    
    try:
        # 检查工作目录
        print(f"当前目录: {os.getcwd()}")
        print(f"config目录存在: {os.path.exists('config/')}")
        
        if not os.path.exists('config/'):
            print("❌ config目录不存在")
            return False
        
        # 检查配置文件
        config_files = [
            'config/classification_prompts.yaml',
            'config/sources.yaml',
            'config/llm_config.yaml'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                print(f"✅ {config_file} 加载成功")
                print(f"   顶层键: {list(config.keys())}")
            else:
                print(f"❌ {config_file} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        traceback.print_exc()
        return False

def test_main_py_config():
    """测试main.py的配置访问"""
    print("\n🔍 测试main.py配置访问...")
    
    try:
        # 添加项目路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from main import load_config
        config = load_config('config/')
        
        print("配置加载成功，结构如下:")
        for key in config.keys():
            print(f"  {key}: {type(config[key])}")
            if isinstance(config[key], dict):
                print(f"    子键: {list(config[key].keys())}")
        
        # 测试修复后的访问路径
        print("\n测试配置访问路径:")
        
        # 1. 测试classification_prompts访问
        try:
            classification_config = config['classification_prompts']['classification_prompts']
            categories_config = classification_config['categories']
            print(f"✅ classification_prompts 访问成功: {len(categories_config)} 个分类")
        except KeyError as e:
            print(f"❌ classification_prompts 访问失败: {e}")
            return False
        
        # 2. 测试llm_config访问
        try:
            llm_config = config['llm_config']['openai']
            print(f"✅ llm_config 访问成功: {list(llm_config.keys())}")
        except KeyError as e:
            print(f"❌ llm_config 访问失败: {e}")
            return False
        
        # 3. 测试sources访问
        try:
            arxiv_config = config['sources']['data_sources'].get('arxiv', {})
            print(f"✅ sources 访问成功: arxiv enabled={arxiv_config.get('enabled', 'N/A')}")
        except KeyError as e:
            print(f"❌ sources 访问失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ main.py配置测试失败: {e}")
        traceback.print_exc()
        return False

def test_classifier_config():
    """测试分类器配置访问"""
    print("\n🔍 测试分类器配置访问...")
    
    try:
        # 直接加载分类提示词配置
        with open('config/classification_prompts.yaml', 'r', encoding='utf-8') as f:
            prompt_config = yaml.safe_load(f)
        
        print(f"提示词配置结构: {list(prompt_config.keys())}")
        
        # 测试分类器中使用的访问路径
        try:
            system_prompt = prompt_config['classification_prompts']['system_prompt']
            print("✅ system_prompt 访问成功")
        except KeyError as e:
            print(f"❌ system_prompt 访问失败: {e}")
            return False
        
        try:
            categories = prompt_config['classification_prompts']['categories']
            print(f"✅ categories 访问成功: {len(categories)} 个分类")
        except KeyError as e:
            print(f"❌ categories 访问失败: {e}")
            return False
        
        try:
            template = prompt_config['classification_prompts']['base_prompt_template']
            print("✅ base_prompt_template 访问成功")
        except KeyError as e:
            print(f"❌ base_prompt_template 访问失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 分类器配置测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    print("🎯 简单配置BUG检查")
    print("=" * 50)
    
    tests = [
        ("基础配置加载", test_basic_config_loading),
        ("main.py配置访问", test_main_py_config),
        ("分类器配置访问", test_classifier_config)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    all_passed = True
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！配置访问正常。")
    else:
        print("⚠️ 发现问题！需要进一步检查。")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())