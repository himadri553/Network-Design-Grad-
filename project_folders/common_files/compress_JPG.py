from PIL import Image
import os

def compress_JPG(pic_path, target_kb=150, quality=85):
    img = Image.open(pic_path).convert("RGB")
    base = os.path.splitext(pic_path)[0]
    output_path = base + "_compressed.jpg"

    # Binary search for the right quality level to hit target size
    lo, hi = 5, 95
    while lo < hi - 1:
        mid = (lo + hi) // 2
        img.save(output_path, format="JPEG", quality=mid)
        size_kb = os.path.getsize(output_path) / 1024
        if size_kb > target_kb:
            hi = mid
        else:
            lo = mid

    img.save(output_path, format="JPEG", quality=lo)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Saved: {output_path} ({size_kb:.1f} KB) at quality={lo}")

if __name__ == "__main__":
    pic_path = input("Paste full pic path to convert here: ")
    compress_JPG(pic_path)

