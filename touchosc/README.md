# Layout TouchOSC / TouchOSC layout

## 🇵🇹 Português

Layout de exemplo para controlar a MESADELUX a partir de um telemóvel ou
tablet com a app [TouchOSC](https://hexler.net/touchosc) (versão Mk1).

### Ficheiro

- `tchmesadelux_osc2.touchosc` — o layout, com **duas páginas** (separadores
  no topo): PLAYBACK e EDITOR.

### Página 1 — PLAYBACK (apoio à reprodução do espectáculo)

![Página PLAYBACK](pagina_playback.jpg)

- Botões de transporte: **GOBACK / GO / PAUSE / LOOPBREAK**
  (`/back`, `/go`, `/pause`, `/soltar`)
- Grelha **FX** — 16 toggles para ligar/desligar os 16 efeitos
  (`/fx/1/toggle` … `/fx/16/toggle`)
- Faders **SUB1** e **SUB2** — submasters (`/submaster/1`, `/submaster/2`)

### Página 2 — EDITOR (gravação e edição de memórias)

![Página EDITOR](pagina_editor.jpg)

- **TAKE / UPDATE / BACKUP** — comprar (gravar memória nova), actualizar a
  memória actual e cópia de segurança do show
- **<<< / >>>** — navegar na lista de memórias
- **RELEASE / CLEAR** — libertar a saída / limpar o programador
- Pré-valores **0% / 25% / 50% / 75% / 100%** e ajuste fino **+5 / −5**
  para os canais seleccionados
- **GROUPS** — 16 teclas de grupos de canais
- **LOOKS** — 16 teclas de looks (retratos)

### Como usar

1. Instalar a app TouchOSC (Mk1) no telemóvel/tablet.
2. Transferir o layout para a app (pelo TouchOSC Editor ou pela função de
   sincronização da app).
3. Nas definições de ligação do TouchOSC, apontar para o **IP do computador
   onde corre a MESADELUX**, porta OSC da app.
4. O telemóvel e o computador têm de estar na **mesma rede WiFi**.

TODO: instruções detalhadas ditadas pelo autor (portas exactas, protocolo
OSC completo — ver também o menu Ajuda → Ajuda OSC na app).

---

## 🇬🇧 English

Sample layout to control MESADELUX from a phone or tablet running the
[TouchOSC](https://hexler.net/touchosc) app (Mk1 version).

### File

- `tchmesadelux_osc2.touchosc` — the layout, with **two pages** (tabs at
  the top): PLAYBACK and EDITOR.

### Page 1 — PLAYBACK (show playback support)

![PLAYBACK page](pagina_playback.jpg)

- Transport buttons: **GOBACK / GO / PAUSE / LOOPBREAK**
  (`/back`, `/go`, `/pause`, `/soltar`)
- **FX** grid — 16 toggles to switch the 16 effects on/off
  (`/fx/1/toggle` … `/fx/16/toggle`)
- **SUB1** and **SUB2** faders — submasters (`/submaster/1`, `/submaster/2`)

### Page 2 — EDITOR (recording and editing cues)

![EDITOR page](pagina_editor.jpg)

- **TAKE / UPDATE / BACKUP** — record a new cue, update the current cue,
  and back up the show
- **<<< / >>>** — navigate the cue list
- **RELEASE / CLEAR** — release the output / clear the programmer
- Presets **0% / 25% / 50% / 75% / 100%** and fine adjust **+5 / −5**
  for the selected channels
- **GROUPS** — 16 channel-group keys
- **LOOKS** — 16 look keys

### How to use

1. Install the TouchOSC app (Mk1) on your phone/tablet.
2. Transfer the layout to the app (via the TouchOSC Editor or the app's
   sync function).
3. In the TouchOSC connection settings, point to the **IP of the computer
   running MESADELUX**, using the app's OSC port.
4. The phone and the computer must be on the **same WiFi network**.

TODO: detailed instructions dictated by the author (exact ports, full OSC
protocol — see also the Help menu → OSC Help in the app).

By Worm
