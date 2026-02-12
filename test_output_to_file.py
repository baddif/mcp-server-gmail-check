#!/usr/bin/env python3
"""
Gmail Check Skill 输出结果到文件测试脚本

这个脚本用于测试Gmail检查技能的完整输出，并将结果保存到JSON文件中，
供其他技能作为输入开发用例使用。
"""

import json
import sys
import os
from datetime import datetime, timezone

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_check_skill import GmailCheckSkill
from ldr_compat import ExecutionContext


def test_and_save_output():
    """测试Gmail Check Skill并保存完整输出结果"""
    
    print("🧪 Gmail Check Skill 完整输出测试")
    print("=" * 60)
    
    # 读取配置文件
    config_file = 'gmail_config_local.json'
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 成功读取配置文件: {config_file}")
    except FileNotFoundError:
        print(f"❌ 配置文件 {config_file} 不存在")
        print("请先创建并配置 gmail_config_local.json 文件")
        return
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return
    
    # 验证配置
    if not config.get('username') or config.get('username') == 'your-email@gmail.com':
        print("❌ 请在配置文件中设置真实的邮箱地址")
        return
    
    if not config.get('app_password') or config.get('app_password') == 'your-16-char-app-password':
        print("❌ 请在配置文件中设置真实的App Password")
        return
    
    # 创建技能实例
    skill = GmailCheckSkill()
    ctx = ExecutionContext()
    
    # 设置测试参数
    test_params = {
        "username": config['username'],
        "app_password": config['app_password'],
        "email_filters": config.get('email_filters', {}),
        "background_mode": False,  # 一次性检查
        "max_emails": config.get('max_emails', 50),  # 限制邮件数量
        "days_back": config.get('days_back', 7),  # 检查7天内的邮件
        "time_range_hours": config.get('time_range_hours'),
        "use_cache": False,  # 关键：不使用缓存，获取所有匹配邮件
        "check_interval": config.get('check_interval', 30)
    }
    
    print(f"\n📋 测试参数:")
    print(f"  邮箱: {test_params['username']}")
    print(f"  过滤器数量: {len(test_params['email_filters'])}")
    print(f"  最大邮件数: {test_params['max_emails']}")
    print(f"  检查天数: {test_params['days_back']}")
    print(f"  使用缓存: {test_params['use_cache']}")
    
    print(f"\n  邮件过滤规则:")
    for sender, subjects in test_params['email_filters'].items():
        print(f"    📧 {sender}: {subjects}")
    
    print(f"\n🔍 开始执行Gmail检查...")
    
    # 执行技能
    try:
        result = skill.execute(ctx, **test_params)
        
        # 显示执行结果摘要
        print(f"\n📊 执行结果摘要:")
        print(f"  成功: {result.get('success')}")
        print(f"  功能名称: {result.get('function_name')}")
        
        if result.get('success'):
            data = result.get('data', {})
            stats = result.get('statistics', {})
            matched_emails = data.get('matched_emails', [])
            
            print(f"  找到匹配邮件: {len(matched_emails)} 封")
            print(f"  检查时间: {data.get('check_time')}")
            print(f"  检查的总邮件数: {stats.get('emails_checked', 0)}")
            print(f"  应用的过滤器数: {stats.get('filters_applied', 0)}")
            
            # 显示每封邮件的简要信息
            if matched_emails:
                print(f"\n📧 匹配邮件列表:")
                for i, email in enumerate(matched_emails, 1):
                    print(f"  {i}. 发件人: {email.get('sender_email', 'unknown')}")
                    print(f"     主题: {email.get('subject', 'no subject')[:50]}...")
                    print(f"     日期: {email.get('date_received', 'unknown')}")
                    print(f"     匹配关键词: {email.get('matched_subject_filters', [])}")
                    print()
            
        else:
            print(f"  执行失败: {result.get('error', {}).get('message', 'unknown error')}")
        
        # 保存完整结果到文件
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_filename = f"gmail_check_output_{timestamp}.json"
        
        # 创建输出对象，包含额外的元数据
        output_data = {
            "test_metadata": {
                "test_time": datetime.now(timezone.utc).isoformat(),
                "script_version": "1.0.0",
                "config_file": config_file,
                "test_purpose": "为其他技能提供真实的Gmail检查输出用例",
                "parameters_used": test_params
            },
            "gmail_check_result": result
        }
        
        # 保存到文件
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 完整结果已保存到: {output_filename}")
            print(f"📁 文件大小: {os.path.getsize(output_filename)} bytes")
            
            # 显示文件内容摘要
            print(f"\n📄 输出文件结构:")
            print(f"  ├── test_metadata (测试元数据)")
            print(f"  │   ├── test_time: 测试时间")
            print(f"  │   ├── parameters_used: 使用的参数")
            print(f"  │   └── config_file: 配置文件名")
            print(f"  └── gmail_check_result (Gmail检查结果)")
            print(f"      ├── success: 执行状态")
            print(f"      ├── data.matched_emails: 匹配的邮件列表")
            print(f"      └── statistics: 统计信息")
            
            # 提供使用建议
            print(f"\n💡 使用建议:")
            print(f"  1. 其他技能可以读取此文件作为输入数据")
            print(f"  2. 文件包含真实的邮件结构和格式")
            print(f"  3. 可以用于开发邮件处理、分析或报告技能")
            print(f"  4. 注意保护邮件内容的隐私性")
            
        except Exception as save_error:
            print(f"❌ 保存文件失败: {save_error}")
            
    except Exception as e:
        print(f"❌ 执行技能时出错: {e}")
        return
    
    print(f"\n✅ 测试完成!")


def create_sample_output():
    """创建一个示例输出文件结构（用于开发参考）"""
    
    sample_output = {
        "test_metadata": {
            "test_time": "2026-02-12T10:00:00Z",
            "script_version": "1.0.0",
            "config_file": "gmail_config_local.json",
            "test_purpose": "为其他技能提供真实的Gmail检查输出用例",
            "parameters_used": {
                "username": "user@example.com",
                "email_filters": {
                    "notifications@github.com": ["Pull Request", "Issue"],
                    "jobalerts-noreply@linkedin.com": ["软件工程师", "开发工程师"]
                },
                "background_mode": False,
                "max_emails": 50,
                "use_cache": False
            }
        },
        "gmail_check_result": {
            "success": True,
            "function_name": "gmail_check",
            "data": {
                "matched_emails": [
                    {
                        "sender": "GitHub <notifications@github.com>",
                        "sender_email": "notifications@github.com",
                        "subject": "New Pull Request in your repository",
                        "content": "A new pull request has been submitted...",
                        "date_received": "Mon, 12 Feb 2026 08:30:00 +0000",
                        "message_id": "<github-pr-123@example.com>",
                        "matched_sender_filter": "notifications@github.com",
                        "matched_subject_filters": ["Pull Request"],
                        "email_id": "abc123def456"
                    }
                ],
                "check_time": "2026-02-12T10:00:00Z",
                "total_matched": 1,
                "background_mode": False
            },
            "statistics": {
                "emails_checked": 25,
                "cache_size": 0,
                "filters_applied": 2,
                "time_range_hours": 168,
                "cache_enabled": False,
                "search_period": "7 days"
            }
        }
    }
    
    # 保存示例文件
    sample_filename = "gmail_check_output_sample.json"
    with open(sample_filename, 'w', encoding='utf-8') as f:
        json.dump(sample_output, f, indent=2, ensure_ascii=False)
    
    print(f"📄 示例输出文件已创建: {sample_filename}")


if __name__ == "__main__":
    print("选择操作:")
    print("1. 执行真实Gmail检查并保存输出")
    print("2. 创建示例输出文件（用于开发参考）")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        test_and_save_output()
    elif choice == "2":
        create_sample_output()
    else:
        print("无效选择，执行真实Gmail检查...")
        test_and_save_output()