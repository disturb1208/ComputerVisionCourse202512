# DAY1 - 電腦視覺基礎：影像處理管線

## 課程目標

本課程將學習如何使用 OpenCV 建立影像處理管線 (Pipeline)，包含：
- 影像模糊化 (Blur)
- 二值化處理 (Threshold)
- 邊緣偵測 (Edge Detection)
- 輪廓檢測 (Contour Detection)
- 霍夫圓檢測 (Hough Circle Detection)

---

## 環境設置

### 1. 安裝 Python

確保已安裝 Python 3.8 或以上版本。

### 2. 安裝相依套件

開啟終端機 (Terminal/CMD)，進入 DAY1 資料夾後執行：

```bash
cd DAY1
pip install -r requirements.txt
```

若要使用 GUI 版本，還需安裝 Pillow：

```bash
pip install Pillow
```

---

## 檔案說明

| 檔案名稱 | 說明 |
|---------|------|
| `main.py` | 命令列版本的影像處理程式 |
| `GUI.py` | 圖形介面版本的影像處理程式 |
| `requirements.txt` | Python 相依套件清單 |
| `Image_20251210104315649.bmp` | 範例影像 |
| `processed_result.jpg` | 處理後的結果影像 |

---

## 操作方式

### 方式一：命令列版本 (main.py)

#### 執行步驟

1. 開啟終端機，進入 DAY1 資料夾：
   ```bash
   cd DAY1
   ```

2. 執行程式：
   ```bash
   python main.py
   ```

3. 程式會依序顯示：
   - 原始影像
   - 模糊化後的影像
   - 二值化後的影像
   - 邊緣偵測後的影像
   - 最終結果 (含輪廓標記)

4. **按任意鍵關閉所有視窗**

5. 處理結果會自動儲存為 `processed_result.jpg`

#### 修改處理參數

編輯 `main.py` 檔案底部的 `pipeline_config`：

```python
pipeline_config = [
    {
        "type": "blur",
        "params": {
            "type": "gaussian",
            "ksize": 9  # 模糊核心大小 (必須是奇數)
        }
    },
    {
        "type": "threshold",
        "params": {
            "threshold": 127  # 二值化閾值 (0-255)
        }
    },
    {
        "type": "edge",
        "params": {
            "method": "canny",
            "threshold1": 50,   # Canny 低閾值
            "threshold2": 150,  # Canny 高閾值
            "ksize": 3          # Sobel 核心大小
        }
    },
    {
        "type": "contour",
        "params": {
            "thresholdValue": 136,
            "retrievalMode": "TREE",  # 輪廓擷取模式
            "minArea": 550,           # 最小面積過濾
            "showBoundingBox": False, # 是否顯示邊界框
            "showCentroid": True,     # 是否顯示中心點
            "showLabel": True         # 是否顯示標籤
        }
    }
]
```

#### 更換處理影像

修改 `main.py` 底部的這行：

```python
target_image = "Image_20251210104315649.bmp"  # 改成你的影像檔名
```

---

### 方式二：圖形介面版本 (GUI.py)

#### 執行步驟

1. 開啟終端機，進入 DAY1 資料夾：
   ```bash
   cd DAY1
   ```

2. 執行程式：
   ```bash
   python GUI.py
   ```

3. 介面操作：

   **載入影像**
   - 點擊左上角的 **「Load Image」** 按鈕
   - 選擇要處理的影像檔案 (支援 .bmp, .jpg, .png, .tif)

   **執行處理**
   - 點擊 **「Run Pipeline」** 按鈕
   - 程式會依序執行所有處理步驟
   - 每個步驟的結果會顯示在不同的分頁 (Tab)

   **查看結果**
   - 點擊上方的分頁標籤切換不同步驟的結果
   - 右側面板顯示偵測到的輪廓資訊

   **校正功能 (Calibration)**
   - 在右側 Contour Data 表格中選擇一個已知尺寸的物件
   - 在下方 Calibration 區域輸入實際尺寸 (mm)
   - 點擊 **「Calibrate & Update」**
   - 所有物件的真實尺寸會自動計算並更新

---

## 處理管線說明

### 1. 模糊化 (Blur)

**用途**：降低影像雜訊，使後續處理更穩定

**參數**：
- `ksize`：核心大小，數值越大模糊程度越高 (必須是奇數)

### 2. 二值化 (Threshold)

**用途**：將灰階影像轉換為黑白二值影像

**參數**：
- `threshold`：閾值 (0-255)，低於此值變黑，高於變白

### 3. 邊緣偵測 (Edge Detection - Canny)

**用途**：偵測影像中的邊緣

**參數**：
- `threshold1`：低閾值，用於邊緣連接
- `threshold2`：高閾值，用於強邊緣偵測
- `ksize`：Sobel 運算子的核心大小

### 4. 霍夫圓檢測 (Hough Circle) - 僅 GUI 版本

**用途**：偵測影像中的圓形物體

**參數**：
- `dp`：累加器解析度比例
- `minDist`：偵測到的圓心之間最小距離
- `param1`：Canny 邊緣偵測的高閾值
- `param2`：圓心偵測的累加器閾值
- `minRadius` / `maxRadius`：最小/最大半徑

### 5. 輪廓檢測 (Contour Detection)

**用途**：找出影像中的物體輪廓並標記

**參數**：
- `retrievalMode`：輪廓擷取模式
  - `EXTERNAL`：只取最外層輪廓
  - `LIST`：取所有輪廓，不建立階層
  - `TREE`：取所有輪廓，建立完整階層
- `minArea`：最小面積過濾，過濾掉太小的輪廓
- `showBoundingBox`：是否繪製邊界框
- `showCentroid`：是否繪製中心點
- `showLabel`：是否繪製標籤 (ID 和面積)

---

## 常見問題

### Q: 執行時出現 "ModuleNotFoundError: No module named 'cv2'"

**A**: 請確認已安裝 opencv-python：
```bash
pip install opencv-python
```

### Q: GUI 版本無法啟動，出現 Pillow 相關錯誤

**A**: 請安裝 Pillow：
```bash
pip install Pillow
```

### Q: 偵測不到物體 / 偵測到太多雜訊

**A**: 嘗試調整以下參數：
- 增加 `minArea` 過濾小雜點
- 調整 `threshold` 二值化閾值
- 調整 Canny 的 `threshold1` 和 `threshold2`
- 增加 `ksize` 模糊程度

### Q: 如何處理自己的影像？

**A**:
- **命令列版本**：修改 `main.py` 中的 `target_image` 變數
- **GUI 版本**：直接點擊「Load Image」按鈕選擇檔案

---

## 練習題

1. 試著調整 `minArea` 參數，觀察輪廓數量的變化
2. 嘗試不同的 `threshold` 值，觀察二值化結果
3. 使用 GUI 版本的校正功能，計算物體的實際尺寸
4. 嘗試只保留圓形物體 (圓度 Circularity > 0.8)

---

## 下一步

完成 DAY1 的學習後，你將具備：
- 基本的影像處理管線概念
- OpenCV 的基礎操作能力
- 物體偵測與標記的實作經驗

繼續學習 DAY2 的進階內容！
