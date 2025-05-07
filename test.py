import socket, struct

MATLAB_IP = '127.0.0.1'
MATLAB_PORT_TAKEOFF = 8090

takeoff_signal = 1

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(struct.pack('>f', takeoff_signal), (MATLAB_IP, MATLAB_PORT_TAKEOFF))
print("done!")