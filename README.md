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
- **Layouts** (v6.5) — vista de células estilo GrandMA, com páginas
  (ex.: MÁQUINAS / LEDS / PAR64) e teclas de atributo (ZOOM, RED,
  STROBE…) para chamar cada atributo dos aparelhos. Editável ao vivo.
- Saída **sACN (E1.31)** e **Art-Net** em paralelo.
- Saída **USB-DMX** — adaptadores baratos tipo "Open DMX" (FTDI; testado
  com o DSD TECH SH-RS09B), em paralelo com o sACN e o Art-Net. Liga o
  adaptador, menu **Configurações → USB-DMX**, e sai DMX directo pelo
  cabo — sem nó de rede nem hardware caro.
- Entrada **OSC** — controla a partir de consolas físicas ou apps OSC (ex.: TouchOSC).
  Ver o protocolo no menu Ajuda → Ajuda OSC ou em [`DEVELOPMENT.md`](DEVELOPMENT.md).
- **MIDI IN/OUT por cue** — sincronização com QLab, vídeo ou qualquer
  dispositivo MIDI. Cada cue pode receber uma nota para disparar (`IN`) ou
  enviar uma nota ao executar (`OUT`), com atraso configurável.
- **Import/Export USITT ASCII** (`.asc`/`.alq`) — troca de shows com outras
  mesas (ETC Eos/Ion, Strand, Avolites…): menu Ficheiro → Importar/Exportar
  ASCII. Viajam as cues (tempos, texto, AUTO, saltos, níveis, partes), o
  patch de intensidade, grupos e submasters; o formato nativo `.ldsk`
  continua a guardar tudo (MIDI, FX, looks, alcunhas, curvas…).
- **PARTES** — até 8 divisões por memória, cada uma com os seus canais,
  tempos de entrada/saída e atrasos próprios, e FX próprio: vários eventos
  em simultâneo num só GO (ex.: um efeito a entrar em 5 s enquanto o
  ciclorama muda em 30 s). Tecla PARTE: seleccionar canais → PARTE → menu.
  Compatível com o `PART` do USITT ASCII (validado com ETC Eos).
- **DMX-In (escuta sACN)** — escuta o sACN de outra mesa (ETC Eos, GrandMA…,
  mesmo no mesmo computador) e os valores recebidos entram AO VIVO no
  programador (a rosa), traduzidos pelo renumerador. Grava-se com
  Comprar/Actualizar como qualquer look — captura de espectáculos de outra
  mesa, memória a memória. Configurações → DMX-In (universos, interface,
  indicador de recepção). Só escuta: nada é gravado sem ordem.

### O que inclui este repositório
- **raiz** — a app MESADELUX (`mesadelux_v6_5_0.py` / `.exe`; `dmx_usb.py`
  é o módulo de saída USB-DMX)
- [`firmware/`](firmware) — firmware MicroPython das duas consolas físicas
  (Raspberry Pi Pico W)
- [`bridge/`](bridge) — ponte USB/OSC entre as consolas e a app, com GUI
- [`hardware/`](hardware) — componentes e ligações das consolas
- [`touchosc/`](touchosc) — layout TouchOSC de exemplo (telemóvel/tablet)
- [`exemplos/`](exemplos) — ficheiros de show de demonstração

### Como correr
- **Windows:** abre `mesadelux_v6_5_0.exe` (não precisa de instalar nada).
- **Do código:** `pip install sacn python-osc` e depois
  `python mesadelux_v6_5_0.py`.
- **MIDI (opcional):** `pip install mido python-rtmidi`
- **USB-DMX (opcional):** `pip install pyserial` (com o `dmx_usb.py` ao
  lado da app)

### Idioma
A app arranca em português. Para mudar para inglês:
**Configurações → Idioma → English** e reinicia a app.
(A escolha fica guardada em `~/.mesadelux.json`.)

### Licença
[AGPL-3.0](LICENSE). Software livre: podes usar, estudar, alterar e partilhar —
desde que as alterações fiquem também livres sob a mesma licença.

> O firmware das consolas físicas está na pasta [`firmware/`](firmware) e o
> protocolo OSC está documentado — qualquer pessoa pode construir o seu
> próprio controlador. Uso por conta e risco: isto controla equipamento de
> palco real.

---

## 🇬🇧 English

**MESADELUX** is a theatrical lighting desk built for low budgets and DiY use.
It runs on Windows (and from source on any system with Python + Tkinter).

### What it does
- Cue list with fade in/out, delays, AUTO-follow and LOOP.
- Patch with **GDTF** import, 8/16 bit, curves and halo colours.
- **16 effects (FX)** — manual (chained steps), dynamic (parametric) and Chaos.
- Looks, Groups and Submasters.
- **Layouts** (v6.5) — GrandMA-style cell view, with pages (e.g.
  MOVERS / LEDS / PAR64) and attribute keys (ZOOM, RED, STROBE…) to
  call each fixture attribute. Editable live.
- **sACN (E1.31)** and **Art-Net** output in parallel.
- **USB-DMX** output — cheap "Open DMX"-style adapters (FTDI; tested with
  the DSD TECH SH-RS09B), in parallel with sACN and Art-Net. Plug the
  adapter in, menu **Settings → USB-DMX**, and DMX comes straight out of
  the cable — no network node or expensive hardware needed.
- **OSC** input — control it from physical consoles or OSC apps (e.g. TouchOSC).
  See the protocol in the Help menu → OSC Help or in [`DEVELOPMENT.md`](DEVELOPMENT.md).
- **MIDI IN/OUT per cue** — sync with QLab, video or any MIDI device. Each cue
  can receive a note to trigger it (`IN`) or send a note when it runs (`OUT`),
  with configurable delay.
- **USITT ASCII Import/Export** (`.asc`/`.alq`) — exchange shows with other
  desks (ETC Eos/Ion, Strand, Avolites…): File menu → Import/Export ASCII.
  Cues (times, text, AUTO, jumps, levels, parts), intensity patch, groups
  and submasters travel; the native `.ldsk` format still stores everything
  (MIDI, FX, looks, nicknames, curves…).
- **PARTS** — up to 8 divisions per cue, each with its own channels,
  in/out times and delays, and its own FX: several events at once on a
  single GO (e.g. an effect fading in over 5 s while the cyclorama
  changes over 30 s). PART key: select channels → PART → menu.
  Compatible with USITT ASCII `PART` (validated against ETC Eos).
- **DMX-In (sACN listen)** — listens to sACN from another desk (ETC Eos,
  GrandMA…, even on the same computer) and the received values feed the
  programmer LIVE (in pink), translated through the patch. Record with
  Take/Update like any look — capture shows from another desk, cue by
  cue. Settings → DMX-In (universes, interface, reception indicator).
  Listen only: nothing is recorded without your command.

### What's in this repository
- **root** — the MESADELUX app (`mesadelux_v6_5_0.py` / `.exe`;
  `dmx_usb.py` is the USB-DMX output module)
- [`firmware/`](firmware) — MicroPython firmware for the two physical
  consoles (Raspberry Pi Pico W)
- [`bridge/`](bridge) — USB/OSC bridge between the consoles and the app,
  with a GUI
- [`hardware/`](hardware) — console parts list and wiring
- [`touchosc/`](touchosc) — sample TouchOSC layout (phone/tablet)
- [`exemplos/`](exemplos) — demo show files

### How to run
- **Windows:** open `mesadelux_v6_5_0.exe` (nothing to install).
- **From source:** `pip install sacn python-osc`, then
  `python mesadelux_v6_5_0.py`.
- **MIDI (optional):** `pip install mido python-rtmidi`
- **USB-DMX (optional):** `pip install pyserial` (with `dmx_usb.py` next
  to the app)

### Language
The app starts in Portuguese. To switch to English:
**Settings → Language → English** and restart the app.
(The choice is stored in `~/.mesadelux.json`.)

### License
[AGPL-3.0](LICENSE). Free software: use, study, modify and share — provided
your changes stay free under the same license.

> The physical consoles' firmware lives in [`firmware/`](firmware) and the
> OSC protocol is documented — anyone can build their own controller. Use
> at your own risk: this drives real stage equipment.
