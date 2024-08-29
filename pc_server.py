import cv2
import socket
import struct
import pickle

# Setup socket to receive video stream
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '192.168.0.126'  # IP address of the server
port = 9999  # Port to listen on

server_socket.bind((host_ip, port))
server_socket.listen(5)
print(f"Server: Listening on {host_ip}:{port}")

client_socket, addr = server_socket.accept()
print(f"Connection from: {addr}")

data = b""
payload_size = struct.calcsize("!L")  # Use network byte order

try:
    while True:
        # Retrieve message size (4 bytes)
        while len(data) < payload_size:
            print("Server: Waiting to receive data...")
            packet = client_socket.recv(4096)  # 4KB buffer size
            if not packet:
                print("Server: No data received. Closing connection.")
                break
            data += packet

        if len(data) < payload_size:
            print("Server: Incomplete data received for message size. Exiting loop.")
            break

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("!L", packed_msg_size)[0]  # Unpack using network byte order
        print(f"Server: Expected message size: {msg_size}")

        # Retrieve the frame data based on the size
        while len(data) < msg_size:
            packet = client_socket.recv(4096)
            if not packet:
                print("Server: No more frame data received. Exiting loop.")
                break
            data += packet

        if len(data) < msg_size:
            print(f"Server: Incomplete frame data received. Needed: {msg_size}, Received: {len(data)}. Exiting loop.")
            break

        print('Server: Preparing to deserialize frame data.')
        frame_data = data[:msg_size]
        data = data[msg_size:]

        try:
            # Deserialize frame using pickle
            frame = pickle.loads(frame_data)
            print("Server: Frame data successfully deserialized.")
        except Exception as e:
            print(f"Server: Deserialization error: {e}")
            break

        # Display the frame
        cv2.imshow('Video Stream', frame)
        print("Server: Displaying frame.")

        # Press 'q' on the keyboard to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Server: Exiting on user command.")
            break

except KeyboardInterrupt:
    print("Server: Program interrupted by user.")

finally:
    client_socket.close()
    server_socket.close()
    cv2.destroyAllWindows()
    print("Server: Sockets closed, resources released.")
