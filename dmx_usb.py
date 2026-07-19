# -*- coding: utf-8 -*-
"""
dmx_usb.py — MesaDeLux v6.4.1 (By Worm)

Saída DMX por adaptador USB tipo "Open DMX" (clones FTDI sem
microcontrolador: DSD TECH SH-RS09B, Enttec Open DMX, clones
Freestyler, etc.). O break e o timing do frame são gerados pelo host.

Módulo completamente isolado: o ficheiro principal importa-o dentro de
try/except; se faltar o pyserial, a aplicação arranca na mesma com o
USB-DMX desactivado e um aviso no terminal.

Referência (Etapa 0, resultado real do identifica_ftdi.py com o
DSD TECH SH-RS09B ligado, 2026-07-17):

    Porta COM ........: COM4
    VID:PID ..........: 0403:6001
    Número de série ..: BG03LXWFA
    Descrição ........: USB Serial Port (COM4)

O chip é FTDI genuíno com número de série gravado, logo a identificação
persistente entre sessões faz-se por número de série (tipo_id "serial").
Clones sem número de série reencontram-se pela porta COM (tipo_id
"porta"); sendo o dispositivo único por desenho, se a COM guardada não
existir mas houver exactamente um adaptador FTDI ligado, usa-se esse.
"""

import sys
import threading
import time

try:
    import serial
    from serial.tools import list_ports
    PYSERIAL_OK = True
except ImportError:          # pyserial em falta — módulo fica inerte
    serial = None
    list_ports = None
    PYSERIAL_OK = False

# FTDI: FT232R/FT232RNL (0x6001) — a esmagadora maioria dos clones;
# FT230X (0x6015) — alguns clones recentes.
VID_FTDI = 0x0403
PIDS_FTDI = (0x6001, 0x6015)

# Gama de refresh permitida (Hz). Alguns fixtures baratos engasgam com
# refresh alto em clones Open DMX; baixar o refresh resolve a maioria.
REFRESH_MIN = 25
REFRESH_MAX = 40
REFRESH_DEFAULT = 30


def _resolucao_timer(fina):
    """Windows: pede (ou liberta) resolução de timer de 1 ms.

    Sem isto, qualquer time.sleep arredonda para o tick de ~15,6 ms do
    sistema — os micro-sleeps do break/MAB e o intervalo entre frames
    somavam ~100 ms por frame e o DMX saía a ~10 Hz em vez de 30 Hz
    (medido com testador real). Com timeBeginPeriod(1) a granularidade
    passa a ~1 ms, o que chega para os 25-40 Hz do Open DMX. Não é
    busy-wait: a CPU continua livre. Chamar sempre em pares
    (fina=True ao arrancar, fina=False ao parar)."""
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        if fina:
            ctypes.windll.winmm.timeBeginPeriod(1)
        else:
            ctypes.windll.winmm.timeEndPeriod(1)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────
# Detecção de dispositivos
# ─────────────────────────────────────────────────────────────────────

class DispositivoFTDI:
    """Um adaptador FTDI detectado no sistema."""

    def __init__(self, porta, serie, descricao, vid, pid):
        self.porta = porta            # ex: 'COM4'
        self.serie = serie or None    # ex: 'BG03LXWFA'; None em clones s/ série
        self.descricao = descricao    # ex: 'USB Serial Port (COM4)'
        self.vid = vid
        self.pid = pid

    def rotulo(self):
        """Texto para o dropdown, ex: 'COM4 — FT232R (S/N BG03LXWFA)'."""
        chip = 'FT232R' if self.pid == 0x6001 else 'FT230X'
        if self.serie:
            return '%s — %s (S/N %s)' % (self.porta, chip, self.serie)
        return '%s — %s (sem S/N)' % (self.porta, chip)

    def __repr__(self):
        return '<DispositivoFTDI %s>' % self.rotulo()


def listar_dispositivos():
    """Lista os adaptadores FTDI ligados (VID 0403, PID 6001/6015)."""
    if not PYSERIAL_OK:
        return []
    out = []
    for p in list_ports.comports():
        if p.vid == VID_FTDI and p.pid in PIDS_FTDI:
            out.append(DispositivoFTDI(p.device, p.serial_number,
                                       p.description, p.vid, p.pid))
    return out


def encontrar_dispositivo(disp_id, tipo_id, porta_com):
    """Reencontra o dispositivo configurado entre os que estão ligados.

    disp_id  = número de série (tipo_id 'serial') ou porta COM (tipo_id
               'porta'), tal como persistido no config.json.
    Devolve (dispositivo, nota): dispositivo é None se não foi
    reencontrado; nota é uma mensagem para o terminal quando a
    configuração deve ser actualizada (COM mudou), senão None.
    """
    ligados = listar_dispositivos()
    if not ligados:
        return None, None

    if tipo_id == 'serial' and disp_id:
        for d in ligados:
            if d.serie == disp_id:
                return d, None
        return None, None

    # tipo_id 'porta' (clones sem número de série)
    for d in ligados:
        if d.porta == porta_com:
            return d, None
    # A COM guardada não existe; sendo o dispositivo único por desenho,
    # se há exactamente um adaptador FTDI ligado, é esse.
    if len(ligados) == 1:
        d = ligados[0]
        nota = ('USB-DMX: a porta %s guardada não existe; a usar o único '
                'adaptador FTDI ligado (%s). Configuração actualizada.'
                % (porta_com, d.porta))
        return d, nota
    return None, None


# ─────────────────────────────────────────────────────────────────────
# Drivers
# ─────────────────────────────────────────────────────────────────────

class DriverDMXUSB:
    """Classe base abstracta para adaptadores USB-DMX."""

    def abrir(self):
        raise NotImplementedError

    def fechar(self):
        raise NotImplementedError

    def enviar_frame(self, dados):
        """dados: 512 bytes de níveis (canais 1-512)."""
        raise NotImplementedError


class DriverOpenDMX(DriverDMXUSB):
    """Clones FTDI 'Open DMX USB' (Freestyler, Enttec Open DMX, etc.).

    Sem microcontrolador — o break e o timing são gerados pelo host.
    Nota sobre timing: o time.sleep em Windows tem granularidade
    limitada; os valores abaixo funcionam na prática com clones FT232R
    porque o driver FTDI adiciona a sua própria latência. Não optimizar
    com busy-wait — a imprecisão é limitação conhecida do Open DMX.
    """

    def __init__(self, porta_com):
        self.porta_com = porta_com
        self.porta = None

    def abrir(self):
        self.porta = serial.Serial(
            port=self.porta_com,
            baudrate=250000,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
        )

    def fechar(self):
        if self.porta is not None:
            try:
                self.porta.close()
            except Exception:
                pass
            self.porta = None

    def enviar_frame(self, dados):
        p = self.porta
        p.break_condition = True     # Break
        time.sleep(0.000100)         # ~100 µs (mínimo DMX: 88 µs)
        p.break_condition = False    # Mark After Break
        time.sleep(0.000012)         # ~12 µs
        p.write(bytes([0x00]) + dados)   # Start code 0 + 512 canais


# ─────────────────────────────────────────────────────────────────────
# Thread de transmissão contínua
# ─────────────────────────────────────────────────────────────────────

class TransmissorDMXUSB:
    """Stream DMX contínuo para um dispositivo Open DMX.

    Ao contrário do sACN, o DMX por cabo exige stream contínuo — muitos
    fixtures apagam ou congelam se o sinal parar. A thread lê sempre o
    buffer actual do universo via `obter_buffer` (polling, sem eventos);
    a função deve devolver uma CÓPIA thread-safe de 512 bytes.

    Estados: 'inactivo' → 'activo' → ('erro' se a escrita falhar, ex.
    dongle desligado fisicamente; a thread termina e a aplicação
    continua a funcionar normalmente).
    """

    def __init__(self, driver, obter_buffer, refresh_hz=REFRESH_DEFAULT):
        self.driver = driver
        self.obter_buffer = obter_buffer
        self.refresh_hz = max(REFRESH_MIN, min(REFRESH_MAX, int(refresh_hz)))
        self.activo = False
        self.estado = 'inactivo'
        self.erro = None
        self._thread = None
        self._timer_fino = False

    def arrancar(self):
        """Abre o driver e arranca a thread. Devolve (ok, msg_erro)."""
        if self.activo:
            return True, None
        try:
            self.driver.abrir()
        except Exception as e:
            self.estado = 'erro'
            self.erro = str(e)
            return False, str(e)
        self.activo = True
        self.estado = 'activo'
        self.erro = None
        _resolucao_timer(True)
        self._timer_fino = True
        self._thread = threading.Thread(target=self._loop_transmissao,
                                        daemon=True,
                                        name='dmx-usb-tx')
        self._thread.start()
        return True, None

    def parar(self):
        """Pára a thread e fecha o driver. Seguro chamar em qualquer estado."""
        self.activo = False
        t = self._thread
        if t is not None and t.is_alive():
            t.join(timeout=1.0)
        self._thread = None
        self.driver.fechar()
        if self._timer_fino:
            _resolucao_timer(False)
            self._timer_fino = False
        if self.estado != 'erro':
            self.estado = 'inactivo'

    def _loop_transmissao(self):
        # Ritmo por perf_counter: o sleep só cobre o tempo que falta até
        # ao próximo frame (o write bloqueante já gasta ~23 ms dos ~33 ms
        # de um frame a 30 Hz), sem acumular atraso.
        intervalo = 1.0 / self.refresh_hz
        proximo = time.perf_counter()
        while self.activo:
            dados = self.obter_buffer()
            try:
                self.driver.enviar_frame(dados)
            except Exception as e:
                # Dongle desligado fisicamente, porta perdida, etc.:
                # marca erro para a UI e termina sem crashar a aplicação.
                self.erro = str(e)
                self.estado = 'erro'
                self.activo = False
                self.driver.fechar()
                break
            proximo += intervalo
            agora = time.perf_counter()
            if agora < proximo:
                time.sleep(proximo - agora)
            else:
                proximo = agora     # atrasado: recomeça sem dívida
