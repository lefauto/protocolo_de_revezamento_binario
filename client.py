import socket
import struct

HEADER_FORMAT = "!HB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

OP_SEND = 0x00
OP_GET = 0x01


def send_packet(sock: socket.socket, op: int, data: bytes) -> None:
    header = struct.pack(HEADER_FORMAT, len(data), op)
    packet = header + data
    sock.sendall(packet)


def recv_exact(sock: socket.socket, n: int) -> bytes | None:
    chunks = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            return None
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def recv_response(sock: socket.socket):
    header = recv_exact(sock, HEADER_SIZE)
    if header is None:
        print("Conexão fechada antes de receber cabeçalho.")
        return

    payload_size, op = struct.unpack(HEADER_FORMAT, header)
    data = b""
    if payload_size > 0:
        data = recv_exact(sock, payload_size)
        if data is None:
            print("Conexão fechada antes de receber payload.")
            return

    if payload_size > 0:
        print("Mensagem recebida:", data.decode("utf-8", errors="replace"))
    elif op == OP_SEND:
        print("Mensagem enviada com sucesso!")
    else:
        print("Nenhuma mensagem disponível.")


def main():
    host = "127.0.0.1"  # altere para IP do servidor
    port = 8888

    with socket.create_connection((host, port)) as sock:
        print("Conectado ao servidor.")

        escolha = input("Digite 'e' para ENVIAR ou 'r' para RECUPERAR: ").strip().lower()

        if escolha == "e":
            texto = input("Mensagem para enviar: ")
            send_packet(sock, OP_SEND, texto.encode("utf-8"))
            # lê ACK opcional
            recv_response(sock)

        elif escolha == "r":
            send_packet(sock, OP_GET, b"")
            recv_response(sock)
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()