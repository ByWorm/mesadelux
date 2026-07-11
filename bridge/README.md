# Bridge USB/OSC

## 🇵🇹 Português

Ponte entre as consolas físicas (ligadas por **USB**) e a app MESADELUX
(que fala **OSC/UDP**). Necessária apenas quando as consolas são usadas por
cabo USB em vez de WiFi.

### Ficheiros

- `osc_bridge_v5.py` — o bridge propriamente dito (linha de comandos)
- `bridge_gui_v5.py` — interface gráfica do bridge (Tkinter)
- `bridge_gui_v5.exe` — versão compilada para Windows (não precisa de
  instalar Python nem dependências)

### Como correr

**Windows (mais simples):** abrir `bridge_gui_v5.exe`.

**Do código (qualquer sistema):**

```
pip install pyserial python-osc
python bridge_gui_v5.py
```

(O Tkinter já vem incluído no Python normal.)

### Como funciona

TODO: instruções ditadas pelo autor (escolher a porta COM, portas UDP
usadas, o que significa cada indicador da GUI, resolução de problemas).

---

## 🇬🇧 English

Bridge between the physical consoles (connected over **USB**) and the
MESADELUX app (which speaks **OSC/UDP**). Only needed when the consoles are
used over a USB cable instead of WiFi.

### Files

- `osc_bridge_v5.py` — the bridge itself (command line)
- `bridge_gui_v5.py` — the bridge's graphical interface (Tkinter)
- `bridge_gui_v5.exe` — compiled Windows version (no need to install
  Python or any dependencies)

### How to run

**Windows (simplest):** open `bridge_gui_v5.exe`.

**From source (any system):**

```
pip install pyserial python-osc
python bridge_gui_v5.py
```

(Tkinter ships with regular Python.)

### How it works

TODO: instructions dictated by the author (choosing the COM port, UDP
ports used, what each GUI indicator means, troubleshooting).

By Worm
