from PIL import Image

def main():
    img = Image.open("bos_skyline.JPG")
    img.save("bos_skyline.bmp")  

if __name__ == "__main__":
    main()