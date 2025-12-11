"""
貓狗分類器 - 下載範例資料腳本
從網路下載小型範例資料集用於測試

注意: 此腳本下載的是小型範例資料集
若需要完整資料集，請從 Kaggle 下載:
https://www.kaggle.com/c/dogs-vs-cats/data
"""

import os
import urllib.request
import zipfile
import shutil
from pathlib import Path

# ============== 設定 ==============
DATA_DIR = "./data"
SAMPLE_SIZE = 100  # 每類下載的樣本數量

# 使用 Oxford-IIIT Pet Dataset 的子集
# 這是一個公開的學術資料集
DATASET_URL = "https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz"


def create_sample_structure():
    """建立範例資料目錄結構"""
    cats_dir = os.path.join(DATA_DIR, "cats")
    dogs_dir = os.path.join(DATA_DIR, "dogs")

    os.makedirs(cats_dir, exist_ok=True)
    os.makedirs(dogs_dir, exist_ok=True)

    print(f"已建立資料目錄結構:")
    print(f"  {cats_dir}")
    print(f"  {dogs_dir}")

    return cats_dir, dogs_dir


def print_instructions():
    """印出資料準備說明"""
    print("=" * 60)
    print("貓狗分類資料準備說明")
    print("=" * 60)
    print()
    print("由於貓狗資料集較大，建議手動下載:")
    print()
    print("方法 1: Kaggle Dogs vs Cats (推薦)")
    print("-" * 40)
    print("1. 前往: https://www.kaggle.com/c/dogs-vs-cats/data")
    print("2. 下載 train.zip")
    print("3. 解壓縮後，將檔案分類放入:")
    print(f"   - 貓圖片 -> {DATA_DIR}/cats/")
    print(f"   - 狗圖片 -> {DATA_DIR}/dogs/")
    print()
    print("方法 2: Oxford-IIIT Pet Dataset")
    print("-" * 40)
    print("1. 前往: https://www.robots.ox.ac.uk/~vgg/data/pets/")
    print("2. 下載 Images 資料集")
    print("3. 依照品種名稱分類 (貓/狗)")
    print()
    print("方法 3: 使用自己的圖片")
    print("-" * 40)
    print(f"直接將圖片放入對應目錄:")
    print(f"   - 貓圖片 -> {DATA_DIR}/cats/")
    print(f"   - 狗圖片 -> {DATA_DIR}/dogs/")
    print()
    print("=" * 60)
    print()
    print("小技巧: 建議每類至少準備 100 張以上的圖片")
    print("        圖片格式支援: .jpg, .jpeg, .png")
    print()


def download_from_url(url, save_path):
    """從 URL 下載檔案"""
    print(f"下載中: {url}")
    print(f"儲存至: {save_path}")

    try:
        urllib.request.urlretrieve(url, save_path)
        print("下載完成!")
        return True
    except Exception as e:
        print(f"下載失敗: {e}")
        return False


def check_data_status():
    """檢查資料狀態"""
    cats_dir = os.path.join(DATA_DIR, "cats")
    dogs_dir = os.path.join(DATA_DIR, "dogs")

    cat_count = 0
    dog_count = 0

    if os.path.exists(cats_dir):
        cat_count = len([f for f in os.listdir(cats_dir)
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    if os.path.exists(dogs_dir):
        dog_count = len([f for f in os.listdir(dogs_dir)
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    print()
    print("目前資料狀態:")
    print(f"  貓圖片: {cat_count} 張")
    print(f"  狗圖片: {dog_count} 張")

    if cat_count > 0 and dog_count > 0:
        print()
        print("資料已就緒! 可以開始訓練:")
        print("  python train.py")
    else:
        print()
        print("請先準備資料!")


def main():
    print("=" * 60)
    print("貓狗分類器 - 資料準備工具")
    print("=" * 60)
    print()

    # 建立目錄結構
    create_sample_structure()

    # 檢查現有資料
    check_data_status()

    # 印出說明
    print()
    print_instructions()


if __name__ == "__main__":
    main()
