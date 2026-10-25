import openwakeword

def main():
    print(" [*] Đang tải các mô hình âm học ONNX (openWakeWord)...")
    openwakeword.utils.download_models()
    print(" [✓] Tải mô hình thành công!")

if __name__ == "__main__":
    main()
