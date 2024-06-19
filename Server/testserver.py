import socket, struct

MATLAB_IP = '127.0.0.1'
MATLAB_PORT_LAT_DEC = 8081
MATLAB_PORT_LAT_MIN = 8082
MATLAB_PORT_LONG_DEC = 8083
MATLAB_PORT_LONG_MIN = 8084

BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

 # parse the latitude and longitude string into degree and minute
latitude = "33-44.454333N"
lat_deg = int(latitude.split("-")[0]) * (1 if latitude.split("-")[1][-1] == "N" else -1)
lat_min = float(latitude.split("-")[1][:-1])

longitude = "084-30.752833W"
long_deg = int(longitude.split("-")[0]) * (1 if longitude.split("-")[1][-1] == "E" else -1)
long_min = float(longitude.split("-")[1][:-1])

# send the location
s.sendto(lat_deg.to_bytes(2, 'big', signed=True), (MATLAB_IP, MATLAB_PORT_LAT_DEC))
s.sendto(struct.pack('>f', lat_min), (MATLAB_IP, MATLAB_PORT_LAT_MIN))
s.sendto(long_deg.to_bytes(2, 'big', signed=True), (MATLAB_IP, MATLAB_PORT_LONG_DEC))
s.sendto(struct.pack('>f', long_min), (MATLAB_IP, MATLAB_PORT_LONG_MIN))
