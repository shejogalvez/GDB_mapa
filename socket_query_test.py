import socket
import struct

IP = "localhost"
PORT = 8080

BUFFER_SIZE = 4096 # bytes that are read each time from DB server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

query = """// This query is asking for the age and name of people
// that knows John having between 60 and 70 years old,
// ordered by their age (ascending) and name (descending).
MATCH (?x :pieza)
RETURN ?x.contexto_historico, ?x.titulo_o_nombre_atribuido
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
        msg = bytes([0])
        result = bytearray()
        while (msg[0] == 0):
            msg = s.recv(BUFFER_SIZE)
            response_length = int.from_bytes(msg[1:3], 'little')
            result+=(msg[3:response_length+1])
            current_length += BUFFER_SIZE
            print(f"{msg[0]=}, {response_length=}")
        

        return result.decode()

def parse_result(query_result: str) -> list[dict]:

    result_list = query_result.split('\n')
    print(result_list)
    headers = result_list[0].split(',')
    data = []
    for row in result_list[1:]:
        data.append({
            pair[0]: pair[1] for pair in zip(headers, row.split(','))
        })
    print(len(data))
    return data

result = send_query(IP, PORT, query)
print(parse_result(result))