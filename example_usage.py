"""
Gmail Check Skill使用示例

这个文件展示了如何使用GmailCheckSkill的各种功能
"""

import json
import time
from gmail_check_skill import GmailCheckSkill
from ldr.context import ExecutionContext


def example_one_time_check():
    """示例：一次性邮件检测"""
    print("=== 一次性邮件检测示例 ===")
    
    skill = GmailCheckSkill()
    ctx = ExecutionContext()
    
    # 配置参数
    params = {
        "username": "your-email@gmail.com",
        "app_password": "your-app-password-here",
        "email_filters": {
            "notifications@github.com": ["Pull Request", "Issue"],
            "alerts@system.com": ["系统告警", "服务器状态"]
        },
        "background_mode": False,
        "max_emails": 50,
        "days_back": 1
    }
    
    # 执行检测
    result = skill.execute(ctx, **params)
    
    if result['success']:
        emails = result['data']['matched_emails']
        print(f"检测完成，找到 {len(emails)} 封匹配邮件")
        
        for i, email in enumerate(emails, 1):
            print(f"\n邮件 {i}:")
            print(f"  发件人: {email['sender']}")
            print(f"  主题: {email['subject']}")
            print(f"  日期: {email['date_received']}")
            print(f"  内容预览: {email['content'][:100]}...")
            print(f"  匹配的过滤器: {email['matched_subject_filters']}")
    else:
        print(f"检测失败: {result['error']['message']}")


def example_background_monitoring():
    """示例：后台监控模式"""
    print("\n=== 后台监控模式示例 ===")
    
    skill = GmailCheckSkill()
    ctx = ExecutionContext()
    
    # 配置参数
    params = {
        "username": "your-email@gmail.com",
        "app_password": "your-app-password-here",
        "email_filters": {
            "important@company.com": ["紧急", "重要通知"],
            "system@server.com": ["故障", "告警"]
        },
        "check_interval": 5,  # 5分钟检测一次（测试用）
        "background_mode": True,
        "max_emails": 20,
        "days_back": 1
    }
    
    # 启动后台监控
    result = skill.execute(ctx, **params)
    
    if result['success']:
        print("后台监控已启动")
        print(f"检测间隔: {result['data']['check_interval']} 分钟")
        
        # 模拟运行一段时间
        print("监控运行中，10秒后停止...")
        time.sleep(10)
        
        # 检查是否有新结果
        latest_results = ctx.get("skill:gmail_check:latest_results")
        if latest_results:
            print(f"监控期间找到 {latest_results['total_matched']} 封新邮件")
        
        # 停止监控
        if skill.stop_monitoring():
            print("监控已停止")
        else:
            print("监控停止失败")
    else:
        print(f"启动监控失败: {result['error']['message']}")


def example_with_config_file():
    """示例：使用配置文件"""
    print("\n=== 使用配置文件示例 ===")
    
    try:
        # 读取配置文件
        with open('gmail_config_example.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 这里需要用户填入真实的认证信息
        if config['username'] == 'your-email@gmail.com':
            print("请先在 gmail_config_example.json 中配置真实的邮箱和密码")
            return
        
        skill = GmailCheckSkill()
        ctx = ExecutionContext()
        
        # 执行检测
        result = skill.execute(ctx, **config)
        
        if result['success']:
            print("配置文件检测成功")
            print(f"统计信息: {result['statistics']}")
        else:
            print(f"检测失败: {result['error']['message']}")
            
    except FileNotFoundError:
        print("配置文件 gmail_config_example.json 未找到")
    except json.JSONDecodeError:
        print("配置文件格式错误")


def example_mcp_resources():
    """示例：MCP资源访问"""
    print("\n=== MCP资源访问示例 ===")
    
    skill = GmailCheckSkill()
    
    # 获取可用资源
    resources = skill.get_mcp_resources()
    print("可用MCP资源:")
    for resource in resources:
        print(f"  - {resource.name}: {resource.description}")
    
    # 读取缓存状态
    cache_status = skill.read_resource("skill://gmail_check/cache_status")
    print(f"\n缓存状态: {cache_status['contents'][0]['text']}")
    
    # 读取监控状态
    monitoring_status = skill.read_resource("skill://gmail_check/monitoring_status")
    print(f"监控状态: {monitoring_status['contents'][0]['text']}")


def example_error_handling():
    """示例：错误处理"""
    print("\n=== 错误处理示例 ===")
    
    skill = GmailCheckSkill()
    ctx = ExecutionContext()
    
    # 测试缺少必需参数
    result = skill.execute(ctx)
    print(f"缺少参数测试: {result['error']['message']}")
    
    # 测试错误的认证信息
    params = {
        "username": "invalid@gmail.com",
        "app_password": "invalidpassword",
        "email_filters": {"test@test.com": ["test"]}
    }
    
    result = skill.execute(ctx, **params)
    print(f"认证错误测试: {result['error']['message']}")


def main():
    """主函数 - 运行所有示例"""
    print("Gmail Check Skill 使用示例")
    print("=" * 50)
    
    # 注意：这些示例需要真实的Gmail凭据才能运行
    # 请先配置 gmail_config_example.json 文件
    
    try:
        # 一次性检测示例
        # example_one_time_check()
        
        # 后台监控示例
        # example_background_monitoring()
        
        # 配置文件示例
        example_with_config_file()
        
        # MCP资源示例
        example_mcp_resources()
        
        # 错误处理示例
        example_error_handling()
        
    except Exception as e:
        print(f"示例执行出错: {str(e)}")


if __name__ == "__main__":
    main()