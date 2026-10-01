import cv2
import json
import os
import shutil
import sys

if sys.platform == "win32":
    import msvcrt
else:
    import select


# =====================================================================
# Helper Functions
# =====================================================================

def prompt_input_with_gui(prompt):
    """
    Get terminal input while keeping the OpenCV GUI event loop active on the main thread.
    Supports Windows (msvcrt), Linux, and macOS (select).
    """
    print(prompt, end="", flush=True)
    if sys.platform == "win32":
        buf = []
        while True:
            cv2.waitKey(30)
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\r", "\n"):
                    print()
                    return "".join(buf).strip()
                elif ch in ("\000", "\xe0"):
                    # Handle special key prefixes (e.g. arrow keys)
                    msvcrt.getwch()
                elif ch == "\b":
                    if buf:
                        buf.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                else:
                    buf.append(ch)
                    sys.stdout.write(ch)
                    sys.stdout.flush()
    else:
        while True:
            # Keep OpenCV GUI event loop pumping continuously on the main thread
            cv2.waitKey(30)
            
            # Non-blocking check for terminal input
            rlist, _, _ = select.select([sys.stdin], [], [], 0.03)
            if rlist:
                return sys.stdin.readline().strip()


def save_progress(progress_file, progress_data):
    """
    Requirement 2 & 5: Save progress data atomically to disk and flush buffers
    so progress persists across sessions and survives unexpected interruptions.
    """
    temp_file = progress_file + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_file, progress_file)


# =====================================================================
# Main Annotation Pipeline
# =====================================================================

def main():
    # 1. Determine Input Directory (CLI argument or interactive prompt)
    if len(sys.argv) > 1:
        image_folder = sys.argv[1]
    else:
        default_folder = "./input" if os.path.exists("./input") else "./input_data"
        user_input = input(f"Enter cropped images directory path [Default: {default_folder}]: ").strip()
        image_folder = user_input if user_input else default_folder

    while not os.path.exists(image_folder) or not os.path.isdir(image_folder):
        print(f"Error: Image directory '{image_folder}' does not exist or is not a directory.")
        user_input = input("Please enter a valid cropped images directory path (or type 'quit' to exit): ").strip()
        if user_input.lower() == 'quit':
            return
        image_folder = user_input if user_input else default_folder

    # Requirement 8: Store All Annotated Data in a Single Output Folder
    output_dir = "./output"
    output_images_dir = os.path.join(output_dir, "images")
    output_gt_file = os.path.join(output_dir, "gt.txt")
    progress_file = os.path.join(output_dir, "progress.json")

    os.makedirs(output_images_dir, exist_ok=True)

    # Requirement 3, 4, 5: Resume Capability & Progress Persistence
    # Load previously saved annotations and skipped images
    annotated = {}  # filename -> label
    skipped = set()  # set of filenames

    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                pdata = json.load(f)
                annotated = pdata.get("annotated", {})
                skipped = set(pdata.get("skipped", []))
        except Exception as e:
            print(f"Warning: Failed to load '{progress_file}': {e}. Recovering state from ground truth file...")

    # Sync with output/gt.txt if present
    if os.path.exists(output_gt_file):
        with open(output_gt_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("\t", 1)
                    if len(parts) == 2:
                        annotated[parts[0]] = parts[1]

    # Sync with legacy root gt.txt if present and output/gt.txt wasn't created yet
    root_gt_file = "gt.txt"
    if not os.path.exists(output_gt_file) and os.path.exists(root_gt_file):
        with open(root_gt_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("\t", 1)
                    if len(parts) == 2:
                        annotated[parts[0]] = parts[1]
                        # Copy legacy entries into output/gt.txt
                        with open(output_gt_file, "a", encoding="utf-8") as f_out:
                            f_out.write(f"{parts[0]}\t{parts[1]}\n")

    # Persist normalized initial progress state
    progress_data = {
        "annotated": annotated,
        "skipped": list(skipped)
    }
    save_progress(progress_file, progress_data)

    # Requirement 6: Performance - Sort image files deterministically for indexing
    image_files = sorted([
        f for f in os.listdir(image_folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])
    total_images = len(image_files)

    if total_images == 0:
        print(f"No valid images found in '{image_folder}'.")
        return

    # Find the index of the first unannotated & unskipped image
    already_processed = len(annotated) + len(skipped)
    first_unannotated_idx = None
    for idx, fname in enumerate(image_files, start=1):
        if fname not in annotated and fname not in skipped:
            first_unannotated_idx = idx
            break

    print(f"Starting annotation from folder: '{image_folder}'")
    print(f"Saving all outputs to directory: '{output_dir}'")
    print("Type the plate number and press Enter.")
    print("Type 'skip' to skip an image, or 'quit' to stop.")

    # Display resume information if restarting a session
    if already_processed > 0:
        remaining_initial = total_images - already_processed
        print("\n" + "=" * 50)
        print(f"Dataset size     : {total_images} images")
        print(f"Already annotated: {len(annotated)}")
        print(f"Skipped          : {len(skipped)}")
        print(f"Remaining        : {remaining_initial}")
        if first_unannotated_idx is not None:
            print(f"Resuming from image {first_unannotated_idx}...")
        else:
            print("All images have already been processed!")
        print("=" * 50 + "\n")

    if first_unannotated_idx is None:
        print("No remaining images to annotate. All work is complete!")
        return

    cv2.namedWindow("License Plate", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("License Plate", 500, 250)

    # Open gt.txt in append mode for incremental writing
    gt_file_handle = open(output_gt_file, "a", encoding="utf-8")

    try:
        for curr_idx, filename in enumerate(image_files, start=1):
            # Requirement 3 & 4: Automatically skip already processed images
            if filename in annotated or filename in skipped:
                continue

            img_path = os.path.join(image_folder, filename)
            img = cv2.imread(img_path)

            if img is None:
                print(f"Warning: Could not read image '{filename}'. Marking as skipped.")
                skipped.add(filename)
                progress_data["skipped"] = list(skipped)
                save_progress(progress_file, progress_data)
                continue

            # Requirement 1: Real-Time Progress Tracking Header
            remaining_count = total_images - (len(annotated) + len(skipped))
            progress_pct = (curr_idx / total_images) * 100

            print("-" * 50)
            print(f"Current Image : {curr_idx} / {total_images}")
            print(f"Filename      : {filename}")
            print(f"Annotated     : {len(annotated)}")
            print(f"Skipped       : {len(skipped)}")
            print(f"Remaining     : {remaining_count}")
            print(f"Progress      : {progress_pct:.2f}%")
            print("-" * 50)

            # Display the image preview
            cv2.imshow("License Plate", img)

            # Requirement 7: Preserve input prompt flow & keyboard controls
            raw_text = prompt_input_with_gui(f"Text for {filename}: ")

            if raw_text.strip().lower() == 'quit':
                print("\nQuit signal received. Progress saved. Exiting session...")
                break
            elif raw_text.strip().lower() == 'skip':
                # Requirement 4: Record skipped image permanently
                skipped.add(filename)
                progress_data["skipped"] = list(skipped)
                save_progress(progress_file, progress_data)
                print(f"Skipped image: {filename}\n")
            elif raw_text.strip() != "":
                # Process text: Remove all spaces and convert to UPPERCASE
                text = "".join(raw_text.split()).upper()

                # Requirement 2 & 8: Immediate auto-save & copy to single output folder
                gt_file_handle.write(f"{filename}\t{text}\n")
                gt_file_handle.flush()
                os.fsync(gt_file_handle.fileno())

                # Copy image into output/images directory
                dst_img_path = os.path.join(output_images_dir, filename)
                try:
                    shutil.copy2(img_path, dst_img_path)
                except Exception as e:
                    print(f"Warning: Failed to copy {filename} to {output_images_dir}: {e}")

                # Update memory state and progress file
                annotated[filename] = text
                progress_data["annotated"] = annotated
                save_progress(progress_file, progress_data)
                print(f"Saved annotation for {filename}: '{text}'\n")

    finally:
        gt_file_handle.close()
        cv2.destroyAllWindows()

    final_processed = len(annotated) + len(skipped)
    print(f"\nAnnotation session ended. Total completed work: {final_processed} / {total_images} images.")
    print(f"Annotated images and ground truth file are saved in: '{output_dir}'")

if __name__ == "__main__":
    main()
