# Layout TouchOSC

Layout de exemplo para controlar a MESADELUX a partir de um telemóvel ou
tablet com a app [TouchOSC](https://hexler.net/touchosc) (versão Mk1).

## Ficheiro

- `tchmesadelux_osc2.touchosc` — layout com:
  - 2 faders → `/submaster/1` e `/submaster/2`
  - botões GO / GOBACK / PAUSE / LOOPBREAK → `/go`, `/back`, `/pause`, `/soltar`
  - toggles de efeitos → `/fx/1/toggle` … `/fx/4/toggle`

## Como usar

1. Instalar a app TouchOSC (Mk1) no telemóvel/tablet.
2. Transferir o layout para a app (pelo TouchOSC Editor ou pela função de
   sincronização da app).
3. Nas definições de ligação do TouchOSC, apontar para o **IP do computador
   onde corre a MESADELUX**, porta OSC da app.
4. O telemóvel e o computador têm de estar na **mesma rede WiFi**.

TODO: instruções detalhadas ditadas pelo autor (portas exactas, protocolo
OSC completo — ver também o menu Ajuda → Ajuda OSC na app).

By Worm
