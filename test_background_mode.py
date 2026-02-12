"""
测试Gmail Check Skill的后台运行模式
"""

import json
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_check_skill import GmailCheckSkill

class SimpleExecutionContext:
    """简单的执行上下文实现，用于测试"""
    def __init__(self):
        self._data = {}
    
    def set(self, key, value):
        self._data[key] = value
        print(f"Context updated: {key} = {value}")
    
    def get(self, key, default=None):
        return self._data.get(key, default)

def test_background_mode():
    """测试后台运行模式"""
    print("Gmail Check Skill 后台模式测试")
    print("=" * 50)
    
    # 读取配置文件
    try:
        with open('gmail_config_local.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 成功读取配置文件")
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return
    
    skill = GmailCheckSkill()
    ctx = SimpleExecutionContext()
    
    print(f"\n📋 测试参数:")
    print(f"  - 邮箱: {config['username']}")
    print(f"  - 检测间隔: {config['check_interval']} 分钟")
    print(f"  - 最大邮件数: {config['max_emails']}")
    print(f"  - 时间范围: {config['time_range_hours']} 小时")
    print(f"  - 使用缓存: {config['use_cache']}")
    
    # 测试1: 非后台模式 (一次性检查)
    print(f"\n🔍 测试1: 非后台模式 (一次性检查)")
    print("-" * 30)
    
    config_one_time = config.copy()
    config_one_time['background_mode'] = False
    
    start_time = time.time()
    result1 = skill.execute(ctx, **config_one_time)
    end_time = time.time()
    
    print(f"执行时间: {end_time - start_time:.2f} 秒")
    if result1['success']:
        print(f"✅ 一次性检查成功")
        print(f"找到邮件: {result1['data']['total_matched']} 封")
        print(f"后台模式: {result1['data']['background_mode']}")
        print(f"检查时间: {result1['data']['check_time']}")
    else:
        print(f"❌ 一次性检查失败: {result1['error']['message']}")
        return
    
    # 测试2: 后台模式 (持续监控)
    print(f"\n🔄 测试2: 后台模式 (持续监控)")
    print("-" * 30)
    
    config_background = config.copy()
    config_background['background_mode'] = True
    config_background['check_interval'] = 1  # 设置为1分钟间隔以便快速测试
    
    start_time = time.time()
    result2 = skill.execute(ctx, **config_background)
    end_time = time.time()
    
    print(f"启动时间: {end_time - start_time:.2f} 秒")
    if result2['success']:
        print(f"✅ 后台监控启动成功")
        print(f"后台模式: {result2['data']['background_mode']}")
        print(f"检测间隔: {result2['data']['check_interval']} 分钟")
        print(f"启动时间: {result2['data']['monitoring_started']}")
        print(f"状态消息: {result2['data']['message']}")
    else:
        print(f"❌ 后台监控启动失败: {result2['error']['message']}")
        return
    
    # 监控一段时间以观察后台运行
    print(f"\n⏰ 监控后台运行状态 (观察3分钟)...")
    print("按 Ctrl+C 提前结束监控")
    
    try:
        for i in range(180):  # 监控3分钟
            time.sleep(1)
            if i % 30 == 0:  # 每30秒报告一次
                print(f"  监控中... 已运行 {i//30 * 30} 秒")
                
                # 检查context中是否有新结果
                latest_results = ctx.get("skill:gmail_check:latest_results")
                last_check = ctx.get("skill:gmail_check:last_check")
                
                if latest_results:
                    print(f"    最新检查: {last_check}")
                    print(f"    找到邮件: {latest_results.get('total_matched', 0)} 封")
                
    except KeyboardInterrupt:
        print(f"\n⏹️ 用户中断监控")
    
    # 停止后台监控
    print(f"\n🛑 停止后台监控...")
    stop_result = skill.stop_monitoring()
    print(f"停止结果: {'成功' if stop_result else '失败'}")
    
    print(f"\n✅ 后台模式测试完成")

def test_background_immediate_execution():
    """测试后台模式是否在启动时立即执行一次"""
    print("\n" + "=" * 50)
    print("测试后台模式立即执行功能")
    print("=" * 50)
    
    # 读取配置
    try:
        with open('gmail_config_local.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return
    
    skill = GmailCheckSkill()
    ctx = SimpleExecutionContext()
    
    # 启用后台模式，设置较长的检测间隔
    config['background_mode'] = True
    config['check_interval'] = 10  # 10分钟间隔
    
    print(f"🚀 启动后台模式 (检测间隔: {config['check_interval']} 分钟)")
    print("观察是否立即执行第一次检查...")
    
    start_time = time.time()
    result = skill.execute(ctx, **config)
    
    if result['success']:
        print(f"✅ 后台监控启动成功")
        
        # 等待几秒钟，看看是否立即开始了第一次检查
        print("等待第一次检查结果...")
        time.sleep(5)
        
        latest_results = ctx.get("skill:gmail_check:latest_results")
        if latest_results:
            print(f"✅ 检测到立即执行的检查结果:")
            print(f"   检查时间: {latest_results['check_time']}")
            print(f"   找到邮件: {latest_results['total_matched']} 封")
            print(f"   后台模式: {latest_results['background_mode']}")
        else:
            print(f"⚠️ 未检测到立即执行的检查结果")
        
        # 停止监控
        skill.stop_monitoring()
        print(f"🛑 后台监控已停止")
    else:
        print(f"❌ 后台监控启动失败: {result['error']['message']}")

if __name__ == "__main__":
    test_background_mode()
    test_background_immediate_execution()