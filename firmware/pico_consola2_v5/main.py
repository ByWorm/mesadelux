# =============================================================================
# Mesadeluz-OSC_CONSOLA — Consola 2 (firmware Pico W)  -  v5
# =============================================================================
# v5 vs v4:
#   - Esta consola SO ENVIA. Em USB, agora DRENA E DESCARTA o que chegar pelo
#     serie (REPL/stdin). Antes, se o bridge lhe escrevesse o feedback da
#     Consola 1 (config bidireccional), os bytes acumulavam no stdin e podiam
#     engasgar/parar a consola — interferindo no espectaculo. Recomendado:
#     no bridge v5 por a Consola 2 como IN ligado / OUT desligado.
#
# v4 vs v2 (estabilidade):
#   - WiFi falhada no boot JA NAO deixa a consola morta a piscar: tenta de
#     novo de 10 em 10 s ate conseguir (recupera quando o router voltar).
#   - Vigilancia da ligacao no loop: se o WiFi cair a meio do espectaculo,
#     o LED apaga e a consola reconecta sozinha (LED volta a fixo).
#   - Credenciais WiFi opcionais em wifi.txt (linha 1 = SSID, linha 2 = pass).
# =============================================================================
# Consola minima de PLAYBACK + FX. So tem 4 botoes + 1 encoder. Sem OLED.
# v5: a GRAVACAO foi REMOVIDA. O clique do encoder passa a alternar XF <-> FX.
#
# Hardware:
#   Botao 1 (esq):  GP16    -> VAI    (XF)  /  FX do slot 1 do grupo (FX)
#   Botao 2:        GP19    -> PAUSA  (XF)  /  FX do slot 2 do grupo (FX)
#   Botao 3:        GP22    -> RECUA  (XF)  /  FX do slot 3 do grupo (FX)
#   Botao 4 (dir):  GP28    -> SOLTAR (XF)  /  FX do slot 4 do grupo (FX)
#   Encoder:        A=GP6   B=GP7        SW=GP8
#
# Modos de operacao (clique do encoder alterna):
#   PLAYBACK / XF (default) - controlo de espectaculo (VAI, PAUSA, RECUA, SOLTAR)
#                             encoder gira: CW = >>> | CCW = <<< (snap de cue)
#   FX                      - pagina de efeitos. Sao 16 FX em 4 GRUPOS de 4.
#                             encoder gira: anda de 4 em 4 (muda de grupo 0..3).
#                             os 4 botoes (esq->dir) fazem TOGGLE aos 4 FX do
#                             grupo actual: FX (grupo*4 + 1..4).
#                             Envia '/fx/N/toggle' e '/fx/group G'; ao entrar/
#                             sair envia '/fx/mode 1|0' (a app mostra a pagina
#                             FX e DESTACA as 4 teclas do grupo seleccionado).
#
# Transporte (USB/WIFI), seleccionavel no splash inicial:
#   - SPLASH dura ~2 s ao ligar. Durante este tempo o LED pisca rapido.
#   - Se GP28 (4.º botao) estiver PREMIDO durante o splash, alterna
#     WIFI <-> USB, guarda em flash e reboot.
#   - Default = WIFI. A escolha persiste em transport.txt.
#
# Esta consola SO ENVIA OSC (nao recebe nada da app). Envia:
#   - em WIFI: pacotes UDP broadcast/IP para a app na porta APP_PORT
#   - em USB:  linhas 'OSC|/path|valor' no stdout (lidas pelo bridge)
#
# LED on-board (feedback minimo sem OLED):
#   - splash:   pisca rapido (~5 Hz)
#   - WIFI ok:  aceso fixo  /  WIFI err: pisca lento  /  USB: apagado
#   - FX:       alterna estado para sinalizar que entramos na pagina FX
# =============================================================================

import sys, time, struct, uselect
from machine import Pin, reset

# ===== WiFi: STA mode (liga-se a uma rede existente) =================
# Credenciais em secrets.py (copiar secrets.example.py -> secrets.py e
# preencher). PODES tambem sobrepor com um ficheiro wifi.txt na
# flash do Pico:  linha 1 = SSID, linha 2 = password.
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
except ImportError:
    WIFI_SSID     = ''
    WIFI_PASSWORD = ''

def load_wifi_credentials():
    """Le wifi.txt (SSID\\npassword); sem ficheiro usa as constantes."""
    try:
        with open('wifi.txt') as f:
            lines = [l.strip() for l in f.readlines()]
        if len(lines) >= 2 and lines[0]:
            return lines[0], lines[1]
    except OSError:
        pass
    return WIFI_SSID, WIFI_PASSWORD

APP_PORT = 8080
# IP da app: '' = broadcast automatico para a subnet; ou '192.168.0.196' etc.
APP_IP   = ''
# =====================================================================

# ---------------------------------------------------------------
# Hardware (declarado cedo para o splash poder usar GP28 e o LED)
# ---------------------------------------------------------------
btn1   = Pin(16, Pin.IN, Pin.PULL_UP)
btn2   = Pin(19, Pin.IN, Pin.PULL_UP)
btn3   = Pin(22, Pin.IN, Pin.PULL_UP)
btn4   = Pin(28, Pin.IN, Pin.PULL_UP)
enc_sw = Pin(8,  Pin.IN, Pin.PULL_UP)

try:
    led = Pin('LED', Pin.OUT)
except Exception:
    led = Pin(25, Pin.OUT)
led.off()

# ---------------------------------------------------------------
# Persistencia em flash (transporte WIFI/USB)
# ---------------------------------------------------------------
def load_bool(fname, true_val):
    try:
        with open(fname) as f: return f.read().strip() == true_val
    except: return False

def save_str(fname, val):
    with open(fname, 'w') as f: f.write(val)

use_usb = load_bool('transport.txt', 'USB')   # default False = WIFI

# ---------------------------------------------------------------
# Splash de selecao do transporte
# Pisca o LED por 2 s. Se GP28 for premido nesta janela, alterna.
# ---------------------------------------------------------------
def splash_select_transport():
    """Janela de 2 s para alternar WIFI/USB premindo GP28."""
    global use_usb
    t0 = time.ticks_ms()
    last_blink = t0
    state = False
    while time.ticks_diff(time.ticks_ms(), t0) < 2000:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_blink) > 100:
            state = not state
            led.value(state)
            last_blink = now
        if btn4.value() == 0:           # premido -> alternar e reboot
            use_usb = not use_usb
            save_str('transport.txt', 'USB' if use_usb else 'WIFI')
            # pisca rapido 3x para confirmar
            for _ in range(6):
                led.toggle(); time.sleep(0.1)
            led.off()
            time.sleep(0.2)
            reset()
        time.sleep_ms(10)
    led.off()

splash_select_transport()

# ---------------------------------------------------------------
# Inicializacao do transporte escolhido
# ---------------------------------------------------------------
osc_sock = None
_APP_ADDR = None
sta = None
wifi_ok = False
_wifi_ssid, _wifi_pass = load_wifi_credentials()

def _calc_broadcast(ip, mask):
    ip_p   = [int(x) for x in ip.split('.')]
    mask_p = [int(x) for x in mask.split('.')]
    bc = [(ip_p[i] & mask_p[i]) | (0xff ^ mask_p[i]) for i in range(4)]
    return '.'.join(str(x) for x in bc)

def wifi_apply_ifconfig():
    """Depois de ligar: recalcula o destino (broadcast da subnet ou APP_IP)."""
    global _APP_ADDR, wifi_ok
    ip, mask, gw, dns = sta.ifconfig()
    print('WiFi OK ip={}'.format(ip))
    dst_ip = APP_IP if APP_IP else _calc_broadcast(ip, mask)
    _APP_ADDR = (dst_ip, APP_PORT)
    wifi_ok = True
    led.on()                     # LED fixo = WiFi OK

if use_usb:
    print('Consola 2 - modo USB')
    led.off()
else:
    import network, socket

    DEVICE_NAME = 'PicoW2'

    try:
        network.hostname(DEVICE_NAME)   # tem de ser antes de activar/ligar o WiFi
    except Exception as e:
        print('Nao consegui definir hostname:', e)

    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    # v4: insiste ate conseguir (a v2 ficava morta a piscar para sempre).
    # Pisca enquanto tenta; LED fixo quando liga.
    while not sta.isconnected():
        print('Consola 2 - a ligar a WiFi:', _wifi_ssid)
        try:
            sta.connect(_wifi_ssid, _wifi_pass)
        except Exception:
            pass
        t0 = time.ticks_ms()
        while not sta.isconnected() and time.ticks_diff(time.ticks_ms(), t0) < 15000:
            led.toggle(); time.sleep(0.2)
        if sta.isconnected():
            break
        print('WiFi FALHOU - nova tentativa em 10 s')
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < 10000:
            led.toggle(); time.sleep_ms(500)
    osc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    osc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    wifi_apply_ifconfig()

# Importa RotaryIRQ depois do splash (mais leve no boot inicial)
from rotary_irq_rp2 import RotaryIRQ
enc = RotaryIRQ(6, 7, reverse=True,
                range_mode=RotaryIRQ.RANGE_UNBOUNDED, pull_up=True)

# ---------------------------------------------------------------
# Modos de operacao (PLAYBACK/XF <-> FX, alterna no clique do encoder)
# ---------------------------------------------------------------
PLAYBACK  = 0      # XF — playback de cues
FXMODE    = 1      # pagina FX — toggle de efeitos
mode = PLAYBACK

# v5: 16 FX em 4 grupos de 4. O encoder anda de grupo em grupo (4 em 4); os
# 4 botoes fazem toggle aos 4 FX do grupo actual.
NUM_FX        = 16
FX_PER_GROUP  = 4
NUM_FX_GROUPS = NUM_FX // FX_PER_GROUP    # 4
fx_group      = 0                          # 0..3

DEBOUNCE_MS = 30

# ---------------------------------------------------------------
# Envio OSC (WIFI = UDP; USB = stdout)
# ---------------------------------------------------------------
def _osc_str_bytes(s):
    b = s.encode() + b'\x00'
    r = len(b) % 4
    if r: b += b'\x00' * (4 - r)
    return b

def send_osc_empty(address):
    if use_usb:
        sys.stdout.write('OSC|{}|\n'.format(address)); return
    if not osc_sock: return
    pkt = _osc_str_bytes(address) + _osc_str_bytes(',')
    try: osc_sock.sendto(pkt, _APP_ADDR)
    except Exception: pass

def send_osc_f(address, value):
    if use_usb:
        sys.stdout.write('OSC|{}|{:.4f}\n'.format(address, value)); return
    if not osc_sock: return
    pkt = (_osc_str_bytes(address) + _osc_str_bytes(',f')
           + struct.pack('>f', float(value)))
    try: osc_sock.sendto(pkt, _APP_ADDR)
    except Exception: pass

def send_osc_i(address, value):
    if use_usb:
        sys.stdout.write('OSC|{}|{}\n'.format(address, value)); return
    if not osc_sock: return
    pkt = (_osc_str_bytes(address) + _osc_str_bytes(',i')
           + struct.pack('>i', int(value)))
    try: osc_sock.sendto(pkt, _APP_ADDR)
    except Exception: pass

# ---------------------------------------------------------------
# Accoes dos botoes
# ---------------------------------------------------------------
def _fx_toggle_slot(slot):
    """slot 0..3 -> FX (fx_group*4 + slot + 1). Toggle do efeito na app."""
    n = fx_group * FX_PER_GROUP + slot + 1
    send_osc_empty('/fx/{}/toggle'.format(n))

def do_btn1():
    if mode == PLAYBACK:  send_osc_empty('/go')
    else:                 _fx_toggle_slot(0)

def do_btn2():
    if mode == PLAYBACK:  send_osc_empty('/pause')
    else:                 _fx_toggle_slot(1)

def do_btn3():
    if mode == PLAYBACK:  send_osc_empty('/back')
    else:                 _fx_toggle_slot(2)

def do_btn4():
    if mode == PLAYBACK:  send_osc_empty('/soltar')
    else:                 _fx_toggle_slot(3)

def toggle_mode():
    """Clique do encoder: alterna XF (playback) <-> FX. Avisa a app p/ ela
    mostrar a pagina FX e destacar as 4 teclas do grupo seleccionado."""
    global mode
    mode = FXMODE if mode == PLAYBACK else PLAYBACK
    if mode == FXMODE:
        send_osc_i('/fx/mode', 1)
        send_osc_i('/fx/group', fx_group)
    else:
        send_osc_i('/fx/mode', 0)
    # LED: em WIFI fica fixo (WiFi ON); apaga brevemente p/ sinalizar a troca.
    # Em USB o LED segue o modo (aceso = pagina FX).
    if use_usb:
        led.value(mode == FXMODE)
    else:
        led.off(); time.sleep(0.08); led.on()

# ---------------------------------------------------------------
# Leitor de botoes c/ deteccao de flanco descendente + debounce
# ---------------------------------------------------------------
class Button:
    __slots__ = ('pin', 'last', 'last_change_ms')
    def __init__(self, pin):
        self.pin = pin
        self.last = pin.value()
        self.last_change_ms = 0
    def pressed(self, now):
        cur = self.pin.value()
        if cur != self.last:
            if time.ticks_diff(now, self.last_change_ms) > DEBOUNCE_MS:
                self.last = cur
                self.last_change_ms = now
                return cur == 0
        return False

b1 = Button(btn1)
b2 = Button(btn2)
b3 = Button(btn3)
b4 = Button(btn4)
bs = Button(enc_sw)

# ---------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------
last_enc = enc.value()
_wifi_check_t = time.ticks_ms()    # v4: vigilancia da ligacao WiFi
_wifi_retry_t = 0

# v5: em USB, drena e DESCARTA tudo o que chegar pelo serie (esta consola so
# envia). Evita que o feedback escrito pelo bridge engasgue o stdin/REPL.
_stdin_poll = uselect.poll()
if use_usb:
    _stdin_poll.register(sys.stdin, uselect.POLLIN)

while True:
    now = time.ticks_ms()

    if use_usb:
        n = 0
        while _stdin_poll.poll(0) and n < 256:
            sys.stdin.read(1)          # descarta (nao processa nada)
            n += 1

    # ── v4: vigilancia do WiFi (verifica a cada 5 s; reconecta a cada 10 s).
    #    LED apagado = sem rede; LED fixo = ligado. Os botoes continuam a
    #    funcionar (os envios falham em silencio ate a rede voltar).
    if not use_usb and sta and time.ticks_diff(now, _wifi_check_t) > 5000:
        _wifi_check_t = now
        if sta.isconnected():
            if not wifi_ok:
                wifi_apply_ifconfig()
        else:
            if wifi_ok:
                wifi_ok = False
                led.off()
            if time.ticks_diff(now, _wifi_retry_t) > 10000:
                _wifi_retry_t = now
                try:
                    sta.connect(_wifi_ssid, _wifi_pass)
                except Exception:
                    pass

    if b1.pressed(now): do_btn1()
    if b2.pressed(now): do_btn2()
    if b3.pressed(now): do_btn3()
    if b4.pressed(now): do_btn4()
    if bs.pressed(now): toggle_mode()

    cur_enc = enc.value()
    if cur_enc != last_enc:
        d = 1 if cur_enc > last_enc else -1
        last_enc = cur_enc
        if mode == PLAYBACK:
            if d > 0: send_osc_empty('/cue/go')      # CW = >>>
            else:     send_osc_empty('/cue/back')    # CCW = <<<
        else:   # FXMODE: anda de 4 em 4 (muda de grupo 0..3)
            fx_group = (fx_group + d) % NUM_FX_GROUPS
            send_osc_i('/fx/group', fx_group)

    time.sleep_ms(5)
