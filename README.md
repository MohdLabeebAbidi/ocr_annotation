# 🚗 License Plate & OCR Image Annotation Tool

An easy-to-use Python tool for manually annotating text in cropped license plate images. It displays images in a window and lets you type the corresponding text in the terminal. Once you finish annotating, it automatically prepares and splits your dataset for OCR machine learning model training!

---

## 📌 Features

- 🖼️ **Interactive Window**: Displays cropped images one-by-one in a clear preview window.
- ⌨️ **Terminal Prompt**: Type the license plate number or text directly into the terminal.
- ⏭️ **Easy Controls**:
  - Type text & press **Enter** to save the label.
  - Type **`skip`** (or press Enter on blank) to skip an image.
  - Type **`quit`** to stop annotating and start dataset preparation.
- 🔀 **Automated Dataset Splitting**:
  - Automatically shuffles your dataset.
  - Splits entries into an **85% Training set** (`./train_data`) and a **15% Validation set** (`./valid_data`).
  - Creates formatted `gt.txt` ground truth files inside each dataset directory.
- 💾 **LMDB Dataset Generator**: Automatically invokes LMDB creation scripts if the benchmark repository is detected.

---

## 🚀 Quick Start Guide (For Beginners)

### Step 1: Install Requirements
Open your terminal inside the project directory and run:

```bash
pip install -r requirements.txt
```

---

### Step 2: Place Your Images
Create a folder named `input_data` (or `cropped_plates`) in the project directory and place your `.jpg`, `.jpeg`, or `.png` cropped license plate images inside it.

---

### Step 3: Run the Script
Execute the main script by running:

```bash
# On Windows:
python main.py

# On Linux / macOS:
python3 main.py
```

---

## 📖 How to Annotate

When you run `main.py`, an image window named **"License Plate"** will appear alongside terminal prompts:

1. Look at the image displayed in the window.
2. Type the license plate number in the terminal (e.g. `UP15EC0427`) and press **Enter**.
3. To skip an unclear image, type `skip` and press **Enter**.
4. To stop at any time, type `quit` and press **Enter**.

---

## 📂 Output Structure

After running, the following files and folders will be created automatically:

```text
ocr_annotation/
│
├── main.py                     # Main annotation script
├── requirements.txt            # Python dependencies
├── gt.txt                      # Full ground truth file (filename <tab> text)
│
├── train_data/                 # 85% Training split (Images + gt.txt)
├── valid_data/                 # 15% Validation split (Images + gt.txt)
└── lmdb_dataset/               # (Optional) Generated LMDB binary datasets
```

---

## 💡 System Requirements
- Python 3.7 or higher
- Linux / macOS / Windows
