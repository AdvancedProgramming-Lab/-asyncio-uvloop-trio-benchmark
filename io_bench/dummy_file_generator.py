import os

def create_files(n=500, size_kb=50, directory="test_files"):
    os.makedirs(directory, exist_ok=True)
    data = "A" * (size_kb * 1024)
    for i in range(n):
        with open(os.path.join(directory, f"file_{i}.txt"), "w") as f:
            f.write(data)

if __name__ == "__main__":
    create_files()
    print("Dummy files have been generated.")
