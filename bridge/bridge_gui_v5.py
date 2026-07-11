"""
bridge_gui_v5.py — Interface gráfica para o osc_bridge_v5.

v5 vs v4:
  - Cada consola tem DOIS sentidos INDEPENDENTES em vez do único «Bidir.»:
      * IN  (recv) = consola → app   (o bridge lê o série e manda p/ a app)
      * OUT (send) = app → consola    (o bridge escreve o feedback no série)
    Permite usar uma consola só a enviar (IN), só a receber (OUT), as duas, ou
    desligar (nenhuma → a porta nem se abre). Ex.: a Consola 2 (playback, só
    envia) fica IN ligado / OUT desligado e deixa de receber o feedback da
    Consola 1 (que estava a interferir).
  - Config em bridge_config_v5.json (migra o «bidirectional» da v4).

Correr: python bridge_gui_v5.py
"""

import queue
import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import osc_bridge_v5 as bridge_mod


# ---------------------------------------------------------------
# Lista todos os IPs locais (loopback + interfaces de rede)
# ---------------------------------------------------------------
def get_local_ips():
    ips = ['127.0.0.1']
    try:
        hostname = socket.gethostname()
        infos = socket.getaddrinfo(hostname, None)
        for info in infos:
            addr = info[4][0]
            if ':' not in addr and addr not in ips:
                ips.append(addr)
    except Exception:
        pass
    return ips


# ---------------------------------------------------------------
# Janela principal
# ---------------------------------------------------------------
class BridgeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('OSC Bridge v5 (multi-consola, IN/OUT independentes)')
        self.root.resizable(False, False)
        self.bridge = None
        self._log_queue = queue.Queue()

        self._build_ui()
        self._load_config()
        self._pump_log()

    def _build_ui(self):
        PAD = dict(padx=10, pady=5)

        # --- Configuração ---
        cfg = ttk.LabelFrame(self.root, text='Configuração')
        cfg.grid(row=0, column=0, columnspan=2, sticky='ew', **PAD)

        ttk.Label(cfg, text='Consolas (portas série):',
                  font=('Arial', 9, 'bold')).grid(
            row=0, column=0, columnspan=5, sticky='w', **PAD)

        ttk.Label(cfg, text='Nome',  width=10).grid(row=1, column=0, sticky='w', padx=8)
        ttk.Label(cfg, text='Porta', width=10).grid(row=1, column=1, sticky='w')
        ttk.Label(cfg, text='IN',    width=4 ).grid(row=1, column=2, sticky='w', padx=4)
        ttk.Label(cfg, text='OUT',   width=4 ).grid(row=1, column=3, sticky='w', padx=4)
        ttk.Label(cfg, text='(IN: consola→app   OUT: app→consola)',
                  foreground='#888').grid(row=1, column=4, sticky='w')

        # duas linhas fixas (Consola 1 e Consola 2)
        self.var_names = []
        self.var_ports = []
        self.var_recv  = []
        self.var_send  = []
        for i in range(2):
            vn = tk.StringVar(value=f'consola{i+1}')
            vp = tk.StringVar(value='')
            vr = tk.BooleanVar(value=True)            # IN ligado por defeito
            vs = tk.BooleanVar(value=(i == 0))        # OUT só na 1.ª por defeito
            self.var_names.append(vn)
            self.var_ports.append(vp)
            self.var_recv.append(vr)
            self.var_send.append(vs)
            ttk.Entry(cfg, textvariable=vn, width=10).grid(
                row=2 + i, column=0, sticky='w', padx=8, pady=2)
            ttk.Entry(cfg, textvariable=vp, width=10).grid(
                row=2 + i, column=1, sticky='w', pady=2)
            ttk.Checkbutton(cfg, variable=vr).grid(
                row=2 + i, column=2, sticky='w', padx=4, pady=2)
            ttk.Checkbutton(cfg, variable=vs).grid(
                row=2 + i, column=3, sticky='w', padx=4, pady=2)

        ttk.Separator(cfg, orient='horizontal').grid(
            row=4, column=0, columnspan=5, sticky='ew', padx=10, pady=4)

        ttk.Label(cfg, text='Consolas → App',
                  font=('Arial', 9, 'bold')).grid(
            row=5, column=0, columnspan=5, sticky='w', **PAD)

        ttk.Label(cfg, text='IP da app:').grid(row=6, column=0, sticky='w', **PAD)
        self.var_app_ip = tk.StringVar()
        self.combo_app_ip = ttk.Combobox(cfg, textvariable=self.var_app_ip,
                                         width=20, values=get_local_ips())
        self.combo_app_ip.grid(row=6, column=1, columnspan=3, sticky='w', **PAD)

        ttk.Label(cfg, text='Porta da app:').grid(row=7, column=0, sticky='w', **PAD)
        self.var_app_port = tk.StringVar()
        ttk.Entry(cfg, textvariable=self.var_app_port, width=8).grid(
            row=7, column=1, sticky='w', **PAD)

        ttk.Separator(cfg, orient='horizontal').grid(
            row=8, column=0, columnspan=5, sticky='ew', padx=10, pady=4)

        ttk.Label(cfg, text='App → Consolas (OUT)',
                  font=('Arial', 9, 'bold')).grid(
            row=9, column=0, columnspan=5, sticky='w', **PAD)

        ttk.Label(cfg, text='Porta de entrada\n(bridge escuta):').grid(
            row=10, column=0, sticky='w', **PAD)
        self.var_in_port = tk.StringVar()
        ttk.Entry(cfg, textvariable=self.var_in_port, width=8).grid(
            row=10, column=1, sticky='w', **PAD)

        ttk.Button(cfg, text='Guardar configuração',
                   command=self._save_config).grid(
            row=11, column=0, columnspan=5, pady=(8, 8))

        # --- Botões arranque/paragem ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=1, column=0, columnspan=2, **PAD)

        self.btn_start = ttk.Button(btn_frame, text='▶  Arrancar bridge',
                                    command=self._start, width=22)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_stop = ttk.Button(btn_frame, text='■  Parar bridge',
                                   command=self._stop, width=22, state='disabled')
        self.btn_stop.grid(row=0, column=1, padx=5)

        # --- Indicador de estado ---
        self.lbl_status = ttk.Label(self.root, text='● Parado', foreground='gray')
        self.lbl_status.grid(row=2, column=0, columnspan=2)

        # --- Log de saída ---
        log_frame = ttk.LabelFrame(self.root, text='Saída do bridge')
        log_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', **PAD)

        self.log = scrolledtext.ScrolledText(
            log_frame, width=72, height=22,
            bg='#1e1e1e', fg='#d4d4d4',
            font=('Consolas', 9), state='disabled')
        self.log.grid(row=0, column=0, padx=5, pady=5)

        # cores no log
        self.log.tag_config('c1',  foreground='#5dade2')   # consola1 -> PC
        self.log.tag_config('c2',  foreground='#2ecc71')   # consola2 -> PC
        self.log.tag_config('a2p', foreground='#f0d840')   # PC -> consolas
        self.log.tag_config('sys', foreground='#aaaaaa')

        ttk.Button(self.root, text='Limpar', command=self._clear_log).grid(
            row=4, column=0, columnspan=2, pady=(0, 8))

        self.root.protocol('WM_DELETE_WINDOW', self._quit)

    # ── configuração (JSON) ──────────────────
    def _load_config(self):
        try:
            cfg = bridge_mod.load_config()
            self.var_app_port.set(str(cfg['app_port']))
            self.var_in_port.set(str(cfg['listen_port']))
            saved_ip = cfg['app_ip']
            current = list(self.combo_app_ip['values'])
            if saved_ip and saved_ip not in current:
                current.insert(0, saved_ip)
                self.combo_app_ip['values'] = current
            self.var_app_ip.set(saved_ip)
            for i, con in enumerate(cfg['consoles'][:2]):
                self.var_names[i].set(con.get('name', f'consola{i+1}'))
                self.var_ports[i].set(con.get('port', ''))
                self.var_recv[i].set(bool(con.get('recv', True)))
                self.var_send[i].set(bool(con.get('send', i == 0)))
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível ler a config:\n{e}')

    def _save_config(self):
        consoles = []
        for i in range(2):
            n = self.var_names[i].get().strip()
            p = self.var_ports[i].get().strip()
            r = bool(self.var_recv[i].get())
            s = bool(self.var_send[i].get())
            # consola sem porta: só é erro se algum sentido estiver ligado
            if (r or s) and (not n or not p):
                messagebox.showwarning('Atenção',
                                       f'Consola {i+1}: preenche nome e porta '
                                       '(ou desliga IN e OUT).')
                return None
            if n and p:
                consoles.append({'name': n, 'port': p, 'recv': r, 'send': s})
        app_ip = self.var_app_ip.get().strip()
        try:
            app_port = int(self.var_app_port.get().strip())
            in_port = int(self.var_in_port.get().strip())
        except ValueError:
            messagebox.showwarning('Atenção', 'Portas têm de ser números.')
            return None
        if not app_ip:
            messagebox.showwarning('Atenção', 'Preenche o IP da app.')
            return None
        cfg = bridge_mod.load_config()
        cfg.update({'consoles': consoles, 'app_ip': app_ip,
                    'app_port': app_port, 'listen_port': in_port})
        try:
            bridge_mod.save_config(cfg)
            self._log_line('[config guardada]  '
                           + ' / '.join('{}={}[{}{}]'.format(
                                 c['name'], c['port'],
                                 'IN' if c['recv'] else '',
                                 '+OUT' if c['send'] else (
                                     'OUT' if not c['recv'] else ''))
                             for c in consoles)
                           + f'   app={app_ip}:{app_port}  in=:{in_port}\n',
                           'sys')
            return cfg
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível guardar:\n{e}')
            return None

    # ── arranque / paragem (in-process) ──────
    def _start(self):
        if self.bridge:
            return
        cfg = self._save_config()
        if cfg is None:
            return
        try:
            # log thread-safe: as threads do bridge escrevem na queue
            self.bridge = bridge_mod.Bridge(
                cfg, log=lambda line: self._log_queue.put(line))
            self.bridge.start()
        except Exception as e:
            self.bridge = None
            messagebox.showerror('Erro',
                                 f'Não foi possível arrancar o bridge:\n{e}')
            return

        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='normal')
        self.lbl_status.config(text='● A correr', foreground='green')
        self._log_line('[bridge v5 iniciado]\n', 'sys')

    def _stop(self):
        if self.bridge:
            try:
                self.bridge.stop()
            except Exception:
                pass
            self.bridge = None
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.lbl_status.config(text='● Parado', foreground='gray')
        self._log_line('[bridge parado]\n', 'sys')

    def _quit(self):
        self._stop()
        self.root.destroy()

    # ── log (pump thread-safe) ───────────────
    def _pump_log(self):
        """Drena a queue de log no mainloop (~10x/s)."""
        try:
            while True:
                line = self._log_queue.get_nowait()
                names = [self.var_names[i].get().strip() for i in range(2)]
                if line.startswith('PC ->'):
                    tag = 'a2p'
                elif names[0] and line.startswith(names[0] + ' ->'):
                    tag = 'c1'
                elif names[1] and line.startswith(names[1] + ' ->'):
                    tag = 'c2'
                else:
                    tag = 'sys'
                if not line.endswith('\n'):
                    line += '\n'
                self._log_line(line, tag)
        except queue.Empty:
            pass
        self.root.after(100, self._pump_log)

    def _log_line(self, text, tag='sys'):
        self.log.config(state='normal')
        self.log.insert('end', text, tag)
        self.log.see('end')
        self.log.config(state='disabled')

    def _clear_log(self):
        self.log.config(state='normal')
        self.log.delete('1.0', 'end')
        self.log.config(state='disabled')


if __name__ == '__main__':
    root = tk.Tk()
    app = BridgeGUI(root)
    root.mainloop()
