<#
.SYNOPSIS
  Spark 医院挂号项目 - Windows 环境一键安装脚本
.DESCRIPTION
  自动下载安装 Apache Spark 3.5.5 并配置环境变量。
  需要以管理员身份运行。
#>

$ErrorActionPreference = "Stop"
$SPARK_VERSION = "3.5.5"
$HADOOP_VERSION = "3"
$INSTALL_DIR = "C:\spark"
$DOWNLOAD_URL = "https://dlcdn.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz"
$WINUTILS_URL = "https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/winutils.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Spark 医院挂号项目 - 环境安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "建议以管理员身份运行此脚本以确保环境变量设置成功。"
    $continue = Read-Host "是否继续? (y/n)"
    if ($continue -ne "y") { exit }
}

# 检查 Java
try {
    $javaVer = java -version 2>&1
    Write-Host "✅ Java 已安装" -ForegroundColor Green
} catch {
    Write-Error "❌ 未检测到 Java！请先安装 JDK 17+"
    exit 1
}

# 检查 Python
try {
    $pyVer = python --version
    Write-Host "✅ Python 已安装" -ForegroundColor Green
} catch {
    Write-Error "❌ 未检测到 Python！请先安装 Python 3.8+"
    exit 1
}

# Step 1: 下载 Spark
if (-not (Test-Path "$INSTALL_DIR\bin\spark-shell.cmd")) {
    Write-Host ""
    Write-Host "📥 步骤1: 下载 Apache Spark $SPARK_VERSION ..." -ForegroundColor Yellow
    
    $tgzPath = "$env:TEMP\spark-$SPARK_VERSION.tgz"
    Write-Host "   下载中（约 380MB，可能需要几分钟）..."
    
    try {
        Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $tgzPath -UseBasicParsing -ErrorAction Stop
        Write-Host "   ✅ 下载完成" -ForegroundColor Green
    } catch {
        Write-Warning "   自动下载失败，尝试备用下载..."
        Write-Host "   请手动下载：$DOWNLOAD_URL"
        Write-Host "   下载后解压到 $INSTALL_DIR 即可"
        $manual = Read-Host "   是否继续(输入路径)或输入 n 跳过? (路径/n)"
        if ($manual -eq "n") { exit }
        if ($manual -ne "") {
            $tgzPath = $manual
        }
    }

    # 解压
    if (Test-Path $tgzPath) {
        Write-Host "   正在解压..."
        New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null
        tar -xzf $tgzPath -C $INSTALL_DIR --strip-components=1
        Write-Host "   ✅ 解压完成" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Spark 已安装，跳过下载" -ForegroundColor Green
}

# Step 2: 下载 WinUtils
if (-not (Test-Path "$INSTALL_DIR\bin\winutils.exe")) {
    Write-Host ""
    Write-Host "📥 步骤2: 下载 WinUtils（Windows Hadoop 兼容层）..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $WINUTILS_URL -OutFile "$INSTALL_DIR\bin\winutils.exe" -UseBasicParsing
        Write-Host "   ✅ WinUtils 下载完成" -ForegroundColor Green
    } catch {
        Write-Warning "   WinUtils 下载失败（不影响核心功能）"
    }
} else {
    Write-Host "✅ WinUtils 已存在" -ForegroundColor Green
}

# Step 3: 设置环境变量
Write-Host ""
Write-Host "⚙️  步骤3: 设置环境变量..." -ForegroundColor Yellow

[Environment]::SetEnvironmentVariable("SPARK_HOME", $INSTALL_DIR, "User")
[Environment]::SetEnvironmentVariable("HADOOP_HOME", $INSTALL_DIR, "User")
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$INSTALL_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$INSTALL_DIR\bin", "User")
}

# 为当前会话设置
$env:SPARK_HOME = $INSTALL_DIR
$env:HADOOP_HOME = $INSTALL_DIR

Write-Host "   ✅ 环境变量已设置 (SPARK_HOME = $INSTALL_DIR)" -ForegroundColor Green

# Step 4: 安装 Python 依赖
Write-Host ""
Write-Host "📦 步骤4: 安装 Python 依赖..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "   ✅ Python 依赖安装完成" -ForegroundColor Green

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ 环境安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "接下来请执行："
Write-Host ""
Write-Host "  1️⃣  生成模拟数据"
Write-Host "      python data/generate_data.py"
Write-Host ""
Write-Host "  2️⃣  运行 Spark 分析"
Write-Host "      python analysis/hospital_analysis.py"
Write-Host ""
Write-Host "  3️⃣  查看结果"
Write-Host "      Get-ChildItem output/"
Write-Host ""

# 验证
try {
    $ver = & "$INSTALL_DIR\bin\spark-shell.cmd" --version 2>&1 | Select-String -Pattern "version"
    Write-Host "✅ Spark 验证通过：$ver" -ForegroundColor Green
} catch {
    Write-Host "⚠️  请重启 PowerShell 后运行 spark-shell --version 验证" -ForegroundColor Yellow
}
