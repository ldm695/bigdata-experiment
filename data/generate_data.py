#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模拟医院挂号记录数据生成器
生成 CSV 格式的模拟挂号数据，供 Spark 分析使用。
可配置记录数量，默认生成 100,000 条。
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "registration_records.csv"
NUM_RECORDS = 100_000  # 生成记录数（可调）
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

# 配置
DEPARTMENTS = {
    "内科": {"doctors": ["张伟", "王芳", "李强", "赵丽"], "fee_range": (10, 50)},
    "外科": {"doctors": ["刘洋", "陈静", "杨磊", "周婷"], "fee_range": (15, 80)},
    "儿科": {"doctors": ["吴敏", "孙浩", "朱莉", "徐鹏"], "fee_range": (20, 60)},
    "妇产科": {"doctors": ["林红", "何军", "郭丹", "马超"], "fee_range": (30, 100)},
    "眼科": {"doctors": ["黄娟", "曹明", "韩雪", "唐亮"], "fee_range": (10, 40)},
    "耳鼻喉科": {"doctors": ["任杰", "潘艳", "姚兵", "段琳"], "fee_range": (10, 45)},
    "皮肤科": {"doctors": ["董洁", "梁宇", "苏娜", "魏涛"], "fee_range": (15, 55)},
    "骨科": {"doctors": ["程辉", "丁霞", "姜波", "沈倩"], "fee_range": (20, 90)},
    "神经内科": {"doctors": ["范伟", "彭静", "谭龙", "戴莉"], "fee_range": (25, 120)},
    "心血管科": {"doctors": ["夏冰", "蔡琴", "田磊", "顾敏"], "fee_range": (30, 150)},
}

FIRST_NAMES = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴",
               "徐", "孙", "马", "朱", "胡", "郭", "何", "高", "林", "罗"]
LAST_NAMES = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "洋",
              "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞", "平"]
# 模拟数据池
HOUR_WEIGHTS = [
    (8, 12), (9, 15), (10, 10), (11, 5),
    (14, 8), (15, 10), (16, 7), (17, 3),
    (12, 1), (13, 1),
    (0, 0.1), (1, 0.05), (2, 0.02), (3, 0.02),
    (4, 0.02), (5, 0.05), (6, 0.5), (7, 2),
    (18, 1), (19, 0.5), (20, 0.2), (21, 0.1), (22, 0.1), (23, 0.1),
]


# 生成逻辑
def random_datetime() -> str:
    days_diff = (END_DATE - START_DATE).days
    random_day = START_DATE + timedelta(days=random.randint(0, days_diff))
    hours, weights = zip(*HOUR_WEIGHTS)
    hour = random.choices(hours, weights=weights, k=1)[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    dt = random_day.replace(hour=int(hour), minute=minute, second=second)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def generate_record(record_id: int) -> dict:
    dept = random.choice(list(DEPARTMENTS.keys()))
    dept_info = DEPARTMENTS[dept]
    doctor = random.choice(dept_info["doctors"])
    fee_min, fee_max = dept_info["fee_range"]
    fee = round(random.uniform(fee_min, fee_max), 2)
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return {
        "record_id": record_id,
        "patient_id": f"P{random.randint(100000, 999999)}",
        "patient_name": first + last,
        "gender": random.choice(["男", "女"]),
        "age": random.randint(0, 90),
        "department": dept,
        "doctor": doctor,
        "registration_fee": fee,
        "is_first_visit": str(random.choice([True, False])),
        "registration_time": random_datetime(),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "record_id", "patient_id", "patient_name", "gender", "age",
        "department", "doctor", "registration_fee", "is_first_visit", "registration_time"
    ]
    print(f"正在生成 {NUM_RECORDS:,} 条模拟挂号记录...")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NUM_RECORDS + 1):
            writer.writerow(generate_record(i))
            if i % 20_000 == 0:
                print(f"  已生成 {i:,} 条...")
    print(f"\n完成！文件位置：{OUTPUT_FILE}")
    print(f"   文件大小：约 {OUTPUT_FILE.stat().st_size / (1024 * 1024):.1f} MB")


if __name__ == "__main__":
    main()
