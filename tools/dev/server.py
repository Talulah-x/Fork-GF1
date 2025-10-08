#!/usr/bin/env python3
"""
独立的MaaFramework服务器
提供交互式终端界面，支持灰域任务的启动和停止
"""

import os
import sys
import time
import datetime
import threading
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import queue

# Windows窗口查找相关导入
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("⚠️ win32gui不可用，窗口查找功能受限")

# MaaFramework导入
try:
    from maa.tasker import Tasker
    from maa.resource import Resource
    from maa.controller import AdbController, Win32Controller, DbgController
    from maa.notification_handler import NotificationHandler
    from maa.toolkit import Toolkit
    from maa.job import JobWithResult, Job
    print("✅ MaaFramework 模块导入成功")
except ImportError as e:
    print(f"❌ MaaFramework 模块导入失败: {e}")
    print("请确保已正确安装 MaaFramework Python 绑定")
    sys.exit(1)


def find_game_window():
    """查找少女前线游戏窗口"""
    if not WIN32_AVAILABLE:
        print("⚠️ win32gui不可用，无法查找游戏窗口")
        return None
    
    try:
        # 首先尝试精确匹配
        hwnd = win32gui.FindWindow(None, "少女前线")
        if hwnd != 0:
            if win32gui.IsWindowVisible(hwnd):
                print(f"✅ 找到少女前线游戏窗口，句柄: {hwnd}")
                return hwnd
        
        # 尝试模糊匹配
        print("🔍 未能精确匹配'少女前线'窗口，尝试模糊匹配...")
        all_windows = []
        win32gui.EnumWindows(lambda h, param: param.append((h, win32gui.GetWindowText(h))), all_windows)
        
        print("找到的窗口列表:")
        game_candidates = []
        
        for h, title in all_windows:
            if len(title) > 0 and win32gui.IsWindowVisible(h):
                # 检查窗口大小，游戏窗口通常较大
                try:
                    rect = win32gui.GetWindowRect(h)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                    
                    print(f"  - 窗口句柄: {h}, 标题: '{title}', 大小: {width}x{height}")
                    
                    # 检查是否包含游戏相关关键词
                    if any(keyword in title for keyword in ["少女前线", "Girls", "Frontline", "GFL"]):
                        print(f"  --> 🎯 匹配到游戏窗口!")
                        return h
                    
                    # 收集可能的游戏窗口（大小合适的窗口）
                    if width > 800 and height > 600:
                        game_candidates.append((h, title, width, height))
                        
                except Exception:
                    continue
        
        # 如果没有找到明确的游戏窗口，显示候选窗口
        if game_candidates:
            print("\n🎮 发现可能的游戏窗口:")
            for i, (h, title, width, height) in enumerate(game_candidates[:5]):  # 只显示前5个
                print(f"  {i+1}. 句柄={h}, 标题='{title}', 大小={width}x{height}")
            
            # 返回第一个候选窗口
            selected_hwnd = game_candidates[0][0]
            print(f"🎯 自动选择窗口: {selected_hwnd}")
            return selected_hwnd
        
        # 最后尝试使用当前前台窗口
        hwnd = win32gui.GetForegroundWindow()
        if hwnd != 0:
            window_title = win32gui.GetWindowText(hwnd)
            print(f"⚠️ 未找到游戏窗口，使用当前活动窗口: 句柄={hwnd}, 标题='{window_title}'")
            return hwnd
            
        print("❌ 无法找到合适的窗口")
        return None
            
    except Exception as e:
        print(f"❌ 查找游戏窗口时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


class TaskManager:
    """任务管理器，跟踪和管理正在执行的任务"""
    
    def __init__(self):
        self.active_tasks: Dict[str, JobWithResult] = {}
        self.task_history: List[Dict] = []
        self.lock = threading.Lock()
    
    def add_task(self, task_name: str, job: JobWithResult):
        """添加任务到管理器"""
        with self.lock:
            self.active_tasks[task_name] = job
            self.task_history.append({
                "name": task_name,
                "job_id": job.job_id,
                "start_time": datetime.datetime.now(),
                "status": "started"
            })
    
    def remove_task(self, task_name: str):
        """从管理器中移除任务"""
        with self.lock:
            if task_name in self.active_tasks:
                job = self.active_tasks.pop(task_name)
                # 更新历史记录
                for record in reversed(self.task_history):
                    if record["name"] == task_name and record["job_id"] == job.job_id:
                        record["end_time"] = datetime.datetime.now()
                        record["status"] = "completed"
                        break
                return job
        return None
    
    def get_task(self, task_name: str) -> Optional[JobWithResult]:
        """获取指定任务"""
        with self.lock:
            return self.active_tasks.get(task_name)
    
    def get_active_tasks(self) -> Dict[str, JobWithResult]:
        """获取所有活跃任务"""
        with self.lock:
            return self.active_tasks.copy()
    
    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """获取任务历史"""
        with self.lock:
            return self.task_history[-limit:]


class CustomNotificationHandler(NotificationHandler):
    """自定义通知处理器"""
    
    def __init__(self, server_instance):
        super().__init__()
        self.server = server_instance
    
    def callback(self, message: str, details_json: str):
        """通知回调"""
        try:
            details = json.loads(details_json) if details_json else {}
            msg_type = details.get("type", "unknown")
            
            if msg_type == "task":
                task_id = details.get("task_id", "unknown")
                status = details.get("status", "unknown")
                print(f"[通知] 任务 {task_id} 状态更新: {status}")
            elif msg_type == "resource":
                res_id = details.get("res_id", "unknown")
                status = details.get("status", "unknown")
                print(f"[通知] 资源 {res_id} 状态更新: {status}")
            else:
                print(f"[通知] {message}")
                
        except Exception as e:
            print(f"[通知处理错误] {e}")


class MaaFrameworkServer:
    """独立的MaaFramework服务器"""
    
    def __init__(self):
        """初始化服务器"""
        self.tasker: Optional[Tasker] = None
        self.resource: Optional[Resource] = None
        self.controller: Optional[AdbController or Win32Controller or DbgController] = None
        self.notification_handler: Optional[CustomNotificationHandler] = None
        self.task_manager = TaskManager()
        
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        print("MaaFrameworkServer 初始化完成")
    
    def initialize(self, resource_path: str = "resource", controller_type: str = "Win32", controller_config: Dict = None):
        """
        初始化MaaFramework组件
        
        参数:
            resource_path: 资源目录路径（包含pipeline等）
            controller_type: 控制器类型 ("ADB", "Win32", "DBG")
            controller_config: 控制器配置
        """
        try:
            print("开始初始化MaaFramework...")
            
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"当前目录: {current_dir}")
            
            # 检查资源目录
            if not os.path.isabs(resource_path):
                resource_path = os.path.join(current_dir, resource_path)
            
            if not os.path.exists(resource_path):
                print(f"❌ 未找到资源目录: {resource_path}")
                print("💡 请确保resource目录存在并包含pipeline配置")
                return False
            
            if not os.path.isdir(resource_path):
                print(f"❌ {resource_path} 不是一个目录")
                return False
            
            print(f"✅ 找到资源目录: {resource_path}")
            
            # 创建通知处理器
            self.notification_handler = CustomNotificationHandler(self)
            
            # 创建Tasker
            print("创建Tasker...")
            self.tasker = Tasker(notification_handler=self.notification_handler)
            
            # 创建并配置Resource
            print("创建Resource...")
            self.resource = Resource(notification_handler=self.notification_handler)
            
            # 加载资源 - 使用资源目录路径
            print("加载资源...")
            resource_job = self.resource.post_bundle(resource_path)
            if not resource_job:
                print(f"❌ 提交资源加载任务失败: {resource_path}")
                return False
            
            print("⏳ 等待资源加载完成...")
            resource_job.wait()
            
            if not resource_job.succeeded:
                print(f"❌ 资源加载失败: {resource_path}")
                print("💡 请检查resource目录是否包含正确的pipeline配置")
                return False
            
            print("✅ 资源加载成功")
            
            # 等待资源完全加载
            timeout = 30  # 30秒超时
            start_time = time.time()
            
            while not self.resource.loaded:
                if time.time() - start_time > timeout:
                    print("❌ 等待资源加载超时")
                    return False
                time.sleep(0.1)
            
            print("✅ 资源已完全加载")
            
            # 创建并配置Controller
            print("创建Controller...")
            controller_config = controller_config or {}
            
            if controller_type.upper() == "ADB":
                self.controller = AdbController(
                    adb_path=controller_config.get("adb_path", "adb"),
                    address=controller_config.get("address", "127.0.0.1:5555"),
                    notification_handler=self.notification_handler
                )
            elif controller_type.upper() == "WIN32":
                # 查找游戏窗口
                hwnd = controller_config.get("hWnd", None)
                
                if hwnd is None:
                    print("🔍 正在查找游戏窗口...")
                    hwnd = find_game_window()
                    
                    if hwnd is None:
                        print("❌ 无法找到游戏窗口")
                        print("💡 请确保游戏正在运行，或手动指定窗口句柄")
                        return False
                
                # 创建Win32Controller
                print(f"🎯 使用窗口句柄: {hwnd}")
                self.controller = Win32Controller(
                    hWnd=hwnd,
                    notification_handler=self.notification_handler
                )
                
            elif controller_type.upper() == "DBG":
                self.controller = DbgController(
                    read_path=controller_config.get("read_path", ""),
                    write_path=controller_config.get("write_path", ""),
                    dbg_type=controller_config.get("dbg_type", 0),
                    config=controller_config.get("config", {}),
                    notification_handler=self.notification_handler
                )
            else:
                print(f"❌ 不支持的控制器类型: {controller_type}")
                return False
            
            print(f"✅ 创建 {controller_type} 控制器成功")
            
            # ✨ 关键修复：先连接Controller
            print("连接Controller...")
            connection_job = self.controller.post_connection()
            if not connection_job:
                print("❌ 提交连接任务失败")
                return False
            
            print("⏳ 等待Controller连接...")
            connection_job.wait()
            
            if not connection_job.succeeded:
                print("❌ Controller连接失败")
                print("💡 请检查游戏是否正在运行，窗口是否可见")
                return False
            
            print("✅ Controller连接成功")
            
            # 验证连接状态
            if not self.controller.connected:
                print("❌ Controller连接状态验证失败")
                return False
            
            print("✅ Controller连接状态验证成功")
            
            # 绑定Resource和Controller到Tasker
            print("绑定资源和控制器到Tasker...")
            bind_result = self.tasker.bind(self.resource, self.controller)
            if not bind_result:
                print("❌ Tasker绑定失败")
                return False
            
            print("✅ Tasker绑定成功")
            
            # 等待初始化完成
            print("等待Tasker初始化完成...")
            timeout = 60  # 增加到60秒超时
            start_time = time.time()
            
            while not self.tasker.inited:
                if time.time() - start_time > timeout:
                    print("❌ Tasker初始化超时")
                    print("💡 可能的原因：")
                    print("   - 控制器连接不稳定")
                    print("   - 资源加载有问题")
                    print("   - 系统资源不足")
                    return False
                time.sleep(0.5)
                
                # 每10秒打印一次状态
                elapsed = time.time() - start_time
                if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                    print(f"⏳ 已等待初始化 {int(elapsed)} 秒...")
            
            print("✅ Tasker初始化完成")
            print("🎉 MaaFramework初始化成功！")
            
            # 显示一些有用的信息
            if self.resource:
                try:
                    node_list = self.resource.node_list
                    print(f"📋 已加载 {len(node_list)} 个pipeline节点")
                    
                    # 检查是否包含灰域相关的pipeline
                    grey_nodes = [node for node in node_list if "灰域" in node or "开始打灰" in node]
                    if grey_nodes:
                        print(f"🎯 找到 {len(grey_nodes)} 个灰域相关节点")
                        print(f"    主要节点: {', '.join(grey_nodes[:3])}")
                    else:
                        print("⚠️ 未找到灰域相关pipeline节点")
                        
                except Exception as e:
                    print(f"📋 获取pipeline节点信息时出错: {e}")
            
            # 显示控制器信息
            if self.controller:
                try:
                    print(f"🎮 控制器UUID: {self.controller.uuid}")
                except Exception as e:
                    print(f"⚠️ 获取控制器UUID失败: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ MaaFramework初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start_grey_zone_task(self, pipeline_override: Dict = None) -> bool:
        """
        启动灰域任务
        
        参数:
            pipeline_override: pipeline覆盖配置
            
        返回:
            bool: 是否成功启动
        """
        if not self.tasker:
            print("❌ Tasker未初始化，无法启动任务")
            return False
        
        if not self.tasker.inited:
            print("❌ Tasker未完成初始化，无法启动任务")
            return False
        
        if not self.controller or not self.controller.connected:
            print("❌ Controller未连接，无法启动任务")
            return False
        
        # 检查是否已有灰域任务在运行
        existing_task = self.task_manager.get_task("GreyZone")
        if existing_task and existing_task.running:
            print("⚠️ 灰域任务已在运行中")
            return False
        
        try:
            print("🚀 开始启动灰域任务...")
            
            # 准备pipeline覆盖配置
            override_config = pipeline_override or {}
            
            # 提交任务
            job = self.tasker.post_task("!开始打灰", pipeline_override=override_config)
            
            if not job:
                print("❌ 提交灰域任务失败")
                print("💡 请确保pipeline中存在'!开始打灰'节点")
                return False
            
            # 添加到任务管理器
            self.task_manager.add_task("GreyZone", job)
            
            print(f"✅ 灰域任务已启动，任务ID: {job.job_id}")
            print("💡 使用 'stop_grey' 命令可以停止任务")
            
            return True
            
        except Exception as e:
            print(f"❌ 启动灰域任务失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_grey_zone_task(self) -> bool:
        """
        停止灰域任务
        
        返回:
            bool: 是否成功停止
        """
        if not self.tasker:
            print("❌ Tasker未初始化")
            return False
        
        try:
            # 获取正在运行的灰域任务
            grey_task = self.task_manager.get_task("GreyZone")
            
            if not grey_task:
                print("⚠️ 没有正在运行的灰域任务")
                return False
            
            if not grey_task.running:
                print("⚠️ 灰域任务已经停止")
                self.task_manager.remove_task("GreyZone")
                return True
            
            print("🛑 正在停止灰域任务...")
            
            # 发送停止指令
            stop_job = self.tasker.post_stop()
            
            if not stop_job:
                print("❌ 发送停止指令失败")
                return False
            
            print(f"✅ 停止指令已发送，停止任务ID: {stop_job.job_id}")
            
            # 等待停止完成
            print("⏳ 等待任务停止...")
            stop_job.wait()
            
            # 从任务管理器中移除
            self.task_manager.remove_task("GreyZone")
            
            print("✅ 灰域任务已停止")
            return True
            
        except Exception as e:
            print(f"❌ 停止灰域任务失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_grey_zone_status(self) -> Dict[str, Any]:
        """
        获取灰域任务状态
        
        返回:
            Dict: 任务状态信息
        """
        grey_task = self.task_manager.get_task("GreyZone")
        
        if not grey_task:
            return {
                "running": False,
                "status": "not_started",
                "job_id": None
            }
        
        return {
            "running": grey_task.running,
            "pending": grey_task.pending,
            "done": grey_task.done,
            "succeeded": grey_task.succeeded,
            "failed": grey_task.failed,
            "status": str(grey_task.status),
            "job_id": grey_task.job_id
        }
    
    def wait_for_grey_zone_completion(self, timeout: int = 300) -> Optional[Any]:
        """
        等待灰域任务完成
        
        参数:
            timeout: 超时时间（秒）
            
        返回:
            任务详情或None
        """
        grey_task = self.task_manager.get_task("GreyZone")
        
        if not grey_task:
            print("⚠️ 没有正在运行的灰域任务")
            return None
        
        try:
            print(f"⏳ 等待灰域任务完成（超时: {timeout}秒）...")
            
            start_time = time.time()
            while grey_task.running and (time.time() - start_time) < timeout:
                time.sleep(1)
                # 打印进度
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 and elapsed > 0:  # 每10秒打印一次
                    print(f"⏳ 已等待 {elapsed} 秒...")
            
            if grey_task.running:
                print(f"⚠️ 等待超时（{timeout}秒）")
                return None
            
            # 获取任务结果
            result = grey_task.get()
            
            # 从任务管理器中移除
            self.task_manager.remove_task("GreyZone")
            
            print("✅ 灰域任务执行完成")
            return result
            
        except Exception as e:
            print(f"❌ 等待任务完成时出错: {e}")
            return None
    
    def start_monitor(self):
        """启动监控线程"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔍 任务监控已启动")
    
    def stop_monitor(self):
        """停止监控线程"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
        print("🔍 任务监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查活跃任务状态
                active_tasks = self.task_manager.get_active_tasks()
                
                for task_name, job in list(active_tasks.items()):
                    if job.done:
                        # 任务完成，从管理器中移除
                        self.task_manager.remove_task(task_name)
                        status = "成功" if job.succeeded else "失败"
                        print(f"📋 任务 {task_name} 已{status} (ID: {job.job_id})")
                
                time.sleep(2)  # 每2秒检查一次
                
            except Exception as e:
                print(f"❌ 监控循环出错: {e}")
                time.sleep(5)
    
    def cleanup(self):
        """清理资源"""
        print("🧹 正在清理资源...")
        
        # 停止监控
        self.stop_monitor()
        
        # 停止所有任务
        if self.tasker:
            try:
                stop_job = self.tasker.post_stop()
                if stop_job:
                    stop_job.wait()
            except Exception as e:
                print(f"⚠️ 停止任务时出错: {e}")
        
        print("✅ 资源清理完成")


def print_help():
    """打印帮助信息"""
    help_text = """
🎮 MaaFramework 灰域服务器 - 可用命令:

基础命令:
  help, h          - 显示此帮助信息
  status, s        - 显示当前状态
  history          - 显示任务历史
  exit, quit, q    - 退出程序

灰域任务:
  start_grey       - 启动灰域任务
  stop_grey        - 停止灰域任务
  wait_grey        - 等待灰域任务完成
  grey_status      - 查看灰域任务状态

系统命令:
  clear            - 清屏
  tasker_info      - 显示Tasker信息
  resource_info    - 显示Resource信息
  controller_info  - 显示Controller信息
  find_window      - 重新查找游戏窗口

注意事项:
  - Windows平台推荐使用Win32控制器
  - 确保游戏窗口可见且未被遮挡
  - 如需使用ADB，请确保设备连接正常
  - 确保resource目录包含完整的pipeline配置
    """
    print(help_text)


def main():
    """主函数"""
    print("🎮 MaaFramework 灰域服务器启动中...")
    print("=" * 50)
    
    # 创建服务器实例
    server = MaaFrameworkServer()
    
    try:
        # 初始化服务器 - Windows平台默认配置
        controller_config = {
            # Win32控制器配置（Windows推荐）
            "hWnd": None,  # None表示自动查找游戏窗口
        }
        
        # 如果需要使用ADB（安卓模拟器），可以改为：
        # controller_type = "ADB"
        # controller_config = {
        #     "address": "127.0.0.1:5555",
        #     "adb_path": "adb"
        # }
        
        if not server.initialize(
            resource_path="resource",  # 使用resource目录
            controller_type="Win32",  # Windows平台推荐，也可以改为 "ADB" 或 "DBG"
            controller_config=controller_config
        ):
            print("❌ 服务器初始化失败")
            return
        
        # 启动监控
        server.start_monitor()
        
        print("\n🎉 服务器启动成功！")
        print("💡 输入 'help' 查看可用命令")
        print("=" * 50)
        
        # 交互式命令循环
        while True:
            try:
                command = input("\n🎮 GrayZone> ").strip().lower()
                
                if command in ['exit', 'quit', 'q']:
                    print("👋 正在退出...")
                    break
                
                elif command in ['help', 'h']:
                    print_help()
                
                elif command in ['status', 's']:
                    status = server.get_grey_zone_status()
                    active_tasks = server.task_manager.get_active_tasks()
                    print(f"📊 灰域任务状态: {status}")
                    print(f"📋 活跃任务数: {len(active_tasks)}")
                    if server.tasker:
                        print(f"🤖 Tasker运行状态: {server.tasker.running}")
                        print(f"🛑 Tasker停止状态: {server.tasker.stopping}")
                        print(f"✅ Tasker初始化状态: {server.tasker.inited}")
                    if server.resource:
                        print(f"📦 Resource加载状态: {server.resource.loaded}")
                    if server.controller:
                        print(f"🎮 Controller连接状态: {server.controller.connected}")
                
                elif command == 'history':
                    history = server.task_manager.get_task_history()
                    print("📜 任务历史:")
                    if not history:
                        print("  (暂无历史记录)")
                    for record in history:
                        start_time = record['start_time'].strftime('%H:%M:%S')
                        status = record['status']
                        print(f"  - {record['name']} (ID: {record['job_id']}) {start_time} [{status}]")
                
                elif command == 'start_grey':
                    server.start_grey_zone_task()
                
                elif command == 'stop_grey':
                    server.stop_grey_zone_task()
                
                elif command == 'wait_grey':
                    result = server.wait_for_grey_zone_completion()
                    if result:
                        print(f"📊 任务结果: {result.status}")
                
                elif command == 'grey_status':
                    status = server.get_grey_zone_status()
                    print("📊 灰域任务详细状态:")
                    for key, value in status.items():
                        print(f"  {key}: {value}")
                
                elif command == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                
                elif command == 'tasker_info':
                    if server.tasker:
                        print("🤖 Tasker信息:")
                        print(f"  初始化状态: {server.tasker.inited}")
                        print(f"  运行状态: {server.tasker.running}")
                        print(f"  停止状态: {server.tasker.stopping}")
                    else:
                        print("❌ Tasker未初始化")
                
                elif command == 'resource_info':
                    if server.resource:
                        print("📦 Resource信息:")
                        print(f"  加载状态: {server.resource.loaded}")
                        try:
                            node_list = server.resource.node_list
                            print(f"  Pipeline节点数: {len(node_list)}")
                            print(f"  资源哈希: {server.resource.hash}")
                            
                            # 显示一些关键节点
                            key_nodes = [node for node in node_list if any(keyword in node for keyword in ["灰域", "开始打灰", "CustomServer"])]
                            if key_nodes:
                                print(f"  关键节点: {', '.join(key_nodes[:5])}")
                                
                        except Exception as e:
                            print(f"  获取详细信息失败: {e}")
                    else:
                        print("❌ Resource未初始化")
                
                elif command == 'controller_info':
                    if server.controller:
                        print("🎮 Controller信息:")
                        print(f"  连接状态: {server.controller.connected}")
                        try:
                            print(f"  UUID: {server.controller.uuid}")
                        except Exception as e:
                            print(f"  获取UUID失败: {e}")
                    else:
                        print("❌ Controller未初始化")
                
                elif command == 'find_window':
                    hwnd = find_game_window()
                    if hwnd:
                        print(f"✅ 找到窗口，句柄: {hwnd}")
                    else:
                        print("❌ 未找到合适的窗口")
                
                elif command == '':
                    continue  # 空命令，忽略
                
                else:
                    print(f"❓ 未知命令: {command}")
                    print("💡 输入 'help' 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n\n🛑 检测到 Ctrl+C，正在退出...")
                break
            except EOFError:
                print("\n\n👋 检测到 EOF，正在退出...")
                break
            except Exception as e:
                print(f"❌ 命令执行出错: {e}")
    
    finally:
        # 清理资源
        server.cleanup()
        print("👋 服务器已关闭，再见！")


if __name__ == "__main__":
    main()