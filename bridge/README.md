# Bridge USB/OSC

Ponte entre as consolas físicas (ligadas por **USB**) e a app MESADELUX
(que fala **OSC/UDP**). Necessária apenas quando as consolas são usadas por
cabo USB em vez de WiFi.

## Ficheiros

- `osc_bridge_v5.py` — o bridge propriamente dito (linha de comandos)
- `bridge_gui_v5.py` — interface gráfica do bridge (Tkinter)
- `bridge_gui_v5.exe` — versão compilada para Windows (não precisa de
  instalar Python nem dependências)

## Como correr

**Windows (mais simples):** abrir `bridge_gui_v5.exe`.

**Do código (qualquer sistema):**

```
pip install pyserial python-osc
python bridge_gui_v5.py
```

(O Tkinter já vem incluído no Python normal.)

## Como funciona

TODO: instruções ditadas pelo autor (escolher a porta COM, portas UDP
usadas, o que significa cada indicador da GUI, resolução de problemas).

By Worm
