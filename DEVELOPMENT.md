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

## Retrato expande pela ALCUNHA (v6.3.3d, 2026-07-08)
- Pedido do autor: num aparelho com alcunha (ex.: parled RGBW = 600
  DIM + 600 R/G/B/W), dar valor ao DIM e chamar um retrato com o B a
  255 devia actuar no aparelho — sem ter de seleccionar o B.
- `Engine.alias_family(chs)`: expande um conjunto de canais pelas
  alcunhas (>0) presentes — a alcunha marca «mesmo aparelho». O
  `_retrato_click` com selecção passa a chamar
  `recall_retrato(idx, only=alias_family(selecção))`.
- Canais sem alcunha: comportamento v6.2 intacto (só os
  seleccionados). A selecção visível NÃO muda (não se juntam os
  canais expandidos) — só o recall alarga. Aparelhos com OUTRA
  alcunha não são tocados. Mesma filosofia do Solo por alias.

## Renumerador: coluna toda + Enter salta (v6.3.3e, 2026-07-08)
- Pedido do autor (colunas 8/16 bit): (1) seleccionar a coluna TODA;
  (2) Enter numa célula solta salta para a de baixo (digitar
  endereços em série); com intervalo seleccionado fica como estava.
- Clicar no CABEÇALHO de uma coluna de valores (alcunha/nome/univ/
  8 bit/16 bit/defeito) selecciona 1..N (`_select_column`, cursor
  hand2, foco na 1.ª célula, scroll ao topo); 2.º clique desfaz.
  Escreve-se na 1.ª célula + Enter → preenche como o intervalo
  arrastado (8/16 bit ascendente, etc.).
- `_range_enter(col, ch)` substituiu o bind do Enter: com intervalo
  activo na coluna → `_range_fill` (igual); sem intervalo → foco na
  célula ch+1 com o texto pré-seleccionado + scroll do canvas
  (`self._canvas` guardado no _build) para a manter visível.
- `patch.hint` actualizado (PT/EN).

## Renumerador: MARCAS de 16 bits (v6.3.3f, 2026-07-08)
- Problema do autor: o «Repetir Aparelho» patcha bem os 16 bits NO
  carimbo, mas faltava a via para patchar/re-patchar À POSTERIORI.
- Desenho final (do autor): cada canal pode estar **ASSINALADO como
  16 bits** — fundo VERDE (`MARK16_BG #2e4d33`) na célula 16 bit.
  A marca (`_bit16_mark`, set de canais) vem de: patch existente
  (bit16/fine), nome …16 (DIM16/PAN16), Repetir Aparelho (assinala
  ao carimbar), e **botão DIREITO** na célula 16 bit (toggle,
  `_toggle_bit16`). `_paint_bit16` pinta; `_highlight_range` usa a
  marca como fundo base da coluna 16 bit.
- Preenchimento da coluna 8 bit (intervalo OU coluna toda): canais
  ASSINALADOS consomem 2 endereços (pares 1,2 · 3,4 · …) e o fine
  escreve-se sozinho; os outros +1. Enter numa célula SOLTA de um
  canal assinalado também emparelha logo (fine = valor+1). Sem
  marcas = comportamento antigo. Liberdade manual intacta: encher
  8+16 à mão continua a fazer um canal 16 bits (o Aplicar deriva
  bit16 do fine, como sempre). patch.hint actualizado (PT/EN).

## Alterações v6.4 (2026-07-08) — DMX-IN, Etapa 1 (só escuta)
Spec do autor em `MESADELUX_V64_DMXIN_SPEC.md` (Downloads → guardar
junto ao projecto). Ficheiro `mesadelux_v6_4.py` (v6.3.3 intacta).
- **EscutaDMXIn** (secção própria antes da SELECÇÃO DE CANAIS):
  recepção sACN com a biblioteca `sacn` (a MESMA da saída — zero
  dependências novas; decisão da spec confirmada). Thread isolada,
  snapshot com lock, `esta_a_receber()` (silêncio > 2 s). NÃO toca
  no motor de saída, no show nem no `.ldsk`.
- **DESCOBERTA desta máquina (2026-07-08):** a firewall do Windows
  bloqueia UDP loopback em sockets 0.0.0.0 — com a mesa de origem
  NO MESMO PC (GMA3/Eos em unicast p/ 127.0.0.1), a escuta tem de
  fazer bind a 127.0.0.1. Por isso a interface é CONFIGURÁVEL
  (0.0.0.0 / 127.0.0.1 / IPs locais). Validado em loopback real.
- **UI:** Configurações → separador «DMX-In» (ligar/desligar,
  universos «1,2», interface, estado A RECEBER/Silêncio por
  universo 2x/s, nota explicativa). Valores ao vivo na grelha:
  crachá CIANO no canto sup. direito de cada célula (0-255 bruto,
  traduzido pelo renumerador universo+endereço→canal; 16 bits
  mostra o coarse). Só aparece com a escuta ligada; ciclo
  root.after 100 ms (10x/s), redesenho só quando muda (entra no
  tuplo de estado das células). Aviso se o universo escutado
  coincidir com a saída própria ACTIVA (sACN/Art-Net).
- **Preferências** (~/.mesadelux.json): `dmx_in_universos` +
  `dmx_in_bind` (máquina, não show). Escuta arranca sempre OFF.
- **test_dmx_in.py** (na pasta): script isolado da spec — corre
  sozinho, imprime pacotes/mudanças; 2.º argumento = interface. Aplica
  o mesmo filtro da app.
- **FIX pisca-pisca (2026-07-08, reportado pelo autor):** o valor
  «piscava» apesar de a receber. Causa: a Eos/GrandMA intercalam no
  mesmo universo pacotes de PRIORIDADE POR ENDEREÇO (E1.31 start code
  0xDD, valores 0-200) com os dados de nível (start code 0x00) — o
  callback aceitava ambos e o crachá saltava entre o nível e a
  prioridade. Correcção em `EscutaDMXIn._faz_cb`: ignora `dmxStartCode
  != 0` e `option_PreviewData` (blind), e ARBITRA a fonte por universo
  (`_fonte[u]=(nome,prioridade,hora)`): trava numa fonte — só a assume
  outra se tiver prioridade MAIOR, for a mesma, ou a actual ficar calada
  > 2 s. Isto também mata o pisca entre a Eos e o nosso próprio output
  no mesmo universo. Testado deterministicamente (callback com pacotes
  falsos: start code, preview, prioridade, takeover, silêncio).
- **Etapa 2 — CAPTURA AO VIVO (2026-07-09, redesenho do autor):**
  1.ª versão tinha um botão «Capturar» (snapshot pontual → programador);
  o autor pediu para o tirar — o DMX-In deve entrar DIRECTO e ao vivo no
  programador, e grava-se com **Comprar** (Take = memória nova) /
  **Actualizar** (Update = existente) como qualquer look. (O botão
  snapshot também tinha um bug: ao gravar 2 memórias e passar, o crachá
  deixava de ser repintado e os valores «desapareciam».)
  · `_dmx_in_tick` (10x/s) alimenta o PROGRAMADOR: para cada canal com
    patch e valor recebido > 0, `set_channel(ch, bruto)` (0-255 tal e
    qual — raw-vs-curva resolvido pela regra do autor: interno 255 mostra
    dec 255 OU pct 100 %); reaplica mesmo depois de um Comprar limpar o
    programador (o DMX-In continua a mandar → resolve o bug dos valores
    que sumiam); canal que cai a 0 é libertado (`clear_channel`).
  · **Cor distinta:** canais conduzidos pelo DMX-In (`_din_driven`) ficam
    azul-CIANO (fill `#0f3a4a`, outline `#2fb6c8`) vs o azul normal do
    programador — o crachá do canto (Etapa 1) foi REMOVIDO (o valor é
    agora o próprio número da célula).
  · **Libertação bloqueada** enquanto o DMX-In entra (`_din_bloqueia` em
    `_on_liberta` e no 2.º toque do `_on_clear` — os valores voltavam
    logo; desligar a escuta primeiro). Desligar a escuta = FREEZE: os
    valores ficam como programador NORMAL (azul), a libertação volta a
    funcionar, o look não se perde.
  · Sem controlo OSC da Eos (avança-se à mão). i18n `din.no_release`.
    NÃO escreve no `.ldsk` (feeding do programador não entra no
    `_show_data`, logo não marca «por gravar»).
- **FIX «a receber mas nada na grelha» (2026-07-09):** o próprio output
  sACN da app fazia loopback na mesma máquina; escutar o mesmo universo
  que se emite → a arbitragem anti-pisca travava na NOSSA fonte (zeros/
  cue actual) em vez da Eos → indicador «a receber» (o nosso output) mas
  grelha vazia. Correcção: o sender sACN de saída passou a ter
  `source_name=SACN_SOURCE_NAME` ('MesaDeLux') e o receptor DMX-In IGNORA
  essa fonte (`_faz_cb`: `if src == SACN_SOURCE_NAME: return`). Assim,
  com output+escuta no mesmo universo, a app captura SÓ a mesa externa;
  se só houver o nosso output, mostra «Silêncio» (honesto). `test_dmx_in.py`
  melhorado: imprime TODOS os endereços com valor (endereço:valor) para
  cruzar com o patch. (Diagnóstico: a grelha só mostra canais PATCHADOS
  no universo+endereço onde a Eos põe o valor — as 3 pontas têm de
  alinhar: output da Eos ↔ universo escutado ↔ patch.)
- **FIX «diz Silêncio a receber» (2026-07-09):** o indicador
  A-RECEBER/Silêncio tinha 2 problemas. (1) `_ultima` (timestamp do
  indicador) só se actualizava quando a arbitragem ACEITAVA o pacote —
  uma 2.ª fonte que perdesse a arbitragem não contava → dizia «Silêncio»
  a receber. Passou a actualizar-se para QUALQUER fonte externa
  (start-code 0, não-preview, não a nossa), fora do bloco de arbitragem;
  o VALOR mostrado continua a seguir a arbitragem. (2) `SILENCIO_S` subiu
  de 2,0 → **2,5 s** (o timeout de perda de dados da norma E1.31; a Eos
  espaça envios quando o valor é estático e 2,0 s dava falso «Silêncio»).
- Etapa 3 (merge num show existente, mapeamento de slots) e as ideias
  mais arrojadas (app avança a Eos por OSC, gravação semi-automática)
  ficam para depois — ver roadmap na spec.

## v6.4 — afinações pós-teste real (2026-07-09/10)
- **Cor DMX-In = ROSA/magenta** (fill #7d1f4a, contorno #ff6ba6,
  número #ffc0dc) — decisão do autor; distinta do vermelho da PARTE,
  do azul do programador, do laranja FX e do violeta submaster.
- **Indicador «a segurar último look (fonte)»** a âmbar quando a
  fonte pára de enviar mas há look captado (fontes send-on-change,
  como Eos onPC, só transmitem quando algo MUDA — não é avaria);
  «sem sinal» só se nunca chegou nada; A RECEBER verde. `estado(u)`
  devolve (rx, fonte, idade, tem_look). SILENCIO_S=2,5 s (E1.31) e
  o timestamp conta QUALQUER fonte externa (não só a dona).
- **Libertação vs DMX-In:** clear_programmer/release_output ganharam
  `exclude`; LIBERTA/LIMPA/Esc libertam o manual e deixam os canais
  do DMX-In (voltavam na tick seguinte); menu «Liberta» =
  `_liberta_total` (libertação total num clique — programador +
  verdes ao defeito, FX off; só fica o DMX-In); Esc = 2-toques como
  a tecla; `/release_all` da consola também exclui o DMX-In (a rampa
  lutava com o tick). Desligar a escuta = freeze (vira azul normal).
- **Aviso (AUTO) do cabeçalho corrigido:** lia o follow da cue
  ACTUAL (semântica antiga) e rotulava a cue errada; agora lê o da
  cue que ENTRA via `_peek_next_index` (loop-aware) = o motor.
- **FIX PARTes na Eos (espectáculo grande):** o TEXT da cue ANTES do
  PART 1 baralhava o parser da Eos (as partes não entravam). Numa
  cue COM partes o TEXT escreve-se DEPOIS de todas as partes (é
  onde a Eos o põe — confirmado no export real dela); sem partes
  fica como sempre. Import: TEXT antes dos CHAN da parte = label da
  parte; depois (parte já com canais) = label da CUE.
- Settings 500x560 e redimensionável (o separador DMX-In não cabia).
- Revisão i18n 2026-07-10: paridade PT/EN total (0 chaves em falta),
  placeholders coerentes; chaves mortas inofensivas mantidas
  (din.silencio/no_release, fxd.chaos_size*, settings.osc_help_tab,
  app.title).

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
