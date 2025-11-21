import subprocess
import re
import sys

def scan_bluetooth_devices():
    """扫描附近的蓝牙设备"""
    try:
        print("正在扫描蓝牙设备...")

        # 执行扫描命令
        result = subprocess.run(
            ["powershell", "-Command", "Get-PnpDevice -Class Bluetooth | Select-Object FriendlyName, Status | Format-Table -AutoSize"],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )

        if result.returncode == 0 and result.stdout:
            output = result.stdout.strip()
            if output and len(output) > 10:
                print("检测到的蓝牙设备:")
                print(output)
            else:
                print("未发现蓝牙设备或蓝牙未启用")
        else:
            # 备选方案
            result2 = subprocess.run(
                ["powershell", "-Command", "Get-Service bthserv"],
                capture_output=True,
                text=True,
                encoding='gbk',
                errors='ignore'
            )

            if result2.returncode == 0:
                print("蓝牙服务已运行，但未发现已配对的设备")
                print("请检查设备是否已配对并处于连接状态")
            else:
                print("蓝牙服务未运行，请先启用蓝牙")

    except Exception as e:
        print(f"扫描出错: {e}")

if __name__ == "__main__":
    scan_bluetooth_devices()