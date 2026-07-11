# =============================================================================
# Mesadeluz-OSC_CONSOLA — Consola 1 (firmware Pico W)  -  v5
# =============================================================================
# v5 vs v4 (tamanho do show DINAMICO):
#   - O tamanho do show DEIXA de ter limite fixo no firmware. A app informa a
#     consola via '/show/size N' (handshake): a consola REDIMENSIONA os seus
#     arrays para N+1 canais. Sem mensagem, arranca com 100 (DEFAULT_CHANNELS).
#   - Handshake: ao ligar (e enquanto nao souber o tamanho) a consola pede
#     '/show/size/request' a app de 3 em 3 s; a app responde com '/show/size'
#     e o resto do estado. A app tambem empurra '/show/size' quando descobre
#     a consola ou quando o tamanho do show muda.
#   - Buffers de recepcao aumentados: a lista '/channel/patched' de um show
#     grande passava os 256 bytes do stdin (USB) e os 1024 do UDP (WiFi) e
#     era descartada — a consola caia no fallback de 100. Agora 4096 nos dois.
#   - O limite de browse do encoder passa a ser o tamanho do show (era 100).
#
# v4 vs v3 (estabilidade) — mantido:
#   - Drena VARIOS datagramas UDP por ciclo (a v3 perdia mensagens em rajadas).
#   - Botao DIR sem espera bloqueante (a v3 parava o loop enquanto premido).
#   - Envio OSC com try/except — a perda de WiFi nao crasha a consola.
#   - WiFi: reconexao automatica (tenta de 10 em 10 s; mostra '?' no OLED).
#   - Credenciais WiFi opcionais em wifi.txt (linha 1 = SSID, linha 2 = pass);
#     sem o ficheiro usa as constantes abaixo.
# =============================================================================
# Hardware:
#   OLED 1 (esq):   SDA=GP4   SCL=GP5    I2C(0)
#   OLED 2 (dir):   SDA=GP6   SCL=GP7    I2C(1)
#   Enc ESQ:        A=GP10    B=GP11     SW=GP12
#   Enc DIR:        A=GP13    B=GP14     SW=GP15
#   Fader 1 (SubA): ADC0=GP26
#   Fader 2 (SubB): ADC1=GP27
#
# Modos da consola:
#   MODE_CHANNEL (default) — selecciona/edita canais
#   MODE_CUELIST            — navega cues sem fade, edita fade_in/out
#
# Botao ESQ: 1x => alterna modo CHANNEL <-> CUELIST  (gap >400 ms p/ duplo clique)
#            2x => LIBERTA TUDO (fade 2 s)
#
# CHANNEL:
#   Enc ESQ gira: browse canais; salta canais SEM patch (lista vem da app).
#   Enc DIR gira: AUTO-SELECCIONA o canal em browse + nivel +/- step.
#   Botao DIR  : cicla step  1 -> 5 -> 10 -> 1
#
# CUELIST:
#   Enc ESQ gira: snap p/ cue seguinte/anterior (sem fade, modo edicao).
#   Enc DIR gira: edita FADE IN (default) ou FADE OUT da cue actual.
#                 Step adaptativo:  <3 s = 0.5   <20 s = 1   >=20 s = 5
#   Botao DIR  : alterna entre editar FADE IN / FADE OUT
#
# Faders (ambos modos): submaster 1 / submaster 2 (0-100% -> 0.0-1.0 em OSC)
#
# OSC:
#   Pico  -> App  (porta 8080 da app)
#   App   -> Pico (porta 8081 do Pico, ou via bridge_v2 em USB)
# =============================================================================

import sys, struct, network, socket, time, framebuf, gc, uselect
from machine import Pin, I2C, ADC, reset
from micropython import const
from rotary_irq_rp2 import RotaryIRQ
import ssd1306

# ---------------------------------------------------------------
# Calibracao dos faders (3.3 V) e parametros gerais
# ---------------------------------------------------------------
DEBUG_FADERS = False

ADC0_MIN = const(0)
ADC0_MAX = const(65900)
ADC1_MIN = const(0)
ADC1_MAX = const(65900)

FADER_DEADBAND = const(1)
FADER_END_SNAP = const(2)
GC_INTERVAL_MS = const(2000)

APP_SEND_PORT     = const(8080)    # Pico -> App
CONSOLE_RECV_PORT = const(8081)    # App  -> Pico

# ===== WiFi: STA mode (liga-se a uma rede existente) ============
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

# v5: o tamanho do show e DINAMICO — a app informa via '/show/size N' e a
# consola redimensiona os arrays. Sem essa informacao arranca com este default.
DEFAULT_CHANNELS = const(100)

# Endereco da app para envio OSC:
#   ''                 = broadcast automatico para a subnet em uso
#   '192.168.0.196'    = IP especifico (mais fiavel se a rede tiver isolacao)
APP_IP = ''
# ================================================================
_APP_ADDR = (APP_IP, APP_SEND_PORT)   # actualizado depois de ligar STA

DBL_CLICK_MS = const(400)
FADE_SECONDS = 2.0          # duracao do LIBERTA

LEVEL_STEPS  = (1, 5, 10)    # step do nivel (cicla com SW DIR)

MODE_CHANNEL = const(0)
MODE_CUELIST = const(1)
EDIT_FADE_IN  = const(0)
EDIT_FADE_OUT = const(1)

# Curvas do canal (vindas da app via /channel/N/curva 'S')
CURVE_LINEAR = 'linear'
CURVE_RELE   = 'rele'
CURVE_LIGADO = 'ligado'

# ---------------------------------------------------------------
# Persistencia em flash (USB/WIFI)
# ---------------------------------------------------------------
def load_bool(fname, true_val):
    try:
        with open(fname) as f: return f.read().strip() == true_val
    except: return False

def save_str(fname, val):
    with open(fname, 'w') as f: f.write(val)

use_usb = load_bool('transport.txt', 'USB')

# ---------------------------------------------------------------
# Wi-Fi STA  (liga-se a uma rede existente; ver WIFI_SSID/PASSWORD acima)
# ---------------------------------------------------------------
def _calc_broadcast(ip, mask):
    """Calcula o endereco de broadcast da subnet a partir do ip+netmask."""
    ip_p   = [int(x) for x in ip.split('.')]
    mask_p = [int(x) for x in mask.split('.')]
    bc = [(ip_p[i] & mask_p[i]) | (0xff ^ mask_p[i]) for i in range(4)]
    return '.'.join(str(x) for x in bc)

sta = None
wifi_ok = False
_wifi_ssid, _wifi_pass = load_wifi_credentials()

def wifi_apply_ifconfig():
    """Depois de ligar: recalcula o destino (broadcast da subnet ou APP_IP)."""
    global _APP_ADDR, wifi_ok
    ip, mask, gw, dns = sta.ifconfig()
    print('WiFi OK  ip={} gw={}'.format(ip, gw))
    dst = APP_IP if APP_IP else _calc_broadcast(ip, mask)
    print('APP destino:', dst)
    _APP_ADDR = (dst, APP_SEND_PORT)
    wifi_ok = True

if use_usb:
    print('Modo USB')
else:
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        print('A ligar a WiFi:', _wifi_ssid)
        sta.connect(_wifi_ssid, _wifi_pass)
        t0 = time.ticks_ms()
        while not sta.isconnected() and time.ticks_diff(time.ticks_ms(), t0) < 15000:
            time.sleep(0.2)
    if sta.isconnected():
        wifi_apply_ifconfig()
    else:
        # v4: nao desiste — o loop principal tenta reconectar de 10 em 10 s
        print('WiFi FALHOU - tentarei reconectar no loop')

# ---------------------------------------------------------------
# Hardware
# ---------------------------------------------------------------
i2c0  = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
i2c1  = I2C(1, sda=Pin(6), scl=Pin(7), freq=400000)
oled1 = ssd1306.SSD1306_I2C(128, 64, i2c0)
oled2 = ssd1306.SSD1306_I2C(128, 64, i2c1)

enc_esq = RotaryIRQ(10, 11, reverse=True,
                    range_mode=RotaryIRQ.RANGE_UNBOUNDED, pull_up=True)
enc_dir = RotaryIRQ(13, 14, reverse=True,
                    range_mode=RotaryIRQ.RANGE_UNBOUNDED, pull_up=True)
sw_esq = Pin(12, Pin.IN, Pin.PULL_UP)
sw_dir = Pin(15, Pin.IN, Pin.PULL_UP)

adc0 = ADC(Pin(26))
adc1 = ADC(Pin(27))

def read_fader(adc, raw_min, raw_max):
    raw = (adc.read_u16() + adc.read_u16()
           + adc.read_u16() + adc.read_u16()) >> 2
    if raw <= raw_min: return 0
    if raw >= raw_max: return 100
    pct = (raw - raw_min) * 100 // (raw_max - raw_min)
    if pct <= FADER_END_SNAP:       return 0
    if pct >= 100 - FADER_END_SNAP: return 100
    return pct

def read_f1(): return read_fader(adc0, ADC0_MIN, ADC0_MAX)
def read_f2(): return read_fader(adc1, ADC1_MIN, ADC1_MAX)

# ---------------------------------------------------------------
# OLED helpers
# ---------------------------------------------------------------
_cb = bytearray(8)
_cf = framebuf.FrameBuffer(_cb, 8, 8, framebuf.MONO_VLSB)

def text2x(oled, txt, x, y):
    """Texto duplicado (16x16 por caracter)."""
    for i, ch in enumerate(txt):
        _cf.fill(0); _cf.text(ch, 0, 0, 1)
        x0 = x + i * 16
        for py in range(8):
            for px in range(8):
                if _cf.pixel(px, py):
                    dx, dy = x0 + px*2, y + py*2
                    if 0 <= dx <= 126 and 0 <= dy <= 62:
                        oled.fill_rect(dx, dy, 2, 2, 1)

def text_md(oled, txt, x, y):
    oled.text(txt, x, y)
    oled.text(txt, x+1, y)

def cx2(t): return max(0, (128 - len(t)*16) // 2)
def cx1(t): return max(0, (128 - len(t)*8)  // 2)

# ---------------------------------------------------------------
# Estado da consola
# ---------------------------------------------------------------
# v5: tamanho do show dinamico. show_channels e' o n.º de canais do show
# (informado pela app). Os arrays tem sempre show_channels+1 posicoes (indice 0
# nao usado). show_size_known fica True assim que a app diz o tamanho — ate la
# a consola pede-o a app de tempos a tempos (handshake).
show_channels    = DEFAULT_CHANNELS
show_size_known  = False

ch_browse        = 1
ch_selected      = 0
ch_level         = [0]   * (show_channels + 1)
ch_name          = ['']  * (show_channels + 1)
ch_alcunha       = [0]   * (show_channels + 1)     # 0 = sem alcunha
ch_curva         = [CURVE_LINEAR] * (show_channels + 1)   # 'linear'/'rele'/'ligado'

sub1_val         = 0
sub2_val         = 0
level_step_idx   = 0

mode             = MODE_CHANNEL
# v6.2: modo HIGHLIGHT (inspeccao) — pressao LONGA (3 s) no botao direito.
# Navega-se canais com o encoder esquerdo (cada um destaca-se: vai a 100% e
# fundo amarelo na app). Sair restaura a seleccao que havia antes.
highlight_mode    = False
_hl_prev_selected = 0
# v6.2: no Highlight o encoder DIREITO ajusta este nivel (0-255), NAO o canal.
# Por defeito 255 (100%); pode descer/subir. A app aplica-o aos destacados.
highlight_level   = 255
# v6.2: a consola ESPELHA a pagina da app no modo Highlight. A app envia
# '/page mesa|dmx [univ]'. Na pagina DMX o OLED mostra 'D001'..'D512' e o
# encoder esquerdo percorre os 512 enderecos (envia '/dmx/highlight/addr').
app_page          = 'mesa'
app_univ          = 0
dmx_browse        = 1
cue_edit         = EDIT_FADE_IN
cue_num_str      = ''
cue_fade_in_sec  = 0.0
cue_fade_out_sec = 0.0
last_in_delta    = 0.0
last_out_delta   = 0.0

# Lista de canais com patch (vinda da app via /channel/patched "1,2,5,10").
# Vazia => fallback range(1..show_channels).
patched_channels = []

# ---------------------------------------------------------------
# v5: redimensionamento dinamico do show
# ---------------------------------------------------------------
def set_show_size(n):
    """A app informou o tamanho do show E vai re-sincronizar a seguir.
    '/show/size' e' SEMPRE o arauto de uma re-sincronizacao COMPLETA da app
    (a app envia logo depois os canais COM conteudo, saltando os vazios). Por
    isso aqui:
      - redimensiona para n+1 canais (cresce/encolhe; sem limite fixo);
      - LIMPA nome/alcunha/curva (parte de zero) — assim um canal que a app
        esvaziou nao fica com o rotulo velho na consola;
      - PRESERVA ch_level (estado VIVO do espectaculo; a app nao o reenvia)."""
    global show_channels, show_size_known
    global ch_level, ch_name, ch_alcunha, ch_curva
    global ch_browse, ch_selected, patched_channels
    try:
        n = int(n)
    except Exception:
        return
    if n < 1:
        n = 1
    show_size_known = True

    # niveis: estado vivo -> preserva o que couber no novo tamanho
    new_level = [0] * (n + 1)
    top = min(len(ch_level), n + 1)
    for i in range(1, top):
        new_level[i] = ch_level[i]
    ch_level = new_level

    # rotulos: parte-se de zero (a app reenvia os canais com conteudo)
    ch_name    = ['']           * (n + 1)
    ch_alcunha = [0]            * (n + 1)
    ch_curva   = [CURVE_LINEAR] * (n + 1)

    show_channels = n
    if ch_browse > n:   ch_browse = 1
    if ch_browse < 1:   ch_browse = 1
    if ch_selected > n: ch_selected = 0
    patched_channels = [c for c in patched_channels if c <= n]
    gc.collect()
    req_draw(o1=True, o2=True)

# ---------------------------------------------------------------
# Display
# ---------------------------------------------------------------
def update_oled1():
    # v4: 'WIFI?' = sem ligacao (a tentar reconectar)
    transport = 'USB' if use_usb else ('WIFI' if wifi_ok else 'WIFI?')
    oled1.fill(0)
    if mode == MODE_CHANNEL:
        if highlight_mode and app_page == 'dmx':
            # v6.2: Highlight na pagina DMX — endereco 'D001'..'D512' + universo
            d_str = 'D{:03d}'.format(dmx_browse)
            text2x(oled1, d_str, cx2(d_str), 4)
            u_str = 'U{}'.format(app_univ) if app_univ else 'DMX'
            oled1.text(u_str, cx1(u_str), 30)
        else:
            # numero grande: alcunha se existir, caso contrario o n.º interno
            alc_b  = ch_alcunha[ch_browse] if 1 <= ch_browse <= show_channels else 0
            ch_str = str(alc_b) if alc_b else '{:03d}'.format(ch_browse)
            text2x(oled1, ch_str, cx2(ch_str), 0)
            # nome do canal em browse
            bname = ch_name[ch_browse] if 1 <= ch_browse <= show_channels else ''
            if bname:
                text2x(oled1, bname, cx2(bname), 20)
            # SEL: SEMPRE o n.º interno do canal seleccionado
            if ch_selected:
                sel_str = 'SEL:{:03d}'.format(ch_selected)
                oled1.text(sel_str, cx1(sel_str), 42)
            else:
                oled1.text('LIVRE', cx1('LIVRE'), 42)
    else:   # MODE_CUELIST
        s = cue_num_str if cue_num_str else '---'
        text2x(oled1, s, cx2(s), 24)
    if highlight_mode:                       # v6.2: indicador do modo Highlight
        oled1.text('HL', 0, 56)
    oled1.text(transport, 128 - len(transport)*8, 56)
    oled1.show()

def update_oled2():
    oled2.fill(0)
    if mode == MODE_CHANNEL:
        if highlight_mode:
            # v6.2: no Highlight o encoder direito mexe no NIVEL do highlight
            pct = round(highlight_level * 100 / 255)
            text2x(oled2, 'HL',           cx2('HL'),           0)
            text2x(oled2, '{}%'.format(pct), cx2('{}%'.format(pct)), 20)
        elif ch_selected:
            curva = ch_curva[ch_selected]
            if curva == CURVE_LIGADO:
                # canal "L" — mostra L gigante centrado, sem nivel numerico
                text2x(oled2, 'L', cx2('L'), 12)
                text2x(oled2, 'L', cx2('L') + 1, 12)   # sobreposto p/ ficar bold
            else:
                lv  = ch_level[ch_selected]
                pct = round(lv * 100 / 255)
                lv_str  = str(lv)
                pct_str = '{}%'.format(pct)
                text2x(oled2, lv_str,  cx2(lv_str),  0)
                text2x(oled2, pct_str, cx2(pct_str), 20)
        step_str = '+/-{}'.format(LEVEL_STEPS[level_step_idx])
        oled2.text(step_str, cx1(step_str), 40)
    else:   # MODE_CUELIST -- so o ultimo delta
        def _fmt(d):
            if abs(d) < 0.01: return ''
            sign = '+' if d > 0 else '-'
            a = abs(d)
            if abs(a - int(a)) < 0.01:
                return '{}{}s'.format(sign, int(a))
            return '{}{:.1f}s'.format(sign, a)
        m_in  = '>' if cue_edit == EDIT_FADE_IN  else ' '
        m_out = '>' if cue_edit == EDIT_FADE_OUT else ' '
        din   = _fmt(last_in_delta)
        dout  = _fmt(last_out_delta)
        in_str  = '{}IN {}'.format(m_in,  din)  if din  else '{}IN'.format(m_in)
        out_str = '{}OUT{}'.format(m_out, dout) if dout else '{}OUT'.format(m_out)
        text2x(oled2, in_str,  cx2(in_str),  4)
        text2x(oled2, out_str, cx2(out_str), 28)
    s1 = 'S1:{:3d}%'.format(sub1_val)
    s2 = 'S2:{:3d}%'.format(sub2_val)
    oled2.text(s1, 0,               56)
    oled2.text(s2, 128 - len(s2)*8, 56)
    oled2.show()

def update_display():
    update_oled1()
    update_oled2()

# ---------------------------------------------------------------
# v5: redraw COALESCIDO. Desenhar nos OLEDs (I2C 400kHz + text2x pixel a
# pixel) e' LENTO (dezenas de ms). A v4 redesenhava a cada pacote OSC: numa
# rajada da app a consola ficava presa a desenhar e perdia datagramas (a
# alteracao "nao tinha efeito"). Agora a recepcao OSC so MARCA o que mudou
# (req_draw) e o loop principal redesenha UMA vez por ciclo.
# ---------------------------------------------------------------
_need_oled1 = False
_need_oled2 = False

def req_draw(o1=False, o2=False):
    global _need_oled1, _need_oled2
    if o1: _need_oled1 = True
    if o2: _need_oled2 = True

def flush_display():
    """Redesenha os OLEDs marcados como sujos. Chamado 1x por ciclo do loop."""
    global _need_oled1, _need_oled2
    if _need_oled1:
        _need_oled1 = False
        update_oled1()
    if _need_oled2:
        _need_oled2 = False
        update_oled2()

# ---------------------------------------------------------------
# Splash + escolha de transporte
# ---------------------------------------------------------------
def show_splash():
    oled1.fill(0)
    oled1.text('MesaDeLux', cx1('MesaDeLux'), 0)
    oled1.hline(0, 10, 128, 1)
    oled1.text('Consola OSC', cx1('Consola OSC'), 18)
    oled1.text('SW ESQ:WIFI/USB', 0, 50)
    oled1.show()
    oled2.fill(0)
    oled2.text('Transporte:', cx1('Transporte:'), 18)
    t = 'USB' if use_usb else 'WIFI'
    text2x(oled2, t, cx2(t), 34)
    oled2.show()

def show_msg(line1, line2):
    for o in (oled1, oled2):
        o.fill(0)
        o.text(line1, cx1(line1), 22)
        o.text(line2, cx1(line2), 38)
        o.show()

show_splash()
_t0 = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), _t0) < 3000:
    if sw_esq.value() == 0:
        use_usb = not use_usb
        save_str('transport.txt', 'USB' if use_usb else 'WIFI')
        show_msg('USB' if use_usb else 'WIFI', 'REBOOT...')
        time.sleep(1); reset()
    time.sleep(0.01)

# ---------------------------------------------------------------
# Sockets OSC (so em modo AP; em USB vai pelo serial)
# ---------------------------------------------------------------
osc_sock  = None
recv_sock = None
if not use_usb:
    osc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    osc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(('0.0.0.0', CONSOLE_RECV_PORT))
    recv_sock.setblocking(False)

# ---------------------------------------------------------------
# Envio OSC
# ---------------------------------------------------------------
def _osc_str_bytes(s):
    b = s.encode() + b'\x00'
    r = len(b) % 4
    if r: b += b'\x00' * (4 - r)
    return b

# v4: envio protegido — sem WiFi (ou com erro de rota) NAO crasha a consola.
def _osc_sendto(pkt):
    if not wifi_ok or osc_sock is None:
        return
    try:
        osc_sock.sendto(pkt, _APP_ADDR)
    except OSError:
        pass

def send_osc_i(address, value_int):
    if use_usb:
        sys.stdout.write('OSC|{}|{}\n'.format(address, value_int)); return
    _osc_sendto(_osc_str_bytes(address) + _osc_str_bytes(',i')
                + struct.pack('>i', value_int))

def send_osc_f(address, value_float):
    if use_usb:
        sys.stdout.write('OSC|{}|{:.4f}\n'.format(address, value_float)); return
    _osc_sendto(_osc_str_bytes(address) + _osc_str_bytes(',f')
                + struct.pack('>f', value_float))

def send_osc_empty(address):
    if use_usb:
        sys.stdout.write('OSC|{}|\n'.format(address)); return
    _osc_sendto(_osc_str_bytes(address) + _osc_str_bytes(','))

# ---------------------------------------------------------------
# Recepcao OSC (binario, modo AP)
# ---------------------------------------------------------------
def _osc_str_read(data, offset):
    end = data.index(0, offset)
    s   = data[offset:end].decode('utf-8', 'ignore')
    nxt = end + 1
    if nxt % 4: nxt += 4 - (nxt % 4)
    return s, nxt

def handle_osc_msg(address, args):
    """Dispatch comum para AP (UDP) e USB (serial)."""
    global ch_selected, ch_browse
    global cue_num_str, cue_fade_in_sec, cue_fade_out_sec
    global last_in_delta, last_out_delta
    global patched_channels
    global app_page, app_univ, dmx_browse

    if address == '/show/size' and args:
        # v5: a app informa o tamanho do show -> redimensiona os arrays
        set_show_size(args[0])
        return

    if address == '/dmx/browse' and args:
        # v6.2: o rato saltou para um endereco DMX na app — sincroniza o cursor
        # (o OLED mostra-o e o encoder continua dai). O destaque ja foi feito
        # pela app (clique), por isso aqui so se actualiza o cursor.
        try:
            a = int(args[0])
            if 1 <= a <= 512:
                dmx_browse = a
                req_draw(o1=True)
        except Exception:
            pass
        return

    if address == '/page' and args:
        # v6.2: a app diz a pagina activa (mesa/dmx) + universo. No Highlight
        # a consola segue-a (na DMX mostra Dxxx e percorre os 512 enderecos).
        app_page = 'dmx' if str(args[0]).strip().lower() == 'dmx' else 'mesa'
        if len(args) >= 2:
            try:    app_univ = int(args[1])
            except: app_univ = 0
        if highlight_mode:
            hl_send_current()       # re-destaca o elemento na nova pagina
        req_draw(o1=True, o2=True)
        return

    if address == '/channel/selected' and args:
        n = int(args[0])
        if 0 <= n <= show_channels:
            ch_selected = n
            if n: ch_browse = n
            req_draw(o1=True, o2=True)

    elif (address.startswith('/channel/')
          and address.endswith('/level') and args):
        parts = address.split('/')
        if len(parts) == 4:
            n   = int(parts[2])
            raw = args[0]
            if 1 <= n <= show_channels:
                if isinstance(raw, float) and raw <= 1.0:
                    ch_level[n] = int(raw * 255)
                else:
                    ch_level[n] = max(0, min(255, int(raw)))
                if n == ch_selected:
                    req_draw(o2=True)

    elif (address.startswith('/channel/')
          and address.endswith('/name') and args):
        parts = address.split('/')
        if len(parts) == 4:
            n = int(parts[2])
            if 1 <= n <= show_channels:
                ch_name[n] = str(args[0])[:6]
                if n == ch_browse or n == ch_selected:
                    req_draw(o1=True)

    elif (address.startswith('/channel/')
          and address.endswith('/alcunha') and args):
        parts = address.split('/')
        if len(parts) == 4:
            n = int(parts[2])
            if 1 <= n <= show_channels:
                try:    ch_alcunha[n] = max(0, min(9999, int(args[0])))
                except: ch_alcunha[n] = 0
                if n == ch_browse or n == ch_selected:
                    req_draw(o1=True)

    elif (address.startswith('/channel/')
          and address.endswith('/curva') and args):
        parts = address.split('/')
        if len(parts) == 4:
            n = int(parts[2])
            if 1 <= n <= show_channels:
                v = str(args[0]).strip().lower()
                if v not in (CURVE_LINEAR, CURVE_RELE, CURVE_LIGADO):
                    v = CURVE_LINEAR
                ch_curva[n] = v
                if n == ch_selected:
                    req_draw(o2=True)

    elif address == '/channel/patched' and args:
        try:
            csv = str(args[0])
            new_list = []
            for tok in csv.split(','):
                tok = tok.strip()
                if not tok: continue
                v = int(tok)
                if 1 <= v <= show_channels: new_list.append(v)
            patched_channels = new_list
            if patched_channels and ch_browse not in patched_channels:
                ch_browse = patched_channels[0]
                req_draw(o1=True)
        except Exception:
            pass

    elif address == '/cue/state' and len(args) >= 4:
        # bundle: num (str), label (str ignorado), fade_in (f), fade_out (f)
        cue_num_str = str(args[0])[:7]
        try:    cue_fade_in_sec  = float(args[2])
        except: cue_fade_in_sec  = 0.0
        try:    cue_fade_out_sec = float(args[3])
        except: cue_fade_out_sec = 0.0
        if mode == MODE_CUELIST:
            req_draw(o1=True, o2=True)
    elif address == '/cue/state/num' and args:
        cue_num_str = str(args[0])[:7]
        if mode == MODE_CUELIST: req_draw(o1=True)
    elif address == '/cue/state/fade_in' and args:
        try:    cue_fade_in_sec = float(args[0])
        except: cue_fade_in_sec = 0.0
    elif address == '/cue/state/fade_out' and args:
        try:    cue_fade_out_sec = float(args[0])
        except: cue_fade_out_sec = 0.0

def process_osc_in(data):
    """OSC binario via UDP."""
    try:
        address, off = _osc_str_read(data, 0)
        if not address.startswith('/'): return
        typetag, off = _osc_str_read(data, off)
        types = typetag[1:] if typetag.startswith(',') else ''
        args = []
        for t in types:
            if t == 'i':
                args.append(struct.unpack_from('>i', data, off)[0]); off += 4
            elif t == 'f':
                args.append(struct.unpack_from('>f', data, off)[0]); off += 4
            elif t == 's':
                s, off = _osc_str_read(data, off); args.append(s)
        handle_osc_msg(address, args)
    except Exception:
        pass

def process_serial_in(line):
    """Linha 'IN|/path|v1[|v2|...]' do bridge_v2 (modo USB)."""
    if not line.startswith('IN|'): return
    parts = line.split('|')
    if len(parts) < 2: return
    addr = parts[1]
    args = []
    for v in parts[2:]:
        if v == '':
            args.append('')
        else:
            try:
                if '.' in v:    args.append(float(v))
                else:           args.append(int(v))
            except ValueError:
                args.append(v)
    try: handle_osc_msg(addr, args)
    except Exception: pass

# ---------------------------------------------------------------
# Accoes da consola
# ---------------------------------------------------------------
def do_autoselect():
    """Selecciona o canal em browse. Devolve True se a seleccao MUDOU agora
    (nesse caso o nivel real do canal ainda nao chegou da app — quem chama
    NAO deve aplicar +/- neste detente, para nao incrementar sobre uma base
    velha; ex.: canal de defeito 255 que a consola ainda tinha a 0 saltava
    para ~step). By Worm."""
    global ch_selected
    if ch_selected != ch_browse:
        ch_selected = ch_browse
        send_osc_i('/channel/select', ch_selected)
        return True
    return False

def do_release_all():
    global ch_selected
    ch_selected = 0
    send_osc_f('/release_all', FADE_SECONDS)
    update_display()

def do_level(n, val):
    ch_level[n] = val
    send_osc_i('/channel/{}/level'.format(n), val)
    update_oled2()

def do_submaster(idx, pct):
    send_osc_f('/submaster/{}'.format(idx), pct / 100.0)

def cycle_step():
    global level_step_idx
    level_step_idx = (level_step_idx + 1) % len(LEVEL_STEPS)
    update_oled2()

def hl_send_current():
    """Destaca o elemento da pagina ACTUAL (canal na mesa, endereco no DMX).
    Liga o Highlight na app (pagina certa) + nivel + o elemento. Chamado ao
    entrar no modo e quando a app muda de pagina durante o Highlight."""
    global ch_selected
    send_osc_i('/highlight', 1)
    send_osc_i('/highlight/level', highlight_level)
    if app_page == 'dmx':
        send_osc_i('/dmx/highlight/addr', dmx_browse)
    else:
        ch_selected = ch_browse
        send_osc_i('/channel/select', ch_selected)

def toggle_highlight_mode():
    """v6.2: pressao LONGA do botao direito -> liga/desliga o modo Highlight.
    Segue a pagina da app (mesa=canais / dmx=enderecos). Ao sair restaura a
    seleccao de canais que havia antes de entrar."""
    global highlight_mode, _hl_prev_selected, ch_selected, ch_browse
    highlight_mode = not highlight_mode
    if highlight_mode:
        _hl_prev_selected = ch_selected     # lembra p/ restaurar a' saida
        hl_send_current()
    else:
        send_osc_i('/highlight', 0)
        if app_page == 'dmx':
            send_osc_i('/dmx/highlight/addr', 0)   # limpa o endereco destacado
        ch_selected = _hl_prev_selected     # volta a' seleccao anterior
        if ch_selected:
            ch_browse = ch_selected
        send_osc_i('/channel/select', ch_selected)
    req_draw(o1=True, o2=True)

def toggle_mode():
    global mode
    if highlight_mode:                 # v6.2: sai do Highlight ao trocar de modo
        toggle_highlight_mode()
    mode = MODE_CUELIST if mode == MODE_CHANNEL else MODE_CHANNEL
    if mode == MODE_CUELIST:
        send_osc_empty('/cue/state/request')
    update_display()

def toggle_cue_edit():
    global cue_edit
    cue_edit = EDIT_FADE_OUT if cue_edit == EDIT_FADE_IN else EDIT_FADE_IN
    update_oled2()

def do_cue_go():
    global last_in_delta, last_out_delta
    last_in_delta = 0.0; last_out_delta = 0.0
    send_osc_empty('/cue/go')
    update_oled2()

def do_cue_back():
    global last_in_delta, last_out_delta
    last_in_delta = 0.0; last_out_delta = 0.0
    send_osc_empty('/cue/back')
    update_oled2()

def step_for_value(v):
    if v < 3:  return 0.5
    if v < 20: return 1.0
    return 5.0

def do_cue_fade_delta(d_sign):
    """Aplica delta com step adaptativo; envia float p/ app, actualiza cache."""
    global cue_fade_in_sec, cue_fade_out_sec, last_in_delta, last_out_delta
    cur = cue_fade_in_sec if cue_edit == EDIT_FADE_IN else cue_fade_out_sec
    delta = d_sign * step_for_value(cur)
    new = max(0.0, cur + delta)
    if cue_edit == EDIT_FADE_IN:
        cue_fade_in_sec = new
        last_in_delta = delta
        send_osc_f('/cue/fade_in', delta)
    else:
        cue_fade_out_sec = new
        last_out_delta = delta
        send_osc_f('/cue/fade_out', delta)
    update_oled2()

# ---------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------
update_display()

last_esq = enc_esq.value()
last_dir = enc_dir.value()
last_f1  = read_f1()
last_f2  = read_f2()

_sw_prev      = False
_clicks       = 0
_first_ms     = 0
_sw_dir_prev  = False
_sw_dir_press_t = 0                # v6.2: instante do flanco descendente
_sw_dir_long    = False            # v6.2: a pressao ja disparou a accao longa?

_gc_t  = time.ticks_ms()
_dbg_t = time.ticks_ms()
_wifi_check_t = time.ticks_ms()    # v4: vigilancia da ligacao WiFi
_wifi_retry_t = 0
_show_req_t   = 0                  # v5: pedido periodico do tamanho do show

# stdin para receber OSC reenviado pelo bridge v2 em USB
_stdin_buf  = ''
_stdin_poll = uselect.poll()
if use_usb:
    _stdin_poll.register(sys.stdin, uselect.POLLIN)

gc.collect()

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, _gc_t) > GC_INTERVAL_MS:
        gc.collect(); _gc_t = now
    if DEBUG_FADERS and time.ticks_diff(now, _dbg_t) > 500:
        print('F1={:3d}%  F2={:3d}%'.format(read_f1(), read_f2()))
        _dbg_t = now

    # ── v4: vigilancia do WiFi (verifica a cada 5 s; reconecta a cada 10 s) ──
    if not use_usb and sta and time.ticks_diff(now, _wifi_check_t) > 5000:
        _wifi_check_t = now
        if sta.isconnected():
            if not wifi_ok:
                wifi_apply_ifconfig()      # voltou: recalcula destino
                update_display()
        else:
            if wifi_ok:
                wifi_ok = False            # caiu: mostra 'WIFI?' no OLED
                update_display()
            if time.ticks_diff(now, _wifi_retry_t) > 10000:
                _wifi_retry_t = now
                try:
                    sta.connect(_wifi_ssid, _wifi_pass)
                except Exception:
                    pass

    # ── v5: handshake do tamanho do show ──
    # Enquanto a app nao disser o tamanho, pede-o de 3 em 3 s. Assim que
    # '/show/size' chega (set_show_size), show_size_known fica True e para.
    if not show_size_known and time.ticks_diff(now, _show_req_t) > 3000:
        _show_req_t = now
        send_osc_empty('/show/size/request')

    # ── recepcao OSC (WIFI via UDP, USB via stdin) ──
    if recv_sock:
        # v5: drena ate 24 datagramas por ciclo (a v4 fazia 16) — mais folga
        # para rajadas em WiFi; nunca fica para tras numa sincronizacao.
        for _ in range(24):
            try:
                data, _ = recv_sock.recvfrom(4096)   # v5: patched grande nao trunca
            except OSError:
                break
            process_osc_in(data)
    elif use_usb:
        # v5: drena VARIOS chars por ciclo. A v4 lia 1 char/ciclo (~1/10ms):
        # uma linha longa do bridge (/channel/patched de um show grande, com
        # centenas/milhares de bytes) demorava SEGUNDOS a chegar e a alteracao
        # parecia nao ter efeito. Agora consome ate 1024 chars de cada vez.
        for _ in range(1024):
            if not _stdin_poll.poll(0):
                break
            c = sys.stdin.read(1)
            if not c:
                break
            if c == '\n':
                process_serial_in(_stdin_buf)
                _stdin_buf = ''
            elif c != '\r':
                _stdin_buf += c
                if len(_stdin_buf) > 4096:   # v5: lista patched grande cabe
                    _stdin_buf = ''

    # ── v5: redraw coalescido — UMA vez por ciclo depois de drenar o OSC ──
    flush_display()

    # ── encoder esquerdo ──
    cur_esq = enc_esq.value()
    if cur_esq != last_esq:
        d = 1 if cur_esq > last_esq else -1
        last_esq = cur_esq
        if mode == MODE_CHANNEL:
            if highlight_mode and app_page == 'dmx':
                # v6.2: Highlight na pagina DMX — percorre os 512 enderecos
                dmx_browse = (dmx_browse - 1 + d) % 512 + 1
                send_osc_i('/dmx/highlight/addr', dmx_browse)
            else:
                if patched_channels:
                    try:    idx = patched_channels.index(ch_browse)
                    except ValueError: idx = 0
                    ch_browse = patched_channels[(idx + d) % len(patched_channels)]
                else:
                    ch_browse = (ch_browse - 1 + d) % show_channels + 1
                if highlight_mode:       # v6.2: navegar = destacar este canal
                    ch_selected = ch_browse
                    send_osc_i('/channel/select', ch_selected)
            update_oled1()
        else:    # MODE_CUELIST
            if d > 0: do_cue_go()
            else:     do_cue_back()

    # ── botao esquerdo (1x=modo, 2x=LIBERTA) ──
    sw_p = sw_esq.value() == 0
    if sw_p and not _sw_prev:
        if _clicks == 0: _first_ms = now
        _clicks += 1
    _sw_prev = sw_p
    if (_clicks > 0 and not sw_p
            and time.ticks_diff(now, _first_ms) > DBL_CLICK_MS):
        if _clicks >= 2: do_release_all()
        else:            toggle_mode()
        _clicks = 0

    # ── botao direito: pressao CURTA = step/edit; LONGA (3 s) = Highlight ──
    #    (v6.2: a accao curta dispara ao LARGAR, p/ distinguir da longa)
    sw_dir_p = sw_dir.value() == 0
    if sw_dir_p and not _sw_dir_prev:
        _sw_dir_press_t = now            # flanco descendente: comeca a contar
        _sw_dir_long = False
    elif sw_dir_p and not _sw_dir_long:
        if time.ticks_diff(now, _sw_dir_press_t) >= 3000:
            _sw_dir_long = True          # 3 s premido -> accao LONGA
            if mode == MODE_CHANNEL:     # Highlight so faz sentido em CANAL
                toggle_highlight_mode()
    elif (not sw_dir_p) and _sw_dir_prev:
        held = time.ticks_diff(now, _sw_dir_press_t)
        if not _sw_dir_long and held > 60:   # largou cedo -> accao CURTA
            if mode == MODE_CHANNEL: cycle_step()
            else:                    toggle_cue_edit()
    _sw_dir_prev = sw_dir_p

    # ── encoder direito ──
    cur_dir = enc_dir.value()
    if cur_dir != last_dir:
        d_sign = 1 if cur_dir > last_dir else -1
        last_dir = cur_dir
        if mode == MODE_CHANNEL:
            if highlight_mode:
                # v6.2: no Highlight o encoder direito mexe no NIVEL do
                # highlight (0-255), NAO no valor do canal.
                nv = max(0, min(255, highlight_level + d_sign
                                * LEVEL_STEPS[level_step_idx]))
                if nv != highlight_level:
                    highlight_level = nv
                    send_osc_i('/highlight/level', highlight_level)
                    update_oled2()
            else:
                # v5: se este detente SELECCIONOU um canal novo, so selecciona —
                # o +/- so se aplica quando ja temos o nivel real (proximo
                # detente), senao incrementava sobre uma base velha (255->~10).
                if not do_autoselect():
                    step = LEVEL_STEPS[level_step_idx]
                    nv = max(0, min(255, ch_level[ch_selected] + d_sign * step))
                    if nv != ch_level[ch_selected]:
                        do_level(ch_selected, nv)
                update_display()
        else:
            do_cue_fade_delta(d_sign)

    # ── faders (submasters) ──
    f1 = read_f1()
    if ((f1 == 0 and last_f1 != 0) or
        (f1 == 100 and last_f1 != 100) or
        abs(f1 - last_f1) > FADER_DEADBAND):
        last_f1 = f1; sub1_val = f1
        do_submaster(1, f1); update_oled2()
    f2 = read_f2()
    if ((f2 == 0 and last_f2 != 0) or
        (f2 == 100 and last_f2 != 100) or
        abs(f2 - last_f2) > FADER_DEADBAND):
        last_f2 = f2; sub2_val = f2
        do_submaster(2, f2); update_oled2()

    time.sleep(0.01)
