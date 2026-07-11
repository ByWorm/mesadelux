# =============================================================================
# osc_bridge_v5.py — Bridge USB <-> OSC para MULTIPLAS consolas
# =============================================================================
# v5 vs v4:
#   - Cada consola tem DOIS sentidos INDEPENDENTES (antes era um unico flag
#     'bidirectional'):
#       * IN  (recv): a consola -> app   (o bridge LE o serie e manda p/ a app)
#       * OUT (send): a app -> consola    (o bridge ESCREVE o feedback no serie)
#     Assim pode-se usar uma consola so para enviar (IN), so para receber (OUT),
#     as duas (bidireccional) ou desligar (nenhuma -> a porta nem se abre).
#     Ex.: a Consola 2 (playback, so envia) fica IN e OUT desligado -> NUNCA
#     lhe e' escrito o feedback da Consola 1 (acabava a interferir).
#   - Migra automaticamente configs v4: 'bidirectional' -> recv=True,
#     send=<bidirectional>.
#
# Formato serial (igual a v2/v3/v4):
#   Consola -> PC : 'OSC|/path|valor\n'
#   PC -> consola : 'IN|/path|v1[|v2|...]\n'
# =============================================================================

import json
import sys
import time
import threading
from pathlib import Path

import serial
from pythonosc import udp_client, dispatcher, osc_server


# -----------------------------------------------------------------------------
# Configuracao (JSON ao lado do ficheiro / executavel)
# -----------------------------------------------------------------------------
def base_dir():
    """Pasta onde vive o programa — funciona em .py e em .exe (PyInstaller)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


CONFIG_FILE = base_dir() / 'bridge_config_v5.json'

DEFAULT_CONFIG = {
    'consoles': [
        # recv = consola->app (IN) ; send = app->consola (OUT)
        {'name': 'consola1', 'port': 'COM5', 'recv': True, 'send': True},
        {'name': 'consola2', 'port': 'COM6', 'recv': True, 'send': False},
    ],
    'baud': 115200,
    'app_ip': '127.0.0.1',     # para onde vao as mensagens das consolas
    'app_port': 8080,
    'listen_ip': '0.0.0.0',    # onde o bridge escuta a app (feedback)
    'listen_port': 8081,
}


def _migrate_console(con):
    """Normaliza uma entrada de consola para o esquema v5 (recv/send).
    Aceita o 'bidirectional' da v4: recv=True, send=<bidirectional>."""
    con = dict(con)
    if 'recv' not in con and 'send' not in con and 'bidirectional' in con:
        con['recv'] = True
        con['send'] = bool(con.get('bidirectional'))
    con.setdefault('recv', True)
    con.setdefault('send', False)
    con.pop('bidirectional', None)
    return con


def load_config():
    """Le o JSON de configuracao; cria-o com os defaults se nao existir.
    Migra entradas v4 (bidirectional) para o esquema v5 (recv/send)."""
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            cfg.update(data)
    except FileNotFoundError:
        save_config(cfg)
    except Exception as e:
        print('Aviso: config invalida ({}) — a usar defaults.'.format(e))
    cfg['consoles'] = [_migrate_console(c) for c in cfg.get('consoles', [])]
    return cfg


def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# -----------------------------------------------------------------------------
# Bridge
# -----------------------------------------------------------------------------
def _format_for_pico(address, args):
    """OSC para texto: IN|/path|v1[|v2|...]\\n  (mesmo formato do v2/v3/v4)."""
    parts = ['IN', address]
    for a in args:
        if isinstance(a, bool):
            parts.append('1' if a else '0')
        elif isinstance(a, int):
            parts.append(str(a))
        elif isinstance(a, float):
            parts.append('{:.4f}'.format(a))
        else:
            parts.append(str(a).replace('|', ' '))
    return '|'.join(parts) + '\n'


def _dir_label(con):
    """Etiqueta legivel do(s) sentido(s) activo(s) de uma consola."""
    r, s = con.get('recv'), con.get('send')
    if r and s:   return 'IN+OUT (bidireccional)'
    if r:         return 'IN (so recebe da consola)'
    if s:         return 'OUT (so envia p/ consola)'
    return 'DESLIGADA'


class Bridge:
    """Bridge serie<->OSC. start() lanca as threads; stop() para tudo.
    log: callable(str) — recebe as linhas de estado (default: print).
    NOTA p/ GUI: o log e chamado a partir de threads do bridge — no Tkinter
    usar uma queue + after, NUNCA tocar nos widgets directamente."""

    def __init__(self, cfg, log=print):
        self.cfg = cfg
        self.log = log
        self._sers = {}                    # nome -> serial aberto
        self._ser_lock = threading.Lock()
        self._stop = threading.Event()
        self._server = None
        self._threads = []

    # ── ciclo de vida ─────────────────────────
    def start(self):
        self._stop.clear()
        client = udp_client.SimpleUDPClient(
            self.cfg['app_ip'], int(self.cfg['app_port']))

        # servidor OSC (app -> consolas com OUT/send activo)
        disp = dispatcher.Dispatcher()
        disp.set_default_handler(self._to_send_serials,
                                 needs_reply_address=False)
        self._server = osc_server.ThreadingOSCUDPServer(
            (self.cfg.get('listen_ip', '0.0.0.0'),
             int(self.cfg['listen_port'])), disp)
        t = threading.Thread(target=self._server.serve_forever, daemon=True)
        t.start()
        self._threads.append(t)
        self.log('Bridge v5: a escutar app em :{}'.format(
            self.cfg['listen_port']))

        # uma thread por consola COM pelo menos um sentido activo
        for con in self.cfg['consoles']:
            con = _migrate_console(con)
            if not (con.get('recv') or con.get('send')):
                self.log('Consola {} em {} — DESLIGADA (sem IN nem OUT)'.format(
                    con['name'], con['port']))
                continue
            t = threading.Thread(target=self._serial_reader,
                                 args=(client, con), daemon=True)
            t.start()
            self._threads.append(t)
            self.log('Consola {} em {}  [{}]'.format(
                con['name'], con['port'], _dir_label(con)))

    def stop(self):
        self._stop.set()
        if self._server:
            try:
                self._server.shutdown()
            finally:
                try:
                    self._server.server_close()
                except Exception:
                    pass
            self._server = None
        # fechar as portas serie desbloqueia os readline() pendentes
        with self._ser_lock:
            for name, ser in list(self._sers.items()):
                try:
                    ser.close()
                except Exception:
                    pass
            self._sers.clear()
        self.log('Bridge parada.')

    # ── App -> consolas com OUT (send) ────────
    def _to_send_serials(self, address, *args):
        line = _format_for_pico(address, list(args))
        encoded = line.encode('utf-8')
        sent_to = []
        with self._ser_lock:
            for con in self.cfg['consoles']:
                if not con.get('send'):
                    continue
                ser = self._sers.get(con['name'])
                if ser is None:
                    continue
                try:
                    ser.write(encoded)
                    sent_to.append(con['name'])
                except Exception as e:
                    self.log('Erro a escrever {}: {}'.format(con['name'], e))
        if sent_to:
            self.log('PC -> {}   {}'.format(','.join(sent_to), line.strip()))

    # ── Consola -> App (so encaminha se IN/recv) ──
    def _serial_reader(self, client, con):
        """Thread por consola: abre a porta (precisa dela p/ ler E/ou escrever).
        Se recv (IN), encaminha 'OSC|...' do serial -> UDP para a app. Se nao
        for recv, continua a ler para esvaziar o buffer mas NAO encaminha.
        Reconecta automaticamente se a porta cair. Sai quando stop() e dado."""
        name, port = con['name'], con['port']
        recv = bool(con.get('recv'))
        baud = int(self.cfg.get('baud', 115200))
        while not self._stop.is_set():
            try:
                with serial.Serial(port, baud, timeout=1) as ser:
                    with self._ser_lock:
                        self._sers[name] = ser
                    self.log('Aberta {} em {} [{}]'.format(
                        name, port, _dir_label(con)))
                    while not self._stop.is_set():
                        raw = ser.readline()
                        if not raw:
                            continue          # timeout 1 s — verifica o stop
                        if not recv:
                            continue          # OUT-only: le p/ esvaziar, nao encaminha
                        line = raw.decode('utf-8', errors='ignore').strip()
                        if not line.startswith('OSC|'):
                            continue
                        parts = line.split('|')
                        if len(parts) != 3:
                            continue
                        raw_val = parts[2]
                        if raw_val == '':
                            client.send_message(parts[1], [])
                            val_repr = '(no args)'
                        else:
                            try:
                                if '.' in raw_val:
                                    val = float(raw_val)
                                else:
                                    val = int(raw_val)
                            except ValueError:
                                val = raw_val
                            client.send_message(parts[1], val)
                            val_repr = repr(val)
                        self.log('{} -> PC   {}   {}'.format(
                            name, parts[1], val_repr))
            except serial.SerialException as e:
                with self._ser_lock:
                    self._sers.pop(name, None)
                if self._stop.is_set():
                    break
                self.log('{} ({}) perdida: {}'.format(name, port, e))
                self.log('A tentar reconectar {} em 3 s...'.format(name))
                if self._stop.wait(3):
                    break
            except Exception as e:
                if self._stop.is_set():
                    break
                self.log('Erro inesperado em {}: {}'.format(name, e))
                if self._stop.wait(3):
                    break
        with self._ser_lock:
            self._sers.pop(name, None)


# -----------------------------------------------------------------------------
# Execucao directa (linha de comandos)
# -----------------------------------------------------------------------------
def main():
    cfg = load_config()
    print('==============================================================')
    print('  Bridge OSC v5 (multi-consola, IN/OUT independentes)')
    for con in cfg['consoles']:
        print('  {} ({}) -> {}'.format(con['name'], con['port'],
                                       _dir_label(con)))
    print('  app em {}:{}'.format(cfg['app_ip'], cfg['app_port']))
    print('  escuta entrada (app -> consolas OUT) em :{}'.format(
        cfg['listen_port']))
    print('  config: {}'.format(CONFIG_FILE))
    print('  Ctrl+C para sair')
    print('==============================================================\n')

    bridge = Bridge(cfg)
    bridge.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bridge.stop()
        print('\nBridge encerrada.')


if __name__ == '__main__':
    main()
