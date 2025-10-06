import socket
import struct
import threading
import time
from datetime import datetime
import re
import sys
import os

class HTTPPacketCapture:
    """HTTP数据包捕获类"""
    
    def __init__(self):
        self.running = False
        self.session_count = 0
        self.connections = {}  # 存储连接状态
        
    def start_capture(self):
        """开始捕获HTTP流量"""
        if os.name != 'nt':
            print("此程序目前只支持Windows系统")
            return
            
        print("HTTP/HTTPS 流量捕获工具")
        print("="*80)
        print("正在初始化网络捕获...")
        print("="*80)
        
        self.running = True
        
        try:
            # 创建原始套接字
            # 在Windows上捕获所有IP数据包
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            
            # 绑定到本地IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.sock.bind((local_ip, 0))
            
            # 设置为混杂模式，接收所有数据包
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            self.sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
            
            print(f"开始捕获网络流量 (本地IP: {local_ip})")
            print("按 Ctrl+C 停止捕获\n")
            
            while self.running:
                try:
                    # 接收数据包
                    packet, addr = self.sock.recvfrom(65565)
                    self.process_packet(packet)
                except Exception as e:
                    if self.running:
                        print(f"处理数据包时出错: {e}")
                        
        except PermissionError:
            print("请以管理员身份运行此程序")
        except Exception as e:
            print(f"捕获错误: {e}")
        finally:
            self.stop_capture()
    
    def stop_capture(self):
        """停止捕获"""
        self.running = False
        if hasattr(self, 'sock'):
            try:
                self.sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
                self.sock.close()
            except:
                pass
    
    def process_packet(self, packet):
        """处理捕获的数据包"""
        try:
            # 解析IP头
            ip_header = packet[0:20]
            iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
            
            protocol = iph[6]
            src_ip = socket.inet_ntoa(iph[8])
            dst_ip = socket.inet_ntoa(iph[9])
            
            # 只处理TCP数据包
            if protocol == 6:  # TCP
                ip_header_length = (iph[0] & 0xF) * 4
                tcp_header_start = ip_header_length
                
                # 解析TCP头
                tcp_header = packet[tcp_header_start:tcp_header_start + 20]
                if len(tcp_header) < 20:
                    return
                    
                tcph = struct.unpack('!HHLLBBHHH', tcp_header)
                src_port = tcph[0]
                dst_port = tcph[1]
                
                # 检查是否是HTTP端口 (80, 8080, 3000, 8000等常见端口)
                http_ports = [80, 8080, 3000, 8000, 8888, 9000]
                is_http = src_port in http_ports or dst_port in http_ports
                
                if is_http:
                    tcp_header_length = (tcph[4] >> 4) * 4
                    data_start = tcp_header_start + tcp_header_length
                    data = packet[data_start:]
                    
                    if data:
                        self.process_http_data(src_ip, src_port, dst_ip, dst_port, data)
                        
        except Exception as e:
            pass  # 忽略解析错误
    
    def process_http_data(self, src_ip, src_port, dst_ip, dst_port, data):
        """处理HTTP数据"""
        try:
            data_str = data.decode('utf-8', errors='ignore')
            
            # 检查是否是HTTP请求
            if self.is_http_request(data_str):
                self.print_http_request(src_ip, src_port, dst_ip, dst_port, data_str)
            
            # 检查是否是HTTP响应
            elif self.is_http_response(data_str):
                self.print_http_response(src_ip, src_port, dst_ip, dst_port, data_str)
                
        except:
            pass
    
    def is_http_request(self, data):
        """判断是否是HTTP请求"""
        http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'CONNECT']
        first_line = data.split('\r\n')[0] if '\r\n' in data else data.split('\n')[0]
        return any(first_line.startswith(method + ' ') for method in http_methods)
    
    def is_http_response(self, data):
        """判断是否是HTTP响应"""
        return data.startswith('HTTP/')
    
    def print_http_request(self, src_ip, src_port, dst_ip, dst_port, data):
        """打印HTTP请求"""
        self.session_count += 1
        
        print(f"\n{'='*80}")
        print(f"HTTP请求 #{self.session_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"来源: {src_ip}:{src_port} -> 目标: {dst_ip}:{dst_port}")
        print(f"{'='*80}")
        
        # 提取和格式化HTTP请求
        lines = data.split('\r\n')
        for i, line in enumerate(lines):
            if line.strip() == '' and i < len(lines) - 1:
                # 遇到空行，后面是请求体
                break
            print(line)
        
        print(f"\n{'-'*60}")
    
    def print_http_response(self, src_ip, src_port, dst_ip, dst_port, data):
        """打印HTTP响应"""
        print(f"\nHTTP响应 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"来源: {src_ip}:{src_port} -> 目标: {dst_ip}:{dst_port}")
        print("-" * 40)
        
        # 只打印响应头，不打印响应体（通常很大）
        lines = data.split('\r\n')
        for line in lines:
            if line.strip() == '':
                break
            print(line)
        
        print(f"\n{'-'*60}")

def main():
    """主函数"""
    # 检查是否以管理员权限运行
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("\n警告: 当前未以管理员权限运行")
            print("请右键点击命令提示符，选择'以管理员身份运行'")
    except:
        pass
    
    capture = HTTPPacketCapture()
    
    try:
        capture.start_capture()
    except KeyboardInterrupt:
        print("\n\n正在停止捕获...")
        capture.stop_capture()
        print("程序已退出")

if __name__ == "__main__":
    main()