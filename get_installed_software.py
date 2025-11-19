#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统软件信息获取工具 - Windows版本
项目名称项目组Seraphiel 作者 TraeAI 邮箱 - 日期 2025-11-19 版本 1.0
描述: 获取Windows系统安装的所有软件信息
"""

import subprocess
import json
import re
from datetime import datetime
import argparse

def get_windows_software():
    """获取Windows系统安装的软件信息"""
    software_list = []
    
    # 使用PowerShell获取注册表中的软件信息
    powershell_cmd = [
        "Get-ItemProperty", 
        "HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",
        "|", "Select-Object", "DisplayName, DisplayVersion, Publisher, InstallDate",
        "|", "Where-Object", "{$_.DisplayName -ne $null}",
        "|", "ConvertTo-Json"
    ]
    
    try:
        # 执行PowerShell命令
        result = subprocess.run(
            ["powershell", "-Command", " ".join(powershell_cmd)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            software_data = json.loads(result.stdout)
            
            # 处理单个或多个软件条目
            if isinstance(software_data, dict):
                software_data = [software_data]
            
            for software in software_data:
                if software.get('DisplayName'):
                    software_list.append({
                        'name': software.get('DisplayName', ''),
                        'version': software.get('DisplayVersion', ''),
                        'publisher': software.get('Publisher', ''),
                        'install_date': software.get('InstallDate', '')
                    })
        
    except (subprocess.TimeoutExpired, json.JSONDecodeError, subprocess.SubprocessError) as e:
        print(f"获取软件信息时出错: {e}")
    
    return software_list

def get_windows_store_apps():
    """获取Windows应用商店安装的应用"""
    store_apps = []
    
    try:
        # 获取所有已安装的应用包
        cmd = ["powershell", "Get-AppxPackage", "|", "Select-Object", "Name, Version, PackageFullName", "|", "ConvertTo-Json"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout.strip():
            apps_data = json.loads(result.stdout)
            
            if isinstance(apps_data, dict):
                apps_data = [apps_data]
            
            for app in apps_data:
                if app.get('Name'):
                    store_apps.append({
                        'name': app.get('Name', ''),
                        'version': app.get('Version', ''),
                        'package_name': app.get('PackageFullName', '')
                    })
    
    except Exception as e:
        print(f"获取应用商店应用时出错: {e}")
    
    return store_apps

def filter_software(software_list, filters):
    """根据过滤器筛选软件列表"""
    filtered_list = software_list
    
    if filters.get('name'):
        filtered_list = [s for s in filtered_list if filters['name'].lower() in s['name'].lower()]
    
    if filters.get('publisher'):
        filtered_list = [s for s in filtered_list if filters['publisher'].lower() in s.get('publisher', '').lower()]
    
    return filtered_list

def export_to_file(software_list, filename, format_type='txt'):
    """导出软件列表到文件"""
    try:
        if format_type == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(software_list, f, ensure_ascii=False, indent=2)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"软件列表导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n")
                
                for i, software in enumerate(software_list, 1):
                    f.write(f"{i}. {software['name']}\n")
                    f.write(f"   版本: {software.get('version', '未知')}\n")
                    f.write(f"   发布者: {software.get('publisher', '未知')}\n")
                    if software.get('install_date'):
                        f.write(f"   安装日期: {software.get('install_date')}\n")
                    f.write("-" * 40 + "\n")
        
        print(f"软件列表已导出到: {filename}")
        
    except Exception as e:
        print(f"导出文件时出错: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='获取Windows系统安装的软件信息')
    parser.add_argument('--filter-name', help='按软件名称过滤')
    parser.add_argument('--filter-publisher', help='按发布者过滤')
    parser.add_argument('--export', choices=['txt', 'json'], help='导出格式')
    parser.add_argument('--output', default='software_list', help='输出文件名(不含扩展名)')
    parser.add_argument('--include-store', action='store_true', help='包含应用商店应用')
    
    args = parser.parse_args()
    
    print("正在获取系统软件信息...")
    
    # 获取传统软件
    software_list = get_windows_software()
    
    # 获取应用商店应用
    if args.include_store:
        store_apps = get_windows_store_apps()
        software_list.extend(store_apps)
    
    # 应用过滤器
    filters = {}
    if args.filter_name:
        filters['name'] = args.filter_name
    if args.filter_publisher:
        filters['publisher'] = args.filter_publisher
    
    filtered_software = filter_software(software_list, filters)
    
    # 输出结果
    print(f"\n找到 {len(filtered_software)} 个软件:")
    print("=" * 80)
    
    for i, software in enumerate(filtered_software, 1):
        print(f"{i}. {software['name']}")
        print(f"   版本: {software.get('version', '未知')}")
        print(f"   发布者: {software.get('publisher', '未知')}")
        if software.get('install_date'):
            print(f"   安装日期: {software.get('install_date')}")
        print("-" * 60)
    
    # 导出到文件
    if args.export:
        filename = f"{args.output}.{args.export}"
        export_to_file(filtered_software, filename, args.export)

if __name__ == "__main__":
    main()