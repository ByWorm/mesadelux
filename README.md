# MESADELUX

Mesa de luz teatral em Python — bilingue (PT/EN), grátis e DiY.
*Theatrical lighting desk in Python — bilingual (PT/EN), free and DiY.*

---

## 🇵🇹 Português

**MESADELUX** é uma mesa de luz para teatro/espectáculo, feita para orçamentos
baixos e uso DiY. Corre em Windows (e a partir do código em qualquer sistema com
Python + Tkinter).

### O que faz
- Lista de memórias (cues) com tempos de entrada/saída, atrasos, AUTO e LOOP.
- Renumerador (patch) com importação **GDTF**, 8/16 bit, curvas e cores de halo.
- **16 efeitos (FX)** — manuais (passos em cadeia) e dinâmicos (paramétricos).
- Looks, Grupos e Submasters.
- Saída **sACN (E1.31)** e **Art-Net** em paralelo.
- Entrada **OSC** — controla a partir de consolas físicas ou apps OSC
  (ex.: TouchOSC). Ver o protocolo em [`DEVELOPMENT.md`](DEVELOPMENT.md).

### Como correr
- **Windows:** abre `mesadelux_v6_2_i18n.exe` (não precisa de instalar nada).
- **Do código:** `pip install sacn python-osc` e depois
  `python mesadelux_v6_2_i18n.py`.

### Idioma
A app arranca em português. Para mudar para inglês:
**Configurações → Idioma → English** e reinicia a app.
(A escolha fica guardada em `~/.mesadelux.json`.)

### Licença
[AGPL-3.0](LICENSE). Software livre: podes usar, estudar, alterar e partilhar —
desde que as alterações fiquem também livres sob a mesma licença.

> Nota: o firmware das consolas físicas **não** está incluído aqui. O protocolo
> OSC está documentado para quem quiser construir o seu próprio controlador.

---

## 🇬🇧 English

**MESADELUX** is a theatrical lighting desk built for low budgets and DiY use.
It runs on Windows (and from source on any system with Python + Tkinter).

### What it does
- Cue list with fade in/out, delays, AUTO-follow and LOOP.
- Patch with **GDTF** import, 8/16 bit, curves and halo colours.
- **16 effects (FX)** — manual (chained steps) and dynamic (parametric).
- Looks, Groups and Submasters.
- **sACN (E1.31)** and **Art-Net** output in parallel.
- **OSC** input — control it from physical consoles or OSC apps
  (e.g. TouchOSC). See the protocol in [`DEVELOPMENT.md`](DEVELOPMENT.md).

### How to run
- **Windows:** open `mesadelux_v6_2_i18n.exe` (nothing to install).
- **From source:** `pip install sacn python-osc`, then
  `python mesadelux_v6_2_i18n.py`.

### Language
The app starts in Portuguese. To switch to English:
**Settings → Language → English** and restart the app.
(The choice is stored in `~/.mesadelux.json`.)

### License
[AGPL-3.0](LICENSE). Free software: use, study, modify and share — provided
your changes stay free under the same license.

> Note: the physical consoles' firmware is **not** included here. The OSC
> protocol is documented so anyone can build their own controller.
