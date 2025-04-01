import serial
import struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

# 센서와 연결된 COM 포트 및 보드레이트
ser = serial.Serial(
    port='COM8',           # 사용 중인 포트
    baudrate=460800,       # 센서에 맞춘 속도
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

data_lock = threading.Lock()
distance_data = []

def read_serial():
    global distance_data
    buffer = b''

    while True:
        if ser.in_waiting:
            buffer += ser.read(ser.in_waiting)

            # STX: 0x02, ETX: 0x03 기준으로 메시지 분리
            while b'\x02' in buffer and b'\x03' in buffer:
                start = buffer.find(b'\x02')
                end = buffer.find(b'\x03', start)
                if end == -1:
                    break
                packet = buffer[start+1:end]
                buffer = buffer[end+1:]

                # MDI 메시지인지 확인 (Message ID == 0x80)
                if len(packet) >= 3 and packet[0] == 0x80:
                    # 거리 데이터 시작 위치는 문서에 따라 다름
                    # 여기서는 샘플로 2바이트씩 거리 데이터라고 가정
                    distances = []
                    try:
                        for i in range(1, len(packet), 2):  # 1번 인덱스부터 2바이트씩
                            if i + 1 < len(packet):
                                dist = struct.unpack('<H', packet[i:i+2])[0]
                                distances.append(dist)
                    except:
                        continue
                    
                    with data_lock:
                        distance_data = distances

def animate(i):
    with data_lock:
        if not distance_data:
            return
        plt.cla()
        angles = list(range(len(distance_data)))
        plt.plot(angles, distance_data)
        plt.ylim(0, 5000)  # 단위는 mm, 실제 거리 범위에 따라 조정
        plt.title("LZR-U92x 실시간 거리 시각화")
        plt.xlabel("Angle Index")
        plt.ylabel("Distance (mm)")

# 시리얼 수신 쓰레드 시작
threading.Thread(target=read_serial, daemon=True).start()

# 그래프 시각화 설정
fig = plt.figure()
ani = animation.FuncAnimation(fig, animate, interval=100, blit=True)
plt.show()
