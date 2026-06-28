# MESADELUX — Notas de Desenvolvimento

## Ficheiros / versões
- `mesadelux_v6_1.py` — versão estável PT, **intacta**. Não mexer.
- `mesadelux_v6_2_i18n.py` — versão de trabalho **bilingue (fonte única)**.
  É aqui que o desenvolvimento continua. O português é a língua canónica;
  o inglês é a tradução.

> Decisão (2026-06-18): abandonámos a ideia de um ficheiro `_ENG.py`
> separado. Manter duas cópias de ~7500 linhas divergiria e criaria bugs
> só numa versão. Em vez disso, **um só ficheiro** com as strings de UI a
> passar por `T()`, e o idioma escolhido em runtime/config.

## Regra de ouro do i18n
1. **Toda a string de UI nova passa por `T("dominio.chave")`** — nunca
   texto fixo nos widgets. Acrescenta a chave nos DOIS idiomas (`pt` e
   `en`) no dicionário `STRINGS`.
2. **NÃO entram no dicionário:** endereços OSC (`/go`, `/soltar`,
   `/rec/comprar`, `/channel/.../curva`…), atributos técnicos (PAN, TILT,
   DIM, ZOOM, GDTF, footprint→«pegada» já fixado), nomes de protocolo.
   São contrato com o firmware/normas e ficam como estão.
3. **Idioma = preferência do utilizador**, guardada em `~/.mesadelux.json`
   (`load_app_config`/`save_app_config`), **não** no `.ldsk`. Abrir o show
   de outra pessoa não deve mudar a tua língua.
4. Comentários e docstrings: o **PT continua a língua de trabalho** no
   código; o inglês para terceiros vive no README/docs do GitHub.

## Fora do âmbito da tradução (por agora)
- **Firmware/OLED das consolas físicas (Pico W)**: fica PT-only por agora
  (decisão do autor 2026-06-18). A app só envia tokens por OSC (níveis,
  curva `ligado`, nomes, alcunha…); o "L" do canal ligado no OLED é
  desenhado pelo firmware, não pela app. Na app já é `grid.on_letter`
  (PT "L" / EN "O"). Rever só se/quando se traduzir o firmware.

## Alterações v6.2 (2026-06-28, em desenvolvimento — re-enviar ao GitHub)
- **GDTF saiu da página principal**: importa-se agora DENTRO do «Repetir
  Aparelho» (Renumerador → Repetir Aparelho → botão «Importar GDTF…»).
  Botão do GDTFDialog passou a «Usar esta pegada». `_open_gdtf` removido.
- **FX em 3 modos**: Manual / Dinâmico / **Caos**.
  - Partilhados: Curva, Direcção, Ataque, Retirada, BPM, V.alto, V.baixo.
  - Só Dinâmico: Blocos, Carroagem, Grupos, Cruzamento.
  - Só Caos: Caos(random), Carroagem, Repetir, **Quantidade** (novo).
  - **Tamanho do caos (caos_size) REMOVIDO da UI** (não fazia nada).
  - **Quantidade** (`quant_min`/`quant_max`): nº de canais sorteados por
    combinação, aleatório entre mín e máx (min=max=fixo; limitado aos
    seleccionados). Dois sub-comportamentos no Caos:
      · `quant_max>0` → SELECÇÃO (sorteia k canais).
      · `quant 0/0`   → CINTILAÇÃO: Carroagem (largura da banda) + Caos
        (random) recuperam o efeito antigo de cintilação.
  - Motor: `mode=='caos'`; selecção só se quant_max>0; no Caos força-se
    G=0/sem blocos/sem cruzamento; no Dinâmico anulam-se caos/random.
  - `.ldsk`: shows antigos com `mode:'dinamico'` continuam a abrir.

## Glossário EN dos botões (decisão do autor 2026-06-18)
O autor escolheu termos próprios para os botões (não tradução literal):

| PT | EN |
|---|---|
| Comprar | **TAKE** |
| Saltar / Salta (cuelist) | **LOOP** |
| Soltar (transporte) | **LOOPBREAK** |
| Liberta (botão, solta todos os canais) | **RELEASE** (termo ETC) |
| Liberta (menu/Esc, liberta o programador) | **Release** |
| Limpa (limpa a selecção) | **CLEAR** |
| Gravar (memória/cue) | **BACKUP** |
| Retrato | **Look** (estado de luz; não Snapshot/Preset/Palette) |
| Escuro / Black Out | **B.O.** |
| Todos | **ALL** |
| Máximo | **FULL** |
| Zero | **Zero** |
| Recua | **GOBACK** |
| Vai | **GO** |
| Ir Para | **GOTO** |
| Actualização | **UPDATE** |
| Apagar | **DELETE** |
| Pausa / Retoma | **PAUSE / RESUME** |
| (menu) Guardar / Guardar como | **Save / Save As** |

Nota: ETC tem o comando **Sneak** (mover canais p/ um valor com fade /
libertar suavemente) — sem equivalente PT fixado ainda («esgueirar»?). Não
está na app; registado só para referência futura.

Restantes botões: termo inglês habitual de mesa de luz. Tradução só nos
RÓTULOS; endereços OSC e tokens internos não mudam.

## Etapas (plano)
- **Etapa 0 (feita):** andaime i18n — `LANG`, `STRINGS`, `T()`,
  `load/save_app_config`, `set_lang`, separador «Idioma» nas Configurações.
  Comportamento inalterado; arranca em PT.
- **Etapa 1 (FEITA):** todas as strings de UI migradas para `T()` —
  parsers, todos os diálogos, menu, botões, transporte, editor FX
  (manual+dinâmico), cores/curvas, e ~60 mensagens internas. 313 chaves
  PT/EN com paridade total. Só ficam literais técnicos propositados
  (sACN/Art-Net/OSC, Multicast/Broadcast, ON/OFF, `sino`/`PWM`).
- **Etapa 2 (FEITA):** coluna `en` revista (paridade + placeholders OK).
- **Etapa 2.5:** página de Ajuda OSC in-app (`osc_reference_text()` via `T()`).
- **Etapa 3:** docs GitHub (README bilingue, LICENSE AGPL-3.0, CONTRIBUTING).

## Referência do protocolo OSC (fonte-de-verdade)
Extraída do código (`_osc_apply` = entrada, `_send_console` = saída).
Os endereços são fixos (contrato com o firmware das consolas). `N` é 1-based.

### Recebe (consola → app)
Sem args: `/go` `/back` `/pause` `/blackout` `/clear` `/soltar`
`/rec/comprar` `/rec/actualiza` `/rec/guarda` `/rec/cancelar`

Com args:
- `/channel/{N}/level` `i`(0-255) ou `f` (≤1.0 normalizado; >1.0 = 0-255)
- `/intensity` `{ch:i} {lvl:f}`
- `/channel/select` `{ch}`
- `/submaster/{N}` `f` (≤1.0→%; senão 0-100)
- `/group/{N}/level` `f`
- `/release_all` `f` (fade IGNORADO — usa o tempo do menu)
- `/cue/go` · `/cue/back`
- `/cue/fade_in` `f` (s) · `/cue/fade_out` `f` (s)
- `/cue/state/request`

### Envia (app → consola, feedback)
- `/channel/{N}/name` `s` (≤6) · `/channel/{N}/alcunha` `i`
- `/channel/{N}/curva` `s` · `/channel/{N}/level` `i` (0-255)
- `/channel/patched` `s` (csv "1,2,5,10")
- `/cue/state` `s s f f` (num, label, fade_in, fade_out)
- `/cue/state/{key}` `f`

> Nota de publicação: documentar o protocolo NÃO revela o hardware das
> consolas. Permite a terceiros construírem o seu próprio controlador OSC
> (TouchOSC, etc.) — reforça o objectivo DiY/baixo orçamento.
