#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spark 医院挂号记录统计分析
"""
import sys, os, tempfile, csv as _csv_module, time
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count as _count, sum as _sum, avg, max as _max, min as _min,
    hour, date_format, when, round as _round
)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
CSV_FILE = DATA_DIR / "registration_records.csv"

SCHEMA = StructType([
    StructField("record_id", IntegerType(), True),
    StructField("patient_id", StringType(), True),
    StructField("patient_name", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("department", StringType(), True),
    StructField("doctor", StringType(), True),
    StructField("registration_fee", FloatType(), True),
    StructField("is_first_visit", StringType(), True),
    StructField("registration_time", StringType(), True),
])

# 工具函数
def _write_csv(df, name):
    """用纯 Python 写 CSV，避免 Hadoop 原生库依赖"""
    out_dir = OUTPUT_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "result.csv"
    cols = df.columns
    rows = df.collect()
    with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
        w = _csv_module.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([str(v) if v is not None else "" for v in r])
    print(f"   >> 结果已保存到 {out_file}")


def _setup_hadoop():
    """创建 Hadoop 配置绕过 Java 25 兼容性问题"""
    conf_dir = Path(tempfile.mkdtemp())
    xml = (
        '<?xml version="1.0"?>\n'
        '<configuration>\n'
        '    <property><name>hadoop.security.authentication</name><value>simple</value></property>\n'
        '    <property><name>hadoop.security.authorization</name><value>false</value></property>\n'
        '</configuration>'
    )
    (conf_dir / "core-site.xml").write_text(xml, encoding="utf-8")
    os.environ["HADOOP_CONF_DIR"] = str(conf_dir)
    os.environ["HADOOP_HOME"] = (os.environ.get("SPARK_HOME") or
                                  os.environ.get("_SPARK_HOME", "D:\\Program Files\\Apache Spark"))
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)


def create_spark():
    return (SparkSession.builder
            .appName("HospitalRegistrationAnalysis")
            .master("local[*]")
            .config("spark.sql.shuffle.partitions", "4")
            .config("spark.sql.adaptive.enabled", "true")
            .getOrCreate())

# 分析函数
def step1_load(spark):
    print("=" * 60)
    print("1. 加载数据")
    print("=" * 60)
    df = (spark.read.option("header", True).option("charset", "UTF-8")
          .schema(SCHEMA).csv(str(CSV_FILE)))
    print(f"   共加载 {df.count():,} 条记录\n")
    return df


def step2_inspect(df):
    print("=" * 60)
    print("2. 数据预览与质量检查")
    print("=" * 60)
    print("\n--- 前 5 条 ---")
    df.show(5, truncate=False)
    print("\n--- 字段统计 ---")
    df.describe(["age", "registration_fee"]).show()
    nulls = df.select([_count(when(col(c).isNull(), c)).alias(c) for c in df.columns])
    print("\n--- 空值检查 ---")
    nulls.show()


def step3_department(df):
    print("\n" + "=" * 60)
    print("3. 按科室统计挂号量")
    print("=" * 60)
    result = (df.groupBy("department")
              .agg(_count("*").alias("registration_count"),
                   _round(avg("registration_fee"), 2).alias("avg_fee"),
                   _round(_sum("registration_fee"), 2).alias("total_revenue"))
              .orderBy(col("registration_count").desc()))
    result.show(20, truncate=False)
    _write_csv(result, "by_department")


def step4_hourly(df):
    print("=" * 60)
    print("4. 按小时统计挂号量（高峰期分析）")
    print("=" * 60)
    result = (df.withColumn("hour", hour("registration_time"))
              .groupBy("hour").agg(_count("*").alias("count"))
              .orderBy("hour"))
    result.show(24, truncate=False)
    _write_csv(result, "by_hour")


def step5_monthly(df):
    print("=" * 60)
    print("5. 按月份统计挂号趋势")
    print("=" * 60)
    result = (df.withColumn("month", date_format("registration_time", "yyyy-MM"))
              .groupBy("month").agg(_count("*").alias("count"))
              .orderBy("month"))
    result.show(truncate=False)
    _write_csv(result, "by_month")


def step6_doctors(df):
    print("=" * 60)
    print("6. 热门医生 Top 10")
    print("=" * 60)
    result = (df.groupBy("department", "doctor")
              .agg(_count("*").alias("patient_count"),
                   _round(_sum("registration_fee"), 2).alias("total_revenue"))
              .orderBy(col("patient_count").desc()))
    result.show(10, truncate=False)
    _write_csv(result, "top_doctors")


def step7_age_gender(df):
    print("=" * 60)
    print("7. 患者年龄与性别分布")
    print("=" * 60)
    df.groupBy("gender").agg(_count("*").alias("count")).show()
    result = (df.withColumn("age_group",
                            when(col("age") < 18, "0-17岁")
                            .when(col("age") <= 30, "18-30岁")
                            .when(col("age") <= 45, "31-45岁")
                            .when(col("age") <= 60, "46-60岁")
                            .otherwise("60岁以上"))
              .groupBy("age_group").agg(_count("*").alias("count"))
              .orderBy("age_group"))
    result.show(truncate=False)
    _write_csv(result, "by_age_group")


def step8_first_visit(df):
    print("\n" + "=" * 60)
    print("8. 初诊与复诊比例")
    print("=" * 60)
    total = df.count()
    result = (df.groupBy("is_first_visit")
              .agg(_count("*").alias("count"))
              .withColumn("ratio", _round(col("count") / total * 100, 2)))
    result.show(truncate=False)
    _write_csv(result, "first_visit_ratio")


def step9_revenue(df):
    print("=" * 60)
    print("9. 挂号费收入汇总")
    print("=" * 60)
    r = df.agg(
        _round(_sum("registration_fee"), 2).alias("total"),
        _round(avg("registration_fee"), 2).alias("avg"),
        _round(_max("registration_fee"), 2).alias("max"),
        _round(_min("registration_fee"), 2).alias("min"),
    ).collect()[0]
    print(f"   总收入:      {r['total']:>10,.2f} 元")
    print(f"   平均挂号费:  {r['avg']:>10,.2f} 元")
    print(f"   最高挂号费:  {r['max']:>10,.2f} 元")
    print(f"   最低挂号费:  {r['min']:>10,.2f} 元")
    _write_csv(df.select(
        _round(_sum("registration_fee"), 2).alias("total_revenue"),
        _round(avg("registration_fee"), 2).alias("avg_fee"),
        _round(_max("registration_fee"), 2).alias("max_fee"),
        _round(_min("registration_fee"), 2).alias("min_fee"),
    ), "revenue_summary")


def main():
    _setup_hadoop()
    start = time.time()

    print("\n 正在启动 Spark ...")
    spark = create_spark()

    try:
        df = step1_load(spark)
        step2_inspect(df)
        step3_department(df)
        step4_hourly(df)
        step5_monthly(df)
        step6_doctors(df)
        step7_age_gender(df)
        step8_first_visit(df)
        step9_revenue(df)

        elapsed = time.time() - start
        print("\n" + "=" * 60)
        print(f" 分析完成！总耗时: {elapsed:.1f} 秒")
        print(f" 所有结果已保存到: {OUTPUT_DIR}/")
        print("=" * 60)

        # 暂停，保持 Spark UI 存活，便于截图 DAG（截图13）
        ui_url = spark.sparkContext.uiWebUrl
        print("\n" + "=" * 60)
        print(f" Spark UI 仍在运行: {ui_url}")
        print(" 请在浏览器打开上面的地址，进入 Jobs / Stages 查看 DAG Visualization。")
        print(" 截图完成后，回到此窗口按 回车 键退出。")
        print("=" * 60)
        try:
            input(" >> 按 Enter 退出并关闭 Spark UI ... ")
        except EOFError:
            pass

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
