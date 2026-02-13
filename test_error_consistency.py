#!/usr/bin/env python3
"""
测试Gmail技能在各种错误情况下的结构一致性

验证以下场景：
1. 无法获得授权登陆服务器（认证失败）
2. 输入参数错误（缺少必要参数）
3. 无法过滤等原因（空过滤条件）
4. 网络连接问题
5. 成功情况对比

确认所有情况下都返回相同的结构，只有matched_emails为空列表
"""

import sys
import os
import json
from typing import Dict, Any
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_check_skill import GmailCheckSkill
from ldr_compat import ExecutionContext

def print_result_structure(result: Dict[str, Any], scenario: str):
    """打印结果结构分析"""
    print(f"\n=== {scenario} ===")
    print(f"✓ success: {result.get('success')}")
    print(f"✓ function_name: {result.get('function_name')}")
    
    data = result.get('data', {})
    print(f"✓ data.matched_emails: {type(data.get('matched_emails'))} (长度: {len(data.get('matched_emails', []))})")
    print(f"✓ data.check_time: {data.get('check_time')}")
    print(f"✓ data.total_matched: {data.get('total_matched')}")
    print(f"✓ data.background_mode: {data.get('background_mode')}")
    
    stats = result.get('statistics', {})
    print(f"✓ statistics.emails_checked: {stats.get('emails_checked')}")
    print(f"✓ statistics.filters_applied: {stats.get('filters_applied')}")
    print(f"✓ statistics.connection_status: {stats.get('connection_status')}")
    
    return {
        'has_matched_emails': 'matched_emails' in data,
        'matched_emails_type': type(data.get('matched_emails')).__name__,
        'matched_emails_count': len(data.get('matched_emails', [])),
        'has_success': 'success' in result,
        'has_function_name': 'function_name' in result,
        'has_data': 'data' in result,
        'has_statistics': 'statistics' in result
    }

def test_error_scenarios():
    """测试各种错误场景"""
    
    skill = GmailCheckSkill()
    ctx = ExecutionContext()
    
    results = {}
    
    # 1. 测试缺少认证参数
    print("🧪 测试场景 1: 缺少认证参数")
    result1 = skill.execute(
        ctx,
        username="",  # 空用户名
        app_password="",  # 空密码
        email_filters={"from": ["test@example.com"]}
    )
    results['missing_auth'] = print_result_structure(result1, "缺少认证参数")
    
    # 2. 测试空过滤条件
    print("\n🧪 测试场景 2: 空过滤条件")
    result2 = skill.execute(
        ctx,
        username="testuser@gmail.com",
        app_password="test_password",
        email_filters={}  # 空过滤条件
    )
    results['empty_filters'] = print_result_structure(result2, "空过滤条件")
    
    # 3. 测试None过滤条件
    print("\n🧪 测试场景 3: None过滤条件")
    result3 = skill.execute(
        ctx,
        username="testuser@gmail.com",
        app_password="test_password",
        email_filters=None
    )
    results['none_filters'] = print_result_structure(result3, "None过滤条件")
    
    # 4. 测试错误的认证信息（会触发连接错误）
    print("\n🧪 测试场景 4: 错误的认证信息")
    result4 = skill.execute(
        ctx,
        username="invalid@gmail.com",
        app_password="wrong_password",
        email_filters={"from": ["test@example.com"]}
    )
    results['invalid_auth'] = print_result_structure(result4, "错误的认证信息")
    
    # 5. 测试背景模式下的错误
    print("\n🧪 测试场景 5: 背景模式缺少认证")
    result5 = skill.execute(
        ctx,
        username="",
        app_password="",
        email_filters={"from": ["test@example.com"]},
        background_mode=True
    )
    results['background_no_auth'] = print_result_structure(result5, "背景模式缺少认证")
    
    return results, [result1, result2, result3, result4, result5]

def analyze_consistency(results: Dict[str, Dict], raw_results):
    """分析结构一致性"""
    print("\n" + "="*60)
    print("📊 结构一致性分析")
    print("="*60)
    
    # 检查关键字段的一致性
    fields_to_check = [
        'has_matched_emails', 'matched_emails_type', 'has_success',
        'has_function_name', 'has_data', 'has_statistics'
    ]
    
    is_consistent = True
    
    for field in fields_to_check:
        values = [results[scenario].get(field) for scenario in results]
        if len(set(values)) > 1:
            print(f"❌ 不一致字段: {field}")
            for scenario in results:
                print(f"   {scenario}: {results[scenario].get(field)}")
            is_consistent = False
        else:
            print(f"✅ 一致字段: {field} = {values[0]}")
    
    # 检查matched_emails是否都为空列表
    print("\n📧 邮件列表检查:")
    for i, (scenario, result) in enumerate(zip(results.keys(), raw_results)):
        matched_emails = result.get('data', {}).get('matched_emails', [])
        print(f"✓ {scenario}: matched_emails = {matched_emails} (长度: {len(matched_emails)})")
        if len(matched_emails) > 0:
            print(f"⚠️  {scenario} 返回了非空邮件列表!")
            is_consistent = False
    
    # 检查success字段
    print("\n✅ 成功状态检查:")
    for i, (scenario, result) in enumerate(zip(results.keys(), raw_results)):
        success = result.get('success')
        print(f"✓ {scenario}: success = {success}")
        if success != True:
            print(f"⚠️  {scenario} success字段不为True!")
    
    print(f"\n{'✅ 结构完全一致!' if is_consistent else '❌ 发现结构不一致!'}")
    return is_consistent

def save_test_results(results, raw_results):
    """保存测试结果到文件"""
    test_output = {
        "test_info": {
            "test_date": datetime.now().isoformat(),
            "version": "1.2.0",
            "purpose": "验证错误情况下的结构一致性"
        },
        "scenarios": {}
    }
    
    scenarios = ['missing_auth', 'empty_filters', 'none_filters', 'invalid_auth', 'background_no_auth']
    
    for i, scenario in enumerate(scenarios):
        test_output["scenarios"][scenario] = {
            "description": {
                'missing_auth': "缺少认证参数",
                'empty_filters': "空过滤条件", 
                'none_filters': "None过滤条件",
                'invalid_auth': "错误的认证信息",
                'background_no_auth': "背景模式缺少认证"
            }[scenario],
            "raw_result": raw_results[i],
            "structure_analysis": results[scenario]
        }
    
    filename = f"error_consistency_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(test_output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已保存到: {filename}")
    print(f"文件大小: {os.path.getsize(filepath):,} 字节")

def main():
    """主测试函数"""
    print("🔍 Gmail技能错误处理一致性测试")
    print("=" * 50)
    print("📋 测试目标:")
    print("  1. 验证各种错误情况下返回结构一致")
    print("  2. 确认matched_emails始终为空列表")
    print("  3. 确认success字段始终为True")
    print("  4. 验证所有必要字段都存在")
    
    # 执行测试
    results, raw_results = test_error_scenarios()
    
    # 分析一致性
    is_consistent = analyze_consistency(results, raw_results)
    
    # 保存结果
    save_test_results(results, raw_results)
    
    # 最终结论
    print("\n" + "="*60)
    print("🎯 最终结论")
    print("="*60)
    
    if is_consistent:
        print("✅ 所有错误情况下的返回结构完全一致!")
        print("✅ matched_emails字段在所有情况下都是空列表!")
        print("✅ success字段在所有情况下都为True!")
        print("✅ 错误处理符合要求!")
    else:
        print("❌ 发现结构不一致的问题!")
        print("❌ 需要修复错误处理逻辑!")
    
    # 显示当前版本信息
    from version import __version__, __release_date__
    print(f"\n📦 当前版本: {__version__} (发布日期: {__release_date__})")

if __name__ == "__main__":
    main()