# Ligações de hardware / Hardware wiring

## 🇵🇹 Português

Lista de componentes e ligações das consolas físicas da MESADELUX.
Os pinos abaixo vêm directamente do firmware (`firmware/…/main.py`).

### Consola 1 (principal)

#### Componentes

- 1× Raspberry Pi **Pico W**
- 2× display OLED **SSD1306** 128×64, I2C (TODO: tamanho/modelo dos módulos)
- 2× encoder rotativo com botão (TODO: modelo, p.ex. EC11)
- 2× fader/potenciómetro linear para os submasters (TODO: valor e modelo)
- Alimentação por USB
- TODO: outros (caixa, botões extra, resistências se existirem)

#### Ligações (pinout)

| Pino do Pico | Componente | Notas |
|---|---|---|
| GP4 (SDA) / GP5 (SCL) | OLED 1 (esquerdo) | I2C0, 400 kHz |
| GP6 (SDA) / GP7 (SCL) | OLED 2 (direito) | I2C1, 400 kHz |
| GP10 / GP11 | Encoder esquerdo (CLK/DT) | pull-up interno |
| GP12 | Botão do encoder esquerdo | pull-up interno, liga ao GND |
| GP13 / GP14 | Encoder direito (CLK/DT) | pull-up interno |
| GP15 | Botão do encoder direito | pull-up interno, liga ao GND |
| GP26 (ADC0) | Fader 1 — submaster A | extremos a GND e 3V3 |
| GP27 (ADC1) | Fader 2 — submaster B | extremos a GND e 3V3 |

### Consola 2 (auxiliar)

#### Componentes

- 1× Raspberry Pi **Pico W**
- 1× encoder rotativo com botão (TODO: modelo)
- 4× botão de pressão (TODO: modelo)
- Alimentação por USB (sem display; usa o LED da placa como indicador)

#### Ligações (pinout)

| Pino do Pico | Componente | Notas |
|---|---|---|
| GP6 / GP7 | Encoder (CLK/DT) | pull-up interno |
| GP8 | Botão do encoder | pull-up interno, liga ao GND |
| GP16 | Botão 1 (GO) | pull-up interno, liga ao GND |
| GP19 | Botão 2 (PAUSE) | pull-up interno, liga ao GND |
| GP22 | Botão 3 (GOBACK) | pull-up interno, liga ao GND |
| GP28 | Botão 4 (RELEASE; premido no arranque alterna USB/WiFi) | pull-up interno, liga ao GND |
| LED da placa | Indicador de estado | — |

> Todos os botões e encoders usam os pull-ups internos do Pico: cada
> contacto liga o pino ao **GND** (não é precisa nenhuma resistência
> externa).

### Esquema

TODO: fotografia ou esquema das ligações.

---

## 🇬🇧 English

Parts list and wiring of the MESADELUX physical consoles.
The pins below come straight from the firmware (`firmware/…/main.py`).

### Console 1 (main)

#### Parts

- 1× Raspberry Pi **Pico W**
- 2× **SSD1306** 128×64 OLED display, I2C (TODO: module size/model)
- 2× rotary encoder with push button (TODO: model, e.g. EC11)
- 2× linear fader/potentiometer for the submasters (TODO: value and model)
- Powered over USB
- TODO: others (enclosure, extra buttons, resistors if any)

#### Wiring (pinout)

| Pico pin | Part | Notes |
|---|---|---|
| GP4 (SDA) / GP5 (SCL) | OLED 1 (left) | I2C0, 400 kHz |
| GP6 (SDA) / GP7 (SCL) | OLED 2 (right) | I2C1, 400 kHz |
| GP10 / GP11 | Left encoder (CLK/DT) | internal pull-up |
| GP12 | Left encoder button | internal pull-up, wired to GND |
| GP13 / GP14 | Right encoder (CLK/DT) | internal pull-up |
| GP15 | Right encoder button | internal pull-up, wired to GND |
| GP26 (ADC0) | Fader 1 — submaster A | ends to GND and 3V3 |
| GP27 (ADC1) | Fader 2 — submaster B | ends to GND and 3V3 |

### Console 2 (auxiliary)

#### Parts

- 1× Raspberry Pi **Pico W**
- 1× rotary encoder with push button (TODO: model)
- 4× push button (TODO: model)
- Powered over USB (no display; uses the on-board LED as indicator)

#### Wiring (pinout)

| Pico pin | Part | Notes |
|---|---|---|
| GP6 / GP7 | Encoder (CLK/DT) | internal pull-up |
| GP8 | Encoder button | internal pull-up, wired to GND |
| GP16 | Button 1 (GO) | internal pull-up, wired to GND |
| GP19 | Button 2 (PAUSE) | internal pull-up, wired to GND |
| GP22 | Button 3 (GOBACK) | internal pull-up, wired to GND |
| GP28 | Button 4 (RELEASE; held at boot toggles USB/WiFi) | internal pull-up, wired to GND |
| On-board LED | Status indicator | — |

> All buttons and encoders use the Pico's internal pull-ups: each contact
> connects the pin to **GND** (no external resistors needed).

### Schematic

TODO: photo or wiring diagram.

By Worm
