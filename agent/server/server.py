"""
自定义服务器模块
提供后台服务功能
"""

import threading
import time
import datetime
import json
import queue
from typing import Optional, Dict, Any, NamedTuple
from action.log import MaaLog_Info, MaaLog_Debug
from action.include import AgentServer, CustomAction, Context

class TaskResult(NamedTuple):
    """任务结果结构"""
    task_type: str
    task_name: str
    success: bool
    task_detail: Optional[Any]  # TaskDetail对象
    execution_time: float
    context_data: Dict

class TaskRequest(NamedTuple):
    """任务请求结构"""
    task_type: str
    task_name: str
    pipeline_override: Dict
    context_data: Dict  # 从Context中提取的必要数据

class CustomServer:
    """
    自定义服务器类
    提供后台服务和Custom Action功能
    """
    
    def __init__(self):
        """初始化CustomServer"""
        self.running = False
        self.thread = None
        self.task_queue = queue.Queue()
        self.task_results = {}  # 存储任务结果
        self.active_tasks = {}  # 存储正在执行的任务
        self.server_stats = {
            "start_time": None,
            "tasks_processed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "last_task_time": None
        }
        MaaLog_Info("CustomServer 初始化完成")
    
    def start(self, delay=0):
        """
        启动服务器
        
        参数:
            delay: 延迟启动时间（秒），默认0表示立即启动
        """
        if self.running:
            MaaLog_Info("CustomServer 已经在运行中")
            return
        
        self.running = True
        self.server_stats["start_time"] = datetime.datetime.now()
        
        if delay > 0:
            # 使用延迟启动
            self.thread = threading.Thread(target=self._delayed_start, args=(delay,), daemon=True)
            MaaLog_Info(f"CustomServer 将在 {delay} 秒后启动")
        else:
            # 立即启动
            self.thread = threading.Thread(target=self._run_service, daemon=True)
            MaaLog_Info("CustomServer 立即启动")
        
        self.thread.start()
    
    def _delayed_start(self, delay):
        """延迟启动函数"""
        MaaLog_Info(f"CustomServer 延迟启动中，等待 {delay} 秒...")
        time.sleep(delay)
        MaaLog_Info("CustomServer 延迟等待完成，开始启动后台服务")
        self._run_service()
    
    def stop(self):
        """停止服务器"""
        if not self.running:
            MaaLog_Info("CustomServer 未在运行")
            return
        
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)
        MaaLog_Info("CustomServer 后台服务已停止")
    
    def _run_service(self):
        """
        后台服务主循环
        处理任务队列和定时任务
        """
        MaaLog_Info("CustomServer 后台服务循环开始运行")
        
        last_heartbeat = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # 处理任务队列（非阻塞）
                self._process_task_queue()
                
                # 每10秒打印一次心跳信息
                if current_time - last_heartbeat >= 10:
                    self._print_heartbeat()
                    last_heartbeat = current_time
                
                # 短暂休眠，避免CPU占用过高
                time.sleep(0.1)
                
            except Exception as e:
                MaaLog_Debug(f"CustomServer 服务循环出错: {e}")
                time.sleep(1)
        
        MaaLog_Info("CustomServer 后台服务循环结束")
    
    def _print_heartbeat(self):
        """打印心跳信息"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = datetime.datetime.now() - self.server_stats["start_time"]
        queue_size = self.task_queue.qsize()
        
        MaaLog_Info(f"[CustomServer] 心跳 - 时间: {current_time}, "
                   f"运行时长: {uptime}, 队列任务: {queue_size}, "
                   f"已处理: {self.server_stats['tasks_processed']}, "
                   f"成功: {self.server_stats['tasks_succeeded']}, "
                   f"失败: {self.server_stats['tasks_failed']}")
    
    def _process_task_queue(self):
        """处理任务队列"""
        try:
            # 非阻塞获取任务
            task_request = self.task_queue.get_nowait()
            
            MaaLog_Info(f"[CustomServer] 开始处理后台任务: {task_request.task_type}")
            
            # 根据任务类型处理
            if task_request.task_type == "GreyZone_Post":
                result = self._execute_grey_zone_post_task(task_request)
            elif task_request.task_type == "Hello":
                result = self._execute_hello_task(task_request)
            else:
                MaaLog_Debug(f"未知任务类型: {task_request.task_type}")
                result = False
            
            # 更新统计信息
            self.server_stats["tasks_processed"] += 1
            if result:
                self.server_stats["tasks_succeeded"] += 1
            else:
                self.server_stats["tasks_failed"] += 1
            self.server_stats["last_task_time"] = datetime.datetime.now()
            
            # 存储结果
            task_id = f"{task_request.task_type}_{self.server_stats['tasks_processed']}"
            self.task_results[task_id] = {
                "result": result,
                "timestamp": datetime.datetime.now(),
                "task_request": task_request
            }
            
            MaaLog_Info(f"[CustomServer] 后台任务完成: {task_request.task_type}, 结果: {result}")
            
            # 标记任务完成
            self.task_queue.task_done()
            
        except queue.Empty:
            # 队列为空，正常情况
            pass
        except Exception as e:
            MaaLog_Debug(f"处理任务队列时出错: {e}")
    
    def _execute_grey_zone_post_task(self, task_request: TaskRequest):
        """
        执行灰域任务的后处理逻辑
        
        这里处理灰域任务完成后的后续工作
        比如：统计数据、定时器管理、状态更新等
        """
        MaaLog_Info(f"[CustomServer] 执行灰域任务后处理逻辑")
        MaaLog_Info(f"[CustomServer] 任务参数: {task_request.pipeline_override}")
        MaaLog_Info(f"[CustomServer] Context数据: {task_request.context_data}")
        
        # 这里可以实现后处理逻辑
        # 1. 数据统计和分析
        # 2. 定时器状态更新
        # 3. 结果通知
        # 4. 下次执行计划
        
        # 模拟后处理任务
        time.sleep(0.5)
        
        MaaLog_Info("[CustomServer] 灰域任务后处理完成")
        return True
    
    def _execute_hello_task(self, task_request: TaskRequest):
        """执行Hello任务的后台逻辑"""
        MaaLog_Info(f"[CustomServer] 执行Hello任务后台逻辑")
        return True
    
    def hello(self):
        """
        Hello方法，将被注册为Custom Action
        
        返回:
            str: 问候消息
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Hello from CustomServer! 当前时间: {current_time}"
        MaaLog_Info(f"[CustomServer.hello] {message}")
        return message
    
    def submit_task(self, task_type: str, task_name: str = "", pipeline_override: Dict = None, context_data: Dict = None):
        """
        提交任务到后台队列
        
        参数:
            task_type: 任务类型
            task_name: 任务名称
            pipeline_override: pipeline覆盖配置
            context_data: 从Context提取的数据
        """
        # 创建任务请求
        task_request = TaskRequest(
            task_type=task_type,
            task_name=task_name,
            pipeline_override=pipeline_override or {},
            context_data=context_data or {}
        )
        
        # 提交到队列
        self.task_queue.put(task_request)
        MaaLog_Info(f"[CustomServer] 任务已提交到队列: {task_type}")
    
    def Task_GreyZone(self, context: Context = None, pipeline_override: Dict = None):
        """
        执行灰域任务 - 使用Context.run_task方案
        
        参数:
            context: Context实例
            pipeline_override: pipeline覆盖配置
            
        返回:
            bool: 任务是否成功完成
        """
        MaaLog_Info("[CustomServer.Task_GreyZone] 开始执行灰域任务")
        
        if not context:
            MaaLog_Debug("Context不可用，无法执行Task_GreyZone")
            return False
        
        start_time = time.time()
        task_detail = None
        
        try:
            # 1. 预处理逻辑
            MaaLog_Info("[CustomServer] 执行灰域任务预处理...")
            
            # 准备pipeline覆盖参数
            override_config = pipeline_override or {}
            MaaLog_Info(f"[CustomServer] Pipeline覆盖配置: {override_config}")
            
            # 2. 使用Context.run_task执行实际的灰域pipeline
            MaaLog_Info("[CustomServer] 调用context.run_task执行'!开始打灰'...")
            
            task_detail = context.run_task("!开始打灰", pipeline_override=override_config)
            
            execution_time = time.time() - start_time
            
            # 3. 检查执行结果
            if task_detail:
                MaaLog_Info(f"[CustomServer] 灰域pipeline执行成功，用时: {execution_time:.2f}秒")
                MaaLog_Info(f"[CustomServer] 任务详情: Entry={task_detail.entry}, "
                           f"Status={task_detail.status}, Nodes={len(task_detail.nodes)}")
                
                # 4. 提取Context数据用于后处理
                context_data = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "execution_time": execution_time,
                    "task_status": str(task_detail.status),
                    "task_entry": task_detail.entry,
                    "nodes_count": len(task_detail.nodes)
                }
                
                # 5. 提交后处理任务到后台队列
                self.submit_task(
                    "GreyZone_Post", 
                    "!开始打灰_后处理", 
                    override_config, 
                    context_data
                )
                
                MaaLog_Info("[CustomServer] 灰域任务主流程完成，后处理任务已提交")
                return True
                
            else:
                MaaLog_Debug("[CustomServer] 灰域pipeline执行失败，返回None")
                return False
            
        except Exception as e:
            execution_time = time.time() - start_time
            MaaLog_Debug(f"[CustomServer] 执行Task_GreyZone时发生异常: {e}")
            MaaLog_Debug(f"[CustomServer] 异常发生时间: {execution_time:.2f}秒")
            import traceback
            traceback.print_exc()
            
            # 记录失败信息到后台任务
            context_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "execution_time": execution_time,
                "error": str(e),
                "success": False
            }
            
            self.submit_task(
                "GreyZone_Post", 
                "!开始打灰_错误处理", 
                pipeline_override or {}, 
                context_data
            )
            
            return False
    
    def get_server_status(self):
        """获取服务器状态信息"""
        return {
            "running": self.running,
            "uptime": (datetime.datetime.now() - self.server_stats["start_time"]).total_seconds() if self.server_stats["start_time"] else 0,
            "tasks_processed": self.server_stats["tasks_processed"],
            "tasks_succeeded": self.server_stats["tasks_succeeded"],
            "tasks_failed": self.server_stats["tasks_failed"],
            "queue_size": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "last_task_time": self.server_stats["last_task_time"].isoformat() if self.server_stats["last_task_time"] else None
        }
    
    def get_task_results(self, limit: int = 10):
        """获取最近的任务结果"""
        sorted_results = sorted(
            self.task_results.items(), 
            key=lambda x: x[1]["timestamp"], 
            reverse=True
        )
        return dict(sorted_results[:limit])
    
    def is_running(self):
        """检查服务器是否在运行"""
        return self.running


# 创建全局CustomServer实例
custom_server_instance = CustomServer()

@AgentServer.custom_action("CustomServer.hello")
class CustomServerHelloAction(CustomAction):
    """
    CustomServer的hello方法对应的Custom Action
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("CustomServer.hello Action 开始执行")
        
        try:
            # 调用CustomServer的hello方法
            message = custom_server_instance.hello()
            
            # 提交Hello任务到后台队列
            context_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "message": message
            }
            custom_server_instance.submit_task("Hello", "hello_task", {}, context_data)
            
            MaaLog_Debug(f"CustomServer.hello Action 执行成功: {message}")
            return CustomAction.RunResult(success=True)
            
        except Exception as e:
            MaaLog_Debug(f"CustomServer.hello Action 执行失败: {e}")
            return CustomAction.RunResult(success=False)


@AgentServer.custom_action("CustomServer.Task_GreyZone")
class CustomServerTaskGreyZoneAction(CustomAction):
    """
    CustomServer的Task_GreyZone方法对应的Custom Action
    这个Action会使用context.run_task真正执行灰域pipeline
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("CustomServer.Task_GreyZone Action 开始执行")
        
        try:
            # 从参数中获取pipeline覆盖配置（如果有的话）
            pipeline_override = {}
            
            # TODO: 如果需要从argv中解析参数，可以在这里添加
            # 例如：pipeline_override = json.loads(argv.param) if argv.param else {}
            
            # 调用CustomServer的Task_GreyZone方法
            # 这里会真正执行context.run_task("!开始打灰")
            result = custom_server_instance.Task_GreyZone(
                context=context, 
                pipeline_override=pipeline_override
            )
            
            if result:
                MaaLog_Debug("CustomServer.Task_GreyZone Action 执行成功")
                return CustomAction.RunResult(success=True)
            else:
                MaaLog_Debug("CustomServer.Task_GreyZone Action 执行失败")
                return CustomAction.RunResult(success=False)
            
        except Exception as e:
            MaaLog_Debug(f"CustomServer.Task_GreyZone Action 执行时发生异常: {e}")
            import traceback
            traceback.print_exc()
            return CustomAction.RunResult(success=False)


@AgentServer.custom_action("CustomServer.GetStatus")
class CustomServerGetStatusAction(CustomAction):
    """
    获取CustomServer状态的Action
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("CustomServer.GetStatus Action 开始执行")
        
        try:
            status = custom_server_instance.get_server_status()
            MaaLog_Info(f"CustomServer状态: {status}")
            
            task_results = custom_server_instance.get_task_results(5)
            MaaLog_Info(f"最近任务结果: {len(task_results)} 条")
            
            return CustomAction.RunResult(success=True)
            
        except Exception as e:
            MaaLog_Debug(f"CustomServer.GetStatus Action 执行失败: {e}")
            return CustomAction.RunResult(success=False)


def get_custom_server():
    """获取全局CustomServer实例"""
    return custom_server_instance