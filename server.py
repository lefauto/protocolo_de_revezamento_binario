import asyncio
import struct

HEADER_FORMAT = "!HB"  # H = 2 bytes (payload size), B = 1 byte (op)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

OP_SEND = 0x00
OP_GET = 0x01

# "Caixa de mensagens" compartilhada entre todos os clientes
stored_message: bytes | None = None
lock = asyncio.Lock()


async def read_exactly(reader: asyncio.StreamReader, n: int) -> bytes | None:
    try:
        data = await reader.readexactly(n)
        return data
    except asyncio.IncompleteReadError:
        return None


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    global stored_message
    peer = writer.get_extra_info("peername")
    print(f"Novo cliente conectado: {peer}")

    try:
        while True:
            # ler exatamente o cabeçalho (3 bytes)
            header = await read_exactly(reader, HEADER_SIZE)
            if header is None:
                print(f"Conexão encerrada por {peer}")
                break

            payload_size, op = struct.unpack(HEADER_FORMAT, header)

            # ler exatamente o payload prometido
            data = b""
            if payload_size > 0:
                data = await read_exactly(reader, payload_size)
                if data is None:
                    print(f"Conexão encerrada (no meio da mensagem) por {peer}")
                    break

            if op == OP_SEND:
                mensagem = data.decode("utf-8", errors="replace")
                print(f"[{peer}] ENVIAR: {mensagem!r}")

                async with lock: # lockando a variável
                    stored_message = data  # guardamos em bytes UTF‑8

                # ajuda ao cliente a saber que a mensagem foi enviada
                ack_header = struct.pack(HEADER_FORMAT, 0, OP_SEND)
                writer.write(ack_header)
                await writer.drain()

            elif op == OP_GET:
                async with lock:
                    if stored_message is None:
                        resp_payload = b""
                        payload_len = 0
                    else:
                        resp_payload = stored_message
                        payload_len = len(resp_payload)
                        stored_message = None  # limpa a caixa após entrega

                print(f"[{peer}] RECUPERAR -> {payload_len} bytes")

                resp_header = struct.pack(HEADER_FORMAT, payload_len, OP_GET)
                writer.write(resp_header + resp_payload)
                await writer.drain()

            else:
                print(f"Operação desconhecida {op} de {peer}, fechando conexão.")
                break

    except Exception as exc:
        print(f"Erro ao lidar com {peer}: {exc!r}")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Conexão fechada: {peer}")


async def main(host: str = "0.0.0.0", port: int = 8888) -> None:
    server = await asyncio.start_server(handle_client, host, port) # inicia o servidor e retorna um objeto Server
    addr = ", ".join(str(sock.getsockname()) for sock in server.sockets) 
    print(f"Servidor ouvindo em {addr}")

    async with server:
        await server.serve_forever() # serve eternamente, aguardando conexões e lidando com elas


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor encerrado manualmente.")