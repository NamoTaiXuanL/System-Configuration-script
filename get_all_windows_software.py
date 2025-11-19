#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows系统完整软件信息获取工具
项目名称项目组Seraphiel 作者 TraeAI 邮箱 - 日期 2025-11-19 版本 2.0
描述: 获取Windows系统安装的所有软件信息（包括传统软件、应用商店应用、系统组件等）
"""

import subprocess
import json
import argparse
from datetime import datetime
import os

def get_registry_software():
    """从注册表获取传统安装的软件信息"""
    software_list = []
    
    # 获取64位系统上的软件（Wow6432Node）
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
                f"Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, UninstallString | "
                f"Where-Object {{$_.DisplayName -ne $null}} | "
                f"ConvertTo-Json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    if item.get('DisplayName'):
                        software_list.append({
                            'type': '传统软件',
                            'name': item.get('DisplayName', ''),
                            'version': item.get('DisplayVersion', ''),
                            'publisher': item.get('Publisher', ''),
                            'install_date': item.get('InstallDate', ''),
                            'uninstall_string': item.get('UninstallString', '')
                        })
        
        except Exception as e:
            print(f"获取注册表路径 {registry_path} 时出错: {e}")
    
    return software_list

def get_store_apps():
    """获取Windows应用商店应用"""
    store_apps = []
    
    try:
        cmd = [
            "powershell", "-Command",
            "Get-AppxPackage | "
            "Select-Object Name, Version, PackageFullName, Publisher, InstallLocation | "
            "ConvertTo-Json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            
            for app in data:
                if app.get('Name'):
                    store_apps.append({
                        'type': '应用商店应用',
                        'name': app.get('Name', ''),
                        'version': str(app.get('Version', '')),
                        'publisher': app.get('Publisher', ''),
                        'package_name': app.get('PackageFullName', ''),
                        'install_location': app.get('InstallLocation', '')
                    })
    
    except Exception as e:
        print(f"获取应用商店应用时出错: {e}")
    
    return store_apps

def get_winget_apps():
    """使用winget获取已安装的应用"""
    winget_apps = []
    
    try:
        # 检查winget是否可用
        subprocess.run(["winget", "--version"], capture_output=True, check=True)
        
        # 获取winget安装的应用（使用UTF-8编码）
        cmd = ["winget", "list", "--accept-source-agreements"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8')
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.split('\n')
            for line in lines[3:]:  # 跳过表头
                if line.strip() and '---' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        name = ' '.join(parts[1:-2])
                        version = parts[-2]
                        publisher = parts[-1] if parts[-1] != 'Unknown' else '未知'
                        
                        winget_apps.append({
                            'type': 'winget应用',
                            'name': name,
                            'version': version,
                            'publisher': publisher
                        })
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # winget不可用，跳过
    except Exception as e:
        print(f"获取winget应用时出错: {e}")
    
    return winget_apps

def get_system_features():
    """获取Windows系统功能和组件"""
    features = []
    
    try:
        cmd = [
            "powershell", "-Command",
            "Get-WindowsOptionalFeature -Online | "
            "Where-Object {$_.State -eq 'Enabled'} | "
            "Select-Object FeatureName, State | "
            "ConvertTo-Json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            
            for feature in data:
                features.append({
                    'type': '系统功能',
                    'name': feature.get('FeatureName', ''),
                    'state': feature.get('State', '')
                })
    
    except Exception as e:
        print(f"获取系统功能时出错: {e}")
    
    return features

def get_services():
    """获取Windows服务信息"""
    services = []
    
    try:
        cmd = [
            "powershell", "-Command",
            "Get-Service | "
            "Where-Object {$_.Status -eq 'Running'} | "
            "Select-Object Name, DisplayName, Status | "
            "ConvertTo-Json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            
            for service in data:
                services.append({
                    'type': '系统服务',
                    'name': service.get('DisplayName', ''),
                    'service_name': service.get('Name', ''),
                    'status': service.get('Status', '')
                })
    
    except Exception as e:
        print(f"获取服务信息时出错: {e}")
    
    return services

def filter_software(all_software, filters):
    """根据过滤器筛选软件"""
    filtered = all_software
    
    if filters.get('name'):
        filtered = [s for s in filtered if filters['name'].lower() in s['name'].lower()]
    
    if filters.get('type'):
        filtered = [s for s in filtered if filters['type'] == s['type']]
    
    if filters.get('publisher'):
        filtered = [s for s in filtered if filters['publisher'].lower() in s.get('publisher', '').lower()]
    
    return filtered

def export_results(data, filename, format_type='txt'):
    """导出结果到文件"""
    try:
        if format_type == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Windows系统软件信息报告\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                # 按类型分组输出
                types = {}
                for item in data:
                    if item['type'] not in types:
                        types[item['type']] = []
                    types[item['type']].append(item)
                
                for type_name, items in types.items():
                    f.write(f"{type_name} ({len(items)}个):\n")
                    f.write("-" * 60 + "\n")
                    
                    for i, item in enumerate(items, 1):
                        f.write(f"{i}. {item['name']}\n")
                        if item.get('version'):
                            f.write(f"   版本: {item['version']}\n")
                        if item.get('publisher'):
                            f.write(f"   发布者: {item['publisher']}\n")
                        if item.get('install_date'):
                            f.write(f"   安装日期: {item['install_date']}\n")
                        f.write("\n")
                    f.write("\n")
        
        print(f"结果已导出到: {os.path.abspath(filename)}")
        
    except Exception as e:
        print(f"导出文件时出错: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='获取Windows系统所有软件信息')
    parser.add_argument('--filter-name', help='按名称过滤')
    parser.add_argument('--filter-type', help='按类型过滤（传统软件/应用商店应用/系统功能等）')
    parser.add_argument('--filter-publisher', help='按发布者过滤')
    parser.add_argument('--export', choices=['txt', 'json'], help='导出格式')
    parser.add_argument('--output', default='windows_software_report', help='输出文件名')
    parser.add_argument('--skip-services', action='store_true', help='跳过服务信息')
    parser.add_argument('--skip-features', action='store_true', help='跳过系统功能')
    
    args = parser.parse_args()
    
    print("正在全面扫描Windows系统软件信息...")
    
    all_software = []
    
    # 获取各种类型的软件信息
    print("1. 获取传统安装软件...")
    all_software.extend(get_registry_software())
    
    print("2. 获取应用商店应用...")
    all_software.extend(get_store_apps())
    
    print("3. 获取winget应用...")
    all_software.extend(get_winget_apps())
    
    if not args.skip_features:
        print("4. 获取系统功能...")
        all_software.extend(get_system_features())
    
    if not args.skip_services:
        print("5. 获取系统服务...")
        all_software.extend(get_services())
    
    # 应用过滤器
    filters = {}
    if args.filter_name:
        filters['name'] = args.filter_name
    if args.filter_type:
        filters['type'] = args.filter_type
    if args.filter_publisher:
        filters['publisher'] = args.filter_publisher
    
    filtered_data = filter_software(all_software, filters)
    
    # 输出统计信息
    print(f"\n扫描完成！共找到 {len(all_software)} 个软件/组件")
    
    type_counts = {}
    for item in all_software:
        if item['type'] not in type_counts:
            type_counts[item['type']] = 0
        type_counts[item['type']] += 1
    
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count}个")
    
    if filters:
        print(f"过滤后结果: {len(filtered_data)}个")
    
    # 导出结果
    if args.export:
        filename = f"{args.output}.{args.export}"
        export_results(filtered_data if filters else all_software, filename, args.export)
    
    # 显示所有结果
    if filtered_data:
        print(f"\n所有结果 ({len(filtered_data)}个):")
        print("=" * 80)
        for i, item in enumerate(filtered_data, 1):
            print(f"{i}. [{item['type']}] {item['name']}")
            if item.get('version'):
                print(f"   版本: {item['version']}")
            if item.get('publisher'):
                print(f"   发布者: {item['publisher']}")
            if item.get('install_date'):
                print(f"   安装日期: {item['install_date']}")
            print()

if __name__ == "__main__":
    main()