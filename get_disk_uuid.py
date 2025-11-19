#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬盘分区UUID获取工具 - 最小化版本
项目名称项目组作者 Seraphiel  日期 2025-11-20 版本 1.0
获取所有硬盘分区的盘符和UUID信息
"""

import subprocess

def get_disk_uuid():
    """获取硬盘分区UUID信息"""
    cmd = 'powershell -Command "Get-Partition | Where-Object {$_.DriveLetter} | Select-Object DriveLetter, UniqueId"'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if result.returncode != 0:
        return []
    
    partitions = []
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if line and 'DriveLetter' not in line and '--------' not in line:
            parts = line.split()
            if len(parts) >= 2:
                partitions.append((parts[0].strip(), ' '.join(parts[1:]).strip()))
    
    return partitions

if __name__ == "__main__":
    print("硬盘分区UUID信息:")
    print("-" * 80)
    for drive, uuid in get_disk_uuid():
        print(f"盘符: {drive:>2} | UUID: {uuid}")
    print("-" * 80)