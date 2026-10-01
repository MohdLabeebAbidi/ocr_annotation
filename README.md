# 🚗 License Plate & OCR Image Annotation Tool

An easy-to-use Python tool for manually annotating text in cropped license plate images. It displays images in an OpenCV GUI window and lets you type the corresponding text in the terminal.

It automatically removes all spaces and converts labels to **UPPERCASE** before saving to `gt.txt`. Once finished, you can run `split_dataset.py` to partition your dataset into **85% Training** and **15% Validation** splits!

---

## 📌 Features

- 🖼️ **Interactive Preview**: Displays cropped images one-by-one in an OpenCV window.
- ⌨️ **Terminal Input**: Type license plate text directly in the terminal.
- 🔤 **Automatic Text Normalization**:
  - Automatically converts all letters to **UPPERCASE** (e.g. `up13ay6827` → `UP13AY6827`).
  - Automatically strips all internal/extra **whitespace** (e.g. `up 13   er 3213` → `UP13ER3213`).
- 📁 **Flexible Input Folder**: Pass input directory via CLI argument (`python main.py input`) or interactive prompt.
- ⏭️ **Easy Controls**:
  - Type text & press **Enter** to save the label.
  - Type **`skip`** to skip an unclear image.
  - Type **`quit`** to safely save progress and exit.
- 🔀 **Automated Dataset Splitting**:
  - Run `python split_dataset.py` to shuffle and split your dataset into **85% Train** (`./train_data`) and **15% Validation** (`./valid_data`) with formatted `gt.txt` files.

---

## 🛠️ Setup & Virtual Environment (vEnv)

Follow the setup instructions below according to your Operating System:

### 🐧 Linux / 🍎 macOS

1. **Open terminal inside the project folder** and create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

### 🪟 Windows

1. **Open Command Prompt (CMD) or PowerShell inside the project folder** and create a virtual environment:
   ```cmd
   python -m venv venv
   ```

2. **Activate the virtual environment**:

   - **Command Prompt (CMD):**
     ```cmd
     venv\Scripts\activate
     ```

   - **PowerShell:**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     *(Note: If PowerShell throws an ExecutionPolicy error, run `Set-ExecutionPolicy Unrestricted -Scope Process` first)*

3. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

---

## 🚀 How to Run & Annotate

### Step 1: Run the Annotation Script

Aap input folder name directly command me de sakte hain:

```bash
python main.py input
```

Ya phir simple run karein aur prompt me folder path enter karein:

```bash
python main.py
```

### Step 2: Annotate Images

1. Look at the image displayed in the **"License Plate"** window.
2. Type the plate text in the terminal and press **Enter** (e.g., `up 15 ec 0427` will automatically save as `UP15EC0427`).
3. Type **`skip`** to skip an image.
4. Type **`quit`** to stop at any time.

---

## 🔀 Step 3: Split Dataset (Train / Valid)

When annotation is complete, split your data into 85% Training and 15% Validation sets by running:

```bash
python split_dataset.py
```

---

## 📂 Project & Output Structure

```text
ocr_annotation/
│
├── main.py                     # Main annotation script
├── split_dataset.py            # Dataset 85/15 train-validation splitter
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── input/                      # Input cropped images folder
│
├── output/                     # Saved annotations
│   ├── images/                 # Processed annotated images
│   ├── gt.txt                  # Full ground truth file (filename <tab> TEXT)
│   └── progress.json           # Session progress tracker
│
├── train_data/                 # 85% Training split (Images + gt.txt)
└── valid_data/                 # 15% Validation split (Images + gt.txt)
```

---

## 💡 System Requirements
- Python 3.7 or higher
- OpenCV (`opencv-python`)
