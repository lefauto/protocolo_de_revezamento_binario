# Protocolo de Revezamento Binário

Atividade da disciplina **Computação Distribuída**: servidor de mensagens assíncrono em TCP com protocolo binário e tratamento de fragmentação.

## Objetivo

- Implementar um servidor de mensagens assíncrono com **TCP** e **asyncio**.
- Usar **serialização binária** (sem envio de strings puras) e tratar **fragmentação** da rede (leitura exata do cabeçalho e do payload).

## Cenário

O servidor permite que **Cliente A** deixe uma mensagem para **Cliente B**. A mensagem fica armazenada em memória e só é entregue quando o destinatário (Cliente B) solicitar com a operação RECUPERAR.

## Protocolo de aplicação

Cada mensagem segue um cabeçalho binário fixo:

| Campo         | Tamanho  | Descrição |
|---------------|----------|-----------|
| Payload Size  | 2 bytes  | Inteiro em **big-endian** indicando o tamanho dos dados que seguem |
| Operação      | 1 byte   | `0x00` = ENVIAR (gravar mensagem), `0x01` = RECUPERAR (ler mensagem) |
| Dados         | Variável | Conteúdo em UTF-8; presente apenas quando a operação é ENVIAR |

Formato no código: `struct.pack("!HB", len(payload), op)` — `!` = big-endian, `H` = 2 bytes, `B` = 1 byte.

## Estrutura do projeto

```
atividade_1/
├── server.py   # Servidor asyncio (múltiplos clientes, lock para caixa única)
├── client.py   # Cliente síncrono (ENVIAR ou RECUPERAR)
└── README.md
```

## Como executar

**Requisitos:** Python 3.10+ (apenas biblioteca padrão: `asyncio`, `struct`, `socket`).

### Local

1. **Inicie o servidor** (escuta em `0.0.0.0:8888`):

   ```bash
   python server.py
   ```

2. **Cliente A – enviar mensagem:**

   ```bash
   python client.py
   ```
   - Digite `e` (ENVIAR) e a mensagem.

3. **Cliente B – recuperar mensagem:**

   ```bash
   python client.py
   ```
   - Digite `r` (RECUPERAR). A mensagem deixada pelo Cliente A será exibida.

Para conectar a outro host, edite `host` e `port` em `client.py` (ex.: IP do professor ou colega para testes de conectividade).

### Online

**...**

## Fragmentação (TCP)

O servidor não assume que um único `read` traz a mensagem inteira. Ele:

1. Lê **exatamente 3 bytes** (cabeçalho) com `reader.readexactly(HEADER_SIZE)`.
2. Obtém o tamanho do payload e entra em um loop (ou novo `readexactly`) até receber **exatamente** esse número de bytes.

Assim o protocolo funciona mesmo quando o TCP entrega os dados em vários fragmentos.
