import os
import random
import shutil
import sys

def split_dataset(output_dir="./output", train_ratio=0.85, seed=42):
    gt_file = os.path.join(output_dir, "gt.txt")
    images_dir = os.path.join(output_dir, "images")

    if not os.path.exists(gt_file) or not os.path.exists(images_dir):
        print(f"Error: Could not find '{gt_file}' or '{images_dir}'. Please make sure annotations are done.")
        return

    # Read ground truth file
    entries = []
    with open(gt_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    entries.append((parts[0], parts[1]))

    if not entries:
        print("No valid annotations found in gt.txt.")
        return

    # Deterministic shuffle
    random.seed(seed)
    random.shuffle(entries)

    total = len(entries)
    train_count = int(total * train_ratio)
    train_entries = entries[:train_count]
    valid_entries = entries[train_count:]

    # Directories
    train_dir = "./train_data"
    valid_dir = "./valid_data"

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(valid_dir, exist_ok=True)

    # Write train_data
    train_gt = os.path.join(train_dir, "gt.txt")
    with open(train_gt, "w", encoding="utf-8") as f:
        for img_name, text in train_entries:
            f.write(f"{img_name}\t{text}\n")
            src_img = os.path.join(images_dir, img_name)
            if os.path.exists(src_img):
                shutil.copy2(src_img, os.path.join(train_dir, img_name))

    # Write valid_data
    valid_gt = os.path.join(valid_dir, "gt.txt")
    with open(valid_gt, "w", encoding="utf-8") as f:
        for img_name, text in valid_entries:
            f.write(f"{img_name}\t{text}\n")
            src_img = os.path.join(images_dir, img_name)
            if os.path.exists(src_img):
                shutil.copy2(src_img, os.path.join(valid_dir, img_name))

    print("=" * 50)
    print("Dataset successfully split!")
    print(f"Total Annotated Images : {total}")
    print(f"Train Set (85%)       : {len(train_entries)} images -> saved in '{train_dir}'")
    print(f"Validation Set (15%)  : {len(valid_entries)} images -> saved in '{valid_dir}'")
    print("=" * 50)

if __name__ == "__main__":
    split_dataset()
