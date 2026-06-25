# Spark 在医院挂号记录统计中的应用

---

## 项目概述

本项目模拟一家综合性医院的 **挂号记录数据**，使用 **Apache Spark（PySpark）** 进行多维度统计分析，涵盖：

| 分析维度 | 说明 |
|----------|------|
| 各科室挂号量 | 统计每个科室的挂号数量、平均费用、总收入 |
| 时间高峰期分析 | 按小时分析挂号量分布，找出就诊高峰时段 |
| 月度趋势分析 | 观察全年每月挂号量的变化趋势 |
| 热门医生排行 | 找出接诊量最高的医生 Top 10 |
| 患者画像分析 | 年龄分组 + 性别分布统计 |
| 初诊/复诊比例 | 了解新老患者构成 |
| 收入汇总 | 全时间段挂号费汇总统计 |

---

## 技术栈

| 技术 | 用途 |
|------|------|
| **Apache Spark 3.5+** | 分布式计算引擎（核心） |
| **PySpark** | Spark 的 Python API |
| **Python 3.8+** | 编程语言 |
| **CSV** | 数据存储格式 |

---

## 项目结构

```
BigData Experiment/
├── README.md # 本文件（项目总说明）
├── data/
│ ├── generate_data.py # 模拟数据生成器
│ └── registration_records.csv # 生成的挂号数据（运行后产生）
├── analysis/
│ └── hospital_analysis.py # Spark 主分析脚本
├── output/ # 分析结果输出目录
├── environment/
│ └── setup.ps1 # Windows 环境一键安装脚本
└── requirements.txt # Python 依赖清单
```

---

## 快速开始（4 步完成）

### 前提条件检查

开始之前，请确认你的电脑已安装以下软件。可在 PowerShell / 终端中运行对应命令自行检查：

| 软件 | 版本要求 | 检查命令 |
|------|----------|----------|
| **Java** | 17 / 21 / 25（LTS 版本） | `java -version` |
| **Python** | 3.8 以上（推荐 3.13） | `python --version` |
| **pip** | 随 Python 一起安装 | `pip --version` |
| **Apache Spark** | 3.5+（尚未安装也没关系） | `pyspark --version` |

> 若某条命令报「找不到命令 / 不是内部或外部命令」，说明该软件尚未安装或未加入 PATH。
> Java 和 Python 请先自行安装；**Apache Spark 可在下面第 1 步一键搞定**，无需提前准备。

### 第 1 步：安装 Apache Spark

> 约 5 分钟

**方式 A：使用一键脚本（推荐）**

以 **管理员身份** 打开 PowerShell，执行：

```powershell
# 进入项目目录
cd D:\Agents\Codex\BigData Experiment

# 运行安装脚本
.\environment\setup.ps1
```

**方式 B：手动安装**

1. 访问 https://spark.apache.org/downloads.html
2. 选择 **Spark 3.5.5** → **Pre-built for Apache Hadoop 3.3 and later**
3. 下载 `.tgz` 文件并解压到 `C:\spark`
4. 设置环境变量：
 ```
 SPARK_HOME = C:\spark
 PATH 添加 %SPARK_HOME%\bin
 ```
5. 下载 WinUtils.exe 放入 `C:\spark\bin`
6. 重启 PowerShell

**验证安装：**
```powershell
spark-shell --version
# 或
pyspark --version
```

### 第 2 步：安装 Python 依赖

```powershell
pip install -r requirements.txt
```

### 第 3 步：生成模拟数据

```powershell
python data/generate_data.py
```

> 默认生成 **10 万条** 挂号记录，文件约 8~10 MB。 
> 你可修改 `data/generate_data.py` 中的 `NUM_RECORDS` 来调整数据量。

### 第 4 步：运行 Spark 分析

```powershell
python analysis/hospital_analysis.py
```

> 首次运行 Spark 需要初始化 JVM，约 10-30 秒 
> 后续运行会更快

**关于 Spark UI（查看任务执行的 DAG 图）**

分析全部完成后，程序**不会立即退出**，而是会打印出 Spark UI 的地址（通常为 `http://localhost:4040`，被占用时自动顺延到 4041 等），并停在「按 Enter 退出」处等待。

此时可在浏览器打开该地址，进入 **Jobs** 或 **Stages** 标签，展开 **DAG Visualization** 查看任务的有向无环图。查看完毕后回到终端按 **回车** 键，程序才会关闭 Spark UI 并退出。

> 由于 `local[*]` 单机模式下分析仅需数秒即可完成，如不暂停，Spark UI 会随程序退出而立即关闭、来不及查看。该暂停即为此设计。
> 注意：需在支持键盘输入的终端（PowerShell / 终端 / IDE 集成终端）中运行；在不支持输入的环境下程序会直接退出，无法查看 UI。

---

## 分析结果解读

运行完成后，在 `output/` 目录下会生成多个子文件夹，每个包含一个 CSV 结果文件：

| 输出目录 | 内容 | 业务含义 |
|----------|------|----------|
| `output/by_department/` | 各科室挂号量/平均费/总收入 | 了解哪些科室最繁忙 |
| `output/by_hour/` | 24小时挂号分布 | 确定高峰期，辅助排班 |
| `output/by_month/` | 月度挂号趋势 | 识别淡旺季 |
| `output/top_doctors/` | 医生接诊量排行 | 医生工作负荷评估 |
| `output/by_age_group/` | 年龄分组统计 | 患者画像分析 |
| `output/first_visit_ratio/` | 初复诊比例 | 新患者获取情况 |

---

## 常见问题

**Q: 运行报错 "Java gateway process exited"？** 
A: 确保 Java 已安装且 `java` 命令可用。运行 `java -version` 检查。

**Q: Spark 启动时提示找不到 Hadoop？** 
A: 在 Python 文件开头添加：
```python
import os
os.environ["SPARK_HOME"] = "C:\\spark"
os.environ["HADOOP_HOME"] = "C:\\spark"
```

**Q: 生成的数据不够真实？** 
A: 可修改 `generate_data.py` 中的科室、医生列表，或调整时间分布权重。

---
