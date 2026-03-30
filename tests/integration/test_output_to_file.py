import os
import pytest

if os.getenv("RUN_LIVE_TESTS") != "1":
    pytest.skip("Live Gmail tests skipped (set RUN_LIVE_TESTS=1 to enable)", allow_module_level=True)

#!/usr/bin/env python3
"""
Gmail Check Skill 输出结果到文件测试脚本

这个脚本用于测试Gmail检查技能的完整输出，并将结果保存到JSON文件中，
供其他技能作为输入开发用例使用。
"""

import json
import sys
import os as _os
from datetime import datetime, timezone

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        pytest.skip(f"Config file {config_file} not found; skipping live test")
    except json.JSONDecodeError as e:
        pytest.skip(f"Config file {config_file} JSON error: {e}")
    
    # 验证配置
    if not config.get('username') or config.get('username') == 'your-email@gmail.com':
        pytest.skip("Config appears to be example; set gmail_config_local.json with real credentials to run live tests")
    
    if not config.get('app_password') or config.get('app_password') == 'your-16-char-app-password':
        pytest.skip("Config missing app_password; set gmail_config_local.json with real app password to run live tests")
    
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
    
    # 执行技能
    result = skill.execute(ctx, **test_params)
    assert isinstance(result, dict)

    # 保存完整结果到文件
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_filename = f"gmail_check_output_{timestamp}.json"

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

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Ensure file exists and is non-empty
    assert _os.path.exists(output_filename) and _os.path.getsize(output_filename) > 0
import os
import pytest

if os.getenv("RUN_LIVE_TESTS") != "1":
    pytest.skip("Live Gmail tests skipped (set RUN_LIVE_TESTS=1 to enable)", allow_module_level=True)

# ...existing code from top-level test_output_to_file.py will be run here when enabled
from ....gmail_check_skill import GmailCheckSkill  # placeholder import; file executed only when env enabled

