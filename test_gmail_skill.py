"""
Gmail Check Skill 独立测试脚本

这个脚本可以独立运行，测试Gmail检测功能，无需依赖LocalDailyReport框架
"""

import json
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SimpleExecutionContext:
    """简单的执行上下文实现，用于测试"""
    def __init__(self):
        self._data = {}
    
    def set(self, key, value):
        self._data[key] = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)


def test_gmail_check():
    """测试Gmail检测功能"""
    print("Gmail Check Skill 测试")
    print("=" * 50)
    
    # 优先从本地配置文件读取认证信息，然后是示例配置文件
    config = None
    config_files = ['gmail_config_local.json', 'gmail_config_example.json']
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ 成功读取配置文件 {config_file}")
            
            # 检查是否为示例配置（包含占位符）
            if config.get('username') == 'your-email@gmail.com':
                print(f"⚠️  检测到示例配置文件，请先配置真实的认证信息")
                if config_file == 'gmail_config_example.json':
                    print("建议：复制 gmail_config_example.json 为 gmail_config_local.json 并填入真实信息")
                config = None
                continue
            else:
                break
                
        except FileNotFoundError:
            print(f"📁 配置文件 {config_file} 未找到")
            continue
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件 {config_file} 格式错误: {str(e)}")
            continue
    
    # 如果配置文件读取失败，则尝试环境变量
    if not config:
        username = os.getenv('GMAIL_USERNAME', '')
        app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        
        if not username or not app_password:
            print("请设置环境变量或配置 gmail_config_example.json 文件：")
            print("export GMAIL_USERNAME='your-email@gmail.com'")
            print("export GMAIL_APP_PASSWORD='your-app-password'")
            print("\n或者修改 gmail_config_example.json 中的认证信息")
            
            # 也可以直接在这里配置（不推荐用于生产环境）
            username = input("请输入Gmail邮箱: ") if not username else username
            app_password = input("请输入App Password: ") if not app_password else app_password
        
        if not username or not app_password:
            print("缺少认证信息，退出测试")
            return
        
        # 构建基本配置
        config = {
            "username": username,
            "app_password": app_password,
            "email_filters": {
                "notifications@github.com": ["Pull Request", "Issue"],
                "noreply@google.com": ["安全提醒", "登录"],
                "no-reply@medium.com": ["Weekly digest", "New story"]
            },
            "background_mode": False,
            "max_emails": 10,
            "days_back": 3,
            "use_cache": False
        }
    
    # 验证配置文件中的关键信息
    username = config.get("username", "")
    app_password = config.get("app_password", "")
    
    if not username or not app_password:
        print("❌ 配置文件中缺少必要的认证信息")
        print("请在 gmail_config_example.json 中正确设置 username 和 app_password")
        return
    
    try:
        # 动态导入skill（避免导入错误）
        from gmail_check_skill import GmailCheckSkill
        
        skill = GmailCheckSkill()
        ctx = SimpleExecutionContext()
        
        # 使用配置文件中的参数
        print(f"开始检测邮箱: {config['username']}")
        print(f"过滤器数量: {len(config['email_filters'])}")
        print("邮件过滤规则:")
        for sender, subjects in config['email_filters'].items():
            print(f"  📧 {sender}: {subjects}")
        
        print(f"检测参数:")
        print(f"  - 最大邮件数: {config.get('max_emails', 100)}")
        print(f"  - 检查天数: {config.get('days_back', 1)}")
        print(f"  - 后台模式: {config.get('background_mode', False)}")
        print(f"  - 检测间隔: {config.get('check_interval', 30)} 分钟")
        
        print("\n正在连接Gmail...")
        
        # 执行检测
        result = skill.execute(ctx, **config)
        
        # 显示结果
        if result['success']:
            emails = result['data']['matched_emails']
            print(f"\n✅ 检测成功！")
            print(f"找到匹配邮件: {len(emails)} 封")
            print(f"检测时间: {result['data']['check_time']}")
            
            if emails:
                print("\n匹配的邮件:")
                for i, email in enumerate(emails, 1):
                    print(f"\n📧 邮件 {i}:")
                    print(f"   发件人: {email['sender']}")
                    print(f"   主题: {email['subject']}")
                    print(f"   接收时间: {email['date_received']}")
                    print(f"   匹配的过滤器: {email['matched_subject_filters']}")
                    content_preview = email['content'][:200] + "..." if len(email['content']) > 200 else email['content']
                    print(f"   内容预览: {content_preview}")
            else:
                print("\n没有找到匹配的邮件")
            
            # 显示统计信息
            stats = result['statistics']
            print(f"\n📊 统计信息:")
            print(f"   检测的邮件数: {stats['emails_checked']}")
            print(f"   缓存大小: {stats['cache_size']}")
            print(f"   应用的过滤器数: {stats['filters_applied']}")
            
        else:
            print(f"\n❌ 检测失败:")
            print(f"   错误类型: {result['error']['type']}")
            print(f"   错误信息: {result['error']['message']}")
            
            # 提供故障排除建议
            if "authentication" in result['error']['message'].lower():
                print("\n💡 故障排除建议:")
                print("   1. 确认Gmail账户已开启两步验证")
                print("   2. 检查App Password是否正确（16位字符，无空格）")
                print("   3. 确认账户未被锁定")
            elif "connection" in result['error']['message'].lower():
                print("\n💡 故障排除建议:")
                print("   1. 检查网络连接")
                print("   2. 确认防火墙未阻止IMAP连接")
                print("   3. 尝试使用VPN")
        
        # 测试MCP资源
        print("\n" + "="*50)
        print("测试MCP资源")
        
        resources = skill.get_mcp_resources()
        print(f"可用资源数量: {len(resources)}")
        
        for resource in resources:
            print(f"\n🔍 资源: {resource.name}")
            try:
                data = skill.read_resource(resource.uri)
                content = data['contents'][0]['text']
                print(f"   数据: {content[:200]}...")
            except Exception as e:
                print(f"   读取失败: {str(e)}")
    
    except ImportError as e:
        print(f"导入失败: {str(e)}")
        print("请确认gmail_check_skill.py文件存在且正确")
    except Exception as e:
        print(f"测试异常: {str(e)}")
        import traceback
        traceback.print_exc()


def test_schema():
    """测试Schema定义"""
    print("\n" + "="*50)
    print("测试Schema定义")
    
    try:
        from gmail_check_skill import GmailCheckSkill
        
        skill = GmailCheckSkill()
        schema = skill.get_openai_schema()
        
        print("✅ Schema格式正确")
        print(f"功能名称: {schema['function']['name']}")
        print(f"描述: {schema['function']['description'][:100]}...")
        
        params = schema['function']['parameters']['properties']
        print(f"参数数量: {len(params)}")
        
        required = schema['function']['parameters']['required']
        print(f"必需参数: {required}")
        
        # 验证必需的参数
        expected_required = ['username', 'app_password', 'email_filters']
        for param in expected_required:
            if param in params:
                print(f"  ✅ {param}: {params[param]['type']}")
            else:
                print(f"  ❌ 缺少参数: {param}")
        
        # 显示完整schema（格式化）
        print(f"\n完整Schema:")
        print(json.dumps(schema, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Schema测试失败: {str(e)}")


def test_config_file():
    """测试配置文件读取和验证"""
    print("\n" + "="*50)
    print("测试配置文件")
    
    config_files = ['gmail_config_local.json', 'gmail_config_example.json']
    
    for config_file in config_files:
        print(f"\n检查配置文件: {config_file}")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"✅ {config_file} 读取成功")
            
            # 验证必需字段
            required_fields = ['username', 'app_password', 'email_filters']
            is_example = False
            
            for field in required_fields:
                if field in config and config[field]:
                    if field == 'username' and config[field] == 'your-email@gmail.com':
                        is_example = True
                        print(f"  📝 {field}: {config[field]} (示例配置)")
                    elif 'password' in field:
                        print(f"  ✅ {field}: {'***示例***' if is_example else '***隐藏***'}")
                    else:
                        print(f"  ✅ {field}: {config[field]}")
                else:
                    print(f"  ❌ 缺少或空白: {field}")
            
            if is_example:
                print(f"  ℹ️  {config_file} 是示例配置，需要配置真实信息")
                continue
            else:
                print(f"  ✅ {config_file} 包含真实配置信息")
                
                # 验证可选字段
                optional_fields = {
                    'check_interval': 30,
                    'background_mode': False,
                    'max_emails': 100,
                    'days_back': 1
                }
                
                print("\n可选配置:")
                for field, default in optional_fields.items():
                    value = config.get(field, default)
                    print(f"  📝 {field}: {value}")
                
                # 验证email_filters格式
                print("\n邮件过滤器:")
                if isinstance(config.get('email_filters'), dict):
                    for sender, subjects in config['email_filters'].items():
                        if isinstance(subjects, list):
                            print(f"  📧 {sender}:")
                            for subject in subjects:
                                print(f"      - '{subject}'")
                        else:
                            print(f"  ❌ {sender}: 主题列表格式错误 (应为数组)")
                else:
                    print("  ❌ email_filters 格式错误 (应为对象)")
                
                return config
                
        except FileNotFoundError:
            print(f"📁 配置文件 {config_file} 未找到")
            continue
        except json.JSONDecodeError as e:
            print(f"❌ JSON格式错误: {str(e)}")
            continue
        except Exception as e:
            print(f"❌ 读取配置文件时出错: {str(e)}")
            continue
    
    print("\n❌ 未找到可用的配置文件")
    print("请创建 gmail_config_local.json 并配置真实的认证信息")
    return None


if __name__ == "__main__":
    # 首先测试schema
    test_schema()
    
    # 测试配置文件
    config = test_config_file()
    
    if config:
        print("\n" + "="*50)
        print("开始Gmail连接测试...")
        test_gmail_check()
    else:
        print("\n配置文件验证失败，无法进行Gmail连接测试")
        print("请检查并修正 gmail_config_example.json 文件")
    
    print("\n测试完成！")