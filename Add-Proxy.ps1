# 一键添加代理环境变量到用户变量
# 作者：Claude
# 用途：快速添加HTTP/HTTPS代理到当前用户环境变量

param(
    [string]$ProxyAddress = "http://127.0.0.1:7897"
)

Write-Host "正在添加代理环境变量到用户变量..." -ForegroundColor Green

try {
    # 设置 http_proxy
    [Environment]::SetEnvironmentVariable("http_proxy", $ProxyAddress, "User")
    Write-Host "✓ 已添加 http_proxy = $ProxyAddress" -ForegroundColor Cyan

    # 设置 https_proxy
    [Environment]::SetEnvironmentVariable("https_proxy", $ProxyAddress, "User")
    Write-Host "✓ 已添加 https_proxy = $ProxyAddress" -ForegroundColor Cyan

    # 设置 no_proxy (避免本地和内网走代理)
    $noProxyValue = "localhost,127.0.0.1,192.168.*,10.*,*.local"
    [Environment]::SetEnvironmentVariable("no_proxy", $noProxyValue, "User")
    Write-Host "✓ 已添加 no_proxy = $noProxyValue" -ForegroundColor Cyan

    Write-Host "`n环境变量设置完成！" -ForegroundColor Green
    Write-Host "注意：请重新打开命令行窗口以使设置生效" -ForegroundColor Yellow

} catch {
    Write-Host "设置失败：$($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 显示当前设置
Write-Host "`n当前用户代理设置：" -ForegroundColor White
Write-Host "http_proxy: $([Environment]::GetEnvironmentVariable('http_proxy', 'User'))" -ForegroundColor Gray
Write-Host "https_proxy: $([Environment]::GetEnvironmentVariable('https_proxy', 'User'))" -ForegroundColor Gray
Write-Host "no_proxy: $([Environment]::GetEnvironmentVariable('no_proxy', 'User'))" -ForegroundColor Gray