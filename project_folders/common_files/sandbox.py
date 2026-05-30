"""
    Trying to test out how to reconstruct an image (working!)

"""
import os
pic_path = os.path.join(os.path.dirname(__file__), 'bos_skyline.bmp')
output_pic_path = os.path.join(os.path.dirname(__file__), 'output_pic.bmp')
packet_size = 1024
all_chunks = []
full_pic = []

def main():
    # Break into chunks
    with open(pic_path, "rb") as f:
        data = f.read()
    
    total_bytes = len(data)
    num_packets = (total_bytes + packet_size - 1) // packet_size

    for i in range(num_packets):
        chunk = data[i * packet_size : (i + 1) * packet_size]
        all_chunks.append(chunk)

    # Append to a full_pic
    for i in range(len(all_chunks)):
        full_pic.append(all_chunks[i])

    # Reconstruct an image based on full_pic
    full_data = b''.join(full_pic)
    with open (output_pic_path, "wb") as f:
        f.write(full_data)

if __name__ == "__main__":
    main()

