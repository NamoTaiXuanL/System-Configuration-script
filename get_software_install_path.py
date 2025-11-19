#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件安装路径获取工具
项目名称项目组Seraphiel 作者 TraeAI 日期 2025-11-19 版本 1.0
描述: 获取Windows系统指定软件的安装路径
"""

import subprocess
import json
import argparse

def get_software_install_path(software_name):
    """获取指定软件的安装路径"""
    
    # 注册表路径列表
    registry_paths = [
        "HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",
        "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",
        "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*"
    ]
    
    for registry_path in registry_paths:
        try:
            cmd = [
                "powershell", "-Command",
                f"Get-ItemProperty '{registry_path}' | "
                f"Where-Object DisplayName -like '*{software_name}*' | "
                f"Select-Object DisplayName, InstallLocation, UninstallString | "
                f"ConvertTo-Json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, dict):
                        data = [data]
                    
                    for item in data:
                        if item.get('DisplayName') and item.get('InstallLocation'):
                            return {
                                'name': item.get('DisplayName', ''),
                                'install_path': item.get('InstallLocation', ''),
                                'uninstall_string': item.get('UninstallString', '')
                            }
                except json.JSONDecodeError:
                    # 输出可能不是有效的JSON，尝试直接解析
                    if software_name.lower() in result.stdout.lower():
                        print(f"找到匹配项但JSON解析失败: {result.stdout}")
                    continue
        
        except Exception as e:
            print(f"搜索注册表路径 {registry_path} 时出错: {e}")
            continue
    
    return None

def get_store_app_path(app_name):
    """获取应用商店应用的安装路径"""
    
    try:
        cmd = [
            "powershell", "-Command",
            f"Get-AppxPackage | "
            f"Where-Object Name -like '*{app_name}*' | "
            f"Select-Object Name, InstallLocation | "
            f"ConvertTo-Json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            
            for app in data:
                if app.get('Name') and app.get('InstallLocation'):
                    return {
                        'name': app.get('Name', ''),
                        'install_path': app.get('InstallLocation', ''),
                        'type': '应用商店应用'
                    }
    
    except Exception:
        pass
    
    return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='获取指定软件的安装路径')
    parser.add_argument('software_name', help='要查找的软件名称')
    parser.add_argument('--search-store', action='store_true', help='同时搜索应用商店应用')
    
    args = parser.parse_args()
    
    # 首先搜索传统软件
    result = get_software_install_path(args.software_name)
    
    if result:
        print(f"软件名称: {result['name']}")
        print(f"安装路径: {result['install_path']}")
        if result.get('uninstall_string'):
            print(f"卸载命令: {result['uninstall_string']}")
        return
    
    # 如果没找到且启用了应用商店搜索
    if args.search_store:
        result = get_store_app_path(args.software_name)
        if result:
            print(f"应用名称: {result['name']}")
            print(f"安装路径: {result['install_path']}")
            print(f"类型: {result['type']}")
            return
    
    print(f"未找到包含 '{args.software_name}' 的软件")

if __name__ == "__main__":
    main()