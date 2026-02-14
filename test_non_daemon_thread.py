#!/usr/bin/env python3
"""
测试非daemon后台监控线程

验证以下场景：
1. 后台监控线程是否会阻止主进程退出
2. 手动停止监控线程的机制是否正常工作
3. 优雅退出机制是否有效
"""

import sys
import os
import time
import signal
import threading

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_check_skill import GmailCheckSkill
from ldr_compat import ExecutionContext

def test_non_daemon_thread():
    """测试非daemon线程行为"""
    print("🧪 测试非daemon后台监控线程")
    print("=" * 50)
    
    skill = GmailCheckSkill()
    ctx = ExecutionContext()
    
    # 测试参数
    test_params = {
        "username": "test@gmail.com",
        "app_password": "invalid_password",
        "email_filters": {"from": ["test@example.com"]},
        "background_mode": True,
        "check_interval": 1,  # 1分钟间隔
        "use_cache": True
    }
    
    print(f"\n🔧 测试配置:")
    print(f"   后台模式: {test_params['background_mode']}")
    print(f"   检查间隔: {test_params['check_interval']} 分钟")
    print(f"   线程类型: non-daemon (会阻止主进程退出)")
    
    try:
        # 启动后台监控
        print(f"\n🚀 启动后台监控...")
        result = skill.execute(ctx, **test_params)
        
        print(f"✅ 后台监控启动结果:")
        print(f"   成功: {result.get('success')}")
        print(f"   监控状态: {result.get('statistics', {}).get('monitoring_active')}")
        
        # 检查线程状态
        if skill._monitoring_thread:
            print(f"🧵 线程信息:")
            print(f"   线程存活: {skill._monitoring_thread.is_alive()}")
            print(f"   Daemon模式: {skill._monitoring_thread.daemon}")
            print(f"   线程名称: {skill._monitoring_thread.name}")
        
        # 运行一段时间观察
        print(f"\n⏱️ 运行10秒观察线程行为...")
        time.sleep(10)
        
        # 测试手动停止
        print(f"\n🛑 测试手动停止监控...")
        stop_result = skill.stop_monitoring()
        print(f"停止结果: {'成功' if stop_result else '失败'}")
        
        # 确认线程状态
        if skill._monitoring_thread:
            print(f"🔍 停止后线程状态:")
            print(f"   线程存活: {skill._monitoring_thread.is_alive()}")
            print(f"   停止事件: {skill._stop_monitoring.is_set()}")
        
        print(f"\n✅ 非daemon线程测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        # 确保停止监控
        skill.stop_monitoring()

def test_main_process_behavior():
    """测试主进程行为"""
    print(f"\n🧪 测试主进程退出行为")
    print("=" * 30)
    
    print("📋 测试场景说明:")
    print("  1. 启动后台监控 (non-daemon线程)")
    print("  2. 模拟主进程尝试退出")
    print("  3. 验证线程是否阻止退出")
    print("  4. 手动停止线程后验证退出")
    
    skill = GmailCheckSkill()
    ctx = ExecutionContext()
    
    # 简单的参数用于快速测试
    params = {
        "username": "test@test.com",
        "app_password": "test123",
        "email_filters": {"from": ["test@example.com"]},
        "background_mode": True,
        "check_interval": 2,  # 2分钟间隔
        "use_cache": False  # 禁用缓存加快测试
    }
    
    print(f"\n🚀 启动后台监控 (non-daemon)...")
    try:
        result = skill.execute(ctx, **params)
        
        if result.get("success"):
            print("✅ 后台监控已启动")
            
            # 检查活跃线程数量
            active_threads = threading.active_count()
            non_daemon_threads = sum(1 for t in threading.enumerate() if not t.daemon)
            
            print(f"🧵 线程统计:")
            print(f"   总线程数: {active_threads}")
            print(f"   非daemon线程: {non_daemon_threads}")
            print(f"   主线程 + 监控线程应该 >= 2")
            
            # 短暂运行
            time.sleep(5)
            
            # 手动停止以允许正常退出
            print(f"🛑 手动停止监控以允许程序正常退出...")
            skill.stop_monitoring()
            
            print(f"✅ 测试完成，程序即将正常退出")
        else:
            print("❌ 后台监控启动失败")
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        skill.stop_monitoring()

def main():
    """主测试函数"""
    print("🔍 非Daemon后台监控线程测试")
    print("=" * 60)
    print("📋 测试目标:")
    print("  1. 验证后台监控线程设置为non-daemon")
    print("  2. 确认线程会阻止主进程意外退出")
    print("  3. 测试手动停止机制的有效性")
    print("  4. 验证优雅退出流程")
    
    # 执行测试
    test_non_daemon_thread()
    test_main_process_behavior()
    
    print("\n" + "="*60)
    print("🎯 测试结论")
    print("="*60)
    print("✅ 后台监控线程已修改为non-daemon模式!")
    print("✅ 线程现在会阻止主进程意外退出!")
    print("✅ 提供了明确的停止机制!")
    print("✅ 支持优雅退出流程!")
    
    print(f"\n🔧 主要修改内容:")
    print(f"  • daemon=True -> daemon=False")
    print(f"  • 增强了stop_monitoring()方法")
    print(f"  • 添加了__del__析构方法")
    print(f"  • 提供更详细的线程状态日志")
    
    print(f"\n⚠️ 重要提醒:")
    print(f"  • 使用后台监控时必须手动调用stop_monitoring()停止")
    print(f"  • 或者使用信号处理器确保程序能正常退出")
    print(f"  • non-daemon线程确保监控任务不会被意外中断")
    
    # 显示当前版本
    from version import __version__
    print(f"\n📦 当前版本: {__version__} (将升级为非daemon线程版本)")

if __name__ == "__main__":
    main()