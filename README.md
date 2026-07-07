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
- **16 efeitos (FX)** — manuais (passos em cadeia), dinâmicos (paramétricos) e Caos.
- Looks, Grupos e Submasters.
- Saída **sACN (E1.31)** e **Art-Net** em paralelo.
- Entrada **OSC** — controla a partir de consolas físicas ou apps OSC (ex.: TouchOSC).
  Ver o protocolo no menu Ajuda → Ajuda OSC ou em [`DEVELOPMENT.md`](DEVELOPMENT.md).
- **MIDI IN/OUT por cue** — sincronização com QLab, vídeo ou qualquer
  dispositivo MIDI. Cada cue pode receber uma nota para disparar (`IN`) ou
  enviar uma nota ao executar (`OUT`), com atraso configurável.
- **Import/Export USITT ASCII** (`.asc`/`.alq`) — troca de shows com outras
  mesas (ETC Eos/Ion, Strand, Avolites…): menu Ficheiro → Importar/Exportar
  ASCII. Viajam as cues (tempos, texto, AUTO, saltos, níveis), o patch de
  intensidade, grupos e submasters; o formato nativo `.ldsk` continua a
  guardar tudo (MIDI, FX, looks, alcunhas, curvas…).

### Como correr
- **Windows:** abre `mesadelux_v6_3_2.exe` (não precisa de instalar nada).
- **Do código:** `pip install sacn python-osc` e depois
  `python mesadelux_v6_3_2.py`.
- **MIDI (opcional):** `pip install mido python-rtmidi`

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
- **16 effects (FX)** — manual (chained steps), dynamic (parametric) and Chaos.
- Looks, Groups and Submasters.
- **sACN (E1.31)** and **Art-Net** output in parallel.
- **OSC** input — control it from physical consoles or OSC apps (e.g. TouchOSC).
  See the protocol in the Help menu → OSC Help or in [`DEVELOPMENT.md`](DEVELOPMENT.md).
- **MIDI IN/OUT per cue** — sync with QLab, video or any MIDI device. Each cue
  can receive a note to trigger it (`IN`) or send a note when it runs (`OUT`),
  with configurable delay.
- **USITT ASCII Import/Export** (`.asc`/`.alq`) — exchange shows with other
  desks (ETC Eos/Ion, Strand, Avolites…): File menu → Import/Export ASCII.
  Cues (times, text, AUTO, jumps, levels), intensity patch, groups and
  submasters travel; the native `.ldsk` format still stores everything
  (MIDI, FX, looks, nicknames, curves…).

### How to run
- **Windows:** open `mesadelux_v6_3_2.exe` (nothing to install).
- **From source:** `pip install sacn python-osc`, then
  `python mesadelux_v6_3_2.py`.
- **MIDI (optional):** `pip install mido python-rtmidi`

### Language
The app starts in Portuguese. To switch to English:
**Settings → Language → English** and restart the app.
(The choice is stored in `~/.mesadelux.json`.)

### License
[AGPL-3.0](LICENSE). Free software: use, study, modify and share — provided
your changes stay free under the same license.

> Note: the physical consoles' firmware is **not** included here. The OSC
> protocol is documented so anyone can build their own controller.
