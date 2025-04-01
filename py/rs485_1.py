import serial

def receive_rs485(port='COM8', baudrate=460800, timeout=1):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )
        print(f"[INFO] 포트 {port} 에서 수신 대기 중... (속도: {baudrate}bps)")

        while True:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                print(f"[RECV] {data.hex()}  // 문자열: {data.decode(errors='ignore')}")
    except KeyboardInterrupt:
        print("\n[EXIT] 사용자 종료")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("[INFO] 포트 닫힘")

# 실행
if __name__ == "__main__":
    receive_rs485()