# Firmware das consolas físicas (Raspberry Pi Pico W)

Firmware MicroPython das duas consolas físicas da MESADELUX. Cada consola
liga-se à app por WiFi (OSC/UDP) ou por USB através do bridge (ver a pasta
[`bridge/`](../bridge)).

## As duas consolas

- **`pico_consola1_v5/`** — consola principal: encoders, display OLED
  (SSD1306), teclas de memórias e GO.
  - `main.py` — programa principal
  - `rotary.py`, `rotary_irq_rp2.py` — leitura dos encoders
  - `ssd1306.py`, `writer.py` — display OLED
- **`pico_consola2_v5/`** — consola auxiliar (submasters/execução).
  - `main.py` — programa principal
  - `rotary.py`, `rotary_irq_rp2.py` — leitura dos encoders

## Instalação (resumo)

1. Instalar o MicroPython no Pico W (ficheiro `.uf2` de
   <https://micropython.org/download/RPI_PICO_W/>): ligar o Pico ao PC com
   o botão BOOTSEL carregado e copiar o `.uf2` para a drive que aparece.
2. Copiar **todos os ficheiros `.py`** da pasta da consola para a flash do
   Pico (com o Thonny, por exemplo: Ver → Ficheiros).
3. Copiar `secrets.example.py` para `secrets.py` **no Pico** e preencher o
   SSID e a password da rede WiFi.
   - Em alternativa: criar um ficheiro `wifi.txt` na flash do Pico com duas
     linhas (linha 1 = SSID, linha 2 = password).
4. Reiniciar o Pico — o `main.py` arranca sozinho.

> **Nunca** publiques o teu `secrets.py` nem o `wifi.txt`: contêm a password
> da tua rede. Só o `secrets.example.py` (sem dados reais) é versionado.

## Iniciação à programação

TODO: instruções de iniciação ditadas pelo autor (como abrir o código no
Thonny, como experimentar alterações simples, por onde começar a ler o
`main.py`, etc.)

## Ligações de hardware

Ver [`hardware/ligacoes.md`](../hardware/ligacoes.md).

By Worm
