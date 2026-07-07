# MESADELUX — Notas de Desenvolvimento

## Ficheiros / versões
- `mesadelux_v6_2_i18n.py` — versão estável bilingue (PT/EN). Referência.
- `mesadelux_v6_3.py` — versão estável **com suporte MIDI + Ajuda OSC**.
- `mesadelux_v6_3_2.py` — versão de trabalho **com Import/Export USITT
  ASCII**. É aqui que o desenvolvimento continua. O português é a língua
  canónica; o inglês é a tradução.

> Decisão (2026-06-18): abandonámos a ideia de um ficheiro `_ENG.py`
> separado. Manter duas cópias de ~9000 linhas divergiria e criaria bugs
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

## Alterações v6.2 (2026-06-28)
- **GDTF saiu da página principal**: importa-se agora DENTRO do «Repetir
  Aparelho» (Renumerador → Repetir Aparelho → botão «Importar GDTF…»).
  Botão do GDTFDialog passou a «Usar esta pegada». `_open_gdtf` removido.
- **FX em 3 modos**: Manual / Dinâmico / **Caos**.
  - Partilhados: Curva, Direcção, Ataque, Retirada, BPM, V.alto, V.baixo.
  - Só Dinâmico: Blocos, Carroagem, Grupos, Cruzamento.
  - Só Caos: Caos(random), Carroagem, Repetir, **Quantidade** (novo).
  - **Quantidade** (`quant_min`/`quant_max`): nº de canais sorteados por
    combinação, aleatório entre mín e máx. Dois sub-comportamentos:
      · `quant_max>0` → SELECÇÃO (sorteia k canais).
      · `quant 0/0`   → CINTILAÇÃO: Carroagem + Caos recuperam o efeito antigo.
  - `.ldsk`: shows antigos com `mode:'dinamico'` continuam a abrir.

## Alterações v6.3 (2026-07-02)
- **Suporte MIDI IN/OUT por cue**: cada cue pode ter uma nota MIDI de
  entrada (trigger) e de saída (feedback). Seleccionáveis via diálogo
  na cue list.
- **Separador MIDI nas Configurações**: selecção de portas MIDI IN/OUT,
  com botão de refresh e indicador de estado.
- **Ajuda OSC in-app (Etapa 2.5)**: separador «Ajuda OSC» / «OSC Help»
  nas Configurações com referência completa do protocolo em PT e EN
  (`osc_reference_text()` via `T('osc_help.text')`).
- **Fechar MIDI no quit**: `_close_midi_in()` e `_close_midi_out()`
  chamados em `_quit()` antes de destruir a janela.

## Alterações v6.3.2 (2026-07-06) — Import/Export USITT ASCII
Porta de portabilidade para outras mesas (ETC Eos/Ion, Strand, Avolites…)
via **USITT ASCII 3.0**. Spec do autor em `MESADELUX_USITT_ASCII_SPEC.md`;
plano de etapas em `MESADELUX_V632_PLANO_ASCII.md`.

- O `.ldsk` continua o ÚNICO formato de gravação. O ASCII é só transporte:
  menu **Ficheiro → Importar ASCII… / Exportar ASCII…**. Sem dependências
  novas (parser de texto stdlib).
- Código: secção `# USITT ASCII (v6.3.2)` (entre GDTF e PATCH) com
  `export_ascii(show_dict, filepath)` e `import_ascii(filepath)` →
  `(show_dict, relatório)`. Falam os dicts de `_show_data()`/`_load_data()`
  para reaproveitar a validação de load.
- **O que viaja:** cues (número decimal, UP/DOWN com delay no 2.º campo,
  TEXT, FOLLOWON, LINK, níveis 0-255↔0-100 %), PATCH de intensidade
  (`canal<dimmer@100`, dimmer = (universo-1)·512+endereço), GROUP (canais
  a 100) e SUB. **O que NÃO viaja:** MIDI por cue, FX, looks, alcunhas,
  curvas, halos… (a UI avisa antes de exportar).
- **Sintaxe validada contra o doc oficial USITT 3.0** (2026-07-06, depois
  do teste real numa Eos que rejeitava patch/níveis/tempos): NÃO existe
  `TIME` (é sempre UP/DOWN), NÃO existe `FULL`/`AT` (níveis = percentagem
  inteira 0-100 ou hex `Hnn`; CHAN é `canal@nível`), tempos podem ser
  `[hh:][mm:]ss[.décimo]` (1 dígito de décimos no máximo) e as vírgulas
  são delimitadores válidos. O exemplo da spec original estava errado
  nesses pontos.
- **Decisões fechadas (2026-07-06):** CHAN usa o nº interno 1..N (alcunhas
  não viajam); LOOP→LINK exportado SEM contagem (import: LINK → salto
  eterno, `salta_count=0`); import de SUB: só os 2 primeiros (o resto é
  contado no relatório); a memória ZERO nunca se exporta (o import ganha a
  sua própria via `_ensure_zero`).
- **Import robusto (nunca rebenta):** aceita `.asc` e `.alq` (mesmo
  parser); `!` = comentário; keywords desconhecidas, `$$fabricante`,
  PATCH página≠1, GROUP>20, SUB>2 → ignorados e CONTADOS (relatório com
  exemplos). CHAN standard (`1@100 2@75`) + tolerâncias (`1 AT FULL`,
  FL/FULL, TIME); níveis percentagem / hex `Hnn`/`Hnnnn` (Eos escreve
  HFF); tempos com `:`; `UP fade delay`; vírgulas como delimitadores;
  linhas de continuação de CHAN/PATCH (registo vai até à keyword
  seguinte); PART funde na cue; leitura latin-1 (não engasga com acentos
  nem binário).
- **FOLLOWON (AUTO) — dois estilos, escolha do utilizador (2026-07-07):**
  a Eos/USITT conta o FOLLOWON desde o INÍCIO da cue precedente (e o
  atributo escreve-se NELA); a MesaDeLux/grandMA conta do FIM da anterior
  (e o atributo vive na cue que entra). O export pergunta o estilo:
  «eos» = compensado (FOLLOWON = tempo_total(precedente)+follow, escrito
  na precedente, LINK-ciente — o alvo do salto conta como «seguinte»);
  «directo» = valor tal e qual na própria cue (grandMA 1/2). O import
  auto-detecta (marcador `! MESADELUX FOLLOW`, MANUFACTURER ETC→eos,
  ByWorm/MesaDeLux→directo) e só pergunta na dúvida. tempo_total =
  max(delay_in+fade_in, delay_out+fade_out); compensações negativas
  (Eos dispara a meio do fade) ficam a 0 + nota no relatório.
- **Extensões Eos entendidas no import (2026-07-07, validado com exports
  reais):** `$$LoopNum n` (contagem do LINK ↔ salta_count — SÓ no
  import; o export é USITT puro); `$$Follow` (=FOLLOWON); `$$Hang` (AUTO
  contado do FIM — entra directo); `$$ChanMove` (níveis COM os movimentos
  a zero, que as linhas `Chan` da Eos omitem — essencial p/ tracking);
  registos primários `$Xyz` ($Curve, $Effect, $CueList…) fecham o bloco
  actual (senão o `Text` deles contaminava o label da última cue);
  `Cue n página` aceite.
- **Cabeçalho — LIÇÃO dos testes reais na Eos (2026-07-07):** NUNCA
  declarar `CONSOLE Eos` / `$$Format 3.10` — a Eos detecta «export da
  Eos» e muda para o modo de leitura NATIVO (espera `$CueList`/`$Patch`/
  `$Personality`), deitando fora TUDO, patch incluído. O cabeçalho é
  sempre `MANUFACTURER ByWorm` / `CONSOLE MesaDeLux v6.3.2` + comentário
  `! Exportado pela MesaDeLux v6.3.2 (By Worm)`; nesse modo genérico a
  Eos importa patch, cues, níveis e tempos. Ordem dos registos na cue =
  a da própria Eos (CHAN primeiro; FOLLOWON; LINK a fechar).
- **DECISÃO FINAL sobre loops (2026-07-07, do autor):** o export escreve
  **USITT puro, sem `$$` nenhum**. O `$$LoopNum` foi testado na Eos nas
  duas formas (antes e depois das CHAN, cabeçalho ByWorm) e ela ignora-o
  vindo de terceiros — a contagem de voltas do LOOP põe-se À MÃO na mesa
  de destino (manobra pontual; o LINK em si viaja). O `$$Follow`
  duplicado também saiu. Os automatismos (FOLLOWON) esses ficam, com o
  cálculo e as opções dos dois estilos, porque funcionam bem e seriam o
  trabalho repetitivo. No IMPORT continua-se a ler as extensões Eos
  ($$LoopNum, $$Follow, $$Hang, $$ChanMove) — ler não custa e recupera
  dados.
- **Round-trip:** o export grava `! MESADELUX MODE tracking|cue_only` e
  `! MESADELUX FOLLOW eos|directo` em comentário; o import lê-os (outras
  mesas ignoram; o marcador tem prioridade sobre o MANUFACTURER na
  detecção). Exporta 7-bit ASCII (acentos transliterados via NFKD),
  linhas ≤75 chars, CRLF.
- i18n: chaves `menu.import_ascii`, `menu.export_ascii` e `ascii.*`
  (PT/EN).

## Alterações v6.3.3 (2026-07-07) — PARTES (divisões da memória)
Plano completo em `MESADELUX_V633_PLANO_PARTS.md`. Ficheiro
`mesadelux_v6_3_3.py` (v6.3.2 intacta).

- **Modelo:** até **8 partes** por memória; a **parte 1 é a própria
  memória** (nada de novo se guarda); as 2-8 vivem em `cue['parts']`
  (`{'2': {channels, fade_in/out, delay_in/out, fx, label}}`). As partes
  são SÓ metadados de TEMPO — o estado final da cue não muda
  (tracking/cue_only/GOTO intactos; `.ldsk` compatível p/ trás: versões
  antigas ignoram o campo). Regra USITT 10.5: um canal, uma parte
  (`normaliza_parts()` valida tudo o que vem de ficheiro).
- **Motor:** `fade_dur[ch]`/`fade_del[ch]` preenchidos no GO segundo a
  parte de cada canal (direcção decide IN/OUT); `_tick` lê dos arrays;
  fim da transição = `fade_total` = max(atraso+fade) de TODAS as partes
  (o AUTO arma aí; barra de progresso idem). LIBERTA/LIMPA ignoram as
  partes (tempo único).
- **FX por parte:** cada parte pode lançar 1 FX (mesmo formato da coluna
  FX, `{'num','fade'}`); a paridade de marcas do tracking conta as marcas
  das partes; no modo ∿ a rampa usa o atraso+fade DA PARTE que lançou
  (rampa ganhou t0 no futuro); ⚡ dispara no GO (decisão do autor). MIDI
  fica na CUE (nota→GO→todas as partes).
- **UI (fluxo do autor):** tecla **«PARTE»** ao lado do MIDI. Criar:
  ir à memória → seleccionar canais → PARTE → canais+tecla vermelho
  `#b03a3a` → menu (nº 1-8, tempos+atrasos, FX ∿/⚡, texto, OK/Cancelar);
  nº 1 edita os tempos da própria memória. Gerir: PARTE sem selecção →
  lista Modificar/Apagar; Modificar arma a parte (vermelho), os cliques
  na grelha tiram/põem canais, PARTE reabre o menu, OK grava/Cancel
  aborta. Coluna «PARTE» (P2+3) nas duas cuelists. «Actualização»
  preserva as partes; «Comprar» por cima apaga tudo (memória nova).
- **ASCII:** export escreve blocos `PART k` standard (UP/DOWN com delay,
  TEXT, CHAN da parte; o FX da parte NÃO viaja); import cria as partes
  (na v6.3.2 fundia); `PART 1` = a cue; parte >8 funde os níveis mas os
  tempos dela vão para uma parte-fantasma (não reescrevem os da cue);
  `_cue_total()` = max das partes → FOLLOWON compensado certo.
- **Afinações v6.3.3b (teste real do autor na Eos, 2026-07-07):**
  · Export: quando a memória tem partes, a estrutura vai TODA em PART
    (`PART 1` explícita com os tempos da cue + canais principais, depois
    `PART k`) — é assim que a Eos escreve e SEM isso ela não lê as
    partes (confirmado nos exports usitttest55/555.asc).
  · Menu da parte: nº começa na **2** (a parte 1 é sempre a principal,
    assumida automaticamente — não se edita no menu).
  · Barra de transição: uma parte com **FX ∿** conta para o
    `fade_total` mesmo sem canais a mover (a barra acompanha a rampa);
    FX ⚡ não estica.
  · Coluna FX: FX das partes aparecem como `P2·4∿` (nº da parte +
    FX). Tentou-se 🔴 mas não se via vermelho — retirado a pedido do
    autor; o Treeview não pinta letras de células individuais.
    Largura da coluna 44→84.
  · Canais AZUIS (programador) escolhidos para uma parte ficam
    registados na memória como ACTUALIZAÇÃO parcial e saem do azul
    (`Engine.update_cue_channels(idx, chs)`).
  · **Um FX, uma marca por memória (v6.3.3c):** o mesmo FX marcado
    na coluna directa E numa parte dava ordens contraditórias no mesmo
    GO (caso real do autor: ∿ pela parte + ⚡ pela coluna). Regra tipo
    «um canal, uma parte»: a nova atribuição ganha e a marca antiga
    sai (aplicada no menu da parte, no diálogo FX e no clique rápido —
    `_fx_marca_unica`); rede de segurança no motor: o tracking só
    conta a ÚLTIMA marca de cada FX por memória (a parte ganha à
    coluna; entre partes, a de nº maior). A coluna FX MANTÉM-SE (é o
    FX da parte 1) — decisão discutida com o autor 2026-07-08.

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
- **Etapa 0 (FEITA):** andaime i18n — `LANG`, `STRINGS`, `T()`,
  `load/save_app_config`, `set_lang`, separador «Idioma» nas Configurações.
  Comportamento inalterado; arranca em PT.
- **Etapa 1 (FEITA):** todas as strings de UI migradas para `T()` —
  parsers, todos os diálogos, menu, botões, transporte, editor FX
  (manual+dinâmico), cores/curvas, e ~60 mensagens internas. 313 chaves
  PT/EN com paridade total.
- **Etapa 2 (FEITA):** coluna `en` revista (paridade + placeholders OK).
- **Etapa 2.5 (FEITA):** página de Ajuda OSC in-app (`osc_reference_text()`
  via `T('osc_help.text')`). Separador «Ajuda OSC» / «OSC Help» nas
  Configurações. (v6.3, 2026-07-02)
- **Etapa 3:** docs GitHub — CONTRIBUTING.md para contribuidores.

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
