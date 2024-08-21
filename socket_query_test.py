import socket
import struct
import csv
from io import StringIO

IP = "localhost"
PORT = 8080

BUFFER_SIZE = 4096 # bytes that are read each time from DB server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

query = """// This query is asking for the age and name of people
// that knows John having between 60 and 70 years old,
// ordered by their age (ascending) and name (descending).
MATCH (?p :pais)<-(?x :pieza )->(?c :componente)
RETURN ?p.name, ?c.peso_grs, ?x.contexto_historico
LIMIT 1000"""


"""
send_query: sends a query to milleniumDB server and returns the query result as a string
"""
def send_query(host: str, port: int, query: str) -> str:
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server
        s.connect((host, port))

        # Encode the message to bytes
        query_bytes = query.encode('utf-8')

        # Pack the length of the message (4 bytes, little ender because ???)
        query_length = struct.pack('<I', len(query_bytes))

        # Send the length followed by the message
        s.sendall(query_length)
        s.sendall(query_bytes)
        print(f"{query_length=}")

        # recive mensaje de servidor
        finished_byte = 0
        result = bytearray()
        while (finished_byte < 128):
            msg = s.recv(BUFFER_SIZE)
            finished_byte = msg[0]
            response_length = int.from_bytes(msg[1:3], 'little')
            result+=(msg[3:response_length])
            print(f"{finished_byte=}, {response_length=}")
        

        return result.decode()

def parse_result(query_result: str):

    f = StringIO(query_result)
    reader = csv.reader(f, delimiter=',')
    return reader

result = send_query(IP, PORT, query)
for x in parse_result(result):
    print(x)