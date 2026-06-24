# Apache Spark 手动安装教程（Windows）

> 适用环境：Java 25 + Python 3.13 + Windows
> 目标：跑通本项目 "Spark 在医院挂号记录统计中的应用"

---

## 目录

1. [下载 Spark](#1-下载-spark)
2. [解压到指定目录](#2-解压到指定目录)
3. [设置环境变量](#3-设置环境变量)
4. [下载 WinUtils（可选但推荐）](#4-下载-winutils可选但推荐)
5. [安装 PySpark](#5-安装-pyspark)
6. [验证安装](#6-验证安装)
7. [运行本项目](#7-运行本项目)

---

## 1. 下载 Spark

### 方法：浏览器下载

打开官网下载页面：
 https://spark.apache.org/downloads.html

按以下选项选择：

| 选项 | 选择 |
|------|------|
| **Choose a Spark release** | **3.5.5**（最新稳定版） |
| **Choose a package type** | **Pre-built for Apache Hadoop 3.3 and later** |
| **Download** | 点击第一个镜像链接，或直接点击下方下载按钮 |

> 或者直接用这个直链（如果有效）：
> https://dlcdn.apache.org/spark/spark-3.5.5/spark-3.5.5-bin-hadoop3.tgz
>
> 文件大小约 **380 MB**，下载需要几分钟。

---

## 2. 解压到指定目录

下载得到的是 `spark-3.5.5-bin-hadoop3.tgz` 文件。

如果你的 Windows 原生支持 `tar` 命令（Windows 10 1803+ 自带），用 PowerShell：

```powershell
# 进入下载目录（根据你的浏览器下载路径调整）
cd ~\Downloads

# 创建目标目录
New-Item -ItemType Directory -Force -Path "C:\spark"

# 解压到 C:\spark（--strip-components=1 会去掉顶层目录，将文件直接展开到 C:\spark 下）
tar -xzf spark-3.5.5-bin-hadoop3.tgz -C C:\spark --strip-components=1
```

**或者**用解压软件（7-Zip / WinRAR）手动解压：
1. 右键 `spark-3.5.5-bin-hadoop3.tgz` → 解压
2. 你会先得到一个 `.tar` 文件，再解压一次得到文件夹 `spark-3.5.5-bin-hadoop3`
3. 把文件夹**里面所有内容**复制到 `C:\spark`

### 验证解压结果

解压后，`C:\spark` 目录下应该有这些关键文件：

```powershell
# 检查关键目录和文件是否存在
Test-Path "C:\spark\bin\spark-shell.cmd"
Test-Path "C:\spark\bin\pyspark"
Test-Path "C:\spark\jars"
```

应该全部返回 `True`。

---

## 3. 设置环境变量

### 3.1 用 PowerShell 设置（推荐）

以**管理员身份**打开 PowerShell，执行：

```powershell
# 设置 SPARK_HOME
[Environment]::SetEnvironmentVariable("SPARK_HOME", "C:\spark", "User")

# 将 Spark bin 目录加入 PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = "$currentPath;C:\spark\bin"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# 当前会话立即生效
$env:SPARK_HOME = "C:\spark"
```

### 3.2 手动设置（图形界面）

1. 按 `Win + R` → 输入 `sysdm.cpl` → 回车
2. 点 **"高级"** 选项卡 → **"环境变量"**
3. 在 **"用户变量"** 中：
 - 点 **"新建"** → 变量名 `SPARK_HOME` → 变量值 `C:\spark`
4. 在 **"系统变量"** 中找到 `Path` → 点编辑 → 添加 `C:\spark\bin`
5. 全部点确定

---

## 4. 下载 WinUtils（可选但推荐）

Spark 在 Windows 上需要 WinUtils 来兼容 Hadoop 文件系统操作。不装也不影响本项目（我们只用本地文件），但装一下可以避免奇怪的警告。

```powershell
# 下载 winutils.exe 到 Spark 的 bin 目录
Invoke-WebRequest -Uri "https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/winutils.exe" -OutFile "C:\spark\bin\winutils.exe" -UseBasicParsing
```

下载完成后验证：
```powershell
Test-Path "C:\spark\bin\winutils.exe"
# 应返回 True
```

---

## 5. 安装 PySpark

打开 PowerShell（普通权限即可），安装 Python 的 PySpark 包：

```powershell
pip install pyspark
```

安装完成后验证：
```powershell
pip list | Select-String pyspark
```

应输出类似 `pyspark 3.5.5` 的信息。

---

## 6. 验证安装

**完全重新打开一个 PowerShell 窗口**（让环境变量生效），然后：

### 6.1 检查 Spark Shell

```powershell
spark-shell --version
```

应该输出 Spark 版本信息，类似：
```
Welcome to Spark version 3.5.5
Using Scala version 2.13.x
...
```

### 6.2 检查 PySpark

```powershell
pyspark --version
```

应该输出：
```
Welcome to Spark version 3.5.5
...
```

### 6.3 测试 PySpark 交互式运行

```powershell
pyspark
```

进入 PySpark Shell 后，输入：
```python
data = list(range(1, 11))
rdd = spark.sparkContext.parallelize(data)
print(f"总和: {rdd.sum()}")
exit()
```

应该输出 `总和: 55`。

---

## 7. 运行本项目

安装完成后，在本项目目录中依次执行：

```powershell
# 进入项目
cd D:\Agents\Codex\BigData Experiment

# 生成 10 万条模拟挂号数据
python data/generate_data.py

# 运行 Spark 分析
python analysis/hospital_analysis.py
```

---

## 8. 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `spark-shell` 不是可执行文件 | 环境变量没生效 | 重新打开 PowerShell |
| `Java gateway process exited` | 找不到 Java | 确认 `java -version` 可用 |
| 找不到或无法加载主类 | Spark 解压不完整 | 重新解压检查 `C:\spark\jars\` 目录 |
| 各种 `winutils` 报错 | 缺少 WinUtils | 不影响本项目，可按第 4 步装上 |

---

## 9. 卸载（如果需要）

```powershell
# 删除 Spark 文件
Remove-Item -Recurse -Force "C:\spark"

# 移除环境变量
[Environment]::SetEnvironmentVariable("SPARK_HOME", $null, "User")

# 卸载 PySpark
pip uninstall pyspark -y
```
