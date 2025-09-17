#!/usr/bin/env python3
"""
配置路径BUG检查脚本
全面检查所有配置访问路径是否正确
"""

import sys
import os
import yaml
import traceback

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_main_py_config_access():
    """检查main.py中的配置访问"""
    print("🔍 检查main.py中的配置访问")
    print("=" * 50)
    
    try:
        from main import load_config
        config = load_config('config/')
        
        # 检查已修复的路径
        try:
            classification_config = config['classification_prompts']['classification_prompts']
            categories_config = classification_config['categories']
            print(f"✅ classification_prompts访问正确: {len(categories_config)} 个分类")
        except KeyError as e:
            print(f"❌ classification_prompts访问错误: {e}")
            return False
        
        # 检查llm_config访问
        try:
            llm_config = config['llm_config']['openai']
            print(f"✅ llm_config['openai']访问正确: {list(llm_config.keys())}")
        except KeyError as e:
            print(f"❌ llm_config['openai']访问错误: {e}")
            return False
        
        # 检查sources访问
        try:
            arxiv_config = config['sources']['data_sources'].get('arxiv', {})
            print(f"✅ sources['data_sources']['arxiv']访问正确: enabled={arxiv_config.get('enabled', 'N/A')}")
        except KeyError as e:
            print(f"❌ sources['data_sources']['arxiv']访问错误: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ main.py配置访问检查失败: {e}")
        return False

def check_classifier_config_access():
    """检查分类器中的配置访问"""
    print("\n🔍 检查分类器中的配置访问")
    print("=" * 50)
    
    try:
        # 模拟分类器的配置加载方式
        with open('config/classification_prompts.yaml', 'r', encoding='utf-8') as f:
            prompt_config = yaml.safe_load(f)
        
        # 检查system_prompt访问
        try:
            system_prompt = prompt_config['classification_prompts']['system_prompt']
            print(f"✅ prompt_config['classification_prompts']['system_prompt']访问正确")
        except KeyError as e:
            print(f"❌ prompt_config['classification_prompts']['system_prompt']访问错误: {e}")
            return False
        
        # 检查categories访问
        try:
            categories = prompt_config['classification_prompts']['categories']
            print(f"✅ prompt_config['classification_prompts']['categories']访问正确: {len(categories)} 个分类")
        except KeyError as e:
            print(f"❌ prompt_config['classification_prompts']['categories']访问错误: {e}")
            return False
        
        # 检查base_prompt_template访问
        try:
            template = prompt_config['classification_prompts']['base_prompt_template']
            print(f"✅ prompt_config['classification_prompts']['base_prompt_template']访问正确")
        except KeyError as e:
            print(f"❌ prompt_config['classification_prompts']['base_prompt_template']访问错误: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 分类器配置访问检查失败: {e}")
        return False

def check_validators_config_access():
    """检查验证器中的配置访问"""
    print("\n🔍 检查验证器中的配置访问")
    print("=" * 50)
    
    try:
        from main import load_config
        from utils.validators import DataValidator
        
        config = load_config('config/')
        validator = DataValidator()
        
        # 检查validate_config方法
        try:
            result = validator.validate_config(config)
            print(f"✅ validate_config执行成功: {result}")
        except Exception as e:
            print(f"❌ validate_config执行失败: {e}")
            return False
        
        # 检查data_sources访问
        try:
            if 'sources' in config and 'data_sources' in config['sources']:
                data_sources = config['sources']['data_sources']
                print(f"✅ data_sources访问正确: {list(data_sources.keys())}")
            else:
                print("⚠️ data_sources配置缺失")
        except Exception as e:
            print(f"❌ data_sources访问错误: {e}")
            return False
        
        # 检查llm_config访问
        try:
            llm_config = config.get('llm_config', {})
            result = validator.validate_llm_config(llm_config)
            print(f"✅ validate_llm_config执行成功: {result}")
        except Exception as e:
            print(f"❌ validate_llm_config执行失败: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 验证器配置访问检查失败: {e}")
        return False

def check_potential_issues():
    """检查潜在的配置问题"""
    print("\n🔍 检查潜在的配置问题")
    print("=" * 50)
    
    try:
        from main import load_config
        config = load_config('config/')
        
        # 检查是否有遗漏的双层嵌套问题
        potential_issues = []
        
        # 1. 检查是否直接访问了classification_prompts的内容（可能错误）
        try:
            # 这个应该失败
            wrong_access = config['classification_prompts']['categories']
            potential_issues.append("可能的错误: 直接访问config['classification_prompts']['categories']应该失败但却成功了")
        except KeyError:
            print("✅ 正确: config['classification_prompts']['categories']确实不存在（符合预期）")
        
        # 2. 检查是否有其他类似的嵌套问题
        config_files = ['classification_prompts', 'sources', 'llm_config']
        for file_key in config_files:
            if file_key in config:
                inner_config = config[file_key]
                if isinstance(inner_config, dict):
                    print(f"📊 {file_key}配置结构: {list(inner_config.keys())}")
                    
                    # 检查是否有同名的内部键（可能导致混淆）
                    if file_key in inner_config:
                        print(f"⚠️ 注意: {file_key}配置中有同名内部键，需要双层访问")
        
        if not potential_issues:
            print("✅ 未发现潜在配置问题")
            return True
        else:
            for issue in potential_issues:
                print(f"❌ {issue}")
            return False
            
    except Exception as e:
        print(f"❌ 潜在问题检查失败: {e}")
        return False

def run_integration_test():
    """运行集成测试"""
    print("\n🔍 运行集成测试")
    print("=" * 50)
    
    try:
        # 模拟完整的配置加载和使用流程
        from main import load_config
        from utils.validators import DataValidator
        
        print("1. 加载配置...")
        config = load_config('config/')
        
        print("2. 验证配置...")
        validator = DataValidator()
        if not validator.validate_config(config):
            print("❌ 配置验证失败")
            return False
        
        print("3. 模拟分类器初始化...")
        # 模拟OpenAIClassifier的配置访问
        try:
            llm_config = config['llm_config']['openai']
            llm_config['api_key'] = 'test_key'  # 模拟API密钥
            print("✅ 分类器配置访问成功")
        except Exception as e:
            print(f"❌ 分类器配置访问失败: {e}")
            return False
        
        print("4. 模拟分类配置访问...")
        try:
            classification_config = config['classification_prompts']['classification_prompts']
            categories_config = classification_config['categories']
            print(f"✅ 分类配置访问成功: {len(categories_config)} 个类别")
        except Exception as e:
            print(f"❌ 分类配置访问失败: {e}")
            return False
        
        print("5. 模拟爬虫配置访问...")
        try:
            arxiv_config = config['sources']['data_sources'].get('arxiv', {})
            if arxiv_config:
                print("✅ 爬虫配置访问成功")
            else:
                print("⚠️ 爬虫配置为空")
                return False
        except Exception as e:
            print(f"❌ 爬虫配置访问失败: {e}")
            return False
        
        print("✅ 集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    print("🎯 配置路径BUG全面检查工具")
    print("=" * 80)
    print("检查所有配置访问路径是否存在类似的KeyError问题")
    print("=" * 80)
    
    # 确保在正确的目录
    if not os.path.exists('config/'):
        print("❌ 错误: config/ 目录不存在，请在tools目录下运行此脚本")
        return 1
    
    all_checks = [
        ("main.py配置访问", check_main_py_config_access),
        ("分类器配置访问", check_classifier_config_access),
        ("验证器配置访问", check_validators_config_access),
        ("潜在问题检查", check_potential_issues),
        ("集成测试", run_integration_test)
    ]
    
    results = {}
    
    for check_name, check_func in all_checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name}检查过程中出错: {e}")
            results[check_name] = False
    
    print("\n" + "=" * 80)
    print("📊 检查结果汇总:")
    print("=" * 80)
    
    all_passed = True
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {check_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 所有检查通过！没有发现类似的配置路径BUG。")
    else:
        print("⚠️ 发现问题！需要修复上述失败的检查项。")
    print("=" * 80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())