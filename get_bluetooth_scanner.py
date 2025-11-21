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
                return True
            else:
                print("未发现蓝牙设备或蓝牙未启用")
                return False
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
            return False

    except Exception as e:
        print(f"扫描出错: {e}")
        return False

def connect_bluetooth_device(device_name):
    """连接指定的蓝牙设备"""
    try:
        print(f"正在连接设备: {device_name}")

        # 启用设备
        enable_cmd = f'Get-PnpDevice -FriendlyName "*{device_name}*" -Class Bluetooth | Enable-PnpDevice -Confirm:$false'
        result = subprocess.run(
            ["powershell", "-Command", enable_cmd],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )

        if result.returncode == 0:
            print(f"设备 {device_name} 连接成功")
            return True
        else:
            print(f"设备 {device_name} 连接失败")
            return False

    except Exception as e:
        print(f"连接出错: {e}")
        return False

def disconnect_bluetooth_device(device_name):
    """断开指定的蓝牙设备"""
    try:
        print(f"正在断开设备: {device_name}")

        # 禁用设备
        disable_cmd = f'Get-PnpDevice -FriendlyName "*{device_name}*" -Class Bluetooth | Disable-PnpDevice -Confirm:$false'
        result = subprocess.run(
            ["powershell", "-Command", disable_cmd],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )

        if result.returncode == 0:
            print(f"设备 {device_name} 已断开连接")
            return True
        else:
            print(f"设备 {device_name} 断开失败")
            return False

    except Exception as e:
        print(f"断开出错: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python get_bluetooth_scanner.py scan           # 扫描蓝牙设备")
        print("  python get_bluetooth_scanner.py connect 名称   # 连接指定设备")
        print("  python get_bluetooth_scanner.py disconnect 名称 # 断开指定设备")
        return

    command = sys.argv[1].lower()

    if command == "scan":
        scan_bluetooth_devices()
    elif command == "connect" and len(sys.argv) >= 3:
        device_name = " ".join(sys.argv[2:])
        connect_bluetooth_device(device_name)
    elif command == "disconnect" and len(sys.argv) >= 3:
        device_name = " ".join(sys.argv[2:])
        disconnect_bluetooth_device(device_name)
    else:
        print("无效命令或缺少参数")

if __name__ == "__main__":
    main()