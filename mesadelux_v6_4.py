#!/usr/bin/env python3
"""
MESADELUX v6.4 - Mesa de Luz Teatral
Saída DMX: sACN (E1.31) + Art-Net (nativo, sem dependências) em paralelo.
Entrada: OSC (consolas físicas Pico W / bridge USB).
Requires: pip install sacn python-osc

v6.4 — DMX-IN, escuta sACN (By Worm):
  · Etapa 1: escutar sACN de ENTRADA (GrandMA3/Eos/qualquer emissor,
    mesmo no mesmo computador) e mostrar os valores AO VIVO na grelha
    de canais, por baixo do valor programado (ciano), traduzidos pelo
    patch (universo+endereço → canal). SÓ escuta — não grava nada.
    Configurações → separador «DMX-In»: ligar/desligar, universos,
    indicador A RECEBER/SILÊNCIO por universo, aviso se o universo
    escutado coincidir com a saída própria. Classe EscutaDMXIn
    (thread sacn isolada, snapshot com lock, UI via root.after).
    Ver MESADELUX_V64_DMXIN_SPEC.md. Etapa 2 (gravação) fica p/ depois.

v6.3.3 — PARTES (divisões da memória, By Worm):
  · Uma memória pode ter até 8 PARTES: a 1 é a divisão principal (a
    própria memória); as 2-8 são subdivisões com canais próprios, tempos
    próprios (fade IN/OUT + atrasos) e FX próprio — vários eventos em
    simultâneo num só GO (ex.: efeito 5/10 + ciclorama a mudar em 30 s).
    As partes NÃO mudam o estado final da memória — são metadados de
    TEMPO (tracking/cue_only/GOTO intactos; .ldsk compatível p/ trás).
    Tecla «PARTE» ao lado do MIDI: seleccionar canais → PARTE → menu
    (nº 1-8, tempos, FX, texto). MIDI fica na cue (nota→GO→tudo).
    FX em modo ∿ lançado por uma parte rampa com os tempos DELA.
    No ASCII as partes viajam como PART k (standard USITT 10.5).
    Ver MESADELUX_V633_PLANO_PARTS.md.

v6.3.2 — IMPORT/EXPORT USITT ASCII 3.0 (By Worm):
  · Porta de entrada/saída para outras mesas (ETC Eos/Ion, Strand,
    Avolites…) via standard USITT ASCII 3.0. O .ldsk continua a ser o
    ÚNICO formato de gravação (fidelidade total); o ASCII é só
    portabilidade: menu Ficheiro → «Importar ASCII…» / «Exportar ASCII…».
    Parser de texto simples (stdlib, sem dependências novas). MIDI por
    cue, FX, looks, alcunhas, curvas e halos NÃO vão no ASCII (aviso).
    Ver MESADELUX_USITT_ASCII_SPEC.md e MESADELUX_V632_PLANO_ASCII.md.

v6.1 — IMPORTAÇÃO GDTF integrada no renumerador (By Worm):
  · Tecla "GDTF" (ao lado do DMX) abre o GDTFDialog: abre um ficheiro .gdtf
    (ZIP com description.xml — stdlib, sem dependências novas), lista os
    modos DMX, e para o modo escolhido gera a NOMENCLATURA reduzida a
    abreviaturas (<=6 ch) no formato do «Repetir Fixture», com «16» nos
    canais de 16 bit (detectado pelo Offset). Botões: «Copiar footprint»
    e «Patchar no renumerador…», que abre logo o renumerador + Repetir
    Fixture com o footprint PRÉ-PREENCHIDO — fecha o ciclo GDTF→patch.
    A ferramenta autónoma gdtf_footprint.py continua a existir à parte.
  · DEFEITOS por NOME no carimbo (2026-06-16 — mais fiável que os defeitos
    do GDTF, que variam de marca): cores (R/G/B/W/A/…) → 255; PAN/TILT/
    ZOOM/FOCUS → 127; DIM (0-100 %), strobe e o resto → 0. Sintaxe «@N» no
    fim do nome = defeito explícito 0-255 (ex.: ZOOM@200, PAN16@128), para
    canais fora dessa lista. nome_defeito() no módulo.

v6 — melhorias no RENUMERADOR (By Worm):
  · "Repetir Fixture" — carimbo de fixtura no PatchDialog. Repete um
    modelo de N canais (nomes separados por espaço, ex.: DIM R G B W) ao
    longo de Q fixturas, a partir de um canal/universo/endereço inicial.
    Cada nome = um canal da mesa (+1 contíguo); o endereço DMX avança 1
    (8 bit) ou 2 (16 bit). Opção de ciclar a cor de halo por fixtura.
    - 16 BITS: termina o nome em «16» (ex.: PAN16) → o canal fica 16 bit e
      ocupa coarse+fine (2 endereços).
    - MOSTRAR automático: DIM → 0-100 % (pct), todos os outros → 0-255
      (dec). Isto afecta o funcionamento da app (TODOS/Solo só mexem em
      pct; passos e grelha respeitam o modo).
    - PAN / TILT → defeito 127 (projector apontado p/ baixo e centrado).
    Escreve SÓ nas linhas do renumerador (StringVar); o utilizador revê e
    grava com «Aplicar» — reaproveita a validação existente. NÃO toca em
    alcunha/curva. Não muda o esquema do .ldsk — abre na v3/v4/v5. Canais >
    NUM_CHANNELS ou DMX > 512 são ignorados (avisa).
  · ENDEREÇO DMX ÚNICO (regra universal): um endereço (universo, addr) só
    pode estar num canal. O carimbo tira o endereço de onde estava; o
    «Aplicar» do renumerador corre Patch.enforce_unique_addresses() como
    rede de segurança (o 1.º canal a usar cada endereço fica com ele); a
    tecla R já usava remove_addr_conflicts.
  · DEFEITOS reaplicados aos canais PASSIVOS ao editar o patch
    (apply_defaults_to_passive) — um defeito acabado de definir (ex.: PAN
    127) passa a aparecer na grelha e a ser o ponto de partida do +/-.
  · PÁGINA MONITOR DMX (tecla DMX, roxa/vermelha, ao lado do >): alterna
    a grelha de canais com um monitor da SAÍDA DMX — 512 endereços de um
    universo, fundo preto, caixas pequenas (nº do endereço + barra/cor =
    está a enviar; sem valor de nível), selector de universo ◀ N ▶.
    Números maiores (8 pt). NAVEGAÇÃO < / > na vista DMX anda nos
    endereços (1..512, em ciclo). HIGHLIGHT (H) = teste de saída: força o
    endereço seleccionado a FULL na saída (dmx_force) para identificar a
    fixtura no palco — com < / > varre-se. SOLO (S) = isola o universo
    (só os endereços forçados saem; dmx_solo). Sair da vista DMX desliga o
    teste. RENUMERAÇÃO INVERSA: R com 1 endereço seleccionado pergunta que
    canal da mesa o controla e patcha (regra do endereço único). Workflow:
    DMX → H → < / > até a fixtura acender → R → indicar o canal da mesa.

v5 — página FX (efeitos) ao lado da página XF (sequência principal):
  ETAPA 0 (feita): teclas XF/FX junto à LIMPA; página FX no painel direito
    (Comprar/Actualização/Guardar/Apagar FX + <<< >>> + 8 botões FX em
    2 linhas de 4, com a zona de edição por baixo); modelo de dados dos
    8 FX (manual = lista de passos; dinâmico = ciclo paramétrico) gravado
    no .ldsk em 'fx' (v3/v4 ignoram o campo);
    Comprar+clique cria a "concha" do FX (nome + modo); esquerdo activa /
    desactiva (visual por ora), direito entra/sai da edição; Apagar FX.
  ETAPA 1 (feita): motor FX no tick — camada acima do playback e abaixo
    do programador, valores ABSOLUTOS, HTP entre FX; modo MANUAL completo:
    editor de passos na zona de edição (Comprar 2× grava a luz em cena
    herdando os tempos do passo anterior, Actualização 2× refaz o passo,
    Apagar passo, clique edita fade/auto 0-60 s — 0 = corte seco,
    <<< >>> navegam passos com preview no programador), loop
    contínuo com 1.º fade a partir da cena; células da grelha comandadas
    por FX ficam laranja; linha verde no editor segue o passo em execução.
  ETAPA 2 (feita): modo DINÂMICO — Comprar 2× compra a selecção de canais
    (sem precisar de níveis); CARROAGEM 1-99 % = largura da banda acesa
    (12 canais c/ quadrada seca: ~92 → 11 acesos/1 apagado; ~8 → 1 aceso);
    dentro da janela: valor = 255 × (v_baixo + (v_alto-v_baixo) × impulso)
    /100, com v_alto/v_baixo 0..100 (negativos eliminados — o escuro
    prolonga-se encurtando a carroagem); curvas sino (assimétrica por
    ataque/retirada 0-10: 0=rápido/seco, 10=lento) e quadrada/PWM (rampas
    nos flancos); BPM 1-240 com fase acumulada (mudar em vivo não salta);
    grupos 0-24 round-robin (0=cada canal no seu ciclo, 1=todos juntos);
    direcção > (esq→dta) / < (dta→esq) / <> baloiço (vai e volta);
    painel de sliders na zona de edição, tudo ajustável EM VIVO.
  ETAPA 3 (re-corrigida 2026-06-13): CARROAGEM (sem blocos, grupos=0) =
    banda única de tamanho variável a percorrer os canais 1 a 1; GRUPOS
    (sem blocos, >=2) = round-robin em CROSSFADE (carroagem regula a
    sobreposição). BLOCOS = unidade composta VIAJANTE (carroagem
    bloqueada): grupos=0 as células viajam (AABB/12 → {1,2}{3,4}…);
    grupos=1 pertença alternada por letra; grupos>=2 provisório (a
    confirmar). CAOS (ex-"Random") 0-100: instante/duração/quem-acende,
    NUNCA o nível. RITMO RETIRADO (redesenhar com o autor).
  ETAPA 4: coluna FX na cuelist (tracking), conflitos, docs.

v4 — alterações principais sobre a v3:
  - Art-Net (ArtDMX, porta UDP 6454) em paralelo com o sACN, implementação
    nativa. Universo da mesa N (1-based) -> port-address Art-Net N-1.
  - Estabilidade de threads: NENHUMA chamada Tkinter fora da thread principal.
    O engine e o servidor OSC comunicam com a UI por queue + flag "dirty",
    drenadas por um pump no mainloop (root.after). Crítico para compilar
    para Windows (PyInstaller).
  - Engine: thread protegida com try/except (um erro não mata a saída DMX),
    RLock em resize/load/run_cue, ordem de resize corrigida.
  - Grelha de canais: redesenho parcial (itemconfig) em vez de delete('all')
    a cada frame — muito menos CPU e sem flicker.
  - OSC: a app APRENDE o IP da consola (origem dos pacotes recebidos) e passa
    a enviar feedback para lá — funciona em modo STA sem configurar IPs.
  - Push de nomes/alcunhas/curvas para a consola com ritmo controlado
    (chunks) para não afogar o buffer UDP do Pico. Novo /channel/patched.
  - stop_osc fecha o socket (server_close) — reiniciar OSC não falha.
"""

import json
import math
import random
import re
import sys
import time
import socket
import struct
import queue
import threading
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import sacn
    HAS_SACN = True
except ImportError:
    HAS_SACN = False

try:
    from pythonosc import dispatcher as osc_disp
    from pythonosc import osc_server as osc_srv
    HAS_OSC = True
except ImportError:
    HAS_OSC = False

# v6.3 — MIDI (mido + python-rtmidi). SEMPRE opcional: a app arranca na
# mesma sem MIDI instalado ou sem dispositivos ligados.
try:
    import mido
    HAS_MIDI = True
except ImportError:
    HAS_MIDI = False

NUM_CHANNELS = 100

# v6.4 — nome da nossa fonte sACN de SAÍDA. O DMX-In IGNORA esta fonte,
# para não capturar o nosso próprio output (na mesma máquina o sACN faz
# loopback: sem isto, escutar o mesmo universo que se emite capturava o
# próprio output em vez da mesa externa).
SACN_SOURCE_NAME = 'MesaDeLux'

# v5 — limite máximo de canais. Defeito do show = 100; pode alargar-se
# até 512 (um universo DMX inteiro). Acima de ~200 a app fica mais pesada
# (desenho da grelha + flush) — serve para testes; optimização futura.
MAX_CHANNELS = 512

# v5 — nº de efeitos da página FX (16: 2 linhas de 8 botões)
NUM_FX = 16

# v6.3.3 — máximo de PARTES por memória. A parte 1 é a divisão principal
# (a própria memória); as 2..NUM_PARTS são subdivisões com canais, tempos
# e FX próprios. Standard da mesa (decisão do autor 2026-07-07).
NUM_PARTS = 8

# cores de HALO para agrupar canais na grelha
HALO_COLORS = {
    'vermelho': '#e74c3c', 'laranja':  '#e67e22', 'amarelo': '#f1c40f',
    'verde':    '#2ecc71', 'ciano':    '#00d5d5', 'azul':    '#3498db',
    'magenta':  '#d633d6', 'branco':   '#ffffff', 'cinzento': '#888888',
}

# Nomes pré-feitos para canais (renumerador). A 1ª opção (vazia) limpa o nome.
# A combobox é editável: o utilizador pode escolher um destes OU escrever
# qualquer nome livre até 6 caracteres.
CHANNEL_NAME_PRESETS = [
    '', 'DIMMER', 'PAN', 'TILT', 'RED', 'GREEN', 'BLUE',
    'WHITE', 'AMBAR', 'FOCUS', 'ZOOM', 'STROBE',
]

# v3 #4 — curvas de resposta DMX (so afecta 8 bits; 16 bits ignora a curva)
#   linear : passa o valor 0-255 directo (default)
#   rele   : actua como rele c/ threshold 10  (0-9 -> 0; 10-255 -> 255)
#   ligado : forca DMX 255 sempre (canal "L" - mostrado a vermelho na grelha)
CURVE_LINEAR = 'linear'
CURVE_RELE   = 'rele'
CURVE_LIGADO = 'ligado'
CURVE_VALUES = (CURVE_LINEAR, CURVE_RELE, CURVE_LIGADO)

# v5 etapa 2 — parâmetros por defeito do FX DINÂMICO.
#   curva     : 'sino' ou 'pwm' (no UI escreve-se só "PWM" — termo
#               internacional, pedido do autor; 'quadrada' aceita-se
#               como sinónimo em shows antigos)
#   ataque    : 0-10 — velocidade ascendente (0 = seco/instantâneo, 10 = lento)
#   retirada  : 0-10 — velocidade descendente (idem)
#   bpm       : ciclos por minuto (60 = ciclo 0→100 60× por minuto)
#   carroagem : 1-99 % — LARGURA DA BANDA ACESA (conceito do autor,
#               2026-06-12): a fracção do ciclo em que cada canal vai
#               aceso = quantos projectores seguem na "carruagem".
#               Ex.: 12 canais, quadrada seca — carroagem ~92 → 11 acesos
#               e 1 apagado; ~8 → 1 aceso e 11 apagados; 50 (defeito) →
#               metade acesa. NÃO mexe no nível da luz.
#   v_alto    : topo do ciclo  (0..100 %; default 100)
#   v_baixo   : fundo do ciclo (0..100 %; default 0)
#               (negativos ELIMINADOS — o escuro prolongado faz-se agora
#                encurtando a carroagem; decisão do autor 2026-06-12)
#   grupos    : 0-24 — divisão round-robin dos canais; 0 = cada canal no
#               seu ciclo, 1 = todos juntos
#   direccao  : '>' esq→dta (defeito) · '<' dta→esq · '<>' baloiço
#               (vai e volta; cada travessia dura um ciclo do BPM)
#   blocos    : ''|'AA..BB..CC..' — blocos de canais CONSECUTIVOS; o
#               comprimento de cada sequência de letras (A→B→C, por esta
#               ordem) define o tamanho dos blocos e o padrão repete-se.
#               Ex.: AABBBC c/ 12 canais → (1,2)(3,4,5)(6)(7,8)(9,10,11)
#               (12). Vazio = usa os grupos. Blocos têm prioridade.
#   random    : 0-100 — 0 = nada; perturba a fase e o nível de cada
#               canal (resample periódico); 100 = caos total
#   caos_size : 0-100 — TAMANHO do caos (modo selecção). 0 = inactivo
#               (a carroagem funciona como largura de janela, caos
#               clássico). >0 ANULA a carroagem: o caos passa a SORTEAR
#               k = arredonda(caos_size% × nº de canais) canais (mín. 1)
#               que acendem/apagam juntos; os restantes ficam escuros. A
#               selecção mantém-se 'caos_rep' flashes antes de re-sortear.
#   caos_rep  : ''|'1 4 …' — repetição da combinação do caos: nº de
#               batidas seguidas que a MESMA combinação aleatória se
#               mantém antes de sortear outra (padrão de números que
#               cicla; 0=1; vazio=1=muda sempre). Ex.: '2 3' → mantém 2,
#               muda, mantém 3, muda, repete. Só actua com Caos>0.
#   ritmo     : 1-24 — padrão musical que comanda o ciclo: cada figura
#               do compasso é UM varrimento completo com duração
#               proporcional (♩ = 1 batida do BPM; pausa = escuro).
#               1 (default) = ♩♩♩♩, igual ao ciclo contínuo.
FX_DIN_DEFAULTS = {'curva': 'sino', 'ataque': 5, 'retirada': 5,
                   'bpm': 60, 'carroagem': 50, 'v_alto': 100,
                   'v_baixo': 0, 'grupos': 0, 'direccao': '>',
                   'blocos': '', 'random': 0, 'caos_size': 0,
                   'caos_rep': '', 'ritmo': 1, 'cruzamento': 0,
                   # v6.2 — modo CAOS: nº de canais sorteados por combinação
                   # é um valor aleatório entre quant_min e quant_max (0 =
                   # nada; min=max = fixo; limitado aos canais seleccionados).
                   'quant_min': 0, 'quant_max': 0}


# ─────────────────────────────────────────────
# i18n — INTERNACIONALIZAÇÃO (Etapa 0 · v6.2, By Worm)
# Fonte ÚNICA bilingue. O português é a língua canónica do projecto
# (filosofia anti-colonial); o inglês é a tradução. Regra de ouro: toda a
# string de UI NOVA passa por T("dominio.chave"). NÃO entram aqui os
# endereços OSC (/go, /soltar, /rec/comprar…) nem os atributos técnicos
# (PAN, TILT, DIM, GDTF, footprint…) — fazem parte do contrato com o
# firmware/normas e ficam como estão. Detalhes em DEVELOPMENT.md.
#
# O idioma é uma PREFERÊNCIA DO UTILIZADOR (não do show): guarda-se em
# ~/.mesadelux.json, não no .ldsk — abrir o show de outra pessoa não muda
# a tua língua.
# ─────────────────────────────────────────────
import os

AVAILABLE_LANGS = ('pt', 'en')
LANG = 'pt'                       # locale activo (defeito = canónico)
APP_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.mesadelux.json')

# v6.3 — portas MIDI escolhidas pelo utilizador (preferência da máquina, não
# do show). Guardadas no mesmo ~/.mesadelux.json. None = nenhuma/desactivado.
MIDI_IN_PORT = None
MIDI_OUT_PORT = None

# v6.4 — DMX-IN (preferência da máquina, não do show): universos a
# escutar e interface de escuta (0.0.0.0 = todas; 127.0.0.1 = mesa de
# origem NO MESMO PC — a firewall do Windows pode bloquear o loopback
# em 0.0.0.0, verificado 2026-07-08).
DMX_IN_UNIVS = [1]
DMX_IN_BIND = '0.0.0.0'

# Dicionário de strings. Etapa 0 = semente (só o que o andaime precisa).
# Nas etapas seguintes migram-se as strings de UI sector a sector. O valor
# 'pt' é a referência; o 'en' é a tradução.
STRINGS = {
    'pt': {
        'app.title':            'MESADELUX — Mesa de Luz',
        'settings.title':       'Configurações',
        'settings.lang_tab':    ' Idioma ',
        'settings.lang_label':  'Idioma da interface:',
        'settings.lang_note':   'A mudança de idioma aplica-se por completo '
                                'ao reiniciar a aplicação.',
        'settings.lang_apply':  'APLICAR IDIOMA',
        'settings.cl_tab':      ' Cuelist ',
        'settings.cl_label':    'Modelo da cuelist principal:',
        'settings.cl_cueonly':  'Cue-only (teatro) — cada cue é um look '
                                'fechado nas intensidades',
        'settings.cl_tracking': 'Tracking (clássico) — tudo LTP + tracking',
        'settings.cl_note':     'Cue-only: intensidades (0-100%) fecham por '
                                'cue (saltar no guião dá sempre o mesmo); '
                                'atributos (0-255) seguem (tracking) e o BLOCK '
                                'aplica-se só a eles. Guarda-se no show.',
        'settings.cl_apply':    'APLICAR MODELO',
        'lang.pt':              'Português',
        'lang.en':              'English',
        'common.close':         'Fechar',
        'common.apply_all':     'Aplicar tudo + Fechar',
        'common.all_files':     'Todos',
        # ── parsers / Art-Net ──
        'artnet.unicast_needs_ip': 'Art-Net unicast requer um IP de destino.',
        # ── GDTFDialog ──
        'gdtf.title':           'Importar GDTF → Renumerador',
        'gdtf.open_btn':        'Abrir GDTF…',
        'gdtf.no_file':         '(nenhum ficheiro)',
        'gdtf.footprint_label': 'Pegada (DIM fica 0-100 %; os outros 0-255; '
                                '«16» = 16 bit):',
        'gdtf.copy_btn':        'Copiar pegada',
        'gdtf.patch_btn':       'Usar esta pegada',
        'gdtf.modes_label':     'Modos DMX:',
        'gdtf.open_title':      'Abrir GDTF',
        'gdtf.read_error':      'Não foi possível ler:\n{e}',
        'gdtf.mode_header':     'Modo: {nome}   ({n} canais)',
        'gdtf.col_header':      'GDTF / nome',
        'gdtf.copied':          'Pegada copiada:\n\n{s}',
        'gdtf.pick_first':      'Abre um GDTF e escolhe um modo primeiro.',
        # ── RepetirFixtureDialog ──
        'rep.title':            'Repetir Aparelho',
        'rep.channels_label':   'Canais (nomes separados por espaço; nº de\n'
                                'nomes = nº de canais do aparelho):',
        'rep.hint':             '«16» no fim = 16 bit (ex.: PAN16).  «@N» no '
                                'fim = defeito (ex.: ZOOM@200).\nDIM 0-100 %, '
                                'outros 0-255.  Defeitos: cores 255, '
                                'PAN/TILT/ZOOM/FOCUS 127.',
        'rep.f_ch':             'Canal inicial:',
        'rep.f_univ':           'Universo:',
        'rep.f_addr':           'DMX inicial:',
        'rep.f_qtd':            'Quantidade:',
        'rep.f_alc':            'Alcunha (opc.):',
        'rep.alc_hint':         '(+1 por aparelho: 601→610; todos os '
                                'parâmetros do mesmo aparelho partilham-na)',
        'rep.cycle_halo':       'Ciclar cor de halo por aparelho',
        'rep.repeat_btn':       'Repetir',
        'rep.import_gdtf':      'Importar GDTF…',
        'rep.need_one':         'Define pelo menos um canal (nome).',
        'rep.must_numbers':     'Canal/Universo/DMX/Quantidade têm de ser '
                                'números.',
        'rep.must_ge1':         'Valores têm de ser ≥ 1.',
        'common.cancel':        'Cancelar',
        # ── PatchDialog (renumerador) ──
        'patch.title':          'Renumerador — Canais → DMX',
        'patch.hint':           "DMX aceita vários endereços separados por '+'"
                                "  (ex.:  3 + 9 + 11).\nUm canal é de 16 bits "
                                "se tiver endereço(s) no campo 16 bit.\n"
                                "Intervalo: arrasta o botão esquerdo numa "
                                "coluna de valores, escreve na 1ª célula e "
                                "carrega Enter (vazio = apaga o intervalo).\n"
                                "  · Alcunha / 16 bit → ascendente (+1 por "
                                "linha)   · Univ / Defeito → todas com o "
                                "mesmo valor.\n"
                                "  · 8 bit → canais ASSINALADOS a verde "
                                "(16 bits) consomem 2 endereços (pares "
                                "1,2 · 3,4 · …) e o 16 bit escreve-se "
                                "sozinho. Botão DIREITO na célula 16 bit "
                                "assinala/desassinala; o patch, o nome "
                                "…16 e o Repetir Aparelho assinalam "
                                "sozinhos.\n"
                                "Clicar no CABEÇALHO selecciona a coluna "
                                "toda (2º clique desfaz). Enter numa célula "
                                "solta salta para a de baixo.",
        'patch.col_channel':    'Canal',
        'patch.col_alias':      'Alcunha',
        'patch.col_name':       'Nome',
        'patch.col_univ':       'Univ',
        'patch.col_dmx8':       'DMX 8 bit',
        'patch.col_dmx16':      'DMX 16 bit',
        'patch.col_default':    'Defeito',
        'patch.col_halo':       'Halo',
        'patch.col_show':       'Mostrar',
        'patch.col_curve':      'Curva',
        'patch.clear_all':      'Apagar Tudo',
        'patch.clear_all_q':    'Apagar todo o renumerador (todos os canais '
                                'ficam sem endereço)?',
        'patch.one_to_one':     '1 para 1',
        'patch.repeat_fixture': 'Repetir Aparelho…',
        'patch.apply':          'Aplicar',
        'patch.halo_none':      '(nenhum)',
        'patch.filled':         '{n} canais preenchidos.',
        'patch.over':           '{n} ignorados (acima do canal {max}).',
        'patch.skipped':        '{n} ignorados (DMX acima de 512).',
        'patch.moved':          '{n} canal(is) perderam endereços já usados.',
        'patch.review':         '\n\nRevê e carrega «Aplicar» para gravar no '
                                'renumerador.',
        'patch.warn_title':     'Renumerador',
        'patch.dropped':        '{n} endereço(s) fora de 1–512 ignorados.',
        'patch.dups':           'Endereços repetidos retirados (um endereço '
                                'DMX só pode estar num canal) — canais: '
                                '{nums}.',
        # ── RecordCueDialog ──
        'rec.title':            'Gravar Memória',
        'rec.f_num':            'Número:',
        'rec.f_label':          'Deixa:',
        'rec.f_fade_in':        'Entrada (s):',
        'rec.f_delay_in':       'Atraso à entrada (s):',
        'rec.f_fade_out':       'Saída (s):',
        'rec.f_delay_out':      'Atraso à saída (s):',
        'rec.f_auto':           'AUTO (s):',
        'rec.auto_note':        '(AUTO vazio = sem automático;\n 0 = entra '
                                'logo a seguir à transição)',
        'rec.record_btn':       'Gravar',
        'rec.num_error':        'Número, tempos e AUTO devem ser numéricos.',
        'common.error':         'Erro',
        # ── cores de halo (RÓTULO; o valor gravado é sempre a chave) ──
        'halo.vermelho': 'vermelho', 'halo.laranja': 'laranja',
        'halo.amarelo': 'amarelo', 'halo.verde': 'verde',
        'halo.ciano': 'ciano', 'halo.azul': 'azul',
        'halo.magenta': 'magenta', 'halo.branco': 'branco',
        'halo.cinzento': 'cinzento',
        # ── curvas (RÓTULO; o valor gravado é sempre o token) ──
        'curve.linear': 'linear', 'curve.rele': 'relé', 'curve.ligado': 'ligado',
        # ── SettingsDialog ──
        'common.ok':            'OK',
        'set.sacn_enable':      'Activar sACN',
        'set.univ_auto':        'Universos automáticos (seguem o renumerador)',
        'set.now_out':          'Agora a sair: {u}',
        'set.univ_manual':      'Universos manuais (até 4):',
        'set.unicast_ip':       'IP Unicast:',
        'set.if_multicast_off': '(usado se Multicast OFF)',
        'set.iface':            'Interface (IP saída):',
        'set.iface_note':       '(adaptador da rede de luz; vazio = auto)',
        'set.apply_sacn':       'APLICAR sACN',
        'set.an_enable':        'Activar Art-Net (paralelo ao sACN)',
        'set.origin_auto':      'auto',
        'set.origin_manual':    'manuais',
        'set.an_univ':          'Universos ({origem}): {u}\n'
                                'Mesa U1 → Art-Net 0, U2 → 1, …',
        'set.an_bcast':         'Broadcast (255.255.255.255)',
        'set.if_bcast_off':     '(usado se Broadcast OFF)',
        'set.apply_artnet':     'APLICAR Art-Net',
        'set.an_need_ip':       'Em modo unicast indica o IP do nó.',
        'set.osc_in_hdr':       'OSC IN  (servidor — recebe da consola/iOS)',
        'set.osc_in_enable':    'Activar OSC IN',
        'set.osc_in_port':      'Porta UDP IN:',
        'set.osc_out_hdr':      'OSC OUT  (envia para a consola física)',
        'set.osc_out_enable':   'Activar OSC OUT',
        'set.osc_out_port':     'Porta UDP OUT:',
        'set.apply_osc':        'APLICAR OSC',
        'settings.midi_tab':    ' MIDI ',
        'set.midi_in':          'MIDI IN (recebe):',
        'set.midi_out':         'MIDI OUT (envia):',
        'set.midi_none':        '(desactivado)',
        'set.midi_refresh':     'Actualizar portas',
        'set.midi_apply':       'APLICAR MIDI',
        'set.midi_unavailable': 'MIDI indisponível — instala:\n'
                                '  pip install mido python-rtmidi',
        'set.midi_applied':     'MIDI aplicado',
        'set.midi_status':      'IN: {in_}\nOUT: {out}',
        'set.sacn_applied':     'sACN aplicado',
        'set.sacn_start_err':   'Erro ao iniciar sACN:\n{msg}',
        'set.sacn_stopped':     'sACN parado.',
        'set.an_applied':       'Art-Net aplicado',
        'set.an_start_err':     'Erro ao iniciar Art-Net:\n{msg}',
        'set.an_stopped':       'Art-Net parado.',
        'set.osc_applied':      'OSC aplicado',
        # ── Menu ──
        'menu.file':            'Ficheiro',
        'menu.new_show':        'Novo Show',
        'menu.open':            'Abrir…',
        'menu.save':            'Guardar',
        'menu.save_as':         'Guardar como…',
        'menu.import_ascii':    'Importar ASCII…',
        'menu.export_ascii':    'Exportar ASCII…',
        # ── USITT ASCII (v6.3.2) ──
        'ascii.export_title':   'Exportar ASCII',
        'ascii.export_warn':    'A exportação USITT ASCII leva só o que o '
                                'standard transporta: cues (tempos, texto, '
                                'AUTO, saltos, níveis), patch de intensidade, '
                                'grupos e submasters.\n\n'
                                'MIDI por cue, FX, looks, alcunhas, curvas e '
                                'halos NÃO vão no ficheiro — isso vive só no '
                                '.ldsk. A contagem dos saltos (LOOP) também '
                                'se perde (o LINK não conta voltas).\n\n'
                                'Continuar?',
        'ascii.export_done':    'Exportado:\n{path}\n\n'
                                '{cues} cues · {chans} canais no patch.',
        'ascii.export_err':     'Erro ao exportar ASCII:\n{msg}',
        'ascii.import_title':   'Importar ASCII',
        'ascii.import_confirm': 'A importação cria um show NOVO — o show '
                                'aberto perde-se se não estiver gravado.\n\n'
                                'Continuar?',
        'ascii.import_done':    'Importado:\n{path}\n\n'
                                '{cues} cues · {chans} canais no patch · '
                                '{ign} linhas ignoradas.',
        'ascii.import_ign_hdr': 'Ignoradas (primeiras):',
        'ascii.import_err':     'Erro ao importar ASCII:\n{msg}',
        'ascii.ft_all':         'Todos os ficheiros',
        'ascii.folw_title':     'FOLLOWON (AUTO)',
        'ascii.folw_export_q':  'Compensar os tempos do AUTO ao estilo '
                                'Eos/USITT?\n\n'
                                'SIM — Eos/USITT: o AUTO conta desde o '
                                'INÍCIO da memória anterior (soma-se o '
                                'tempo dela ao escrever).\n\n'
                                'NÃO — grandMA/MesaDeLux: escreve o valor '
                                'tal e qual (conta desde o FIM da '
                                'anterior).',
        'ascii.folw_import_q':  'O ficheiro não diz como conta o AUTO '
                                '(FOLLOWON).\n\n'
                                'Veio de uma Eos/USITT estrito? (o AUTO '
                                'conta do INÍCIO da memória anterior — '
                                'converte-se subtraindo o tempo dela)\n\n'
                                'SIM — Eos/USITT (compensa)\n'
                                'NÃO — grandMA e afins (valor directo)',
        'ascii.folw_used':      'FOLLOWON: {estilo}.',
        'ascii.folw_eos':       'estilo Eos/USITT (compensado)',
        'ascii.folw_directo':   'directo (grandMA/MesaDeLux)',
        'ascii.notas_hdr':      'Notas:',
        # ── PARTES (v6.3.3) ──
        'parte.btn':            'PARTE',
        'tree.parte':           'PARTE',
        'parte.title':          'Partes da memória',
        'parte.need_cue':       'Vai primeiro à memória que queres dividir '
                                '(a ZERO não se divide).',
        'parte.need_sel':       'Selecciona canais para criar uma parte.\n\n'
                                '(Com a memória já dividida, PARTE sem '
                                'selecção abre a lista Modificar/Apagar.)',
        'parte.cheia':          'A memória já tem as {max} partes todas.',
        'parte.dlg_title':      'PARTE — memória {num}',
        'parte.num':            'Nº da parte (2-8)',
        'parte.p1_nota':        'A parte 1 é sempre a divisão principal — '
                                'a própria memória (tempos na cuelist).',
        'parte.fade_in':        'Tempo IN (s)',
        'parte.fade_out':       'Tempo OUT (s)',
        'parte.delay_in':       'Atraso IN (s)',
        'parte.delay_out':      'Atraso OUT (s)',
        'parte.fx':             'FX (1-16, vazio = nenhum)',
        'parte.fx_fade':        '∿ FX acompanha os tempos da parte',
        'parte.fx_snap':        '⚡ FX imediato (dispara no GO)',
        'parte.texto':          'Texto (breve explicação)',
        'parte.ok':             'OK',
        'parte.cancel':         'Cancelar',
        'parte.mod':            'Modificar',
        'parte.del':            'Apagar a parte',
        'parte.fechar':         'Fechar',
        'parte.canais':         '{n} canais',
        'parte.mod_hint':       'PARTE {n} em edição: clica nos canais para '
                                'tirar/pôr (vermelho); PARTE abre os tempos; '
                                'OK grava, Cancelar aborta.',
        'parte.fx_unica':       'FX {n}: a marca antiga saiu (um FX, uma '
                                'marca por memória).',
        # ── DMX-IN (v6.4, Etapa 1: só escuta) ──
        'settings.din_tab':     ' DMX-In ',
        'din.title':            'DMX-In (escuta sACN)',
        'din.enable':           'Escutar DMX-In (sACN de outra mesa)',
        'din.univs':            'Universo(s), ex.: 1,2',
        'din.iface':            'Interface de escuta',
        'din.nota':             'Entra no programador (rosa) — gravas com '
                                'Comprar/Actualizar. Se receber e parar, '
                                'escolhe o IP da tua placa de rede (não '
                                '0.0.0.0). Mesa no mesmo PC: unicast p/ '
                                '127.0.0.1 + escolhe 127.0.0.1.',
        'din.apply':            'Aplicar DMX-In',
        'din.univs_err':        'Universos ilegíveis — escreve números '
                                'separados por vírgulas (ex.: 1,2).',
        'din.start_err':        'Erro ao arrancar a escuta:\n{msg}',
        'din.off':              'Escuta desligada.',
        'din.rx':               'A RECEBER',
        'din.silencio':         'Silêncio',
        'din.segurar':          'a segurar último look ({nome})',
        'din.sem_sinal':        'sem sinal',
        'din.aviso_out':        'Atenção: também estás a EMITIR no(s) '
                                'universo(s) {u} — os valores DMX-In '
                                'podem ser o teu próprio output, não a '
                                'mesa externa.',
        'din.no_release':       'DMX-In a entrar: não se liberta o '
                                'programador (desliga a escuta primeiro '
                                'em Configurações → DMX-In).',
        'menu.quit':            'Sair',
        'menu.desk':            'Mesa',
        'menu.patch':           'Renumerador…',
        'menu.total_channels':  'Total de Canais…',
        'menu.zero_cue':        'Memória ZERO no ciclo',
        'menu.settings':        'Configurações…',
        'menu.bo':              'Escuro',
        'menu.help':            'Ajuda',
        'menu.help_osc':        'Ajuda OSC (protocolo)…',
        'osc_help.title':       'Ajuda OSC — protocolo',
        'menu.clear_prog':      'Liberta',
        'menu.release_time':    'Tempo Liberta/Limpa…',
        # ── botões principais (glossário do autor; EN = termos próprios) ──
        'btn.all':              'TODOS',
        'btn.full':             'Máximo',
        'btn.zero':             'Zero',
        'btn.bo':               'ESCURO',
        'btn.release':          'LIBERTA',
        'btn.loopbreak':        'SOLTAR',
        'btn.loopbreak_n':      'SOLTAR {n}',
        'btn.clear':            'LIMPA',
        'btn.im_cueonly':       'CUE-ONLY',
        'btn.im_tracking':      'TRACKING',
        'btn.go':               '  VAI  ',
        'btn.goback':           '◀ RECUA',
        'btn.pause':            'PAUSA',
        'btn.resume':           'RETOMA',
        'btn.take':             'Comprar',
        'btn.update':           'Actualização',
        'btn.save':             'Guardar',
        'btn.goto':             'Ir Para',
        'btn.midi_on':          'MIDI ON',
        'btn.midi_off':         'MIDI OFF',
        'btn.delete':           'Apagar',
        'btn.delete_fx':        'Apagar FX',
        # ── etiquetas / painéis ──
        'ui.no_show':           'MESADELUX  |  Sem show carregado',
        'ui.snapshots':         'Retratos',
        'ui.snapshot_n':        'Retrato {n}',
        'ui.groups':            'Grupos',
        'ui.group_n':           'Grupo {n}',
        'ui.pre_n':             'Pré {n}',
        'fx.title':             'FX — Efeitos',
        'cue.zero_label':       '',
        'grid.on_letter':       'L',
        'fx.erase_step':        'Apagar passo',
        'fx.erase_step_q':      'Apagar o passo {n}?',
        # ── diálogo Total de Canais ──
        'showsize.title':       'Total de Canais',
        'showsize.msg_main':    'Número de canais actual: {cur}\n'
                                'Novo número (1 a {max}):',
        'showsize.heavy':       '\n(acima de 200 a app fica mais pesada — '
                                'só p/ teste)',
        'showsize.locked':      '\n\n⚠ Já existem cues/retratos/grupos '
                                'gravados.\nSó pode aumentar (não pode '
                                'reduzir).',
        'showsize.invalid_title': 'Inválido',
        'showsize.invalid_int': 'Insere um inteiro entre 1 e {max}.',
        'showsize.invalid_range': 'Tem de ser entre 1 e {max}.',
        'showsize.locked_title': 'Bloqueado',
        'showsize.locked_msg':  'Há memórias gravadas — não pode reduzir o '
                                'total de canais.\nPara reduzir, faz Novo Show.',
        # ── ChannelPatchDialog (tecla R) ──
        'cpatch.title':         'Renumerador — Canal {ch}',
        'cpatch.channel_n':     'Canal {ch}',
        'cpatch.alias':         'Alcunha (0 = nº do canal):',
        'cpatch.name':          'Nome (até 6 letras):',
        'multi.title':          'Vários canais ({n})',
        'multi.header':         'Aplicar a {n} canais seleccionados:',
        'multi.alc_note':       'Alcunha: incrementa por canal; «@» = a mesma '
                                'em todos (ex.: @601).',
        'cpatch.dmx8':          'DMX 8 bit (ex: 3 + 9 + 11):',
        'cpatch.dmx16':         'DMX 16 bit (fine; vazio = 8 bit):',
        'cpatch.default':       'Defeito (0-255; vazio = 0):',
        'cpatch.halo':          'Halo:',
        'cpatch.show':          'Mostrar:',
        'cpatch.curve':         'Curva:',
        # ── RetratoDialog ──
        'rdlg.title_look':      'Gravar Retrato',
        'rdlg.title_group':     'Gravar Grupo',
        'rdlg.label_title':     'Título:',
        'rdlg.save':            'Gravar',
        'sub.save_title':       'Gravar Submaster',
        'sub.name_prompt':      'Nome do submaster:',
        'sub.default_n':        'Sub {n}',
        # ── FXCreateDialog ──
        'fxc.title':            'Comprar FX {n}',
        'fxc.name':             'Nome:',
        'fxc.default_name':     'FX {n}',
        'fxc.mode':             'Modo:',
        'fxc.manual':           'Manual  (lista de passos em cadeia)',
        'fxc.dynamic':          'Dinâmico  (ciclo contínuo paramétrico)',
        'fxc.chaos':            'Caos  (selecção aleatória de canais)',
        # ── FXLinkDialog ──
        'fxl.title':            'FX na memória',
        'fxl.prompt':           'Nº do FX (1–{max}; vazio = tira a marca):',
        'fxl.recorded':         'Gravados: {list}',
        'fxl.immediate':        '⚡ imediato (entra/sai a seco)',
        'fxl.follow_fade':      '∿ acompanha o fade da memória',
        'fxl.invalid':          'Número inválido (1–{max}).',
        'fxl.range':            'O FX tem de ser de 1 a {max}.',
        # ── editor FX (manual + dinâmico) ──
        'fx.editor_cues':       'Memórias',
        'fx.editor_cues_xf':    'Memórias (XF)',
        'fx.editor_manual':     'Edição — {nome}  (manual)',
        'fx.editor_dyn':        'Edição — {nome}  (dinâmico)',
        'fx.editor_caos':       'Edição — {nome}  (caos)',
        'fx.col_step':          'Passo',
        'fx.col_fade':          'Fade',
        'fx.col_auto':          'Auto.',
        'fx.col_channels':      'Canais',
        'fx.bought':            'Canais comprados ({n}):  {txt}',
        'fx.no_channels':       'Sem canais — selecciona na grelha e '
                                'Comprar 2×.',
        'fxd.curve':            'Curva',
        'fxd.dir':              '  Dir.',
        'fxd.blocks':           '  Blocos',
        'fxd.attack':           'Ataque',
        'fxd.decay':            'Retirada',
        'fxd.bpm':              'BPM',
        'fxd.width':            'Carroagem',
        'fxd.v_high':           'V. alto',
        'fxd.v_low':            'V. baixo',
        'fxd.groups':           'Grupos',
        'fxd.chaos':            'Caos',
        'fxd.quant_min':        'Quant. mín',
        'fxd.quant_max':        'Quant. máx',
        'fxd.quant_note':       '(nº de canais sorteados; 0/0 = cintilação)',
        'fxd.chaos_size':       'Tam. caos',
        'fxd.chaos_size_note':  '(>0 anula a carroagem)',
        'fxd.cross':            'Cruzam.',
        'fxd.cross_note':       '(0=sem cruzar · 100≈simultâneo; não no caos)',
        'fxd.repeat':           'Repete',
        'fxd.blk_invalid':      'inválido',
        'fxd.blk_info':         '= {n} ch/bloco, {mm} tempos',
        'fxd.blk_one':          '= 1 tempo (sem efeito)',
        'fxd.rep_always':       '= muda sempre',
        'fxd.rep_hold':         '= mantém {seq} (cicla)',
        # ── cabeçalhos da cuelist ──
        'tree.num': 'Nº', 'tree.barr': 'B', 'tree.label': 'Deixa',
        'tree.in': 'Entr.', 'tree.out': 'Saí.', 'tree.auto': 'Auto.',
        'tree.loop': 'Salta', 'tree.fx': 'FX', 'tree.midi': 'MIDI',
        # ── MidiCueDialog (v6.3) ──
        'midi.title':           'Nota MIDI — Cue {n}',
        'midi.none':            'Sem MIDI',
        'midi.in':              'IN  (recebe nota → executa a cue)',
        'midi.out':             'OUT  (executa a cue → envia nota)',
        'midi.note':            'Nota (1–127)',
        'midi.delay':           'Atraso (s)',
        'midi.note_error':      'A nota tem de ser um inteiro 1–127.',
        'midi.delay_error':     'O atraso tem de ser em segundos (0–3600; '
                                'ex.: 0.5).',
        # ── erros genéricos ──
        'm.err_value':          'Valor inválido.',
        'm.err_values':         'Valores inválidos.',
        'm.err_number':         'Número inválido.',
        # ── renumeração inversa (vista DMX) ──
        'm.rev_title':          'Renumerar inverso',
        'm.rev_pick_one':       'Selecciona UM endereço DMX para renumerar.',
        'm.rev_prompt':         'DMX  U{univ}  endereço {addr}\nÉ controlado '
                                'pelo canal da mesa (vazio = nenhum):',
        'm.rev_bad_channel':    'Canal inválido.',
        'm.rev_channel_range':  'O canal tem de ser de 1 a {max}.',
        # ── renumerador por canal (R) ──
        'm.cp_pick_one':        'Selecciona UM canal para renumerar.\n(O '
                                'renumerador por canal só funciona com um '
                                'canal.)',
        'm.cp_moved':           'Endereço(s) retirado(s) do(s) canal(is): '
                                '{nums}',
        # ── FX: passos manuais ──
        'm.fx_delete_q':        'Apagar «{name}»?',
        'm.take_step_title':    'Comprar passo',
        'm.take_step_help':     'Para gravar passos: botão direito num FX '
                                'MANUAL abre a edição; depois Comprar 2× '
                                'grava a luz em cena.\n(Comprar + clique num '
                                'botão FX cria um FX novo.)',
        'm.take_nothing':       'Nada em cena para gravar — põe canais a '
                                'nível primeiro.',
        'm.update_step_title':  'Actualizar passo',
        'm.update_step_need':   'Abre a edição de um FX manual com passos e '
                                'selecciona o passo a actualizar.',
        'm.update_nothing':     'Nada em cena — põe canais a nível primeiro.',
        'm.update_arm_help':    'Actualização é 2 pressões seguidas no botão '
                                '(com um FX manual em edição e um passo '
                                'seleccionado):\nactualiza os níveis desse '
                                'passo com a luz em cena.',
        'm.zero_no_fx':         'A memória ZERO não lança FX.',
        'm.fxlink_empty':       'O FX {n} ainda está vazio — a marca fica '
                                'gravada mas só actua quando o comprares.',
        'm.fx_buy_title':       'Comprar selecção',
        'm.fx_buy_help':        'Selecciona canais na grelha (ou chama '
                                'grupos) — depois Comprar 2× compra a '
                                'selecção.',
        'm.fx_order_title':     'Actualizar ordem',
        'm.fx_order_help':      'Selecciona o(s) canal(is) a acrescentar à '
                                'ordem.\n(Comprar 2× recomeça a ordem do '
                                'zero.)',
        'm.fx_alltimes_title':  '{label} de TODOS os passos',
        'm.fx_alltimes_prompt': '{label} (s) — 0 a 60 — aplicar aos {n} '
                                'passos:',
        'm.fx_editstep_title':  'Editar passo',
        'm.fx_time_prompt':     '{label} (s) — 0 a 60:',
        # ── grupos ──
        'm.group_need_sel':     'Selecciona canais antes de gravar um grupo.',
        # ── apagar memórias ──
        'm.del_title':          'Apagar Memórias',
        'm.del_prompt':         'Memória(s) a apagar  (ex.:  1   |   1 ao 5   '
                                '|   1 + 4 + 5):',
        'm.del_short_title':    'Apagar',
        'm.del_indicate':       'Indica a(s) memória(s) a apagar.',
        'm.del_none':           'Nenhuma memória corresponde.',
        'm.undo_done':          '↶ Desfeito (Ctrl+Y refaz)',
        'm.redo_done':          '↷ Refeito',
        'm.undo_none':          'Nada para desfazer.',
        'm.del_confirm':        'Apagar {n} memória(s):  {nums}?',
        # ── actualizar memória ──
        'm.upd_position':       'Posiciona a barra na memória a actualizar '
                                '(com <<< / >>> ou VAI).',
        'm.upd_zero':           'A memória ZERO é sempre um escuro — não '
                                'guarda valores de canais.',
        'm.upd_confirm':        'Actualizar os valores da memória {n}?',
        # ── ir para ──
        'm.goto_prompt':        "Número da memória (ou 'zero') a ir:",
        'm.goto_zero_btn':      'Ir para ZERO',
        'm.goto_missing':       'Não existe a memória {n}.',
        # ── editar célula da cuelist ──
        'm.zero_title':         'Memória ZERO',
        'm.zero_no_renum':      'A memória ZERO é o escuro inicial e não pode '
                                'ser renumerada.',
        'm.zero_toggle':        'Usa a opção «Memória ZERO no ciclo» para a '
                                'activar/desactivar.',
        'm.barr_title':         'Barreira',
        'm.barr_zero':          'A memória ZERO não tem barreira.',
        'm.edit_in_title':      'Editar entrada',
        'm.edit_in_time':       'Tempo de entrada (s):',
        'm.edit_in_delay':      'Atraso à entrada (s):',
        'm.edit_out_title':     'Editar saída',
        'm.edit_out_time':      'Tempo de saída (s):',
        'm.edit_out_delay':     'Atraso à saída (s):',
        'm.edit_cue_title':     'Editar memória',
        'm.edit_auto_prompt':   'AUTO (s) — vazio = sem automático:',
        'm.edit_num_prompt':    'Número da memória (até 2 casas decimais):',
        # ── SALTAR (loop) ──
        'm.loop_title':         'SALTAR',
        'm.loop_zero':          'A memória ZERO não pode ter SALTAR.',
        'm.loop_edit_title':    'Editar SALTAR (loop)',
        'm.loop_target_prompt': 'Saltar p/ memória nº (vazio = sem salto):',
        'm.loop_count_prompt':  'Nº de saltos (0 ou vazio = eterno):',
        'm.loop_bad_num':       'Número de memória inválido.',
        'm.loop_backwards':     'O SALTAR tem de ser para uma memória '
                                'anterior (de número menor).',
        'm.loop_bad_count':     'Nº de saltos inválido.',
        # ── OSC ──
        'm.osc_install':        'Instala o pacote:\n  pip install python-osc',
        'm.osc_start_err':      'Erro ao iniciar OSC:\n{e}',
        # ── tempo do liberta (RELEASE) ──
        'm.rel_title':          'Tempo Liberta/Limpa',
        'm.rel_prompt':         'Fade do LIBERTA e LIMPA (segundos; 0 = imediato):',
        # ── novo show ──
        'm.new_title':          'Novo Show',
        'm.new_confirm':        'Descartar TODO o show actual\n(cues, '
                                'retratos, grupos, submasters, patch)?',
        'm.new_chan_prompt':    'Número de canais para o novo show\n(1 a '
                                '{max}, default 100; acima de 200 fica '
                                'pesado, só p/ teste):',
        'm.status_new':         'MESADELUX  |  Novo Show  |  {n} canais',
        # ── abrir / sair ──
        'm.open_err':           'Não foi possível abrir:\n{e}',
        'm.quit_title':         'Sair',
        'm.quit_unsaved':       'Há alterações por gravar.\n\nGuardar o show '
                                'antes de sair?',
        # ── Ajuda OSC — referência do protocolo (Etapa 2.5) ──
        'settings.osc_help_tab':  ' Ajuda OSC ',
        'osc_help.text': (
            'PROTOCOLO OSC — MesaDeLux v6.3\n'
            '═══════════════════════════════════════════════════════\n'
            'Controla a app a partir de consolas físicas, TouchOSC\n'
            'ou qualquer controlador Open Sound Control.\n'
            'N = canal / submaster / grupo / FX (base 1) — substitui-se pelo\n'
            '    número, ex.: /submaster/1 · /group/2/level · /fx/3/toggle\n'
            'i = inteiro · f = decimal · s = texto.\n'
            '\n'
            '── RECEBE (controlador → app) ──────────────────────────\n'
            'Playback / gravação (sem argumentos):\n'
            '  /go                  VAI — avança na cuelist\n'
            '  /back                RECUA — volta na cuelist\n'
            '  /pause               Pausa / Retoma\n'
            '  /blackout            Escuro (B.O.)\n'
            '  /clear               CLEAR (2 toques): 1º desselecciona;\n'
            '                       2º apaga o programador (azul)\n'
            '  /release             RELEASE (2 toques): 1º apaga o azul e\n'
            '                       desselecciona; 2º deita cue+FX ao zero\n'
            '                       (os submasters mantêm-se)\n'
            '  /clear/1  /clear/2   passo DIRECTO (1 botão/passo — fiável)\n'
            '  /release/1 /release/2  idem, sem depender do 2-toque\n'
            '  /loopbreak           LOOPBREAK — sai do loop activo\n'
            '  /rec/take            TAKE — arma/grava a memória (2 toques)\n'
            '  /rec/update          UPDATE — actualiza a memória\n'
            '  /rec/save            SAVE — grava o show\n'
            '  /rec/cancel          cancela a gravação\n'
            '  /show/size/request   (handshake) pede o estado completo\n'
            '\n'
            'Canais / níveis:\n'
            '  /channel/{N}/level   i(0-255) ou f(<=1.0 normaliz.; >1.0=0-255)\n'
            '  /intensity           {canal:i} {nivel:f} — nível ABSOLUTO\n'
            '  /level/adjust        i — passo +/- nos seleccionados (ex.: 5,-5)\n'
            '  /level/set           f — valor fixo nos seleccionados (0.5=50%)\n'
            '  /level/set/{pct}     0-100 no endereço (ex.: /level/set/50)\n'
            '  /level/up  /level/down   passo +/-5 (ou /level/up/{n})\n'
            '  /channel/select      i (canal; 0 = deselecciona)\n'
            '  /submaster/{N}       f  (<=1.0 -> %;  >1.0 -> 0-100)\n'
            '  /group/{N}/level     f\n'
            '  /group/{N}           chamar o grupo N (1-20) — no pressionar\n'
            '  /look/{N}            chamar o Look (Retrato) N (1-20)\n'
            '\n'
            'Cuelist — mover a barra SEM disparar (setas <<< / >>>):\n'
            '  /cue/back            <<<  memória anterior (sem fade)\n'
            '  /cue/go              >>>  memória seguinte (sem fade)\n'
            '  /cue/fade_in         f (segundos)\n'
            '  /cue/fade_out        f (segundos)\n'
            '  /cue/state/request   pede o estado actual da cue\n'
            '\n'
            'Highlight / teste de saída:\n'
            '  /highlight           i(0|1) — liga/desliga Highlight\n'
            '                       (na vista DMX = teste de saída DMX)\n'
            '  /highlight/level     i(0-255) — nível dos destacados\n'
            '  /dmx/highlight/addr  i(1-512; 0=nenhum) — endereço a testar\n'
            '\n'
            'FX (página de efeitos):\n'
            '  /fx/mode             i(0|1) — entra/sai da página FX\n'
            '  /fx/group            i — selecciona o grupo de 4 FX\n'
            '  /fx/{N}/toggle       liga/desliga o FX N (1-16)\n'
            '\n'
            '── ENVIA (app → controlador, feedback) ─────────────────\n'
            '  /channel/{N}/name    s  (<=6 caracteres)\n'
            '  /channel/{N}/alias   i\n'
            '  /channel/{N}/curve   s\n'
            '  /channel/{N}/level   i  (0-255)\n'
            '  /channel/patched     s  (csv "1,2,5,10")\n'
            '  /channel/selected    i  (canal seleccionado; 0 = nenhum)\n'
            '  /fx/{N}/state        i(0|1) — estado do FX N (acender a tecla)\n'
            '  /show/size           i  (nº de canais do show)\n'
            '  /page                s i  ("dmx" univ | "mesa" 0)\n'
            '  /dmx/browse          i  (endereço em foco na vista DMX)\n'
            '  /cue/state           s s f f  (num, label, fade_in, fade_out)\n'
            '  /cue/state/{key}     f\n'
            '\n'
            '── EXEMPLOS de sintaxe ─────────────────────────────────\n'
            '  /channel/5/level 200      canal 5 a 200 (0-255)\n'
            '  /level/up                 sobe +5 nos seleccionados\n'
            '  /level/down               desce -5 nos seleccionados\n'
            '  /level/set/50             seleccionados a 50 %\n'
            '  /submaster/1 0.8          submaster 1 a 80 %\n'
            '  /group/2/level 1.0        grupo 2 a full\n'
            '  /fx/3/toggle              liga/desliga o FX 3\n'
            '\n'
            '═══════════════════════════════════════════════════════\n'
            'Porta OSC IN (defeito): 8080     Porta OUT: 8081\n'
            'Para configurar as portas: Configurações -> OSC\n'
        ),
    },
    'en': {
        'app.title':            'MESADELUX — Lighting Desk',
        'settings.title':       'Settings',
        'settings.lang_tab':    ' Language ',
        'settings.lang_label':  'Interface language:',
        'settings.lang_note':   'The language change fully applies when the '
                                'application is restarted.',
        'settings.lang_apply':  'APPLY LANGUAGE',
        'settings.cl_tab':      ' Cuelist ',
        'settings.cl_label':    'Main cuelist model:',
        'settings.cl_cueonly':  'Cue-only (theatre) — each cue is a self-'
                                'contained intensity look',
        'settings.cl_tracking': 'Tracking (classic) — everything LTP + tracking',
        'settings.cl_note':     'Cue-only: intensities (0-100%) are sealed per '
                                'cue (jumping in the script always gives the '
                                'same look); attributes (0-255) track and BLOCK '
                                'applies only to them. Saved in the show.',
        'settings.cl_apply':    'APPLY MODEL',
        'lang.pt':              'Português',
        'lang.en':              'English',
        'common.close':         'Close',
        'common.apply_all':     'Apply all + Close',
        'common.all_files':     'All',
        # ── parsers / Art-Net ──
        'artnet.unicast_needs_ip': 'Art-Net unicast requires a destination IP.',
        # ── GDTFDialog ──
        'gdtf.title':           'Import GDTF → Patch',
        'gdtf.open_btn':        'Open GDTF…',
        'gdtf.no_file':         '(no file)',
        'gdtf.footprint_label': 'Footprint (DIM is 0-100 %; the rest 0-255; '
                                '«16» = 16 bit):',
        'gdtf.copy_btn':        'Copy footprint',
        'gdtf.patch_btn':       'Use this footprint',
        'gdtf.modes_label':     'DMX modes:',
        'gdtf.open_title':      'Open GDTF',
        'gdtf.read_error':      'Could not read:\n{e}',
        'gdtf.mode_header':     'Mode: {nome}   ({n} channels)',
        'gdtf.col_header':      'GDTF / name',
        'gdtf.copied':          'Footprint copied:\n\n{s}',
        'gdtf.pick_first':      'Open a GDTF and pick a mode first.',
        # ── RepetirFixtureDialog ──
        'rep.title':            'Repeat Fixture',
        'rep.channels_label':   'Channels (names separated by spaces; number '
                                'of\nnames = number of fixture channels):',
        'rep.hint':             '«16» at the end = 16 bit (e.g. PAN16).  «@N» '
                                'at the end = default (e.g. ZOOM@200).\nDIM '
                                '0-100 %, others 0-255.  Defaults: colours '
                                '255, PAN/TILT/ZOOM/FOCUS 127.',
        'rep.f_ch':             'Start channel:',
        'rep.f_univ':           'Universe:',
        'rep.f_addr':           'Start DMX:',
        'rep.f_qtd':            'Quantity:',
        'rep.f_alc':            'Alias (opt.):',
        'rep.alc_hint':         '(+1 per fixture: 601→610; all parameters of '
                                'the same fixture share it)',
        'rep.cycle_halo':       'Cycle halo colour per fixture',
        'rep.repeat_btn':       'Repeat',
        'rep.import_gdtf':      'Import GDTF…',
        'rep.need_one':         'Define at least one channel (name).',
        'rep.must_numbers':     'Channel/Universe/DMX/Quantity must be '
                                'numbers.',
        'rep.must_ge1':         'Values must be ≥ 1.',
        'common.cancel':        'Cancel',
        # ── PatchDialog (patch) ──
        'patch.title':          'Patch — Channels → DMX',
        'patch.hint':           "DMX accepts several addresses separated by "
                                "'+'  (e.g.  3 + 9 + 11).\nA channel is 16 "
                                "bit if it has address(es) in the 16 bit "
                                "field.\nRange: drag the left button down a "
                                "value column, type in the 1st cell and press "
                                "Enter (empty = clears the range).\n  · Alias "
                                "/ 16 bit → ascending (+1 per row)   "
                                "· Univ / Default → all with the same value."
                                "\n  · 8 bit → channels MARKED in green "
                                "(16 bit) take 2 addresses (pairs 1,2 · "
                                "3,4 · …) and the 16 bit cell is written "
                                "automatically. RIGHT-click the 16 bit "
                                "cell to mark/unmark; the patch, names "
                                "…16 and Repeat Fixture mark by "
                                "themselves."
                                "\nClick the HEADER to select the whole "
                                "column (2nd click undoes). Enter on a "
                                "single cell jumps to the one below.",
        'patch.col_channel':    'Channel',
        'patch.col_alias':      'Alias',
        'patch.col_name':       'Name',
        'patch.col_univ':       'Univ',
        'patch.col_dmx8':       'DMX 8 bit',
        'patch.col_dmx16':      'DMX 16 bit',
        'patch.col_default':    'Default',
        'patch.col_halo':       'Halo',
        'patch.col_show':       'Display',
        'patch.col_curve':      'Curve',
        'patch.clear_all':      'Clear All',
        'patch.clear_all_q':    'Clear the whole patch (all channels left '
                                'without an address)?',
        'patch.one_to_one':     '1 to 1',
        'patch.repeat_fixture': 'Repeat Fixture…',
        'patch.apply':          'Apply',
        'patch.halo_none':      '(none)',
        'patch.filled':         '{n} channels filled.',
        'patch.over':           '{n} skipped (above channel {max}).',
        'patch.skipped':        '{n} skipped (DMX above 512).',
        'patch.moved':          '{n} channel(s) lost already-used addresses.',
        'patch.review':         '\n\nReview and press Apply to save into '
                                'the patch.',
        'patch.warn_title':     'Patch',
        'patch.dropped':        '{n} address(es) outside 1–512 ignored.',
        'patch.dups':           'Duplicate addresses removed (a DMX address '
                                'can only be on one channel) — channels: '
                                '{nums}.',
        # ── RecordCueDialog ──
        'rec.title':            'Save Cue',
        'rec.f_num':            'Number:',
        'rec.f_label':          'Label:',
        'rec.f_fade_in':        'Fade in (s):',
        'rec.f_delay_in':       'Delay in (s):',
        'rec.f_fade_out':       'Fade out (s):',
        'rec.f_delay_out':      'Delay out (s):',
        'rec.f_auto':           'AUTO (s):',
        'rec.auto_note':        '(AUTO empty = no auto-follow;\n 0 = starts '
                                'right after the transition)',
        'rec.record_btn':       'SAVE',
        'rec.num_error':        'Number, times and AUTO must be numeric.',
        'common.error':         'Error',
        # ── halo colours (LABEL; the stored value is always the key) ──
        'halo.vermelho': 'red', 'halo.laranja': 'orange',
        'halo.amarelo': 'yellow', 'halo.verde': 'green',
        'halo.ciano': 'cyan', 'halo.azul': 'blue',
        'halo.magenta': 'magenta', 'halo.branco': 'white',
        'halo.cinzento': 'grey',
        # ── curves (LABEL; the stored value is always the token) ──
        'curve.linear': 'linear', 'curve.rele': 'on/off', 'curve.ligado': 'on',
        # ── SettingsDialog ──
        'common.ok':            'OK',
        'set.sacn_enable':      'Enable sACN',
        'set.univ_auto':        'Automatic universes (follow the patch)',
        'set.now_out':          'Now sending: {u}',
        'set.univ_manual':      'Manual universes (up to 4):',
        'set.unicast_ip':       'Unicast IP:',
        'set.if_multicast_off': '(used if Multicast OFF)',
        'set.iface':            'Interface (output IP):',
        'set.iface_note':       '(lighting network adapter; empty = auto)',
        'set.apply_sacn':       'APPLY sACN',
        'set.an_enable':        'Enable Art-Net (parallel to sACN)',
        'set.origin_auto':      'auto',
        'set.origin_manual':    'manual',
        'set.an_univ':          'Universes ({origem}): {u}\n'
                                'Desk U1 → Art-Net 0, U2 → 1, …',
        'set.an_bcast':         'Broadcast (255.255.255.255)',
        'set.if_bcast_off':     '(used if Broadcast OFF)',
        'set.apply_artnet':     'APPLY Art-Net',
        'set.an_need_ip':       'In unicast mode, enter the node IP.',
        'set.osc_in_hdr':       'OSC IN  (server — receives from console/iOS)',
        'set.osc_in_enable':    'Enable OSC IN',
        'set.osc_in_port':      'UDP IN port:',
        'set.osc_out_hdr':      'OSC OUT  (sends to the physical console)',
        'set.osc_out_enable':   'Enable OSC OUT',
        'set.osc_out_port':     'UDP OUT port:',
        'set.apply_osc':        'APPLY OSC',
        'settings.midi_tab':    ' MIDI ',
        'set.midi_in':          'MIDI IN (receive):',
        'set.midi_out':         'MIDI OUT (send):',
        'set.midi_none':        '(disabled)',
        'set.midi_refresh':     'Refresh ports',
        'set.midi_apply':       'APPLY MIDI',
        'set.midi_unavailable': 'MIDI unavailable — install:\n'
                                '  pip install mido python-rtmidi',
        'set.midi_applied':     'MIDI applied',
        'set.midi_status':      'IN: {in_}\nOUT: {out}',
        'set.sacn_applied':     'sACN applied',
        'set.sacn_start_err':   'Error starting sACN:\n{msg}',
        'set.sacn_stopped':     'sACN stopped.',
        'set.an_applied':       'Art-Net applied',
        'set.an_start_err':     'Error starting Art-Net:\n{msg}',
        'set.an_stopped':       'Art-Net stopped.',
        'set.osc_applied':      'OSC applied',
        # ── Menu ──
        'menu.file':            'File',
        'menu.new_show':        'New Show',
        'menu.open':            'Open…',
        'menu.save':            'Save',
        'menu.save_as':         'Save As…',
        'menu.import_ascii':    'Import ASCII…',
        'menu.export_ascii':    'Export ASCII…',
        # ── USITT ASCII (v6.3.2) ──
        'ascii.export_title':   'Export ASCII',
        'ascii.export_warn':    'USITT ASCII export carries only what the '
                                'standard can hold: cues (times, text, AUTO, '
                                'jumps, levels), intensity patch, groups and '
                                'submasters.\n\n'
                                'Per-cue MIDI, FX, looks, nicknames, curves '
                                'and halos do NOT travel — those live in the '
                                '.ldsk only. The LOOP jump count is also '
                                'lost (LINK has no lap counter).\n\n'
                                'Continue?',
        'ascii.export_done':    'Exported:\n{path}\n\n'
                                '{cues} cues · {chans} channels patched.',
        'ascii.export_err':     'Error exporting ASCII:\n{msg}',
        'ascii.import_title':   'Import ASCII',
        'ascii.import_confirm': 'Importing creates a NEW show — the open '
                                'show is lost if not saved.\n\nContinue?',
        'ascii.import_done':    'Imported:\n{path}\n\n'
                                '{cues} cues · {chans} channels patched · '
                                '{ign} lines ignored.',
        'ascii.import_ign_hdr': 'Ignored (first ones):',
        'ascii.import_err':     'Error importing ASCII:\n{msg}',
        'ascii.ft_all':         'All files',
        'ascii.folw_title':     'FOLLOWON (AUTO)',
        'ascii.folw_export_q':  'Compensate AUTO times the Eos/USITT '
                                'way?\n\n'
                                'YES — Eos/USITT: the AUTO counts from '
                                'the START of the previous cue (its time '
                                'is added on write).\n\n'
                                'NO — grandMA/MesaDeLux: writes the value '
                                'as-is (counts from the END of the '
                                'previous cue).',
        'ascii.folw_import_q':  'The file does not say how the AUTO '
                                '(FOLLOWON) counts.\n\n'
                                'Does it come from a strict Eos/USITT '
                                'desk? (AUTO counts from the START of '
                                'the previous cue — converted by '
                                'subtracting its time)\n\n'
                                'YES — Eos/USITT (compensate)\n'
                                'NO — grandMA and alike (value as-is)',
        'ascii.folw_used':      'FOLLOWON: {estilo}.',
        'ascii.folw_eos':       'Eos/USITT style (compensated)',
        'ascii.folw_directo':   'as-is (grandMA/MesaDeLux)',
        'ascii.notas_hdr':      'Notes:',
        # ── PARTS (v6.3.3) ──
        'parte.btn':            'PART',
        'tree.parte':           'PART',
        'parte.title':          'Cue parts',
        'parte.need_cue':       'Go to the cue you want to split first '
                                '(ZERO cannot be split).',
        'parte.need_sel':       'Select channels to create a part.\n\n'
                                '(With the cue already split, PART with no '
                                'selection opens the Modify/Delete list.)',
        'parte.cheia':          'The cue already has all {max} parts.',
        'parte.dlg_title':      'PART — cue {num}',
        'parte.num':            'Part number (2-8)',
        'parte.p1_nota':        'Part 1 is always the main division — '
                                'the cue itself (times in the cuelist).',
        'parte.fade_in':        'Time IN (s)',
        'parte.fade_out':       'Time OUT (s)',
        'parte.delay_in':       'Delay IN (s)',
        'parte.delay_out':      'Delay OUT (s)',
        'parte.fx':             'FX (1-16, empty = none)',
        'parte.fx_fade':        '∿ FX follows the part’s times',
        'parte.fx_snap':        '⚡ FX immediate (fires on GO)',
        'parte.texto':          'Text (brief note)',
        'parte.ok':             'OK',
        'parte.cancel':         'Cancel',
        'parte.mod':            'Modify',
        'parte.del':            'Delete part',
        'parte.fechar':         'Close',
        'parte.canais':         '{n} channels',
        'parte.mod_hint':       'PART {n} editing: click channels to '
                                'remove/add (red); PART opens the times; '
                                'OK saves, Cancel aborts.',
        'parte.fx_unica':       'FX {n}: previous mark removed (one FX, '
                                'one mark per cue).',
        # ── DMX-IN (v6.4, stage 1: listen only) ──
        'settings.din_tab':     ' DMX-In ',
        'din.title':            'DMX-In (sACN listen)',
        'din.enable':           'Listen to DMX-In (sACN from another desk)',
        'din.univs':            'Universe(s), e.g. 1,2',
        'din.iface':            'Listen interface',
        'din.nota':             'Feeds the programmer (pink) — record with '
                                'Take/Update. If it receives then stops, '
                                'pick your network card IP (not 0.0.0.0). '
                                'Source on the same PC: unicast to '
                                '127.0.0.1 + pick 127.0.0.1.',
        'din.apply':            'Apply DMX-In',
        'din.univs_err':        'Unreadable universes — write numbers '
                                'separated by commas (e.g. 1,2).',
        'din.start_err':        'Error starting the listener:\n{msg}',
        'din.off':              'Listening off.',
        'din.rx':               'RECEIVING',
        'din.silencio':         'Silence',
        'din.segurar':          'holding last look ({nome})',
        'din.sem_sinal':        'no signal',
        'din.aviso_out':        'Warning: you are also OUTPUTTING on '
                                'universe(s) {u} — the DMX-In values may '
                                'be your own output, not the external '
                                'desk.',
        'din.no_release':       'DMX-In incoming: the programmer is not '
                                'released (turn the listener off first in '
                                'Settings → DMX-In).',
        'menu.quit':            'Quit',
        'menu.desk':            'Desk',
        'menu.patch':           'Patch…',
        'menu.total_channels':  'Total Channels…',
        'menu.zero_cue':        'ZERO cue in the loop',
        'menu.settings':        'Settings…',
        'menu.bo':              'B.O.',
        'menu.help':            'Help',
        'menu.help_osc':        'OSC Help (protocol)…',
        'osc_help.title':       'OSC Help — protocol',
        'menu.clear_prog':      'Release',
        'menu.release_time':    'RELEASE/CLEAR time…',
        # ── main buttons (author glossary) ──
        'btn.all':              'ALL',
        'btn.full':             'FULL',
        'btn.zero':             'Zero',
        'btn.bo':               'B.O.',
        'btn.release':          'RELEASE',
        'btn.loopbreak':        'LOOPBREAK',
        'btn.loopbreak_n':      'LOOPBREAK {n}',
        'btn.clear':            'CLEAR',
        'btn.im_cueonly':       'CUE-ONLY',
        'btn.im_tracking':      'TRACKING',
        'btn.go':               '  GO  ',
        'btn.goback':           '◀ GOBACK',
        'btn.pause':            'PAUSE',
        'btn.resume':           'RESUME',
        'btn.take':             'TAKE',
        'btn.update':           'UPDATE',
        'btn.save':             'BACKUP',
        'btn.goto':             'GOTO',
        'btn.midi_on':          'MIDI ON',
        'btn.midi_off':         'MIDI OFF',
        'btn.delete':           'DELETE',
        'btn.delete_fx':        'DELETE FX',
        # ── labels / panels ──
        'ui.no_show':           'MESADELUX  |  No show loaded',
        'ui.snapshots':         'Looks',
        'ui.snapshot_n':        'Look {n}',
        'ui.groups':            'Groups',
        'ui.group_n':           'Group {n}',
        'ui.pre_n':             'SET {n}',
        'fx.title':             'FX — Effects',
        'cue.zero_label':       '',
        'grid.on_letter':       'O',
        'fx.erase_step':        'Erase step',
        'fx.erase_step_q':      'Erase step {n}?',
        # ── Total Channels dialog ──
        'showsize.title':       'Total Channels',
        'showsize.msg_main':    'Current channels: {cur}\n'
                                'New number (1 to {max}):',
        'showsize.heavy':       '\n(above 200 the app gets heavier — '
                                'test only)',
        'showsize.locked':      '\n\n⚠ Cues/looks/groups already recorded.\n'
                                'You can only increase (cannot reduce).',
        'showsize.invalid_title': 'Invalid',
        'showsize.invalid_int': 'Enter an integer between 1 and {max}.',
        'showsize.invalid_range': 'Must be between 1 and {max}.',
        'showsize.locked_title': 'Locked',
        'showsize.locked_msg':  'There are recordings — you cannot reduce the '
                                'total channels.\nTo reduce, do New Show.',
        # ── ChannelPatchDialog (R key) ──
        'cpatch.title':         'Patch — Channel {ch}',
        'cpatch.channel_n':     'Channel {ch}',
        'cpatch.alias':         'Alias (0 = channel no.):',
        'cpatch.name':          'Name (up to 6 letters):',
        'multi.title':          'Multiple channels ({n})',
        'multi.header':         'Apply to {n} selected channels:',
        'multi.alc_note':       'Alias: increments per channel; «@» = same for '
                                'all (e.g. @601).',
        'cpatch.dmx8':          'DMX 8 bit (e.g. 3 + 9 + 11):',
        'cpatch.dmx16':         'DMX 16 bit (fine; empty = 8 bit):',
        'cpatch.default':       'Default (0-255; empty = 0):',
        'cpatch.halo':          'Halo:',
        'cpatch.show':          'Display:',
        'cpatch.curve':         'Curve:',
        # ── RetratoDialog ──
        'rdlg.title_look':      'TAKE Look',
        'rdlg.title_group':     'TAKE Group',
        'rdlg.label_title':     'Title:',
        'rdlg.save':            'TAKE',
        'sub.save_title':       'TAKE Submaster',
        'sub.name_prompt':      'Submaster name:',
        'sub.default_n':        'Sub {n}',
        # ── FXCreateDialog ──
        'fxc.title':            'TAKE FX {n}',
        'fxc.name':             'Name:',
        'fxc.default_name':     'FX {n}',
        'fxc.mode':             'Mode:',
        'fxc.manual':           'Manual  (chained step list)',
        'fxc.dynamic':          'Dynamic  (parametric continuous cycle)',
        'fxc.chaos':            'Chaos  (random channel selection)',
        # ── FXLinkDialog ──
        'fxl.title':            'FX on the cue',
        'fxl.prompt':           'FX no. (1–{max}; empty = remove mark):',
        'fxl.recorded':         'Recorded: {list}',
        'fxl.immediate':        '⚡ immediate (hard in/out)',
        'fxl.follow_fade':      '∿ follows the cue fade',
        'fxl.invalid':          'Invalid number (1–{max}).',
        'fxl.range':            'FX must be from 1 to {max}.',
        # ── FX editor (manual + dynamic) ──
        'fx.editor_cues':       'Cues',
        'fx.editor_cues_xf':    'Cues (XF)',
        'fx.editor_manual':     'Editing — {nome}  (manual)',
        'fx.editor_dyn':        'Editing — {nome}  (dynamic)',
        'fx.editor_caos':       'Editing — {nome}  (chaos)',
        'fx.col_step':          'Step',
        'fx.col_fade':          'Fade',
        'fx.col_auto':          'Auto.',
        'fx.col_channels':      'Channels',
        'fx.bought':            'Channels taken ({n}):  {txt}',
        'fx.no_channels':       'No channels — select on the grid and '
                                'TAKE 2×.',
        'fxd.curve':            'Curve',
        'fxd.dir':              '  Dir.',
        'fxd.blocks':           '  Blocks',
        'fxd.attack':           'Attack',
        'fxd.decay':            'Decay',
        'fxd.bpm':              'BPM',
        'fxd.width':            'Width',
        'fxd.v_high':           'V. high',
        'fxd.v_low':            'V. low',
        'fxd.groups':           'Groups',
        'fxd.chaos':            'Chaos',
        'fxd.quant_min':        'Qty. min',
        'fxd.quant_max':        'Qty. max',
        'fxd.quant_note':       '(channels drawn; 0/0 = shimmer)',
        'fxd.chaos_size':       'Chaos size',
        'fxd.chaos_size_note':  '(>0 overrides Width)',
        'fxd.cross':            'Cross',
        'fxd.cross_note':       '(0=no cross · 100≈simultaneous; not in chaos)',
        'fxd.repeat':           'Repeat',
        'fxd.blk_invalid':      'invalid',
        'fxd.blk_info':         '= {n} ch/block, {mm} beats',
        'fxd.blk_one':          '= 1 beat (no effect)',
        'fxd.rep_always':       '= always changes',
        'fxd.rep_hold':         '= holds {seq} (cycles)',
        # ── cuelist headers ──
        'tree.num': 'No.', 'tree.barr': 'B', 'tree.label': 'Label',
        'tree.in': 'In', 'tree.out': 'Out', 'tree.auto': 'Auto',
        'tree.loop': 'Loop', 'tree.fx': 'FX', 'tree.midi': 'MIDI',
        # ── MidiCueDialog (v6.3) ──
        'midi.title':           'MIDI Note — Cue {n}',
        'midi.none':            'No MIDI',
        'midi.in':              'IN  (receive note → run the cue)',
        'midi.out':             'OUT  (run the cue → send note)',
        'midi.note':            'Note (1–127)',
        'midi.delay':           'Delay (s)',
        'midi.note_error':      'Note must be an integer 1–127.',
        'midi.delay_error':     'Delay must be in seconds (0–3600; e.g. 0.5).',
        # ── generic errors ──
        'm.err_value':          'Invalid value.',
        'm.err_values':         'Invalid values.',
        'm.err_number':         'Invalid number.',
        # ── reverse patch (DMX view) ──
        'm.rev_title':          'Reverse patch',
        'm.rev_pick_one':       'Select ONE DMX address to repatch.',
        'm.rev_prompt':         'DMX  U{univ}  address {addr}\nControlled by '
                                'desk channel (empty = none):',
        'm.rev_bad_channel':    'Invalid channel.',
        'm.rev_channel_range':  'Channel must be from 1 to {max}.',
        # ── per-channel patch (R) ──
        'm.cp_pick_one':        'Select ONE channel to patch.\n(Per-channel '
                                'patch only works with one channel.)',
        'm.cp_moved':           'Address(es) removed from channel(s): {nums}',
        # ── FX: manual steps ──
        'm.fx_delete_q':        'Delete «{name}»?',
        'm.take_step_title':    'TAKE step',
        'm.take_step_help':     'To record steps: right-click a MANUAL FX to '
                                'open editing; then TAKE 2× records the stage '
                                'look.\n(TAKE + click an FX button creates a '
                                'new FX.)',
        'm.take_nothing':       'Nothing on stage to record — set channels to '
                                'a level first.',
        'm.update_step_title':  'Update step',
        'm.update_step_need':   'Open a manual FX with steps and select the '
                                'step to update.',
        'm.update_nothing':     'Nothing on stage — set channels to a level '
                                'first.',
        'm.update_arm_help':    'UPDATE is 2 presses on the button (with a '
                                'manual FX in editing and a step selected):\n'
                                "it updates that step's levels with the stage "
                                'look.',
        'm.zero_no_fx':         'The ZERO cue does not trigger FX.',
        'm.fxlink_empty':       'FX {n} is still empty — the mark is saved '
                                'but only acts once you TAKE it.',
        'm.fx_buy_title':       'TAKE selection',
        'm.fx_buy_help':        'Select channels on the grid (or call '
                                'groups) — then TAKE 2× takes the selection.',
        'm.fx_order_title':     'Update order',
        'm.fx_order_help':      'Select the channel(s) to add to the order.\n'
                                '(TAKE 2× restarts the order from scratch.)',
        'm.fx_alltimes_title':  '{label} of ALL steps',
        'm.fx_alltimes_prompt': '{label} (s) — 0 to 60 — apply to {n} steps:',
        'm.fx_editstep_title':  'Edit step',
        'm.fx_time_prompt':     '{label} (s) — 0 to 60:',
        # ── groups ──
        'm.group_need_sel':     'Select channels before saving a group.',
        # ── delete cues ──
        'm.del_title':          'Delete Cues',
        'm.del_prompt':         'Cue(s) to delete  (e.g.  1   |   1 thru 5   |  '
                                ' 1 + 4 + 5):',
        'm.del_short_title':    'Delete',
        'm.del_indicate':       'Indicate the cue(s) to delete.',
        'm.del_none':           'No cue matches.',
        'm.undo_done':          '↶ Undone (Ctrl+Y redoes)',
        'm.redo_done':          '↷ Redone',
        'm.undo_none':          'Nothing to undo.',
        'm.del_confirm':        'Delete {n} cue(s):  {nums}?',
        # ── update cue ──
        'm.upd_position':       'Position the bar on the cue to update (with '
                                '<<< / >>> or GO).',
        'm.upd_zero':           'The ZERO cue is always a blackout — it does '
                                'not store channel values.',
        'm.upd_confirm':        'Update the values of cue {n}?',
        # ── goto ──
        'm.goto_prompt':        "Cue number (or 'zero') to go to:",
        'm.goto_zero_btn':      'Go to ZERO',
        'm.goto_missing':       'Cue {n} does not exist.',
        # ── edit cuelist cell ──
        'm.zero_title':         'ZERO cue',
        'm.zero_no_renum':      'The ZERO cue is the initial blackout and '
                                'cannot be renumbered.',
        'm.zero_toggle':        'Use the «ZERO cue in the loop» option to '
                                'enable/disable it.',
        'm.barr_title':         'Barrier',
        'm.barr_zero':          'The ZERO cue has no barrier.',
        'm.edit_in_title':      'Edit fade in',
        'm.edit_in_time':       'Fade in time (s):',
        'm.edit_in_delay':      'Delay in (s):',
        'm.edit_out_title':     'Edit fade out',
        'm.edit_out_time':      'Fade out time (s):',
        'm.edit_out_delay':     'Delay out (s):',
        'm.edit_cue_title':     'Edit cue',
        'm.edit_auto_prompt':   'AUTO (s) — empty = no auto-follow:',
        'm.edit_num_prompt':    'Cue number (up to 2 decimals):',
        # ── LOOP (Saltar) ──
        'm.loop_title':         'LOOP',
        'm.loop_zero':          'The ZERO cue cannot have a LOOP.',
        'm.loop_edit_title':    'Edit LOOP',
        'm.loop_target_prompt': 'Loop to cue no. (empty = no loop):',
        'm.loop_count_prompt':  'Number of loops (0 or empty = forever):',
        'm.loop_bad_num':       'Invalid cue number.',
        'm.loop_backwards':     'The LOOP must target an earlier cue (lower '
                                'number).',
        'm.loop_bad_count':     'Invalid loop count.',
        # ── OSC ──
        'm.osc_install':        'Install the package:\n  pip install '
                                'python-osc',
        'm.osc_start_err':      'Error starting OSC:\n{e}',
        # ── release time ──
        'm.rel_title':          'RELEASE/CLEAR time',
        'm.rel_prompt':         'RELEASE and CLEAR fade (seconds; 0 = immediate):',
        # ── new show ──
        'm.new_title':          'New Show',
        'm.new_confirm':        'Discard the WHOLE current show\n(cues, '
                                'looks, groups, submasters, patch)?',
        'm.new_chan_prompt':    'Number of channels for the new show\n(1 to '
                                '{max}, default 100; above 200 it gets heavy, '
                                'test only):',
        'm.status_new':         'MESADELUX  |  New Show  |  {n} channels',
        # ── open / quit ──
        'm.open_err':           'Could not open:\n{e}',
        'm.quit_title':         'Quit',
        'm.quit_unsaved':       'There are unsaved changes.\n\nSave the show '
                                'before quitting?',
        # ── OSC Help — protocol reference (Step 2.5) ──
        'settings.osc_help_tab':  ' OSC Help ',
        'osc_help.text': (
            'OSC PROTOCOL — MesaDeLux v6.3\n'
            '═══════════════════════════════════════════════════════\n'
            'Control the app from physical consoles, TouchOSC,\n'
            'or any Open Sound Control-compatible controller.\n'
            'N = channel / submaster / group / FX (1-based) — replace with\n'
            '    the number, e.g. /submaster/1 · /group/2/level · /fx/3/toggle\n'
            'i = integer · f = float · s = string.\n'
            '\n'
            '── RECEIVES (controller → app) ─────────────────────────\n'
            'Playback / recording (no arguments):\n'
            '  /go                  GO — advance in cuelist\n'
            '  /back                GOBACK — step back in cuelist\n'
            '  /pause               Pause / Resume\n'
            '  /blackout            Blackout (B.O.)\n'
            '  /clear               CLEAR (2 taps): 1st deselect;\n'
            '                       2nd clear the programmer (blue)\n'
            '  /release             RELEASE (2 taps): 1st clear blue and\n'
            '                       deselect; 2nd bring cue+FX to zero\n'
            '                       (submasters are kept)\n'
            '  /clear/1  /clear/2   DIRECT step (1 button/step — reliable)\n'
            '  /release/1 /release/2  same, no double-tap timing needed\n'
            '  /loopbreak           LOOPBREAK — exit the active loop\n'
            '  /rec/take            TAKE — arm/record cue (2 presses)\n'
            '  /rec/update          UPDATE — update the cue\n'
            '  /rec/save            SAVE — save the show\n'
            '  /rec/cancel          cancel recording\n'
            '  /show/size/request   (handshake) request full state\n'
            '\n'
            'Channels / levels:\n'
            '  /channel/{N}/level   i(0-255) or f(<=1.0 normalised; >1.0=0-255)\n'
            '  /intensity           {channel:i} {level:f} — ABSOLUTE level\n'
            '  /level/adjust        i — +/- step on selected (e.g. 5,-5)\n'
            '  /level/set           f — fixed value on selected (0.5=50%)\n'
            '  /level/set/{pct}     0-100 in address (e.g. /level/set/50)\n'
            '  /level/up  /level/down   +/-5 step (or /level/up/{n})\n'
            '  /channel/select      i (channel; 0 = deselect)\n'
            '  /submaster/{N}       f  (<=1.0 -> %;  >1.0 -> 0-100)\n'
            '  /group/{N}/level     f\n'
            '  /group/{N}           call group N (1-20) — on press\n'
            '  /look/{N}            recall look/snapshot N (1-20)\n'
            '\n'
            'Cuelist — move the bar WITHOUT firing (arrows <<< / >>>):\n'
            '  /cue/back            <<<  previous cue (no fade)\n'
            '  /cue/go              >>>  next cue (no fade)\n'
            '  /cue/fade_in         f (seconds)\n'
            '  /cue/fade_out        f (seconds)\n'
            '  /cue/state/request   request current cue state\n'
            '\n'
            'Highlight / output test:\n'
            '  /highlight           i(0|1) — toggle Highlight\n'
            '                       (in DMX view = DMX output test)\n'
            '  /highlight/level     i(0-255) — level of highlighted\n'
            '  /dmx/highlight/addr  i(1-512; 0=none) — address to test\n'
            '\n'
            'FX (effects page):\n'
            '  /fx/mode             i(0|1) — enter/leave the FX page\n'
            '  /fx/group            i — select the group of 4 FX\n'
            '  /fx/{N}/toggle       toggle FX N (1-16)\n'
            '\n'
            '── SENDS (app → controller, feedback) ──────────────────\n'
            '  /channel/{N}/name    s  (<=6 chars)\n'
            '  /channel/{N}/alias   i\n'
            '  /channel/{N}/curve   s\n'
            '  /channel/{N}/level   i  (0-255)\n'
            '  /channel/patched     s  (csv "1,2,5,10")\n'
            '  /channel/selected    i  (selected channel; 0 = none)\n'
            '  /fx/{N}/state        i(0|1) — FX N state (light the button)\n'
            '  /show/size           i  (show channel count)\n'
            '  /page                s i  ("dmx" univ | "mesa" 0)\n'
            '  /dmx/browse          i  (address in focus in DMX view)\n'
            '  /cue/state           s s f f  (num, label, fade_in, fade_out)\n'
            '  /cue/state/{key}     f\n'
            '\n'
            '── SYNTAX examples ─────────────────────────────────────\n'
            '  /channel/5/level 200      channel 5 to 200 (0-255)\n'
            '  /level/up                 raise +5 on selected\n'
            '  /level/down               lower -5 on selected\n'
            '  /level/set/50             selected to 50 %\n'
            '  /submaster/1 0.8          submaster 1 to 80 %\n'
            '  /group/2/level 1.0        group 2 to full\n'
            '  /fx/3/toggle              toggle FX 3\n'
            '\n'
            '═══════════════════════════════════════════════════════\n'
            'Default OSC IN port: 8080     OSC OUT port: 8081\n'
            'Configure ports at: Settings -> OSC\n'
        ),
    },
}


def T(key, **kw):
    """String traduzida para LANG. Cai no PT e depois na própria chave se
    faltar — NUNCA rebenta. Aceita interpolação .format(**kw)."""
    s = STRINGS.get(LANG, STRINGS['pt']).get(key)
    if s is None:
        s = STRINGS['pt'].get(key, key)
    try:
        return s.format(**kw) if kw else s
    except (KeyError, IndexError, ValueError):
        return s


def osc_reference_text():
    """Texto de referência do protocolo OSC, na língua activa.
    Usado na tab «Ajuda OSC» / «OSC Help» das Configurações (Etapa 2.5)."""
    return T('osc_help.text')


def load_app_config():
    """Lê ~/.mesadelux.json (preferências do utilizador, não do show):
    idioma e portas MIDI escolhidas (v6.3)."""
    global LANG, MIDI_IN_PORT, MIDI_OUT_PORT, DMX_IN_UNIVS, DMX_IN_BIND
    try:
        with open(APP_CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        if cfg.get('lang') in AVAILABLE_LANGS:
            LANG = cfg['lang']
        # v6.3 — portas MIDI (nome da porta ou None). Guarda-se o NOME; se o
        # dispositivo não estiver ligado no arranque, fica só registado.
        mi = cfg.get('midi_in_porta')
        mo = cfg.get('midi_out_porta')
        MIDI_IN_PORT = mi if isinstance(mi, str) else None
        MIDI_OUT_PORT = mo if isinstance(mo, str) else None
        # v6.4 — DMX-IN
        du = cfg.get('dmx_in_universos')
        if isinstance(du, list):
            du = [int(u) for u in du
                  if isinstance(u, (int, float)) and 1 <= int(u) <= 63999]
            if du:
                DMX_IN_UNIVS = du
        db = cfg.get('dmx_in_bind')
        if isinstance(db, str) and db.strip():
            DMX_IN_BIND = db.strip()
    except Exception:
        pass


def save_app_config():
    """Grava as preferências do utilizador (idioma, portas MIDI, …)."""
    try:
        with open(APP_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump({'lang': LANG,
                       'midi_in_porta': MIDI_IN_PORT,
                       'midi_out_porta': MIDI_OUT_PORT,
                       'dmx_in_universos': DMX_IN_UNIVS,   # v6.4
                       'dmx_in_bind': DMX_IN_BIND},
                      f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def set_lang(code):
    """Define o idioma activo (runtime) e persiste-o."""
    global LANG
    if code in AVAILABLE_LANGS:
        LANG = code
        save_app_config()


load_app_config()


# ── Rótulo ↔ valor para campos acoplados a dados (cores de halo, curvas).
#    A UI mostra o rótulo traduzido; o que se GRAVA é sempre o token interno
#    (chave de HALO_COLORS / token de CURVE_VALUES), para não partir shows. ──
def halo_label(key):
    """Chave de cor de halo → rótulo traduzido."""
    return T('halo.' + key) if key else key


def halo_key_from_label(label):
    """Rótulo (qualquer idioma) → chave de cor de halo, ou None."""
    for k in HALO_COLORS:
        if halo_label(k) == label:
            return k
    return label if label in HALO_COLORS else None


def curve_label(token):
    """Token de curva → rótulo traduzido."""
    return T('curve.' + token)


def curve_from_label(label):
    """Rótulo (qualquer idioma) → token de curva, defeito = CURVE_LINEAR."""
    for t in CURVE_VALUES:
        if curve_label(t) == label:
            return t
    return label if label in CURVE_VALUES else CURVE_LINEAR


def _rit(label, *figs):
    """Constrói uma entrada da tabela de ritmos: (duração em ♩, é_nota)."""
    f = [(float(d), bool(nota)) for d, nota in figs]
    return {'label': label, 'fig': f, 'total': sum(d for d, _ in f)}


# v5 etapa 3 — os 24 ritmos do autor (tabela no CLAUDE_V5.md; NÃO alterar
# a ordem). ♩=1 batida, 𝅗𝅥=2, ♪=0.5, pausa=1 batida de escuro. Nos rótulos
# usa-se a leitura ("ta taa ta-ta") — os glifos musicais não rendem bem
# no Tk do Windows.
FX_RITMOS = [
    _rit("1 · 4/4 · ta ta ta ta",        (1, 1), (1, 1), (1, 1), (1, 1)),
    _rit("2 · 4/4 · ta ta taa",          (1, 1), (1, 1), (2, 1)),
    _rit("3 · 4/4 · taa ta ta",          (2, 1), (1, 1), (1, 1)),
    _rit("4 · 4/4 · ta taa ta",          (1, 1), (2, 1), (1, 1)),
    _rit("5 · 4/4 · taa taa",            (2, 1), (2, 1)),
    _rit("6 · 4/4 · ta-ta ta ta ta",     (.5, 1), (.5, 1), (1, 1), (1, 1), (1, 1)),
    _rit("7 · 4/4 · ta ta-ta ta ta",     (1, 1), (.5, 1), (.5, 1), (1, 1), (1, 1)),
    _rit("8 · 4/4 · ta ta ta-ta ta",     (1, 1), (1, 1), (.5, 1), (.5, 1), (1, 1)),
    _rit("9 · 4/4 · ta ta ta ta-ta",     (1, 1), (1, 1), (1, 1), (.5, 1), (.5, 1)),
    _rit("10 · 4/4 · ta-ta ta-ta ta ta", (.5, 1), (.5, 1), (.5, 1), (.5, 1), (1, 1), (1, 1)),
    _rit("11 · 4/4 · ta ta-ta ta-ta ta", (1, 1), (.5, 1), (.5, 1), (.5, 1), (.5, 1), (1, 1)),
    _rit("12 · 4/4 · ta-ta ta ta-ta ta", (.5, 1), (.5, 1), (1, 1), (.5, 1), (.5, 1), (1, 1)),
    _rit("13 · 4/4 · ta-ta ×4",          (.5, 1), (.5, 1), (.5, 1), (.5, 1),
                                         (.5, 1), (.5, 1), (.5, 1), (.5, 1)),
    _rit("14 · 4/4 · ta pausa ta ta",    (1, 1), (1, 0), (1, 1), (1, 1)),
    _rit("15 · 4/4 · ta ta pausa ta",    (1, 1), (1, 1), (1, 0), (1, 1)),
    _rit("16 · 4/4 · pausa ta ta ta",    (1, 0), (1, 1), (1, 1), (1, 1)),
    _rit("17 · 3/4 · ta ta ta",          (1, 1), (1, 1), (1, 1)),
    _rit("18 · 3/4 · ta taa",            (1, 1), (2, 1)),
    _rit("19 · 3/4 · taa ta",            (2, 1), (1, 1)),
    _rit("20 · 3/4 · ta-ta ta ta",       (.5, 1), (.5, 1), (1, 1), (1, 1)),
    _rit("21 · 3/4 · ta ta-ta ta",       (1, 1), (.5, 1), (.5, 1), (1, 1)),
    _rit("22 · 3/4 · ta ta ta-ta",       (1, 1), (1, 1), (.5, 1), (.5, 1)),
    _rit("23 · 2/4 · ta ta",             (1, 1), (1, 1)),
    _rit("24 · 2/4 · ta-ta ta",          (.5, 1), (.5, 1), (1, 1)),
]

# Porta da consola para RECEBER da app (app -> Pico).
# Em modo AP: app envia UDP direct para 192.168.4.1:8081.
# Em modo USB: bridge v2 escuta UDP em 0.0.0.0:8081 e escreve no serial.
# A porta 8080 e Pico -> App (sem mudancas).
CONSOLE_OSC_HOST = '192.168.4.1'
CONSOLE_OSC_PORT = 8081


# ─────────────────────────────────────────────
# REDE
# ─────────────────────────────────────────────
def local_ips():
    """Devolve a lista de IPs IPv4 locais (para escolher a interface de saída)."""
    ips = []
    try:
        host = socket.gethostname()
        for info in socket.getaddrinfo(host, None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    # truque do socket UDP para descobrir o IP da rota por defeito
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip not in ips:
            ips.insert(0, ip)
    except Exception:
        pass
    return ips


# ─────────────────────────────────────────────
# ART-NET (v4) — emissor ArtDMX nativo
# ─────────────────────────────────────────────
class ArtNetSender:
    """Emissor Art-Net (pacote ArtDMX / OpDmx 0x5000) sem dependências.

    Convenção de universos: o universo da mesa N (1-based, igual ao sACN)
    é transmitido como port-address Art-Net N-1 (0-based). Ou seja:
        Mesa U1  ->  Art-Net universe 0
        Mesa U2  ->  Art-Net universe 1
    A maioria dos nós/softwares (QLC+, MagicQ, nodes chineses) usa esta
    convenção quando mostra "Universe 0/1".

    broadcast=True  -> envia para 255.255.255.255 (limited broadcast);
                       com bind_ip definido sai pela interface certa.
    broadcast=False -> unicast para dest_ip.
    """
    ARTNET_PORT = 6454
    _HEADER = b'Art-Net\x00' + struct.pack('<H', 0x5000) + struct.pack('>H', 14)

    def __init__(self, bind_ip='', dest_ip='', broadcast=True):
        dest = '255.255.255.255' if broadcast else (dest_ip or '')
        if not dest:
            raise ValueError(T('artnet.unicast_needs_ip'))
        self._dest = (dest, self.ARTNET_PORT)
        self._seq = {}                       # port_addr -> sequência 1..255
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if broadcast:
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if bind_ip:
            self._sock.bind((bind_ip, 0))

    def send(self, universe, data512):
        """Envia um universo (1-based, da mesa) com 512 bytes de DMX."""
        pa = max(0, min(32767, int(universe) - 1))
        seq = self._seq.get(pa, 0) % 255 + 1       # cicla 1..255 (0=desligado)
        self._seq[pa] = seq
        pkt = (self._HEADER
               + bytes((seq, 0))                   # Sequence, Physical
               + struct.pack('<H', pa)             # SubUni + Net (little-endian)
               + struct.pack('>H', 512)            # Length (big-endian)
               + bytes(data512))
        self._sock.sendto(pkt, self._dest)

    def stop(self):
        try:
            self._sock.close()
        except Exception:
            pass


# ─────────────────────────────────────────────
# DMX-IN — escuta sACN (v6.4, Etapa 1: SÓ escuta, não grava nada)
# ─────────────────────────────────────────────
class EscutaDMXIn:
    """Escuta sACN de ENTRADA (outra mesa — GrandMA3/Eos/… — mesmo no
    mesmo computador) e guarda o último estado de cada universo. NÃO
    toca no motor de saída, no show nem no .ldsk: só lê da rede e expõe
    um snapshot thread-safe. A UI lê via obter_snapshot() num ciclo
    root.after — NUNCA a partir da thread de escuta (Tkinter não é
    thread-safe). Ver MESADELUX_V64_DMXIN_SPEC.md."""
    # E1.31 define o timeout de perda de dados em 2,5 s — usamo-lo como
    # limiar de «Silêncio» (a Eos espaça os envios quando o valor é
    # estático; 2,0 s dava «Silêncio» a receber).
    SILENCIO_S = 2.5

    def __init__(self, universos, bind='0.0.0.0'):
        self.universos = sorted({int(u) for u in universos if int(u) > 0})
        # interface de escuta. DESCOBERTA nesta máquina (2026-07-08): a
        # firewall do Windows pode bloquear UDP loopback em sockets
        # 0.0.0.0 — com a mesa de origem NO MESMO PC (unicast p/
        # 127.0.0.1), escutar em 127.0.0.1 é o que funciona sem mexer
        # na firewall. Da rede, 0.0.0.0 (ou o IP da placa).
        self.bind = bind or '0.0.0.0'
        self._valores = {u: None for u in self.universos}   # tuple de 512
        self._ultima = {u: 0.0 for u in self.universos}
        # v6.4 — fonte «dona» de cada universo: (nome, prioridade, hora).
        # Trava numa fonte para não piscar quando há mais do que uma a
        # emitir no mesmo universo (ex.: a Eos + o nosso próprio output).
        self._fonte = {u: None for u in self.universos}
        self._lock = threading.Lock()
        self._recv = None

    def iniciar(self):
        """Arranca a thread de escuta (biblioteca sacn — a mesma que a
        saída já usa). Junta-se ao multicast de cada universo; o unicast
        para o IP escutado entra de qualquer maneira (porta 5568)."""
        if not HAS_SACN:
            raise RuntimeError('pip install sacn')
        if self._recv is not None:
            return
        self._recv = sacn.sACNreceiver(bind_address=self.bind)
        for u in self.universos:
            self._recv.register_listener('universe', self._faz_cb(u),
                                          universe=u)
        self._recv.start()
        for u in self.universos:
            try:
                self._recv.join_multicast(u)
            except Exception:
                pass    # sem multicast nesta interface: fica o unicast

    def _faz_cb(self, u):
        def cb(packet):
            # SÓ dados de nível (start code 0). A Eos/GrandMA intercalam
            # no mesmo universo pacotes de PRIORIDADE POR ENDEREÇO (start
            # code 0xDD, valores 0-200) — aceitá-los fazia o valor piscar
            # entre o nível real e a prioridade (bug reportado 2026-07-08).
            if getattr(packet, 'dmxStartCode', 0) != 0:
                return
            if getattr(packet, 'option_PreviewData', False):
                return          # dados de «blind»/preview, não a saída viva
            src = getattr(packet, 'sourceName', '') or ''
            # v6.4 — ignora o NOSSO próprio output sACN (loopback na mesma
            # máquina): escutar o mesmo universo que se emite capturava o
            # próprio output em vez da mesa externa — «a receber» mas nada
            # na grelha. Sem isto a arbitragem travava na nossa fonte.
            if src == SACN_SOURCE_NAME:
                return
            prio = int(getattr(packet, 'priority', 100) or 100)
            agora = time.time()
            with self._lock:
                # «a receber» (indicador) = QUALQUER fonte externa neste
                # universo, mesmo que perca a arbitragem — senão, com duas
                # fontes, a que não é «dona» não contava e dizia «Silêncio».
                self._ultima[u] = agora
                dono = self._fonte.get(u)
                # o VALOR mostrado segue a arbitragem: aceita se não há
                # dono, prioridade maior, é o mesmo dono, ou o dono actual
                # está calado há > SILENCIO_S. (outra fonte com prioridade
                # igual/menor não rouba o valor → não pisca.)
                if (dono is None or prio > dono[1] or src == dono[0]
                        or agora - dono[2] > self.SILENCIO_S):
                    self._fonte[u] = (src, prio, agora)
                    self._valores[u] = tuple(packet.dmxData)
        return cb

    def rejuntar_multicast(self):
        """Re-inscreve no multicast de cada universo. O Windows por vezes
        larga a inscrição IGMP passado o arranque (sobretudo com fonte e
        receptor no MESMO PC) e a recepção «recebe e pára». Chamado
        periodicamente pela UI para manter a inscrição viva."""
        r = self._recv
        if r is None:
            return
        for u in self.universos:
            try:
                r.join_multicast(u)
            except Exception:
                pass

    def parar(self):
        r, self._recv = self._recv, None
        if r is not None:
            for u in self.universos:
                try:
                    r.leave_multicast(u)
                except Exception:
                    pass
            try:
                r.stop()
            except Exception:
                pass

    def obter_snapshot(self):
        """Cópia thread-safe: {universo: tuple de 512 valores ou None}."""
        with self._lock:
            return dict(self._valores)

    def esta_a_receber(self, universo):
        """True se chegou pacote deste universo há menos de SILENCIO_S."""
        with self._lock:
            return (time.time()
                    - self._ultima.get(universo, 0.0)) < self.SILENCIO_S

    def estado(self, universo):
        """(a_receber, fonte, idade_s, tem_look) para o indicador da UI.
        idade_s = segundos desde o último pacote (None se nunca chegou);
        tem_look = já recebeu valores (mesmo que a fonte tenha parado —
        muitas fontes só enviam sACN quando algo MUDA; nesse caso o
        último look fica seguro e captável)."""
        with self._lock:
            ult = self._ultima.get(universo, 0.0)
            fonte = self._fonte.get(universo)
            idade = (time.time() - ult) if ult else None
            nome = fonte[0] if fonte else ''
            tem_look = self._valores.get(universo) is not None
            return (idade is not None and idade < self.SILENCIO_S,
                    nome, idade, tem_look)


def parse_universos_dmx_in(texto):
    """Texto «1,2» → lista de universos válidos (1..63999), sem repetidos.
    Ilegível → lista vazia (a UI avisa)."""
    out = []
    for tok in str(texto or '').replace(';', ',').split(','):
        tok = tok.strip()
        if not tok:
            continue
        try:
            u = int(float(tok))
        except (TypeError, ValueError):
            continue
        if 1 <= u <= 63999 and u not in out:
            out.append(u)
    return out


# ─────────────────────────────────────────────
# SELECÇÃO DE CANAIS
# ─────────────────────────────────────────────
def parse_channel_expr(expr, maxch):
    """Interpreta expressões de selecção de canais.

    Exemplos:
        '5'           -> {5}
        '1 ao 10'     -> {1..10}
        '1 + 5 + 9'   -> {1, 5, 9}
        '1 ao 20 - 5' -> {1..20} sem o 5
    Aceita 'ao', 'thru' ou '>' para intervalos.
    """
    if not expr:
        return set()
    txt = expr.lower().replace('thru', ' ao ').replace('>', ' ao ')
    txt = txt.replace('ao', ' ao ')
    txt = txt.replace('+', ' + ').replace('-', ' - ')
    tokens = txt.split()
    result = set()
    op = '+'
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ('+', '-'):
            op = t
            i += 1
            continue
        if t == 'ao':
            i += 1
            continue
        try:
            start = int(t)
        except ValueError:
            i += 1
            continue
        end = start
        if i + 1 < len(tokens) and tokens[i + 1] == 'ao':
            try:
                end = int(tokens[i + 2])
                i += 2
            except (ValueError, IndexError):
                end = start
        lo, hi = min(start, end), max(start, end)
        chans = {c for c in range(lo, hi + 1) if 1 <= c <= maxch}
        if op == '-':
            result -= chans
        else:
            result |= chans
        op = '+'
        i += 1
    return result


def summarize_channels(chans):
    """Resume um conjunto de canais numa string compacta: '1▸10, 15, 20▸22'."""
    s = sorted(chans)
    parts = []
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[j] + 1:
            j += 1
        parts.append(f"{s[i]}▸{s[j]}" if j > i else str(s[i]))
        i = j + 1
    return ", ".join(parts)


def parse_addr_list(txt):
    """'3 + 9 + 11' → [3, 9, 11]. Ignora partes vazias ou inválidas."""
    out = []
    for part in txt.replace(' ', '').split('+'):
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            pass
    return out


# ─────────────────────────────────────────────
# GDTF → FOOTPRINT (v6.1 — importação de fixturas)
# ─────────────────────────────────────────────
# Abreviaturas dos atributos GDTF padrão (<= 6 caracteres). A chave é o
# Attribute padrão do GDTF; o valor é a abreviatura usada na mesa.
GDTF_ABBR = {
    'Dimmer': 'DIM', 'DimmerCurve': 'DCURV',
    'LEDFrequency': 'LFRQ', 'LEDFrequencyAdjust': 'LFRQAJ',
    'AnimationWheel1': 'ANMWH', 'AnimationWheel1Pos': 'ANMWHP',
    'AnimationWheel1SelectEffects': 'ANMWHE',
    'ColorAdd_R': 'R', 'ColorAdd_G': 'G', 'ColorAdd_B': 'B',
    'ColorAdd_W': 'W', 'ColorAdd_A': 'A', 'ColorAdd_C': 'C',
    'ColorAdd_M': 'M', 'ColorAdd_Y': 'Y', 'ColorAdd_UV': 'UV',
    'ColorAdd_WW': 'WW', 'ColorAdd_CW': 'CW', 'ColorAdd_RY': 'RY',
    'ColorAdd_GY': 'GY', 'ColorAdd_L': 'LIME', 'ColorAdd_RGB': 'RGB',
    'ColorSub_C': 'C', 'ColorSub_M': 'M', 'ColorSub_Y': 'Y',
    'Pan': 'PAN', 'Tilt': 'TILT', 'PanRotate': 'PANROT',
    'TiltRotate': 'TLTROT',
    'Zoom': 'ZOOM', 'ZoomMode': 'ZMODE', 'ZoomModeSpot': 'ZMODE',
    'Focus1': 'FOCUS', 'Focus': 'FOCUS', 'FocusMode': 'FMODE',
    'Iris': 'IRIS', 'IrisStrobe': 'IRISST',
    'Prism1': 'PRISM', 'Prism1Pos': 'PRPOS', 'Frost1': 'FROST',
    'Gobo1': 'GOBO', 'Gobo1WheelSpin': 'GOBOSP', 'Gobo1Pos': 'GOBOPS',
    'Gobo2': 'GOBO2', 'Gobo2Pos': 'GOB2PS',
    'Color1': 'COLOR', 'Color1WheelSpin': 'COLRSP',
    'ColorMacro1': 'MACRO', 'ColorMacro2': 'MACRO2',
    'Shutter1': 'STROB', 'Shutter1Strobe': 'STROB', 'StrobeMode': 'STRMOD',
    'Effects1': 'FX', 'Effects2': 'FX2',
    'Effects1Rate': 'FXRATE', 'Effects2Rate': 'FX2RAT', 'EffectsRate': 'FXRATE',
    'Effects1Fade': 'FXFADE',
    'IntensityMSpeed': 'MSPEED', 'PositionMSpeed': 'PSPEED',
    'ColorMSpeed': 'CSPEED', 'GoboWheelMSpeed': 'GSPEED',
    'CTO': 'CTO', 'CTC': 'CTC', 'CTB': 'CTB', 'CTORatio': 'CTO',
    'Tint': 'TINT', 'Hue': 'HUE', 'Saturation': 'SAT',
    'Function': 'FUNC', 'Control1': 'CTRL', 'Reset': 'RESET',
    'Fans': 'FANS', 'BlackoutMode': 'BLKOUT',
}


# v6.1 — defeitos por NOME de canal (decisão do autor 2026-06-16): mais
# fiável que os defeitos do GDTF (que variam de marca para marca).
_COR_DEFEITO = {'R', 'G', 'B', 'W', 'A', 'C', 'M', 'Y', 'UV', 'WW', 'CW',
                'RGB', 'LIME', 'RED', 'GREEN', 'BLUE', 'WHITE', 'AMBER',
                'CYAN', 'MAGENTA', 'YELLOW'}


def nome_defeito(name):
    """Defeito (0-255) sugerido pelo NOME do canal:
        cores (R/G/B/W/A/…) → 255 (repouso a full; o dimmer é que controla)
        PAN / TILT / ZOOM / FOCUS → 127 (centro / meio)
        tudo o resto (DIM, STROBE, controlo…) → 0
    O strobe/shutter fica a 0 porque open/closed varia de marca para marca."""
    u = (name or '').strip().upper()
    if u in _COR_DEFEITO:
        return 255
    if u in ('PAN', 'TILT', 'ZOOM', 'FOCUS'):
        return 127
    return 0


def gdtf_abbrev(attr):
    """Atributo GDTF → abreviatura <= 6 (MAIÚSCULAS). Usa a tabela; senão
    deriva (tira nº final, só letras, 6 caracteres). None se sem feature."""
    if not attr or attr == 'NoFeature':
        return None
    if attr in GDTF_ABBR:
        return GDTF_ABBR[attr]
    # Control: Control1->CTRL, Control2->CTRL2, Control3->CTRL3 (mantém o nº,
    # excepto o 1). A regra genérica perdia o número (->CONTRO).
    m = re.match(r'^Control(\d+)$', attr)
    if m:
        n = m.group(1)
        return 'CTRL' if n == '1' else ('CTRL' + n)[:6]
    # Facas (blades): o que identifica a faca está no FIM (nº + lado/rotação),
    # por isso a regra genérica perdia-o (BLADEA/BLADER iguais p/ todas).
    # Blade1A->B1A, Blade1B->B1B, Blade1Rot->B1Rot, Blade12Rot->B12Rot.
    m = re.match(r'^Blade(\d+)([A-Za-z]+)$', attr)
    if m:
        return ('B' + m.group(1) + m.group(2))[:6]
    # ShaperRot (rotação de todas as facas / shaper) -> SRot.
    if attr == 'ShaperRot':
        return 'SRot'
    base = re.sub(r'\d+$', '', attr)
    base = re.sub(r'[^A-Za-z]', '', base)
    return (base[:6] or attr[:6]).upper()


def _gdtf_localname(tag):
    return tag.rsplit('}', 1)[-1]            # ignora namespace XML


def gdtf_ler(path):
    """Lê um .gdtf e devolve {nome_do_modo: [canais]} onde cada canal é
    (offset_str, n_bytes, attr, cfname). Ordenado por endereço DMX."""
    z = zipfile.ZipFile(path)
    xml = z.read('description.xml').decode('utf-8', 'ignore')
    root = ET.fromstring(xml)
    modos = {}
    for mode in root.iter():
        if _gdtf_localname(mode.tag) != 'DMXMode':
            continue
        nome = mode.get('Name', '?')
        canais = []
        for ch in mode.iter():
            if _gdtf_localname(ch.tag) != 'DMXChannel':
                continue
            off = ch.get('Offset')
            if not off or off.lower() == 'none':
                continue                     # canal virtual (sem DMX)
            try:
                bytes_ = [int(x) for x in off.split(',')]
            except ValueError:
                continue
            attr = cfname = None
            for sub in ch.iter():
                ln = _gdtf_localname(sub.tag)
                if ln == 'LogicalChannel' and attr is None:
                    attr = sub.get('Attribute')
                if ln == 'ChannelFunction' and cfname is None:
                    cfname = sub.get('Name')
            canais.append((off, len(bytes_), attr, cfname, min(bytes_)))
        canais.sort(key=lambda c: c[4])      # por endereço DMX
        modos[nome] = canais
    return modos


def gdtf_footprint(canais):
    """Lista de canais (de gdtf_ler) → string footprint (DIM R16 G16 …)."""
    toks = []
    for off, nb, attr, cfname, _ in canais:
        ab = gdtf_abbrev(attr) or (re.sub(r'[^A-Za-z]', '', cfname or 'CH')[:6]
                                   or 'CH').upper()
        toks.append(ab + '16' if nb >= 2 else ab)
    return ' '.join(toks)


def parse_memory_expr(expr):
    """Interpreta uma expressão de memórias → lista de intervalos [(lo, hi), …].

    Exemplos:
        '1'          -> [(1, 1)]
        '1 aa 5'     -> [(1, 5)]
        '1 + 4 + 5'  -> [(1, 1), (4, 4), (5, 5)]
    'aa', 'ao', 'thru' e '>' indicam um intervalo. Texto extra é ignorado.
    """
    if not expr:
        return []
    txt = expr.lower()
    for kw in ('thru', 'aa', 'ao', '>'):
        txt = txt.replace(kw, ' ~ ')
    txt = txt.replace('+', ' + ')
    intervals = []
    for term in txt.split('+'):
        toks = term.split()
        nums = []
        for t in toks:
            if t == '~':
                continue
            try:
                nums.append(float(t.replace(',', '.')))
            except ValueError:
                pass
        if not nums:
            continue
        if '~' in toks and len(nums) >= 2:
            intervals.append((min(nums[:2]), max(nums[:2])))
        else:
            for n in nums:
                intervals.append((n, n))
    return intervals


# ─────────────────────────────────────────────
# USITT ASCII (v6.3.2) — import/export de shows
# ─────────────────────────────────────────────
# Porta de portabilidade para outras mesas (ETC Eos/Ion, Strand, Avolites…)
# via USITT ASCII 3.0. O .ldsk continua a ser o ÚNICO formato de gravação;
# aqui só viaja o que o standard transporta: cues (tempos, texto, FOLLOWON,
# LINK, níveis), patch de intensidade, grupos e submasters. MIDI por cue,
# FX, looks, alcunhas, curvas e halos ficam de fora (a UI avisa).
# As funções falam o dialecto dos dicts de _show_data()/_load_data() do
# Engine, para reaproveitar toda a validação de load existente.
# Ver MESADELUX_USITT_ASCII_SPEC.md e MESADELUX_V632_PLANO_ASCII.md.

def _ascii_num(x):
    """Número (cue/tempo) → texto sem zeros a mais (2.0 → '2', 2.5 → '2.5')."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return str(x)
    if f == int(f):
        return str(int(f))
    return ('%g' % f)


def _ascii_level(v):
    """Nível interno 0-255 → percentagem USITT (0-100). O standard (7.5)
    só define percentagem inteira e hex Hnn — 'FULL' NÃO existe (a Eos
    rejeitava os níveis; confirmado no doc oficial, 2026-07-06)."""
    try:
        v = int(v)
    except (TypeError, ValueError):
        v = 0
    v = max(0, min(255, v))
    return str(int(round(v * 100.0 / 255.0)))


def _ascii_time(x):
    """Tempo em segundos → texto USITT (7.7): decimal com UMA casa no
    máximo (o standard só admite 1 dígito de décimos)."""
    try:
        return _ascii_num(round(float(x), 1))
    except (TypeError, ValueError):
        return '0'


def _cue_total(c):
    """Tempo total da transição de uma cue (o momento em que 'acaba'):
    max(delay+fade) sobre a memória E as suas PARTES (v6.3.3). Usado na
    conversão do FOLLOWON entre a semântica MesaDeLux/grandMA (conta do
    FIM da cue anterior) e a Eos/USITT (conta do INÍCIO)."""
    try:
        f_in = float(c.get('fade_in', 3.0) or 0)
        f_out = float(c.get('fade_out', f_in) or 0)
        d_in = float(c.get('delay_in', 0) or 0)
        d_out = float(c.get('delay_out', 0) or 0)
        total = max(d_in + f_in, d_out + f_out)
        for p in (c.get('parts') or {}).values():   # v6.3.3
            total = max(total,
                        float(p.get('delay_in', 0)) + float(p.get('fade_in', 0)),
                        float(p.get('delay_out', 0)) + float(p.get('fade_out', 0)))
        return total
    except (TypeError, ValueError):
        return 0.0


def _ascii_wrap(prefix, tokens):
    """Distribui tokens por linhas 'prefix tok tok…' de <=75 chars."""
    out, line = [], prefix
    for tk_ in tokens:
        if len(line) + 1 + len(tk_) > 75 and line != prefix:
            out.append(line)
            line = prefix
        line += ' ' + tk_
    if line != prefix:
        out.append(line)
    return out


def _ascii_text(s):
    """Texto para linhas TEXT — 7-bit puro (tira acentos: 'transição' →
    'transicao'), porque o standard é ASCII e há mesas que engasgam."""
    s = unicodedata.normalize('NFKD', str(s))
    return s.encode('ascii', 'ignore').decode('ascii')


def export_ascii(show_dict, filepath, follow_estilo='eos'):
    """Escreve o show (dict no formato de _show_data()) num ficheiro USITT
    ASCII 3.0 (.asc). Só viaja o que o standard transporta: cues (UP/DOWN
    com delay no 2.º campo, TEXT, FOLLOWON, LINK, níveis em %), PATCH de
    intensidade, GROUP e SUB. Devolve {'cues', 'channels', 'notas'}.
    Sintaxe validada contra o doc oficial USITT 3.0 + exports reais da
    Eos (2026-07-06): sem TIME, sem FULL, níveis 0-100, CHAN canal@nível,
    PATCH canal<dimmer@100 com dimmer=(universo-1)*512+endereço (fine 16
    bit fica de fora). Canais = número interno 1..N; a ZERO não vai.

    follow_estilo — a semântica do FOLLOWON no ficheiro:
      'eos'     (defeito) Eos/USITT estrito: o FOLLOWON escreve-se na cue
                PRECEDENTE e conta desde o INÍCIO dela → valor gravado =
                tempo_total(precedente) + follow. É o que a Eos espera.
      'directo' grandMA e afins: escreve o follow tal e qual, na própria
                cue que entra (semântica MesaDeLux, conta do FIM da
                anterior) — sem aritmética.
    O LOOP viaja como LINK (standard) SEM contagem — decisão final
    2026-07-07: escreve-se só o que é USITT puro; a contagem de voltas
    põe-se à mão na mesa de destino (é manobra pontual). Tentou-se
    $$LoopNum (dialecto Eos) e a Eos ignorou-o vindo de terceiros.
    HISTÓRIA (2026-07-07, testes reais na Eos): declarar CONSOLE Eos +
    $$Format 3.10 no cabeçalho fazia a Eos entrar no modo de leitura
    NATIVO (espera $CueList/$Patch/$Personality) e deitava TUDO fora —
    nunca fingir que o ficheiro é um export da Eos. Com MANUFACTURER
    ByWorm o modo genérico importa patch, cues, níveis e tempos.
    O comentário ! MESADELUX FOLLOW regista o estilo para o import
    detectar sozinho no round-trip."""
    L = ['IDENT 3:0',
         'MANUFACTURER ByWorm',
         'CONSOLE MesaDeLux v6.4',
         'CLEAR ALL',
         '! Exportado pela MesaDeLux v6.4 (By Worm)',
         # comentários (as mesas ignoram): modo da cuelist + estilo do
         # FOLLOWON, para o round-trip MesaDeLux → MesaDeLux.
         '! MESADELUX MODE ' + str(show_dict.get('intensity_mode',
                                                 'tracking')),
         '! MESADELUX FOLLOW ' + follow_estilo,
         '']
    notas = []

    # ── PATCH (página 1) — só canais com endereço; linhas até 75 chars ──
    n_chans = 0
    tokens = []
    patch = show_dict.get('patch', {})
    for ch in sorted(patch, key=int):
        info = patch[ch]
        if not isinstance(info, dict) or not info.get('addrs'):
            continue
        n_chans += 1
        uni = int(info.get('universe', 1))
        for addr in info['addrs']:
            dim = (uni - 1) * 512 + int(addr)
            tokens.append('%s<%d@100' % (ch, dim))
    L.extend(_ascii_wrap('PATCH 1', tokens))
    if tokens:
        L.append('')

    # ── CUES (a ZERO nunca vai — é interna da mesa) ──
    cs = [c for c in show_dict.get('cues', []) if not c.get('zero')]
    n_cues = len(cs)
    if (follow_estilo == 'eos' and cs and cs[0].get('follow') is not None):
        # no estilo Eos o FOLLOWON vive na cue precedente; a 1.ª cue
        # entra a seguir à ZERO, que não vai no ficheiro — perde-se.
        notas.append('AUTO da 1.a cue nao tem onde viajar (estilo Eos)')
    for i, c in enumerate(cs):
        L.append('CUE ' + _ascii_num(c.get('num', 0)))
        f_in = float(c.get('fade_in', 3.0) or 0)
        f_out = float(c.get('fade_out', f_in) or 0)
        d_in = float(c.get('delay_in', 0) or 0)
        d_out = float(c.get('delay_out', 0) or 0)
        label = _ascii_text(c.get('label', '') or '')
        lv = c.get('levels', {})
        pts = c.get('parts') or {}
        # TEXT: cue SEM partes → logo a seguir a CUE (como a Eos). Cue COM
        # partes → o TEXT vai DEPOIS de todas as partes (é aí que a Eos o
        # põe; ANTES do PART 1 baralha o parser dela e as partes não
        # entravam — bug do espectáculo grande, 2026-07-09).
        if label and not pts:
            L.append(('TEXT ' + label)[:75])
        em_partes = set()
        for p in pts.values():
            em_partes.update(int(x) for x in p.get('channels', []))
        pares_main = ['%s@%s' % (ch, _ascii_level(lv[ch]))
                      for ch in sorted(lv, key=int)
                      if int(ch) not in em_partes]
        # sem TIME no standard: UP/DOWN sempre; delay = 2.º campo.
        # COM partes, a estrutura vai TODA em PART (como a Eos escreve —
        # confirmado no export real 2026-07-07): PART 1 leva os tempos da
        # memória e os canais principais; sem isso a Eos não lê as partes.
        if pts:
            L.append('PART 1')
        L.append('UP ' + _ascii_time(f_in)
                 + (' ' + _ascii_time(d_in) if d_in else ''))
        L.append('DOWN ' + _ascii_time(f_out)
                 + (' ' + _ascii_time(d_out) if d_out else ''))
        L.extend(_ascii_wrap('CHAN', pares_main))
        # v6.3.3 — PARTES: blocos PART k (standard 10.5), cada um com os
        # seus tempos (delay no 2.º campo) e os CHAN dos seus canais.
        # O FX da parte NÃO viaja (como o da cue — vive só no .ldsk).
        for k in sorted(pts, key=int):
            p = pts[k]
            pares = ['%d@%s' % (ch, _ascii_level(lv[str(ch)]))
                     for ch in sorted(int(x) for x in p.get('channels', []))
                     if str(ch) in lv]
            if not pares:
                continue                  # parte sem níveis nesta cue
            L.append('PART ' + str(int(k)))
            d_i = float(p.get('delay_in', 0) or 0)
            d_o = float(p.get('delay_out', 0) or 0)
            L.append('UP ' + _ascii_time(p.get('fade_in', 3.0))
                     + (' ' + _ascii_time(d_i) if d_i else ''))
            L.append('DOWN ' + _ascii_time(p.get('fade_out', 3.0))
                     + (' ' + _ascii_time(d_o) if d_o else ''))
            plabel = _ascii_text(p.get('label', '') or '')
            if plabel:
                L.append(('TEXT ' + plabel)[:75])
            L.extend(_ascii_wrap('CHAN', pares))
        # cue COM partes: o TEXT da cue vai AQUI, depois das partes (como a
        # Eos escreve — antes do PART 1 partia a leitura das partes)
        if label and pts:
            L.append(('TEXT ' + label)[:75])
        if follow_estilo == 'eos':
            # AUTO da cue que entra A SEGUIR a esta (o alvo do LINK, se
            # houver; senão a próxima), compensado: conta do início desta
            tgt = c.get('salta_target')
            nxt = None
            if tgt is not None:
                for c2 in cs:
                    if float(c2.get('num', -1)) == float(tgt):
                        nxt = c2
                        break
            if nxt is None and i + 1 < len(cs):
                nxt = cs[i + 1]
            if nxt is not None and nxt.get('follow') is not None:
                L.append('FOLLOWON ' + _ascii_time(
                    _cue_total(c) + float(nxt['follow'])))
        else:                             # 'directo' (grandMA/MesaDeLux)
            if c.get('follow') is not None:
                L.append('FOLLOWON ' + _ascii_time(c['follow']))
        tgt = c.get('salta_target')       # LOOP → LINK (standard); a
        if tgt is not None:               # contagem NÃO viaja (decisão
            L.append('LINK ' + _ascii_num(tgt))   # 2026-07-07, ver doc)
        L.append('')

    # ── GROUP — no MesaDeLux o grupo é uma selecção: canais a FULL ──
    for i, g in enumerate(show_dict.get('groups', []) or []):
        if not g or not g.get('channels'):
            continue
        L.append('GROUP %d' % (i + 1))
        name = _ascii_text(g.get('name', '') or '')
        if name:
            L.append(('TEXT ' + name)[:75])
        L.extend(_ascii_wrap('CHAN', ['%d@100' % int(ch)
                                      for ch in g['channels']]))
        L.append('')

    # ── SUB — os 2 submasters, se tiverem níveis ──
    for i, sm in enumerate(show_dict.get('submasters', []) or []):
        if not sm or not sm.get('levels'):
            continue
        L.append('SUB %d' % (i + 1))
        name = _ascii_text(sm.get('name', '') or '')
        if name:
            L.append(('TEXT ' + name)[:75])
        lv = sm['levels']
        L.extend(_ascii_wrap('CHAN', ['%s@%s' % (ch, _ascii_level(lv[ch]))
                                      for ch in sorted(lv, key=int)]))
        L.append('')

    L.append('ENDDATA')
    with open(filepath, 'w', encoding='ascii', errors='replace',
              newline='\r\n') as f:      # CRLF: praxe dos .asc de consola
        f.write('\n'.join(L) + '\n')
    return {'cues': n_cues, 'channels': n_chans, 'notas': notas}


def _ascii_parse_level(s):
    """Nível USITT → 0-255 interno. Standard (7.5): percentagem 0-100 ou
    hex Hnn/Hnnnn (a Eos escreve HFF=full). Por tolerância aceita-se
    também FL/FULL (aparece em ficheiros antigos) e '%' colado."""
    s = s.strip().upper().rstrip('%')
    if s in ('FL', 'FULL'):
        return 255
    if s.startswith('H'):
        h = int(s[1:], 16)
        if len(s) > 3:                   # Hnnnn (16 bit) → fica o byte alto
            h >>= 8
        return max(0, min(255, h))
    p = max(0.0, min(100.0, float(s)))
    return int(round(p * 255.0 / 100.0))


def _ascii_parse_time(s):
    """Tempo USITT (7.7) → segundos float. Formatos: 'ss', 'ss.t',
    'mm:ss', 'hh:mm:ss' (ex.: '1:30' = 90 s; '0:3' = 3 s)."""
    total = 0.0
    for parte in s.strip().split(':'):
        total = total * 60.0 + float(parte or 0)
    return total


def _ascii_parse_chans(tokens):
    """Tokens a seguir a CHAN → lista [(canal, nível 0-255)]. Dois
    dialectos: «1 AT FULL» (ETC/spec) e «1@FL 2@50» (Strand). Tokens
    ilegíveis levantam ValueError (a linha é reportada, não rebenta)."""
    up = [t.upper() for t in tokens]
    if 'AT' in up:
        i = up.index('AT')
        lvl = _ascii_parse_level(tokens[i + 1])
        return [(int(float(t)), lvl) for t in tokens[:i]]
    out = []
    for t in tokens:
        c, _, l = t.partition('@')
        out.append((int(float(c)), _ascii_parse_level(l) if l else 255))
    return out


def ascii_sniff_follow(filepath):
    """Espreita o cabeçalho de um .asc/.alq e tenta adivinhar o estilo do
    FOLLOWON: 'eos' (compensado), 'directo' (grandMA/MesaDeLux) ou None
    (desconhecido — a UI pergunta ao utilizador). Pistas, por ordem:
    marcador ! MESADELUX FOLLOW (nosso), MANUFACTURER ETC → 'eos',
    MANUFACTURER ByWorm/MesaDeLux sem marcador (exports antigos) →
    'directo'."""
    fabricante = None
    try:
        with open(filepath, 'r', encoding='latin-1') as f:
            for _ in range(200):
                ln = f.readline()
                if not ln:
                    break
                s = ln.strip()
                u = s.upper()
                if u.startswith('! MESADELUX FOLLOW'):
                    v = s.split()[-1].lower()
                    if v in ('eos', 'directo'):
                        return v
                elif u.startswith('MANUFACTURER'):
                    fabricante = u
    except Exception:
        return None
    if fabricante:
        if 'ETC' in fabricante:
            return 'eos'
        if 'BYWORM' in fabricante or 'MESADELUX' in fabricante:
            return 'directo'
    return None


def import_ascii(filepath, follow_estilo=None):
    """Lê um ficheiro USITT ASCII (.asc/.alq — mesmo parser) e devolve
    (show_dict, relatorio): dict no formato de _load_data() + relatório
    {'cues', 'channels', 'ignoradas', 'exemplos', 'follow_estilo',
    'notas'}. O parser NUNCA rebenta: linha ilegível ou keyword
    desconhecida → ignora e conta. Registos Eos '$Xyz' (uma só cifra)
    fecham o bloco actual (senão o 'Text' de um $Curve/$Effect ia parar
    ao label da última cue). Extensões Eos entendidas: $$LoopNum (contagem
    do LINK), $$Follow (=FOLLOWON), $$Hang (AUTO contado do FIM — a nossa
    semântica, entra directo), $$ChanMove (níveis COM os movimentos a
    zero, que faltam nas linhas Chan da Eos).

    follow_estilo — como interpretar o FOLLOWON: 'eos' (compensado:
    converte para a nossa semântica subtraindo o tempo da cue precedente),
    'directo' (valor tal e qual, na própria cue) ou None = auto-detectar
    via ascii_sniff_follow (na dúvida, 'directo')."""
    if follow_estilo not in ('eos', 'directo'):
        follow_estilo = ascii_sniff_follow(filepath) or 'directo'
    with open(filepath, 'r', encoding='latin-1') as f:   # nunca falha
        raw_lines = f.read().splitlines()

    cues, groups, subs, patch = [], [None] * 20, [], {}
    intensity_mode = 'tracking'
    ignoradas, exemplos, notas = 0, [], []
    ctx = None            # ('cue', dict) | ('group', dict) | ('sub', dict)
    #                     | ('patch',) | ('skip',) — alvo dos secundários

    def _ignora(n, ln):
        nonlocal ignoradas
        ignoradas += 1
        if len(exemplos) < 8:
            exemplos.append('%d: %s' % (n, ln.strip()[:60]))

    def _patch_tokens(toks, n, ln):
        """Tokens canal<dimmer[@prop] → patch (1 universo por canal)."""
        ok = False
        for t in toks:
            try:
                c, d = t.split('@')[0].split('<')
                ch, dim = int(float(c)), int(float(d))
                if not (1 <= ch <= MAX_CHANNELS) or dim < 1:
                    raise ValueError
                uni, addr = (dim - 1) // 512 + 1, (dim - 1) % 512 + 1
                e = patch.setdefault(str(ch), {'universe': uni, 'addrs': []})
                if e['universe'] == uni:
                    if addr not in e['addrs']:
                        e['addrs'].append(addr)
                    ok = True
                # universo diferente do 1.º do canal: MesaDeLux só tem um
                # universo por canal — fica de fora (contado)
            except (ValueError, IndexError):
                pass
        if not ok:
            _ignora(n, ln)
        return ok

    def _chans_ctx(pares):
        """Aplica pares (canal, nível 0-255) ao bloco actual (cue/part/
        group/sub/skip). Devolve False se não há bloco que os aceite."""
        if not ctx:
            return False
        if ctx[0] == 'part':
            # v6.3.3 — nível vai para a CUE; o canal fica membro da parte
            for ch, lvl in pares:
                if 1 <= ch <= MAX_CHANNELS:
                    ctx[1]['levels'][str(ch)] = lvl
                    if ch not in ctx[2]['channels']:
                        ctx[2]['channels'].append(ch)
        elif ctx[0] == 'cue':
            for ch, lvl in pares:
                if 1 <= ch <= MAX_CHANNELS:
                    ctx[1]['levels'][str(ch)] = lvl
        elif ctx[0] == 'group':
            for ch, lvl in pares:
                if (1 <= ch <= MAX_CHANNELS and lvl > 0
                        and ch not in ctx[1]['channels']):
                    ctx[1]['channels'].append(ch)
        elif ctx[0] == 'sub':
            for ch, lvl in pares:
                if 1 <= ch <= MAX_CHANNELS:
                    ctx[1]['levels'][str(ch)] = lvl
        elif ctx[0] != 'skip':
            return False
        return True

    for n, ln in enumerate(raw_lines, 1):
        line = ln.strip()
        if not line:
            continue
        if line.startswith('!'):
            toks = line[1:].split()      # comentário — só o nosso MODE conta
            if (len(toks) >= 3 and toks[0].upper() == 'MESADELUX'
                    and toks[1].upper() == 'MODE'
                    and toks[2] in ('tracking', 'cue_only')):
                intensity_mode = toks[2]
            continue
        # vírgulas são delimitadores válidos no standard (5.x) — só o TEXT
        # as preserva (usa a linha original)
        toks = line.replace(',', ' ').split()
        kw = toks[0].upper()
        try:
            if kw == 'ENDDATA':
                break
            elif kw in ('IDENT', 'MANUFACTURER', 'CONSOLE', 'CLEAR', 'SET'):
                ctx = None               # básicas reconhecidas — nada a fazer
            elif kw == '$$FORMAT':       # metadado de cabeçalho Eos —
                pass                     # reconhecido, nada a fazer
            elif kw == '$$LOOPNUM':      # extensão Eos: contagem do LINK
                if ctx and ctx[0] in ('cue', 'part'):
                    ctx[1]['salta_count'] = int(float(toks[1]))
                elif not (ctx and ctx[0] == 'skip'):
                    _ignora(n, ln)
            elif kw == '$$FOLLOW':       # extensão Eos: = FOLLOWON
                if ctx and ctx[0] in ('cue', 'part'):
                    ctx[1]['_follow_raw'] = _ascii_parse_time(toks[1])
                elif not (ctx and ctx[0] == 'skip'):
                    _ignora(n, ln)
            elif kw == '$$HANG':         # extensão Eos: AUTO contado do FIM
                if ctx and ctx[0] in ('cue', 'part'):   # (a NOSSA semântica)
                    ctx[1]['_hang_raw'] = _ascii_parse_time(toks[1])
                elif not (ctx and ctx[0] == 'skip'):
                    _ignora(n, ln)
            elif kw == '$$CHANMOVE':     # extensão Eos: níveis COM os
                if not _chans_ctx(       # movimentos a zero (o Chan da Eos
                        _ascii_parse_chans(toks[1:])):   # omite-os)
                    _ignora(n, ln)
            elif kw.startswith('$$'):
                _ignora(n, ln)           # dados de fabricante — fora (v1)
            elif kw.startswith('$'):
                # registo primário Eos ($Curve, $Effect, $Patch, $CueList…)
                # — fecha o bloco actual, senão o 'Text' dele contaminava
                # o label da última cue lida
                _ignora(n, ln)
                ctx = ('skip',)
            elif kw == 'PATCH':
                page = int(float(toks[1])) if len(toks) > 1 else 1
                if page != 1:            # só a página 1 (v1)
                    _ignora(n, ln)
                    ctx = ('skip',)
                else:
                    ctx = ('patch',)
                    if len(toks) > 2:
                        _patch_tokens(toks[2:], n, ln)
            elif kw == 'CUE':
                num = float(toks[1])
                cue = {'num': int(num) if num == int(num) else num,
                       'label': '', 'fade_in': 3.0, 'fade_out': 3.0,
                       'delay_in': 0.0, 'delay_out': 0.0, 'follow': None,
                       'levels': {}, 'midi_nota': None,
                       'midi_direccao': None, 'midi_delay_s': 0.0}
                cues.append(cue)
                ctx = ('cue', cue)
            elif kw == 'GROUP':
                g_num = int(float(toks[1]))
                if 1 <= g_num <= 20:
                    g = {'name': '', 'halo': None, 'channels': []}
                    groups[g_num - 1] = g
                    ctx = ('group', g)
                else:                    # a mesa só tem 20 grupos
                    _ignora(n, ln)
                    ctx = ('skip',)
            elif kw == 'SUB':
                s_num = int(float(toks[1]))
                if 1 <= s_num <= 2:      # decisão: importar os 2 primeiros
                    sm = {'name': 'Sub %d' % s_num, 'levels': {}}
                    while len(subs) < s_num:
                        subs.append(None)
                    subs[s_num - 1] = sm
                    ctx = ('sub', sm)
                else:
                    _ignora(n, ln)
                    ctx = ('skip',)
            elif kw == 'TEXT':
                txt = line.split(None, 1)[1] if len(toks) > 1 else ''
                if ctx and ctx[0] == 'part':          # v6.3.3
                    # TEXT ANTES dos CHAN da parte = label da PARTE; DEPOIS
                    # (parte já com canais) = label da CUE — a Eos põe o
                    # texto da cue no fim, no contexto da última parte.
                    if ctx[2].get('channels'):
                        ctx[1]['label'] = txt         # ctx[1] = a cue
                    else:
                        ctx[2]['label'] = txt[:40]
                elif ctx and ctx[0] == 'cue':
                    ctx[1]['label'] = txt
                elif ctx and ctx[0] == 'group':
                    ctx[1]['name'] = txt[:20]
                elif ctx and ctx[0] == 'sub':
                    ctx[1]['name'] = txt[:20]
                elif ctx and ctx[0] == 'skip':
                    pass                 # texto de um bloco já descartado
                else:
                    _ignora(n, ln)
            elif kw in ('UP', 'DOWN', 'TIME'):
                # TIME não é do standard, mas aceita-se a ler (tolerância)
                if ctx and ctx[0] in ('cue', 'part'):
                    alvo = ctx[2] if ctx[0] == 'part' else ctx[1]  # v6.3.3
                    t = _ascii_parse_time(toks[1])
                    if kw in ('UP', 'TIME'):
                        alvo['fade_in'] = t
                    if kw in ('DOWN', 'TIME'):
                        alvo['fade_out'] = t
                    if len(toks) > 2:    # UP/DOWN <fade> <delay> (10.2/10.7)
                        d = _ascii_parse_time(toks[2])
                        alvo['delay_in' if kw != 'DOWN'
                             else 'delay_out'] = d
                elif ctx and ctx[0] == 'skip':
                    pass
                else:
                    _ignora(n, ln)
            elif kw == 'FOLLOWON':
                # fica em bruto; a semântica resolve-se no fim (estilo)
                if ctx and ctx[0] in ('cue', 'part'):
                    ctx[1]['_follow_raw'] = _ascii_parse_time(toks[1])
                elif not (ctx and ctx[0] == 'skip'):
                    _ignora(n, ln)
            elif kw == 'LINK':
                if ctx and ctx[0] in ('cue', 'part'):
                    t = float(toks[1])   # LINK não conta voltas → eterno
                    ctx[1]['salta_target'] = (int(t) if t == int(t) else t)
                    ctx[1]['salta_count'] = 0
                elif not (ctx and ctx[0] == 'skip'):
                    _ignora(n, ln)
            elif kw == 'PART':
                # v6.3.3 — cria a parte na cue (antes fundia-se); PART 1
                # é a própria cue (volta ao contexto dela)
                if ctx and ctx[0] in ('cue', 'part'):
                    cue_d = ctx[1]
                    try:
                        pn = int(float(toks[1]))
                    except (TypeError, ValueError, IndexError):
                        pn = 0
                    if pn == 1:
                        ctx = ('cue', cue_d)
                    elif 2 <= pn <= NUM_PARTS:
                        part = cue_d.setdefault('parts', {}).setdefault(
                            str(pn), {'channels': [], 'fade_in': 3.0,
                                      'fade_out': 3.0, 'delay_in': 0.0,
                                      'delay_out': 0.0, 'label': ''})
                        ctx = ('part', cue_d, part)
                    else:
                        # parte >NUM_PARTS: os NÍVEIS fundem na cue mas os
                        # tempos/texto dela vão para uma parte-fantasma
                        # (senão o UP/DOWN seguinte reescrevia os da cue)
                        _ignora(n, ln)
                        ctx = ('part', cue_d,
                               {'channels': [], 'label': ''})
                elif not (ctx and ctx[0] == 'skip'):
                    _ignora(n, ln)
            elif kw == 'CHAN':
                if not _chans_ctx(_ascii_parse_chans(toks[1:])):
                    _ignora(n, ln)
            elif ctx and ctx[0] == 'patch' and '<' in line:
                _patch_tokens(toks, n, ln)   # continuação de PATCH
            elif ctx and ctx[0] in ('cue', 'part', 'group', 'sub') and '@' in line:
                # continuação de CHAN — um registo estende-se até à
                # keyword seguinte (standard 5.x); ex.: '5@90 100@2'
                if not _chans_ctx(_ascii_parse_chans(toks)):
                    _ignora(n, ln)
            else:
                _ignora(n, ln)           # keyword desconhecida
        except (ValueError, IndexError, KeyError):
            _ignora(n, ln)               # linha ilegível — NUNCA rebenta

    cues.sort(key=lambda c: float(c['num']))
    # v6.3.3 — PARTES: normaliza/limpa (regra 1 canal = 1 parte, tipos,
    # partes vazias fora) antes de resolver o FOLLOWON (que usa os tempos)
    for c in cues:
        pts = normaliza_parts(c.get('parts'))
        if pts:
            c['parts'] = pts
        else:
            c.pop('parts', None)
    # ── FOLLOWON → follow (semântica MesaDeLux) segundo o estilo ──
    # 'directo': o valor é o follow da própria cue, tal e qual.
    # 'eos': o FOLLOWON da cue A dispara a que entra A SEGUIR (o alvo do
    #        LINK, se houver; senão a seguinte na lista), contado do
    #        INÍCIO de A → follow = valor − tempo_total(A), nunca <0.
    #        $$Hang já vem na nossa semântica (conta do FIM) — directo.
    idx_por_num = {float(c['num']): i for i, c in enumerate(cues)}

    def _destino(i, c):
        """Índice da cue que entra a seguir à cue i (LINK ciente)."""
        tgt = c.get('salta_target')
        if tgt is not None and float(tgt) in idx_por_num:
            return idx_por_num[float(tgt)]
        return i + 1 if i + 1 < len(cues) else None

    def _poe_follow(j, f):
        if cues[j].get('follow') is not None and cues[j]['follow'] != f:
            notas.append('AUTO da cue %s definido 2x (fica %s)'
                         % (_ascii_num(cues[j]['num']), _ascii_num(f)))
        cues[j]['follow'] = f

    for i, c in enumerate(cues):
        raw = c.pop('_follow_raw', None)
        hang = c.pop('_hang_raw', None)
        if hang is None and raw is None:
            continue
        if follow_estilo == 'directo' and hang is None:
            c['follow'] = raw            # valor tal e qual, nesta cue
            continue
        j = _destino(i, c)
        if j is None:
            notas.append('AUTO da cue %s sem cue seguinte'
                         % _ascii_num(c['num']))
            continue
        if hang is not None:             # $$Hang: já conta do FIM
            _poe_follow(j, hang)
        else:                            # FOLLOWON estilo eos: compensa
            f = raw - _cue_total(c)
            if f < 0:
                notas.append('AUTO da cue %s disparava a meio do fade '
                             '(%s -> 0)' % (_ascii_num(cues[j]['num']),
                                            _ascii_num(f)))
                f = 0.0
            _poe_follow(j, f)
    max_ch = 0
    for src in ([int(k) for k in patch]
                + [int(k) for c in cues for k in c['levels']]
                + [ch for g in groups if g for ch in g['channels']]
                + [int(k) for sm in subs if sm for k in sm['levels']]):
        max_ch = max(max_ch, src)
    show = {
        'num_channels': max(1, min(MAX_CHANNELS, max_ch or 100)),
        'intensity_mode': intensity_mode,
        'patch': patch,
        'cues': cues,
        'groups': groups,
        # posicional: SUB 2 sem SUB 1 no ficheiro fica mesmo no Sub 2
        'submasters': [sm or {'name': 'Sub %d' % (i + 1), 'levels': {}}
                       for i, sm in enumerate(subs)],
    }
    rel = {'cues': len(cues), 'channels': len(patch),
           'ignoradas': ignoradas, 'exemplos': exemplos,
           'follow_estilo': follow_estilo, 'notas': notas}
    return show, rel


# ─────────────────────────────────────────────
# PATCH
# ─────────────────────────────────────────────
class Patch:
    """Cada canal mapeia para um ou vários endereços DMX.

    Entrada por canal (dict):
        universe : nº do universo
        addrs    : lista de endereços DMX (8 bit; course, se for 16 bit)
        bit16    : True se o canal é de 16 bits (há endereços 'fine')
        fine     : lista de endereços fine; se mais curta → course+1
        halo     : nome de cor do halo (ou None)
        display  : 'pct' (0–100 %) ou 'dec' (0–255) na grelha de canais
        default  : valor DMX fixo 0–255 (canal sempre nesse valor) ou None
    """
    def __init__(self):
        self.data = {}
        for ch in range(1, NUM_CHANNELS + 1):
            self.data[ch] = self._default(ch)

    @staticmethod
    def _default(ch):
        return {'universe': 1, 'addrs': [ch], 'bit16': False,
                'fine': [], 'halo': None, 'display': 'pct', 'default': None,
                'name': '', 'alcunha': 0, 'curva': CURVE_LINEAR}

    @staticmethod
    def _empty():
        return {'universe': 1, 'addrs': [], 'bit16': False,
                'fine': [], 'halo': None, 'display': 'pct', 'default': None,
                'name': '', 'alcunha': 0, 'curva': CURVE_LINEAR}

    def get(self, ch):
        return self.data.get(ch, self._default(ch))

    def set(self, ch, entry):
        self.data[ch] = entry

    def clear_all(self):
        """Apaga os endereços DMX (8 e 16 bit) e o valor de defeito.
        O universo, o halo e o modo de mostrar mantêm-se."""
        for ch in range(1, NUM_CHANNELS + 1):
            e = self.data.get(ch) or self._default(ch)
            e['addrs'] = []
            e['fine'] = []
            e['bit16'] = False
            e['default'] = None
            self.data[ch] = e

    def one_to_one(self):
        """Renumera 1 para 1: canal N → DMX N."""
        for ch in range(1, NUM_CHANNELS + 1):
            self.data[ch] = self._default(ch)

    def universes_used(self):
        return {e['universe'] for e in self.data.values() if e.get('addrs')}

    def remove_addr_conflicts(self, keep_ch):
        """v5 — um endereço DMX (universo, addr) só pode estar num canal:
        remove de TODOS os outros canais os endereços (course e fine, no
        MESMO universo) que keep_ch passou a usar. Ex: pôr DMX 7 univ 1 no
        canal 6 tira o 7 do canal 7 (que fica sem esse endereço).
        Devolve a lista de canais alterados."""
        e = self.data.get(keep_ch)
        if not e:
            return []
        univ = e.get('universe', 1)
        taken = set(e.get('addrs', [])) | set(e.get('fine', []))
        if not taken:
            return []
        changed = []
        for ch, other in self.data.items():
            if ch == keep_ch or other.get('universe', 1) != univ:
                continue
            new_a = [a for a in other.get('addrs', []) if a not in taken]
            new_f = [a for a in other.get('fine', []) if a not in taken]
            if (new_a != other.get('addrs', [])
                    or new_f != other.get('fine', [])):
                other['addrs'] = new_a
                other['fine'] = new_f
                other['bit16'] = len(new_f) > 0
                changed.append(ch)
        return changed

    def enforce_unique_addresses(self):
        """v6 — garante a regra GLOBAL: um endereço DMX (universo, addr) só
        pode estar num canal. Varre todos os canais por ordem; o PRIMEIRO
        canal a usar cada (univ, addr) fica com ele, os seguintes perdem-no
        (course e fine). Devolve a lista de canais alterados. Usado no
        Aplicar do renumerador como rede de segurança universal."""
        seen = set()                          # (univ, addr) já atribuídos
        changed = []
        for ch in sorted(self.data.keys()):
            e = self.data[ch]
            univ = e.get('universe', 1)
            new_a, new_f = [], []
            touched = False
            for a in e.get('addrs', []):
                if (univ, a) in seen:
                    touched = True
                else:
                    seen.add((univ, a))
                    new_a.append(a)
            for a in e.get('fine', []):
                if (univ, a) in seen:
                    touched = True
                else:
                    seen.add((univ, a))
                    new_f.append(a)
            if touched:
                e['addrs'] = new_a
                e['fine'] = new_f
                e['bit16'] = len(new_f) > 0
                changed.append(ch)
        return changed


# ─────────────────────────────────────────────
# PARTES (v6.3.3) — validação do campo 'parts' das memórias
# ─────────────────────────────────────────────
def normaliza_parts(raw):
    """v6.3.3 — valida/limpa o dict 'parts' de uma memória vinda de
    ficheiro (.ldsk ou ASCII). Devolve {'2'..'8': {...}} ou None se nada
    aproveitável. Regras: nº da parte 2..NUM_PARTS (a 1 é a própria
    memória — nunca se guarda); canais int 1..MAX_CHANNELS; UM canal só
    numa parte (regra USITT 10.5 — em conflito fica na de nº mais alto);
    tempos float >=0; fx = {'num' 1..NUM_FX, 'fade' bool} ou nada;
    partes sem canais são descartadas (não fazem nada)."""
    if not isinstance(raw, dict):
        return None
    dono, partes = {}, {}
    for k, p in raw.items():
        try:
            n = int(float(k))
        except (TypeError, ValueError):
            continue
        if not (2 <= n <= NUM_PARTS) or not isinstance(p, dict):
            continue

        def _t(campo, defeito=0.0):
            try:
                return max(0.0, float(p.get(campo, defeito)))
            except (TypeError, ValueError):
                return defeito

        ent = {'channels': [],
               'fade_in': _t('fade_in', 3.0),
               'fade_out': _t('fade_out', 3.0),
               'delay_in': _t('delay_in'),
               'delay_out': _t('delay_out'),
               'label': str(p.get('label', '') or '')[:40]}
        fx = p.get('fx')
        if isinstance(fx, dict):
            try:
                fn = int(fx.get('num', 0))
            except (TypeError, ValueError):
                fn = 0
            if 1 <= fn <= NUM_FX:
                ent['fx'] = {'num': fn, 'fade': bool(fx.get('fade', True))}
        for ch in (p.get('channels') or []):
            try:
                ch = int(ch)
            except (TypeError, ValueError):
                continue
            if 1 <= ch <= MAX_CHANNELS:
                dono[ch] = max(dono.get(ch, 0), n) if ch in dono else n
        partes[n] = ent
    # cada canal fica só na sua parte "dona"
    for ch, n in dono.items():
        if n in partes:
            partes[n]['channels'].append(ch)
    out = {}
    for n, ent in partes.items():
        ent['channels'].sort()
        if ent['channels']:
            out[str(n)] = ent
    return out or None


# ─────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────
class Engine:
    def __init__(self):
        self.patch = Patch()
        self.output = [0.0] * (NUM_CHANNELS + 1)        # saída actual (0-255)
        self.programmer = [None] * (NUM_CHANNELS + 1)   # None = não forçado
        self.active = [False] * (NUM_CHANNELS + 1)      # True = recebeu ordem
        self._prog_base = [None] * (NUM_CHANNELS + 1)   # valor antes do override
        self._prog_abase = [None] * (NUM_CHANNELS + 1)  # estado activo anterior
        for ch in range(1, NUM_CHANNELS + 1):
            self.output[ch] = float(self._partida(ch))

        self.cues = [self._make_zero()]   # cues[0] é sempre a memória ZERO
        self.current_cue_idx = -1
        # v6.2: modelo da cuelist (guardado no show).
        #   'cue_only' (novo): intensidades (pct) cue-only/não-tracking — cada
        #     cue é um look fechado; atributos (dec) tracking. Block = só dec.
        #   'tracking' (shows antigos): tudo LTP+tracking (comportamento v6.1).
        self.intensity_mode = 'cue_only'
        self.presets = ["0", "0"]         # pré-valores (guardados no show)
        self.retratos = [None] * 20       # v4.9: 20 retratos (no show)
        self.groups = [None] * 20         # v4.9: 20 grupos de canais (no show)
        self.submasters = self._make_submasters()   # 2 submasters manuais

        # v5 — 8 efeitos (página FX). Cada entrada é None (vazio) ou dict:
        #   {'name': str, 'mode': 'manual'|'dinamico',
        #    'steps': [...],      # manual: passos {num, levels, fade, auto}
        #    'channels': [...],   # dinamico: canais comprados
        #    'levels': {...}}     # dinamico: niveis base dos canais
        #   (parametros do dinamico juntam-se na etapa 2)
        # Gravado no show ('fx'); o estado ACTIVO é runtime e nao se grava.
        # Conflito entre FX activos no mesmo canal: HTP (valor mais alto).
        self.fx = [None] * NUM_FX
        self.fx_active = [False] * NUM_FX
        # v5 etapa 1 — runtime do loop manual de cada FX activo:
        #   {'idx': passo actual, 'phase': 'fade'|'hold', 't0': inicio da
        #    fase, 'from': {ch: nivel}, 'to': {ch: nivel}}
        # fx_levels = resultado de cada tick {ch: 0-255}, consumido pelo
        # _flush_dmx e pela grelha. Prioridade: programador > FX > playback.
        self._fx_run = [None] * NUM_FX
        self.fx_levels = {}
        # v5 etapa 4 — FX lançados pela SEQUÊNCIA (coluna FX da cuelist):
        # escala 0..1 por FX (o modo "acompanha o fade" rampa-a com os
        # tempos da memória) e a rampa em curso por FX.
        self._fx_scale = [1.0] * NUM_FX
        self._fx_ramp = [None] * NUM_FX

        self.fade_start = [0] * (NUM_CHANNELS + 1)
        self.fade_target = [0] * (NUM_CHANNELS + 1)
        self.fade_in = 0.0           # tempo de subida (canais a aumentar)
        self.fade_out = 0.0          # tempo de descida (canais a diminuir)
        self.delay_in = 0.0          # atraso antes da entrada começar
        self.delay_out = 0.0         # atraso antes da saída começar
        # v6.3.3 — PARTES: tempos POR CANAL, preenchidos no GO segundo a
        # parte de cada canal (direcção já decidida → um só par por canal)
        self.fade_dur = [0.0] * (NUM_CHANNELS + 1)   # duração do movimento
        self.fade_del = [0.0] * (NUM_CHANNELS + 1)   # atraso do movimento
        self.fade_total = 0.0        # fim da transição = max(atraso+duração)
        self.fade_time = 0.0
        self.fading = False
        self._releasing = False      # v6.2: fade de LIBERTA/LIMPA (não arma follow)

        self.follow_armed = False    # follow agendado após o fade
        self.follow_at = 0.0         # timestamp absoluto para o auto-GO
        self.follow_total = 0.0      # v6.3: duração do countdown (p/ a barra)
        self.auto_fade = False       # transição actual disparada por AUTO

        self.paused = False          # transição/encadeado congelados
        self._pause_fade_elapsed = 0.0
        self._pause_follow_remaining = 0.0

        self._salta_idx = None       # índice da memória com SALTAR activo
        self._salta_remaining = 0    # saltos restantes

        self.universes = {}          # {univ_num: bytearray(512)}
        self.sacn_sender = None
        self.sacn_enabled = False
        # v3: lista de até 4 universos de saída ARBITRÁRIOS (ex: [1, 7, 9, 10]).
        # v4: passou a ser a lista MANUAL — só é usada com universes_auto OFF.
        self.sacn_universes = [1]
        # v4: por defeito os universos de saída derivam do RENUMERADOR
        # ("o que se patcha é o que sai") — ver out_universes(). A lista
        # manual fica como recurso (ex: emitir um universo ainda sem canais).
        self.universes_auto = True
        self.bo_active          = False  # B.O. (Black Out) - zera DMX sem perder estado
        # v5 — modos de visualização tipo GrandMA (afectam só a saída DMX,
        # NÃO o estado guardado): Highlight põe a selecção a 255; Solo deixa
        # só a selecção acesa (afecta apenas canais dimmer, display='pct').
        self.highlight = False
        # v6.2: nivel a que o Highlight põe os canais destacados (0-255).
        # Por defeito 255 (100%); a consola pode descer/subir no modo Highlight.
        self.highlight_level = 255
        self.solo = False
        self.hs_channels = frozenset()   # canais do H/S (= selecção da app)
        # v6 — teste de saída DMX (vista DMX): força endereços a 255 e/ou
        # isola um universo (só os forçados sobrevivem)
        self.dmx_force = frozenset()     # {(univ, addr), …} forçados a 255
        self.dmx_solo = False
        self.dmx_solo_univ = None
        self.sacn_multicast = True
        self.sacn_unicast_ip = "192.168.1.10"
        self.sacn_bind_ip = ""       # "" = 0.0.0.0 (OS escolhe a interface)

        # v4 — Art-Net em paralelo com o sACN (mesma lista de universos)
        self.artnet_sender = None
        self.artnet_enabled = False
        self.artnet_broadcast = True
        self.artnet_dest_ip = "192.168.1.10"   # usado quando broadcast OFF
        self.artnet_bind_ip = ""

        self.on_change = None        # callback → UI (só pode marcar flags!)

        # v4 — protege as estruturas internas contra o resize/load enquanto
        # a thread do engine itera (RLock: o tick pode chamar go() via follow)
        self._lock = threading.RLock()
        self._zero512 = bytes(512)   # template p/ limpar buffers depressa

        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    # ── loop ──────────────────────────────────
    def _loop(self):
        # v4: um erro num tick NUNCA pode matar a thread do engine — sem ela
        # a mesa deixa de emitir DMX silenciosamente.
        while self._running:
            try:
                with self._lock:
                    self._tick()
            except Exception as e:
                print('[engine] erro no tick (ignorado):', e)
            time.sleep(0.04)          # ~25 fps

    def _tick(self):
        changed = False

        # fade (entrada/saída separadas, com atrasos) — congelado em pausa
        if self.fading and not self.paused:
            elapsed = time.time() - self.fade_time
            for ch in range(1, NUM_CHANNELS + 1):
                s, tg = self.fade_start[ch], self.fade_target[ch]
                # v6.3.3 — PARTES: tempos por canal, fixados no GO (a
                # direcção subir→IN / descer→OUT já foi lá decidida)
                dur, delay = self.fade_dur[ch], self.fade_del[ch]
                local = elapsed - delay
                if local <= 0:
                    t = 0.0
                elif dur > 0:
                    t = min(local / dur, 1.0)
                else:
                    t = 1.0
                v = s + (tg - s) * t          # float — permite precisão 16 bit
                if self.output[ch] != v:
                    self.output[ch] = v
                    changed = True
            if elapsed >= self.fade_total:   # v6.3.3: fim = max das PARTES
                self.fading = False
                changed = True   # v6.2: força 1 refresh final (dígitos brancos
                                 # voltam à cor de estado ao acabar o movimento)
                if self._releasing:
                    self._releasing = False   # LIBERTA/LIMPA não arma follow
                else:
                    self._arm_follow()

        # follow (encadeamento automático) — congelado em pausa
        if self.follow_armed and not self.paused and time.time() >= self.follow_at:
            self.follow_armed = False
            self.go()
            self.auto_fade = True     # esta transição foi automática (AUTO)
            changed = True

        # programmer override
        for ch in range(1, NUM_CHANNELS + 1):
            if self.programmer[ch] is not None:
                if self.output[ch] != self.programmer[ch]:
                    self.output[ch] = self.programmer[ch]
                    changed = True

        # v5 — camada FX (acima do playback, abaixo do programador)
        if self._tick_fx(time.time()):
            changed = True

        self._flush_dmx()
        # actualiza a UI sempre que algo muda — e durante toda a transição,
        # para a barra de progresso evoluir mesmo nos atrasos
        if (changed or self.fading) and self.on_change:
            self.on_change()

    # ── valor de defeito (ponto de partida) ───
    def _partida(self, ch):
        """Valor de partida (defeito) do canal — 0 se não definido."""
        d = self.patch.get(ch).get('default')
        return int(d) if d is not None else 0

    def _output_to_partida(self):
        """Repõe toda a saída nos valores de partida (defeito) — tudo passivo."""
        for ch in range(1, NUM_CHANNELS + 1):
            self.output[ch] = float(self._partida(ch))
            self.active[ch] = False

    def dmx_snapshot(self, univ):
        """v6 — devolve os 512 bytes de saída DMX do universo (cópia segura
        para a thread da UI). Zeros se o universo não estiver a ser emitido."""
        with self._lock:
            buf = self.universes.get(univ)
            return bytes(buf) if buf is not None else bytes(512)

    def apply_defaults_to_passive(self):
        """v6 — reaplica o valor de partida (defeito) aos canais PASSIVOS
        (sem ordem activa e fora do programador). Usado depois de editar o
        renumerador: um defeito acabado de definir (ex.: PAN 127) passa a
        aparecer na grelha e a ser o ponto de partida do +/-. NÃO mexe nos
        canais activos (não estraga a luz que está em cena)."""
        with self._lock:
            for ch in range(1, NUM_CHANNELS + 1):
                if (ch < len(self.active) and not self.active[ch]
                        and self.programmer[ch] is None):
                    self.output[ch] = float(self._partida(ch))
        if self.on_change:
            self.on_change()

    # ── submasters ────────────────────────────
    @staticmethod
    def _make_submasters():
        """Dois submasters manuais: cada um guarda uma luz (níveis) e tem um
        fader 0-100 % que a mistura na saída por HTP (o mais alto prevalece)."""
        return [{'name': 'Sub 1', 'levels': {}, 'fader': 0},
                {'name': 'Sub 2', 'levels': {}, 'fader': 0}]

    def set_submaster_fader(self, idx, value):
        """Move o fader do submaster idx (0-100 %)."""
        if 0 <= idx < len(self.submasters):
            try:
                self.submasters[idx]['fader'] = max(0, min(100,
                    int(round(float(value)))))
            except (ValueError, TypeError):
                pass

    def save_submaster(self, idx, name):
        """Grava no submaster idx a luz actual (canais no programador +
        activos). O fader mantém-se onde está."""
        if not (0 <= idx < len(self.submasters)):
            return
        levels = {}
        for ch in range(1, NUM_CHANNELS + 1):
            if self.programmer[ch] is not None:
                levels[str(ch)] = int(self.programmer[ch])
            elif self.active[ch]:
                levels[str(ch)] = int(round(self.output[ch]))
        self.submasters[idx]['name'] = name
        self.submasters[idx]['levels'] = levels

    def submaster_contribution(self, ch):
        """Maior contribuição dos submasters para o canal ch (0.0 se nenhuma)."""
        best = 0.0
        for sm in self.submasters:
            fv = sm['fader'] / 100.0
            if fv > 0.0:
                sl = sm['levels'].get(str(ch))
                if sl is not None:
                    c = sl * fv
                    if c > best:
                        best = c
        return best

    # ── FX (v5 etapa 1 — loop manual) ─────────
    @staticmethod
    def _fx_clamp_t(v):
        """Tempos de fade/auto dos passos: 0 a 60 s (0 = corte seco /
        avanço imediato — pedido do autor)."""
        try:
            v = float(v)
        except (TypeError, ValueError):
            v = 1.0
        return max(0.0, min(60.0, v))

    @staticmethod
    def _fx_union(fx):
        """Conjunto de canais do FX = união dos canais de todos os passos."""
        chans = set()
        for st in fx.get('steps', []):
            for k in st.get('levels', {}):
                try:
                    chans.add(int(k))
                except (TypeError, ValueError):
                    pass
        return chans

    @staticmethod
    def _fx_step_levels(fx, idx, union=None):
        """Níveis ABSOLUTOS do passo idx. Sem LTP: cada passo é a fotografia
        completa — canais do FX ausentes deste passo valem 0."""
        steps = fx.get('steps', [])
        if not steps:
            return {}
        st = steps[idx % len(steps)]
        levels = st.get('levels', {})
        if union is None:
            union = Engine._fx_union(fx)
        out = {}
        for ch in union:
            v = levels.get(str(ch), levels.get(ch, 0))
            try:
                out[ch] = max(0, min(255, int(v)))
            except (TypeError, ValueError):
                out[ch] = 0
        return out

    def fx_toggle(self, i):
        """Liga/desliga o FX i (toggle, como um sampler de som). O primeiro
        fade parte dos níveis actualmente em cena — entrada suave. Devolve
        o novo estado."""
        if not (0 <= i < len(self.fx)):
            return False
        with self._lock:
            fx = self.fx[i]
            if fx is None or self.fx_active[i]:
                self.fx_active[i] = False
                self._fx_run[i] = None
            else:
                self.fx_active[i] = True
                self._fx_run[i] = None      # o tick inicializa o loop
            # toggle manual cancela qualquer rampa da sequência
            self._fx_scale[i] = 1.0
            self._fx_ramp[i] = None
        if self.on_change:
            self.on_change()
        return self.fx_active[i]

    def fx_deactivate_all(self):
        """v6.3 — desliga TODOS os FX activos (sem os apagar). Usado no RELEASE
        (2.º toque) para o laranja dos FX cair também."""
        changed = False
        with self._lock:
            for i in range(len(self.fx_active)):
                if self.fx_active[i]:
                    self.fx_active[i] = False
                    self._fx_run[i] = None
                    self._fx_scale[i] = 1.0
                    self._fx_ramp[i] = None
                    changed = True
            self.fx_levels = {}
        if changed and self.on_change:
            self.on_change()

    def fx_clear(self, i):
        """Apaga o FX i por completo (definição + estado de execução)."""
        if not (0 <= i < len(self.fx)):
            return
        with self._lock:
            self.fx[i] = None
            self.fx_active[i] = False
            self._fx_run[i] = None
            self._fx_scale[i] = 1.0
            self._fx_ramp[i] = None
        if self.on_change:
            self.on_change()

    def _fx_start_run(self, i, fx, now):
        """Prepara o runtime de um FX manual: 1.º fade parte da cena actual."""
        union = self._fx_union(fx)
        frm = {}
        for ch in union:
            frm[ch] = (float(self.output[ch])
                       if 0 < ch < len(self.output) else 0.0)
        return {'idx': 0, 'phase': 'fade', 't0': now,
                'from': frm, 'to': self._fx_step_levels(fx, 0, union)}

    def _tick_fx(self, now):
        """Calcula fx_levels (HTP entre FX activos) — corre no tick, sob o
        lock. Lê passos e parâmetros EM VIVO: editar com o efeito a correr
        reflecte-se imediatamente. Devolve True se algo mudou."""
        # rampas dos FX lançados pela sequência ("acompanha o fade"):
        # a escala sobe 0→1 com o fade in da memória que liga o FX e
        # desce 1→0 com o fade out da que o desliga (desliga no fim)
        for i in range(len(self.fx)):
            rmp = self._fx_ramp[i]
            if not rmp:
                continue
            # v6.3.3 — rampa pode ter t0 no FUTURO (atraso da PARTE que
            # lançou o FX): antes de t0 fica no valor de partida
            if now < rmp['t0']:
                k = 0.0
            elif rmp['dur'] <= 0.0:
                k = 1.0
            else:
                k = min(1.0, (now - rmp['t0']) / rmp['dur'])
            self._fx_scale[i] = rmp['de'] + (rmp['para'] - rmp['de']) * k
            if k >= 1.0:
                if rmp.get('desligar'):
                    self.fx_active[i] = False
                    self._fx_run[i] = None
                self._fx_scale[i] = 1.0
                self._fx_ramp[i] = None

        new = {}
        for i, fx in enumerate(self.fx):
            if not (self.fx_active[i] and fx):
                continue
            if fx.get('mode') == 'manual':
                self._fx_tick_manual(i, fx, now, new)
            else:
                self._fx_tick_din(i, fx, now, new)
        changed = (new != self.fx_levels)
        self.fx_levels = new
        return changed

    # ── FX lançados pela sequência (v5 etapa 4 — coluna FX da cuelist) ──
    def fx_apply_tracking(self, idx, snap=False):
        """Alinha o estado dos FX com o TRACKING da posição idx da lista:
        um FX está activo se houver um número ÍMPAR de marcas dele nas
        memórias até idx (inclusive). Assim o RECUA e o «Ir Para» dão
        sempre o estado certo, como nas consolas grandes.

        snap=True (navegação <<< >>> / Ir Para em edição): aplica a seco.
        snap=False (VAI/RECUA): respeita o modo da última marca — imediato
        ou "acompanha o fade" (rampa com fade_in/fade_out da memória idx)."""
        if not (0 <= idx < len(self.cues)):
            return
        with self._lock:
            desejado = [False] * len(self.fx)
            com_fade = [False] * len(self.fx)
            # v6.3.3 — tempos da PARTE que marcou o FX NA CUE idx (se a
            # marca vier de uma parte): a rampa ∿ usa o atraso+fade DELA
            tempos_parte = {}
            for ci, c in enumerate(self.cues[:idx + 1]):
                if c.get('zero'):
                    continue
                marcas = []
                ln = c.get('fx_link')
                if isinstance(ln, dict):
                    marcas.append((ln, None))
                for pk in sorted((c.get('parts') or {}), key=int):
                    p = c['parts'][pk]                       # v6.3.3
                    if isinstance(p.get('fx'), dict):
                        marcas.append((p['fx'], p))
                # v6.3.3 — rede de segurança: UM FX só conta UMA marca
                # por memória (a última: a parte ganha à coluna; entre
                # partes, a de nº maior). Duplicados vindos de ficheiros
                # antigos deixavam ordens contraditórias no mesmo GO.
                por_fx = {}
                for ln, p in marcas:
                    try:
                        n = int(ln.get('num', 0)) - 1
                    except (TypeError, ValueError):
                        continue
                    if 0 <= n < len(self.fx):
                        por_fx[n] = (ln, p)
                for n, (ln, p) in por_fx.items():
                    desejado[n] = not desejado[n]
                    com_fade[n] = bool(ln.get('fade'))
                    tempos_parte[n] = p if ci == idx else None
            cue = self.cues[idx]
            legacy = float(cue.get('fade', 0) or 0)
            f_in = float(cue.get('fade_in', legacy) or 0)
            f_out = float(cue.get('fade_out', legacy) or 0)
            agora = time.time()
            for i in range(len(self.fx)):
                if desejado[i] == self.fx_active[i]:
                    # já está como deve — mas cancela rampa de desligar
                    # pendente se o tracking volta a querer este FX aceso
                    if (desejado[i] and self._fx_ramp[i]
                            and self._fx_ramp[i].get('desligar')):
                        self._fx_ramp[i] = None
                        self._fx_scale[i] = 1.0
                    continue
                # v6.3.3 — se a marca desta cue veio de uma PARTE, o ∿
                # respeita os tempos (atraso+fade) dessa parte
                pt = tempos_parte.get(i)
                if desejado[i]:
                    if self.fx[i] is None:
                        continue            # marca para FX vazio: ignora
                    fi = float(pt.get('fade_in', f_in)) if pt else f_in
                    di = float(pt.get('delay_in', 0)) if pt else 0.0
                    self.fx_active[i] = True
                    self._fx_run[i] = None
                    if snap or not com_fade[i] or (fi <= 0 and di <= 0):
                        self._fx_scale[i] = 1.0
                        self._fx_ramp[i] = None
                    else:
                        self._fx_scale[i] = 0.0
                        self._fx_ramp[i] = {'de': 0.0, 'para': 1.0,
                                            't0': agora + di, 'dur': fi}
                else:
                    fo = float(pt.get('fade_out', f_out)) if pt else f_out
                    do = float(pt.get('delay_out', 0)) if pt else 0.0
                    if snap or not com_fade[i] or (fo <= 0 and do <= 0):
                        self.fx_active[i] = False
                        self._fx_run[i] = None
                        self._fx_scale[i] = 1.0
                        self._fx_ramp[i] = None
                    else:
                        # continua activo enquanto desce; desliga no fim
                        self._fx_ramp[i] = {'de': self._fx_scale[i],
                                            'para': 0.0, 't0': agora + do,
                                            'dur': fo, 'desligar': True}
        if self.on_change:
            self.on_change()

    def _fx_tick_manual(self, i, fx, now, new):
        """Loop manual: fade → hold(auto) → passo seguinte, em ciclo."""
        steps = fx.get('steps') or []
        if not steps:
            return                          # FX sem passos não emite nada
        run = self._fx_run[i]
        if run is None:                     # arranque (ou passos criados)
            run = self._fx_run[i] = self._fx_start_run(i, fx, now)
        run['idx'] %= len(steps)            # passos apagados em edição
        st = steps[run['idx']]
        fade = self._fx_clamp_t(st.get('fade', 1.0))
        auto = self._fx_clamp_t(st.get('auto', 1.0))
        t = now - run['t0']
        if run['phase'] == 'fade':
            # fade 0 = corte seco (sem divisão por zero)
            k = 1.0 if fade <= 0.0 else min(1.0, t / fade)
            cur = {}
            frm = run['from']
            for ch, tv in run['to'].items():
                fv = frm.get(ch, 0.0)
                cur[ch] = fv + (tv - fv) * k
            if k >= 1.0:
                run['phase'] = 'hold'
                run['t0'] = now
        else:                               # hold → espera o tempo auto
            cur = {ch: float(v) for ch, v in run['to'].items()}
            if t >= auto:
                union = self._fx_union(fx)
                nxt = (run['idx'] + 1) % len(steps)
                run['from'] = {ch: cur.get(ch, 0.0) for ch in union}
                run['to'] = self._fx_step_levels(fx, nxt, union)
                run['idx'] = nxt
                run['phase'] = 'fade'
                run['t0'] = now
        # HTP entre FX: prevalece o valor mais alto (decisão do autor).
        # A escala (FX lançado pela sequência em fade) aplica-se aqui.
        esc = self._fx_scale[i]
        for ch, v in cur.items():
            if not (1 <= ch <= NUM_CHANNELS):
                continue
            v = max(0.0, min(255.0, v * esc))
            if v > new.get(ch, -1.0):
                new[ch] = v

    # ── FX dinâmico (v5 etapa 2) ──────────────
    @staticmethod
    def _fx_wave(q, curva, atq, ret):
        """Forma do IMPULSO dentro da janela acesa (carroagem).
        q = posição na janela (0..1) → 0.0..1.0. Fora da janela o canal
        está a 0 (o corte é feito no _fx_tick_din pela carroagem).

        sino: impulso completo 0→1→0; ataque/retirada (0-10) repartem a
              janela — 0 = sobe/desce depressa, 10 = devagar
              (5/5 = simétrico; 0/10 ≈ dente de serra).
        PWM:  aceso a 1 durante a janela, com rampas nos flancos —
              ataque/retirada = fracção da janela em rampa; 0 = flanco
              seco ("pode ou não fazer fade", espec. do autor), 10 =
              rampa ocupa meia janela (10/10 = triângulo)."""
        atq = max(0.0, min(10.0, float(atq)))
        ret = max(0.0, min(10.0, float(ret)))
        if curva in ('pwm', 'quadrada'):    # 'quadrada' = sinónimo antigo
            a = (atq / 10.0) * 0.5          # rampa de subida (máx. ½ janela)
            r = (ret / 10.0) * 0.5          # rampa de descida
            if a > 0.0 and q < a:
                return q / a
            if r > 0.0 and q > 1.0 - r:
                return (1.0 - q) / r
            return 1.0
        # sino assimétrico: pesos de subida/descida conforme as velocidades
        rise = 0.5 + atq
        fall = 0.5 + ret
        rf = rise / (rise + fall)
        if q < rf:
            return (1.0 - math.cos(math.pi * q / rf)) / 2.0
        return (1.0 + math.cos(math.pi * (q - rf) / (1.0 - rf))) / 2.0

    def _fx_tick_din(self, i, fx, now, new):
        """FX dinâmico (etapas 2+3): o RITMO comanda o ciclo — cada figura
        do compasso é UM varrimento completo com duração proporcional ao
        valor da figura (♩ = 1 batida do BPM); pausa = escuro. O ritmo 1
        (♩♩♩♩) reproduz o ciclo contínuo clássico. CARROAGEM = fracção da
        janela acesa; dentro dela:
        value = base × (v_baixo + (v_alto−v_baixo) × impulso) / 100."""
        chans = fx.get('channels') or []
        if not chans:
            return
        run = self._fx_run[i]
        if run is None:
            run = self._fx_run[i] = {'phase': 0.0, 'last': now, 'rj': {}}
        try:
            bpm = max(0.5, min(600.0, float(fx.get('bpm', 60))))
        except (TypeError, ValueError):
            bpm = 60.0
        # fase acumulada (módulo 2 p/ baloiço) — BPM muda em vivo sem saltar.
        # NOTA: o RITMO foi RETIRADO a pedido do autor (2026-06-12) — a
        # primeira abordagem não era o que ele imaginava; redesenhar em
        # conjunto mais tarde. A tabela FX_RITMOS fica no código, inactiva.
        run['phase'] = (run['phase'] + (now - run['last']) * bpm / 60.0) % 2.0
        run['last'] = now

        # direcção do varrimento: '>' esq→dta · '<' dta→esq · '<>' baloiço
        dirc = fx.get('direccao', '>')
        ph = run['phase']
        sweep = ph % 1.0
        travel = 0.0

        curva = fx.get('curva', 'sino')
        atq = fx.get('ataque', 5)
        ret = fx.get('retirada', 5)
        try:
            duty = max(1.0, min(99.0,
                                float(fx.get('carroagem', 50)))) / 100.0
        except (TypeError, ValueError):
            duty = 0.5
        try:
            v_hi = max(0.0, min(100.0, float(fx.get('v_alto', 100))))
        except (TypeError, ValueError):
            v_hi = 100.0
        try:
            v_lo = max(0.0, min(100.0, float(fx.get('v_baixo', 0))))
        except (TypeError, ValueError):
            v_lo = 0.0
        try:
            G = max(0, min(24, int(fx.get('grupos', 0))))
        except (TypeError, ValueError):
            G = 0
        # v6.2 — modo CAOS EXPLÍCITO (mode=='caos'). Dois sub-comportamentos
        # decididos pela QUANTIDADE:
        #   · quant_max > 0  → SELECÇÃO: sorteia k canais (entre mín e máx).
        #   · quant 0/0      → CINTILAÇÃO: o random fica livre sobre a banda
        #                      da Carroagem (recupera o efeito antigo).
        # No DINÂMICO não há caos/random; no CAOS não há blocos/grupos.
        is_caos = fx.get('mode') == 'caos'
        qmin = qmax = 0
        if is_caos:
            # v6.2 — o «Caos» fundiu carroagem + random num único cursor: o
            # GRAU de desordem é FIXO (~0.55, a zona que dá boa cintilação) e
            # o cursor «Caos» controla a CARROAGEM = % de canais envolvidos.
            rnd_amt = 0.55
            try:
                qmin = int(float(fx.get('quant_min', 1)))
            except (TypeError, ValueError):
                qmin = 1
            try:
                qmax = int(float(fx.get('quant_max', 3)))
            except (TypeError, ValueError):
                qmax = 3
            G = 0                       # caos não usa grupos
        else:
            rnd_amt = 0.0
        caos_sel = is_caos and qmax > 0     # selecção só com quantidade

        levels = fx.get('levels', {})
        n = len(chans)

        # posições no varrimento + largura efectiva da janela (duty_eff).
        # pos_of = POSIÇÃO inteira de cada canal (o caos trabalha por
        # posição: os canais da mesma posição picam JUNTOS).
        #
        # CARROAGEM (sem blocos, grupos=0): UMA banda única de tamanho
        #   variável (=carroagem) a percorrer todos os canais, 1 a 1.
        #   carroagem=1 → 1 canal de cada vez; grande → quase todos.
        # GRUPOS (sem blocos, G>=2): conjuntos round-robin em CROSSFADE —
        #   o grupo seguinte acende ENQUANTO o anterior apaga; a carroagem
        #   regula a sobreposição (50=crossfade pleno no sino; 25=seco).
        #
        # BLOCOS (padrão A/B/C) — CORRIGIDO pelo autor 2026-06-13. Um bloco
        #   é como a carroagem mas a unidade VIAJANTE é composta e fixa:
        #   AABB = unidade de 4 canais com 2 tempos (AA depois BB) que
        #   percorre TODOS os canais 4 a 4. As suas células viajam uma de
        #   cada vez. A carroagem fica BLOQUEADA (cada célula = 1 slot).
        #     · grupos=0  → as células percorrem todos os canais em
        #                   sequência: AABB/12 → {1,2}{3,4}{5,6}…{11,12}
        #     · grupos=1  → todos os canais alternam A↔B↔C (pertença):
        #                   AABB/12 → {1,2,5,6,9,10} ↔ {3,4,7,8,11,12}
        #     · grupos>=2 → (PROVISÓRIO, a confirmar) as instâncias do
        #                   bloco dobram-se em G fluxos
        pat, M = ((None, 0) if is_caos
                  else self._fx_parse_blocos(fx.get('blocos', '')))
        if pat and M >= 2:
            L = len(pat)
            letra = [pat[idx % L] for idx in range(n)]   # letra de cada canal
            if G <= 0:
                # células viajam: índice da "corrida" (run) na sequência
                pos_of = []
                c = 0
                for idx in range(n):
                    if idx > 0 and letra[idx] != letra[idx - 1]:
                        c += 1
                    pos_of.append(c)
                npos = (pos_of[-1] + 1) if pos_of else 1
            elif G == 1:
                pos_of = letra                # pertença por letra (alterna)
                npos = M
            else:
                inst = [idx // L for idx in range(n)]      # instância do bloco
                pos_of = [(inst[idx] % G) * M + letra[idx] for idx in range(n)]
                npos = (max(pos_of) + 1) if pos_of else 1
            duty_eff = 1.0 / npos             # carroagem bloqueada nos blocos
        elif G == 0:
            npos = n
            pos_of = list(range(n))
            duty_eff = duty
        elif G == 1:
            npos = 1
            pos_of = [0] * n
            duty_eff = duty
        else:
            # GRUPOS (sem blocos): G conjuntos round-robin a percorrer o
            # ciclo. CORRIGIDO 2026-06-13 — a fórmula antiga (duty*4/G)
            # tinha um tecto que deixava SEMPRE ~2 grupos acesos qualquer
            # que fosse G (punha-se 6 e viam-se 2). Agora a janela encolhe
            # com G, por isso 6 grupos = 6 blocos distintos a passar.
            # nº de grupos acesos ao mesmo tempo ≈ carroagem/50:
            #   carroagem 50 (defeito) → ~1 grupo de cada vez (distintos)
            #   carroagem 100 → ~2 grupos (crossfade/sobreposição)
            #   carroagem 25 → ~½ grupo (separados, com folga)
            npos = G
            pos_of = [idx % G for idx in range(n)]
            duty_eff = min(1.0, duty * 2.0 / G)
        # v6.2 — CRUZAMENTO (0-100): alarga a janela para os blocos/bandas
        # VIZINHOS se sobreporem (a subida de um cruza com a descida do outro).
        # Factor da janela: 0→×1 (sequencial), 50→×2 (vizinho a cruzar),
        # 100→×3 — com 3 blocos (AAAABBBBCCCC) dá onda contínua: enquanto B
        # está no pico, A desce e C sobe. Aplica-se a blocos/carroagem/grupos;
        # o CAOS fica de fora (caos_sel ignora a janela).
        try:
            cross = max(0.0, min(100.0, float(fx.get('cruzamento', 0)))) / 100.0
        except (TypeError, ValueError):
            cross = 0.0
        if cross > 0.0 and not caos_sel and not is_caos:
            duty_eff = min(1.0, duty_eff * (1.0 + 2.0 * cross))
        off_max = (npos - 1.0) / npos if npos > 1 else 0.0
        offs = [(pp / float(npos) if npos > 1 else 0.0) for pp in pos_of]

        # baloiço: posição LINEAR, SEM wrap (correcções do autor): a banda
        # SAI pelo extremo (tudo apagado um instante) e volta pelo mesmo
        # lado; folga de UM SLOT em ambos os extremos.
        if dirc == '<>':
            slot = (1.0 / npos) if npos > 1 else duty_eff
            tri = ph if ph < 1.0 else 2.0 - ph      # triângulo 0→1→0
            travel = -slot + tri * (off_max + duty_eff + 2.0 * slot)

        # CAOS — relógio GLOBAL da combinação (espec. do autor 2026-06-17).
        # A caixa 'caos_rep' diz quantas batidas seguidas se mantém a MESMA
        # combinação aleatória antes de sortear outra; 1 = muda sempre. Aqui
        # só decidimos QUANDO renovar (esvaziar run['rj']); o sorteio em si é
        # lazy, por posição, mais abaixo. Todas as posições mudam JUNTAS.
        if rnd_amt > 0.0 or caos_sel:
            rep_pat = self._fx_parse_caos_rep(fx.get('caos_rep', ''))
            if now >= run.get('caos_next', 0.0):
                if run.get('caos_left', 0) > 1:
                    run['caos_left'] -= 1                 # mantém (repete)
                else:
                    run['rj'] = {}                        # nova combinação
                    if caos_sel and n > 0:
                        # v6.2 — QUANTIDADE: o nº de canais sorteados é um
                        # valor aleatório entre quant_min e quant_max (limitado
                        # aos canais seleccionados). min=max = fixo.
                        a = max(0, min(n, qmin))
                        b = max(0, min(n, qmax))
                        if a > b:
                            a, b = b, a
                        k = random.randint(a, b)
                        run['caos_pick'] = (set(random.sample(range(n), k))
                                            if k > 0 else set())
                    pi = run.get('caos_pi', 0)
                    run['caos_left'] = rep_pat[pi % len(rep_pat)]
                    run['caos_pi'] = pi + 1
                run['caos_next'] = now + 60.0 / bpm

        for idx, ch in enumerate(chans):
            try:
                ch = int(ch)
            except (TypeError, ValueError):
                continue
            if not (1 <= ch <= NUM_CHANNELS):
                continue
            # MODO SELECÇÃO (caos_size>0): a carroagem/posição/direcção são
            # ignoradas. Só os canais sorteados (caos_pick) piscam, em
            # uníssono, 1 flash por batida (curva sino/PWM); os restantes
            # ficam no v_baixo. O Repetidor mantém a selecção N flashes.
            if caos_sel:
                if idx in run.get('caos_pick', ()):
                    # FLASH NÍTIDO: aceso na 1.ª metade da batida (com a
                    # curva), APAGADO na 2.ª — assim VÊ-SE acender e apagar a
                    # cada batida; mantido N batidas = N flashes (a velocidade
                    # é o BPM). Sem isto, com PWM ficava sempre aceso.
                    if sweep < 0.5:
                        w = self._fx_wave(sweep / 0.5, curva, atq, ret)
                    else:
                        w = 0.0
                else:
                    w = 0.0
                pct = v_lo + (v_hi - v_lo) * w
                try:
                    base = float(levels.get(str(ch), levels.get(ch, 255)))
                except (TypeError, ValueError):
                    base = 255.0
                v = max(0.0, min(255.0,
                                 base * (pct / 100.0) * self._fx_scale[i]))
                if v > new.get(ch, -1.0):
                    new[ch] = v
                continue
            off = offs[idx]
            # random (correcções do autor 2026-06-12, 3.ª iteração):
            #   · NUNCA toca no NÍVEL — se o v_alto é 100, acende a 100;
            #     o aleatório vive no INSTANTE do flash, na DURAÇÃO e em
            #     QUEM acende
            #   · trabalha por POSIÇÃO — os canais do mesmo grupo/bloco
            #     picam JUNTOS (1 grupo + random = o grupo todo pisca)
            #   · 0→50: instante de disparo aleatório (a direcção morre
            #     aos 50) + DURAÇÃO do flash aleatória (flashes longos e
            #     curtos misturados)
            #   · 50→100: cada posição pode FALHAR ciclos ao acaso (até
            #     ~2/3 aos 100) — imprevisível o que acende, e o mesmo
            #     canal pode repetir-se de seguida enquanto outros falham
            janela = duty_eff
            saltar = False
            if rnd_amt > 0.0:
                pos = pos_of[idx]
                w_dir = min(1.0, 2.0 * rnd_amt)        # mata a direcção
                w_dur = min(1.0, 2.0 * rnd_amt)        # duração aleatória
                w_skip = max(0.0, 2.0 * rnd_amt - 1.0)  # falhar ciclos
                ent = run['rj'].get(pos)
                if ent is None:
                    # combinação nova só quando o relógio global esvaziou o rj;
                    # entre renovações o ent persiste → a mesma combinação
                    # repete-se batida a batida (o nº de batidas = caos_rep)
                    ent = {'off': (random.random()
                                   if random.random() < w_dir else None),
                           'dur': random.random(),
                           'on': random.random() >= w_skip * 0.65}
                    run['rj'][pos] = ent
                if ent['off'] is not None:
                    # instante aleatório — no baloiço fica dentro do
                    # percurso real das posições
                    off = ent['off'] * (off_max if dirc == '<>' else 1.0)
                janela = max(0.02, duty_eff
                             * (1.0 - w_dur * ent['dur'] * 0.85))
                saltar = not ent.get('on', True)
            # posição do canal face à janela acesa (duty_eff):
            #   '>' / '<' : chase circular (com wrap), sentido normal/inverso
            #   '<>'      : baloiço linear — distância à cabeça da banda,
            #               sem wrap; fora de [0, duty_eff) está apagado
            if saltar:
                p = None                     # random: este ciclo falha
            elif dirc == '<>':
                p = travel - off
                if not (0.0 <= p < janela):
                    p = None
            elif dirc == '<':
                p = (sweep + off) % 1.0
                if p >= janela:
                    p = None
            else:
                p = (sweep - off) % 1.0
                if p >= janela:
                    p = None
            # dentro da janela o canal vive o impulso (até ao v_alto —
            # o random NÃO baixa o nível); fora fica no v_baixo
            w = (self._fx_wave(p / janela, curva, atq, ret)
                 if p is not None else 0.0)
            pct = v_lo + (v_hi - v_lo) * w
            # base por defeito 255: a compra já não exige níveis — o nível
            # do efeito é definido por v_alto/v_baixo (espec. do autor)
            try:
                base = float(levels.get(str(ch), levels.get(ch, 255)))
            except (TypeError, ValueError):
                base = 255.0
            # a escala (FX lançado pela sequência em fade) aplica-se aqui
            v = base * (pct / 100.0) * self._fx_scale[i]
            v = max(0.0, min(255.0, v))
            if v > new.get(ch, -1.0):
                new[ch] = v

    @staticmethod
    def _fx_parse_blocos(txt):
        """'AAABB' → ([0,0,0,1,1], 2): padrão de PERTENÇA dos canais aos
        blocos A/B/C + nº de blocos distintos.

        Semântica CORRIGIDA pelo autor (2026-06-12): os blocos NÃO são
        janelas consecutivas — são CONJUNTOS de canais que vivem
        ALTERNADAMENTE. O padrão repete-se pela selecção: 10 canais com
        AAABB → bloco A = {1,2,3,6,7,8}, bloco B = {4,5,9,10}; primeiro
        acende o A, depois o B, vezes sem conta. Com blocos activos a
        carroagem fica BLOQUEADA (cada bloco ocupa 1/M do ciclo).
        Inválido/vazio → (None, 0) — usam-se os grupos."""
        s = str(txt or '').strip().upper()
        if not s or any(c not in 'ABC' for c in s):
            return None, 0
        letras = sorted(set(s))
        mapa = {c: i for i, c in enumerate(letras)}
        return [mapa[c] for c in s], len(letras)

    @staticmethod
    def _fx_parse_caos_rep(txt):
        """'1 4' → [1, 4]: nº de batidas seguidas que cada combinação
        aleatória do caos se mantém antes de mudar. Números separados por
        espaços/vírgulas; 0 conta como 1; vazio/inválido → [1] (muda
        sempre). O padrão cicla (espec. do autor 2026-06-17)."""
        out = []
        for tok in re.split(r'[\s,]+', str(txt or '').strip()):
            if not tok:
                continue
            try:
                out.append(max(1, int(tok)))
            except ValueError:
                continue
        return out or [1]

    # ── DMX / sACN ────────────────────────────
    @staticmethod
    def _norm_universes(seq):
        """Normaliza uma lista de universos: inteiros >=1, sem repetidos,
        máximo 4, pela ordem dada. Garante pelo menos um universo ([1])."""
        out = []
        for x in seq:
            try:
                u = int(x)
            except (TypeError, ValueError):
                continue
            if u < 1 or u > 63999:
                continue
            if u not in out:
                out.append(u)
            if len(out) >= 4:
                break
        return out or [1]

    # v4 — tecto de segurança do modo automático (contra gralhas no
    # renumerador que criariam dezenas de universos de saída)
    AUTO_UNIVERSES_MAX = 16

    def out_universes(self):
        """Lista EFECTIVA de universos de saída (comum a sACN e Art-Net).

        Modo automático (default): derivada do renumerador — o que se
        patcha é o que sai. Sem patch nenhum, emite U1 (heartbeat).
        Modo manual: a lista sacn_universes (até 4, das Configurações)."""
        if not self.universes_auto:
            return list(self.sacn_universes)
        univs = sorted(self.patch.universes_used())
        if not univs:
            return [1]
        return univs[:self.AUTO_UNIVERSES_MAX]

    def sync_sacn_outputs(self):
        """v4 — alinha os universos activos do sender sACN com a lista de
        saída efectiva. Chamar depois de o renumerador mudar (modo auto):
        desactiva universos que saíram do patch e activa os novos com o
        destination/multicast correctos."""
        if not (self.sacn_sender and self.sacn_enabled):
            return
        with self._lock:
            want = set(self.out_universes())
            try:
                active = set(self.sacn_sender.get_active_outputs())
            except Exception:
                return
            for u in active - want:
                try:
                    self.sacn_sender.deactivate_output(u)
                except Exception:
                    pass
            for u in want - active:
                try:
                    self.sacn_sender.activate_output(u)
                    out = self.sacn_sender[u]
                    if self.sacn_unicast_ip:
                        out.destination = self.sacn_unicast_ip
                    out.multicast = self.sacn_multicast
                    if u not in self.universes:
                        self.universes[u] = bytearray(512)
                except Exception:
                    pass

    def _flush_dmx(self):
        # reset buffers (v4: slice-assign — muito mais rápido que loop python)
        for buf in self.universes.values():
            buf[:] = self._zero512

        # faders dos submasters (fracção 0.0-1.0 + níveis guardados)
        subs = [(sm['fader'] / 100.0, sm['levels']) for sm in self.submasters]

        # v5 — Highlight/Solo: calcula uma vez por flush (selecção da app)
        hs_set = self.hs_channels
        hs = (self.highlight or self.solo) and bool(hs_set)
        # v6.2 — Solo POR ALIAS (alcunha): seleccionar QUALQUER atributo de um
        # aparelho (ex.: ZOOM, 0-255) deve manter aceso o dimmer (pct) do MESMO
        # alias — senão o solo apagava o próprio aparelho que se quer ver. Aqui
        # juntam-se as alcunhas (>0) da selecção; os canais pct dessas alcunhas
        # NÃO são apagados (mantêm o nível programado, decisão do utilizador).
        solo_aliases = frozenset()
        if self.solo and hs_set:
            solo_aliases = frozenset(
                a for a in (int(self.patch.get(c).get('alcunha') or 0)
                            for c in hs_set) if a)

        for ch in range(1, NUM_CHANNELS + 1):
            e = self.patch.get(ch)
            addrs = e.get('addrs', [])
            if not addrs:
                continue
            univ = e.get('universe', 1)
            if univ not in self.universes:
                self.universes[univ] = bytearray(512)
            buf = self.universes[univ]

            lvl = max(0.0, min(255.0, float(self.output[ch])))
            # v5: FX por cima do playback em HTP — o nível mais alto
            # prevalece (correcção do autor 2026-06-13). Assim, quando um FX
            # em fade-out e um canal da memória se sobrepõem, o canal desce
            # SUAVEMENTE do FX até ao nível da memória sem saltar quando o
            # FX desaparece. O programador (azul) continua a mandar no canal.
            if self.fx_levels and self.programmer[ch] is None:
                fxv = self.fx_levels.get(ch)
                if fxv is not None and fxv > lvl:
                    lvl = float(fxv)
            # submasters — mistura HTP (o nível mais alto prevalece)
            for fv, levs in subs:
                if fv > 0.0:
                    sl = levs.get(str(ch))
                    if sl is not None:
                        c = sl * fv
                        if c > lvl:
                            lvl = c
            # v5 — Highlight / Solo (modos de visualização, sobre TUDO):
            #   Highlight: a selecção vai a 255 (full), para a veres.
            #   Solo: só a selecção fica acesa; os OUTROS canais DIMMER
            #   (display='pct') vão a 0. Canais não-dimmer não são afectados.
            if hs:
                in_sel = ch in hs_set
                if self.highlight and in_sel:
                    lvl = float(self.highlight_level)   # v6.2: nivel ajustavel
                if (self.solo and not in_sel
                        and e.get('display', 'pct') == 'pct'
                        and (int(e.get('alcunha') or 0) not in solo_aliases)):
                    lvl = 0.0
            if e.get('bit16'):
                # 16 bit: course = byte alto, fine = byte baixo
                # curvas nao se aplicam em 16 bit (resolucao alta da resposta)
                val16 = int(round(lvl / 255.0 * 65535))
                coarse, fine = (val16 >> 8) & 0xFF, val16 & 0xFF
                fines = e.get('fine') or []
                for i, a in enumerate(addrs):
                    if 1 <= a <= 512:
                        buf[a - 1] = coarse
                    fa = fines[i] if i < len(fines) else a + 1
                    if 1 <= fa <= 512:
                        buf[fa - 1] = fine
            else:
                # 8 bit: aplica a curva configurada no patch
                curva = e.get('curva', CURVE_LINEAR)
                if   curva == CURVE_LIGADO:  v = 255              # sempre 100 %
                elif curva == CURVE_RELE:    v = 0 if lvl < 10 else 255
                else:                        v = int(round(lvl))  # linear
                for a in addrs:
                    if 1 <= a <= 512:
                        buf[a - 1] = v

        # B.O. — zera todos os buffers DMX (sem tocar no estado interno)
        if self.bo_active:
            for buf in self.universes.values():
                buf[:] = self._zero512

        # v6 — teste de saída DMX (Highlight/Solo na vista DMX): SOLO zera
        # tudo no universo excepto os endereços forçados; FORCE põe esses ao
        # nível do Highlight (v6.2: ajustável pela consola; 255 por defeito)
        # para identificar a fixtura no palco. Por cima de tudo, mesmo B.O.
        if self.dmx_solo and self.dmx_solo_univ is not None:
            buf = self.universes.get(self.dmx_solo_univ)
            if buf is not None:
                buf[:] = self._zero512
        if self.dmx_force:
            hlv = max(0, min(255, int(self.highlight_level)))
            for u, a in self.dmx_force:
                if not (1 <= a <= 512):
                    continue
                buf = self.universes.get(u)
                if buf is None:
                    buf = self.universes[u] = bytearray(512)
                buf[a - 1] = hlv

        # v4: lista efectiva (auto = derivada do renumerador) calculada uma
        # vez por flush e partilhada pelas duas saídas
        out_univs = self.out_universes()

        if self.sacn_sender and self.sacn_enabled:
            for univ in out_univs:
                buf = self.universes.get(univ)
                if buf is None:
                    buf = self.universes[univ] = bytearray(512)
                try:
                    out = self.sacn_sender[univ]
                    if out is None:
                        # universo apareceu depois de ligar o sACN → activa-o
                        self.sacn_sender.activate_output(univ)
                        out = self.sacn_sender[univ]
                        # destination ANTES de configurar multicast (igual ao start_sacn)
                        if self.sacn_unicast_ip:
                            out.destination = self.sacn_unicast_ip
                        out.multicast = self.sacn_multicast
                    out.dmx_data = tuple(buf)
                except Exception:
                    pass

        # v4 — Art-Net em paralelo: envia os MESMOS universos de saída.
        # ~25 pacotes/s por universo (limite da spec: 44 Hz) — dentro do limite.
        if self.artnet_sender and self.artnet_enabled:
            for univ in out_univs:
                buf = self.universes.get(univ)
                if buf is None:
                    buf = self.universes[univ] = bytearray(512)
                try:
                    self.artnet_sender.send(univ, buf)
                except Exception:
                    pass

    def start_sacn(self, universes=None, multicast=True,
                   unicast_ip="192.168.1.10", bind_ip=""):
        """v3 — activa uma LISTA de até 4 universos sACN ARBITRÁRIOS:
            universes       = lista de universos (ex: [1, 7, 9, 10]); None mantém
                              os actuais
            multicast       = True (multicast) ou False (unicast p/ unicast_ip)
            bind_ip         = IP da interface local (''/None = 0.0.0.0 = qualquer)"""
        if not HAS_SACN:
            return False, "Pacote 'sacn' não instalado."
        try:
            # 1) Para totalmente o sender antigo e esperar libertar o socket
            if self.sacn_sender:
                try: self.sacn_sender.stop()
                except Exception: pass
                self.sacn_sender = None
                time.sleep(0.15)

            # 2) Aplica os parametros no estado interno
            if universes is not None:
                self.sacn_universes = self._norm_universes(universes)
            self.sacn_multicast = bool(multicast)
            self.sacn_unicast_ip = unicast_ip or ""
            self.sacn_bind_ip = bind_ip or ""

            bind = self.sacn_bind_ip if self.sacn_bind_ip else "0.0.0.0"
            # v4: lista efectiva — em modo auto vem do renumerador
            univs = list(self.out_universes())
            print(f'[sACN] start: multicast={self.sacn_multicast} '
                  f'unicast_ip="{self.sacn_unicast_ip}" bind="{bind}" '
                  f'universos={univs} auto={self.universes_auto}')

            # 3) Cria sender novo e arranca
            self.sacn_sender = sacn.sACNsender(bind_address=bind,
                                               source_name=SACN_SOURCE_NAME)
            self.sacn_sender.start()

            # 4) Activa os universos efectivos (a ordem aqui importa)
            for u in univs:
                self.sacn_sender.activate_output(u)
                out = self.sacn_sender[u]
                # destination PRIMEIRO (necessario antes de desligar multicast);
                # depois liga/desliga o multicast.
                if self.sacn_unicast_ip:
                    out.destination = self.sacn_unicast_ip
                out.multicast = self.sacn_multicast
                if u not in self.universes:
                    self.universes[u] = bytearray(512)

            self.sacn_enabled = True
            mode = 'Multicast' if self.sacn_multicast else f'Unicast→{self.sacn_unicast_ip}'
            lst = ', '.join('U' + str(u) for u in univs)
            origem = 'automáticos (renumerador)' if self.universes_auto \
                     else 'manuais'
            msg = (f"sACN activo — {len(univs)} universo(s) {origem}: {lst}\n"
                   f"Modo: {mode}\nBind: {bind}")
            if self.universes_auto and len(univs) > 8 and self.sacn_multicast:
                msg += ("\n\n⚠ Muitos universos em multicast — se a rede de "
                        "luz tiver WiFi no caminho, pode saturar. Em cabo "
                        "não há problema.")
            return True, msg
        except Exception as e:
            self.sacn_sender = None
            self.sacn_enabled = False
            return False, str(e)

    def stop_sacn(self):
        if self.sacn_sender:
            try:
                self.sacn_sender.stop()
            except Exception:
                pass
            self.sacn_sender = None
        self.sacn_enabled = False

    # ── Art-Net (v4) ──────────────────────────
    def start_artnet(self, broadcast=True, dest_ip='', bind_ip=''):
        """Activa a saída Art-Net (em paralelo com o sACN, se este estiver
        ligado). Usa a MESMA lista de universos de saída (sacn_universes).
        Devolve (ok, mensagem)."""
        try:
            with self._lock:
                if self.artnet_sender:
                    self.artnet_sender.stop()
                    self.artnet_sender = None
                self.artnet_broadcast = bool(broadcast)
                self.artnet_dest_ip = (dest_ip or '').strip()
                self.artnet_bind_ip = (bind_ip or '').strip()
                self.artnet_sender = ArtNetSender(
                    bind_ip=self.artnet_bind_ip,
                    dest_ip=self.artnet_dest_ip,
                    broadcast=self.artnet_broadcast)
                self.artnet_enabled = True
            univs = list(self.out_universes())
            lst = ', '.join('U{}→AN{}'.format(u, u - 1) for u in univs)
            mode = ('Broadcast 255.255.255.255' if self.artnet_broadcast
                    else 'Unicast→' + self.artnet_dest_ip)
            bind = self.artnet_bind_ip or 'auto'
            print('[Art-Net] start: {} bind={} universos={}'.format(
                mode, bind, univs))
            origem = ('automáticos (renumerador)' if self.universes_auto
                      else 'manuais')
            msg = ("Art-Net activo — {} universo(s) {}: {}\n"
                   "Modo: {}\nBind: {}\n"
                   "(universo da mesa N = Art-Net N-1)"
                   .format(len(univs), origem, lst, mode, bind))
            if self.universes_auto and len(univs) > 8 and self.artnet_broadcast:
                msg += ("\n\n⚠ Muitos universos em broadcast — se a rede de "
                        "luz tiver WiFi no caminho, pode saturar. Em cabo "
                        "não há problema.")
            return True, msg
        except Exception as e:
            self.artnet_sender = None
            self.artnet_enabled = False
            return False, str(e)

    def stop_artnet(self):
        if self.artnet_sender:
            try:
                self.artnet_sender.stop()
            except Exception:
                pass
            self.artnet_sender = None
        self.artnet_enabled = False

    # ── memória ZERO ──────────────────────────
    @staticmethod
    def _make_zero():
        """Memória ZERO: escuro inicial. Nunca tem valores de canais."""
        return {'num': 'ZERO', 'label': T('cue.zero_label'), 'fade_in': 3.0,
                'fade_out': 3.0, 'delay_in': 0.0, 'delay_out': 0.0,
                'follow': None, 'levels': {}, 'zero': True, 'enabled': True,
                'midi_nota': None, 'midi_direccao': None, 'midi_delay_s': 0.0}

    def _ensure_zero(self):
        """Garante que existe uma memória ZERO em cues[0]."""
        if not self.cues or not self.cues[0].get('zero'):
            self.cues.insert(0, self._make_zero())

    def clear_cues(self):
        """Recomeça com apenas a memória ZERO."""
        self.cues = [self._make_zero()]
        self.current_cue_idx = -1
        self.retratos = [None] * 20
        self.groups = [None] * 20
        self.submasters = self._make_submasters()
        self.fx = [None] * NUM_FX                 # v5
        self.fx_active = [False] * NUM_FX
        self._fx_run = [None] * NUM_FX
        self.fx_levels = {}
        self._fx_scale = [1.0] * NUM_FX
        self._fx_ramp = [None] * NUM_FX
        self._reset_salta()
        self._commit_programmer()
        self._output_to_partida()

    @property
    def zero_enabled(self):
        return bool(self.cues and self.cues[0].get('zero')
                    and self.cues[0].get('enabled'))

    # ── lista de memórias (sequência circular) ─
    def next_index(self, idx):
        """Índice seguinte na sequência circular; salta o ZERO se desactivado."""
        n = len(self.cues)
        if n <= 1:
            return 0 if self.zero_enabled else None
        nxt = idx + 1
        if nxt >= n:
            nxt = 0
        if self.cues[nxt].get('zero') and not self.cues[nxt].get('enabled'):
            nxt = 1
        return nxt

    def _peek_next_index(self):
        """v6.3 — índice da cue que o próximo GO/AUTO vai MESMO executar,
        considerando o SALTAR (loop). Read-only: não altera o estado do
        salto. Espelha a decisão do go() para o _arm_follow ler o AUTO da
        cue que vai ENTRAR (que num loop é o alvo, não a cue seguinte)."""
        cur = self.current_cue_idx
        if 0 <= cur < len(self.cues):
            cue = self.cues[cur]
            tgt = cue.get('salta_target')
            if tgt is not None:
                count = int(cue.get('salta_count', 0) or 0)   # 0 = eterno
                eternal = (count == 0)
                remaining = (self._salta_remaining
                             if self._salta_idx == cur else count)
                if eternal or remaining > 0:
                    tidx = self._find_cue_index(tgt)
                    if tidx is not None:
                        return tidx
        return self.next_index(cur)

    def prev_index(self, idx):
        """Índice anterior na sequência circular; salta o ZERO se desactivado."""
        n = len(self.cues)
        if n <= 1:
            return 0 if self.zero_enabled else None
        prv = idx - 1
        if prv < 0:
            prv = n - 1
        if self.cues[prv].get('zero') and not self.cues[prv].get('enabled'):
            prv = n - 1
        return prv

    # ── SALTAR (loop / jump) ──────────────────
    def _reset_salta(self):
        self._salta_idx = None
        self._salta_remaining = 0

    def _find_cue_index(self, num):
        """Índice da memória com este número (ignora o ZERO)."""
        for i, c in enumerate(self.cues):
            if not c.get('zero') and abs(float(c.get('num', 0)) - num) < 1e-6:
                return i
        return None

    @property
    def active_salta(self):
        """Número (1, 2, …) do SALTAR actualmente activo; 0 se nenhum.
        A ordem segue a posição das memórias-SALTAR na lista."""
        if self._salta_idx is None:
            return 0
        rank = 0
        for i, c in enumerate(self.cues):
            if c.get('salta_target') is not None:
                rank += 1
                if i == self._salta_idx:
                    return rank
        return 0

    def soltar(self):
        """Sai imediatamente do SALTAR activo, lançando a memória seguinte
        à memória que o contém."""
        if self._salta_idx is None:
            return
        idx = self._salta_idx
        self._reset_salta()
        nxt = self.next_index(idx)
        if nxt is not None:
            self._run_cue(nxt)

    def go(self):
        cur = self.current_cue_idx
        # ── SALTAR: se a memória actual tem um salto definido ──
        if 0 <= cur < len(self.cues):
            cue = self.cues[cur]
            tgt = cue.get('salta_target')
            if tgt is not None:
                count = int(cue.get('salta_count', 0) or 0)   # 0 = eterno
                if self._salta_idx != cur:
                    self._salta_idx = cur
                    self._salta_remaining = count
                eternal = (count == 0)
                if eternal or self._salta_remaining > 0:
                    tidx = self._find_cue_index(tgt)
                    if tidx is not None:
                        if not eternal:
                            self._salta_remaining -= 1
                        self._run_cue(tidx)
                        return
                self._salta_idx = None   # saltos esgotados
        # ── avanço normal ──
        nxt = self.next_index(cur)
        if nxt is not None:
            self._run_cue(nxt)

    def back(self):
        self._reset_salta()
        prv = self.prev_index(self.current_cue_idx)
        if prv is not None:
            self._run_cue(prv)

    def goto(self, idx):
        self._reset_salta()
        if 0 <= idx < len(self.cues):
            self._run_cue(idx)

    # ── pausa ─────────────────────────────────
    def pause(self):
        """Congela a transição e o encadeado em curso."""
        if self.paused:
            return
        self.paused = True
        self._pause_fade_elapsed = time.time() - self.fade_time
        self._pause_follow_remaining = self.follow_at - time.time()

    def resume(self):
        """Retoma a transição/encadeado a partir do ponto onde foi congelado."""
        if not self.paused:
            return
        self.paused = False
        now = time.time()
        self.fade_time = now - self._pause_fade_elapsed
        self.follow_at = now + self._pause_follow_remaining

    def toggle_pause(self):
        if self.paused:
            self.resume()
        else:
            self.pause()
        return self.paused

    @property
    def fade_progress(self):
        """Progresso da transição em curso (0.0–1.0). 0.0 se não há transição."""
        if not self.fading:
            return 0.0
        total = self.fade_total          # v6.3.3: inclui as PARTES
        if total <= 0:
            return 1.0
        elapsed = (self._pause_fade_elapsed if self.paused
                   else time.time() - self.fade_time)
        return max(0.0, min(1.0, elapsed / total))

    @property
    def fade_remaining(self):
        """v6.3 — segundos que faltam para a transição terminar (0.0 se não
        há transição)."""
        if not self.fading:
            return 0.0
        total = self.fade_total          # v6.3.3: inclui as PARTES
        elapsed = (self._pause_fade_elapsed if self.paused
                   else time.time() - self.fade_time)
        return max(0.0, total - elapsed)

    @property
    def follow_progress(self):
        """v6.3 — progresso do COUNTDOWN do AUTO (0.0–1.0). 0.0 se não há
        countdown armado ou se a duração é 0."""
        if not self.follow_armed or self.follow_total <= 0:
            return 0.0
        remaining = self.follow_at - time.time()
        return max(0.0, min(1.0, 1.0 - remaining / self.follow_total))

    def _arm_follow(self):
        """Após terminar o fade da cue actual, agenda a ENTRADA AUTOMÁTICA da
        memória SEGUINTE se esta (a que ENTRA) tiver AUTO. v6.3: o AUTO passou
        a pertencer à cue que entra — cue N+1 com AUTO=10 entra 10 s depois de
        a cue N acabar (não é o AUTO da cue anterior)."""
        if not (0 <= self.current_cue_idx < len(self.cues)):
            return
        nxt = self._peek_next_index()   # considera o LOOP (alvo do salto)
        if nxt is None:
            return
        fol = self.cues[nxt].get('follow')
        if fol is not None and fol >= 0:
            self.follow_armed = True
            self.follow_total = float(fol)
            self.follow_at = time.time() + float(fol)

    def _run_cue(self, idx):
        # v4: corre sob o lock — uma transição nunca apanha as listas a meio
        # de um resize/load (a thread do engine adquire o mesmo RLock no tick)
        with self._lock:
            self._run_cue_impl(idx)

    def _run_cue_impl(self, idx):
        cue = self.cues[idx]
        # compatibilidade: shows antigos têm apenas 'fade'
        legacy = float(cue.get('fade', 0))
        fade_in = float(cue.get('fade_in', legacy))
        fade_out = float(cue.get('fade_out', legacy))
        levels = cue.get('levels', {})

        self.fade_start = self.output[:]
        if cue.get('zero'):
            # ZERO → todos os canais para o seu ponto de partida (passivos)
            for ch in range(1, NUM_CHANNELS + 1):
                self.fade_target[ch] = self._partida(ch)
                self.active[ch] = False
                self._update_prog_base(ch, self._partida(ch), False)
        elif self.intensity_mode == 'cue_only':
            self._targets_cue_only(idx, levels)
        else:
            self._targets_tracking(cue, levels)

        self.fade_in = fade_in
        self.fade_out = fade_out
        self.delay_in = float(cue.get('delay_in', 0))
        self.delay_out = float(cue.get('delay_out', 0))
        # v6.3.3 — PARTES: tempos POR CANAL. Cada canal usa os tempos da
        # sua parte (a 1 = os da própria memória); a direcção do movimento
        # (já fixada nos alvos) decide se leva os tempos IN ou OUT. O fim
        # da transição é o movimento mais longo de TODAS as partes.
        parte_de = {}
        for p in (cue.get('parts') or {}).values():
            for pch in p.get('channels', []):
                parte_de[pch] = p
        total = max(self.delay_in + self.fade_in,
                    self.delay_out + self.fade_out)
        for ch in range(1, NUM_CHANNELS + 1):
            p = parte_de.get(ch)
            if p is None:
                f_i, f_o = fade_in, fade_out
                d_i, d_o = self.delay_in, self.delay_out
            else:
                f_i = float(p.get('fade_in', fade_in))
                f_o = float(p.get('fade_out', fade_out))
                d_i = float(p.get('delay_in', 0))
                d_o = float(p.get('delay_out', 0))
            if self.fade_target[ch] >= self.fade_start[ch]:
                self.fade_dur[ch], self.fade_del[ch] = f_i, d_i
            else:
                self.fade_dur[ch], self.fade_del[ch] = f_o, d_o
            if (p is not None
                    and self.fade_target[ch] != self.fade_start[ch]):
                total = max(total, self.fade_del[ch] + self.fade_dur[ch])
        # v6.3.3b — parte com FX ∿ também conta para o fim da transição:
        # a barra acompanha a rampa do FX mesmo sem canais a mover
        # (pedido do autor 2026-07-07)
        for p in (cue.get('parts') or {}).values():
            fx = p.get('fx')
            if isinstance(fx, dict) and fx.get('fade'):
                total = max(total,
                            float(p.get('delay_in', 0))
                            + float(p.get('fade_in', 0)),
                            float(p.get('delay_out', 0))
                            + float(p.get('fade_out', 0)))
        self.fade_total = total
        self.fade_time = time.time()
        self.fading = True
        self.auto_fade = False           # por defeito é manual (VAI/RECUA)
        self.follow_armed = False        # cancela follow pendente
        self.paused = False              # um novo VAI tem prioridade máxima
        self.current_cue_idx = idx
        # v5 etapa 4: alinha os FX com o tracking da coluna FX (modo
        # imediato ou "acompanha o fade" conforme a marca)
        self.fx_apply_tracking(idx, snap=False)
        # NOTA: o VAI não limpa o programador — os canais a azul mantêm-se
        # azuis até serem gravados (memória/retrato) ou libertados.

    # ── alvos da transição (LTP/tracking vs cue-only) ─────────
    def _targets_tracking(self, cue, levels):
        """Modelo ANTIGO (intensity_mode='tracking'): tudo LTP. BARREIRA (block)
        manda os PCT (0-100%) SEM ordem ao defeito/0; os DEC (0-255) mantêm-se
        (LTP). Comportamento da v6.1."""
        is_barreira = bool(cue.get('barreira', False))
        for ch in range(1, NUM_CHANNELS + 1):
            lvl_v = levels.get(str(ch), levels.get(ch))
            if lvl_v is not None:
                self.fade_target[ch] = lvl_v
                self.active[ch] = True
                self._update_prog_base(ch, lvl_v, True)
            elif is_barreira and self.patch.get(ch).get('display', 'pct') == 'pct':
                self.fade_target[ch] = self._partida(ch)
                self.active[ch] = False
                self._update_prog_base(ch, self._partida(ch), False)
            else:
                self.fade_target[ch] = self.output[ch]   # LTP: mantém

    def _targets_cue_only(self, idx, levels):
        """Modelo NOVO (intensity_mode='cue_only'):
          · INTENSIDADES (pct, 0-100%) = CUE-ONLY: só a cue idx manda; pct SEM
            ordem → defeito/0. Cada cue é um look fechado (saltar no guião dá
            sempre o mesmo resultado, independente do caminho).
          · ATRIBUTOS (dec, 0-255) = TRACKING: estado SEGUIDO desde o início até
            idx (re-derivado). BLOCK (barreira) repõe os dec SEM ordem no
            defeito (assertam posição/cor)."""
        dec_val, dec_act = self._track_dec_state(idx)
        for ch in range(1, NUM_CHANNELS + 1):
            if self.patch.get(ch).get('display', 'pct') == 'pct':
                lvl_v = levels.get(str(ch), levels.get(ch))
                if lvl_v is not None:
                    t, a = lvl_v, True
                else:
                    t, a = self._partida(ch), False     # cue-only: sem ordem → defeito
            else:
                t, a = dec_val[ch], dec_act[ch]
            self.fade_target[ch] = t
            self.active[ch] = a
            self._update_prog_base(ch, t, a)

    def _track_dec_state(self, idx):
        """Estado SEGUIDO (tracking) dos canais DEC (0-255) ao chegar à cue idx:
        percorre as cues 0..idx aplicando as ordens dec por ordem; um BLOCK
        (barreira) repõe os dec SEM ordem no defeito. Devolve (val, act)."""
        val, act = {}, {}
        for ch in range(1, NUM_CHANNELS + 1):
            if self.patch.get(ch).get('display', 'pct') != 'pct':   # só dec
                val[ch] = float(self._partida(ch))
                act[ch] = False
        for j in range(0, min(idx, len(self.cues) - 1) + 1):
            c = self.cues[j]
            if c.get('zero'):
                for ch in val:
                    val[ch] = float(self._partida(ch)); act[ch] = False
                continue
            levels = c.get('levels', {})
            is_block = bool(c.get('barreira', False))
            for ch in val:                                  # só dec
                lv = levels.get(str(ch), levels.get(ch))
                if lv is not None:
                    val[ch] = lv; act[ch] = True
                elif is_block:
                    val[ch] = float(self._partida(ch)); act[ch] = False
                # else: mantém (track)
        return val, act

    def _update_prog_base(self, ch, value, active):
        """Mantém actualizado o 'fundo' de um canal que está no programador,
        para o LIBERTAR o repor no estado da memória correcta."""
        if self.programmer[ch] is not None:
            self._prog_base[ch] = value
            self._prog_abase[ch] = active

    def _commit_programmer(self):
        """Os valores do programador deixam de estar 'por gravar'."""
        self.programmer = [None] * (NUM_CHANNELS + 1)
        self._prog_base = [None] * (NUM_CHANNELS + 1)
        self._prog_abase = [None] * (NUM_CHANNELS + 1)

    def record_cue(self, num, label, fade_in, fade_out, follow=None,
                   delay_in=0.0, delay_out=0.0):
        self._reset_salta()
        if self.intensity_mode == 'cue_only':
            # v6.2 cue-only: as INTENSIDADES (pct) gravam o LOOK COMPLETO
            # (playback + programador = self.output; submasters NÃO entram) —
            # grava-se os acesos, os outros ficam off via cue-only. Os
            # ATRIBUTOS (dec) gravam só as MUDANÇAS (programador).
            levels = {}
            for ch in range(1, NUM_CHANNELS + 1):
                if self.patch.get(ch).get('display', 'pct') == 'pct':
                    v = int(round(self.output[ch]))
                    if v > 0:
                        levels[str(ch)] = v
                elif self.programmer[ch] is not None:
                    levels[str(ch)] = int(self.programmer[ch])
        else:
            # tracking (antigo): a memória guarda só as ORDENS (programador)
            levels = {str(ch): int(self.programmer[ch])
                      for ch in range(1, NUM_CHANNELS + 1)
                      if self.programmer[ch] is not None}
        cue = {'num': num, 'label': label,
               'fade_in': fade_in, 'fade_out': fade_out,
               'delay_in': delay_in, 'delay_out': delay_out,
               'follow': follow, 'levels': levels,
               # v6.3 — MIDI (sem MIDI por defeito): direcção None|'in'|'out'.
               'midi_nota': None, 'midi_direccao': None, 'midi_delay_s': 0.0}

        result = None
        for i in range(1, len(self.cues)):   # cues[0] é o ZERO — nunca se toca
            c = self.cues[i]
            if c['num'] == num:
                # v6.3 — regravar por cima preserva o MIDI da cue (é metadado
                # à parte da luz; não se perde ao re-comprar).
                for k in ('midi_nota', 'midi_direccao', 'midi_delay_s'):
                    if k in c:
                        cue[k] = c[k]
                self.cues[i] = cue
                result = i
                break
            if c['num'] > num:
                self.cues.insert(i, cue)
                result = i
                break
        if result is None:
            self.cues.append(cue)
            result = len(self.cues) - 1
        self._commit_programmer()
        return result

    def delete_cue(self, idx):
        if 1 <= idx < len(self.cues):   # o ZERO (idx 0) não se apaga
            self.cues.pop(idx)
            if self.current_cue_idx >= len(self.cues):
                self.current_cue_idx = len(self.cues) - 1
            self._reset_salta()

    def load_cue_for_edit(self, idx):
        """Aplica uma memória na saída — sem transição nem encadeado.
        Filosofia LTP: só mexe nos canais que a memória comanda. O programador
        mantém-se (os canais a azul só saem ao gravar ou libertar)."""
        if not (0 <= idx < len(self.cues)):
            return
        cue = self.cues[idx]
        self.fading = False
        self.follow_armed = False
        self.paused = False
        levels = cue.get('levels', {})
        if cue.get('zero'):
            for ch in range(1, NUM_CHANNELS + 1):
                self.output[ch] = float(self._partida(ch))
                self.active[ch] = False
                self._update_prog_base(ch, self._partida(ch), False)
        elif self.intensity_mode == 'cue_only':
            # mesmo modelo da reprodução, mas A SECO (sem fade)
            dec_val, dec_act = self._track_dec_state(idx)
            for ch in range(1, NUM_CHANNELS + 1):
                if self.patch.get(ch).get('display', 'pct') == 'pct':
                    lvl_v = levels.get(str(ch), levels.get(ch))
                    if lvl_v is not None:
                        v, a = lvl_v, True
                    else:
                        v, a = float(self._partida(ch)), False
                else:
                    v, a = dec_val[ch], dec_act[ch]
                self.output[ch] = v
                self.active[ch] = a
                self._update_prog_base(ch, v, a)
        else:
            is_barreira = bool(cue.get('barreira', False))
            for ch in range(1, NUM_CHANNELS + 1):
                lvl_v = levels.get(str(ch), levels.get(ch))
                if lvl_v is not None:
                    self.output[ch] = lvl_v
                    self.active[ch] = True
                    self._update_prog_base(ch, lvl_v, True)
                elif is_barreira and self.patch.get(ch).get('display', 'pct') == 'pct':
                    self.output[ch] = float(self._partida(ch))
                    self.active[ch] = False
                    self._update_prog_base(ch, self._partida(ch), False)
                # else (LTP ou canal decimal numa barreira): mantém
        if self.on_change:
            self.on_change()

    def set_position(self, idx):
        """Move a posição da lista de memórias para idx (sem transição nem
        encadeado). O VAI passa a continuar a partir desta posição."""
        if not (0 <= idx < len(self.cues)):
            return
        self._reset_salta()
        self.current_cue_idx = idx
        self.load_cue_for_edit(idx)
        # v5 etapa 4: em navegação de edição o tracking aplica-se A SECO
        self.fx_apply_tracking(idx, snap=True)

    def update_cue(self, idx):
        """Funde as ordens do programador na memória idx (filosofia LTP):
        os canais tocados passam a fazer parte da memória."""
        if not (0 <= idx < len(self.cues)):
            return False
        levels = dict(self.cues[idx].get('levels', {}))
        for ch in range(1, NUM_CHANNELS + 1):
            if self.programmer[ch] is not None:
                levels[str(ch)] = int(self.programmer[ch])
        self.cues[idx]['levels'] = levels
        self._commit_programmer()
        return True

    def update_cue_channels(self, idx, chs):
        """v6.3.3 — Actualização PARCIAL: funde na memória idx só os
        canais chs que estejam no programador (azuis) e liberta-os do
        programador (a ordem passa a ser da memória). Usado ao criar/
        modificar uma PARTE: o valor azul fica registado na cue e a
        parte governa-lhe os tempos."""
        if not (0 <= idx < len(self.cues)):
            return False
        levels = dict(self.cues[idx].get('levels', {}))
        tocados = False
        for ch in chs:
            if (1 <= ch <= NUM_CHANNELS
                    and self.programmer[ch] is not None):
                levels[str(ch)] = int(self.programmer[ch])
                self.programmer[ch] = None
                self._prog_base[ch] = None
                self._prog_abase[ch] = None
                self.active[ch] = True
                tocados = True
        if tocados:
            self.cues[idx]['levels'] = levels
            if self.on_change:
                self.on_change()
        return tocados

    # ── retratos (snapshots) ──────────────────
    def save_retrato(self, idx, title, halo):
        """Guarda no retrato idx o estado actual dos canais activos / no
        programador. Os canais passivos não entram no retrato."""
        if not (0 <= idx < len(self.retratos)):
            return
        levels = {}
        for ch in range(1, NUM_CHANNELS + 1):
            if self.programmer[ch] is not None:
                levels[str(ch)] = int(self.programmer[ch])
            elif self.active[ch]:
                levels[str(ch)] = int(round(self.output[ch]))
        self.retratos[idx] = {'title': title, 'halo': halo, 'levels': levels}
        # NOTA: um retrato NÃO é uma memória — não compromete o programador.
        # Os canais mantêm-se azuis (podem ser libertados, gravados, etc.).

    def alias_family(self, chs):
        """v6.3.3 — expande um conjunto de canais pela ALCUNHA (alias).
        As alcunhas marcam canais do MESMO aparelho (ex.: 600 = DIM +
        R/G/B/W de um par LED): basta ter UM canal do aparelho no
        conjunto (o dimmer, p. ex.) para o conjunto passar a incluir o
        aparelho INTEIRO — não é preciso seleccionar tudo para um
        retrato actuar no aparelho (pedido do autor 2026-07-08).
        Canais sem alcunha (0) não expandem nada."""
        out = set(chs)
        alcs = set()
        for ch in chs:
            if 1 <= ch <= NUM_CHANNELS:
                a = int(self.patch.get(ch).get('alcunha') or 0)
                if a > 0:
                    alcs.add(a)
        if alcs:
            for ch in range(1, NUM_CHANNELS + 1):
                if int(self.patch.get(ch).get('alcunha') or 0) in alcs:
                    out.add(ch)
        return out

    def recall_retrato(self, idx, only=None):
        """Chama um retrato — aplica os seus valores no programador.
        only=None      → aplica TODOS os canais gravados no retrato.
        only={canais}  → aplica SÓ os canais indicados que TAMBÉM pertencem ao
                         retrato (os restantes do retrato ficam como estão).
                         v6.2: permite chamar só parte do retrato pela selecção."""
        if 0 <= idx < len(self.retratos) and self.retratos[idx]:
            for ch_s, v in self.retratos[idx].get('levels', {}).items():
                ch = int(ch_s)
                if only is not None and ch not in only:
                    continue
                self.set_channel(ch, v)

    def set_cue_field(self, idx, field, value):
        """Altera um campo simples de uma memória
        ('label', 'fade_in', 'fade_out', 'follow')."""
        if 0 <= idx < len(self.cues):
            self.cues[idx][field] = value

    def renumber_cue(self, idx, new_num):
        """Muda o número de uma memória e reordena a lista.
        Devolve o novo índice da memória. O ZERO (idx 0) não se renumera."""
        if not (1 <= idx < len(self.cues)):
            return idx
        self._reset_salta()
        cur_obj = (self.cues[self.current_cue_idx]
                   if 0 <= self.current_cue_idx < len(self.cues) else None)
        cue = self.cues.pop(idx)
        cue['num'] = new_num
        new_idx = len(self.cues)
        for i in range(1, len(self.cues)):   # salta o ZERO em [0]
            if self.cues[i]['num'] > new_num:
                new_idx = i
                break
        self.cues.insert(new_idx, cue)
        if cur_obj is not None:
            try:
                self.current_cue_idx = self.cues.index(cur_obj)
            except ValueError:
                self.current_cue_idx = -1
        return new_idx

    def set_channel(self, ch, level):
        if 1 <= ch <= NUM_CHANNELS:
            if self.programmer[ch] is None:
                # guarda o valor e o estado que o canal tinha antes do override
                self._prog_base[ch] = self.output[ch]
                self._prog_abase[ch] = self.active[ch]
            self.programmer[ch] = max(0, min(255, int(level)))
            self.active[ch] = True       # uma ordem torna o canal activo

    def clear_programmer(self, duration=0.0, exclude=None):
        """Apaga os canais forçados no programador (azul), repondo o valor de
        antes do override. v6.2: duration>0 → faz FADE (no tempo) do valor
        actual até à base; 0 = instantâneo (comportamento antigo).
        v6.4: `exclude` = canais a NÃO libertar (os conduzidos pelo DMX-In,
        que voltariam logo na tick seguinte)."""
        exc = exclude or ()
        if duration and duration > 0:
            with self._lock:
                # canais a libertar. Se NENHUM, NÃO se toca na transição em
                # curso — e os canais SEM programador NÃO têm o alvo reescrito
                # (senão congelavam a meio do fade: bug "Limpar 2× encrava nos
                # 80%", 2026-06-23). Só os canais do programador é que fundem.
                prog_chs = [ch for ch in range(1, NUM_CHANNELS + 1)
                            if self.programmer[ch] is not None and ch not in exc]
                if prog_chs:
                    self.fade_start = self.output[:]
                    for ch in prog_chs:
                        base = self._prog_base[ch]
                        self.fade_target[ch] = float(base if base is not None
                                                     else self.output[ch])
                        if self._prog_abase[ch] is not None:
                            self.active[ch] = self._prog_abase[ch]
                        self.programmer[ch] = None
                        self._prog_base[ch] = None
                        self._prog_abase[ch] = None
                    self._start_release_fade(duration)
            if prog_chs and self.on_change:
                self.on_change()
            return
        # instantâneo (comportamento antigo)
        for ch in range(1, NUM_CHANNELS + 1):
            if self.programmer[ch] is not None and ch not in exc:
                self.programmer[ch] = None
                if not self.fading and self._prog_base[ch] is not None:
                    self.output[ch] = self._prog_base[ch]
                    if self._prog_abase[ch] is not None:
                        self.active[ch] = self._prog_abase[ch]
                self._prog_base[ch] = None
                self._prog_abase[ch] = None
        # forca refresh da UI: o _tick pode nao detectar mudanca de output
        # quando este ja igualava o _prog_base, e a celula ficava azul.
        if self.on_change:
            self.on_change()

    # ── estado VIVO para o undo (programador/saída/posição) ──
    def live_snapshot(self):
        """Fotografia do estado VIVO (não estrutural) para o Ctrl+Z: programador,
        saída, activos e posição da cuelist. Permite desfazer mexidas manuais."""
        with self._lock:
            return {
                'programmer': list(self.programmer),
                'output':     [float(v) for v in self.output],
                'active':     list(self.active),
                'prog_base':  list(self._prog_base),
                'prog_abase': list(self._prog_abase),
                'cue_idx':    self.current_cue_idx,
            }

    def restore_live(self, st):
        """Repõe o estado vivo guardado por live_snapshot (ajusta ao tamanho
        actual do show, caso tenha mudado). Pára a transição em curso."""
        if not st:
            return
        n = NUM_CHANNELS + 1

        def _fit(lst, fill):
            out = [fill] * n
            for i in range(min(len(lst), n)):
                out[i] = lst[i]
            return out
        with self._lock:
            self.programmer  = _fit(st.get('programmer', []), None)
            self.output      = _fit(st.get('output', []), 0.0)
            self.active      = _fit(st.get('active', []), False)
            self._prog_base  = _fit(st.get('prog_base', []), None)
            self._prog_abase = _fit(st.get('prog_abase', []), None)
            self.fade_start  = self.output[:]
            self.fade_target = self.output[:]
            self.fading = False
            self.follow_armed = False
            idx = st.get('cue_idx', -1)
            self.current_cue_idx = idx if 0 <= idx < len(self.cues) else -1
        if self.on_change:
            self.on_change()

    def release_output(self, pct_only, duration=0.0, exclude=None):
        """v6.2 — DEITA O OUTPUT ABAIXO para os valores de DEFEITO, com FADE no
        tempo `duration` (0 = instantâneo). Para construir uma memória do zero
        sem fazer ZERO.
          pct_only=True  → só as INTENSIDADES (0-100%) vão ao defeito/0.
          pct_only=False → TUDO (inclui atributos 0-255) vai ao defeito.
        Limpa o programador/estado activo dos canais afectados. Usa o fade do
        motor mas NÃO arma o follow (_releasing).
        v6.4: `exclude` = canais a NÃO mexer (conduzidos pelo DMX-In)."""
        exc = exclude or ()
        with self._lock:
            self.follow_armed = False
            self.fade_start = self.output[:]
            for ch in range(1, NUM_CHANNELS + 1):
                is_pct = self.patch.get(ch).get('display', 'pct') == 'pct'
                if (pct_only and not is_pct) or ch in exc:
                    self.fade_target[ch] = self.output[ch]   # não mexe
                    continue
                d = float(self._partida(ch))
                self.fade_target[ch] = d
                self.active[ch] = False
                self.programmer[ch] = None
                self._prog_base[ch] = None
                self._prog_abase[ch] = None
            self._start_release_fade(duration)
        if self.on_change:
            self.on_change()

    def _start_release_fade(self, duration):
        """Arranca (ou aplica a seco) o fade de release já com fade_start/target
        definidos. Chamar SOB o lock. duration<=0 = instantâneo."""
        if duration and duration > 0:
            self.fade_in = float(duration)
            self.fade_out = float(duration)
            self.delay_in = 0.0
            self.delay_out = 0.0
            # v6.3.3 — o release ignora as PARTES: tempo único p/ todos
            for ch in range(1, NUM_CHANNELS + 1):
                self.fade_dur[ch] = float(duration)
                self.fade_del[ch] = 0.0
            self.fade_total = float(duration)
            self.fade_time = time.time()
            self.fading = True
            self._releasing = True
            self.paused = False
        else:
            for ch in range(1, NUM_CHANNELS + 1):
                self.output[ch] = self.fade_target[ch]
            self.fading = False
            self._releasing = False

    def toggle_blackout(self):
        """B.O. (Black Out) — toggle. ZERA o DMX que sai por sACN, mas
        NAO toca no estado interno (output/programmer/cues). Ao desligar,
        o sinal volta exactamente ao que estava antes. Usado em emergencia."""
        self.bo_active = not self.bo_active
        if self.on_change:
            self.on_change()

    def clear_channel(self, ch):
        """Liberta um único canal do programmer (mesma lógica do clear_programmer
        mas só para o canal ch). Usado pela consola na acção LIBERTA."""
        if not (1 <= ch <= NUM_CHANNELS): return
        if self.programmer[ch] is None: return
        self.programmer[ch] = None
        if not self.fading and self._prog_base[ch] is not None:
            self.output[ch] = self._prog_base[ch]
            if self._prog_abase[ch] is not None:
                self.active[ch] = self._prog_abase[ch]
        self._prog_base[ch] = None
        self._prog_abase[ch] = None
        # com transição em curso → o fade reassume o canal sozinho
        if self.on_change:
            self.on_change()

    # ── v3 #1: tamanho do show variavel (max MAX_CHANNELS) ────
    def has_recordings(self):
        """True se ja foi gravada alguma cue (alem do ZERO), retrato,
        grupo ou submaster com luz. Usado para bloquear a reducao do
        tamanho do show — encolher apagava memorias gravadas."""
        if len(self.cues) > 1: return True
        if any(r is not None for r in self.retratos): return True
        if any(g is not None for g in self.groups):   return True
        if any(sm.get('levels') for sm in self.submasters): return True
        return False

    def resize(self, new_n):
        """Redimensiona as listas internas do engine e do patch para new_n
        canais (1..new_n). Preserva os dados dos canais que continuam a
        existir. Atualiza o NUM_CHANNELS GLOBAL para que todos os loops
        `for ch in range(1, NUM_CHANNELS + 1)` no codigo passem a iterar
        o novo intervalo."""
        global NUM_CHANNELS
        new_n = max(1, min(MAX_CHANNELS, int(new_n)))
        old_n = NUM_CHANNELS
        if new_n == old_n:
            return
        # v4: tudo sob o lock — a thread do engine nunca apanha as listas
        # com um tamanho e o NUM_CHANNELS com outro (matava a thread).
        with self._lock:
            keep = min(old_n, new_n)

            def _grow_shrink(lst, fill):
                new = [fill] * (new_n + 1)
                for i in range(1, keep + 1):
                    if i < len(lst):
                        new[i] = lst[i]
                return new

            self.output      = _grow_shrink(self.output,      0.0)
            self.programmer  = _grow_shrink(self.programmer,  None)
            self.active      = _grow_shrink(self.active,      False)
            self._prog_base  = _grow_shrink(self._prog_base,  None)
            self._prog_abase = _grow_shrink(self._prog_abase, None)
            self.fade_start  = _grow_shrink(self.fade_start,  0)
            self.fade_target = _grow_shrink(self.fade_target, 0)
            self.fade_dur    = _grow_shrink(self.fade_dur,    0.0)  # v6.3.3
            self.fade_del    = _grow_shrink(self.fade_del,    0.0)

            if new_n > old_n:
                for ch in range(old_n + 1, new_n + 1):
                    self.patch.data[ch] = Patch._default(ch)
            else:
                for ch in list(self.patch.data.keys()):
                    if ch > new_n:
                        del self.patch.data[ch]

            NUM_CHANNELS = new_n   # só DEPOIS de as listas terem o novo tamanho

        # v4: encolher o show pode ter removido canais (e universos) do patch
        self.sync_sacn_outputs()
        if self.on_change:
            self.on_change()

    def reset_show(self):
        """Repoe o engine como acabado de arrancar: patch 1-para-1,
        sem cues, sem retratos, sem grupos, submasters limpos.
        Usado pelo 'New Show'. v4: corre sob o lock do engine."""
        with self._lock:
            self._reset_show_impl()

    def _reset_show_impl(self):
        self.patch = Patch()
        self.cues = [self._make_zero()]
        self.current_cue_idx = -1
        self.intensity_mode = 'cue_only'   # v6.2: novo show usa o modelo novo
        self.presets = ["0", "0"]
        self.retratos = [None] * 20
        self.groups = [None] * 20
        self.submasters = self._make_submasters()
        self.fx = [None] * NUM_FX                 # v5
        self.fx_active = [False] * NUM_FX
        self._fx_run = [None] * NUM_FX
        self.fx_levels = {}
        self._fx_scale = [1.0] * NUM_FX
        self._fx_ramp = [None] * NUM_FX
        self.fading = False
        self.follow_armed = False
        self.paused = False
        self.programmer = [None] * (NUM_CHANNELS + 1)
        self._prog_base = [None] * (NUM_CHANNELS + 1)
        self._prog_abase = [None] * (NUM_CHANNELS + 1)
        self.active = [False] * (NUM_CHANNELS + 1)
        self._output_to_partida()
        if self.on_change:
            self.on_change()

    # ── show file ─────────────────────────────
    def _show_data(self):
        """Os dados do show (o que se grava no ficheiro)."""
        return {
            'num_channels': NUM_CHANNELS,    # v3 #1
            # v6.2: modelo da cuelist ('cue_only' | 'tracking'). Shows antigos
            # sem o campo abrem como 'tracking' (compatível com a v6.1).
            'intensity_mode': self.intensity_mode,
            'patch': {str(k): v for k, v in self.patch.data.items()},
            'cues': self.cues,
            'presets': self.presets,
            'retratos': self.retratos,
            'groups': self.groups,
            'submasters': [{'name': sm['name'], 'levels': sm['levels']}
                           for sm in self.submasters],
            # v5: os 10 efeitos da página FX (None = vazio). A v3/v4
            # ignoram este campo ao abrir o show — compatibilidade mantida.
            'fx': self.fx,
            # v3: grava também a config de saída sACN (lista de universos).
            # v4: grava a lista EFECTIVA (em modo auto, a derivada do
            # renumerador) — assim a v3 abre o show e emite o mesmo.
            'sacn_universes': list(self.out_universes()),
            # v4: modo de saída completo (sACN + Art-Net). A v3 ignora este
            # campo ao abrir o mesmo show — compatibilidade mantida.
            'output_cfg': {
                'universes_auto':   bool(self.universes_auto),
                'manual_universes': list(self.sacn_universes),
                'sacn_multicast':   bool(self.sacn_multicast),
                'sacn_unicast_ip':  self.sacn_unicast_ip,
                'artnet_enabled':   bool(self.artnet_enabled),
                'artnet_broadcast': bool(self.artnet_broadcast),
                'artnet_dest_ip':   self.artnet_dest_ip,
            },
        }

    def snapshot(self):
        """Assinatura do estado do show — para detectar alterações por gravar."""
        return json.dumps(self._show_data(), sort_keys=True, ensure_ascii=False)

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._show_data(), f, indent=2, ensure_ascii=False)

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # v4: aplica tudo sob o lock do engine (ver _run_cue)
        with self._lock:
            self._load_data(data)

    def _load_data(self, data):
        # v3 #1: aplica num_channels ANTES de carregar patch/cues, para que
        # as listas internas tenham o tamanho certo para os dados que vamos
        # colocar. Shows antigos sem este campo assumem 100. Limite 1..512.
        new_n = max(1, min(MAX_CHANNELS, int(data.get('num_channels', 100))))
        if new_n != NUM_CHANNELS:
            self.resize(new_n)
        if 'patch' in data:
            pd = {}
            for k, v in data['patch'].items():
                ch = int(k)
                if isinstance(v, dict):
                    # alcunha: int 0..9999 (0 = sem alcunha, mostra n.º canal)
                    try:    alc = int(v.get('alcunha', 0) or 0)
                    except: alc = 0
                    alc = max(0, min(9999, alc))
                    curva = v.get('curva', CURVE_LINEAR)
                    if curva not in CURVE_VALUES: curva = CURVE_LINEAR
                    pd[ch] = {'universe': v.get('universe', 1),
                              'addrs': list(v.get('addrs', [])),
                              'bit16': bool(v.get('bit16', False)),
                              'fine': list(v.get('fine', [])),
                              'halo': v.get('halo'),
                              'display': v.get('display', 'pct'),
                              'default': v.get('default'),
                              'name': str(v.get('name', ''))[:6],
                              'alcunha': alc,
                              'curva': curva}
                else:   # formato antigo [universo, endereço]
                    pd[ch] = {'universe': v[0], 'addrs': [v[1]],
                              'bit16': False, 'fine': [], 'halo': None,
                              'display': 'pct', 'default': None,
                              'name': '', 'alcunha': 0, 'curva': CURVE_LINEAR}
            self.patch.data = {ch: pd.get(ch, Patch._default(ch))
                               for ch in range(1, NUM_CHANNELS + 1)}
        if 'cues' in data:
            self.cues = data['cues']
            # v6.3 — garante os campos MIDI em shows antigos (sem MIDI).
            for c in self.cues:
                c.setdefault('midi_nota', None)
                c.setdefault('midi_direccao', None)
                # migração: atraso passou de ms (int) para segundos (float).
                if 'midi_delay_ms' in c and 'midi_delay_s' not in c:
                    try:
                        c['midi_delay_s'] = int(c['midi_delay_ms']) / 1000.0
                    except (TypeError, ValueError):
                        c['midi_delay_s'] = 0.0
                c.pop('midi_delay_ms', None)
                c.setdefault('midi_delay_s', 0.0)
                # v6.3.3 — PARTES: normaliza/limpa (shows antigos não têm
                # o campo; ficheiros doentes não rebentam a app)
                pts = normaliza_parts(c.get('parts'))
                if pts:
                    c['parts'] = pts
                else:
                    c.pop('parts', None)
        self._ensure_zero()
        # v6.2: shows SEM o campo são v6.1 ou anteriores → 'tracking' (mantém o
        # comportamento com que foram gravados). Com o campo, respeita-o.
        im = data.get('intensity_mode', 'tracking')
        self.intensity_mode = im if im in ('tracking', 'cue_only') else 'tracking'
        p = data.get('presets', ["0", "0"])
        self.presets = [str(p[0]) if len(p) > 0 else "0",
                        str(p[1]) if len(p) > 1 else "0"]
        rt = data.get('retratos', [])
        self.retratos = [(rt[i] if i < len(rt) else None) for i in range(20)]
        gr = data.get('groups', [])
        self.groups = [(gr[i] if i < len(gr) else None) for i in range(20)]
        # submasters: restaura nome + níveis; o fader arranca sempre a 0
        smd = data.get('submasters', [])
        self.submasters = self._make_submasters()
        for i in range(2):
            if i < len(smd) and isinstance(smd[i], dict):
                self.submasters[i]['name'] = smd[i].get('name', f'Sub {i + 1}')
                self.submasters[i]['levels'] = dict(smd[i].get('levels', {}))
        # v5: efeitos FX — shows v3/v4 sem o campo ficam com NUM_FX vazios.
        # Os FX carregam sempre DESACTIVADOS (o estado activo é runtime).
        fxd = data.get('fx', [])
        self.fx = [(fxd[i] if i < len(fxd) and isinstance(fxd[i], dict)
                    else None) for i in range(NUM_FX)]
        self.fx_active = [False] * NUM_FX
        self._fx_run = [None] * NUM_FX
        self.fx_levels = {}
        self._fx_scale = [1.0] * NUM_FX
        self._fx_ramp = [None] * NUM_FX
        # v3: restaura a config de saída sACN (lista de universos). Shows
        # antigos sem este campo mantêm o valor actual. Aceita também o formato
        # antigo (sacn_universe + sacn_num_universes = gama contígua).
        if 'sacn_universes' in data:
            self.sacn_universes = self._norm_universes(
                data.get('sacn_universes') or [1])
        elif 'sacn_universe' in data:
            first = data.get('sacn_universe', 1)
            num = data.get('sacn_num_universes', 1)
            try:
                first = max(1, int(first))
                num = max(1, min(4, int(num)))
                self.sacn_universes = self._norm_universes(
                    range(first, first + num))
            except (TypeError, ValueError):
                pass
        # v4: restaura a configuração de saída (sACN modo + Art-Net) se o
        # show a tiver gravado. Shows v3 não têm este campo — mantêm defaults
        # (universos automáticos, derivados do patch acabado de carregar).
        oc = data.get('output_cfg')
        if isinstance(oc, dict):
            self.universes_auto   = bool(oc.get('universes_auto', True))
            if 'manual_universes' in oc:
                self.sacn_universes = self._norm_universes(
                    oc.get('manual_universes') or [1])
            self.sacn_multicast   = bool(oc.get('sacn_multicast',
                                                self.sacn_multicast))
            self.sacn_unicast_ip  = str(oc.get('sacn_unicast_ip',
                                               self.sacn_unicast_ip))
            self.artnet_enabled   = bool(oc.get('artnet_enabled', False))
            self.artnet_broadcast = bool(oc.get('artnet_broadcast', True))
            self.artnet_dest_ip   = str(oc.get('artnet_dest_ip',
                                               self.artnet_dest_ip))
        self._reset_salta()
        self.current_cue_idx = -1
        self.output = [0.0] * (NUM_CHANNELS + 1)
        self._commit_programmer()
        self._output_to_partida()
        # v4: o patch carregado pode trazer universos diferentes — alinha o
        # sender sACN se este já estiver a correr (o _open_show religa na
        # mesma, mas o load também pode ser chamado por outras vias)
        self.sync_sacn_outputs()

    def shutdown(self):
        self._running = False
        self.stop_sacn()
        self.stop_artnet()


# ─────────────────────────────────────────────
# DIALOGS
# ─────────────────────────────────────────────
class GDTFDialog(tk.Toplevel):
    """v6.1 — Importação GDTF: abre um .gdtf, lista os modos DMX e gera o
    footprint (abreviaturas, com «16» nos canais de 16 bit) do modo
    escolhido. result = footprint (str) quando o utilizador carrega
    «Patchar no renumerador…»; None se fechou/cancelou. By Worm."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title(T('gdtf.title'))
        self.geometry("740x560")
        self.minsize(620, 460)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.modos = {}
        self._build()

    def _build(self):
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(top, text=T('gdtf.open_btn'),
                   command=self._abrir).pack(side=tk.LEFT)
        self.lbl_file = ttk.Label(top, text=T('gdtf.no_file'),
                                  foreground='#888')
        self.lbl_file.pack(side=tk.LEFT, padx=8)

        # v6.1: a parte de baixo (footprint + botões) é ancorada ao FUNDO
        # ANTES de o corpo expandir — assim os botões ficam SEMPRE visíveis.
        bot = ttk.Frame(self, padding=8)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(bot, text=T('gdtf.footprint_label')).pack(anchor='w')
        self.foot = tk.Entry(bot, font=('Consolas', 11))
        self.foot.pack(fill=tk.X, pady=(2, 8))
        # linha própria para os botões, com altura garantida
        brow = ttk.Frame(bot)
        brow.pack(fill=tk.X)
        ttk.Button(brow, text=T('gdtf.copy_btn'),
                   command=self._copiar).pack(side=tk.LEFT)
        ttk.Button(brow, text=T('common.close'),
                   command=self.destroy).pack(side=tk.LEFT, padx=6)
        tk.Button(brow, text=T('gdtf.patch_btn'), command=self._patchar,
                  bg='#2c7d4f', fg='white', font=('Arial', 11, 'bold'),
                  relief=tk.FLAT, padx=14, pady=6,
                  cursor='hand2').pack(side=tk.RIGHT)

        body = ttk.Frame(self, padding=(8, 0))
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        left = ttk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(left, text=T('gdtf.modes_label')).pack(anchor='w')
        self.lst = tk.Listbox(left, width=22, height=14,
                              exportselection=False)
        self.lst.pack(fill=tk.Y, expand=True)
        self.lst.bind('<<ListboxSelect>>', lambda e: self._mostra())

        right = ttk.Frame(body)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        self.txt = tk.Text(right, width=50, height=14, bg='#1e1e1e',
                           fg='#d4d4d4', font=('Consolas', 9))
        self.txt.pack(fill=tk.BOTH, expand=True)

    def _abrir(self):
        p = filedialog.askopenfilename(
            title=T('gdtf.open_title'),
            filetypes=[("GDTF", "*.gdtf"), (T('common.all_files'), "*.*")])
        if not p:
            return
        try:
            self.modos = gdtf_ler(p)
        except Exception as e:
            messagebox.showerror("GDTF", T('gdtf.read_error', e=e))
            return
        self.lbl_file.config(text=p.replace('\\', '/').rsplit('/', 1)[-1])
        self.lst.delete(0, tk.END)
        for nome, canais in self.modos.items():
            self.lst.insert(tk.END, f"{nome}  ({len(canais)} ch)")
        if self.modos:
            self.lst.selection_set(0)
            self._mostra()

    def _mostra(self):
        sel = self.lst.curselection()
        if not sel:
            return
        nome = list(self.modos.keys())[sel[0]]
        canais = self.modos[nome]
        self.txt.delete('1.0', tk.END)
        self.txt.insert(tk.END, T('gdtf.mode_header', nome=nome,
                                  n=len(canais)) + "\n\n")
        self.txt.insert(tk.END, f"{'DMX':>4}  {'bits':>4}  {'abrev':<7} "
                                + T('gdtf.col_header') + "\n" + "-" * 48 + "\n")
        addr = 1
        for off, nb, attr, cfname, _ in canais:
            ab = gdtf_abbrev(attr) or '?'
            ab16 = ab + '16' if nb >= 2 else ab
            self.txt.insert(tk.END, f"{addr:>4}  {('16' if nb>=2 else '8'):>4}"
                                    f"  {ab16:<7} {attr or '?'}"
                                    f"  ({cfname or ''})\n")
            addr += nb
        self.foot.delete(0, tk.END)
        self.foot.insert(0, gdtf_footprint(canais))

    def _copiar(self):
        s = self.foot.get()
        if not s:
            return
        self.clipboard_clear()
        self.clipboard_append(s)
        messagebox.showinfo("GDTF", T('gdtf.copied', s=s))

    def _patchar(self):
        s = self.foot.get().strip()
        if not s:
            messagebox.showinfo("GDTF", T('gdtf.pick_first'))
            return
        self.result = s
        self.destroy()


class RepetirFixtureDialog(tk.Toplevel):
    """v6 — Carimbo de fixture: repete um modelo de N canais (nomes) ao
    longo do renumerador, a partir de um canal/endereço, +1 contíguo.

    · Marca de 16 bits: termina o nome em «16» (ex.: PAN16) → o canal fica
      16 bit e ocupa DOIS endereços (coarse + fine). Os 8 bit ocupam um.
    · Mostrar automático: DIM → 0-100 %, todos os outros → 0-255. By Worm."""
    PRESETS = ['DIM R G B W', 'R G B W', 'R G B', 'R G B W A',
               'R G B W STRB', 'DIM R G B',
               'DIM PAN16 TILT16', 'DIM PAN16 TILT16 R G B W']

    def __init__(self, parent, footprint=None):
        super().__init__(parent)
        self.title(T('rep.title'))
        self.geometry("460x520")
        self.minsize(440, 500)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self._init_foot = footprint   # v6.1: footprint pré-preenchido (GDTF)
        self._build()

    @staticmethod
    def _parse_tok(t):
        """Token do footprint → (nome[:6], is16, defeito).
        · «PAN16» / «PAN.16» → 16 bit.
        · «@N» no FIM → defeito explícito 0-255 (ex.: ZOOM@200, PAN16@128).
          Sem «@», o defeito vem do NOME (ver nome_defeito).
        Nome vazio depois de tirar as marcas = (None, False, None)."""
        s = t.strip()
        default = None
        m = re.search(r'@\s*(\d+)\s*$', s)
        if m:
            default = max(0, min(255, int(m.group(1))))
            s = s[:m.start()].rstrip()
        is16 = False
        if len(s) > 2 and s[-2:] == '16':
            is16 = True
            s = s[:-2].rstrip('.:-_~ ')
        s = s[:6]
        return (s, is16, default) if s else (None, False, None)

    @classmethod
    def parse_footprint(cls, text):
        """Texto → lista de (nome, is16, defeito), ignorando tokens vazios."""
        out = []
        for t in text.split():
            n, b, d = cls._parse_tok(t)
            if n:
                out.append((n, b, d))
        return out

    def _build(self):
        f = ttk.Frame(self, padding=12)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text=T('rep.channels_label'),
                  foreground='#888', justify='left').pack(anchor='w')
        self.v_foot = tk.StringVar(value=self._init_foot or 'DIM R G B W')
        ttk.Combobox(f, textvariable=self.v_foot, values=self.PRESETS,
                     width=34).pack(fill=tk.X, pady=(2, 2))
        # v6.2 — GDTF importa-se AQUI (fecha o ciclo dentro do Repetir
        # Aparelho), em vez de uma tecla na página principal.
        ttk.Button(f, text=T('rep.import_gdtf'),
                   command=self._import_gdtf).pack(anchor='w', pady=(0, 4))
        ttk.Label(f, text=T('rep.hint'),
                  foreground='#888', justify='left').pack(anchor='w',
                                                          pady=(0, 8))
        grid = ttk.Frame(f)
        grid.pack(fill=tk.X)

        def field(row, label, init):
            ttk.Label(grid, text=label, width=14).grid(
                row=row, column=0, sticky='w', pady=2)
            var = tk.StringVar(value=str(init))
            ttk.Entry(grid, textvariable=var, width=8).grid(
                row=row, column=1, sticky='w')
            return var

        self.v_ch   = field(0, T('rep.f_ch'), 1)
        self.v_univ = field(1, T('rep.f_univ'), 1)
        self.v_addr = field(2, T('rep.f_addr'), 1)
        self.v_qtd  = field(3, T('rep.f_qtd'), 10)
        # v6.2 — Alcunha com menu rápido (centenas/milhares); editável
        ttk.Label(grid, text=T('rep.f_alc'), width=14).grid(
            row=4, column=0, sticky='w', pady=2)
        self.v_alc = tk.StringVar(value='')          # vazia = sem alcunha
        ttk.Combobox(grid, textvariable=self.v_alc, width=8,
                     values=['', '101', '201', '301', '401', '501', '601',
                             '701', '801', '901', '1001', '2001', '3001']
                     ).grid(row=4, column=1, sticky='w')
        ttk.Label(grid, text=T('rep.alc_hint'), foreground='#888').grid(
            row=5, column=0, columnspan=2, sticky='w', pady=(0, 2))
        self.v_halo = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text=T('rep.cycle_halo'),
                        variable=self.v_halo).pack(anchor='w', pady=(8, 0))
        br = ttk.Frame(f)
        br.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(br, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(br, text=T('rep.repeat_btn'),
                   command=self._ok).pack(side=tk.RIGHT, padx=4)

    def _import_gdtf(self):
        """v6.2 — abre o GDTFDialog e preenche a pegada com o resultado.
        Fecha o ciclo GDTF dentro do próprio Repetir Aparelho."""
        dlg = GDTFDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.v_foot.set(dlg.result)

    def _ok(self):
        foot = self.parse_footprint(self.v_foot.get())   # [(nome, is16), …]
        if not foot:
            messagebox.showwarning(T('rep.title'), T('rep.need_one'))
            return
        try:
            ch, univ = int(self.v_ch.get()), int(self.v_univ.get())
            addr, qtd = int(self.v_addr.get()), int(self.v_qtd.get())
        except ValueError:
            messagebox.showwarning(T('rep.title'), T('rep.must_numbers'))
            return
        if ch < 1 or addr < 1 or qtd < 1:
            messagebox.showwarning(T('rep.title'), T('rep.must_ge1'))
            return
        # alcunha (opcional): vazia = None; senão inteiro (incrementa +1 por
        # aparelho — todos os parâmetros do mesmo aparelho partilham o valor)
        alc_txt = self.v_alc.get().strip().lstrip('@').strip()
        if alc_txt == '':
            alc = None
        else:
            try:
                alc = max(0, min(9999, int(alc_txt)))
            except ValueError:
                messagebox.showwarning(T('rep.title'), T('rep.must_numbers'))
                return
        self.result = {'foot': foot, 'ch': ch, 'univ': univ, 'addr': addr,
                       'qtd': qtd, 'halo': self.v_halo.get(), 'alc': alc}
        self.destroy()


class PatchDialog(tk.Toplevel):
    def __init__(self, parent, engine, repetir_footprint=None):
        super().__init__(parent)
        self.engine = engine
        # v6.1: se vier um footprint (do GDTF), abre logo o Repetir Aparelho
        # pré-preenchido depois da janela montar
        self._auto_footprint = repetir_footprint
        self.title(T('patch.title'))
        self.geometry("820x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self._rows = {}
        self._alcunha_entries = {}    # ch -> Entry da coluna Alcunha
        self._univ_entries = {}       # ch -> Entry da coluna Universo
        self._course_entries = {}     # ch -> Entry da coluna 8 bit
        self._fine_entries = {}       # ch -> Entry da coluna 16 bit
        self._defeito_entries = {}    # ch -> Entry da coluna Defeito
        self._range_col = None        # 'alcunha'/'univ'/'course'/'fine'/'defeito'/None
        self._range_a = None          # canal-origem do intervalo
        self._range_b = None          # canal-fim do intervalo
        self._range_origin = None     # (coluna, canal) do botão premido
        # v6.3.3f — canais ASSINALADOS como 16 bits (fundo verde na célula
        # 16 bit). A marca guia o preenchimento da coluna 8 bit (pares
        # coarse+fine). Fontes: patch existente (bit16/fine), nome …16,
        # Repetir Aparelho, e botão DIREITO do rato na célula 16 bit.
        self._bit16_mark = set()
        self._build()
        if self._auto_footprint:      # v6.1: vindo do GDTF
            self.after(80, lambda: self._repetir_fixture(self._auto_footprint))

    def _build(self):
        top = ttk.Frame(self, padding=5)
        top.pack(fill=tk.BOTH, expand=True)

        ttk.Label(top, text=T('patch.hint'), foreground='#888',
                  justify='left').pack(fill=tk.X, pady=(0, 4))

        hdr = ttk.Frame(top)
        hdr.pack(fill=tk.X)
        # v6.3.3 — clicar no cabeçalho de uma coluna de valores selecciona
        # a coluna TODA (pedido do autor p/ 8/16 bit; vale p/ as restantes
        # colunas de intervalo por coerência)
        col_do_hdr = {'patch.col_alias': 'alcunha', 'patch.col_name': 'nome',
                      'patch.col_univ': 'univ', 'patch.col_dmx8': 'course',
                      'patch.col_dmx16': 'fine', 'patch.col_default': 'defeito'}
        for key, w in (('patch.col_channel', 6), ('patch.col_alias', 7),
                       ('patch.col_name', 7), ('patch.col_univ', 6),
                       ('patch.col_dmx8', 22), ('patch.col_dmx16', 20),
                       ('patch.col_default', 8), ('patch.col_halo', 11),
                       ('patch.col_show', 9), ('patch.col_curve', 9)):
            lb = ttk.Label(hdr, text=T(key), width=w)
            lb.pack(side=tk.LEFT, padx=1)
            c = col_do_hdr.get(key)
            if c:
                lb.configure(cursor='hand2')
                lb.bind('<Button-1>',
                        lambda ev, cc=c: self._select_column(cc))

        container = ttk.Frame(top)
        container.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(container, highlightthickness=0)
        self._canvas = canvas        # v6.3.3: p/ o Enter fazer scroll
        sb = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(fill=tk.BOTH, expand=True)
        self._inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self._inner, anchor='nw')
        self._inner.bind('<Configure>',
                         lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        self._build_rows()

        btn_row = ttk.Frame(self, padding=5)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text=T('patch.clear_all'),
                   command=self._clear_all).pack(side=tk.LEFT)
        ttk.Button(btn_row, text=T('patch.one_to_one'),
                   command=self._one_to_one).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text=T('patch.repeat_fixture'),
                   command=self._repetir_fixture).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text=T('common.close'),
                   command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(btn_row, text=T('patch.apply'),
                   command=self._apply).pack(side=tk.RIGHT, padx=4)

    def _build_rows(self):
        for w in self._inner.winfo_children():
            w.destroy()
        self._rows = {}
        self._alcunha_entries = {}
        self._name_entries = {}
        self._univ_entries = {}
        self._course_entries = {}
        self._fine_entries = {}
        self._defeito_entries = {}
        self._range_col = None
        self._range_a = self._range_b = None
        self._range_origin = None
        self._bit16_mark = set()      # v6.3.3f — repovoada linha a linha
        ekw = dict(bg=self.ENTRY_BG, fg='#dddded', insertbackground='#dddded',
                   relief=tk.FLAT, highlightthickness=1,
                   highlightbackground='#3a3a52', highlightcolor='#5a5a7a')
        halo_values = [T('patch.halo_none')] + [halo_label(k)
                                                for k in HALO_COLORS]
        # validators
        v_nome    = (self.register(lambda p: len(p) <= 6), '%P')
        # v6.2: alcunha aceita 4 dígitos OU um prefixo '@' (ex.: @601) que,
        # no preenchimento por intervalo, FIXA o valor (não incrementa) — marca
        # que vários canais pertencem ao mesmo aparelho. O '@' é só uma pista de
        # edição: ao gravar fica o número (601) na app e na consola.
        v_alcunha = (self.register(lambda p: p == '' or
                     (p.isdigit() and len(p) <= 4) or
                     (p.startswith('@') and (p[1:] == '' or
                      (p[1:].isdigit() and len(p[1:]) <= 4)))), '%P')
        for ch in range(1, NUM_CHANNELS + 1):
            e = self.engine.patch.get(ch)
            row = ttk.Frame(self._inner)
            row.pack(fill=tk.X)
            ttk.Label(row, text=str(ch), width=6).pack(side=tk.LEFT, padx=1)
            # alcunha: int 1..9999, ou 0 = vazio
            alc_int = int(e.get('alcunha', 0) or 0)
            av = tk.StringVar(value=('' if alc_int == 0 else str(alc_int)))
            nv = tk.StringVar(value=str(e.get('name', ''))[:6])
            uv = tk.StringVar(value=str(e.get('universe', 1)))
            cv = tk.StringVar(value=' + '.join(str(a) for a in e.get('addrs', [])))
            fv = tk.StringVar(value=' + '.join(str(a) for a in e.get('fine', [])))
            gv = tk.StringVar(value=('' if e.get('default') is None
                                     else str(e.get('default'))))
            hv = tk.StringVar(value=halo_label(e.get('halo'))
                              if e.get('halo') else T('patch.halo_none'))
            dv = tk.StringVar(value='0-255' if e.get('display') == 'dec'
                              else '0-100 %')
            cu = tk.StringVar(value=curve_label(e.get('curva', CURVE_LINEAR)))
            # Entry da alcunha (max 4 digitos numericos) com seleccao de
            # intervalo: arrasta para baixo varias linhas, escreve um valor
            # na 1.a celula e Enter -> as restantes preenchem +1 por linha.
            ae = tk.Entry(row, textvariable=av, width=7, validate='key',
                          validatecommand=v_alcunha, **ekw)
            ae.pack(side=tk.LEFT, padx=1)
            self._bind_range(ae, 'alcunha', ch)
            self._alcunha_entries[ch] = ae
            # Combobox do nome: presets + escrita livre (max 6 chars). v6.2:
            # também aceita selecção de intervalo (arrasta várias linhas, escreve
            # o nome na 1.ª e Enter → o MESMO nome em todas; ex.: GERAL, SALA).
            ne = ttk.Combobox(row, textvariable=nv, values=CHANNEL_NAME_PRESETS,
                              width=7, validate='key', validatecommand=v_nome)
            ne.pack(side=tk.LEFT, padx=1)
            self._bind_range(ne, 'nome', ch)
            self._name_entries[ch] = ne
            # Universo: Entry com seleccao de intervalo (mesmo valor em todas)
            ue = tk.Entry(row, textvariable=uv, width=6, **ekw)
            ue.pack(side=tk.LEFT, padx=1)
            self._bind_range(ue, 'univ', ch)
            self._univ_entries[ch] = ue

            ce = tk.Entry(row, textvariable=cv, width=22, **ekw)
            ce.pack(side=tk.LEFT, padx=1)
            self._bind_range(ce, 'course', ch)
            self._course_entries[ch] = ce

            fe = tk.Entry(row, textvariable=fv, width=20, **ekw)
            fe.pack(side=tk.LEFT, padx=1)
            self._bind_range(fe, 'fine', ch)
            # v6.3.3f — botão direito assinala/desassinala o canal como
            # 16 bits (fundo verde); marca inicial vem do patch/nome
            fe.bind('<Button-3>',
                    lambda ev, c=ch: self._toggle_bit16(c))
            self._fine_entries[ch] = fe
            if (e.get('bit16') or e.get('fine')
                    or str(e.get('name', '')).strip().upper()
                    .endswith('16')):
                self._bit16_mark.add(ch)

            ge = tk.Entry(row, textvariable=gv, width=8, **ekw)
            ge.pack(side=tk.LEFT, padx=1)
            self._bind_range(ge, 'defeito', ch)
            self._defeito_entries[ch] = ge

            ttk.Combobox(row, textvariable=hv, values=halo_values,
                         width=10, state='readonly').pack(side=tk.LEFT, padx=1)
            ttk.Combobox(row, textvariable=dv, values=['0-100 %', '0-255'],
                         width=8, state='readonly').pack(side=tk.LEFT, padx=1)
            # curva: combobox readonly entre linear / rele / ligado
            # (mostra rótulo traduzido; grava o token interno)
            ttk.Combobox(row, textvariable=cu,
                         values=[curve_label(t) for t in CURVE_VALUES],
                         width=8, state='readonly').pack(side=tk.LEFT, padx=1)
            self._rows[ch] = (av, nv, uv, cv, fv, gv, hv, dv, cu)
        self._paint_bit16()           # v6.3.3f — pinta as marcas iniciais

    # ── selecção de intervalo por coluna (arrastar c/ botão esquerdo) ──
    ENTRY_BG = '#1e1e30'
    RANGE_BG = '#42506e'
    MARK16_BG = '#2e4d33'             # v6.3.3f — célula 16 bit assinalada

    # ── v6.3.3f — marca «este canal é 16 bits» ──
    def _toggle_bit16(self, ch):
        """Botão direito na célula 16 bit: assinala/desassinala o canal
        como 16 bits (fundo verde). A marca guia o preenchimento da
        coluna 8 bit (pares coarse+fine); não mexe nos valores."""
        if ch in self._bit16_mark:
            self._bit16_mark.discard(ch)
        else:
            self._bit16_mark.add(ch)
        self._paint_bit16()
        return 'break'

    def _paint_bit16(self):
        """Repinta o fundo das células 16 bit (marca verde), respeitando
        um intervalo activo (que pinta por cima)."""
        lo = hi = None
        if self._range_col == 'fine' and self._range_a is not None:
            lo, hi = sorted((self._range_a, self._range_b))
        for ch, ent in self._fine_entries.items():
            if lo is not None and lo <= ch <= hi:
                continue                       # o intervalo manda
            self._set_bg(ent, self.MARK16_BG if ch in self._bit16_mark
                         else self.ENTRY_BG)
    _COL_VI = {'alcunha': 0, 'nome': 1, 'univ': 2, 'course': 3,
               'fine': 4, 'defeito': 5}   # índice no tuplo _rows

    def _bind_range(self, entry, col, ch):
        entry.bind('<Button-1>', lambda ev: self._range_press(col, ch))
        entry.bind('<B1-Motion>', self._range_drag)
        entry.bind('<ButtonRelease-1>', self._range_release)
        entry.bind('<Return>', lambda ev: self._range_enter(col, ch))

    def _range_enter(self, col, ch):
        """Enter numa célula (v6.3.3): com intervalo activo nessa coluna →
        preenche-o (comportamento de sempre); SEM intervalo → salta para a
        célula de BAIXO da mesma coluna (pedido do autor: digitar
        endereços DMX em série — número, Enter, número, Enter…)."""
        if self._range_col == col and self._range_a is not None:
            self._range_fill(col)
            return
        # v6.3.3f — canal ASSINALADO 16 bits: o número posto no 8 bit
        # emparelha logo o seguinte na célula 16 bit do lado
        if col == 'course' and ch in self._bit16_mark and ch in self._rows:
            try:
                v = int(float(self._rows[ch][self._COL_VI['course']]
                              .get().strip().replace(',', '.')))
                self._rows[ch][self._COL_VI['fine']].set(str(v + 1))
            except (ValueError, TypeError):
                pass
        nxt = self._entries_of(col).get(ch + 1)
        if nxt is None:
            return
        nxt.focus_set()
        try:
            nxt.selection_range(0, tk.END)   # texto pré-seleccionado:
            nxt.icursor(tk.END)              # escrever substitui logo
        except (tk.TclError, AttributeError):
            pass
        # garante que a célula seguinte fica visível (scroll do canvas)
        try:
            cv = self._canvas
            topo = cv.canvasy(0)
            fundo = topo + cv.winfo_height()
            y = nxt.winfo_rooty() - self._inner.winfo_rooty()
            h = max(1, nxt.winfo_height())
            if y < topo or y + h > fundo:
                total = max(1, self._inner.winfo_height())
                cv.yview_moveto(max(0.0, (y - 2 * h) / total))
        except tk.TclError:
            pass

    def _select_column(self, col):
        """v6.3.3 — clique no CABEÇALHO: selecciona a coluna toda (1..N)
        para preencher com um Enter na 1.ª célula; 2.º clique desfaz."""
        if (self._range_col == col and self._range_a is not None
                and sorted((self._range_a, self._range_b))
                == [1, NUM_CHANNELS]):
            self._clear_range()
            return
        self._range_col = col
        self._range_a, self._range_b = 1, NUM_CHANNELS
        self._highlight_range()
        ent = self._entries_of(col).get(1)
        if ent is not None:
            ent.focus_set()
            try:
                ent.selection_range(0, tk.END)
                ent.icursor(tk.END)
            except (tk.TclError, AttributeError):
                pass
            self._canvas.yview_moveto(0.0)   # mostra o topo da coluna

    def _entries_of(self, col):
        return {'alcunha': self._alcunha_entries,
                'nome':    self._name_entries,
                'univ':    self._univ_entries,
                'course':  self._course_entries,
                'fine':    self._fine_entries,
                'defeito': self._defeito_entries}[col]

    def _range_press(self, col, ch):
        # apenas memoriza a origem; não inicia intervalo (deixa editar o texto)
        self._range_origin = (col, ch)

    def _range_drag(self, event):
        if self._range_origin is None:
            return
        ocol, och = self._range_origin
        w = self.winfo_containing(event.x_root, event.y_root)
        wpath = str(w) if w is not None else ''
        for ch, ent in self._entries_of(ocol).items():
            # 'ent is w' p/ tk.Entry; o ttk.Combobox (nome) pode devolver um
            # filho interno → também aceita w descendente do widget.
            if ent is w or (wpath and wpath.startswith(str(ent) + '.')):
                # arrasto cruzou outra linha → modo intervalo
                if ch != och or self._range_col is not None:
                    self._range_col = ocol
                    self._range_a = och
                    self._range_b = ch
                    self._highlight_range()
                return

    def _range_release(self, event):
        self._range_origin = None        # o intervalo (se houve) mantém-se

    @staticmethod
    def _set_bg(ent, color):
        # o nome é um ttk.Combobox (sem opção 'bg') — ignora em silêncio
        try:
            ent.config(bg=color)
        except tk.TclError:
            pass

    def _highlight_range(self):
        for ent in (list(self._alcunha_entries.values())
                    + list(self._name_entries.values())
                    + list(self._univ_entries.values())
                    + list(self._course_entries.values())
                    + list(self._defeito_entries.values())):
            self._set_bg(ent, self.ENTRY_BG)
        # v6.3.3f — a coluna 16 bit volta ao fundo BASE dela (marca verde
        # nos canais assinalados), não ao fundo normal
        for ch, ent in self._fine_entries.items():
            self._set_bg(ent, self.MARK16_BG if ch in self._bit16_mark
                         else self.ENTRY_BG)
        if self._range_col is None or self._range_a is None:
            return
        lo, hi = sorted((self._range_a, self._range_b))
        for ch, ent in self._entries_of(self._range_col).items():
            if lo <= ch <= hi:
                self._set_bg(ent, self.RANGE_BG)

    def _clear_range(self):
        self._range_col = None
        self._range_a = self._range_b = None
        self._highlight_range()

    def _range_fill(self, col):
        """Enter na 1ª célula do intervalo → preenche-o.
        8/16 bit: ascendente (+1 por linha). Defeito: o mesmo valor em todas.
        Se a 1ª célula estiver vazia, apaga todo o intervalo."""
        if self._range_col != col or self._range_a is None:
            return
        lo, hi = sorted((self._range_a, self._range_b))
        vi = self._COL_VI[col]
        raw = self._rows[lo][vi].get().strip() if lo in self._rows else ''
        if raw == '':
            for ch in range(lo, hi + 1):       # célula de topo vazia → apaga
                if ch in self._rows:
                    self._rows[ch][vi].set('')
            self._clear_range()
            return
        # v6.2: NOME → o MESMO texto em todas as linhas (não incrementa).
        # Ex.: selecciona canais 1..20, escreve GERAL, Enter → todos GERAL.
        if col == 'nome':
            for ch in range(lo, hi + 1):
                if ch in self._rows:
                    self._rows[ch][vi].set(raw[:6])
            self._clear_range()
            return
        raw = raw.replace(',', '.')            # colunas numéricas
        # na alcunha, prefixo '@' (ex.: @601) FIXA o valor — mesmo número em
        # todas as linhas em vez de incrementar +1.
        fixo = col == 'alcunha' and raw.startswith('@')
        if fixo:
            raw = raw[1:].strip()
        try:
            base = int(float(raw))
        except ValueError:
            return
        if col == 'course':
            # v6.3.3f — preenchimento do 8 bit CIENTE dos 16 bits: manda
            # a MARCA verde (assinalada pelo patch/nome …16/Repetir
            # Aparelho ou pelo botão direito na célula 16 bit). Canais
            # assinalados consomem DOIS endereços — coarse+fine
            # emparelhados (1,2 · 3,4 · 5,6…) e o fine escreve-se
            # sozinho; os outros consomem um. Sem marcas no intervalo,
            # comporta-se como sempre (+1 por linha). A edição manual
            # continua livre (encher 8+16 à mão também faz 16 bits).
            nxt = base
            vi_f = self._COL_VI['fine']
            for ch in range(lo, hi + 1):
                if ch not in self._rows:
                    continue
                self._rows[ch][vi].set(str(nxt))
                if ch in self._bit16_mark:
                    self._rows[ch][vi_f].set(str(nxt + 1))
                    nxt += 2
                else:
                    nxt += 1
            self._clear_range()
            return
        for i, ch in enumerate(range(lo, hi + 1)):
            if ch in self._rows:
                val = base if (fixo or col in ('defeito', 'univ')) else base + i
                self._rows[ch][vi].set(str(val))
        self._clear_range()

    def _notify(self):
        if self.engine.on_change:
            self.engine.on_change()

    def _clear_all(self):
        if messagebox.askyesno(T('patch.clear_all'), T('patch.clear_all_q')):
            self.engine.patch.clear_all()
            self._build_rows()
            self._notify()

    def _one_to_one(self):
        self.engine.patch.one_to_one()
        self._build_rows()
        self._notify()

    # ── v6: carimbo de fixture (Repetir Fixture) ──────────────
    def _repetir_fixture(self, footprint=None):
        """Carimba um modelo de fixtura (nomes) ao longo do renumerador.
        Cada nome = um canal da mesa (+1 contíguo); o endereço DMX avança 1
        (8 bit) ou 2 (16 bit: coarse+fine). DIM fica 0-100 %, os outros
        0-255. Escreve SÓ nos StringVar das linhas (self._rows) — o
        utilizador revê e grava com «Aplicar». footprint (v6.1) =
        pré-preenchimento vindo do GDTF.
        v6.2: campo Alcunha opcional — incrementa +1 POR APARELHO (todos os
        parâmetros do mesmo aparelho partilham o valor: 601…610). By Worm."""
        dlg = RepetirFixtureDialog(self, footprint=footprint)
        self.wait_window(dlg)
        if not dlg.result:
            return
        r = dlg.result
        foot = r['foot']                       # lista de (nome, is16, defeito)
        halo_keys = list(HALO_COLORS.keys())
        univ = r['univ']
        ch, addr = r['ch'], r['addr']
        alc_base = r.get('alc')                # None = não mexe na alcunha
        written = over = skipped = 0
        used_addrs = set()                     # endereços carimbados (univ)
        stamped_chs = set()                    # canais carimbados
        for i in range(r['qtd']):
            halo = halo_keys[i % len(halo_keys)] if r['halo'] else None
            for name, is16, dflt in foot:
                top = addr + 1 if is16 else addr   # último endereço usado
                if ch > NUM_CHANNELS:
                    over += 1
                elif top > 512:
                    skipped += 1
                elif ch in self._rows:
                    av, nv, uv, cv, fv, gv, hv, dv, cu = self._rows[ch]
                    up = name.strip().upper()
                    # alcunha por APARELHO: base + i (igual em todos os seus
                    # parâmetros). i = índice do aparelho repetido.
                    if alc_base is not None:
                        av.set(str(min(9999, alc_base + i)))
                    nv.set(name)
                    uv.set(str(univ))
                    cv.set(str(addr))
                    fv.set(str(addr + 1) if is16 else '')
                    # v6.3.3f — o carimbo assinala/desassinala a marca
                    # 16 bits do canal (fundo verde na célula 16 bit)
                    if is16:
                        self._bit16_mark.add(ch)
                    else:
                        self._bit16_mark.discard(ch)
                    # DIM → 0-100 %; todos os outros → 0-255
                    dv.set('0-100 %' if up in ('DIM', 'DIMMER') else '0-255')
                    # DEFEITO: «@N» explícito ou, na falta dele, pelo NOME
                    # (cores 255; PAN/TILT/ZOOM/FOCUS 127; resto 0)
                    d = dflt if dflt is not None else nome_defeito(name)
                    gv.set(str(d) if d else '')   # 0 → vazio (= 0)
                    if r['halo']:
                        hv.set(halo_label(halo))
                    used_addrs.add(addr)
                    if is16:
                        used_addrs.add(addr + 1)
                    stamped_chs.add(ch)
                    written += 1
                ch += 1
                addr += 2 if is16 else 1
        # endereço DMX único: tira os endereços carimbados de QUALQUER outro
        # canal do mesmo universo (nas linhas do renumerador, p/ o carimbo
        # ganhar — o endereço sai de onde estava)
        moved = self._clear_addrs_from_other_rows(univ, used_addrs, stamped_chs)
        self._paint_bit16()                    # v6.3.3f — mostra as marcas
        msg = T('patch.filled', n=written)
        if over:
            msg += "\n" + T('patch.over', n=over, max=NUM_CHANNELS)
        if skipped:
            msg += "\n" + T('patch.skipped', n=skipped)
        if moved:
            msg += "\n" + T('patch.moved', n=moved)
        msg += T('patch.review')
        messagebox.showinfo(T('rep.title'), msg)

    def _clear_addrs_from_other_rows(self, univ, addrs, keep_chs):
        """Tira os endereços `addrs` (do universo `univ`) das linhas do
        renumerador EXCEPTO `keep_chs` — endereço DMX único. Devolve o nº
        de linhas alteradas."""
        if not addrs:
            return 0
        n = 0
        for ch, row in self._rows.items():
            if ch in keep_chs:
                continue
            av, nv, uv, cv, fv, gv, hv, dv, cu = row
            try:
                u = int(uv.get())
            except ValueError:
                continue
            if u != univ:
                continue
            cur_c = parse_addr_list(cv.get())
            cur_f = parse_addr_list(fv.get())
            new_c = [a for a in cur_c if a not in addrs]
            new_f = [a for a in cur_f if a not in addrs]
            if new_c != cur_c or new_f != cur_f:
                cv.set(' + '.join(str(a) for a in new_c))
                fv.set(' + '.join(str(a) for a in new_f))
                n += 1
        return n

    def _apply(self):
        dropped = 0
        for ch, (av, nv, uv, cv, fv, gv, hv, dv, cu) in self._rows.items():
            try:
                u = int(uv.get())
            except ValueError:
                u = 1
            if not (1 <= u <= 63999):
                u = 1
            raw_c = parse_addr_list(cv.get())
            raw_f = parse_addr_list(fv.get())
            addrs = [a for a in raw_c if 1 <= a <= 512]
            fine = [a for a in raw_f if 1 <= a <= 512]
            dropped += (len(raw_c) - len(addrs)) + (len(raw_f) - len(fine))
            halo = hv.get()
            halo = (None if halo in ('', T('patch.halo_none'))
                    else halo_key_from_label(halo))
            display = 'dec' if dv.get() == '0-255' else 'pct'
            gtxt = gv.get().strip()
            if gtxt == '':
                default = None
            else:
                try:
                    default = max(0, min(255, int(float(gtxt.replace(',', '.')))))
                except ValueError:
                    default = None
            name = nv.get().strip()[:6]
            # alcunha: 0..9999, 0 = vazio (mostra n.º do canal na grelha).
            # v6.2: tira o prefixo '@' (pista de "não incrementar"); guarda o nº.
            atxt = av.get().strip().lstrip('@').strip()
            try:    alcunha = int(atxt) if atxt else 0
            except: alcunha = 0
            alcunha = max(0, min(9999, alcunha))
            curva = curve_from_label(cu.get())
            if curva not in CURVE_VALUES: curva = CURVE_LINEAR
            self.engine.patch.set(ch, {'universe': u, 'addrs': addrs,
                                       'bit16': len(fine) > 0,
                                       'fine': fine, 'halo': halo,
                                       'display': display, 'default': default,
                                       'name': name, 'alcunha': alcunha,
                                       'curva': curva})
        # v6 — regra universal: um endereço DMX só num canal. Tira os
        # repetidos (o 1.º canal a usá-lo fica com ele).
        dups = self.engine.patch.enforce_unique_addresses()
        # v6 — reaplica os defeitos aos canais passivos (ex.: PAN 127 passa
        # a aparecer na grelha e a ser o ponto de partida do +/-)
        self.engine.apply_defaults_to_passive()
        self._notify()
        avisos = []
        if dropped:
            avisos.append(T('patch.dropped', n=dropped))
        if dups:
            nums = ", ".join(str(c) for c in dups)
            avisos.append(T('patch.dups', nums=nums))
        if avisos:
            messagebox.showwarning(T('patch.warn_title'), "\n\n".join(avisos))
        self.destroy()        # Aplicar fecha sempre a janela


class RecordCueDialog(tk.Toplevel):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine
        self.result = None
        self.title(T('rec.title'))
        self.geometry("340x360")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        f = ttk.Frame(self, padding=12)
        f.pack(fill=tk.BOTH, expand=True)

        nums = [c['num'] for c in self.engine.cues if not c.get('zero')]
        next_n = round((nums[-1] if nums else 0) + 1, 1)

        fields = [
            (T('rec.f_num'), str(next_n)),
            (T('rec.f_label'), ""),
            (T('rec.f_fade_in'), "3.0"),
            (T('rec.f_delay_in'), "0"),
            (T('rec.f_fade_out'), "3.0"),
            (T('rec.f_delay_out'), "0"),
            (T('rec.f_auto'), ""),
        ]
        for i, (lbl, var_init) in enumerate(fields):
            ttk.Label(f, text=lbl).grid(row=i, column=0, sticky='w', pady=3)
            setattr(self, f'_v{i}', tk.StringVar(value=var_init))
            ttk.Entry(f, textvariable=getattr(self, f'_v{i}')).grid(
                row=i, column=1, sticky='ew')

        ttk.Label(f, text=T('rec.auto_note'),
                  foreground='gray', font=('Arial', 8), justify='left').grid(
            row=len(fields), column=0, columnspan=2, sticky='w', pady=(4, 0))

        f.columnconfigure(1, weight=1)

        btn = ttk.Frame(f)
        btn.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)
        ttk.Button(btn, text=T('rec.record_btn'),
                   command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.LEFT)

    def _ok(self):
        try:
            num = round(float(self._v0.get().replace(',', '.')), 2)
            label = self._v1.get()
            fade_in = float(self._v2.get().replace(',', '.'))
            delay_in = float(self._v3.get().replace(',', '.'))
            fade_out = float(self._v4.get().replace(',', '.'))
            delay_out = float(self._v5.get().replace(',', '.'))
            follow_s = self._v6.get().strip().replace(',', '.')
            follow = float(follow_s) if follow_s else None
            self.result = (num, label, fade_in, fade_out, follow,
                           delay_in, delay_out)
            self.destroy()
        except ValueError:
            messagebox.showerror(T('common.error'), T('rec.num_error'))


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title(T('settings.title'))
        self.geometry("500x560")
        self.resizable(True, True)      # v6.4 — deixa aumentar se preciso
        self.minsize(470, 480)
        self.grab_set()
        self._build()

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ── sACN tab ──
        sf = ttk.Frame(nb, padding=12)
        nb.add(sf, text=" sACN ")

        self._sacn_on = tk.BooleanVar(value=self.app.engine.sacn_enabled)
        ttk.Checkbutton(sf, text=T('set.sacn_enable'),
                        variable=self._sacn_on).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))

        # v4 — modo automático: os universos de saída derivam do renumerador
        # ("o que se patcha é o que sai"). As caixas manuais são o recurso.
        self._univ_auto = tk.BooleanVar(value=self.app.engine.universes_auto)
        ttk.Checkbutton(sf, text=T('set.univ_auto'),
                        variable=self._univ_auto,
                        command=self._toggle_univ_boxes).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=(0, 2))
        agora = ', '.join('U' + str(u)
                          for u in self.app.engine.out_universes())
        ttk.Label(sf, text=T('set.now_out', u=agora),
                  foreground='gray').grid(row=2, column=0, columnspan=2,
                                          sticky='w', pady=(0, 6))

        ttk.Label(sf, text=T('set.univ_manual')).grid(
            row=3, column=0, sticky='w')
        # 4 caixas livres — escreve o nº de cada universo (ex: 1, 7, 9, 10).
        # Vazio = caixa ignorada. Os repetidos são descartados.
        uni_box = ttk.Frame(sf)
        uni_box.grid(row=3, column=1, sticky='w')
        cur = list(self.app.engine.sacn_universes)
        self._univ_vars = []
        self._univ_entries = []
        for i in range(4):
            val = str(cur[i]) if i < len(cur) else ''
            v = tk.StringVar(value=val)
            self._univ_vars.append(v)
            en = ttk.Entry(uni_box, textvariable=v, width=5)
            en.pack(side=tk.LEFT, padx=2)
            self._univ_entries.append(en)
        self._toggle_univ_boxes()       # estado inicial conforme o modo

        self._multicast = tk.BooleanVar(value=self.app.engine.sacn_multicast)
        ttk.Checkbutton(sf, text="Multicast", variable=self._multicast).grid(
            row=5, column=0, columnspan=2, sticky='w', pady=4)

        ttk.Label(sf, text=T('set.unicast_ip')).grid(row=6, column=0, sticky='w')
        self._ip = tk.StringVar(value=self.app.engine.sacn_unicast_ip)
        ttk.Entry(sf, textvariable=self._ip, width=18).grid(row=6, column=1, sticky='w')
        ttk.Label(sf, text=T('set.if_multicast_off'),
                  foreground='gray').grid(row=7, column=0, columnspan=2, sticky='w')

        ttk.Separator(sf, orient=tk.HORIZONTAL).grid(
            row=8, column=0, columnspan=2, sticky='ew', pady=8)

        ttk.Label(sf, text=T('set.iface')).grid(row=9, column=0, sticky='w')
        ips = local_ips()
        self._bind_ip = tk.StringVar(value=self.app.engine.sacn_bind_ip)
        cb = ttk.Combobox(sf, textvariable=self._bind_ip, width=16,
                          values=[""] + ips)
        cb.grid(row=9, column=1, sticky='w')
        ttk.Label(sf, text=T('set.iface_note'),
                  foreground='gray', justify='left').grid(
            row=10, column=0, columnspan=2, sticky='w')

        # Botao APLICAR dedicado ao sACN (so afecta este tab)
        ttk.Separator(sf, orient='horizontal').grid(
            row=11, column=0, columnspan=2, sticky='ew', pady=(8, 4))
        sb = tk.Button(sf, text=T('set.apply_sacn'), command=self._apply_sacn,
                       bg='#2c7d4f', fg='white', font=('Arial', 10, 'bold'),
                       relief=tk.FLAT, padx=12, pady=6, cursor='hand2')
        sb.grid(row=12, column=0, columnspan=2, pady=(2, 2))

        # ── Art-Net tab (v4) ──
        af = ttk.Frame(nb, padding=12)
        nb.add(af, text=" Art-Net ")

        eng = self.app.engine
        self._an_on = tk.BooleanVar(value=eng.artnet_enabled)
        ttk.Checkbutton(af, text=T('set.an_enable'),
                        variable=self._an_on).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))

        univ_txt = ', '.join('U' + str(u) for u in eng.out_universes())
        origem = (T('set.origin_auto') if eng.universes_auto
                  else T('set.origin_manual'))
        ttk.Label(af, text=T('set.an_univ', origem=origem, u=univ_txt),
                  foreground='gray', justify='left').grid(
            row=1, column=0, columnspan=2, sticky='w', pady=(0, 8))

        self._an_bcast = tk.BooleanVar(value=eng.artnet_broadcast)
        ttk.Checkbutton(af, text=T('set.an_bcast'),
                        variable=self._an_bcast).grid(
            row=2, column=0, columnspan=2, sticky='w', pady=4)

        ttk.Label(af, text=T('set.unicast_ip')).grid(row=3, column=0, sticky='w')
        self._an_ip = tk.StringVar(value=eng.artnet_dest_ip)
        ttk.Entry(af, textvariable=self._an_ip, width=18).grid(
            row=3, column=1, sticky='w')
        ttk.Label(af, text=T('set.if_bcast_off'),
                  foreground='gray').grid(row=4, column=0, columnspan=2,
                                          sticky='w')

        ttk.Separator(af, orient=tk.HORIZONTAL).grid(
            row=5, column=0, columnspan=2, sticky='ew', pady=8)

        ttk.Label(af, text=T('set.iface')).grid(
            row=6, column=0, sticky='w')
        self._an_bind = tk.StringVar(value=eng.artnet_bind_ip)
        ttk.Combobox(af, textvariable=self._an_bind, width=16,
                     values=[""] + local_ips()).grid(row=6, column=1, sticky='w')
        ttk.Label(af, text=T('set.iface_note'),
                  foreground='gray').grid(row=7, column=0, columnspan=2,
                                          sticky='w')

        ttk.Separator(af, orient='horizontal').grid(
            row=8, column=0, columnspan=2, sticky='ew', pady=(8, 4))
        ab = tk.Button(af, text=T('set.apply_artnet'), command=self._apply_artnet,
                       bg='#2c7d4f', fg='white', font=('Arial', 10, 'bold'),
                       relief=tk.FLAT, padx=12, pady=6, cursor='hand2')
        ab.grid(row=9, column=0, columnspan=2, pady=(2, 2))

        # ── OSC tab ──
        of = ttk.Frame(nb, padding=12)
        nb.add(of, text=" OSC ")

        # ─ OSC IN (servidor) ─
        ttk.Label(of, text=T('set.osc_in_hdr'),
                  font=('Arial', 9, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 4))

        self._osc_on = tk.BooleanVar(value=self.app.osc_enabled)
        ttk.Checkbutton(of, text=T('set.osc_in_enable'),
                        variable=self._osc_on).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=(0, 4))

        ttk.Label(of, text=T('set.osc_in_port')).grid(row=2, column=0, sticky='w')
        self._osc_port = tk.StringVar(value=str(self.app.osc_port))
        ttk.Entry(of, textvariable=self._osc_port, width=8).grid(
            row=2, column=1, sticky='w')

        ttk.Separator(of, orient='horizontal').grid(
            row=3, column=0, columnspan=2, sticky='ew', pady=8)

        # ─ OSC OUT (cliente para a consola) ─
        ttk.Label(of, text=T('set.osc_out_hdr'),
                  font=('Arial', 9, 'bold')).grid(
            row=4, column=0, columnspan=2, sticky='w', pady=(0, 4))

        self._osc_out_on = tk.BooleanVar(value=self.app.osc_out_enabled)
        ttk.Checkbutton(of, text=T('set.osc_out_enable'),
                        variable=self._osc_out_on).grid(
            row=5, column=0, columnspan=2, sticky='w', pady=(0, 4))

        ttk.Label(of, text=T('set.osc_out_port')).grid(row=6, column=0, sticky='w')
        self._osc_out_port = tk.StringVar(value=str(self.app.osc_out_port))
        ttk.Entry(of, textvariable=self._osc_out_port, width=8).grid(
            row=6, column=1, sticky='w')

        # Botao APLICAR dedicado ao OSC (so afecta este tab)
        ttk.Separator(of, orient='horizontal').grid(
            row=7, column=0, columnspan=2, sticky='ew', pady=(12, 6))
        ob = tk.Button(of, text=T('set.apply_osc'), command=self._apply_osc,
                       bg='#2c7d4f', fg='white', font=('Arial', 10, 'bold'),
                       relief=tk.FLAT, padx=12, pady=6, cursor='hand2')
        ob.grid(row=8, column=0, columnspan=2, pady=(2, 2))

        # (v6.3: a Ajuda OSC saiu das Configurações para o menu «Ajuda».)

        # ── MIDI tab (v6.3) ──
        mf = ttk.Frame(nb, padding=12)
        nb.add(mf, text=T('settings.midi_tab'))
        if not HAS_MIDI:
            ttk.Label(mf, text=T('set.midi_unavailable'),
                      foreground='gray', justify='left').grid(
                row=0, column=0, columnspan=2, sticky='w')
        else:
            ttk.Label(mf, text=T('set.midi_in')).grid(
                row=0, column=0, sticky='w', pady=3)
            self._midi_in_var = tk.StringVar(
                value=self.app.midi_in_name or T('set.midi_none'))
            self._midi_in_cb = ttk.Combobox(mf, textvariable=self._midi_in_var,
                                            width=28, state='readonly')
            self._midi_in_cb.grid(row=0, column=1, sticky='w')
            ttk.Label(mf, text=T('set.midi_out')).grid(
                row=1, column=0, sticky='w', pady=3)
            self._midi_out_var = tk.StringVar(
                value=self.app.midi_out_name or T('set.midi_none'))
            self._midi_out_cb = ttk.Combobox(mf, textvariable=self._midi_out_var,
                                             width=28, state='readonly')
            self._midi_out_cb.grid(row=1, column=1, sticky='w')
            self._refresh_midi_ports()
            ttk.Button(mf, text=T('set.midi_refresh'),
                       command=self._refresh_midi_ports).grid(
                row=2, column=0, columnspan=2, sticky='w', pady=(6, 0))
            ttk.Separator(mf, orient='horizontal').grid(
                row=3, column=0, columnspan=2, sticky='ew', pady=(10, 6))
            mb = tk.Button(mf, text=T('set.midi_apply'),
                           command=self._apply_midi,
                           bg='#2c7d4f', fg='white', font=('Arial', 10, 'bold'),
                           relief=tk.FLAT, padx=12, pady=6, cursor='hand2')
            mb.grid(row=4, column=0, columnspan=2, pady=(2, 2))

        # ── Idioma / Language tab (v6.2 i18n) ──
        lf = ttk.Frame(nb, padding=12)
        nb.add(lf, text=T('settings.lang_tab'))
        ttk.Label(lf, text=T('settings.lang_label')).grid(
            row=0, column=0, sticky='w', pady=(0, 6))
        self._lang_var = tk.StringVar(value=LANG)
        for i, code in enumerate(AVAILABLE_LANGS):
            ttk.Radiobutton(lf, text=T('lang.' + code), value=code,
                            variable=self._lang_var).grid(
                row=1 + i, column=0, sticky='w')
        ttk.Label(lf, text=T('settings.lang_note'), foreground='gray',
                  wraplength=380, justify='left').grid(
            row=10, column=0, sticky='w', pady=(10, 6))
        lb = tk.Button(lf, text=T('settings.lang_apply'),
                       command=self._apply_lang,
                       bg='#2c7d4f', fg='white', font=('Arial', 10, 'bold'),
                       relief=tk.FLAT, padx=12, pady=6, cursor='hand2')
        lb.grid(row=11, column=0, pady=(2, 2), sticky='w')

        # ── Cuelist tab (v6.2: modelo intensidade cue-only vs tracking) ──
        clf = ttk.Frame(nb, padding=12)
        nb.add(clf, text=T('settings.cl_tab'))
        ttk.Label(clf, text=T('settings.cl_label'),
                  font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky='w',
                                                  pady=(0, 6))
        self._cl_mode = tk.StringVar(value=self.app.engine.intensity_mode)
        ttk.Radiobutton(clf, text=T('settings.cl_cueonly'), value='cue_only',
                        variable=self._cl_mode).grid(row=1, column=0, sticky='w')
        ttk.Radiobutton(clf, text=T('settings.cl_tracking'), value='tracking',
                        variable=self._cl_mode).grid(row=2, column=0, sticky='w')
        ttk.Label(clf, text=T('settings.cl_note'), foreground='gray',
                  wraplength=400, justify='left').grid(
            row=3, column=0, sticky='w', pady=(10, 6))
        cb2 = tk.Button(clf, text=T('settings.cl_apply'),
                        command=self._apply_cuelist,
                        bg='#2c7d4f', fg='white', font=('Arial', 10, 'bold'),
                        relief=tk.FLAT, padx=12, pady=6, cursor='hand2')
        cb2.grid(row=4, column=0, pady=(2, 2), sticky='w')

        # ── DMX-In tab (v6.4, Etapa 1: só escuta) ──
        df = ttk.Frame(nb, padding=12)
        nb.add(df, text=T('settings.din_tab'))
        self._din_on = tk.BooleanVar(value=self.app._dmx_in is not None)
        ttk.Checkbutton(df, text=T('din.enable'),
                        variable=self._din_on).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 6))
        ttk.Label(df, text=T('din.univs')).grid(row=1, column=0, sticky='w')
        univs_act = (self.app._dmx_in.universos if self.app._dmx_in
                     else DMX_IN_UNIVS)
        self._din_univs = tk.StringVar(
            value=', '.join(str(u) for u in univs_act))
        ttk.Entry(df, textvariable=self._din_univs, width=14).grid(
            row=1, column=1, sticky='w', padx=(4, 0))
        ttk.Label(df, text=T('din.iface')).grid(row=2, column=0, sticky='w',
                                                pady=(6, 0))
        bind_act = (self.app._dmx_in.bind if self.app._dmx_in
                    else DMX_IN_BIND)
        ifaces = ['0.0.0.0', '127.0.0.1'] + local_ips()
        self._din_bind = tk.StringVar(value=bind_act)
        ttk.Combobox(df, textvariable=self._din_bind, values=ifaces,
                     width=16).grid(row=2, column=1, sticky='w',
                                    padx=(4, 0), pady=(6, 0))
        ttk.Label(df, text=T('din.nota'), foreground='gray',
                  wraplength=400, justify='left').grid(
            row=3, column=0, columnspan=2, sticky='w', pady=(8, 6))
        db = tk.Button(df, text=T('din.apply'), command=self._apply_dmx_in,
                       bg='#2c7d4f', fg='white', font=('Arial', 10, 'bold'),
                       relief=tk.FLAT, padx=12, pady=6, cursor='hand2')
        db.grid(row=4, column=0, pady=(2, 8), sticky='w')
        # indicador de estado por universo (actualiza enquanto o diálogo
        # está aberto; «Silêncio» = sem pacotes há mais de ~2 s)
        self._din_estado = ttk.Label(df, text='', font=('Arial', 10, 'bold'),
                                     wraplength=440, justify='left')
        self._din_estado.grid(row=5, column=0, columnspan=2, sticky='w')
        self._din_refresh_estado()

        # ── buttons (global) ──
        btn = ttk.Frame(self, padding=5)
        btn.pack(fill=tk.X)
        ttk.Button(btn, text=T('common.close'),
                   command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(btn, text=T('common.apply_all'),
                   command=self._apply).pack(side=tk.RIGHT, padx=4)

    # ── DMX-In (v6.4) ──
    def _apply_dmx_in(self):
        """Aplica o separador DMX-In: liga/desliga a escuta e persiste a
        preferência (universos + interface) no ~/.mesadelux.json."""
        global DMX_IN_UNIVS, DMX_IN_BIND
        if not self._din_on.get():
            self.app._dmx_in_desliga()
            self._din_refresh_estado()
            return
        univs = parse_universos_dmx_in(self._din_univs.get())
        if not univs:
            messagebox.showwarning(T('din.title'), T('din.univs_err'))
            return
        bind = (self._din_bind.get() or '0.0.0.0').strip()
        try:
            self.app._dmx_in_liga(univs, bind)
        except Exception as e:
            messagebox.showerror(T('din.title'),
                                 T('din.start_err', msg=str(e)))
            self._din_on.set(False)
            return
        DMX_IN_UNIVS = univs
        DMX_IN_BIND = bind
        save_app_config()
        self._din_refresh_estado()

    def _din_refresh_estado(self):
        """Estado por universo («A receber» / «Silêncio»), 2x/s enquanto
        o diálogo estiver aberto."""
        if not self.winfo_exists():
            return
        esc = self.app._dmx_in
        if esc is None:
            self._din_estado.config(text=T('din.off'), foreground='gray')
        else:
            partes = []
            algum = False
            cor = 'gray'
            for u in esc.universos:
                rx, nome, idade, tem_look = esc.estado(u)
                etiq = (' (%s)' % nome) if nome else ''
                if rx:
                    partes.append('U%d: %s%s' % (u, T('din.rx'), etiq))
                    algum = True
                elif tem_look:
                    # a fonte parou de enviar (muitas só mandam quando algo
                    # MUDA), mas o último look está SEGURO e captável —
                    # tranquilizador, não «Silêncio» alarmante
                    partes.append('U%d: %s' % (u, T('din.segurar', nome=nome or '?')))
                    if cor == 'gray':
                        cor = '#e0a52a'          # âmbar: temos look, fonte quieta
                else:
                    partes.append('U%d: %s' % (u, T('din.sem_sinal')))
            self._din_estado.config(
                text='   '.join(partes),
                foreground='#2ecc71' if algum else cor)
        self.after(500, self._din_refresh_estado)

    # v6.2 — aplica o idioma (runtime + persistência). A UI já construída
    # só muda por completo no reinício; o aviso informa o utilizador.
    def _apply_lang(self):
        set_lang(self._lang_var.get())
        messagebox.showinfo(T('settings.lang_tab').strip(),
                            T('settings.lang_note'))

    # ── MIDI (v6.3) ──
    def _refresh_midi_ports(self):
        """Repopula os dropdowns com as portas MIDI actuais (dispositivo pode
        ter sido ligado depois da janela abrir)."""
        if not HAS_MIDI:
            return
        none = T('set.midi_none')
        try:
            ins = mido.get_input_names()
            outs = mido.get_output_names()
        except Exception:
            ins = outs = []
        self._midi_in_cb['values'] = [none] + ins
        self._midi_out_cb['values'] = [none] + outs

    def _apply_midi(self):
        """Aplica as portas escolhidas: persiste e reabre as portas MIDI sem
        reiniciar a aplicação."""
        if not HAS_MIDI:
            return
        none = T('set.midi_none')
        in_sel = self._midi_in_var.get()
        out_sel = self._midi_out_var.get()
        in_name = None if in_sel in ('', none) else in_sel
        out_name = None if out_sel in ('', none) else out_sel
        self.app.apply_midi_ports(in_name, out_name)
        messagebox.showinfo(
            T('set.midi_applied'),
            T('set.midi_status', in_=in_name or none, out=out_name or none))

    def _apply_cuelist(self):
        """v6.2 — fixa o modelo da cuelist (cue_only/tracking) no show e
        reflecte-o já na cue actual (a seco). Guarda-se ao gravar o show."""
        mode = self._cl_mode.get()
        if mode not in ('cue_only', 'tracking'):
            mode = 'cue_only'
        self.app.engine.intensity_mode = mode
        idx = self.app.engine.current_cue_idx
        if 0 <= idx < len(self.app.engine.cues):
            self.app.engine.load_cue_for_edit(idx)   # aplica o novo modelo já
        self.app._mark_dirty()
        self.app._refresh()
        messagebox.showinfo(T('settings.cl_tab').strip(), T('settings.cl_note'))

    # v4 — caixas manuais só editáveis com o modo automático desligado
    def _toggle_univ_boxes(self):
        state = 'disabled' if self._univ_auto.get() else 'normal'
        for en in self._univ_entries:
            en.config(state=state)

    # ───────────────────────────────────────────────────────────────
    # APLICAR sACN — botao dedicado, so afecta sACN, NAO fecha a janela
    # ───────────────────────────────────────────────────────────────
    def _apply_sacn(self):
        # v4: modo automático (universos do renumerador) ou lista manual.
        auto = bool(self._univ_auto.get())
        # Lê as 4 caixas e normaliza (inteiros >=1, sem repetidos, máx 4).
        univs = self.app.engine._norm_universes(
            v.get().strip() for v in self._univ_vars)
        multicast = bool(self._multicast.get())
        ip = self._ip.get().strip()
        bind_ip = self._bind_ip.get().strip()

        # Aplica no estado interno PRIMEIRO (e para o sender se estiver a correr)
        self.app.engine.universes_auto  = auto
        self.app.engine.sacn_universes  = univs     # lista manual (recurso)
        self.app.engine.sacn_multicast  = multicast
        self.app.engine.sacn_unicast_ip = ip
        self.app.engine.sacn_bind_ip    = bind_ip

        if self._sacn_on.get():
            # universes=None: o start_sacn usa a lista efectiva
            # (out_universes) — auto ou manual conforme o modo
            ok, msg = self.app.engine.start_sacn(
                None, multicast, ip, bind_ip)
            if ok:
                messagebox.showinfo(T('set.sacn_applied'), msg)
            else:
                messagebox.showerror("sACN", T('set.sacn_start_err', msg=msg))
        else:
            self.app.engine.stop_sacn()
            messagebox.showinfo("sACN", T('set.sacn_stopped'))
        self.app._refresh_status()
        # NAO fecha a janela — assim consegues testar e reajustar

    # ───────────────────────────────────────────────────────────────
    # APLICAR Art-Net (v4) — botao dedicado, NAO fecha a janela
    # ───────────────────────────────────────────────────────────────
    def _apply_artnet(self):
        eng = self.app.engine
        bcast = bool(self._an_bcast.get())
        ip = self._an_ip.get().strip()
        bind_ip = self._an_bind.get().strip()

        # guarda sempre os parametros no engine (mesmo com Art-Net OFF)
        eng.artnet_broadcast = bcast
        eng.artnet_dest_ip = ip
        eng.artnet_bind_ip = bind_ip

        if self._an_on.get():
            if not bcast and not ip:
                messagebox.showerror("Art-Net", T('set.an_need_ip'))
                return
            ok, msg = eng.start_artnet(bcast, ip, bind_ip)
            if ok:
                messagebox.showinfo(T('set.an_applied'), msg)
            else:
                messagebox.showerror("Art-Net", T('set.an_start_err', msg=msg))
        else:
            eng.stop_artnet()
            messagebox.showinfo("Art-Net", T('set.an_stopped'))
        self.app._refresh_status()

    # ───────────────────────────────────────────────────────────────
    # APLICAR OSC — botao dedicado, so afecta OSC IN/OUT, NAO fecha
    # ───────────────────────────────────────────────────────────────
    def _apply_osc(self):
        # Le valores actuais dos campos
        try:    new_in_port  = int(self._osc_port.get())
        except: new_in_port  = self.app.osc_port
        try:    new_out_port = int(self._osc_out_port.get())
        except: new_out_port = self.app.osc_out_port
        want_in   = bool(self._osc_on.get())
        want_out  = bool(self._osc_out_on.get())

        # detecta mudancas (importante: reiniciar o servidor se a porta mudou)
        in_port_changed  = (new_in_port  != self.app.osc_port)
        out_port_changed = (new_out_port != self.app.osc_out_port)

        self.app.osc_port     = new_in_port
        self.app.osc_out_port = new_out_port

        # OSC IN: reinicia se enable mudou OU se a porta mudou
        if self.app.osc_enabled and (not want_in or in_port_changed):
            self.app.stop_osc()
        if want_in and not self.app.osc_enabled:
            self.app.start_osc()

        # OSC OUT: refaz clientes se a porta mudou ou o enable mudou
        self.app.osc_out_enabled = want_out
        if out_port_changed or want_out:
            self.app._rebuild_console_clients()

        self.app._refresh_status()
        messagebox.showinfo(
            T('set.osc_applied'),
            f"OSC IN  : {'ON :' + str(self.app.osc_port) if self.app.osc_enabled else 'OFF'}\n"
            f"OSC OUT : {'ON →:' + str(self.app.osc_out_port) if self.app.osc_out_enabled else 'OFF'}")

    # ───────────────────────────────────────────────────────────────
    # APLICAR TUDO + FECHAR (botao do rodape)
    # ───────────────────────────────────────────────────────────────
    def _apply(self):
        self._apply_sacn()
        self._apply_artnet()
        self._apply_osc()
        self.destroy()


class ValueDialog(tk.Toplevel):
    """Diálogo genérico para introduzir/editar um único valor.
    `extra` opcional = (rótulo, valor): acrescenta um botão que devolve
    logo esse valor (ex.: «Ir para ZERO» → 'zero')."""
    def __init__(self, parent, title, prompt, initial="", extra=None):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text=prompt).pack(anchor='w', pady=(0, 6))

        self._var = tk.StringVar(value=initial)
        e = ttk.Entry(f, textvariable=self._var, width=30)
        e.pack(fill=tk.X)
        e.focus_set()
        e.selection_range(0, tk.END)
        e.bind('<Return>', lambda ev: self._ok())
        e.bind('<Escape>', lambda ev: self.destroy())

        btn = ttk.Frame(f)
        btn.pack(pady=(12, 0))
        ttk.Button(btn, text=T('common.ok'),
                   command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.LEFT)
        if extra:
            lbl, val = extra
            self._extra_val = val
            tk.Button(btn, text=lbl, command=self._extra, bg='#4a0000',
                      fg='white', font=('Arial', 9, 'bold'), relief=tk.FLAT,
                      padx=8, cursor='hand2').pack(side=tk.LEFT, padx=(12, 0))

    def _extra(self):
        self.result = self._extra_val
        self.destroy()

    def _ok(self):
        self.result = self._var.get()
        self.destroy()


class MultiValueDialog(tk.Toplevel):
    """Diálogo genérico para editar vários valores de uma vez.
    `fields` é uma lista de pares (rótulo, valor_inicial)."""
    def __init__(self, parent, title, fields):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)
        self._vars = []
        for i, (lbl, init) in enumerate(fields):
            ttk.Label(f, text=lbl).grid(row=i, column=0, sticky='w', pady=3)
            v = tk.StringVar(value=init)
            self._vars.append(v)
            e = ttk.Entry(f, textvariable=v, width=12)
            e.grid(row=i, column=1, sticky='ew', padx=(8, 0))
            e.bind('<Return>', lambda ev: self._ok())
            e.bind('<Escape>', lambda ev: self.destroy())
            if i == 0:
                e.focus_set()
                e.selection_range(0, tk.END)
        f.columnconfigure(1, weight=1)

        btn = ttk.Frame(f)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn, text=T('common.ok'),
                   command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.LEFT)

    def _ok(self):
        self.result = [v.get() for v in self._vars]
        self.destroy()


class MultiAttrDialog(tk.Toplevel):
    """v6.2 — aplica NOME / HALO / ALCUNHA comuns a VÁRIOS canais (tecla R com
    selecção múltipla). Cada atributo tem uma checkbox «aplicar»; só os marcados
    são aplicados. result = dict (chaves só dos marcados):
      'name': str ; 'halo': key|None ; 'alc': (base:int, fixo:bool)
    ou None se cancelado."""
    def __init__(self, parent, n):
        super().__init__(parent)
        self.result = None
        self.title(T('multi.title', n=n))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        halo_values = [T('patch.halo_none')] + [halo_label(k) for k in HALO_COLORS]

        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text=T('multi.header', n=n), font=('Arial', 11, 'bold'),
                  foreground='#e8d44d').grid(row=0, column=0, columnspan=2,
                                             sticky='w', pady=(0, 8))
        # Nome (ligado por defeito)
        self._do_name = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text=T('cpatch.name'), variable=self._do_name).grid(
            row=1, column=0, sticky='w', pady=3)
        self._name = tk.StringVar()
        ttk.Combobox(f, textvariable=self._name, values=CHANNEL_NAME_PRESETS,
                     width=12).grid(row=1, column=1, sticky='w', padx=(8, 0))
        # Halo
        self._do_halo = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text='Halo', variable=self._do_halo).grid(
            row=2, column=0, sticky='w', pady=3)
        self._halo = tk.StringVar(value=T('patch.halo_none'))
        ttk.Combobox(f, textvariable=self._halo, values=halo_values, width=12,
                     state='readonly').grid(row=2, column=1, sticky='w', padx=(8, 0))
        # Alcunha
        self._do_alc = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text=T('cpatch.alias'), variable=self._do_alc).grid(
            row=3, column=0, sticky='w', pady=3)
        self._alc = tk.StringVar()
        ttk.Entry(f, textvariable=self._alc, width=12).grid(
            row=3, column=1, sticky='w', padx=(8, 0))
        ttk.Label(f, text=T('multi.alc_note'), foreground='#888',
                  wraplength=320, justify='left').grid(
            row=4, column=0, columnspan=2, sticky='w', pady=(2, 6))

        br = ttk.Frame(f)
        br.grid(row=5, column=0, columnspan=2, pady=(8, 0), sticky='e')
        ttk.Button(br, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(br, text=T('common.ok'),
                   command=self._ok).pack(side=tk.RIGHT, padx=4)

    def _ok(self):
        res = {}
        if self._do_name.get():
            res['name'] = self._name.get().strip()[:6]
        if self._do_halo.get():
            h = self._halo.get()
            res['halo'] = (None if h in ('', T('patch.halo_none'))
                           else halo_key_from_label(h))
        if self._do_alc.get():
            raw = self._alc.get().strip()
            fixo = raw.startswith('@')
            if fixo:
                raw = raw[1:].strip()
            try:
                base = max(0, min(9999, int(raw))) if raw else 0
            except ValueError:
                base = 0
            res['alc'] = (base, fixo)
        self.result = res
        self.destroy()


class ChannelPatchDialog(tk.Toplevel):
    """v5 — editor do renumerador para UM canal (tecla R). Mostra todas as
    opções da página do renumerador para o canal seleccionado.
    result = dict (nova entrada do patch) ou None se cancelado."""
    def __init__(self, parent, engine, ch):
        super().__init__(parent)
        self.result = None
        self.ch = ch
        self.title(T('cpatch.title', ch=ch))
        self.resizable(False, False)
        self.grab_set()
        e = engine.patch.get(ch)

        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text=T('cpatch.channel_n', ch=ch), font=('Arial', 13, 'bold'),
                  foreground='#e8d44d').grid(row=0, column=0, columnspan=2,
                                             sticky='w', pady=(0, 8))
        self._r = 1

        def field(label, widget):
            ttk.Label(f, text=label).grid(row=self._r, column=0, sticky='w',
                                          pady=3)
            widget.grid(row=self._r, column=1, sticky='w', padx=(8, 0))
            self._r += 1

        alc = int(e.get('alcunha', 0) or 0)
        self._alc = tk.StringVar(value='' if alc == 0 else str(alc))
        field(T('cpatch.alias'),
              ttk.Entry(f, textvariable=self._alc, width=12))

        self._nome = tk.StringVar(value=str(e.get('name', ''))[:6])
        field(T('cpatch.name'),
              ttk.Combobox(f, textvariable=self._nome,
                           values=CHANNEL_NAME_PRESETS, width=12))

        self._univ = tk.StringVar(value=str(e.get('universe', 1)))
        field(T('rep.f_univ'), ttk.Entry(f, textvariable=self._univ, width=12))

        self._course = tk.StringVar(
            value=' + '.join(str(a) for a in e.get('addrs', [])))
        field(T('cpatch.dmx8'),
              ttk.Entry(f, textvariable=self._course, width=20))

        self._fine = tk.StringVar(
            value=' + '.join(str(a) for a in e.get('fine', [])))
        field(T('cpatch.dmx16'),
              ttk.Entry(f, textvariable=self._fine, width=20))

        self._def = tk.StringVar(
            value='' if e.get('default') is None else str(e.get('default')))
        field(T('cpatch.default'),
              ttk.Entry(f, textvariable=self._def, width=12))

        self._halo = tk.StringVar(value=halo_label(e.get('halo'))
                                  if e.get('halo') else T('patch.halo_none'))
        field(T('cpatch.halo'),
              ttk.Combobox(f, textvariable=self._halo, state='readonly',
                           width=12,
                           values=[T('patch.halo_none')]
                           + [halo_label(k) for k in HALO_COLORS]))

        self._disp = tk.StringVar(
            value='0-255' if e.get('display') == 'dec' else '0-100 %')
        field(T('cpatch.show'),
              ttk.Combobox(f, textvariable=self._disp, state='readonly',
                           width=12, values=['0-100 %', '0-255']))

        self._curva = tk.StringVar(value=curve_label(e.get('curva',
                                                           CURVE_LINEAR)))
        field(T('cpatch.curve'),
              ttk.Combobox(f, textvariable=self._curva, state='readonly',
                           width=12,
                           values=[curve_label(t) for t in CURVE_VALUES]))

        btn = ttk.Frame(f)
        btn.grid(row=self._r, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn, text=T('patch.apply'),
                   command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.LEFT)
        self.bind('<Return>', lambda ev: self._ok())
        self.bind('<Escape>', lambda ev: self.destroy())

    def _ok(self):
        try:
            u = int(self._univ.get())
        except ValueError:
            u = 1
        if not (1 <= u <= 63999):
            u = 1
        addrs = [a for a in parse_addr_list(self._course.get())
                 if 1 <= a <= 512]
        fine = [a for a in parse_addr_list(self._fine.get())
                if 1 <= a <= 512]
        halo = self._halo.get()
        halo = (None if halo in ('', T('patch.halo_none'))
                else halo_key_from_label(halo))
        display = 'dec' if self._disp.get() == '0-255' else 'pct'
        gtxt = self._def.get().strip()
        if gtxt == '':
            default = None
        else:
            try:
                default = max(0, min(255,
                                     int(float(gtxt.replace(',', '.')))))
            except ValueError:
                default = None
        name = self._nome.get().strip()[:6]
        atxt = self._alc.get().strip()
        try:
            alc = int(atxt) if atxt else 0
        except ValueError:
            alc = 0
        alc = max(0, min(9999, alc))
        curva = curve_from_label(self._curva.get())
        if curva not in CURVE_VALUES:
            curva = CURVE_LINEAR
        self.result = {'universe': u, 'addrs': addrs, 'bit16': len(fine) > 0,
                       'fine': fine, 'halo': halo, 'display': display,
                       'default': default, 'name': name, 'alcunha': alc,
                       'curva': curva}
        self.destroy()


class RetratoDialog(tk.Toplevel):
    """Pede um título/nome e uma cor de halo (retratos e grupos)."""
    def __init__(self, parent, title_init='', halo_init=None,
                 win_title=None):
        super().__init__(parent)
        self.result = None
        self.title(win_title or T('rdlg.title_look'))
        self.resizable(False, False)
        self.grab_set()

        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text=T('rdlg.label_title')).grid(
            row=0, column=0, sticky='w', pady=3)
        self._t = tk.StringVar(value=title_init)
        e = ttk.Entry(f, textvariable=self._t, width=22)
        e.grid(row=0, column=1, sticky='ew', padx=(6, 0))
        e.focus_set()
        e.selection_range(0, tk.END)

        ttk.Label(f, text=T('cpatch.halo')).grid(
            row=1, column=0, sticky='w', pady=3)
        self._h = tk.StringVar(value=halo_label(halo_init)
                               if halo_init else T('patch.halo_none'))
        ttk.Combobox(f, textvariable=self._h, width=20, state='readonly',
                     values=[T('patch.halo_none')]
                     + [halo_label(k) for k in HALO_COLORS]).grid(
            row=1, column=1, sticky='ew', padx=(6, 0))
        f.columnconfigure(1, weight=1)

        btn = ttk.Frame(f)
        btn.grid(row=2, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn, text=T('rdlg.save'),
                   command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.LEFT)
        e.bind('<Return>', lambda ev: self._ok())

    def _ok(self):
        h = self._h.get()
        self.result = (self._t.get().strip(),
                       None if h in ('', T('patch.halo_none'))
                       else halo_key_from_label(h))
        self.destroy()


class FXCreateDialog(tk.Toplevel):
    """v5 — Comprar um FX: pede o nome e o modo (manual / dinâmico).
    result = (nome, modo) ou None se cancelado."""
    def __init__(self, parent, idx, existing=None):
        super().__init__(parent)
        self.result = None
        self.title(T('fxc.title', n=idx + 1))
        self.resizable(False, False)
        self.grab_set()
        ex = existing or {}

        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text=T('fxc.name')).grid(row=0, column=0, sticky='w', pady=3)
        self._n = tk.StringVar(value=ex.get('name')
                               or T('fxc.default_name', n=idx + 1))
        e = ttk.Entry(f, textvariable=self._n, width=18)
        e.grid(row=0, column=1, sticky='ew', padx=(6, 0))
        e.focus_set()
        e.selection_range(0, tk.END)
        e.bind('<Return>', lambda ev: self._ok())
        e.bind('<Escape>', lambda ev: self.destroy())

        ttk.Label(f, text=T('fxc.mode')).grid(row=1, column=0, sticky='nw', pady=(8, 0))
        self._m = tk.StringVar(value=ex.get('mode') or 'manual')
        rb = ttk.Frame(f)
        rb.grid(row=1, column=1, sticky='w', padx=(6, 0), pady=(8, 0))
        ttk.Radiobutton(rb, text=T('fxc.manual'),
                        variable=self._m, value='manual').pack(anchor='w')
        ttk.Radiobutton(rb, text=T('fxc.dynamic'),
                        variable=self._m, value='dinamico').pack(anchor='w')
        ttk.Radiobutton(rb, text=T('fxc.chaos'),
                        variable=self._m, value='caos').pack(anchor='w')
        f.columnconfigure(1, weight=1)

        btn = ttk.Frame(f)
        btn.grid(row=2, column=0, columnspan=2, pady=(14, 0))
        ttk.Button(btn, text=T('btn.take'),
                   command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.LEFT)

    def _ok(self):
        nome = self._n.get().strip()
        self.result = (nome, self._m.get())
        self.destroy()


class FXLinkDialog(tk.Toplevel):
    """v5 etapa 4 — marca FX numa memória da sequência (coluna FX).
    A marca ALTERNA o efeito: liga-o nesta memória; a mesma marca numa
    memória mais à frente desliga-o (tracking).
    result: None (cancelado) | ('rem',) | (num 1-NUM_FX, fade_bool)."""
    def __init__(self, parent, current=None, gravados=None):
        super().__init__(parent)
        self.result = None
        self.title(T('fxl.title'))
        self.resizable(False, False)
        self.grab_set()
        cur = current if isinstance(current, dict) else {}

        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text=T('fxl.prompt', max=NUM_FX)).grid(
            row=0, column=0, sticky='w', pady=3)
        try:
            ini = str(int(cur.get('num'))) if cur.get('num') else ''
        except (TypeError, ValueError):
            ini = ''
        self._n = tk.StringVar(value=ini)
        e = ttk.Entry(f, textvariable=self._n, width=6)
        e.grid(row=0, column=1, sticky='w', padx=(6, 0))
        e.focus_set()
        e.selection_range(0, tk.END)
        e.bind('<Return>', lambda ev: self._ok())
        e.bind('<Escape>', lambda ev: self.destroy())
        if gravados:
            ttk.Label(f, text=T('fxl.recorded', list=", ".join(gravados)),
                      foreground='gray').grid(row=1, column=0, columnspan=2,
                                              sticky='w')

        self._fade = tk.IntVar(value=1 if cur.get('fade') else 0)
        rb = ttk.Frame(f)
        rb.grid(row=2, column=0, columnspan=2, sticky='w', pady=(8, 0))
        ttk.Radiobutton(rb, text=T('fxl.immediate'),
                        variable=self._fade, value=0).pack(anchor='w')
        ttk.Radiobutton(rb, text=T('fxl.follow_fade'),
                        variable=self._fade, value=1).pack(anchor='w')

        btn = ttk.Frame(f)
        btn.grid(row=3, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn, text=T('common.ok'),
                   command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.LEFT)

    def _ok(self):
        txt = self._n.get().strip()
        if txt == '':
            self.result = ('rem',)
            self.destroy()
            return
        try:
            n = int(txt)
        except ValueError:
            messagebox.showerror("FX", T('fxl.invalid', max=NUM_FX))
            return
        if not (1 <= n <= NUM_FX):
            messagebox.showerror("FX", T('fxl.range', max=NUM_FX))
            return
        self.result = (n, bool(self._fade.get()))
        self.destroy()


class MidiCueDialog(tk.Toplevel):
    """v6.3 — edita o MIDI de uma cue: Sem MIDI / IN / OUT, nota 1–127,
    atraso em SEGUNDOS (décimas; ex.: 0.5). result = (direccao|None,
    nota|None, delay_s) ou None se cancelado. Nunca IN e OUT ao mesmo tempo."""
    def __init__(self, parent, cue_num, direccao, nota, delay_s):
        super().__init__(parent)
        self.result = None
        self.title(T('midi.title', n=cue_num))
        self.resizable(False, False)
        self.grab_set()

        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)
        self._dir = tk.StringVar(
            value=direccao if direccao in ('in', 'out') else 'none')
        for val, key in (('none', 'midi.none'), ('in', 'midi.in'),
                         ('out', 'midi.out')):
            ttk.Radiobutton(f, text=T(key), value=val, variable=self._dir,
                            command=self._toggle).pack(anchor='w')

        gr = ttk.Frame(f)
        gr.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(gr, text=T('midi.note'), width=14).grid(
            row=0, column=0, sticky='w', pady=3)
        self._nota = tk.StringVar(value=str(int(nota)) if nota else '1')
        self._e_nota = ttk.Entry(gr, textvariable=self._nota, width=8)
        self._e_nota.grid(row=0, column=1, sticky='w')
        ttk.Label(gr, text=T('midi.delay'), width=14).grid(
            row=1, column=0, sticky='w', pady=3)
        self._delay = tk.StringVar(value=f"{float(delay_s or 0):g}")
        self._e_delay = ttk.Entry(gr, textvariable=self._delay, width=8)
        self._e_delay.grid(row=1, column=1, sticky='w')

        btn = ttk.Frame(f)
        btn.pack(pady=(12, 0))
        ttk.Button(btn, text=T('common.ok'),
                   command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn, text=T('common.cancel'),
                   command=self.destroy).pack(side=tk.LEFT)
        self._toggle()

    def _toggle(self):
        """Sem MIDI → campos Nota/Atraso desactivados (greyed)."""
        st = 'disabled' if self._dir.get() == 'none' else 'normal'
        self._e_nota.config(state=st)
        self._e_delay.config(state=st)

    def _ok(self):
        d = self._dir.get()
        if d == 'none':
            self.result = (None, None, 0.0)
            self.destroy()
            return
        try:
            nota = int(self._nota.get())
        except ValueError:
            messagebox.showerror("MIDI", T('midi.note_error'))
            return
        if not (1 <= nota <= 127):
            messagebox.showerror("MIDI", T('midi.note_error'))
            return
        try:
            s = float(self._delay.get().replace(',', '.'))
        except ValueError:
            messagebox.showerror("MIDI", T('midi.delay_error'))
            return
        if not (0.0 <= s <= 3600.0):
            messagebox.showerror("MIDI", T('midi.delay_error'))
            return
        self.result = (d, nota, s)
        self.destroy()


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
class MesaDeLuxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MESADELUX v6.4")
        self.root.geometry("1280x720")
        self.root.configure(bg='#111122')

        self.engine = Engine()
        self.engine.on_change = self._mark_dirty   # v4: só marca a flag

        self.osc_enabled       = False    # OSC IN (servidor 0.0.0.0:osc_port)
        self.osc_out_enabled   = True     # OSC OUT (envia para a consola)
        self.osc_port          = 8080     # porta do OSC IN
        self.osc_out_port      = 8081     # porta de destino do OSC OUT (console)
        self._osc_server = None
        self._console_clients = []     # OSC clientes (localhost + AP) para a consola
        self._console_ips = []         # v4: IPs de consolas APRENDIDOS (origem OSC)
        self._console_outbox = []      # v4: fila de envio paced para a consola
        self._console_sel_sent = None  # v6.2: ultima selecção espelhada p/ consola
        self._fx_console_group = None  # v6.2: grupo de 4 FX seleccionado na Consola 2
        self._clear_last = 0.0         # v6.2: 2-toque do LIMPA (sel / programador)
        self._liberta_last = 0.0       # v6.2: 2-toque do LIBERTA (pct / tudo)

        # v6.3 — MIDI (opcional): portas escolhidas (nome ou None) + objectos
        # de porta abertos. O IN escuta numa thread e passa pela fila da UI.
        self.midi_in_name = MIDI_IN_PORT
        self.midi_out_name = MIDI_OUT_PORT
        self._midi_out = None          # mido output port aberto (ou None)
        self._midi_in = None           # mido input port aberto
        self._midi_queue = queue.Queue()   # notas IN recebidas (thread→UI)
        self._midi_pump_started = False
        self._midi_pending = 0             # atrasos MIDI em curso (p/ cintilar)
        self._midi_blink_on = False        # animação da tecla MIDI ON
        self._midi_active = True       # botão MIDI ON/OFF (v6.3)

        # v4 — ponte thread-safe para a UI: as threads (engine, OSC) nunca
        # tocam no Tkinter. Poem trabalho na queue / marcam dirty; o pump
        # (root.after no mainloop) drena e refresca.
        self._ui_queue = queue.Queue()
        self._dirty = False
        self._selected = set()        # conjunto de canais seleccionados
        # v6.3.3 — PARTES: canais marcados (vermelho) na criação/edição de
        # uma parte + estado da edição em curso (None = nada armado)
        self._parte_canais = set()
        self._parte_mod = None        # {'idx': cue, 'num': parte em edição}
        # v6.4 — DMX-IN: escuta sACN activa (ou None). Os valores recebidos
        # entram AO VIVO no programador (azul-ciano); grava-se com Comprar/
        # Actualizar como qualquer look. `_din_driven` = canais conduzidos
        # agora pelo DMX-In (cor distinta + libertação bloqueada).
        self._dmx_in = None
        self._din_driven = set()
        self._dmx_in_after = None
        self._din_rejoin_c = 0        # contador p/ re-inscrever no multicast
                                      # (aditiva — só LIMPA a esvazia)
        self._step_group = None       # grupo onde o < / > anda (afinar 1 a 1)
        self._sel_locked = False      # depois de mexer num nivel, a proxima
                                      # seleccao limpa primeiro (e desbloqueia)
        self._preset_vars = {}        # presets de nível rápido
        self._record_armed = False    # COMPRAR premido, à espera de destino
        self._delete_armed = False    # v6.2: APAGAR premido, à espera de grupo/retrato
        self._undo_snap = None        # v6.2: fotografia p/ Ctrl+Z (1 nível)
        self._redo_snap = None        # v6.2: fotografia p/ Ctrl+Y
        # Consola 2 (botoes de gravacao): 1.ª pressao arma, 2.ª executa
        self._console2_pending = None    # None | 'comprar' | 'actualiza' | 'guarda'
        self._retrato_btns = []       # botões dos 20 retratos (v4.9)
        self._group_btns = []         # botões dos 20 grupos de canais (v4.9)
        self._sub_btns = []           # botões-nome dos 2 submasters
        self._sub_scales = []         # faders dos 2 submasters
        self._sub_guard = False       # evita laço ao sincronizar os faders
        self._show_file = None
        # tempo (s) do fade-out do botão LIBERTA — configurável no menu Mesa
        self._release_time = 1.0
        # v6 — vista do painel de canais: 'mesa' (canais da mesa) ou 'dmx'
        # (monitor da saída DMX, 512 endereços de um universo)
        self._chan_view = 'mesa'
        self._dmx_univ = 1            # universo a monitorizar
        self._dmx_selected = set()    # endereços DMX seleccionados (1..512)
        self._dmx_highlight = False   # teste de saída: força a selecção a full
        self._dmx_solo = False        # teste de saída: isola o universo
        # v5 — página activa do painel direito + estado da página FX
        self._page = 'xf'             # 'xf' (sequência) | 'fx' (efeitos)
        self._fx_armed = None         # None|'comprar'|'actualiza'|'apagar'
        self._fx_edit = None          # índice do FX em edição (ou None)
        self._fx_step_sel = 0         # passo seleccionado no editor manual
        self._fx_tree = None          # Treeview dos passos (se editor aberto)
        self._fx_ed_cache = None      # cache do editor (refresh a 25 fps)
        self._fx_last_active = None   # último FX ligado à mão (atalho de link)

        self._build_ui()
        self._bind_space_to_buttons(self.root)
        self._refresh()
        self._show_snapshot = self.engine.snapshot()   # estado de referência
        root.protocol("WM_DELETE_WINDOW", self._quit)

        # v4: arranca o pump da UI (única via de entrada para o Tkinter)
        self.root.after(40, self._pump)

        # auto-arranque do OSC e sACN apos a UI estar montada (after 100 ms
        # para evitar dialogos modais durante o build)
        self.root.after(150, self._auto_start_services)

    # ── v4: ponte thread-safe para a UI ───────
    def _mark_dirty(self):
        """Chamado pelo engine (qualquer thread): pede um refresh da UI.
        NÃO toca no Tkinter — apenas marca a flag, o _pump trata do resto."""
        self._dirty = True

    def _ui(self, fn):
        """Agenda fn() para correr na thread principal (Tk). Seguro a partir
        de qualquer thread (servidor OSC, engine, etc.)."""
        self._ui_queue.put(fn)

    def _pump(self):
        """Corre no mainloop a ~25 fps: drena a fila de trabalho vindo das
        outras threads e refresca a UI se o engine marcou alterações."""
        try:
            while True:
                fn = self._ui_queue.get_nowait()
                try:
                    fn()
                except Exception as e:
                    print('[ui] erro em accao agendada:', e)
        except queue.Empty:
            pass
        if self._dirty or self.engine.fading or self.engine.follow_armed:
            self._dirty = False
            self._refresh()
        elif self._chan_view == 'dmx':
            # v6: o monitor DMX é AO VIVO — actualiza sempre (a saída pode
            # mudar sem marcar dirty, ex.: Highlight a forçar um endereço).
            # Redesenho parcial, só toca nas caixas que mudaram.
            self._draw_dmx()
        self.root.after(40, self._pump)

    # ── auto-arranque de servicos no boot da app ──
    def _pick_bind_ip(self):
        """Escolhe a interface mais provavel para sair sACN/OSC:
          1. IP da rede do Pico AP (192.168.4.x)
          2. Qualquer outro IPv4 nao-loopback (ex: ethernet, 192.168.1.x)
          3. Vazio = OS decide (fallback)."""
        ips = local_ips()
        # 1. Pico AP
        for ip in ips:
            if ip.startswith('192.168.4.'):
                return ip
        # 2. Primeiro IP que nao seja loopback nem APIPA
        for ip in ips:
            if not (ip.startswith('127.') or ip.startswith('169.254.')):
                return ip
        return ''

    def _auto_start_services(self):
        """Arranca OSC IN/OUT e sACN automaticamente. Usado no boot."""
        # OSC OUT (clientes) sempre criado, mesmo que o servidor IN nao arranque
        if HAS_OSC:
            self._rebuild_console_clients()
            # envia logo todos os nomes para a consola se OUT activo
            if self.osc_out_enabled:
                self._push_all_channel_names()
                self._push_cue_state()
        try:
            if not self.osc_enabled and HAS_OSC:
                self.start_osc()
        except Exception as e:
            print('Erro auto-start OSC:', e)
        try:
            if not self.engine.sacn_enabled and HAS_SACN:
                # bind_ip: respeita o que estiver guardado no engine; so
                # tenta auto-pick se for vazio. Assim, se o utilizador ja
                # tinha definido um IP no diálogo, NAO sobrescreve.
                bind = self.engine.sacn_bind_ip or self._pick_bind_ip()
                self.engine.start_sacn(universes=self.engine.sacn_universes,
                                       multicast=self.engine.sacn_multicast,
                                       unicast_ip=self.engine.sacn_unicast_ip,
                                       bind_ip=bind)
                self._refresh_status()
        except Exception as e:
            print('Erro auto-start sACN:', e)
        # v4: Art-Net só auto-arranca se estava activo na config carregada
        # (por defeito fica OFF — o sACN continua a ser a saída principal)
        try:
            if self.engine.artnet_enabled and not self.engine.artnet_sender:
                self.engine.start_artnet(self.engine.artnet_broadcast,
                                         self.engine.artnet_dest_ip,
                                         self.engine.artnet_bind_ip
                                         or self._pick_bind_ip())
                self._refresh_status()
        except Exception as e:
            print('Erro auto-start Art-Net:', e)
        # v6.3 — MIDI: abre a porta OUT e arranca a escuta IN se já havia
        # portas guardadas na config. Silencioso se o dispositivo não estiver.
        try:
            if HAS_MIDI:
                self._open_midi_out()
                self.start_midi_in()
        except Exception as e:
            print('Erro auto-start MIDI:', e)

    # ── Espaço = VAI (prioridade máxima) ──────
    def _space_vai(self, event=None):
        """Espaço dá sempre VAI — mesmo com um botão em foco. Excepção: quando
        se está a escrever num campo de texto, o espaço é digitado normalmente."""
        w = self.root.focus_get()
        if w is not None and w.winfo_class() in ('Entry', 'TEntry', 'TCombobox'):
            return
        self._go()
        return 'break'

    def _bind_space_to_buttons(self, widget):
        """Faz com que o Espaço dê VAI mesmo quando um botão tem o foco
        (em vez de activar esse botão)."""
        for child in widget.winfo_children():
            if child.winfo_class() in ('Button', 'TButton'):
                child.bind('<KeyPress-space>', self._space_vai)
                child.bind('<KeyRelease-space>', lambda e: 'break')
            self._bind_space_to_buttons(child)

    # ── UI construction ───────────────────────
    def _on_mousewheel(self, event):
        """Roda do rato → scroll vertical do widget sob o cursor. Sobe na
        hierarquia até achar o 1.º antecessor que TENHA scroll a sério
        (yview != (0,1)); ignora os que não rolam. Funciona em qualquer
        página e em qualquer caixa/diálogo (bind_all)."""
        # direcção: Windows/Mac usam delta (±120 por entalhe); Linux usa num 4/5
        if getattr(event, 'num', 0) == 4:
            up = True
        elif getattr(event, 'num', 0) == 5:
            up = False
        elif getattr(event, 'delta', 0):
            up = event.delta > 0
        else:
            return None
        # botão direito mantido sobre a grelha → sobe/desce o nível dos canais
        # SELECCIONADOS (cada um no seu modo), em vez de fazer scroll
        if getattr(self, '_rb3_active', False):
            self._rb3_used = True
            if self._selected:
                self._adjust_level(1 if up else -1)
                self._mark_dirty()
            return 'break'
        step = -1 if up else 1
        try:
            w = self.root.winfo_containing(event.x_root, event.y_root)
        except tk.TclError:
            w = getattr(event, 'widget', None)
        while w is not None:
            scroll = getattr(w, 'yview_scroll', None)
            if scroll is not None:
                try:
                    first, last = w.yview()
                    if (float(first), float(last)) != (0.0, 1.0):
                        scroll(step, 'units')
                        return 'break'
                except (tk.TclError, TypeError, ValueError):
                    pass
            w = getattr(w, 'master', None)
        return None

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#111122')
        style.configure('TLabel', background='#111122', foreground='#ccccee')
        style.configure('TLabelframe', background='#111122', foreground='#8888aa')
        style.configure('TLabelframe.Label', background='#111122', foreground='#8888aa')
        style.configure('Treeview', background='#1a1a2e', fieldbackground='#1a1a2e',
                        foreground='#ccccee', rowheight=22)
        style.configure('Treeview.Heading', background='#2c2c44', foreground='#aaaacc')
        style.configure('Horizontal.TProgressbar', background='#e74c3c',
                        troughcolor='#2c2c3e', bordercolor='#2c2c3e',
                        lightcolor='#e74c3c', darkcolor='#e74c3c')
        # v5 — fundo magenta MUITO escuro da página FX (distingue do XF)
        FXBG = '#1e0a1e'
        self.FX_BG = FXBG
        style.configure('FX.TFrame', background=FXBG)
        style.configure('FX.TLabel', background=FXBG, foreground='#ccaacc')
        style.configure('FX.TLabelframe', background=FXBG, foreground='#c97fc9')
        style.configure('FX.TLabelframe.Label', background=FXBG,
                        foreground='#c97fc9')

        # ── menu ──
        menu = tk.Menu(self.root, bg='#1a1a2e', fg='#ccccee',
                       activebackground='#2c2c44', tearoff=0)
        self.root.config(menu=menu)

        fm = tk.Menu(menu, tearoff=0, bg='#1a1a2e', fg='#ccccee')
        menu.add_cascade(label=T('menu.file'), menu=fm)
        fm.add_command(label=T('menu.new_show'), command=self._new_show)
        fm.add_command(label=T('menu.open'), command=self._open_show)
        fm.add_command(label=T('menu.save'), command=self._save_show,
                       accelerator="Ctrl+S")
        fm.add_command(label=T('menu.save_as'), command=self._save_show_as)
        # v6.3.2 — portabilidade USITT ASCII (o .ldsk é o formato nativo)
        fm.add_separator()
        fm.add_command(label=T('menu.import_ascii'),
                       command=self._import_ascii_show)
        fm.add_command(label=T('menu.export_ascii'),
                       command=self._export_ascii_show)
        fm.add_separator()
        fm.add_command(label=T('menu.quit'), command=self._quit)

        dm = tk.Menu(menu, tearoff=0, bg='#1a1a2e', fg='#ccccee')
        menu.add_cascade(label=T('menu.desk'), menu=dm)
        dm.add_command(label=T('menu.patch'), command=self._open_patch_dialog)
        dm.add_command(label=T('menu.total_channels'),
                       command=self._change_show_size)
        self._zero_var = tk.BooleanVar(value=self.engine.zero_enabled)
        dm.add_checkbutton(label=T('menu.zero_cue'),
                           variable=self._zero_var,
                           command=self._toggle_zero)
        dm.add_command(label=T('menu.settings'),
                       command=lambda: SettingsDialog(self.root, self))
        dm.add_separator()
        dm.add_command(label=T('menu.bo'), command=self._blackout,
                       accelerator="B")
        dm.add_command(label=T('menu.clear_prog'),
                       command=self._liberta_total, accelerator="Esc")
        dm.add_command(label=T('menu.release_time'),
                       command=self._set_release_time)

        # v6.3 — menu «Ajuda» (lista de ajudas): a Ajuda OSC vive aqui agora
        hm = tk.Menu(menu, tearoff=0, bg='#1a1a2e', fg='#ccccee')
        menu.add_cascade(label=T('menu.help'), menu=hm)
        hm.add_command(label=T('menu.help_osc'), command=self._open_osc_help)

        self.root.bind('<Control-s>', lambda e: self._save_show())
        self.root.bind('<Control-z>', self._undo)   # v6.2: desfazer (1 nível)
        self.root.bind('<Control-y>', self._redo)   # v6.2: refazer
        self.root.bind('<b>', lambda e: self._blackout())
        self.root.bind('<B>', lambda e: self._blackout())
        self.root.bind('<Escape>', lambda e: self._on_liberta())
        self.root.bind('<space>', self._space_vai)
        self.root.bind('<Left>', lambda e: self._back())

        # ── roda do rato: scroll vertical geral em qualquer página/caixa ──
        # (Windows/Mac usam <MouseWheel>; Linux usa Button-4/5)
        self.root.bind_all('<MouseWheel>', self._on_mousewheel)
        self.root.bind_all('<Button-4>', self._on_mousewheel)
        self.root.bind_all('<Button-5>', self._on_mousewheel)

        # ── status bar ──
        status_bar = ttk.Frame(self.root)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=2)

        self._status_var = tk.StringVar(value=T('ui.no_show'))
        ttk.Label(status_bar, textvariable=self._status_var).pack(side=tk.LEFT)

        self._osc_out_lbl = tk.Label(status_bar, text="◉ OSC→ OFF",
                                     bg='#111122', fg='#555577', font=('Arial', 9))
        self._osc_out_lbl.pack(side=tk.RIGHT, padx=8)
        # v6.3 — MIDI IN/OUT
        self._midi_lbl = tk.Label(status_bar, text="◉ MIDI OFF",
                                  bg='#111122', fg='#555577', font=('Arial', 9))
        self._midi_lbl.pack(side=tk.RIGHT, padx=8)
        self._osc_lbl = tk.Label(status_bar, text="◉ OSC← OFF",
                                 bg='#111122', fg='#555577', font=('Arial', 9))
        self._osc_lbl.pack(side=tk.RIGHT, padx=8)
        self._sacn_lbl = tk.Label(status_bar, text="◉ sACN OFF",
                                  bg='#111122', fg='#555577', font=('Arial', 9))
        self._sacn_lbl.pack(side=tk.RIGHT, padx=8)
        # v4 — estado do Art-Net
        self._artnet_lbl = tk.Label(status_bar, text="◉ ArtNet OFF",
                                    bg='#111122', fg='#555577', font=('Arial', 9))
        self._artnet_lbl.pack(side=tk.RIGHT, padx=8)
        # IP da interface usado pelo sACN (mostrado quando activo)
        self._ip_lbl = tk.Label(status_bar, text="",
                                bg='#111122', fg='#7a7a8a', font=('Arial', 9))
        self._ip_lbl.pack(side=tk.RIGHT, padx=8)

        # ── grupos + retratos (v4.9: 20 de cada, em baixo, 2 linhas de 10;
        #    botões um pouco mais altos). Ordem do pack(BOTTOM): a status bar
        #    fica mais abaixo, depois Retratos, depois Grupos por cima.
        rf = ttk.LabelFrame(self.root, text=T('ui.snapshots'), padding=4)
        rf.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=(0, 2))
        self._retrato_btns = []
        for i in range(20):
            b = tk.Button(rf, text=T('ui.snapshot_n', n=i + 1), width=13,
                          bg='#2c2c44', fg='#ccccee', font=('Arial', 8, 'bold'),
                          relief=tk.FLAT, cursor='hand2', pady=4,
                          command=lambda i=i: self._retrato_click(i))
            b.grid(row=i // 10, column=i % 10, padx=2, pady=2, sticky='ew')
            self._retrato_btns.append(b)
        for c in range(10):
            rf.columnconfigure(c, weight=1)

        gf = ttk.LabelFrame(self.root, text=T('ui.groups'), padding=4)
        gf.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=(0, 2))
        self._group_btns = []
        for i in range(20):
            b = tk.Button(gf, text=T('ui.group_n', n=i + 1), width=13,
                          bg='#2c2c44', fg='#888899', font=('Arial', 8, 'bold'),
                          relief=tk.FLAT, cursor='hand2', pady=4,
                          command=lambda i=i: self._group_click(i))
            b.grid(row=i // 10, column=i % 10, padx=2, pady=2, sticky='ew')
            self._group_btns.append(b)
        for c in range(10):
            gf.columnconfigure(c, weight=1)

        # ── main paned ──
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        left = ttk.Frame(paned)
        paned.add(left, weight=5)
        self._build_channel_panel(left)

        right = ttk.Frame(paned)
        paned.add(right, weight=2)
        # v5: o painel direito tem DUAS páginas — XF (sequência principal,
        # a mesa de sempre) e FX (efeitos). Troca pelas teclas XF/FX que
        # estão ao lado da LIMPA, no painel esquerdo.
        self._xf_page = ttk.Frame(right)
        self._fx_page = ttk.Frame(right, style='FX.TFrame')   # fundo magenta
        self._build_cue_panel(self._xf_page)
        self._build_fx_panel(self._fx_page)
        self._xf_page.pack(fill=tk.BOTH, expand=True)   # arranca em XF

    # ── channel panel ─────────────────────────
    def _build_channel_panel(self, parent):
        # ── linha 1: selecção, níveis e ações (tudo numa linha, azul) ──
        ctrl2 = ttk.Frame(parent)
        ctrl2.pack(fill=tk.X, pady=(0, 4))


        self._sel_var = tk.StringVar()
        self._level_var = tk.StringVar(value="0")

        _BLUE = '#2c3e80'

        def _blue_btn(parent_, text, command, width=None, bg=_BLUE):
            return tk.Button(parent_, text=text, command=command,
                             bg=bg, fg='white', font=('Arial', 11, 'bold'),
                             relief=tk.FLAT, padx=10, pady=6, cursor='hand2',
                             **({'width': width} if width else {}))

        _blue_btn(ctrl2, T('btn.all'), self._todo).pack(side=tk.LEFT, padx=2)
        _blue_btn(ctrl2, T('btn.full'),
                  lambda: self._set_level(255)).pack(side=tk.LEFT, padx=2)
        _blue_btn(ctrl2, T('btn.zero'),
                  lambda: self._set_level(0)).pack(side=tk.LEFT, padx=2)

        for txt, d in (("+5", 5), ("-5", -5), ("+1", 1), ("-1", -1)):
            _blue_btn(ctrl2, txt, lambda dd=d: self._adjust_level(dd),
                      width=3).pack(side=tk.LEFT, padx=1)

        ttk.Separator(ctrl2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        self._bo_btn = _blue_btn(ctrl2, T('btn.bo'), self._blackout, bg='#4a0000')
        self._bo_btn.pack(side=tk.LEFT)
        _blue_btn(ctrl2, T('btn.release'),
                  self._on_liberta).pack(side=tk.LEFT, padx=4)
        _blue_btn(ctrl2, T('btn.clear'),
                  self._on_clear).pack(side=tk.LEFT, padx=4)

        # v5 — selecção da página do painel direito (verde = activa)
        ttk.Separator(ctrl2, orient=tk.VERTICAL).pack(side=tk.LEFT,
                                                      fill=tk.Y, padx=8)
        self._xf_btn = _blue_btn(ctrl2, "XF",
                                 lambda: self._show_page('xf'), bg='#2c7d4f')
        self._xf_btn.pack(side=tk.LEFT, padx=2)
        self._fx_btn = _blue_btn(ctrl2, "FX",
                                 lambda: self._show_page('fx'))
        self._fx_btn.pack(side=tk.LEFT, padx=2)

        # ── linha 3: pré-valores + submasters ──
        ctrl3 = ttk.Frame(parent)
        ctrl3.pack(fill=tk.X, pady=(0, 4))
        for idx in (1, 2):
            var = tk.StringVar(value="0")
            self._preset_vars[idx] = var
            var.trace_add('write', lambda *a, i=idx: self._sync_preset(i))
            tk.Button(ctrl3, text=T('ui.pre_n', n=idx),
                      command=lambda i=idx: self._apply_preset(i),
                      bg='#2c3e6a', fg='white', font=('Arial', 9, 'bold'),
                      relief=tk.FLAT, padx=6).pack(side=tk.LEFT, padx=(4, 2))
            ttk.Entry(ctrl3, textvariable=var, width=5).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Separator(ctrl3, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        # dois submasters: botão-nome (alvo do COMPRAR) + fader
        self._sub_btns = []
        self._sub_scales = []
        for i in (0, 1):
            btn = tk.Button(ctrl3, command=lambda i=i: self._submaster_click(i),
                            bg='#5a3a7a', fg='white', font=('Arial', 8, 'bold'),
                            relief=tk.FLAT, cursor='hand2', width=11)
            btn.pack(side=tk.LEFT, padx=(4, 2))
            sc = tk.Scale(ctrl3, from_=0, to=100, orient=tk.HORIZONTAL,
                          showvalue=True, length=120,
                          command=lambda v, i=i: self._on_sub_slider(i, v),
                          bg='#111122', fg='#ccccee', troughcolor='#2c2c3e',
                          highlightthickness=0, sliderlength=26, width=12)
            sc.pack(side=tk.LEFT, padx=(0, 6))
            self._sub_btns.append(btn)
            self._sub_scales.append(sc)

        # v5 — 4 teclas tipo GrandMA: <  H(Highlight)  S(Solo)  >
        ttk.Separator(ctrl3, orient=tk.VERTICAL).pack(side=tk.LEFT,
                                                      fill=tk.Y, padx=6)

        def _hs_btn(txt, cmd, bg='#33415c'):
            return tk.Button(ctrl3, text=txt, command=cmd, bg=bg, fg='white',
                             font=('Arial', 11, 'bold'), relief=tk.FLAT,
                             width=3, pady=4, cursor='hand2')

        _hs_btn("<", lambda: self._select_step(-1)).pack(side=tk.LEFT, padx=1)
        self._hl_btn = _hs_btn("H", self._toggle_highlight)
        self._hl_btn.pack(side=tk.LEFT, padx=1)
        self._solo_btn = _hs_btn("S", self._toggle_solo)
        self._solo_btn.pack(side=tk.LEFT, padx=1)
        # R — renumerador: na vista mesa renumera o canal seleccionado;
        # na vista DMX faz a renumeração INVERSA (endereço → canal)
        _hs_btn("R", self._r_key, bg='#c0392b').pack(side=tk.LEFT, padx=1)
        _hs_btn(">", lambda: self._select_step(+1)).pack(side=tk.LEFT, padx=1)
        # v6 — DMX: alterna a grelha entre canais da mesa e monitor da saída
        # DMX. Roxo; vermelho quando activo.
        self._dmx_btn = _hs_btn("DMX", self._toggle_dmx_view, bg='#7a3fa0')
        self._dmx_btn.pack(side=tk.LEFT, padx=(6, 1))
        # v6.2 — GDTF saiu da página principal: importa-se agora DENTRO do
        # «Repetir Aparelho» (Renumerador → Repetir Aparelho → Importar GDTF).
        # (v5: a etiqueta de "X canais seleccionados" foi retirada — era
        #  redundante; a grelha já mostra a selecção a amarelo.)

        # (v4.9: os grupos passaram para baixo, junto aos retratos)
        cf = ttk.Frame(parent)
        cf.pack(fill=tk.BOTH, expand=True)
        self._chan_cf = cf

        # ── vista MESA (canais da mesa) ──
        self._mesa_view = ttk.Frame(cf)
        self._canvas = tk.Canvas(self._mesa_view, bg='#0d0d1a',
                                 highlightthickness=0)
        hsc = ttk.Scrollbar(self._mesa_view, orient=tk.HORIZONTAL,
                            command=self._canvas.xview)
        vsc = ttk.Scrollbar(self._mesa_view, orient=tk.VERTICAL,
                            command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=hsc.set, yscrollcommand=vsc.set)
        hsc.pack(side=tk.BOTTOM, fill=tk.X)
        vsc.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self._canvas.bind('<Configure>', lambda e: self._draw_channels())
        # botão esquerdo: clique = 1 canal; arrastar = rectângulo (estilo Excel)
        self._canvas.bind('<Button-1>', self._rb_start)
        self._canvas.bind('<B1-Motion>', self._rb_motion)
        self._canvas.bind('<ButtonRelease-1>', self._rb_end)
        # botão direito: selecciona como o esquerdo (clique = 1 canal, arrastar
        # = rectângulo) E, mantido + roda do rato, sobe/desce o nível dos canais
        # SELECCIONADOS (um ou vários), cada um no seu modo (±1 % ou ±1)
        self._canvas.bind('<Button-3>', self._rb3_press)
        self._canvas.bind('<B3-Motion>', self._rb3_motion)
        self._canvas.bind('<ButtonRelease-3>', self._rb3_release)
        self._mesa_view.pack(fill=tk.BOTH, expand=True)   # arranca em MESA

        self._cells = {}    # ch -> (x, y, w, h)
        self._rb_origin = None    # origem do rectângulo de selecção
        self._rb3_active = False  # botão direito mantido (roda = nível dos selec.)
        # v4 — caches do redesenho parcial da grelha
        self._grid_layout = None  # (cols, NUM_CHANNELS) da última construção
        self._grid_items = {}     # ch -> ids dos items de canvas da célula
        self._grid_state = {}     # ch -> tuplo do último estado visual

        # ── vista DMX (monitor da saída; fundo preto, 512 endereços) ──
        self._dmx_view = ttk.Frame(cf)
        bar = ttk.Frame(self._dmx_view)
        bar.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(bar, text="Saída DMX — Universo",
                  font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(2, 4))
        tk.Button(bar, text="◀", command=lambda: self._dmx_step_univ(-1),
                  bg='#33415c', fg='white', relief=tk.FLAT, width=2,
                  cursor='hand2').pack(side=tk.LEFT)
        self._dmx_univ_lbl = tk.Label(bar, text="1", bg='#111122',
                                      fg='#e8d44d', font=('Arial', 11, 'bold'),
                                      width=4)
        self._dmx_univ_lbl.pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="▶", command=lambda: self._dmx_step_univ(+1),
                  bg='#33415c', fg='white', relief=tk.FLAT, width=2,
                  cursor='hand2').pack(side=tk.LEFT)
        ttk.Label(bar, text="  (R com 1 endereço selec. = renumerar inverso)",
                  foreground='#666688').pack(side=tk.LEFT, padx=6)
        self._dmx_canvas = tk.Canvas(self._dmx_view, bg='#000000',
                                     highlightthickness=0)
        self._dmx_canvas.pack(fill=tk.BOTH, expand=True)
        self._dmx_canvas.bind('<Configure>', lambda e: self._draw_dmx())
        self._dmx_canvas.bind('<Button-1>', self._dmx_click)
        self._dmx_cells = {}       # addr -> ids dos items
        self._dmx_state = {}       # addr -> tuplo do último estado
        self._dmx_layout = None    # cols da última construção

    # v4 — grelha em duas fases: _build_grid cria os items de canvas uma vez
    # (só quando a geometria muda); _update_grid actualiza por itemconfig as
    # células cujo estado visual mudou. Elimina o delete('all') + recriar
    # ~600 items a cada frame da v3 — menos CPU e zero flicker.
    CELL_W, CELL_H, CELL_PAD = 72, 62, 4
    # v6.2: fundo dos painéis de grupo FX (Consola 2). ON = grupo seleccionado.
    FX_GRP_OFF = '#2c2c44'
    FX_GRP_ON  = '#e67e22'        # laranja vivo (distinto dos estados dos botões)

    def _draw_channels(self):
        # v5: mantém o engine a par da selecção (Highlight/Solo agem sobre
        # ela). frozenset → troca de referência atómica para a thread do engine.
        self.engine.hs_channels = frozenset(self._selected)
        canvas = self._canvas
        cw = canvas.winfo_width() or 900
        cols = max(1, cw // (self.CELL_W + self.CELL_PAD))
        layout = (cols, NUM_CHANNELS)
        if layout != self._grid_layout:
            self._grid_layout = layout
            self._build_grid(cols)
        self._update_grid()
        self._sync_console_selection()

    def _sync_console_selection(self):
        """v6.2 — espelha na consola física a selecção feita com o rato na app.
        Ponto único: chamado por _draw_channels(), por isso cobre TODAS as
        formas de seleccionar (clique, rectângulo, < >, TODOS, expressão…).
          · 1 canal seleccionado  → /channel/selected N  (consola salta p/ N)
          · 0 canais              → /channel/selected 0  (consola fica LIVRE)
          · vários canais         → não mexe na consola (é mono-canal)
        Só envia quando MUDA (anti-eco): a selecção vinda da consola já passa
        por _console_select, que actualiza _console_sel_sent e não reenvia.
        Depois de apontar a consola, mexer nela faz a app SEGUIR a selecção
        (a consola envia /channel/select → _console_select)."""
        n = len(self._selected)
        if n == 1:
            sel = next(iter(self._selected))
        elif n == 0:
            sel = 0
        else:
            return                      # multi-selecção: a consola não a mostra
        if sel == self._console_sel_sent:
            return
        self._console_sel_sent = sel
        self._send_console('/channel/selected', int(sel))
        if sel:                         # manda o nível actual p/ o OLED acertar
            self._push_channel_level(sel)

    def _build_grid(self, cols):
        """Reconstrói todos os items de canvas (ordem de criação = z-order:
        halo, célula, barra, textos — os textos ficam por cima da barra)."""
        canvas = self._canvas
        canvas.delete('all')
        self._grid_items = {}
        self._grid_state = {}
        self._cells = {}
        W, H, PAD = self.CELL_W, self.CELL_H, self.CELL_PAD
        row = col = 0
        for ch in range(1, NUM_CHANNELS + 1):
            x = col * (W + PAD) + PAD
            y = row * (H + PAD) + PAD
            halo_id = canvas.create_rectangle(
                x - 2, y - 2, x + W + 2, y + H + 2, outline='', width=2)
            rect_id = canvas.create_rectangle(
                x, y, x + W, y + H, fill='#16162a', outline='#2c2c3e')
            bar_id = canvas.create_rectangle(
                x + 4, y + H - 6, x + W - 4, y + H - 6,
                fill='', outline='', state='hidden')
            name_id = canvas.create_text(
                x + W // 2, y + 7, text='', fill='#ffffff',
                font=('Arial', 8, 'bold'))
            num_id = canvas.create_text(
                x + W // 2, y + H // 2 - 8, text=str(ch), fill='#f0d840',
                font=('Arial', 13, 'bold'))
            val_id = canvas.create_text(
                x + W // 2, y + H // 2 + 11, text='', fill='#ffffff',
                font=('Arial', 11, 'bold'))
            self._grid_items[ch] = (halo_id, rect_id, bar_id,
                                    name_id, num_id, val_id, x, y)
            self._cells[ch] = (x, y, W, H)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        total_h = (row + (1 if col > 0 else 0)) * (H + PAD) + PAD
        total_w = cols * (W + PAD) + PAD
        canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def _update_grid(self):
        """Actualiza apenas as células cujo estado visual mudou desde o
        último frame. Cores idênticas às da v3."""
        canvas = self._canvas
        W, H = self.CELL_W, self.CELL_H
        fxm = self.engine.fx_levels           # v5: canais comandados por FX
        # v5 — Highlight/Solo activos (com selecção): a grelha reflecte-os
        hs = ((self.engine.highlight or self.engine.solo)
              and bool(self._selected))
        # v6.2 — Solo por alias: alcunhas (>0) da selecção; os pct desses
        # aliases não são apagados no preview (igual ao _flush_dmx da engine).
        solo_aliases = frozenset()
        if self.engine.solo and self._selected:
            solo_aliases = frozenset(
                a for a in (int(self.engine.patch.get(c).get('alcunha') or 0)
                            for c in self._selected) if a)
        din_driven = self._din_driven if self._dmx_in is not None else ()  # v6.4
        for ch, (halo_id, rect_id, bar_id, name_id, num_id, val_id, x, y) \
                in self._grid_items.items():
            e = self.engine.patch.get(ch)
            # nível visível = HTP entre o playback/programador e os submasters
            play = self.engine.output[ch]
            prog = self.engine.programmer[ch] is not None
            # v5: FX em HTP por cima do playback, abaixo do programador
            # (correcção do autor 2026-06-13 — ver _flush_dmx)
            fxv = fxm.get(ch) if (fxm and not prog) else None
            base = play
            fx_dom = False
            if fxv is not None and fxv > base:
                base = fxv
                fx_dom = True              # o FX é que está a mandar na célula
            sub = self.engine.submaster_contribution(ch)
            lvl = max(base, sub)
            selected = ch in self._selected
            # v6.2 — canal destacado pelo Highlight (fundo amarelo)
            highlighted = self.engine.highlight and selected
            # v5 — Highlight/Solo: a grelha reflecte o que sai por DMX
            if hs:
                if self.engine.highlight and selected:
                    lvl = float(self.engine.highlight_level)   # v6.2: ajustavel
                if (self.engine.solo and not selected
                        and e.get('display', 'pct') == 'pct'
                        and (int(e.get('alcunha') or 0) not in solo_aliases)):
                    lvl = 0.0
            lvl_i = int(round(lvl))
            # passivo = canal sem ordem activa (no seu valor de defeito)
            passive = not self.engine.active[ch]
            # v6.2: canal a MOVER-SE numa transição → dígitos brancos enquanto
            # muda; ao chegar ao fim do fade volta à cor de estado normal.
            moving = (self.engine.fading and
                      self.engine.fade_start[ch] != self.engine.fade_target[ch])
            if sub > base and sub > 0:
                fx_dom = False             # submaster ainda mais alto
            sub_dom = sub > base and sub > 0      # luz dominada por submaster
            curva = e.get('curva', CURVE_LINEAR)
            halo = e.get('halo')
            name = (e.get('name') or '')[:6]
            alc = e.get('alcunha') or 0
            display = e.get('display')

            # v6.3.3 — canal marcado na criação/edição de uma PARTE
            parte_m = ch in self._parte_canais
            # v6.4 — canal conduzido AO VIVO pelo DMX-In (cor distinta)
            din_ch = ch in din_driven
            state = (lvl_i, prog, selected, passive, sub_dom, fx_dom, curva,
                     halo, name, alc, display, highlighted, moving, parte_m,
                     din_ch)
            if self._grid_state.get(ch) == state:
                continue                          # célula sem alterações
            self._grid_state[ch] = state

            is_ligado = (curva == CURVE_LIGADO)
            is_rele   = (curva == CURVE_RELE)

            # fundo / contorno
            if is_ligado:                           # canal "L" sempre ligado
                fill = '#8b1a1a'
                outline = '#e8d44d' if selected else '#e74c3c'
            elif is_rele:                           # canal "Rele" - threshold 10
                fill = '#8a5a14'
                outline = '#e8d44d' if selected else '#e67e22'
            elif prog:
                if din_ch:                  # v6.4 — DMX-In: ROSA/magenta
                    # distinto do vermelho da PARTE (#b03a3a), do azul do
                    # programador, do laranja FX e do violeta submaster
                    fill = '#7d1f4a'
                    outline = '#e8d44d' if selected else '#ff6ba6'
                else:
                    fill = '#1a3a5c'
                    outline = '#e8d44d' if selected else '#5dade2'
            elif fx_dom:                            # canal de FX (laranja)
                o = int(60 + lvl_i / 255 * 160)
                fill = f'#{o:02x}{int(o * 0.55):02x}00'
                outline = '#e8d44d' if selected else '#e67e22'
            elif sub_dom:                           # luz de submaster (violeta)
                v = int(50 + lvl_i / 255 * 130)
                fill = f'#{v // 3:02x}00{v:02x}'
                outline = '#e8d44d' if selected else '#9b6dd6'
            elif not passive:                       # valor activo (verde)
                g = int(60 + lvl_i / 255 * 150)
                fill = f'#00{g:02x}44'
                outline = '#e8d44d' if selected else '#2ecc71'
            else:                                   # valor passivo (escuro)
                fill = '#16162a'
                outline = '#e8d44d' if selected else '#2c2c3e'
            # v6.2 — Highlight: fundo AMARELO no(s) canal(is) destacado(s)
            if highlighted:
                fill = '#e8d44d'
                outline = '#fff4b0'
            # v6.3.3 — PARTES: canal marcado fica vermelho (não muito
            # escuro) enquanto se cria/edita a parte
            if parte_m:
                fill = '#b03a3a'
                outline = '#ff9090'
            canvas.itemconfig(rect_id, fill=fill, outline=outline,
                              width=2 if selected else 1)

            # halo de grupo — moldura de cor à volta da célula
            canvas.itemconfig(
                halo_id,
                outline=HALO_COLORS[halo] if halo in HALO_COLORS else '')

            # barra de nível
            bar_h = int(lvl_i / 255 * (H - 22))
            if bar_h > 0:
                if highlighted:
                    colour = '#d4c020'              # Highlight — barra amarela
                elif prog:
                    colour = '#3498db'
                elif fx_dom:
                    colour = '#e67e22'              # FX — laranja
                elif sub_dom:
                    colour = '#9b6dd6'              # submaster — violeta
                elif passive:
                    colour = '#33384a'              # passivo — escuro
                else:
                    colour = '#2ecc71'              # activo — verde
                canvas.coords(bar_id, x + 4, y + H - 6 - bar_h,
                              x + W - 4, y + H - 6)
                canvas.itemconfig(bar_id, fill=colour, state='normal')
            else:
                canvas.itemconfig(bar_id, state='hidden')

            # nome (topo) + número do canal OU alcunha (centro). v6.2: quando
            # há alcunha, o número fica rosa muito claro (quase branco) p/ se
            # distinguir do nº de canal normal (âmbar).
            canvas.itemconfig(name_id, text=name)
            canvas.itemconfig(num_id, text=str(alc) if alc else str(ch),
                              fill='#ff9ec9' if alc else '#f0d840')

            # nível — % ou 0-255 conforme patch; "L" grande se curva 'ligado'
            if is_ligado:
                canvas.itemconfig(val_id, text=T('grid.on_letter'),
                                  fill='#ffffff', font=('Arial', 22, 'bold'))
            else:
                if display == 'dec':
                    txt = str(lvl_i) if lvl_i > 0 else '—'
                else:
                    pct = round(lvl_i / 255 * 100)
                    txt = f'{pct}%' if pct > 0 else '—'
                if highlighted:
                    colour = '#1a1a1a'                  # Highlight — texto escuro
                elif moving:
                    colour = '#ffffff'                  # v6.2: a mover → branco
                elif din_ch:
                    colour = '#ffc0dc'                  # v6.4 — DMX-In: rosa claro
                elif prog:
                    colour = '#ffffff'                  # programmer — branco
                elif fx_dom:
                    colour = '#ffd9a8'                  # FX — laranja claro
                elif sub_dom:
                    colour = '#c9b3e8'                  # submaster — violeta
                elif passive:
                    colour = '#5b6072'                  # passivo — escuro
                else:
                    colour = '#ffffff'                  # activo
                canvas.itemconfig(val_id, text=txt, fill=colour,
                                  font=('Arial', 11, 'bold'))

    # ── v6: vista DMX (monitor da saída) ──────
    DMX_CW, DMX_CH, DMX_PAD = 30, 18, 1

    def _toggle_dmx_view(self):
        """Alterna a grelha entre os canais da mesa e o monitor da saída
        DMX (512 endereços de um universo). DMX roxo / vermelho activo."""
        if self._chan_view == 'mesa':
            self._chan_view = 'dmx'
            outs = self.engine.out_universes()
            if self._dmx_univ not in outs and outs:
                self._dmx_univ = outs[0]
            self._mesa_view.pack_forget()
            self._dmx_view.pack(fill=tk.BOTH, expand=True)
            self._dmx_layout = None
            self._dmx_state = {}
            self._dmx_btn.config(bg='#c0392b')
            self._dmx_univ_lbl.config(text=str(self._dmx_univ))
            self._push_page()            # v6.2: consola segue a página DMX
            self._draw_dmx()
        else:
            self._chan_view = 'mesa'
            # sair da vista DMX desliga o teste de saída (deixa de forçar)
            self._dmx_highlight = False
            self._dmx_solo = False
            self._push_dmx_force()
            self._dmx_view.pack_forget()
            self._mesa_view.pack(fill=tk.BOTH, expand=True)
            self._dmx_btn.config(bg='#7a3fa0')
            self._push_page()            # v6.2: consola volta à página mesa
            self._update_hs_btns()
            self._draw_channels()

    def _dmx_step_univ(self, d):
        self._dmx_univ = max(1, min(63999, self._dmx_univ + d))
        self._dmx_univ_lbl.config(text=str(self._dmx_univ))
        self._dmx_selected.clear()
        self._dmx_state = {}
        self._push_page()                # v6.2: consola actualiza o universo
        self._draw_dmx()

    def _draw_dmx(self):
        cv = self._dmx_canvas
        w = cv.winfo_width() or 800
        cols = max(8, w // (self.DMX_CW + self.DMX_PAD))
        if (cols,) != self._dmx_layout:
            self._dmx_layout = (cols,)
            self._build_dmx_grid(cols)
        self._update_dmx_grid()

    def _build_dmx_grid(self, cols):
        cv = self._dmx_canvas
        cv.delete('all')
        self._dmx_cells = {}
        self._dmx_state = {}
        CW, CH, PAD = self.DMX_CW, self.DMX_CH, self.DMX_PAD
        row = col = 0
        for a in range(1, 513):
            x = col * (CW + PAD) + PAD
            y = row * (CH + PAD) + PAD
            rect = cv.create_rectangle(x, y, x + CW, y + CH,
                                       fill='#0a0a0a', outline='#222222')
            bar = cv.create_rectangle(x + 1, y + CH - 1, x + CW - 1, y + CH - 1,
                                      fill='', outline='', state='hidden')
            num = cv.create_text(x + CW // 2, y + CH // 2, text=str(a),
                                 fill='#555555', font=('Arial', 8))
            self._dmx_cells[a] = (rect, bar, num, x, y)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        total_h = (row + (1 if col > 0 else 0)) * (CH + PAD) + PAD
        cv.configure(scrollregion=(0, 0, cols * (CW + PAD) + PAD, total_h))

    def _update_dmx_grid(self):
        cv = self._dmx_canvas
        CW, CH = self.DMX_CW, self.DMX_CH
        snap = self.engine.dmx_snapshot(self._dmx_univ)
        for a, (rect, bar, num, x, y) in self._dmx_cells.items():
            v = snap[a - 1]
            sel = a in self._dmx_selected
            st = (v, sel)
            if self._dmx_state.get(a) == st:
                continue
            self._dmx_state[a] = st
            if v > 0:
                g = int(40 + v / 255 * 150)
                cv.itemconfig(rect, fill=f'#00{g // 4:02x}10',
                              outline='#e8d44d' if sel else '#2ecc71')
                bar_h = int(v / 255 * (CH - 2))
                cv.coords(bar, x + 1, y + CH - 1 - bar_h, x + CW - 1, y + CH - 1)
                cv.itemconfig(bar, fill='#2ecc71', state='normal')
                cv.itemconfig(num, fill='#cfe8cf')
            else:
                cv.itemconfig(rect, fill='#0a0a0a',
                              outline='#e8d44d' if sel else '#222222')
                cv.itemconfig(bar, state='hidden')
                cv.itemconfig(num, fill='#aa9944' if sel else '#555555')

    def _dmx_click(self, event):
        x = self._dmx_canvas.canvasx(event.x)
        y = self._dmx_canvas.canvasy(event.y)
        CW, CH = self.DMX_CW, self.DMX_CH
        for a, (rect, bar, num, cx, cy) in self._dmx_cells.items():
            if cx <= x <= cx + CW and cy <= y <= cy + CH:
                self._dmx_selected = {a}
                self._dmx_state = {}     # força redesenho da selecção
                self._push_dmx_force()   # Highlight segue o clique
                # v6.2: a consola salta o cursor DMX p/ o endereço clicado
                # (rato salta endereços, sem rodar o encoder desde 1)
                self._send_console('/dmx/browse', int(a))
                self._draw_dmx()
                return

    # ── selecção com o botão esquerdo (clique ou rectângulo) ──
    def _rb_start(self, event):
        self._rb_origin = (self._canvas.canvasx(event.x),
                           self._canvas.canvasy(event.y))
        self._canvas.delete('rubberband')

    def _rb_motion(self, event):
        if self._rb_origin is None:
            return
        x0, y0 = self._rb_origin
        x1 = self._canvas.canvasx(event.x)
        y1 = self._canvas.canvasy(event.y)
        self._canvas.delete('rubberband')
        self._canvas.create_rectangle(x0, y0, x1, y1, outline='#e8d44d',
                                      width=1, dash=(3, 2), tags='rubberband')

    def _rb_end(self, event):
        if self._rb_origin is None:
            return
        x0, y0 = self._rb_origin
        x1 = self._canvas.canvasx(event.x)
        y1 = self._canvas.canvasy(event.y)
        self._rb_origin = None
        self._canvas.delete('rubberband')
        rx0, rx1 = min(x0, x1), max(x0, x1)
        ry0, ry1 = min(y0, y1), max(y0, y1)
        sel = set()
        for ch, (cx, cy, cw, ch_h) in self._cells.items():
            if (cx <= rx1 and cx + cw >= rx0
                    and cy <= ry1 and cy + ch_h >= ry0):
                sel.add(ch)
        # v6.3.3 — a editar uma PARTE: o clique tira/põe canais na parte
        # (vermelho), não mexe na selecção normal
        if self._parte_mod is not None:
            for ch in sel:
                if ch in self._parte_canais:
                    self._parte_canais.discard(ch)   # volta à parte 1
                else:
                    self._parte_canais.add(ch)
            self._draw_channels()
            return
        if sel:
            # aditiva — EXCEPTO se acabamos de mexer num nivel: nesse caso
            # esta seleccao limpa a anterior antes de juntar (e desbloqueia).
            # v6.2: com Solo OU Highlight ligado, um clique SIMPLES (1 canal)
            # isola — limpa a seleccao para focar só este (no Highlight permite
            # SALTAR p/ qualquer canal com o rato, ex.: 300, sem rodar desde 1;
            # a consola segue via /channel/selected). Vários = arrasto (len>1).
            if self._sel_locked or ((self.engine.solo or self.engine.highlight)
                                    and len(sel) == 1):
                self._selected.clear()
                self._sel_locked = False
            self._selected |= sel
            self._step_group = None       # nova selecção manual sai do grupo
            if len(sel) == 1:
                ch = next(iter(sel))
                self._level_var.set(str(int(round(self.engine.output[ch]))))
            self._update_sel_label()
        self._draw_channels()

    def _cell_at_canvas(self, event):
        """Canal cuja célula está sob o evento do canvas (ou None)."""
        cx = self._canvas.canvasx(event.x)
        cy = self._canvas.canvasy(event.y)
        for ch, (x, y, w, h) in self._cells.items():
            if x <= cx <= x + w and y <= cy <= y + h:
                return ch
        return None

    def _rb3_press(self, event):
        # AO CONTRÁRIO do esquerdo, o direito selecciona JÁ no clique (mais
        # rápido para depois subir/descer com a roda). Arma também o gesto da
        # roda e o possível arrasto-rectângulo.
        self._rb3_active = True
        self._rb3_used = False        # roda usada durante este gesto?
        self._rb3_moved = False       # houve arrasto?
        self._rb_start(event)
        ch = self._cell_at_canvas(event)
        # v6.3.3 — a editar uma PARTE: o clique direito também tira/põe
        if ch is not None and self._parte_mod is not None:
            if ch in self._parte_canais:
                self._parte_canais.discard(ch)
            else:
                self._parte_canais.add(ch)
            self._draw_channels()
            return 'break'
        if ch is not None:
            # aditivo como o esquerdo: vai juntando canais — EXCEPTO logo a
            # seguir a uma alteração de nível (_sel_locked), em que este clique
            # limpa a selecção anterior antes de juntar.
            # v6.2: com Solo OU Highlight ligado, o clique limpa (isola/salta).
            # Para vários usa-se o arrasto com o botao direito.
            if self._sel_locked or self.engine.solo or self.engine.highlight:
                self._selected.clear()
                self._sel_locked = False
            self._selected.add(ch)
            self._step_group = None
            self._level_var.set(str(int(round(self.engine.output[ch]))))
            self._update_sel_label()
            self._draw_channels()
        return 'break'

    def _rb3_motion(self, event):
        self._rb3_moved = True
        self._rb_motion(event)

    def _rb3_release(self, event):
        self._rb3_active = False
        # arrasto → aplica o rectângulo (junta à selecção do clique); senão a
        # selecção já foi feita no press (ou a roda ajustou e não se mexe nela)
        if self._rb3_moved and not self._rb3_used:
            self._rb_end(event)
        else:
            self._rb_origin = None
            self._canvas.delete('rubberband')

    def _apply_selection(self):
        # aditiva — EXCEPTO se acabamos de mexer num nivel (igual a _rb_release)
        if self._sel_locked:
            self._selected.clear()
            self._sel_locked = False
        self._selected |= parse_channel_expr(self._sel_var.get(), NUM_CHANNELS)
        self._step_group = None           # nova selecção manual sai do grupo
        self._update_sel_label()
        self._draw_channels()

    def _clear_selection(self):
        self._selected = set()
        self._step_group = None       # LIMPA também sai do grupo do < / >
        self._sel_var.set("")
        self._sel_locked = False
        self._update_sel_label()
        self._draw_channels()

    # ── v6.2: LIMPA / LIBERTA com 2-toque (janela folgada) ──────
    _MULTI_PRESS_S = 1.2          # tempo p/ o 2.º toque contar como "duplo"

    # ── CLEAR / RELEASE em PASSOS (v6.3) — reutilizados pelos botões da mesa
    #    (com 2-toque temporizado) e pelo OSC (passos directos, fiáveis) ──
    def _clear_step1(self):
        """CLEAR 1.º: desselecciona (o azul mantém-se)."""
        self._clear_selection()

    def _din_exc(self):
        """v6.4 — canais a NÃO libertar: os conduzidos pelo DMX-In (voltam
        logo na tick seguinte). Os canais que o utilizador subiu à MÃO
        (fora do DMX-In) libertam-se normalmente."""
        return set(self._din_driven) if self._dmx_in is not None else None

    def _clear_step2(self):
        """CLEAR 2.º: apaga o programador (azul), com fade."""
        self._capture_undo()
        self.engine.clear_programmer(self._release_time, exclude=self._din_exc())
        self._refresh()

    def _release_step1(self):
        """RELEASE 1.º: apaga o azul E desselecciona."""
        self._capture_undo()
        self.engine.clear_programmer(self._release_time, exclude=self._din_exc())
        self._selected = set()
        self._sel_locked = False
        self._refresh()

    def _release_step2(self):
        """RELEASE 2.º: deita o OUTPUT abaixo (cue VERDE + FX LARANJA) ao
        defeito/zero e desliga os FX; os SUBMASTERS mantêm-se."""
        self._capture_undo()
        self.engine.fx_deactivate_all()
        self.engine.release_output(pct_only=False, duration=self._release_time,
                                   exclude=self._din_exc())
        self._refresh()

    def _liberta_total(self):
        """v6.4 — LIBERTAÇÃO TOTAL num só gesto (opção «Liberta» do menu,
        onde não há 2-toque): programador (azul) + output (memórias VERDES
        + FX) ao valor de DEFEITO do patch; FX off; desselecciona. Só fica
        o que entra pelo DMX-In (se em escuta). Equivale a carregar 2× na
        tecla LIBERTA."""
        self._capture_undo()
        self.engine.fx_deactivate_all()
        self.engine.release_output(pct_only=False, duration=self._release_time,
                                   exclude=self._din_exc())
        self._selected = set()
        self._sel_locked = False
        self._refresh()

    def _on_clear(self):
        """LIMPA (botão da mesa): 1 toque desselecciona; 2.º toque (até 1.2 s)
        apaga o programador (azul)."""
        now = time.time()
        if now - self._clear_last < self._MULTI_PRESS_S:
            self._clear_step2()      # v6.4 — liberta o manual; DMX-In fica
        else:
            self._clear_step1()      # desseleccionar
        self._clear_last = now

    def _on_liberta(self):
        """RELEASE (LIBERTA, botão da mesa) — distinto do CLEAR:
          1.º toque: apaga o azul e DESSELECCIONA.
          2.º toque (até 1.2 s): deita o OUTPUT abaixo (cue verde + FX laranja),
            FX off, submasters mantêm-se.
        v6.4: os canais conduzidos pelo DMX-In NÃO se libertam (voltam
        logo); os que o utilizador subiu à mão libertam-se normalmente."""
        now = time.time()
        if now - self._liberta_last < self._MULTI_PRESS_S:
            self._release_step2()
        else:
            self._release_step1()
        self._liberta_last = now

    def _toggle_midi_active(self):
        """Liga/desliga o MIDI IN e MIDI OUT temporariamente sem tocar nas portas."""
        self._midi_active = not self._midi_active
        self._refresh_midi_toggle_btn()
        estado = T('btn.midi_on') if self._midi_active else T('btn.midi_off')
        self._status_var.set(f"MIDI → {estado}")

    # ── MIDI: atraso em curso → tecla MIDI ON cintila branco↔amarelo ──
    def _midi_delayed(self, delay_s, fn):
        """Agenda fn após delay_s s, marcando um efeito MIDI EM CURSO. Enquanto
        houver atrasos pendentes, a tecla MIDI ON cintila (branco↔amarelo)."""
        self._midi_pending += 1
        self._midi_start_blink()

        def _run():
            try:
                fn()
            finally:
                self._midi_pending = max(0, self._midi_pending - 1)
                if self._midi_pending == 0:
                    self._midi_stop_blink()
        self.root.after(int(delay_s * 1000), _run)

    def _midi_start_blink(self):
        if self._midi_blink_on:
            return
        self._midi_blink_on = True
        self._midi_blink_state = False
        self._midi_blink_tick()

    def _midi_blink_tick(self):
        if not self._midi_blink_on or self._midi_pending <= 0:
            self._midi_stop_blink()
            return
        self._midi_blink_state = not self._midi_blink_state
        col = '#f1c40f' if self._midi_blink_state else 'white'   # amarelo↔branco
        try:
            if self._midi_active and self._midi_toggle_btn.winfo_exists():
                self._midi_toggle_btn.config(fg=col)
        except Exception:
            pass
        self.root.after(300, self._midi_blink_tick)

    def _midi_stop_blink(self):
        self._midi_blink_on = False
        try:
            self._refresh_midi_toggle_btn()   # restaura o aspecto normal
        except Exception:
            pass

    def _refresh_midi_toggle_btn(self):
        """Actualiza cor e texto do botão MIDI ON/OFF."""
        if not HAS_MIDI:
            self._midi_toggle_btn.config(text='MIDI —', bg='#333344',
                                         state=tk.DISABLED)
            return
        if self._midi_active:
            # MIDI ON — tecla ciano (escuro), texto branco
            self._midi_toggle_btn.config(text=T('btn.midi_on'), fg='white',
                                         bg='#0a8f8f', state=tk.NORMAL)
        else:
            # MIDI OFF — tecla violeta (escuro), texto branco
            self._midi_toggle_btn.config(text=T('btn.midi_off'), fg='white',
                                         bg='#5f3a9c', state=tk.NORMAL)

    def _toggle_intensity_mode(self):
        """v6.2: alterna o modelo da cuelist (cue_only ↔ tracking) — atalho do
        tab Configurações, na barra do XF. Reflecte já na cue actual."""
        eng = self.engine
        eng.intensity_mode = ('tracking' if eng.intensity_mode == 'cue_only'
                              else 'cue_only')
        idx = eng.current_cue_idx
        if 0 <= idx < len(eng.cues):
            eng.load_cue_for_edit(idx)
        self._mark_dirty()
        self._refresh_im_btn()
        self._refresh()

    def _refresh_im_btn(self):
        """Cor/texto do botão do modelo da cuelist (cue_only vs tracking)."""
        if not hasattr(self, '_im_btn'):
            return
        if self.engine.intensity_mode == 'cue_only':
            self._im_btn.config(text=T('btn.im_cueonly'), bg='#e67e22')
        else:
            self._im_btn.config(text=T('btn.im_tracking'), bg='#2980b9')

    def _todo(self):
        """Junta à selecção todos os canais activos (em modo percentual). Os
        canais em modo decimal (0-255) não são afectados pelo TODOS."""
        self._prog_checkpoint()       # marca p/ o Ctrl+Z poder voltar atrás
        for ch in range(1, NUM_CHANNELS + 1):
            if self.engine.patch.get(ch).get('display') == 'dec':
                continue
            if self.engine.active[ch]:
                self._selected.add(ch)
        self._update_sel_label()
        self._draw_channels()

    def _update_sel_label(self):
        # v5: etiqueta de selecção removida (redundante com a grelha).
        # Método mantido (chamado em vários sítios) — sem efeito.
        pass

    # ── teclas tipo GrandMA: < H S > ──────────
    def _select_one(self, ch):
        """Passa a selecção a ser SÓ o canal ch (usado pelo < / >)."""
        self._selected = {ch}
        self._sel_locked = False
        self._level_var.set(str(int(round(self.engine.output[ch]))))
        self._update_sel_label()
        self._draw_channels()

    def _select_step(self, d):
        """< / > : anda nos canais um a um (selecção única, em ciclo).

        · Selecção ÚNICA (ex: canal 78): vai para o canal ADJACENTE por
          número — > 79, < 77 (em ciclo 1..N).
        · GRUPO seleccionado (>1 canal): o 1.º < ou > ENTRA nele pelo canal
          mais baixo e passa a ciclar SÓ dentro desses canais — afinar um
          grupo de projectores um a um (pedido do autor).
        Na vista DMX, anda nos ENDEREÇOS DMX (1..512) — com o Highlight
        ligado, vai-se identificando a fixtura à medida que avança."""
        if self._chan_view == 'dmx':
            self._dmx_step(d)
            return
        sel = self._selected
        if len(sel) > 1:                      # entra no grupo pelo mais baixo
            self._step_group = sorted(c for c in sel
                                      if 1 <= c <= NUM_CHANNELS)
            if self._step_group:
                self._select_one(self._step_group[0])
            return
        cur = next(iter(sel)) if len(sel) == 1 else None
        # selecção única dentro do grupo memorizado → cicla no grupo
        if self._step_group and cur in self._step_group:
            g = self._step_group
            nxt = g[(g.index(cur) + d) % len(g)]
        elif cur is None:                     # nada seleccionado → arranca
            self._step_group = None
            nxt = 1 if d > 0 else NUM_CHANNELS
        else:                                 # canal adjacente por número
            self._step_group = None
            nxt = (cur - 1 + d) % NUM_CHANNELS + 1
        self._select_one(nxt)

    def _toggle_highlight(self):
        """H : MESA → a selecção de canais vai a 255 na saída. DMX → força
        o endereço DMX seleccionado a full, para IDENTIFICAR a fixtura no
        palco (anda com < / > para varrer)."""
        if self._chan_view == 'dmx':
            self._dmx_highlight = not self._dmx_highlight
            self._push_dmx_force()
        else:
            self.engine.highlight = not self.engine.highlight
            self._draw_channels()
        self._update_hs_btns()

    def _toggle_solo(self):
        """S : MESA → só a selecção fica acesa (dimmers). DMX → isola o
        universo: só os endereços forçados (Highlight) saem, o resto a 0."""
        if self._chan_view == 'dmx':
            self._dmx_solo = not self._dmx_solo
            self._push_dmx_force()
        else:
            self.engine.solo = not self.engine.solo
            self._draw_channels()
        self._update_hs_btns()

    def _push_dmx_force(self):
        """Empurra para o engine o teste de saída DMX conforme a vista, os
        modos H/S e a selecção de endereços."""
        if self._chan_view == 'dmx' and self._dmx_highlight:
            self.engine.dmx_force = frozenset(
                (self._dmx_univ, a) for a in self._dmx_selected)
        else:
            self.engine.dmx_force = frozenset()
        if self._chan_view == 'dmx' and self._dmx_solo:
            self.engine.dmx_solo = True
            self.engine.dmx_solo_univ = self._dmx_univ
        else:
            self.engine.dmx_solo = False
            self.engine.dmx_solo_univ = None

    def _dmx_step(self, d):
        """< / > na vista DMX: endereço DMX adjacente (1..512, em ciclo).
        Actualiza o teste de saída (Highlight segue o endereço)."""
        cur = (next(iter(self._dmx_selected))
               if len(self._dmx_selected) == 1 else None)
        if cur is None:
            nxt = 1 if d > 0 else 512
        else:
            nxt = (cur - 1 + d) % 512 + 1
        self._dmx_selected = {nxt}
        self._dmx_state = {}
        self._push_dmx_force()
        self._draw_dmx()

    def _r_key(self):
        """Tecla R: na vista MESA renumera o canal seleccionado; na vista
        DMX faz a renumeração INVERSA (endereço DMX → canal da mesa)."""
        if self._chan_view == 'dmx':
            self._open_reverse_patch()
        else:
            self._open_channel_patch()

    def _open_reverse_patch(self):
        """v6 — renumeração inversa: com UM endereço DMX seleccionado na
        vista DMX, pergunta que canal da mesa o controla e patcha-o (com a
        regra do endereço único). Vazio = tira o endereço do canal que o
        tinha."""
        if len(self._dmx_selected) != 1:
            messagebox.showinfo(T('m.rev_title'), T('m.rev_pick_one'))
            return
        addr = next(iter(self._dmx_selected))
        univ = self._dmx_univ
        # canal que actualmente controla este endereço (se houver)
        cur = None
        for ch in range(1, NUM_CHANNELS + 1):
            e = self.engine.patch.get(ch)
            if e.get('universe') == univ and (addr in e.get('addrs', [])
                                              or addr in e.get('fine', [])):
                cur = ch
                break
        dlg = ValueDialog(
            self.root, T('m.rev_title'),
            T('m.rev_prompt', univ=univ, addr=addr),
            '' if cur is None else str(cur))
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        txt = dlg.result.strip()
        if txt == '':
            if cur is not None:
                e = dict(self.engine.patch.get(cur))
                e['addrs'] = [a for a in e.get('addrs', []) if a != addr]
                e['fine'] = [a for a in e.get('fine', []) if a != addr]
                e['bit16'] = len(e['fine']) > 0
                self.engine.patch.set(cur, e)
            self._post_patch_change()
            return
        try:
            mch = int(txt)
        except ValueError:
            messagebox.showerror(T('m.rev_title'), T('m.rev_bad_channel'))
            return
        if not (1 <= mch <= NUM_CHANNELS):
            messagebox.showerror(T('m.rev_title'),
                                 T('m.rev_channel_range', max=NUM_CHANNELS))
            return
        e = dict(self.engine.patch.get(mch))
        if e.get('universe') != univ and (e.get('addrs') or e.get('fine')):
            # universo diferente → substitui (um canal só tem um universo)
            e['universe'] = univ
            e['addrs'] = [addr]
            e['fine'] = []
            e['bit16'] = False
        else:
            e['universe'] = univ
            if addr not in e.get('addrs', []):
                e['addrs'] = sorted(e.get('addrs', []) + [addr])
        self.engine.patch.set(mch, e)
        self.engine.patch.remove_addr_conflicts(mch)   # endereço único
        self._post_patch_change()

    def _post_patch_change(self):
        """Pós-edição de patch (inverso): alinha saída, defeitos, consola."""
        self.engine.sync_sacn_outputs()
        self.engine.apply_defaults_to_passive()
        self._refresh_status()
        self._push_all_channel_names()
        self._draw_dmx()
        self._refresh()

    def _open_channel_patch(self):
        """R — com 1 canal abre o renumerador completo desse canal; com VÁRIOS
        abre um diálogo para dar NOME / HALO / ALCUNHA comuns a todos."""
        n = len(self._selected)
        if n == 0:
            messagebox.showinfo(T('patch.warn_title'), T('m.cp_pick_one'))
            return
        if n > 1:
            self._multi_attr(sorted(self._selected))
            return
        ch = next(iter(self._selected))
        dlg = ChannelPatchDialog(self.root, self.engine, ch)
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        self._capture_undo()
        self.engine.patch.set(ch, dlg.result)
        # endereço DMX único: o(s) endereço(s) atribuídos a este canal saem
        # de qualquer outro canal que os tivesse (no mesmo universo)
        movidos = self.engine.patch.remove_addr_conflicts(ch)
        if movidos:
            nums = ", ".join(str(c) for c in sorted(movidos))
            messagebox.showinfo(T('patch.warn_title'),
                                T('m.cp_moved', nums=nums))
        # o patch mudou: alinha universos de saída + reaplica defeitos aos
        # passivos (ex.: defeito acabado de definir) + actualiza a consola
        self.engine.sync_sacn_outputs()
        self.engine.apply_defaults_to_passive()
        self._refresh_status()
        self._push_channel_name(ch)
        self._push_channel_alcunha(ch)
        self._push_channel_curva(ch)
        self._push_patched_channels()
        self._refresh()

    def _multi_attr(self, chs):
        """v6.2 — R com vários canais: nome/halo/alcunha comuns a todos. A
        alcunha incrementa por canal (ordem do nº do canal); «@» = a mesma."""
        dlg = MultiAttrDialog(self.root, len(chs))
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        r = dlg.result
        self._capture_undo()
        for i, ch in enumerate(chs):
            e = dict(self.engine.patch.get(ch))
            if 'name' in r:
                e['name'] = r['name']
            if 'halo' in r:
                e['halo'] = r['halo']
            if 'alc' in r:
                base, fixo = r['alc']
                # 0 (ou vazio) = LIMPA a alcunha em TODOS (volta ao nº do canal);
                # «@» = a mesma em todos; senão incrementa por canal.
                if base == 0 or fixo:
                    e['alcunha'] = base
                else:
                    e['alcunha'] = max(0, min(9999, base + i))
            self.engine.patch.set(ch, e)
        self.engine.sync_sacn_outputs()
        self.engine.apply_defaults_to_passive()
        self._refresh_status()
        self._push_all_channel_names()    # nomes/alcunhas/halo p/ a consola
        self._refresh()

    def _update_hs_btns(self):
        """Cor dos botões H/S conforme o modo (amarelo vivo = activo). Na
        vista DMX reflectem o teste de saída; na mesa, o H/S dos canais."""
        hl = (self._dmx_highlight if self._chan_view == 'dmx'
              else self.engine.highlight)
        so = (self._dmx_solo if self._chan_view == 'dmx'
              else self.engine.solo)
        if hasattr(self, '_hl_btn'):
            self._hl_btn.config(bg='#f1c40f' if hl else '#33415c',
                                fg='#222222' if hl else 'white')
        if hasattr(self, '_solo_btn'):
            self._solo_btn.config(bg='#e67e22' if so else '#33415c')

    def _set_level_from_entry(self):
        val = self._level_var.get().strip().rstrip('%')
        try:
            v = float(val)
            level = int(v * 2.55) if v <= 100 else int(v)
            self._set_level(level)
        except ValueError:
            pass

    def _apply_preset(self, idx):
        val = self._preset_vars[idx].get().strip().rstrip('%')
        try:
            v = float(val)
            level = int(v * 2.55) if v <= 100 else int(v)
            self._set_level(level)
        except ValueError:
            pass

    def _sync_preset(self, idx):
        """Mantém os pré-valores no motor (para serem guardados no show)."""
        self.engine.presets[idx - 1] = self._preset_vars[idx].get()

    def _set_level(self, level):
        if self._selected:
            self._prog_checkpoint()       # undo do gesto de programação
        for ch in self._selected:
            self.engine.set_channel(ch, level)
        if self._selected:
            self._level_var.set(str(level))
            # tranca a seleccao: a proxima accao de seleccionar limpa primeiro
            self._sel_locked = True

    def _adjust_level(self, delta):
        """Aumenta/diminui o nível dos canais seleccionados. O passo respeita o
        modo do canal: ±delta % se for percentual, ±delta (0-255) se decimal."""
        if self._selected:
            self._prog_checkpoint()       # undo do gesto de programação
            self._sel_locked = True
        for ch in self._selected:
            cur = self.engine.output[ch]
            if self.engine.patch.get(ch).get('display') == 'dec':
                new = max(0, min(255, round(cur) + delta))
            else:
                pct = round(cur / 255 * 100)
                new_pct = max(0, min(100, pct + delta))
                new = round(new_pct * 255 / 100)
            self.engine.set_channel(ch, new)

    def _blackout(self):
        """B.O. (Black Out) — toggle de emergencia. Zera o DMX que sai
        pelo sACN; o estado interno (output/programmer/cues) nao muda.
        Segunda pressao -> repoe o sinal."""
        self.engine.toggle_blackout()
        self._update_blackout_btn()

    def _update_blackout_btn(self):
        if hasattr(self, '_bo_btn'):
            # mantem SEMPRE a palavra "ESCURO"; so muda a cor.
            if self.engine.bo_active:
                self._bo_btn.config(bg='#ff0000')   # vermelho vivo = B.O. activo
            else:
                self._bo_btn.config(bg='#4a0000')   # vermelho muito escuro = pronto

    # ── cue panel ─────────────────────────────
    def _build_cue_panel(self, parent):
        # transport
        tf = ttk.Frame(parent, padding=6)
        tf.pack(fill=tk.X, pady=(0, 6))

        # v4.9: sem o prefixo "Memória:" — mais espaço para a deixa
        self._cue_now_var = tk.StringVar(value="—")
        ttk.Label(tf, textvariable=self._cue_now_var,
                  font=('Arial', 18, 'bold'), foreground='#e8d44d').pack(fill=tk.X)

        # marca de água do criador — fixa no canto superior direito (place).
        # criada/elevada no fim para ficar por cima de tudo (ver abaixo).
        self._wm_lbl = ttk.Label(tf, text="By Worm", foreground='#444444',
                                 font=('Arial', 30, 'italic', 'bold'))
        self._wm_lbl.place(relx=1.0, y=0, anchor='ne', x=-6)

        # v4.9: a próxima é indicada só pela seta (a cor já a distingue)
        self._cue_next_var = tk.StringVar(value="→ —")
        self._cue_next_lbl = ttk.Label(tf, textvariable=self._cue_next_var,
                                       font=('Arial', 16, 'bold'),
                                       foreground='#90ee90')
        self._cue_next_lbl.pack(fill=tk.X)

        btns = ttk.Frame(tf)
        btns.pack(fill=tk.X, pady=(6, 0))

        self._back_btn = tk.Button(btns, text=T('btn.goback'), command=self._back,
                                   bg='#2c3e50', fg='white', font=('Arial', 12, 'bold'),
                                   relief=tk.FLAT, width=12, pady=8, cursor='hand2')
        self._back_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._go_btn = tk.Button(btns, text=T('btn.go'), command=self._go,
                                 bg='#8b0000', fg='white', font=('Arial', 16, 'bold'),
                                 relief=tk.RAISED, width=10, pady=8, cursor='hand2')
        self._go_btn.pack(side=tk.LEFT)

        self._pause_btn = tk.Button(btns, text=T('btn.pause'), command=self._toggle_pause,
                                    bg='#8a6d3b', fg='white', font=('Arial', 12, 'bold'),
                                    relief=tk.FLAT, width=12, pady=8, cursor='hand2')
        self._pause_btn.pack(side=tk.LEFT, padx=(6, 0))

        self._soltar_btn = tk.Button(btns, text=T('btn.loopbreak'), command=self._soltar,
                                     bg='#5d6d7e', fg='white', font=('Arial', 12, 'bold'),
                                     relief=tk.FLAT, width=12, pady=8, cursor='hand2')
        self._soltar_btn.pack(side=tk.LEFT, padx=(6, 0))

        # barra de progresso da transição em curso
        prog = ttk.Frame(tf)
        prog.pack(fill=tk.X, pady=(6, 0))
        self._fade_lbl = ttk.Label(prog, text="—", width=6,
                                   foreground='#7f8c8d')
        self._fade_lbl.pack(side=tk.LEFT)
        # dois estilos: normal (manual) e violeta (transição AUTO)
        _st = ttk.Style()
        _st.configure('Fade.Horizontal.TProgressbar', background='#27ae60')
        _st.configure('Auto.Horizontal.TProgressbar', background='#9b30ff')
        # v6.3 — countdown do AUTO: barra laranja
        _st.configure('Count.Horizontal.TProgressbar', background='#e67e22')
        self._fade_bar = ttk.Progressbar(prog, mode='determinate', maximum=100,
                                         style='Fade.Horizontal.TProgressbar')
        self._fade_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # eleva a marca de água acima de todos os widgets do transporte
        self._wm_lbl.lift()

        # lista de memórias
        clf = ttk.Frame(parent, padding=6)
        clf.pack(fill=tk.BOTH, expand=True)

        # linha de cima — todos os botões de acção (coloridos)
        act = ttk.Frame(clf)
        act.pack(fill=tk.X, pady=(0, 2))
        # v6.2: fila do Comprar com a MESMA altura da fila de baixo (pady=4,
        # fonte 11) para alinharem.
        _AKW = dict(fg='white', font=('Arial', 11, 'bold'),
                    relief=tk.FLAT, width=12, pady=4, cursor='hand2')
        self._comprar_btn = tk.Button(act, text=T('btn.take'), command=self._comprar,
                                      bg='#c0392b', **_AKW)
        self._comprar_btn.pack(side=tk.LEFT, padx=2)
        self._actualiza_btn = tk.Button(act, text=T('btn.update'),
                                        command=self._update_cue,
                                        bg='#b9770e', **_AKW)
        self._actualiza_btn.pack(side=tk.LEFT, padx=2)
        self._guarda_btn = tk.Button(act, text=T('btn.save'),
                                     command=self._save_show,
                                     bg='#16a085', **_AKW)
        self._guarda_btn.pack(side=tk.LEFT, padx=2)
        tk.Button(act, text=T('btn.goto'), command=self._goto_selected,
                  bg='#2c3e80', **_AKW).pack(side=tk.LEFT, padx=2)
        self._apagar_btn = tk.Button(act, text=T('btn.delete'),
                                     command=self._apagar, bg='#2c3e80', **_AKW)
        self._apagar_btn.pack(side=tk.LEFT, padx=2)

        # linha de baixo — navegação do cursor de edição
        act2 = ttk.Frame(clf)
        act2.pack(fill=tk.X, pady=(0, 4))
        tk.Button(act2, text="<<<", command=self._seq_prev,
                  bg='#34495e', fg='white', font=('Arial', 11, 'bold'),
                  relief=tk.FLAT, width=12, pady=4, cursor='hand2').pack(side=tk.LEFT, padx=2)
        tk.Button(act2, text=">>>", command=self._seq_next,
                  bg='#34495e', fg='white', font=('Arial', 11, 'bold'),
                  relief=tk.FLAT, width=12, pady=4, cursor='hand2').pack(side=tk.LEFT, padx=2)
        # v6.2: atalho do modelo da cuelist (cue_only laranja / tracking azul)
        self._im_btn = tk.Button(act2, command=self._toggle_intensity_mode,
                                 fg='white', font=('Arial', 11, 'bold'),
                                 relief=tk.FLAT, width=12, pady=4, cursor='hand2')
        self._im_btn.pack(side=tk.LEFT, padx=2)
        self._refresh_im_btn()
        # v6.3: botão MIDI ON/OFF ao lado do TRACKING/CUE-ONLY
        self._midi_toggle_btn = tk.Button(act2, command=self._toggle_midi_active,
                                          fg='white', font=('Arial', 11, 'bold'),
                                          relief=tk.FLAT, width=12, pady=4,
                                          cursor='hand2')
        self._midi_toggle_btn.pack(side=tk.LEFT, padx=2)
        self._refresh_midi_toggle_btn()
        # v6.3.3: tecla PARTE (divisões da memória) ao lado do MIDI
        self._parte_btn = tk.Button(act2, text=T('parte.btn'),
                                    command=self._on_parte,
                                    fg='white', bg='#33415c',
                                    font=('Arial', 11, 'bold'),
                                    relief=tk.FLAT, width=12, pady=4,
                                    cursor='hand2')
        self._parte_btn.pack(side=tk.LEFT, padx=2)

        # 'barr' = checkbox da barreira (block cue); 'fx' = link aos FX
        # (v5 etapa 4: lançar/tirar efeitos a partir da sequência)
        cols = ('num', 'barr', 'label', 'entrada', 'saida', 'encad',
                'salta', 'fx', 'midi', 'parte')
        self._tree = ttk.Treeview(clf, columns=cols, show='headings',
                                  height=20, selectmode='none')
        self._tree.heading('num',     text=T('tree.num'))
        self._tree.heading('barr',    text=T('tree.barr'))
        self._tree.heading('label',   text=T('tree.label'))
        self._tree.heading('entrada', text=T('tree.in'))
        self._tree.heading('saida',   text=T('tree.out'))
        self._tree.heading('encad',   text=T('tree.auto'))
        self._tree.heading('salta',   text=T('tree.loop'))
        self._tree.heading('fx',      text=T('tree.fx'))
        self._tree.heading('midi',    text=T('tree.midi'))
        self._tree.heading('parte',   text=T('tree.parte'))   # v6.3.3
        self._tree.column('num',     width=38, anchor='center')
        self._tree.column('barr',    width=28, anchor='center')
        self._tree.column('label',   width=72)
        self._tree.column('entrada', width=52, anchor='center')
        self._tree.column('saida',   width=52, anchor='center')
        self._tree.column('encad',   width=44, anchor='center')
        self._tree.column('salta',   width=58, anchor='center')
        self._tree.column('fx',      width=84, anchor='center')  # v6.3.3
        self._tree.column('midi',    width=76, anchor='center')
        self._tree.column('parte',   width=52, anchor='center')  # v6.3.3

        sc = ttk.Scrollbar(clf, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=sc.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree.tag_configure('active',   background='#2e7d4f', foreground='#ffffff')
        self._tree.tag_configure('zero',     background='#2a2a3e', foreground='#aaaacc')
        self._tree.tag_configure('zerooff',  background='#16161e', foreground='#555577')
        # BARREIRA: linha em magenta. Aplicado depois das outras (linha activa
        # mantem prioridade, p/ nao confundir com a memoria em execucao).
        self._tree.tag_configure('barreira', background='#7a2070', foreground='#ffffff')
        self._tree.bind('<ButtonRelease-1>', self._tree_click)
        # botão direito em qualquer linha → janela de links de FX (via
        # principal, serve sempre em XF ou FX)
        self._tree.bind('<Button-3>', self._tree_right)

    # ── página FX (v5) ────────────────────────
    def _build_fx_panel(self, parent):
        """Página FX (fundo magenta escuro): Comprar/Actualização/Guardar/
        Apagar FX em cima, <<< >>> por baixo e NUM_FX botões de efeitos
        (2 linhas de 8). A zona de baixo mostra a CUELIST principal quando
        não há FX em edição; o editor do FX quando há."""
        tf = ttk.Frame(parent, padding=6, style='FX.TFrame')
        tf.pack(fill=tk.X)
        ttk.Label(tf, text=T('fx.title'), font=('Arial', 18, 'bold'),
                  foreground='#e8d44d', style='FX.TLabel').pack(anchor='w')

        act = ttk.Frame(parent, padding=(6, 0), style='FX.TFrame')
        act.pack(fill=tk.X, pady=(4, 2))

        def _abtn(txt, cmd, bg):
            return tk.Button(act, text=txt, command=cmd, bg=bg, fg='white',
                             font=('Arial', 12, 'bold'), relief=tk.FLAT,
                             width=12, pady=8, cursor='hand2')

        self._fxc_btn = _abtn(T('btn.take'), lambda: self._fx_arm('comprar'),
                              '#c0392b')
        self._fxc_btn.pack(side=tk.LEFT, padx=2)
        self._fxa_btn = _abtn(T('btn.update'), lambda: self._fx_arm('actualiza'),
                              '#b9770e')
        self._fxa_btn.pack(side=tk.LEFT, padx=2)
        self._fxg_btn = _abtn(T('btn.save'), self._save_show, '#16a085')
        self._fxg_btn.pack(side=tk.LEFT, padx=2)
        self._fxd_btn = _abtn(T('btn.delete_fx'), lambda: self._fx_arm('apagar'),
                              '#2c3e80')
        self._fxd_btn.pack(side=tk.LEFT, padx=2)

        # v5 etapa 1: na página FX as <<< >>> navegam os PASSOS do loop
        # manual em edição (decisão do autor) — não a sequência principal
        act2 = ttk.Frame(parent, padding=(6, 0), style='FX.TFrame')
        act2.pack(fill=tk.X, pady=(0, 4))
        tk.Button(act2, text="<<<", command=self._fx_seq_prev,
                  bg='#34495e', fg='white', font=('Arial', 10, 'bold'),
                  relief=tk.FLAT, width=18, pady=4,
                  cursor='hand2').pack(side=tk.LEFT, padx=2)
        tk.Button(act2, text=">>>", command=self._fx_seq_next,
                  bg='#34495e', fg='white', font=('Arial', 10, 'bold'),
                  relief=tk.FLAT, width=18, pady=4,
                  cursor='hand2').pack(side=tk.LEFT, padx=2)

        # NUM_FX botões FX agrupados em PAINÉIS de 4 (16 FX = 4 grupos, igual
        # ao passo do encoder da Consola 2). O painel do grupo seleccionado
        # pela Consola 2 ACENDE (fundo laranja) — identifica claramente que 4
        # teclas físicas estão activas. Layout: 2 painéis por linha (mantém o
        # aspecto de 2×8 mas com uma folga a separar cada grupo de 4).
        FXG = 4                                   # FX por grupo
        n_groups = (NUM_FX + FXG - 1) // FXG
        GCOLS = 2                                 # painéis por linha
        groups = ttk.Frame(parent, padding=(6, 2), style='FX.TFrame')
        groups.pack(fill=tk.X)
        self._fx_btns = [None] * NUM_FX
        self._fx_group_frames = []
        for g in range(n_groups):
            gf = tk.Frame(groups, bg=self.FX_GRP_OFF, padx=3, pady=3)
            gf.grid(row=g // GCOLS, column=g % GCOLS,
                    padx=4, pady=3, sticky='nsew')
            self._fx_group_frames.append(gf)
            for k in range(FXG):
                i = g * FXG + k
                if i >= NUM_FX:
                    break
                b = tk.Button(gf, text=f"FX {i + 1}", bg='#2c2c44',
                              fg='#666677', font=('Arial', 9, 'bold'),
                              relief=tk.FLAT, cursor='hand2', pady=6)
                b.grid(row=0, column=k, padx=2, pady=2, sticky='ew')
                b.bind('<Button-1>', lambda ev, i=i: self._fx_left(i))
                b.bind('<Button-3>', lambda ev, i=i: self._fx_right(i))
                self._fx_btns[i] = b
                gf.columnconfigure(k, weight=1)
        for c in range(GCOLS):
            groups.columnconfigure(c, weight=1)

        # zona de baixo — CUELIST principal (sem FX em edição) ou editor do
        # FX (com edição); construída/trocada por _fx_build_editor.
        self._fx_editor = ttk.LabelFrame(parent, text=T('fx.editor_cues'),
                                         padding=6, style='FX.TLabelframe')
        self._fx_editor.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4, 4))
        self._fx_cue_tree = None
        self._fx_build_editor()

    def _show_page(self, page):
        """Troca a página do painel direito (XF ↔ FX)."""
        if page == self._page:
            return
        self._page = page
        if page == 'fx':
            self._xf_page.pack_forget()
            self._fx_page.pack(fill=tk.BOTH, expand=True)
        else:
            self._fx_page.pack_forget()
            self._xf_page.pack(fill=tk.BOTH, expand=True)
        on, off = '#2c7d4f', '#2c3e80'
        self._xf_btn.config(bg=on if page == 'xf' else off)
        self._fx_btn.config(bg=on if page == 'fx' else off)

    # ── FX: armar acções (mesma lógica visual do COMPRAR da XF) ──
    def _fx_arm(self, action):
        """1.ª pressão arma (amarelo). 2.ª pressão da MESMA acção:
        Comprar 2× → grava um PASSO no FX manual em edição (espec. do
        autor); Actualização 2× → actualiza os níveis do passo
        seleccionado; Apagar 2× → apenas desarma. Com a acção armada,
        clicar num botão FX executa sobre esse FX (criar / apagar).

        EXCEPÇÃO (pedido do autor 2026-06-12): com um FX DINÂMICO em
        edição, Actualização é UM TOQUE ÚNICO — acrescenta a selecção
        actual à ORDEM dos canais. Permite construir ordens personalizadas:
        compra-se o 5, depois Actualização com o 3, com o 4, … →
        ordem 5,3,4,1,6,2 em vez de 1..6."""
        if action == 'actualiza':
            fx_e = (self.engine.fx[self._fx_edit]
                    if self._fx_edit is not None else None)
            if fx_e and fx_e.get('mode') in ('dinamico', 'caos'):
                self._fx_armed = None
                self._refresh_fx_action_btns()
                self._fx_append_selection()
                return
        if self._fx_armed == action:
            self._fx_armed = None
            self._refresh_fx_action_btns()
            if action == 'comprar':
                self._fx_record_step()
            elif action == 'actualiza':
                self._fx_update_step()
            return
        self._fx_armed = action
        self._refresh_fx_action_btns()

    def _refresh_fx_action_btns(self):
        ARMED = '#f1c40f'
        self._fxc_btn.config(bg=ARMED if self._fx_armed == 'comprar'
                             else '#c0392b')
        self._fxa_btn.config(bg=ARMED if self._fx_armed == 'actualiza'
                             else '#b9770e')
        self._fxd_btn.config(bg=ARMED if self._fx_armed == 'apagar'
                             else '#2c3e80')

    def _fx_left(self, i):
        """Botão esquerdo num FX: executa a acção armada (comprar = criar
        FX / apagar) ou, sem acção armada, CORRE/PÁRA o loop — como um
        sampler de som (espec. do autor)."""
        fx = self.engine.fx[i]
        armed, self._fx_armed = self._fx_armed, None
        self._refresh_fx_action_btns()
        if armed == 'comprar':
            self._fx_create(i)
            return
        if armed == 'apagar':
            if fx and messagebox.askyesno(
                    T('btn.delete_fx'),
                    T('m.fx_delete_q',
                      name=fx.get('name') or T('fxc.default_name', n=i + 1))):
                self.engine.fx_clear(i)
                if self._fx_edit == i:
                    self._fx_edit = None
                    self._fx_build_editor()
                self._refresh_fx()
            return
        if armed == 'actualiza':
            messagebox.showinfo(T('btn.update'), T('m.update_arm_help'))
            return
        # sem acção armada → corre/pára o loop (toggle)
        if not fx:
            return
        ligou = self.engine.fx_toggle(i)
        if ligou:
            self._fx_last_active = i   # p/ o atalho de link na cuelist
        self._refresh_fx()

    def _fx_right(self, i):
        """Botão direito num FX gravado: abre/fecha a edição e gravação."""
        if not self.engine.fx[i]:
            return
        self._fx_edit = None if self._fx_edit == i else i
        self._fx_step_sel = 0
        self._fx_build_editor()
        self._refresh_fx()

    def _fx_create(self, i):
        """Comprar + clique → cria (ou re-compra por cima) a 'concha' do
        FX: nome + modo. Abre logo a edição para gravar os passos."""
        dlg = FXCreateDialog(self.root, i, self.engine.fx[i])
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        nome, modo = dlg.result
        old = self.engine.fx[i] or {}
        novo = {'name': nome or T('fxc.default_name', n=i + 1), 'mode': modo,
                'steps': list(old.get('steps', [])),
                'channels': list(old.get('channels', [])),
                'levels': dict(old.get('levels', {}))}
        if modo in ('dinamico', 'caos'):
            # parâmetros do ciclo — preserva os antigos numa re-compra
            # (dinâmico e caos partilham o mesmo conjunto de campos)
            for k, v in FX_DIN_DEFAULTS.items():
                novo[k] = old.get(k, v)
            # caos NOVO nasce estreito (Caos=1); re-compra preserva o valor
            if modo == 'caos' and 'carroagem' not in old:
                novo['carroagem'] = 1
        self.engine.fx[i] = novo
        self.engine.fx_active[i] = False
        self.engine._fx_run[i] = None
        self._fx_edit = i               # entra logo em edição
        self._fx_step_sel = 0
        self._fx_build_editor()
        self._refresh_fx()

    # ── FX: gravação e edição de passos (modo manual, etapa 1) ──
    def _fx_capture_look(self):
        """Fotografia da luz em cena: canais no programador (azul) ou
        activos. Igual à lógica do retrato. O programador NÃO é limpo —
        ajusta-se e compra-se o passo seguinte."""
        levels = {}
        for ch in range(1, NUM_CHANNELS + 1):
            if self.engine.programmer[ch] is not None:
                levels[str(ch)] = int(self.engine.programmer[ch])
            elif self.engine.active[ch]:
                levels[str(ch)] = int(round(self.engine.output[ch]))
        return levels

    def _fx_edited_manual(self):
        """Devolve (i, fx) do FX manual em edição, ou (None, None)."""
        i = self._fx_edit
        fx = self.engine.fx[i] if i is not None else None
        if fx and fx.get('mode') == 'manual':
            return i, fx
        return None, None

    def _fx_record_step(self):
        """Comprar 2× → no FX MANUAL acrescenta um passo com a luz em
        cena (tempos herdam do passo anterior; o 1.º nasce 1 s/1 s); no
        FX DINÂMICO compra a SELECÇÃO de canais + níveis base."""
        fx_e = (self.engine.fx[self._fx_edit]
                if self._fx_edit is not None else None)
        if fx_e and fx_e.get('mode') in ('dinamico', 'caos'):
            self._fx_buy_selection()
            return
        i, fx = self._fx_edited_manual()
        if fx is None:
            messagebox.showinfo(T('m.take_step_title'), T('m.take_step_help'))
            return
        levels = self._fx_capture_look()
        if not levels:
            messagebox.showinfo(T('m.take_step_title'), T('m.take_nothing'))
            return
        steps = fx.setdefault('steps', [])
        if steps:
            fade = Engine._fx_clamp_t(steps[-1].get('fade', 1.0))
            auto = Engine._fx_clamp_t(steps[-1].get('auto', 1.0))
        else:
            fade, auto = 1.0, 1.0
        steps.append({'levels': levels, 'fade': fade, 'auto': auto})
        self._fx_step_sel = len(steps) - 1
        self._fx_refresh_editor(force=True)
        self._refresh_fx()

    def _fx_update_step(self):
        """Actualização 2× → no manual substitui os níveis do passo
        seleccionado pela luz em cena (tempos mantêm-se). (No dinâmico a
        Actualização nunca chega aqui — é um toque único que acrescenta
        a selecção à ordem; ver _fx_arm/_fx_append_selection.)"""
        i, fx = self._fx_edited_manual()
        steps = fx.get('steps', []) if fx else []
        if fx is None or not steps:
            messagebox.showinfo(T('m.update_step_title'), T('m.update_step_need'))
            return
        levels = self._fx_capture_look()
        if not levels:
            messagebox.showinfo(T('m.update_step_title'), T('m.update_nothing'))
            return
        idx = max(0, min(self._fx_step_sel, len(steps) - 1))
        steps[idx]['levels'] = levels
        self._fx_refresh_editor(force=True)

    def _fx_delete_step(self):
        """Apaga o passo seleccionado do FX manual em edição."""
        i, fx = self._fx_edited_manual()
        steps = fx.get('steps', []) if fx else []
        if fx is None or not steps:
            return
        idx = max(0, min(self._fx_step_sel, len(steps) - 1))
        if not messagebox.askyesno(T('fx.erase_step'),
                                   T('fx.erase_step_q', n=idx + 1)):
            return
        steps.pop(idx)
        self._fx_step_sel = max(0, min(idx, len(steps) - 1))
        self._fx_refresh_editor(force=True)
        self._refresh_fx()

    def _fx_seq_prev(self):
        # sem FX em edição (espelho da cuelist à vista) → navega a SEQUÊNCIA
        # principal como em XF, p/ poder adicionar links; com FX em edição →
        # navega os passos do FX manual
        if self._fx_edit is None:
            self._move_cursor(-1)
        else:
            self._fx_step_move(-1)

    def _fx_seq_next(self):
        if self._fx_edit is None:
            self._move_cursor(+1)
        else:
            self._fx_step_move(+1)

    def _fx_step_move(self, d):
        """<<< >>> da página FX: navegam os passos do FX manual em edição
        (em ciclo) e mostram os níveis desse passo no programador."""
        i, fx = self._fx_edited_manual()
        steps = fx.get('steps', []) if fx else []
        if fx is None or not steps:
            return
        self._fx_step_sel = (self._fx_step_sel + d) % len(steps)
        self._fx_preview_step(self._fx_step_sel)
        self._fx_refresh_editor(force=True)

    def _fx_preview_step(self, idx):
        """Aplica os níveis ABSOLUTOS do passo no programador (a azul) —
        para ver/afinar; Esc/LIBERTA solta como sempre."""
        i, fx = self._fx_edited_manual()
        if fx is None:
            return
        for ch, v in Engine._fx_step_levels(fx, idx).items():
            self.engine.set_channel(ch, v)
        self._mark_dirty()

    # ── FX: zona de edição (constrói/actualiza a lista de passos) ──
    def _fx_build_cue_mirror(self):
        """Cria o espelho (só-leitura) da cuelist principal na zona de
        baixo da página FX. Mesmas colunas/cores do tree principal; clicar
        numa linha posiciona a sequência (set_position), útil para operar."""
        cols = ('num', 'barr', 'label', 'entrada', 'saida', 'encad',
                'salta', 'fx', 'midi', 'parte')
        tree = ttk.Treeview(self._fx_editor, columns=cols, show='headings',
                            selectmode='none')
        for cid, txt, w, anc in (
                ('num', T('tree.num'), 38, 'center'),
                ('barr', T('tree.barr'), 28, 'center'),
                ('label', T('tree.label'), 72, 'w'),
                ('entrada', T('tree.in'), 52, 'center'),
                ('saida', T('tree.out'), 52, 'center'),
                ('encad', T('tree.auto'), 44, 'center'),
                ('salta', T('tree.loop'), 58, 'center'),
                ('fx', T('tree.fx'), 84, 'center'),
                ('midi', T('tree.midi'), 76, 'center'),
                ('parte', T('tree.parte'), 52, 'center')):   # v6.3.3
            tree.heading(cid, text=txt)
            tree.column(cid, width=w, anchor=anc)
        sc = ttk.Scrollbar(self._fx_editor, orient=tk.VERTICAL,
                           command=tree.yview)
        tree.configure(yscrollcommand=sc.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        tree.tag_configure('active',   background='#2e7d4f', foreground='#ffffff')
        tree.tag_configure('zero',     background='#2a2a3e', foreground='#aaaacc')
        tree.tag_configure('zerooff',  background='#16161e', foreground='#555577')
        tree.tag_configure('barreira', background='#7a2070', foreground='#ffffff')
        tree.bind('<ButtonRelease-1>', self._fx_cue_mirror_click)
        tree.bind('<Button-3>', self._fx_cue_mirror_right)
        self._fx_cue_tree = tree
        self._fill_cue_tree(tree)

    def _fx_marca_unica(self, cue, n, manter):
        """v6.3.3 — regra: UM FX só pode ter UMA marca por memória (na
        coluna directa OU numa parte — nunca nas duas: dava ordens
        contraditórias no mesmo GO). Remove as marcas do FX n (1-based)
        de todo o lado EXCEPTO em `manter` ('link' = coluna directa, ou
        o nº da parte em string). Devolve True se tirou alguma."""
        tirou = False
        ln = cue.get('fx_link')
        if (manter != 'link' and isinstance(ln, dict)
                and int(ln.get('num', 0) or 0) == n):
            cue['fx_link'] = None
            tirou = True
        for k, p in list((cue.get('parts') or {}).items()):
            if manter == k:
                continue
            fx = p.get('fx')
            if isinstance(fx, dict) and int(fx.get('num', 0) or 0) == n:
                p.pop('fx', None)
                tirou = True
        return tirou

    def _fx_quick_link(self, idx):
        """Atalho (pedido do autor 2026-06-13/17): com UM FX activo, clicar
        (esquerdo) na célula FX de uma memória cicla a marca desse FX em 3
        estados: 1.º ∿ ACOMPANHA O FADE → 2.º ⚡ IMEDIATO («esticão») →
        3.º apaga; sem abrir o diálogo. Devolve True se tratou pelo atalho;
        False se há 0 ou >1 FX activos ambíguos (→ usa o diálogo). O FX-alvo
        é o único activo, ou o último ligado à mão se ainda o estiver."""
        if not (0 <= idx < len(self.engine.cues)):
            return False
        cue = self.engine.cues[idx]
        if cue.get('zero'):
            return False
        actives = [j for j, a in enumerate(self.engine.fx_active)
                   if a and self.engine.fx[j]]
        if not actives:
            return False
        if len(actives) == 1:
            target = actives[0]
        elif self._fx_last_active in actives:
            target = self._fx_last_active
        else:
            return False                  # vários activos: cai no diálogo
        n = target + 1
        ln = cue.get('fx_link')
        same = isinstance(ln, dict) and int(ln.get('num', 0) or 0) == n
        if not same:
            novo = {'num': n, 'fade': True}    # 1.º clique → ∿ acompanha fade
        elif ln.get('fade'):
            novo = {'num': n, 'fade': False}   # 2.º clique → ⚡ imediato
        else:
            novo = None                        # 3.º clique → apaga
        self.engine.set_cue_field(idx, 'fx_link', novo)
        # v6.3.3 — um FX, uma marca por memória: tira-o das partes
        if novo and self._fx_marca_unica(cue, n, 'link'):
            self._status_var.set(T('parte.fx_unica', n=n))
        self._refresh()
        return True

    def _open_fx_link_dialog(self, idx):
        """Janela de edição do link de FX de uma memória (a via PRINCIPAL,
        serve sempre, em XF ou FX). Botão direito em qualquer cuelist e botão
        esquerdo quando não há link rápido (0 FX activos ou página XF)."""
        if not (0 <= idx < len(self.engine.cues)):
            return
        cue = self.engine.cues[idx]
        if cue.get('zero'):
            messagebox.showinfo("FX", T('m.zero_no_fx'))
            return
        gravados = [f"{j + 1} {fx.get('name') or ''}".strip()
                    for j, fx in enumerate(self.engine.fx) if fx]
        dlg = FXLinkDialog(self.root, cue.get('fx_link'), gravados)
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        if dlg.result[0] == 'rem':
            self.engine.set_cue_field(idx, 'fx_link', None)
        else:
            n, fade = dlg.result
            if self.engine.fx[n - 1] is None:
                messagebox.showwarning("FX", T('m.fxlink_empty', n=n))
            self.engine.set_cue_field(idx, 'fx_link',
                                      {'num': n, 'fade': fade})
            # v6.3.3 — um FX, uma marca por memória: tira-o das partes
            if self._fx_marca_unica(cue, n, 'link'):
                self._status_var.set(T('parte.fx_unica', n=n))
        self._refresh()

    def _fx_cue_mirror_click(self, event):
        """Clique no espelho da cuelist (página FX): na coluna FX tenta o
        atalho de link (FX activo → liga-o a essa memória); nas outras
        colunas posiciona a sequência nessa memória (como as <<< >>>)."""
        tree = self._fx_cue_tree
        if tree is None:
            return
        row = tree.identify_row(event.y)
        if row == '':
            return
        try:
            idx = int(row)
        except ValueError:
            return
        col = tree.identify_column(event.x)
        if col == '#8':
            # coluna FX: 1 FX activo → ciclo rápido (∿→⚡→apaga); senão (0 ou
            # ambíguo) abre a janela. As outras colunas posicionam a sequência.
            if self._fx_quick_link(idx):
                return
            self._open_fx_link_dialog(idx)
            return
        if col == '#9':
            self._open_midi_dialog(idx)     # v6.3 — coluna MIDI no espelho
            return
        if 0 <= idx < len(self.engine.cues):
            self.engine.set_position(idx)
            self._refresh()

    def _fx_cue_mirror_right(self, event):
        """Botão direito no espelho da cuelist (página FX): abre SEMPRE a
        janela de links, haja ou não FX activo."""
        tree = self._fx_cue_tree
        if tree is None:
            return
        row = tree.identify_row(event.y)
        if row != '':
            try:
                self._open_fx_link_dialog(int(row))
            except ValueError:
                pass

    def _fx_build_editor(self):
        """Reconstrói o conteúdo da zona de baixo da página FX: sem FX em
        edição mostra a CUELIST principal (espelho); com FX em edição
        mostra os passos (manual) ou os parâmetros (dinâmico)."""
        for w in self._fx_editor.winfo_children():
            w.destroy()
        self._fx_tree = None
        self._fx_cue_tree = None
        self._fx_ed_cache = None
        i = self._fx_edit
        fx = self.engine.fx[i] if i is not None else None
        if not fx:
            # sem FX em edição → espelho da cuelist principal, para ver a
            # sequência enquanto se opera os FX (pedido do autor)
            self._fx_editor.config(text=T('fx.editor_cues_xf'))
            self._fx_build_cue_mirror()
            return
        nome = fx.get('name') or T('fxc.default_name', n=i + 1)
        if fx.get('mode') != 'manual':
            self._fx_build_editor_din(i, fx, nome)
            return
        self._fx_editor.config(text=T('fx.editor_manual', nome=nome))
        bar = ttk.Frame(self._fx_editor)
        bar.pack(fill=tk.X, pady=(0, 4))
        tk.Button(bar, text=T('fx.erase_step'), command=self._fx_delete_step,
                  bg='#2c3e80', fg='white', font=('Arial', 9, 'bold'),
                  relief=tk.FLAT, padx=8, pady=4,
                  cursor='hand2').pack(side=tk.RIGHT)

        cols = ('passo', 'fade', 'auto', 'canais')
        tree = ttk.Treeview(self._fx_editor, columns=cols, show='headings',
                            selectmode='browse')
        tree.heading('passo',  text=T('fx.col_step'))
        # clique no TÍTULO Fade/Auto. → muda o tempo de TODOS os passos
        tree.heading('fade',   text=T('fx.col_fade'),
                     command=lambda: self._fx_edit_all_times('fade'))
        tree.heading('auto',   text=T('fx.col_auto'),
                     command=lambda: self._fx_edit_all_times('auto'))
        tree.heading('canais', text=T('fx.col_channels'))
        tree.column('passo',  width=46, anchor='center')
        tree.column('fade',   width=58, anchor='center')
        tree.column('auto',   width=58, anchor='center')
        tree.column('canais', width=150)
        sc = ttk.Scrollbar(self._fx_editor, orient=tk.VERTICAL,
                           command=tree.yview)
        tree.configure(yscrollcommand=sc.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        # passo em execução (loop a correr) — linha verde
        tree.tag_configure('run', background='#2e7d4f', foreground='#ffffff')
        tree.bind('<ButtonRelease-1>', self._fx_step_click)
        self._fx_tree = tree
        self._fx_refresh_editor(force=True)

    def _fx_build_editor_din(self, i, fx, nome):
        """Painel de parâmetros do FX DINÂMICO ou CAOS — compacto, 2 colunas.
        v6.2: cada modo mostra só os seus controlos.
          · partilhados: Curva, Ataque, Retirada, BPM, V.alto, V.baixo
          · só dinâmico: Direcção, Blocos, Carroagem, Grupos, Cruzamento
          · só caos:     Quantidade (mín/máx), Caos, Repetir
        Tudo mexe EM VIVO."""
        is_caos = fx.get('mode') == 'caos'
        self._fx_editor.config(text=T('fx.editor_caos' if is_caos
                                      else 'fx.editor_dyn', nome=nome))
        self._fx_din_chlbl = ttk.Label(self._fx_editor,
                                       font=('Arial', 9, 'bold'))
        self._fx_din_chlbl.pack(anchor='nw', pady=(0, 4))
        self._fx_din_refresh_chlbl()

        pf = ttk.Frame(self._fx_editor)
        pf.pack(fill=tk.BOTH, expand=True)
        pf.columnconfigure(0, weight=1)
        pf.columnconfigure(1, weight=1)

        # ── linha 0: curva + direcção (partilhados); blocos só no dinâmico ──
        row = ttk.Frame(pf)
        row.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 2))
        ttk.Label(row, text=T('fxd.curve'), width=9).pack(side=tk.LEFT)
        cur = fx.get('curva', 'sino')
        cv = tk.StringVar(value='PWM' if cur in ('pwm', 'quadrada')
                          else 'sino')
        cb = ttk.Combobox(row, textvariable=cv, state='readonly', width=6,
                          values=['sino', 'PWM'])
        cb.pack(side=tk.LEFT)
        cb.bind('<<ComboboxSelected>>',
                lambda ev: self._fx_din_set('curva', cv.get()))
        if not is_caos:
            # Direcção e Blocos só fazem sentido no dinâmico
            ttk.Label(row, text=T('fxd.dir')).pack(side=tk.LEFT)
            dv = tk.StringVar(value=fx.get('direccao', '>')
                              if fx.get('direccao') in ('>', '<', '<>') else '>')
            db = ttk.Combobox(row, textvariable=dv, state='readonly', width=4,
                              values=['>', '<', '<>'])
            db.pack(side=tk.LEFT, padx=(2, 0))
            db.bind('<<ComboboxSelected>>',
                    lambda ev: self._fx_din_set('direccao', dv.get()))
            ttk.Label(row, text=T('fxd.blocks')).pack(side=tk.LEFT)
            bv = tk.StringVar(value=str(fx.get('blocos', '')))
            be = ttk.Entry(row, textvariable=bv, width=9)
            be.pack(side=tk.LEFT, padx=(2, 0))
            self._fx_blocos_fb = ttk.Label(row, foreground='#666688')
            self._fx_blocos_fb.pack(side=tk.LEFT, padx=(4, 0))

            def _blocos_mudou(*_a):
                s = bv.get().strip().upper()
                self._fx_din_set('blocos', s)
                if not s:
                    txt = ""
                else:
                    pat, mm = Engine._fx_parse_blocos(s)
                    if pat is None:
                        txt = T('fxd.blk_invalid')
                    elif mm >= 2:
                        txt = T('fxd.blk_info', n=len(s), mm=mm)
                    else:
                        txt = T('fxd.blk_one')
                if self._fx_blocos_fb.winfo_exists():
                    self._fx_blocos_fb.config(text=txt)
            bv.trace_add('write', _blocos_mudou)
            _blocos_mudou()

        # ── sliders em 2 colunas ──
        def _slider(rotulo, key, frm, to, r, c):
            cell = ttk.Frame(pf)
            cell.grid(row=r, column=c, sticky='ew', padx=(0, 8))
            ttk.Label(cell, text=rotulo, width=9).pack(side=tk.LEFT)
            sc = tk.Scale(cell, from_=frm, to=to, orient=tk.HORIZONTAL,
                          resolution=1, showvalue=True, length=120,
                          bg='#111122', fg='#ccccee', troughcolor='#2c2c3e',
                          highlightthickness=0, sliderlength=16, width=10,
                          command=lambda v, k=key: self._fx_din_set(k, v))
            sc.set(fx.get(key, FX_DIN_DEFAULTS.get(key, 0)))
            sc.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # partilhados (os dois modos)
        _slider(T('fxd.attack'), 'ataque',   0,  10, 1, 0)
        _slider(T('fxd.decay'),  'retirada', 0,  10, 1, 1)
        _slider(T('fxd.bpm'),    'bpm',      1, 360, 2, 0)

        if not is_caos:
            # ── DINÂMICO: carroagem, grupos, cruzamento ──
            _slider(T('fxd.width'),  'carroagem', 1,  99, 2, 1)
            _slider(T('fxd.v_high'), 'v_alto',    0, 100, 3, 0)
            _slider(T('fxd.v_low'),  'v_baixo',   0, 100, 3, 1)
            _slider(T('fxd.groups'), 'grupos',    0,  24, 4, 0)
            # CRUZAMENTO — sobreposição entre blocos/bandas vizinhos
            _slider(T('fxd.cross'),  'cruzamento', 0, 100, 4, 1)
            ttk.Label(pf, text=T('fxd.cross_note'), foreground='#666688'
                      ).grid(row=5, column=0, columnspan=2, sticky='w')
            return

        # ── CAOS ──
        # cursor único «Caos» (funde carroagem + random): controla a % de
        # canais envolvidos na desordem; o grau de random é fixo no motor.
        # Fica entre a Retirada e o V.baixo (r2,c1).
        _slider(T('fxd.chaos'),  'carroagem', 1,  99, 2, 1)
        _slider(T('fxd.v_high'), 'v_alto',    0, 100, 3, 0)
        _slider(T('fxd.v_low'),  'v_baixo',   0, 100, 3, 1)
        # Quantidade (mín/máx): nº de canais sorteados; 0/0 = cintilação
        qrow = ttk.Frame(pf)
        qrow.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(4, 0))
        ttk.Label(qrow, text=T('fxd.quant_min'), width=9).pack(side=tk.LEFT)
        qmin = tk.StringVar(value=str(int(fx.get('quant_min', 0))))
        ttk.Entry(qrow, textvariable=qmin, width=5).pack(side=tk.LEFT)
        ttk.Label(qrow, text=T('fxd.quant_max'),
                  width=9).pack(side=tk.LEFT, padx=(8, 0))
        qmax = tk.StringVar(value=str(int(fx.get('quant_max', 0))))
        ttk.Entry(qrow, textvariable=qmax, width=5).pack(side=tk.LEFT)
        qmin.trace_add('write',
                       lambda *_a: self._fx_din_set('quant_min', qmin.get()))
        qmax.trace_add('write',
                       lambda *_a: self._fx_din_set('quant_max', qmax.get()))
        ttk.Label(pf, text=T('fxd.quant_note'), foreground='#666688'
                  ).grid(row=5, column=0, columnspan=2, sticky='w')

        # Repete (caos): nº de batidas que a mesma combinação se mantém
        crow = ttk.Frame(pf)
        crow.grid(row=6, column=0, columnspan=2, sticky='ew', pady=(4, 0))
        ttk.Label(crow, text=T('fxd.repeat'), width=9).pack(side=tk.LEFT)
        rv = tk.StringVar(value=str(fx.get('caos_rep', '')))
        re_ = ttk.Entry(crow, textvariable=rv, width=14)
        re_.pack(side=tk.LEFT, padx=(2, 0))
        self._fx_caosrep_fb = ttk.Label(crow, foreground='#666688')
        self._fx_caosrep_fb.pack(side=tk.LEFT, padx=(6, 0))

        def _caosrep_mudou(*_a):
            self._fx_din_set('caos_rep', rv.get())
            seq = Engine._fx_parse_caos_rep(rv.get())
            if rv.get().strip() in ('', '1'):
                txt = T('fxd.rep_always')
            else:
                txt = T('fxd.rep_hold',
                        seq="·".join(str(k) for k in seq))
            if self._fx_caosrep_fb.winfo_exists():
                self._fx_caosrep_fb.config(text=txt)
        rv.trace_add('write', _caosrep_mudou)
        _caosrep_mudou()

    def _fx_refresh_editor(self, force=False):
        """Actualiza a lista de passos (com cache — chamada no _refresh a
        25 fps quando o loop corre, para a linha verde acompanhar)."""
        tree = getattr(self, '_fx_tree', None)
        if tree is None or not tree.winfo_exists():
            return
        i, fx = self._fx_edited_manual()
        if fx is None:
            return
        steps = fx.get('steps', [])
        run = self.engine._fx_run[i] if self.engine.fx_active[i] else None
        run_idx = (run['idx'] % len(steps)) if (run and steps) else None
        sel = max(0, min(self._fx_step_sel, len(steps) - 1)) if steps else 0
        self._fx_step_sel = sel
        sig = (len(steps), sel, run_idx,
               tuple((round(float(st.get('fade', 1)), 3),
                      round(float(st.get('auto', 1)), 3),
                      len(st.get('levels', {})),
                      sum(int(v) for v in st.get('levels', {}).values()))
                     for st in steps))
        if not force and sig == self._fx_ed_cache:
            return
        self._fx_ed_cache = sig
        tree.delete(*tree.get_children())
        for idx, st in enumerate(steps):
            chans = set()
            for k in st.get('levels', {}):
                try:
                    chans.add(int(k))
                except (TypeError, ValueError):
                    pass
            tree.insert('', tk.END, iid=str(idx),
                        values=(idx + 1,
                                f"{float(st.get('fade', 1)):g}s",
                                f"{float(st.get('auto', 1)):g}s",
                                summarize_channels(chans)),
                        tags=('run',) if idx == run_idx else ())
        if steps:
            tree.selection_set(str(sel))
            tree.see(str(sel))

    # ── FX dinâmico: compra de selecção + parâmetros (etapa 2) ──
    def _fx_buy_selection(self):
        """Comprar/Actualização 2× num FX DINÂMICO em edição: compra a
        selecção actual de canais (feita na grelha ou chamando grupos).
        NÃO é preciso pôr níveis — o nível do efeito é definido pelo
        v_alto/v_baixo (espec. do autor). Re-comprar substitui."""
        i = self._fx_edit
        fx = self.engine.fx[i] if i is not None else None
        if not fx or fx.get('mode') not in ('dinamico', 'caos'):
            return
        sel = sorted(c for c in self._selected if 1 <= c <= NUM_CHANNELS)
        if not sel:
            messagebox.showinfo(T('m.fx_buy_title'), T('m.fx_buy_help'))
            return
        fx['channels'] = sel
        fx['levels'] = {str(ch): 255 for ch in sel}   # base = full
        # reinicia o ciclo se estiver a correr (a selecção mudou)
        with self.engine._lock:
            self.engine._fx_run[i] = None
        self._fx_din_refresh_chlbl()
        self._refresh_fx()

    def _fx_append_selection(self):
        """Actualização (1 toque) num FX DINÂMICO em edição: ACRESCENTA a
        selecção actual ao FIM da ordem de canais — para ordens
        personalizadas (5,3,4,1,6,2…). Canais já presentes são ignorados.
        Para recomeçar a ordem usa-se Comprar 2× (substitui)."""
        i = self._fx_edit
        fx = self.engine.fx[i] if i is not None else None
        if not fx or fx.get('mode') not in ('dinamico', 'caos'):
            return
        sel = sorted(c for c in self._selected if 1 <= c <= NUM_CHANNELS)
        if not sel:
            messagebox.showinfo(T('m.fx_order_title'), T('m.fx_order_help'))
            return
        chans = fx.setdefault('channels', [])
        added = [c for c in sel if c not in chans]
        chans.extend(added)
        levels = fx.setdefault('levels', {})
        for c in added:
            levels[str(c)] = 255
        # reinicia o ciclo (a ordem mudou)
        with self.engine._lock:
            self.engine._fx_run[i] = None
        self._fx_din_refresh_chlbl()
        self._refresh_fx()

    def _fx_din_set(self, key, value):
        """Callback dos controlos do painel dinâmico — escreve o parâmetro
        no FX em edição. O motor lê em vivo: ouve-se logo a mudança."""
        i = self._fx_edit
        fx = self.engine.fx[i] if i is not None else None
        if not fx or fx.get('mode') not in ('dinamico', 'caos'):
            return
        if key == 'curva':
            fx[key] = ('pwm' if str(value).lower() in ('pwm', 'quadrada')
                       else 'sino')
            return
        if key == 'direccao':
            v = str(value)
            fx[key] = v if v in ('>', '<', '<>') else '>'
            return
        if key == 'blocos':
            # guarda apenas letras A/B/C (máx. 12); a validação da ordem
            # A→B→C é feita pelo motor (_fx_parse_blocos) — inválido = ignora
            s = str(value).strip().upper()
            if len(s) <= 12 and all(c in 'ABC' for c in s):
                fx[key] = s
            return
        if key == 'caos_rep':
            # guarda só dígitos/espaços/vírgulas (máx. 40 car.); a leitura
            # do padrão é feita pelo motor (_fx_parse_caos_rep)
            s = re.sub(r'[^0-9 ,]', '', str(value))[:40]
            fx[key] = s
            return
        if key == 'ritmo':
            try:
                fx[key] = max(1, min(24, int(float(value))))
            except (TypeError, ValueError):
                pass
            return
        try:
            v = float(value)
        except (TypeError, ValueError):
            return
        fx[key] = int(v) if float(v).is_integer() else v

    def _fx_din_refresh_chlbl(self):
        """Actualiza a etiqueta 'Canais comprados' do painel dinâmico."""
        lbl = getattr(self, '_fx_din_chlbl', None)
        if lbl is None or not lbl.winfo_exists():
            return
        i = self._fx_edit
        fx = self.engine.fx[i] if i is not None else None
        if not fx:
            return
        chans = fx.get('channels') or []
        if chans:
            # ordem personalizada mostra-se LITERAL (a ordem é o efeito);
            # ordem ascendente mostra-se compacta (1▸6)
            if list(chans) == sorted(chans):
                txt = summarize_channels(chans)
            else:
                txt = ', '.join(str(c) for c in chans)
                if len(txt) > 46:
                    txt = txt[:46] + '…'
            lbl.config(text=T('fx.bought', n=len(chans), txt=txt),
                       foreground='#e8d44d')
        else:
            lbl.config(text=T('fx.no_channels'),
                       foreground='#cc7755')

    def _fx_set_all_times(self, key, value):
        """Aplica o mesmo tempo (fade ou auto) a TODOS os passos do FX
        manual em edição. Devolve o nº de passos alterados."""
        i, fx = self._fx_edited_manual()
        steps = fx.get('steps', []) if fx else []
        if not steps:
            return 0
        v = Engine._fx_clamp_t(value)
        for st in steps:
            st[key] = v
        self._fx_refresh_editor(force=True)
        return len(steps)

    def _fx_edit_all_times(self, key):
        """Clique no título da coluna Fade/Auto. → pede um tempo e
        aplica-o a todos os passos (a edição célula a célula mantém-se)."""
        i, fx = self._fx_edited_manual()
        steps = fx.get('steps', []) if fx else []
        if not steps:
            return
        rotulo = 'Fade' if key == 'fade' else 'Auto'
        dlg = ValueDialog(self.root, T('m.fx_alltimes_title', label=rotulo),
                          T('m.fx_alltimes_prompt', label=rotulo,
                            n=len(steps)),
                          f"{float(steps[0].get(key, 1)):g}")
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        v = self._to_float(dlg.result, minimum=0.0)
        if v is None:
            messagebox.showerror(T('common.error'), T('m.err_value'))
            return
        self._fx_set_all_times(key, v)

    def _fx_step_click(self, event):
        """Clique na lista de passos: selecciona + mostra o passo; nas
        colunas Fade/Auto. abre a edição do tempo (0.01–60 s)."""
        i, fx = self._fx_edited_manual()
        if fx is None:
            return
        tree = self._fx_tree
        row = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        if row == '':
            return
        idx = int(row)
        steps = fx.get('steps', [])
        if not (0 <= idx < len(steps)):
            return
        self._fx_step_sel = idx
        self._fx_preview_step(idx)
        if col in ('#2', '#3'):
            key = 'fade' if col == '#2' else 'auto'
            rotulo = 'Fade' if key == 'fade' else 'Auto'
            st = steps[idx]
            dlg = ValueDialog(self.root, T('m.fx_editstep_title'),
                              T('m.fx_time_prompt', label=rotulo),
                              f"{float(st.get(key, 1)):g}")
            self.root.wait_window(dlg)
            if dlg.result is not None:
                v = self._to_float(dlg.result, minimum=0.0)
                if v is None:
                    messagebox.showerror(T('common.error'), T('m.err_value'))
                else:
                    st[key] = Engine._fx_clamp_t(v)
        self._fx_refresh_editor(force=True)

    def _refresh_fx(self):
        """Cores dos botões FX: vazio (escuro) / gravado MANUAL (âmbar) /
        gravado DINÂMICO (violeta) / ACTIVO (verde) / edição (amarelo, ✎).
        v6.2: o PAINEL de fundo do grupo de 4 seleccionado pela Consola 2
        ACENDE (laranja) — identifica claramente as 4 teclas físicas activas."""
        g_sel = self._fx_console_group
        for g, gf in enumerate(getattr(self, '_fx_group_frames', [])):
            gf.config(bg=self.FX_GRP_ON if g == g_sel else self.FX_GRP_OFF)
        for i, b in enumerate(self._fx_btns):
            if b is None:
                continue
            fx = self.engine.fx[i]
            if not fx:
                b.config(text=f"FX {i + 1}", bg='#2c2c44', fg='#666677')
                continue
            mode = fx.get('mode')
            badge = {'manual': 'M', 'caos': 'C'}.get(mode, 'D')
            txt = f"{fx.get('name') or f'FX {i + 1}'}  ·{badge}"
            if self._fx_edit == i:
                b.config(text="✎ " + txt, bg='#f1c40f', fg='#222222')
            elif self.engine.fx_active[i]:
                b.config(text=txt, bg='#27ae60', fg='white')
            elif mode == 'manual':
                b.config(text=txt, bg='#8a5e14', fg='white')   # manual: âmbar escuro
            elif mode == 'caos':
                b.config(text=txt, bg='#a0356a', fg='white')   # caos: magenta-rosa
            else:
                b.config(text=txt, bg='#5a3a7a', fg='white')   # dinâmico: violeta
        self._push_fx_states()      # v6.3 — feedback OSC do estado dos FX

    def _push_fx_states(self):
        """v6.3 — envia /fx/{N}/state (0|1) para os controladores OSC quando o
        estado ACTIVO de um FX muda (feedback p/ TouchOSC acender a tecla).
        Só envia as diferenças — não afoga a rede."""
        cur = [1 if a else 0 for a in self.engine.fx_active]
        last = getattr(self, '_fx_state_sent', None)
        if last == cur:
            return
        for i, on in enumerate(cur):
            if last is None or last[i] != on:
                self._send_console('/fx/{}/state'.format(i + 1), on)
        self._fx_state_sent = cur

    def _go(self):
        self._back_fading = False
        _prev = self.engine.current_cue_idx
        self.engine.go()
        self._go_btn.config(bg='#5c0000')
        self.root.after(120, lambda: self._go_btn.config(bg='#8b0000'))
        if self.engine.current_cue_idx != _prev:   # só dispara se avançou
            self._disparar_midi_out()
        self._refresh()

    def _back(self):
        _prev = self.engine.current_cue_idx
        self.engine.back()
        # só o RECUA muda de cor enquanto a memória anterior está a entrar
        self._back_fading = self.engine.fading
        if self.engine.current_cue_idx != _prev:   # só dispara se recuou
            self._disparar_midi_out()
        self._refresh()

    def _toggle_pause(self):
        """Congela/retoma o efeito em curso e alterna o nome do botão."""
        self.engine.toggle_pause()
        self._update_pause_btn()

    def _update_pause_btn(self):
        if self.engine.paused:
            self._pause_btn.config(text=T('btn.resume'), bg='#27ae60')
        else:
            self._pause_btn.config(text=T('btn.pause'), bg='#8a6d3b')

    def _update_soltar_btn(self):
        """SOLTAR mostra o número do SALTAR activo; fica inactivo se não houver."""
        n = self.engine.active_salta
        if n > 0:
            self._soltar_btn.config(text=T('btn.loopbreak_n', n=n), bg='#c0392b',
                                    state=tk.NORMAL)
        else:
            self._soltar_btn.config(text=T('btn.loopbreak'), bg='#3a3a4a',
                                    state=tk.DISABLED)

    def _soltar(self):
        """Sai imediatamente do SALTAR activo, lançando a memória seguinte."""
        self.engine.soltar()
        self._refresh()

    # ── Consola 2 — fluxo de 2 pressoes (arma/executa/cancela) ──
    # COR de armado: laranja (mesma logica visual que ja usamos no COMPRAR)
    _C2_ARMED_BG = '#e67e22'

    def _console2_arm_or_exec(self, action):
        """1.ª pressao: arma a accao e muda a cor do botao correspondente.
        2.ª pressao da MESMA accao: executa.
        Pressao de OUTRA accao: cancela a 1.ª e arma a nova."""
        if self._console2_pending == action:
            # 2.ª pressao da mesma accao -> executa
            self._console2_pending = None
            self._console2_refresh_armed_visuals()
            self._console2_execute(action)
        else:
            # arma esta accao (cancela a anterior, se houver)
            self._console2_pending = action
            self._console2_refresh_armed_visuals()

    def _console2_cancel(self):
        """Cancela qualquer accao armada (4.º botao em modo gravacao)."""
        if self._console2_pending is not None:
            self._console2_pending = None
            self._console2_refresh_armed_visuals()

    def _console2_refresh_armed_visuals(self):
        """Actualiza a cor dos botoes COMPRAR/ATUALIZA/GUARDA conforme o
        estado armado. ARMED = amarelo (vivo), facil de notar."""
        ARMED = '#f1c40f'        # amarelo vivo = pronto para confirmar
        # Comprar  : base vermelho (#c0392b), armed amarelo
        if hasattr(self, '_comprar_btn'):
            if self._console2_pending == 'comprar':
                self._comprar_btn.config(bg=ARMED)
            else:
                self._update_comprar_btn()    # repoe (#c0392b ou #e67e22 se _record_armed)
        # Actualiza: base laranja escuro (#b9770e), armed amarelo
        if hasattr(self, '_actualiza_btn'):
            self._actualiza_btn.config(
                bg=ARMED if self._console2_pending == 'actualiza' else '#b9770e')
        # Guarda   : base turquesa (#16a085), armed amarelo
        if hasattr(self, '_guarda_btn'):
            self._guarda_btn.config(
                bg=ARMED if self._console2_pending == 'guarda' else '#16a085')

    def _console2_execute(self, action):
        """Executa directamente, SEM abrir dialogos (diferente do mouse na app)."""
        if action == 'comprar':
            self._console2_save_next_cue()
        elif action == 'actualiza':
            self._console2_update_current_cue()
        elif action == 'guarda':
            self._save_show()    # gravar show no ficheiro

    def _console2_save_next_cue(self):
        """COMPRAR via consola 2: grava o ESTADO ACTUAL do programmer como a
        proxima cue (numero auto-incrementado), com tempos default 3 s in/out.
        Nao abre dialogo nenhum."""
        nums = [c['num'] for c in self.engine.cues if not c.get('zero')]
        if not nums:
            next_n = 1.0
        else:
            try:
                next_n = round(float(nums[-1]) + 1, 1)
            except (ValueError, TypeError):
                next_n = 1.0
        self._capture_undo()
        self.engine.record_cue(next_n, '', 3.0, 3.0)
        self._refresh()

    def _console2_update_current_cue(self):
        """ATUALIZA via consola 2: actualiza a cue actual com o estado actual
        do programmer. Sem dialogo de confirmacao."""
        idx = self.engine.current_cue_idx
        if not (0 <= idx < len(self.engine.cues)): return
        cue = self.engine.cues[idx]
        if cue.get('zero'): return     # nao actualizar a ZERO
        if hasattr(self.engine, 'update_cue'):
            self._capture_undo()
            self.engine.update_cue(idx)
        self._refresh()

    def _record(self):
        dlg = RecordCueDialog(self.root, self.engine)
        self.root.wait_window(dlg)
        if dlg.result:
            self._capture_undo()
            self.engine.record_cue(*dlg.result)
            self._refresh()

    # ── undo / redo (1 nível) ─────────────────
    def _take_snap(self):
        """Fotografia completa = (estrutura, estado vivo)."""
        return (self.engine.snapshot(), self.engine.live_snapshot())

    def _capture_undo(self):
        """Guarda uma fotografia (estrutura + estado vivo) ANTES de uma edição,
        para o Ctrl+Z. Uma edição nova invalida o redo."""
        try:
            self._undo_snap = self._take_snap()
        except Exception:
            self._undo_snap = None
        self._redo_snap = None
        self._prog_cap_t = time.time()

    def _prog_checkpoint(self):
        """Captura undo no INÍCIO de um gesto de programação (debounce ~1.5 s):
        várias mexidas seguidas contam como UM passo; o Ctrl+Z reverte o gesto
        manual (subir/baixar à mão) inteiro."""
        if time.time() - getattr(self, '_prog_cap_t', 0.0) > 1.5:
            self._capture_undo()

    def _restore_snapshot(self, snap):
        """Restaura uma fotografia (estrutura + estado vivo), preservando o que
        estava em palco (programador/saída/posição)."""
        show_json, live = snap
        try:
            data = json.loads(show_json)
        except Exception:
            return
        with self.engine._lock:
            self.engine._load_data(data)
        self.engine.sync_sacn_outputs()
        self.engine.restore_live(live)        # repõe programador/saída/posição
        self._selected = {c for c in self._selected if 1 <= c <= NUM_CHANNELS}
        self._push_all_channel_names()
        self._refresh()

    def _undo(self, event=None):
        if not self._undo_snap:
            self._status_var.set(T('m.undo_none'))
            return 'break'
        cur = self._take_snap()
        self._restore_snapshot(self._undo_snap)
        self._redo_snap = cur
        self._undo_snap = None
        self._prog_cap_t = time.time()
        self._status_var.set(T('m.undo_done'))
        return 'break'

    def _redo(self, event=None):
        if not self._redo_snap:
            return 'break'
        cur = self._take_snap()
        self._restore_snapshot(self._redo_snap)
        self._undo_snap = cur
        self._redo_snap = None
        self._prog_cap_t = time.time()
        self._status_var.set(T('m.redo_done'))
        return 'break'

    # ── COMPRAR e retratos ────────────────────
    def _comprar(self):
        """1ª vez arma; clicar num retrato grava o retrato; COMPRAR de novo
        (2ª vez) abre a caixa para gravar uma memória."""
        if self._record_armed:
            self._record_armed = False
            self._update_comprar_btn()
            self._record()
        else:
            self._record_armed = True
            if self._delete_armed:              # exclusivo com o APAGAR
                self._delete_armed = False
                self._update_apagar_btn()
            self._update_comprar_btn()

    def _update_comprar_btn(self):
        self._comprar_btn.config(bg='#e67e22' if self._record_armed else '#c0392b')

    def _apagar(self):
        """APAGAR: 1ª vez ARMA (clicar num grupo/retrato apaga-o); 2ª vez
        (APAGAR de novo) abre o menu de apagar memórias (cues)."""
        if self._delete_armed:
            self._delete_armed = False
            self._update_apagar_btn()
            self._delete_cue()
        else:
            self._delete_armed = True
            if self._record_armed:              # exclusivo com o COMPRAR
                self._record_armed = False
                self._update_comprar_btn()
            self._update_apagar_btn()

    def _update_apagar_btn(self):
        if hasattr(self, '_apagar_btn'):
            self._apagar_btn.config(
                bg='#e67e22' if self._delete_armed else '#2c3e80')

    def _delete_retrato(self, idx):
        """Apaga o retrato idx (com APAGAR armado + clique)."""
        if 0 <= idx < len(self.engine.retratos) and self.engine.retratos[idx]:
            self._capture_undo()
            self.engine.retratos[idx] = None
            self._refresh_retratos()
            self._mark_dirty()

    def _delete_group(self, idx):
        """Apaga o grupo idx (com APAGAR armado + clique)."""
        if 0 <= idx < len(self.engine.groups) and self.engine.groups[idx]:
            self._capture_undo()
            self.engine.groups[idx] = None
            self._refresh_groups()
            self._mark_dirty()

    def _retrato_click(self, idx):
        if self._delete_armed:
            self._delete_armed = False
            self._update_apagar_btn()
            self._delete_retrato(idx)
        elif self._record_armed:
            self._record_armed = False
            self._update_comprar_btn()
            self._save_retrato(idx)
        else:
            r = self.engine.retratos[idx]
            levels = r.get('levels') if r else None
            if levels:
                retr_chs = {int(c) for c in levels
                            if 1 <= int(c) <= NUM_CHANNELS}
                if self._selected:
                    # v6.2: HÁ selecção → só os canais seleccionados que também
                    # pertencem a este retrato vão para os valores gravados; os
                    # restantes do retrato ficam como estão. A selecção mantém-se
                    # (não se junta o resto do retrato).
                    # v6.3.3: a selecção EXPANDE-SE pela alcunha — ter o DIM
                    # do aparelho seleccionado chega para o retrato actuar
                    # nos R/G/B/W… do mesmo aparelho (mesma alcunha).
                    self.engine.recall_retrato(
                        idx, only=self.engine.alias_family(self._selected))
                else:
                    # SEM selecção → comportamento de sempre: aplica TODO o
                    # retrato e junta os seus canais à selecção.
                    self.engine.recall_retrato(idx)
                    self._selected |= retr_chs
                self._update_sel_label()
            self._refresh()

    def _save_retrato(self, idx):
        r = self.engine.retratos[idx]
        dlg = RetratoDialog(self.root,
                            title_init=(r.get('title', '') if r else ''),
                            halo_init=(r.get('halo') if r else None))
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        title, halo = dlg.result
        if not title:
            title = T('ui.snapshot_n', n=idx + 1)
        self._capture_undo()
        self.engine.save_retrato(idx, title, halo)
        self._refresh_retratos()

    @staticmethod
    def _dim(hexcol, factor=0.55):
        r = int(hexcol[1:3], 16)
        g = int(hexcol[3:5], 16)
        b = int(hexcol[5:7], 16)
        return f'#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}'

    def _refresh_retratos(self):
        for i, b in enumerate(self._retrato_btns):
            r = self.engine.retratos[i] if i < len(self.engine.retratos) else None
            if r:
                halo = r.get('halo')
                bg = (self._dim(HALO_COLORS[halo]) if halo in HALO_COLORS
                      else '#3a4a6a')
                b.config(text=r.get('title') or T('ui.snapshot_n', n=i + 1),
                         bg=bg, fg='#ffffff')
            else:
                b.config(text=T('ui.snapshot_n', n=i + 1),
                         bg='#2c2c44', fg='#888899')

    # ── submasters ────────────────────────────
    def _on_sub_slider(self, idx, val):
        if self._sub_guard:
            return
        self.engine.set_submaster_fader(idx, int(float(val)))
        self._draw_channels()        # a grelha mostra o HTP em tempo real

    def _submaster_click(self, idx):
        """Com COMPRAR armado grava a luz no submaster; com APAGAR armado
        apaga (limpa) o submaster."""
        if self._delete_armed:
            self._delete_armed = False
            self._update_apagar_btn()
            self._delete_submaster(idx)
        elif self._record_armed:
            self._record_armed = False
            self._update_comprar_btn()
            self._save_submaster(idx)

    def _delete_submaster(self, idx):
        """Apaga (limpa) a luz gravada no submaster idx."""
        if 0 <= idx < len(self.engine.submasters):
            sm = self.engine.submasters[idx]
            if sm.get('levels'):
                self._capture_undo()
                sm['levels'] = {}
                sm['name'] = T('sub.default_n', n=idx + 1)
                self._refresh_submasters()
                self._mark_dirty()

    def _save_submaster(self, idx):
        sm = self.engine.submasters[idx]
        dlg = ValueDialog(self.root, T('sub.save_title'),
                          T('sub.name_prompt'), sm.get('name', ''))
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        nome = dlg.result.strip() or T('sub.default_n', n=idx + 1)
        self._capture_undo()
        self.engine.save_submaster(idx, nome)
        self._refresh_submasters()

    def _refresh_submasters(self):
        for i, btn in enumerate(self._sub_btns):
            sm = self.engine.submasters[i]
            nome = sm.get('name') or f"Sub {i + 1}"
            tem_luz = bool(sm.get('levels'))
            btn.config(text=nome, bg='#5a3a7a' if tem_luz else '#3a3a4a')
            self._sub_guard = True
            self._sub_scales[i].set(sm.get('fader', 0))
            self._sub_guard = False

    # ── grupos de canais ──────────────────────
    def _group_click(self, idx):
        """Sem COMPRAR/APAGAR armado: chama o grupo (selecciona os seus canais).
        Com COMPRAR armado: grava a selecção; com APAGAR armado: apaga o grupo."""
        if self._delete_armed:
            self._delete_armed = False
            self._update_apagar_btn()
            self._delete_group(idx)
            return
        if self._record_armed:
            self._record_armed = False
            self._update_comprar_btn()
            self._save_group(idx)
            return
        g = self.engine.groups[idx]
        if not g or not g.get('channels'):
            return                       # grupo vazio — nada a chamar
        # aditiva — junta os canais do grupo à selecção actual
        self._selected |= {c for c in g['channels'] if 1 <= c <= NUM_CHANNELS}
        self._update_sel_label()
        self._draw_channels()

    def _save_group(self, idx):
        """Guarda a selecção actual no grupo idx (nome + cor de halo)."""
        if not self._selected:
            messagebox.showinfo(T('ui.groups'), T('m.group_need_sel'))
            return
        g = self.engine.groups[idx]
        dlg = RetratoDialog(self.root,
                            title_init=(g.get('name', '') if g else ''),
                            halo_init=(g.get('halo') if g else None),
                            win_title=T('rdlg.title_group'))
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        nome, halo = dlg.result
        if not nome:
            nome = T('ui.group_n', n=idx + 1)
        self._capture_undo()
        self.engine.groups[idx] = {'name': nome, 'halo': halo,
                                   'channels': sorted(self._selected)}
        self._refresh_groups()

    def _refresh_groups(self):
        for i, b in enumerate(self._group_btns):
            g = self.engine.groups[i] if i < len(self.engine.groups) else None
            if g and g.get('channels'):
                nome = g.get('name') or T('ui.group_n', n=i + 1)
                halo = g.get('halo')
                bg = (self._dim(HALO_COLORS[halo]) if halo in HALO_COLORS
                      else '#1f6f6a')
                b.config(text=nome, bg=bg, fg='#ffffff')
            else:
                b.config(text=T('ui.group_n', n=i + 1),
                         bg='#2c2c44', fg='#888899')

    def _toggle_zero(self):
        """Activa/desactiva a memória ZERO no ciclo da lista."""
        if self.engine.cues and self.engine.cues[0].get('zero'):
            self.engine.cues[0]['enabled'] = self._zero_var.get()
            self._refresh()

    def _delete_cue(self):
        """Pergunta que memória(s) apagar — aceita 'N', 'N ao M', 'N + M + …'."""
        dlg = ValueDialog(self.root, T('m.del_title'), T('m.del_prompt'), "")
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        intervals = parse_memory_expr(dlg.result)
        if not intervals:
            messagebox.showerror(T('m.del_short_title'), T('m.del_indicate'))
            return
        to_del = []
        for i, c in enumerate(self.engine.cues):
            if c.get('zero'):
                continue
            n = c['num']
            if any(lo - 1e-6 <= n <= hi + 1e-6 for lo, hi in intervals):
                to_del.append((i, n))
        if not to_del:
            messagebox.showwarning(T('m.del_short_title'), T('m.del_none'))
            return
        nums = ", ".join(f"{n:g}" for _, n in to_del)
        if messagebox.askyesno(T('m.del_short_title'),
                               T('m.del_confirm', n=len(to_del), nums=nums)):
            self._capture_undo()
            for i, _ in reversed(to_del):   # de trás p/ a frente: índices estáveis
                self.engine.delete_cue(i)
            self._refresh()

    def _update_cue(self):
        """Actualiza a memória sob a barra com os valores actualmente em palco."""
        idx = self.engine.current_cue_idx
        if not (0 <= idx < len(self.engine.cues)):
            messagebox.showinfo(T('btn.update'), T('m.upd_position'))
            return
        if self.engine.cues[idx].get('zero'):
            messagebox.showinfo(T('btn.update'), T('m.upd_zero'))
            return
        cue_n = self.engine.cues[idx]['num']
        if messagebox.askyesno(T('btn.update'),
                               T('m.upd_confirm', n=f"{cue_n:g}")):
            self._capture_undo()
            self.engine.update_cue(idx)
            self._refresh()

    def _goto_selected(self):
        """Pergunta o número da memória e vai para ela (com os tempos dela)."""
        if not self.engine.cues:
            return
        dlg = ValueDialog(self.root, T('btn.goto'),
                          T('m.goto_prompt'), "",
                          extra=(T('m.goto_zero_btn'), "zero"))
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        txt = dlg.result.strip()
        if txt.lower() == 'zero':
            self.engine.goto(0)
            self._refresh()
            return
        try:
            num = round(float(txt.replace(',', '.')), 2)
        except ValueError:
            messagebox.showerror(T('btn.goto'), T('m.err_number'))
            return
        for i, c in enumerate(self.engine.cues):
            if not c.get('zero') and abs(c['num'] - num) < 1e-6:
                self.engine.goto(i)
                self._refresh()
                return
        messagebox.showwarning(T('btn.goto'), T('m.goto_missing', n=f"{num:g}"))

    # ── setas de sequência: movem a barra da lista (sem transições) ──
    def _seq_prev(self):
        self._move_cursor(-1)

    def _seq_next(self):
        self._move_cursor(+1)

    def _move_cursor(self, delta):
        """As setas <<< / >>> movem a barra da lista de memórias (em ciclo)
        e mostram os valores dessa memória — sem disparar transições nem
        encadeados. O VAI passa a continuar a partir desta posição."""
        if delta > 0:
            new_idx = self.engine.next_index(self.engine.current_cue_idx)
        else:
            new_idx = self.engine.prev_index(self.engine.current_cue_idx)
        if new_idx is None:
            return
        self.engine.set_position(new_idx)
        self._refresh()

    def _tree_click(self, event):
        """Clicar numa célula edita essa coluna (não move a barra)."""
        row = self._tree.identify_row(event.y)
        col = self._tree.identify_column(event.x)
        if row != '':
            self._edit_cell(int(row), col)

    def _tree_right(self, event):
        """Botão direito na cuelist principal (XF) → abre SEMPRE a janela de
        links de FX dessa memória, em qualquer situação."""
        row = self._tree.identify_row(event.y)
        if row != '':
            try:
                self._open_fx_link_dialog(int(row))
            except ValueError:
                pass

    @staticmethod
    def _to_float(txt, minimum=0.0):
        """Converte texto para float (aceita vírgula); None se inválido."""
        try:
            return max(minimum, float(txt.strip().replace(',', '.')))
        except ValueError:
            return None

    def _edit_cell(self, idx, col):
        """Abre um diálogo para editar o campo da coluna clicada."""
        if not (0 <= idx < len(self.engine.cues)):
            return
        cue = self.engine.cues[idx]
        fi, fo = self._cue_fades(cue)
        di, do = self._cue_delays(cue)
        fol = cue.get('follow')
        is_zero = cue.get('zero')

        if is_zero and col == '#1':
            messagebox.showinfo(T('m.zero_title'), T('m.zero_no_renum'))
            return
        if is_zero and col == '#6':
            messagebox.showinfo(T('m.zero_title'), T('m.zero_toggle'))
            return

        # ── coluna BARREIRA (#2) → toggle, sem dialogo ──
        if col == '#2':
            if is_zero:
                messagebox.showinfo(T('m.barr_title'), T('m.barr_zero'))
                return
            actual = bool(cue.get('barreira', False))
            self.engine.set_cue_field(idx, 'barreira', not actual)
            self._refresh()
            return

        # ── colunas Entr. / Saí. → tempo + atraso (dois valores) ──
        if col in ('#4', '#5'):
            if col == '#4':
                dlg = MultiValueDialog(self.root, T('m.edit_in_title'),
                                       [(T('m.edit_in_time'), f"{fi:g}"),
                                        (T('m.edit_in_delay'), f"{di:g}")])
            else:
                dlg = MultiValueDialog(self.root, T('m.edit_out_title'),
                                       [(T('m.edit_out_time'), f"{fo:g}"),
                                        (T('m.edit_out_delay'), f"{do:g}")])
            self.root.wait_window(dlg)
            if dlg.result is None:
                return
            fade = self._to_float(dlg.result[0])
            delay = self._to_float(dlg.result[1])
            if fade is None or delay is None:
                messagebox.showerror(T('common.error'), T('m.err_values'))
                return
            if col == '#4':
                self.engine.set_cue_field(idx, 'fade_in', fade)
                self.engine.set_cue_field(idx, 'delay_in', delay)
            else:
                self.engine.set_cue_field(idx, 'fade_out', fade)
                self.engine.set_cue_field(idx, 'delay_out', delay)
            self._refresh()
            return

        # ── colunas de valor único ──
        if col == '#3':
            dlg = ValueDialog(self.root, T('m.edit_cue_title'),
                              T('rec.f_label'), cue.get('label', ''))
            self.root.wait_window(dlg)
            if dlg.result is not None:
                self.engine.set_cue_field(idx, 'label', dlg.result.strip())
                self._refresh()
        elif col == '#6':
            dlg = ValueDialog(self.root, T('m.edit_cue_title'),
                              T('m.edit_auto_prompt'),
                              '' if fol is None else f"{fol:g}")
            self.root.wait_window(dlg)
            if dlg.result is None:
                return
            txt = dlg.result.strip()
            if txt == '':
                self.engine.set_cue_field(idx, 'follow', None)
            else:
                val = self._to_float(txt)
                if val is None:
                    messagebox.showerror(T('common.error'), T('m.err_value'))
                    return
                self.engine.set_cue_field(idx, 'follow', val)
            self._refresh()
        elif col == '#1':
            dlg = ValueDialog(self.root, T('m.edit_cue_title'),
                              T('m.edit_num_prompt'),
                              f"{cue['num']:g}")
            self.root.wait_window(dlg)
            if dlg.result is None:
                return
            val = self._to_float(dlg.result)
            if val is None:
                messagebox.showerror(T('common.error'), T('m.err_number'))
                return
            self.engine.renumber_cue(idx, round(val, 2))
            self._refresh()
        elif col == '#7':
            if is_zero:
                messagebox.showinfo(T('m.loop_title'), T('m.loop_zero'))
                return
            tgt = cue.get('salta_target')
            cnt = int(cue.get('salta_count', 0) or 0)
            dlg = MultiValueDialog(self.root, T('m.loop_edit_title'),
                [(T('m.loop_target_prompt'),
                  '' if tgt is None else f"{tgt:g}"),
                 (T('m.loop_count_prompt'),
                  '' if (tgt is None or cnt == 0) else str(cnt))])
            self.root.wait_window(dlg)
            if dlg.result is None:
                return
            t_txt = dlg.result[0].strip().replace(',', '.')
            c_txt = dlg.result[1].strip().replace(',', '.')
            if t_txt == '':
                self.engine.set_cue_field(idx, 'salta_target', None)
                self.engine.set_cue_field(idx, 'salta_count', None)
                self._refresh()
                return
            try:
                t_num = round(float(t_txt), 2)
            except ValueError:
                messagebox.showerror(T('common.error'), T('m.loop_bad_num'))
                return
            if self.engine._find_cue_index(t_num) is None:
                messagebox.showerror(T('m.loop_title'),
                                     T('m.goto_missing', n=f"{t_num:g}"))
                return
            if t_num >= cue['num']:
                messagebox.showerror(T('m.loop_title'), T('m.loop_backwards'))
                return
            try:
                cnt_val = max(0, int(float(c_txt))) if c_txt else 0
            except ValueError:
                messagebox.showerror(T('common.error'), T('m.loop_bad_count'))
                return
            self.engine.set_cue_field(idx, 'salta_target', t_num)
            self.engine.set_cue_field(idx, 'salta_count', cnt_val)
            self._refresh()
        elif col == '#8':
            # v5 etapa 4 — coluna FX: liga/desliga um efeito a partir da
            # sequência (a mesma marca mais à frente tira-o; tracking).
            # Na página XF o link rápido NÃO se aplica (só na página FX): o
            # esquerdo abre sempre a janela; o ciclo rápido vive no espelho FX.
            self._open_fx_link_dialog(idx)
        elif col == '#9':
            self._open_midi_dialog(idx)     # v6.3 — coluna MIDI

    def _open_osc_help(self):
        """v6.3 — Ajuda OSC (referência do protocolo) numa janela própria,
        acessível pelo menu «Ajuda» (saiu das Configurações)."""
        win = tk.Toplevel(self.root)
        win.title(T('osc_help.title'))
        win.geometry("760x560")
        win.transient(self.root)
        txt = tk.Text(win, wrap=tk.NONE, font=('Courier', 9),
                      relief=tk.FLAT, borderwidth=0, padx=6, pady=6)
        sbv = ttk.Scrollbar(win, orient=tk.VERTICAL, command=txt.yview)
        sbh = ttk.Scrollbar(win, orient=tk.HORIZONTAL, command=txt.xview)
        txt.configure(yscrollcommand=sbv.set, xscrollcommand=sbh.set)
        txt.insert(tk.END, osc_reference_text())
        txt.config(state=tk.DISABLED)
        sbv.pack(side=tk.RIGHT, fill=tk.Y)
        sbh.pack(side=tk.BOTTOM, fill=tk.X)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _open_midi_dialog(self, idx):
        """v6.3 — edita o MIDI da cue idx (duplo-clique na coluna MIDI)."""
        if not (0 <= idx < len(self.engine.cues)):
            return
        c = self.engine.cues[idx]
        dlg = MidiCueDialog(self.root, self._cue_num_txt(c),
                            c.get('midi_direccao'), c.get('midi_nota'),
                            c.get('midi_delay_s', 0.0))
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        d, nota, s = dlg.result
        self.engine.set_cue_field(idx, 'midi_direccao', d)
        self.engine.set_cue_field(idx, 'midi_nota', nota)
        self.engine.set_cue_field(idx, 'midi_delay_s', s)
        self._refresh()

    # ── refresh ───────────────────────────────
    def _refresh(self):
        # v6: desenha a vista activa (mesa ou monitor DMX); a outra está
        # escondida, não vale gastar CPU a desenhá-la
        if getattr(self, '_chan_view', 'mesa') == 'dmx':
            self._draw_dmx()
        else:
            self._draw_channels()
        self._refresh_cue_panel()
        self._refresh_status()
        self._update_pause_btn()
        self._update_soltar_btn()
        self._update_fade_bar()
        self._refresh_retratos()
        self._refresh_groups()
        self._refresh_submasters()
        self._update_comprar_btn()
        self._update_apagar_btn()     # v6.2: cor do APAGAR (armado)
        self._refresh_fx()            # v5
        self._fx_refresh_editor()     # v5: linha verde segue o loop
        self._update_hs_btns()        # v5: cor dos botões Highlight/Solo
        self._refresh_im_btn()        # v6.2: botão do modelo da cuelist

    def _update_fade_bar(self):
        """Mostra o progresso da transição lançada pelo VAI, ou o COUNTDOWN
        do AUTO (barra laranja) enquanto se espera a entrada automática."""
        if self.engine.fading:
            p = self.engine.fade_progress
            self._fade_bar['value'] = p * 100
            self._fade_lbl.config(
                text=f"{self.engine.fade_remaining:0.1f}s",
                foreground='#e8d44d')
            self._fade_bar.config(
                style='Auto.Horizontal.TProgressbar' if self.engine.auto_fade
                else 'Fade.Horizontal.TProgressbar')
            if getattr(self, '_back_fading', False):
                self._back_btn.config(bg='#2980b9')
        elif self.engine.follow_armed:
            # AUTO em countdown — barra laranja a encher até à entrada
            p = self.engine.follow_progress
            self._fade_bar['value'] = p * 100
            self._fade_bar.config(style='Count.Horizontal.TProgressbar')
            remaining = max(0.0, self.engine.follow_at - time.time())
            self._fade_lbl.config(text=f"{remaining:0.1f}s",
                                  foreground='#e67e22')
        else:
            self._fade_bar['value'] = 0
            self._fade_lbl.config(text="—", foreground='#7f8c8d')
            self._back_fading = False
            self._back_btn.config(bg='#2c3e50')

    @staticmethod
    def _cue_fades(c):
        """Devolve (fade_in, fade_out) de um cue, com fallback p/ shows antigos."""
        legacy = c.get('fade', 0)
        return c.get('fade_in', legacy), c.get('fade_out', legacy)

    @staticmethod
    def _cue_delays(c):
        """Devolve (delay_in, delay_out) de um cue."""
        return c.get('delay_in', 0) or 0, c.get('delay_out', 0) or 0

    @staticmethod
    def _cue_num_txt(c):
        return "ZERO" if c.get('zero') else f"{c['num']:g}"

    @staticmethod
    def _time_txt(delay, fade):
        """'5s' ou '2+5s' quando há atraso."""
        return f"{delay:g}+{fade:g}s" if delay > 0 else f"{fade:g}s"

    @staticmethod
    def _salta_txt(c):
        """'—', '→1 ×3' (saltos finitos) ou '→1 ∞' (eterno)."""
        tgt = c.get('salta_target')
        if tgt is None:
            return "—"
        cnt = int(c.get('salta_count', 0) or 0)
        return f"→{tgt:g} ∞" if cnt == 0 else f"→{tgt:g} ×{cnt}"

    @staticmethod
    def _fx_link_txt(c):
        """Coluna FX: '3⚡' (imediato) ou '3∿' (acompanha o fade); '·' sem
        marca. A marca alterna o FX: liga numa memória, desliga noutra.
        v6.3.3 — FX lançados pelas PARTES aparecem com o nº da parte:
        'P2·4∿' (o Treeview não pinta células individuais; o P2 é a
        informação — decisão do autor 2026-07-07)."""
        s = '·'
        ln = c.get('fx_link')
        if isinstance(ln, dict):
            try:
                n = int(ln.get('num', 0))
            except (TypeError, ValueError):
                n = 0
            if 1 <= n <= NUM_FX:
                s = f"{n}∿" if ln.get('fade') else f"{n}⚡"
        extra = []
        for k in sorted((c.get('parts') or {}), key=int):
            fx = c['parts'][k].get('fx')
            if isinstance(fx, dict):
                extra.append('P%s·%d%s' % (k, int(fx.get('num', 0)),
                                           '∿' if fx.get('fade') else '⚡'))
        if extra:
            return (('' if s == '·' else s + ' ') + ' '.join(extra))
        return s

    @staticmethod
    def _midi_txt(c):
        """v6.3 — texto da coluna MIDI: '—' | 'OUT 1' | 'IN 10' |
        'OUT 2 +0.5s'."""
        d = c.get('midi_direccao')
        n = c.get('midi_nota')
        if d not in ('in', 'out') or n is None:
            return "—"
        s = f"{'OUT' if d == 'out' else 'IN'} {int(n)}"
        delay = float(c.get('midi_delay_s', 0) or 0)
        if delay > 0:
            s += f" +{delay:g}s"
        return s

    # ── PARTES (v6.3.3) ───────────────────────
    _PARTE_COR = '#b03a3a'      # vermelho não muito escuro (decisão autor)

    @staticmethod
    def _parte_txt(c):
        """Texto da coluna PARTE: '—' ou 'P2' / 'P2+3' (nºs das partes)."""
        pts = c.get('parts') or {}
        if not pts:
            return "—"
        return 'P' + '+'.join(sorted(pts, key=int))

    def _parte_desarma(self):
        """Sai do estado de criação/edição de parte (vermelho apagado)."""
        self._parte_mod = None
        self._parte_canais = set()
        self._parte_btn.config(bg='#33415c')
        self._status_var.set("MESADELUX")
        self._draw_channels()

    def _on_parte(self):
        """Tecla PARTE (fluxo do autor 2026-07-07):
        · a editar uma parte (vermelho armado) → reabre o menu dos tempos;
        · com canais seleccionados → cria uma parte na memória ACTUAL;
        · sem selecção e memória dividida → lista Modificar/Apagar."""
        eng = self.engine
        if self._parte_mod is not None:              # edição em curso
            self._parte_dialog(self._parte_mod['idx'],
                               self._parte_mod['num'])
            return
        idx = eng.current_cue_idx
        if not (1 <= idx < len(eng.cues)) or eng.cues[idx].get('zero'):
            messagebox.showinfo(T('parte.title'), T('parte.need_cue'))
            return
        if self._selected:
            livre = None
            usados = set(int(k) for k in
                         (eng.cues[idx].get('parts') or {}))
            for n in range(2, NUM_PARTS + 1):
                if n not in usados:
                    livre = n
                    break
            if livre is None:
                messagebox.showinfo(T('parte.title'),
                                    T('parte.cheia', max=NUM_PARTS))
                return
            self._parte_canais = set(self._selected)
            self._parte_btn.config(bg=self._PARTE_COR)
            self._draw_channels()
            self._parte_dialog(idx, None, sugestao=livre)
        elif eng.cues[idx].get('parts'):
            self._parte_lista(idx)
        else:
            messagebox.showinfo(T('parte.title'), T('parte.need_sel'))

    def _parte_lista(self, idx):
        """Lista das partes da memória idx: Modificar / Apagar a parte."""
        cue = self.engine.cues[idx]
        dlg = tk.Toplevel(self.root)
        dlg.title(T('parte.title'))
        dlg.configure(bg='#1a1a2e')
        dlg.transient(self.root)
        dlg.grab_set()

        def _fecha():
            dlg.destroy()

        def _modificar(n):
            p = (cue.get('parts') or {}).get(str(n))
            if not p:
                return
            self._parte_mod = {'idx': idx, 'num': n}
            self._parte_canais = set(p.get('channels', []))
            self._parte_btn.config(bg=self._PARTE_COR)
            self._status_var.set(T('parte.mod_hint', n=n))
            self._draw_channels()
            dlg.destroy()

        def _apagar(n):
            self._capture_undo()
            pts = cue.get('parts') or {}
            pts.pop(str(n), None)
            if not pts:
                cue.pop('parts', None)
            self._mark_dirty()
            self._refresh_cue_panel()
            dlg.destroy()

        for n in sorted((cue.get('parts') or {}), key=int):
            p = cue['parts'][n]
            row = tk.Frame(dlg, bg='#1a1a2e')
            row.pack(fill=tk.X, padx=10, pady=3)
            txt = 'P%s · %s' % (n, T('parte.canais',
                                     n=len(p.get('channels', []))))
            if p.get('label'):
                txt += ' · ' + p['label']
            tk.Label(row, text=txt, bg='#1a1a2e', fg='#ccccee',
                     font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 12))
            tk.Button(row, text=T('parte.del'), bg='#7a2020', fg='white',
                      relief=tk.FLAT, cursor='hand2',
                      command=lambda k=int(n): _apagar(k)
                      ).pack(side=tk.RIGHT, padx=2)
            tk.Button(row, text=T('parte.mod'), bg='#2c3e80', fg='white',
                      relief=tk.FLAT, cursor='hand2',
                      command=lambda k=int(n): _modificar(k)
                      ).pack(side=tk.RIGHT, padx=2)
        tk.Button(dlg, text=T('parte.fechar'), command=_fecha,
                  bg='#33415c', fg='white', relief=tk.FLAT,
                  cursor='hand2').pack(pady=(6, 10))

    def _parte_dialog(self, idx, num, sugestao=None):
        """Menu da parte (criação num=None, ou edição da parte num):
        nº 1-8, tempos IN/OUT + atrasos, FX (∿/⚡), texto, OK/Cancelar.
        Nº 1 = a divisão principal (edita os tempos da própria memória)."""
        eng = self.engine
        if not (1 <= idx < len(eng.cues)):
            self._parte_desarma()
            return
        cue = eng.cues[idx]
        editar = num is not None
        p0 = (cue.get('parts') or {}).get(str(num)) if editar else None

        dlg = tk.Toplevel(self.root)
        dlg.title(T('parte.dlg_title', num=self._cue_num_txt(cue)))
        dlg.configure(bg='#1a1a2e')
        dlg.transient(self.root)
        dlg.grab_set()

        def _lab(r, chave):
            tk.Label(dlg, text=T(chave), bg='#1a1a2e', fg='#ccccee',
                     font=('Arial', 10)).grid(row=r, column=0, sticky='e',
                                              padx=(12, 6), pady=3)

        def _ent(r, valor):
            v = tk.StringVar(value=valor)
            e = tk.Entry(dlg, textvariable=v, width=8, bg='#2c2c44',
                         fg='white', insertbackground='white',
                         relief=tk.FLAT)
            e.grid(row=r, column=1, sticky='w', pady=3)
            return v

        _lab(0, 'parte.num')
        v_num = tk.StringVar(value=str(num if editar
                                       else (sugestao or 2)))
        # v6.3.3b — começa na 2: a parte 1 é SEMPRE a divisão principal
        # (a própria memória), assumida automaticamente
        sp = tk.Spinbox(dlg, from_=2, to=NUM_PARTS, textvariable=v_num,
                        width=6, bg='#2c2c44', fg='white', relief=tk.FLAT,
                        state='disabled' if editar else 'normal')
        sp.grid(row=0, column=1, sticky='w', pady=3)
        tk.Label(dlg, text=T('parte.p1_nota'), bg='#1a1a2e', fg='#8888aa',
                 font=('Arial', 8)).grid(row=1, column=0, columnspan=2,
                                         padx=12, sticky='w')
        src = p0 or {}
        v_fi = _ent(2, '%g' % float(src.get('fade_in',
                                            cue.get('fade_in', 3.0))))
        _lab(2, 'parte.fade_in')
        v_fo = _ent(3, '%g' % float(src.get('fade_out',
                                            cue.get('fade_out', 3.0))))
        _lab(3, 'parte.fade_out')
        v_di = _ent(4, '%g' % float(src.get('delay_in', 0.0)))
        _lab(4, 'parte.delay_in')
        v_do = _ent(5, '%g' % float(src.get('delay_out', 0.0)))
        _lab(5, 'parte.delay_out')
        fx0 = src.get('fx') or {}
        v_fx = _ent(6, str(fx0.get('num', '')) if fx0 else '')
        _lab(6, 'parte.fx')
        v_modo = tk.BooleanVar(value=bool(fx0.get('fade', True)))
        fr = tk.Frame(dlg, bg='#1a1a2e')
        fr.grid(row=7, column=0, columnspan=2, padx=12, sticky='w')
        tk.Radiobutton(fr, text=T('parte.fx_fade'), variable=v_modo,
                       value=True, bg='#1a1a2e', fg='#ccccee',
                       selectcolor='#2c2c44',
                       activebackground='#1a1a2e').pack(anchor='w')
        tk.Radiobutton(fr, text=T('parte.fx_snap'), variable=v_modo,
                       value=False, bg='#1a1a2e', fg='#ccccee',
                       selectcolor='#2c2c44',
                       activebackground='#1a1a2e').pack(anchor='w')
        _lab(8, 'parte.texto')
        v_txt = tk.StringVar(value=str(src.get('label', '')))
        tk.Entry(dlg, textvariable=v_txt, width=24, bg='#2c2c44',
                 fg='white', insertbackground='white',
                 relief=tk.FLAT).grid(row=8, column=1, sticky='w', pady=3)

        def _f(v, defeito=0.0):
            try:
                return max(0.0, float(str(v.get()).replace(',', '.')))
            except (TypeError, ValueError):
                return defeito

        def _ok():
            # v6.3.3b — a parte 1 é implícita: o menu só cria/edita 2-8
            n = max(2, min(NUM_PARTS, int(_f(v_num, 2))))
            fi, fo = _f(v_fi, 3.0), _f(v_fo, 3.0)
            di, do = _f(v_di), _f(v_do)
            fx_n = 0
            try:
                fx_n = int(float(str(v_fx.get()).strip() or 0))
            except (TypeError, ValueError):
                fx_n = 0
            self._capture_undo()
            canais = sorted(self._parte_canais)
            # v6.3.3b — canais AZUIS (programador) entram como
            # ACTUALIZAÇÃO directa da memória ao criar a parte
            # (pedido do autor: o valor azul fica registado na cue)
            eng.update_cue_channels(idx, canais)
            pts = cue.setdefault('parts', {})
            # regra USITT: um canal, uma parte — tira das outras
            for k, outra in list(pts.items()):
                if int(k) == n:
                    continue
                outra['channels'] = [c_ for c_ in outra['channels']
                                     if c_ not in canais]
                if not outra['channels']:
                    pts.pop(k)
            ent = {'channels': canais, 'fade_in': fi, 'fade_out': fo,
                   'delay_in': di, 'delay_out': do,
                   'label': str(v_txt.get() or '')[:40]}
            if 1 <= fx_n <= NUM_FX:
                ent['fx'] = {'num': fx_n, 'fade': bool(v_modo.get())}
                # v6.3.3 — um FX, uma marca por memória: sai da coluna
                # directa e das outras partes (a nova atribuição ganha)
                if self._fx_marca_unica(cue, fx_n, str(n)):
                    self._status_var.set(T('parte.fx_unica', n=fx_n))
            if canais:
                pts[str(n)] = ent
            else:
                pts.pop(str(n), None)    # parte esvaziada → apaga-se
            if not pts:
                cue.pop('parts', None)
            self._mark_dirty()
            self._refresh_cue_panel()
            dlg.destroy()
            self._parte_desarma()

        def _cancel():
            dlg.destroy()
            self._parte_desarma()

        bt = tk.Frame(dlg, bg='#1a1a2e')
        bt.grid(row=9, column=0, columnspan=2, pady=(8, 10))
        tk.Button(bt, text=T('parte.ok'), command=_ok, bg='#16a085',
                  fg='white', relief=tk.FLAT, width=10,
                  cursor='hand2').pack(side=tk.LEFT, padx=4)
        tk.Button(bt, text=T('parte.cancel'), command=_cancel,
                  bg='#7a2020', fg='white', relief=tk.FLAT, width=10,
                  cursor='hand2').pack(side=tk.LEFT, padx=4)
        dlg.protocol('WM_DELETE_WINDOW', _cancel)

    def _fill_cue_tree(self, tree):
        """Preenche um Treeview de memórias (o principal da XF ou o espelho
        da página FX). v5: partilhado para os dois ficarem sincronizados."""
        tree.delete(*tree.get_children())
        for i, c in enumerate(self.engine.cues):
            is_zero = c.get('zero')
            is_barr = bool(c.get('barreira', False)) and not is_zero
            if i == self.engine.current_cue_idx:
                tag = 'active'           # memoria activa - tem prioridade
            elif is_barr:
                tag = 'barreira'         # block cue - linha magenta
            elif is_zero:
                tag = 'zero' if c.get('enabled') else 'zerooff'
            else:
                tag = ''
            fi, fo = self._cue_fades(c)
            di, do = self._cue_delays(c)
            fol = c.get('follow')
            if is_zero:
                encad_txt = "ciclo" if c.get('enabled') else "fora"
            else:
                encad_txt = f"{fol:g}s" if fol is not None else "—"
            salta_txt = "—" if is_zero else self._salta_txt(c)
            barr_txt  = "—" if is_zero else ("◼" if is_barr else "·")
            fx_txt    = "—" if is_zero else self._fx_link_txt(c)
            midi_txt  = self._midi_txt(c)
            parte_txt = "—" if is_zero else self._parte_txt(c)   # v6.3.3
            tree.insert('', tk.END, iid=str(i),
                        values=(self._cue_num_txt(c), barr_txt,
                                c.get('label', ''),
                                self._time_txt(di, fi),
                                self._time_txt(do, fo),
                                encad_txt, salta_txt, fx_txt, midi_txt,
                                parte_txt),
                        tags=(tag,))
        idx = self.engine.current_cue_idx
        if 0 <= idx < len(self.engine.cues):
            tree.see(str(idx))

    def _refresh_cue_panel(self):
        self._fill_cue_tree(self._tree)
        # v5: se a página FX está a mostrar a cuelist (sem FX em edição),
        # mantém o espelho sincronizado
        mt = getattr(self, '_fx_cue_tree', None)
        if mt is not None and mt.winfo_exists():
            self._fill_cue_tree(mt)

        idx = self.engine.current_cue_idx
        if 0 <= idx < len(self.engine.cues):
            c = self.engine.cues[idx]
            self._cue_now_var.set(
                f"{self._cue_num_txt(c)}  |  {c.get('label', '')}")
        else:
            self._cue_now_var.set("—")

        # v6.4 — a cue que ENTRA a seguir (loop-aware), o MESMO que o motor
        # arma em _arm_follow; assim o cabeçalho e a execução coincidem.
        nxt = self.engine._peek_next_index()
        if nxt is not None and 0 <= nxt < len(self.engine.cues):
            nc = self.engine.cues[nxt]
            # v6.3+: o AUTO pertence à cue que ENTRA (a seguinte), como o
            # _arm_follow lê. Antes lia o follow da cue ACTUAL (aviso
            # antigo) e rotulava a cue errada como AUTO.
            fol = nc.get('follow')
            is_auto = fol is not None and fol >= 0
            extra = "  (AUTO)" if is_auto else ""
            self._cue_next_var.set(
                f"→ {self._cue_num_txt(nc)}  {nc.get('label', '')}{extra}")
            # próxima automática → texto roxo; manual → verde claro
            self._cue_next_lbl.config(foreground='#b06bff' if is_auto else '#90ee90')
        else:
            self._cue_next_var.set("→ —")
            self._cue_next_lbl.config(foreground='#90ee90')

        # sincroniza o estado da opção «ZERO no ciclo»
        self._zero_var.set(self.engine.zero_enabled)

    def _refresh_status(self):
        if self.engine.sacn_enabled:
            if self.engine.sacn_multicast:
                mode = "Mcast"
            else:
                mode = f"→{self.engine.sacn_unicast_ip or '?'}"
            univ_txt = "/".join("U" + str(u)
                                for u in self.engine.out_universes())
            if self.engine.universes_auto:
                univ_txt += "·auto"
            self._sacn_lbl.config(
                text=f"◉ sACN  {univ_txt}  {mode}", fg='#2ecc71')
        else:
            self._sacn_lbl.config(text="◉ sACN OFF", fg='#555577')

        # v4 — Art-Net
        if self.engine.artnet_enabled:
            if self.engine.artnet_broadcast:
                an_mode = "Bcast"
            else:
                an_mode = f"→{self.engine.artnet_dest_ip or '?'}"
            an_univ = "/".join("U" + str(u)
                               for u in self.engine.out_universes())
            self._artnet_lbl.config(
                text=f"◉ ArtNet  {an_univ}  {an_mode}", fg='#e67e22')
        else:
            self._artnet_lbl.config(text="◉ ArtNet OFF", fg='#555577')

        if self.osc_enabled:
            self._osc_lbl.config(text=f"◉ OSC←  :{self.osc_port}", fg='#3498db')
        else:
            self._osc_lbl.config(text="◉ OSC← OFF", fg='#555577')

        if self.osc_out_enabled and self._console_clients:
            self._osc_out_lbl.config(text=f"◉ OSC→  :{self.osc_out_port}", fg='#f39c12')
        else:
            self._osc_out_lbl.config(text="◉ OSC→ OFF", fg='#555577')

        # v6.3 — MIDI
        if HAS_MIDI:
            in_ok  = self._midi_in  is not None
            out_ok = self._midi_out is not None
            if in_ok or out_ok:
                parts = []
                if in_ok:
                    parts.append('IN●')
                if out_ok:
                    parts.append('OUT●')
                self._midi_lbl.config(
                    text='◉ MIDI ' + ' '.join(parts), fg='#9b59b6')
            else:
                self._midi_lbl.config(text='◉ MIDI OFF', fg='#555577')
        else:
            self._midi_lbl.config(text='◉ MIDI —', fg='#444455')

        # IP da interface de saida do sACN: mostra o que foi CONFIGURADO.
        # Se vazio, indica "auto" (kernel escolhe).
        bind = self.engine.sacn_bind_ip
        if bind:
            self._ip_lbl.config(text=f"bind: {bind}")
        else:
            ips = local_ips()
            hint = ips[0] if ips else '?'
            self._ip_lbl.config(text=f"bind: auto ({hint})")

    # ── MIDI (v6.3) ───────────────────────────
    def _open_midi_out(self):
        """Abre a porta MIDI OUT escolhida (se houver). Falha silenciosa se o
        dispositivo não estiver ligado — a app nunca rebenta por causa disso."""
        self._close_midi_out()
        if not (HAS_MIDI and self.midi_out_name):
            return
        try:
            self._midi_out = mido.open_output(self.midi_out_name)
        except Exception as e:
            print('[midi] erro a abrir OUT', self.midi_out_name, '->', e)
            self._midi_out = None

    def _close_midi_out(self):
        if self._midi_out is not None:
            try:
                self._midi_out.reset()   # All Notes Off antes de fechar
            except Exception:
                pass
            try:
                self._midi_out.close()
            except Exception:
                pass
            self._midi_out = None

    def apply_midi_ports(self, in_name, out_name):
        """Aplica a escolha de portas: persiste em ~/.mesadelux.json e reabre
        as portas (OUT já; IN na Etapa 5). Não reinicia a aplicação."""
        global MIDI_IN_PORT, MIDI_OUT_PORT
        self.midi_in_name = in_name
        self.midi_out_name = out_name
        MIDI_IN_PORT = in_name
        MIDI_OUT_PORT = out_name
        save_app_config()
        self._open_midi_out()
        self.start_midi_in()               # (Etapa 5: (re)arranca a escuta)
        self._refresh_status()

    def start_midi_in(self):
        """(Re)arranca a escuta MIDI IN. O mido chama o callback numa thread
        própria; nós só metemos a nota na fila e o pump (thread UI) trata."""
        self._close_midi_in()
        if not (HAS_MIDI and self.midi_in_name):
            return
        try:
            self._midi_in = mido.open_input(self.midi_in_name,
                                            callback=self._midi_in_callback)
        except Exception as e:
            print('[midi] erro a abrir IN', self.midi_in_name, '->', e)
            self._midi_in = None
        # garante que o pump da fila está a correr (uma só vez)
        if not self._midi_pump_started:
            self._midi_pump_started = True
            self.root.after(20, self._midi_pump)

    def _close_midi_in(self):
        if self._midi_in is not None:
            try:
                self._midi_in.close()
            except Exception:
                pass
            self._midi_in = None

    def _midi_in_callback(self, msg):
        """CORRE NA THREAD DO MIDO. Só Note On com velocidade > 0 conta
        (qualquer canal). Mete a nota na fila — NUNCA toca no Tkinter aqui."""
        try:
            if msg.type == 'note_on' and msg.velocity > 0:
                self._midi_queue.put(int(msg.note))
        except Exception:
            pass

    def _midi_pump(self):
        """(thread UI) Drena a fila de notas IN e dispara a 1ª cue que tenha
        essa nota em modo IN, respeitando o atraso (ms).
        O reagendamento está num finally — nunca morre mesmo com excepção."""
        try:
            while True:
                nota = self._midi_queue.get_nowait()
                if not self._midi_active:
                    continue           # MIDI desligado — descarta notas IN
                for idx, c in enumerate(self.engine.cues):
                    if (c.get('midi_direccao') == 'in'
                            and c.get('midi_nota') == nota):
                        s = float(c.get('midi_delay_s', 0) or 0)
                        if s > 0:
                            self._midi_delayed(
                                s, lambda i=idx: self._midi_execute_cue(i))
                        else:
                            self._midi_execute_cue(idx)
                        break            # só a 1.ª cue que corresponde
        except queue.Empty:
            pass
        except Exception as e:
            print('[midi] erro no pump:', e)
        finally:
            self.root.after(20, self._midi_pump)   # reagenda SEMPRE

    def _midi_execute_cue(self, idx):
        """(thread UI) Executa a cue idx com os tempos dela (como o «Ir Para»)."""
        if 0 <= idx < len(self.engine.cues):
            self.engine.goto(idx)
            self._disparar_midi_out()   # v6.3 — envia nota MIDI OUT se a cue tiver
            self._refresh()

    # ── MIDI OUT — envio de notas ─────────────
    def _disparar_midi_out(self):
        """Envia MIDI OUT para a cue actual (se tiver midi_direccao='out').
        Chamado após cada VAI, RECUA ou MIDI-IN executar uma cue."""
        if not self._midi_active:
            return                     # MIDI desligado pelo operador
        idx = self.engine.current_cue_idx
        if not (0 <= idx < len(self.engine.cues)):
            return
        cue = self.engine.cues[idx]
        if cue.get('midi_direccao') != 'out':
            return
        nota = cue.get('midi_nota')
        if nota is None:
            return
        s = float(cue.get('midi_delay_s', 0) or 0)
        if s > 0:
            self._midi_delayed(s, lambda n=nota: self._enviar_note_out(n))
        else:
            self._enviar_note_out(nota)

    def _enviar_note_out(self, nota):
        """Envia Note On + Note Off (100ms depois). Corre sempre na thread UI."""
        if not (HAS_MIDI and self._midi_out is not None):
            return
        try:
            self._midi_out.send(
                mido.Message('note_on', channel=0, note=int(nota), velocity=127))
            self.root.after(100, lambda n=nota: self._enviar_note_off(n))
        except Exception as e:
            print('[midi] erro note_on', nota, '->', e)

    def _enviar_note_off(self, nota):
        """Envia Note Off para a nota dada."""
        if not (HAS_MIDI and self._midi_out is not None):
            return
        try:
            self._midi_out.send(
                mido.Message('note_off', channel=0, note=int(nota), velocity=0))
        except Exception as e:
            print('[midi] erro note_off', nota, '->', e)

    # ── OSC ───────────────────────────────────
    def start_osc(self):
        if not HAS_OSC:
            messagebox.showerror("OSC", T('m.osc_install'))
            return
        try:
            d = osc_disp.Dispatcher()
            # v4: TUDO passa por um handler único que corre na thread do
            # servidor: aprende o IP da consola (origem do pacote) e agenda
            # o trabalho na fila da UI. NUNCA toca no Tkinter directamente.
            d.set_default_handler(self._osc_packet, needs_reply_address=True)

            self._osc_server = osc_srv.ThreadingOSCUDPServer(
                ("0.0.0.0", self.osc_port), d)
            threading.Thread(target=self._osc_server.serve_forever, daemon=True).start()
            # OSC OUT (clientes para a consola) e gerido em
            # _rebuild_console_clients() - independente do OSC IN.
            if not self._console_clients:
                self._rebuild_console_clients()
            self.osc_enabled = True
            self._refresh_status()
            # envia logo todos os nomes para a consola actualizar o cache
            self._push_all_channel_names()
        except Exception as e:
            messagebox.showerror("OSC", T('m.osc_start_err', e=e))

    def stop_osc(self):
        if self._osc_server:
            try:
                self._osc_server.shutdown()
            finally:
                # v4: fecha mesmo o socket — sem server_close(), religar o
                # OSC na mesma porta podia falhar (socket ficava bound).
                try:
                    self._osc_server.server_close()
                except Exception:
                    pass
            self._osc_server = None
        # nota: nao limpa _console_clients - OSC OUT continua independente
        self.osc_enabled = False
        self._refresh_status()

    def _rebuild_console_clients(self):
        """Recria os clientes OSC OUT: localhost (bridge USB), IPs de consolas
        APRENDIDOS pela origem dos pacotes (v4) e o IP fixo do modo AP."""
        try:
            from pythonosc import udp_client
            targets = ['127.0.0.1'] + list(self._console_ips) + [CONSOLE_OSC_HOST]
            self._console_clients = []
            seen = set()
            for ip in targets:
                if ip in seen:
                    continue
                seen.add(ip)
                self._console_clients.append(
                    udp_client.SimpleUDPClient(ip, self.osc_out_port))
        except Exception:
            self._console_clients = []
        self._refresh_status()

    # ── envio de mensagens OSC para a consola fisica ──
    def _send_console(self, address, value=None):
        """Envia OSC para a consola (modo USB via bridge OU modo AP direct).
        Respeita o flag osc_out_enabled. Tenta os dois destinos em paralelo;
        o errado falha silenciosamente (UDP sendto)."""
        if not self.osc_out_enabled: return
        if not self._console_clients: return
        for client in self._console_clients:
            try:
                if value is None:
                    client.send_message(address, [])
                else:
                    client.send_message(address, value)
            except Exception:
                pass

    def _push_channel_name(self, ch):
        """Envia o nome do canal ch para a consola."""
        if not (1 <= ch <= NUM_CHANNELS): return
        name = (self.engine.patch.get(ch).get('name') or '')[:6]
        self._send_console('/channel/{}/name'.format(ch), name)

    def _push_channel_alcunha(self, ch):
        """v3 #2 — envia alcunha (int 0..9999) para a consola.
        0 = sem alcunha, a consola mostra o n.º interno do canal."""
        if not (1 <= ch <= NUM_CHANNELS): return
        alc = int(self.engine.patch.get(ch).get('alcunha') or 0)
        self._send_console('/channel/{}/alias'.format(ch), alc)      # EN
        self._send_console('/channel/{}/alcunha'.format(ch), alc)    # alias PT

    def _push_channel_curva(self, ch):
        """v3 #4 — envia a curva do canal (linear/rele/ligado) para a consola.
        Usada no OLED quando o canal e 'ligado' (mostra L grande no OLED dir)."""
        if not (1 <= ch <= NUM_CHANNELS): return
        curva = self.engine.patch.get(ch).get('curva', CURVE_LINEAR)
        self._send_console('/channel/{}/curve'.format(ch), str(curva))   # EN
        self._send_console('/channel/{}/curva'.format(ch), str(curva))   # PT

    def _push_page(self):
        """v6.2 — avisa a consola da PÁGINA activa (mesa/dmx) + universo DMX.
        No modo Highlight a consola segue a página: na DMX mostra 'D001'..'D512'
        e percorre os 512 endereços; na mesa percorre os canais."""
        if self._chan_view == 'dmx':
            self._send_console('/page', ['dmx', int(self._dmx_univ)])
        else:
            self._send_console('/page', ['mesa', 0])

    def _push_channel_level(self, ch):
        """Envia o nivel actual do canal para a consola (programmer ou base)."""
        if not (1 <= ch <= NUM_CHANNELS): return
        lvl = self.engine.programmer[ch]
        if lvl is None:
            lvl = int(self.engine.output[ch])
        self._send_console('/channel/{}/level'.format(ch),
                           max(0, min(255, int(lvl))))

    # ── v4: envio em ritmo controlado (o Pico lê poucos pacotes por ciclo;
    #        uma rajada de 300+ datagramas UDP perdia mensagens) ──
    def _queue_console_msgs(self, msgs):
        """Junta mensagens [(addr, val), …] à fila de saída paced."""
        was_empty = not self._console_outbox
        self._console_outbox.extend(msgs)
        if was_empty and self._console_outbox:
            self.root.after(1, self._drain_console_outbox)

    def _drain_console_outbox(self):
        """Ritmo de envio paced para a consola. ~14 msgs a cada 40 ms (≈350/s).
        IMPORTANTE — NÃO subir muito: em modo USB o bridge escreve no série a
        115200 baud (~11,5 KB/s ≈ 300-350 msgs de ~30 B). Acima disso o buffer
        série enche e o bridge LARGA pacotes UDP — a consola perde nomes/patch.
        O grande ganho de velocidade da v6.2 veio de ENVIAR MENOS mensagens
        (saltar canais vazios em _push_all_channel_names), não de acelerar o
        ritmo. Em WiFi puro daria para ir mais depressa, mas mantém-se um ritmo
        seguro para os dois transportes."""
        chunk, self._console_outbox = (self._console_outbox[:14],
                                       self._console_outbox[14:])
        for addr, val in chunk:
            self._send_console(addr, val)
        if self._console_outbox:
            self.root.after(40, self._drain_console_outbox)

    # NOTA: '/show/size' NÃO se envia isolado. No firmware v5 essa mensagem é o
    # arauto de uma re-sincronização COMPLETA (a consola LIMPA os rótulos e
    # espera recebê-los de novo). Por isso vai SEMPRE como 1.ª mensagem de
    # _push_all_channel_names — nunca sozinha (limparia a consola sem repor).

    def _push_patched_channels(self):
        """v4 — envia a lista de canais COM patch ('1,2,5,10') para a consola
        1 saltar canais vazios no browse do encoder (/channel/patched)."""
        chans = [str(ch) for ch in range(1, NUM_CHANNELS + 1)
                 if self.engine.patch.get(ch).get('addrs')]
        self._send_console('/channel/patched', ','.join(chans))

    def _push_all_channel_names(self):
        """Envia nomes + alcunhas + curvas + lista de patch para a consola
        (no arranque do OSC, quando o renumerador é aplicado e quando uma
        consola nova é aprendida). v4: paced — não afoga o buffer do Pico.
        v6.2: SÓ envia canais com conteúdo (patch/nome/alcunha/curva≠linear).
        Os vazios ficam no defeito da consola — poupava-se enviar centenas de
        mensagens inúteis num show de 512 canais (era a maior causa de lentidão
        na sincronização)."""
        if not self._console_clients: return
        # v5: o tamanho do show vai PRIMEIRO — a consola redimensiona-se antes
        # de receber nomes/alcunhas/curvas/patch dos canais altos.
        msgs = [('/show/size', int(NUM_CHANNELS))]
        for ch in range(1, NUM_CHANNELS + 1):
            e = self.engine.patch.get(ch)
            name  = (e.get('name') or '')[:6]
            alc   = int(e.get('alcunha') or 0)
            curva = str(e.get('curva', CURVE_LINEAR))
            # v6.2: salta canais totalmente vazios (sem patch nem rótulos)
            if not (e.get('addrs') or name or alc or curva != CURVE_LINEAR):
                continue
            msgs.append(('/channel/{}/name'.format(ch),    name))
            msgs.append(('/channel/{}/alias'.format(ch),   alc))     # EN
            msgs.append(('/channel/{}/alcunha'.format(ch), alc))     # PT
            msgs.append(('/channel/{}/curve'.format(ch),   curva))   # EN
            msgs.append(('/channel/{}/curva'.format(ch),   curva))   # PT
        chans = [str(ch) for ch in range(1, NUM_CHANNELS + 1)
                 if self.engine.patch.get(ch).get('addrs')]
        msgs.append(('/channel/patched', ','.join(chans)))
        self._queue_console_msgs(msgs)
        self._push_page()       # v6.2: a consola fica a saber a página activa

    def _push_cue_state(self):
        """Envia o estado da cue actual (num, label, fade_in/out) para a consola
        num UNICO pacote OSC '/cue/state' com 4 args (s s f f) - mais rapido
        que 4 mensagens separadas quando se navega depressa pelas cues."""
        if not self._console_clients: return
        idx = self.engine.current_cue_idx
        if not (0 <= idx < len(self.engine.cues)):
            self._send_console('/cue/state', ['', '', 0.0, 0.0])
            return
        cue = self.engine.cues[idx]
        num_txt = self._cue_num_txt(cue) if hasattr(self, '_cue_num_txt') else str(cue.get('num', ''))
        legacy  = float(cue.get('fade', 0.0) or 0.0)
        fi = float(cue.get('fade_in',  legacy) or 0.0)
        fo = float(cue.get('fade_out', legacy) or 0.0)
        self._send_console('/cue/state',
                           [str(num_txt), str(cue.get('label', '')), fi, fo])

    def _schedule_cue_state_push(self, delay_ms=60):
        """Faz debounce do push: se navegares depressa, so o ULTIMO estado e
        enviado (depois de delay_ms sem novos /cue/go ou /cue/back)."""
        if getattr(self, '_cue_state_push_id', None):
            try: self.root.after_cancel(self._cue_state_push_id)
            except Exception: pass
        self._cue_state_push_id = self.root.after(delay_ms, self._push_cue_state)

    # ── v4: recepção OSC ──────────────────────
    def _osc_packet(self, client_addr, addr, *args):
        """Handler único do servidor OSC — CORRE NA THREAD DO SERVIDOR.
        Aprende o IP da consola e agenda o processamento na thread da UI."""
        try:
            ip = client_addr[0] if client_addr else ''
        except Exception:
            ip = ''
        if ip and not ip.startswith('127.') and ip not in self._console_ips:
            self._ui(lambda: self._add_console_ip(ip))
        self._ui(lambda: self._osc_apply(addr, args))

    def _add_console_ip(self, ip):
        """(thread UI) Regista um IP de consola novo, refaz os clientes OSC
        OUT e empurra o estado completo (a consola pode ter acabado de ligar
        ou de reiniciar — precisa de nomes/alcunhas/curvas/cue)."""
        if ip in self._console_ips:
            return
        self._console_ips.append(ip)
        del self._console_ips[:-3]          # guarda no máximo os 3 últimos
        print('[osc] consola aprendida em', ip)
        self._rebuild_console_clients()
        if self.osc_out_enabled:
            self._push_all_channel_names()
            self._schedule_cue_state_push()

    def _osc_apply(self, addr, args):
        """(thread UI) Aplica uma mensagem OSC recebida.
        Consola 2 — playback: /go /pause /back /soltar
        Consola 2 — gravacao (2-press): /rec/comprar /rec/actualiza
                    /rec/guarda /rec/cancelar
        Consola 1: /channel/... /cue/... /submaster/N /release_all
        Outros:    /blackout /clear /intensity /group/N/level"""
        simple = {
            '/go':            self._go,
            '/back':          self._back,
            '/blackout':      self._blackout,
            # v6.3 — CLEAR e RELEASE espelham EXACTAMENTE os botões da mesa
            # (lógica de 2 toques). O controlador manda /clear (ou /release) a
            # cada pressão; a janela de 1.2 s decide 1.º/2.º toque.
            '/clear':         self._on_clear,
            '/release':       self._on_liberta,
            '/pause':         self._toggle_pause,
            # v6.3 — protocolo em INGLÊS; os nomes PT ficam como ALIAS para as
            # consolas físicas actuais continuarem a funcionar sem mexer no
            # firmware. O help só mostra os nomes ingleses.
            '/loopbreak':     self._soltar,     # EN
            '/soltar':        self._soltar,     # alias PT (firmware)
            '/rec/take':      lambda: self._console2_arm_or_exec('comprar'),
            '/rec/update':    lambda: self._console2_arm_or_exec('actualiza'),
            '/rec/save':      lambda: self._console2_arm_or_exec('guarda'),
            '/rec/cancel':    self._console2_cancel,
            '/rec/comprar':   lambda: self._console2_arm_or_exec('comprar'),
            '/rec/actualiza': lambda: self._console2_arm_or_exec('actualiza'),
            '/rec/guarda':    lambda: self._console2_arm_or_exec('guarda'),
            '/rec/cancelar':  self._console2_cancel,
            # v5: a consola pede o tamanho do show no arranque/handshake.
            # Respondemos com o estado completo (inclui /show/size primeiro).
            '/show/size/request': self._push_all_channel_names,
        }
        fn = simple.get(addr)
        if fn:
            fn()
            return

        # v6.2: a consola (modo Highlight — pressão longa no botão direito)
        # liga/desliga o Highlight na app. CIENTE DA PÁGINA: na vista DMX liga
        # o teste de saída DMX; na mesa liga o Highlight dos canais. Reflecte-se
        # no botão H, esteja ou não algo seleccionado.
        if addr == '/highlight':
            on = bool(int(float(args[0]))) if args else False
            if self._chan_view == 'dmx':
                self._dmx_highlight = on
                self.engine.highlight = False   # exclusivo: só o force DMX
                self._push_dmx_force()
                self._update_hs_btns()
                self._draw_dmx()
            else:
                self.engine.highlight = on
                self._dmx_highlight = False      # exclusivo: limpa force DMX
                self._push_dmx_force()
                self._update_hs_btns()
                self._draw_channels()
            return

        # v6.2: a consola ajusta o NÍVEL do Highlight (encoder direito no modo
        # Highlight) — os destacados (canais OU endereços DMX) passam a ir a
        # este valor (0-255) em vez de 255 fixos.
        if addr == '/highlight/level' and args:
            self.engine.highlight_level = max(0, min(255, int(float(args[0]))))
            if self._chan_view == 'dmx':
                self._draw_dmx()
            else:
                self._draw_channels()
            return

        # v6.2: a consola, no modo Highlight + página DMX, percorre os 512
        # endereços e diz qual destacar (1..512; 0 = nenhum). A app força esse
        # endereço (no universo actual) ao highlight_level no monitor DMX.
        if addr == '/dmx/highlight/addr' and args:
            a = int(float(args[0]))
            self._dmx_selected = {a} if 1 <= a <= 512 else set()
            self._dmx_state = {}
            self._push_dmx_force()
            self._draw_dmx()
            return

        # v6.2: Consola 2 — página FX. Entrar/sair do modo FX (clique do
        # encoder) -> mostra a página FX na app e destaca/limpa o grupo de 4.
        if addr == '/fx/mode' and args:
            on = bool(int(float(args[0])))
            if on:
                self._show_page('fx')
                if self._fx_console_group is None:
                    self._fx_console_group = 0
            else:
                self._fx_console_group = None
                self._show_page('xf')        # volta ao playback (simétrico)
            self._refresh_fx()
            return

        # v6.2: a Consola 2 (encoder na página FX) seleccionou um grupo de 4.
        if addr == '/fx/group' and args:
            g = int(float(args[0]))
            n_groups = (NUM_FX + 3) // 4
            self._fx_console_group = g if 0 <= g < n_groups else None
            self._refresh_fx()
            return

        # v6.2: a Consola 2 faz TOGGLE a um FX (botão na página FX). Só liga/
        # desliga FX já gravados (slot vazio ignora — igual ao clique na app).
        if addr.startswith('/fx/') and addr.endswith('/toggle'):
            try:    n = int(addr.split('/')[2])
            except (ValueError, IndexError): n = 0
            if 1 <= n <= NUM_FX and self.engine.fx[n - 1]:
                self.engine.fx_toggle(n - 1)
                self._refresh_fx()
            return

        # v6.3 — passos EXPLÍCITOS de CLEAR/RELEASE (fiáveis p/ TouchOSC, sem
        # depender do duplo-toque temporizado). Um botão por passo. Disparam
        # no pressionar (arg ausente ou > 0; ignora o soltar arg == 0).
        _steps = {'/clear/1': self._clear_step1, '/clear/2': self._clear_step2,
                  '/release/1': self._release_step1,
                  '/release/2': self._release_step2}
        if addr in _steps:
            if not args or float(args[0]) != 0:
                _steps[addr]()
            return

        parts = addr.strip('/').split('/')
        try:
            if parts[0] == 'channel' and len(parts) == 3 and parts[2] == 'level':
                ch = int(parts[1])
                raw = args[0]
                # typetag ',i' (int) -> 0-255 directo (vem da consola)
                # typetag ',f' (float) -> 0.0-1.0 normalizado OU 0-255
                if isinstance(raw, int):
                    lvl = max(0, min(255, raw))
                else:
                    f = float(raw)
                    lvl = int(f * 255) if f <= 1.0 else int(f)
                self._prog_checkpoint()       # undo do gesto (encoder da consola)
                self.engine.set_channel(ch, lvl)
                self._mark_dirty()

            elif parts[0] == 'intensity' and len(args) >= 2:
                ch = int(args[0])
                f = float(args[1])
                lvl = int(f * 255) if f <= 1.0 else int(f)
                self.engine.set_channel(ch, lvl)
                self._mark_dirty()

            # v6.3 — passo RELATIVO nos canais seleccionados (botões +5/-5).
            # /level/adjust {delta}  — delta pode ser +/- (ex.: 5, -5, 1, -1)
            elif (parts[0] == 'level' and len(parts) == 2
                  and parts[1] == 'adjust' and args):
                delta = int(float(args[0]))
                if delta != 0:
                    self._adjust_level(delta)
                    self._mark_dirty()

            # v6.3 — valor ABSOLUTO nos canais seleccionados (botões 0/50/100%).
            # /level/set {v}  — f<=1.0 normalizado (0.5 = 50 %); >1.0 = 0-255
            elif (parts[0] == 'level' and len(parts) == 2
                  and parts[1] == 'set' and args):
                f = float(args[0])
                lvl = int(round(f * 255)) if f <= 1.0 else int(f)
                self._set_level(max(0, min(255, lvl)))
                self._mark_dirty()

            # v6.3 — variantes com o valor no ENDEREÇO (botões TouchOSC que só
            # mandam a morada, sem argumento). Disparam no pressionar.
            #   /level/set/{pct}   pct 0-100 (ex.: /level/set/50 = 50 %)
            elif (parts[0] == 'level' and len(parts) == 3
                  and parts[1] == 'set' and (not args or float(args[0]) != 0)):
                pct = float(parts[2])
                self._set_level(max(0, min(255, int(round(pct / 100.0 * 255)))))
                self._mark_dirty()

            #   /level/up[/{n}]  e  /level/down[/{n}]  (n opcional, defeito 5)
            elif (parts[0] == 'level' and len(parts) >= 2
                  and parts[1] in ('up', 'down')
                  and (not args or float(args[0]) != 0)):
                step = int(float(parts[2])) if len(parts) == 3 else 5
                self._adjust_level(step if parts[1] == 'up' else -step)
                self._mark_dirty()

            elif parts[0] == 'submaster' and len(parts) == 2 and len(args) >= 1:
                si = int(parts[1]) - 1
                f = float(args[0])
                v = int(f * 100) if f <= 1.0 else int(f)
                self._osc_set_submaster(si, v)

            elif parts[0] == 'group' and len(parts) == 3 and parts[2] == 'level':
                gi = int(parts[1]) - 1
                f = float(args[0])
                lvl = int(f * 255) if f <= 1.0 else int(f)
                self._acao_group(gi, lvl)
                self._mark_dirty()

            # v6.3 — chamar Grupo N (1-20) como carregar no botão (dispara no
            # pressionar: arg ausente ou > 0; ignora o soltar arg == 0)
            elif parts[0] == 'group' and len(parts) == 2:
                if not args or float(args[0]) != 0:
                    self._osc_call_group(int(parts[1]))

            # v6.3 — chamar Look/Retrato N (1-20)
            elif parts[0] in ('retrato', 'look') and len(parts) == 2:
                if not args or float(args[0]) != 0:
                    self._osc_recall_retrato(int(parts[1]))

            # ── Console: selecção e libertação ──
            elif (parts[0] == 'channel' and len(parts) == 2 and
                  parts[1] == 'select' and len(args) >= 1):
                ch = int(float(args[0]))
                if ch == 0:
                    self._clear_selection()       # v6.2: consola deseleccionou
                elif 1 <= ch <= NUM_CHANNELS:
                    self._console_select(ch)

            elif parts[0] == 'release_all':
                # /release_all F  — a consola manda o seu FADE_SECONDS, mas a
                # app IGNORA-O e usa o tempo configurado no menu (uma só
                # regulação governa o botão e a consola). Decisão do autor
                # 2026-06-13 — sem mexer no firmware do Pico.
                self._console_release_all(self._release_time)

            # ── Cuelist (consola em modo CUELIST) ──
            elif parts[0] == 'cue' and len(parts) == 2:
                cmd = parts[1]
                if cmd == 'go':
                    self._console_cue_go()
                elif cmd == 'back':
                    self._console_cue_back()
                elif cmd == 'fade_in' and args:
                    self._console_cue_fade('fade_in', float(args[0]))
                elif cmd == 'fade_out' and args:
                    self._console_cue_fade('fade_out', float(args[0]))

            # consola pede o estado actual da cue (ao entrar em CUELIST mode)
            elif parts[0] == 'cue' and len(parts) == 3 and \
                 parts[1] == 'state' and parts[2] == 'request':
                self._push_cue_state()
        except (IndexError, ValueError):
            pass

    def _acao_group(self, gi, lvl):
        """Aplica um nível a todos os canais do grupo gi (0-based)."""
        if 0 <= gi < len(self.engine.groups):
            g = self.engine.groups[gi]
            if g:
                for ch in g.get('channels', []):
                    self.engine.set_channel(ch, lvl)

    def _osc_call_group(self, n):
        """v6.3 — chama o Grupo n (1-20) via OSC: junta os canais do grupo à
        selecção actual (igual a carregar no botão, sem armas)."""
        idx = int(n) - 1
        if not (0 <= idx < len(self.engine.groups)):
            return
        g = self.engine.groups[idx]
        if not g or not g.get('channels'):
            return
        self._selected |= {c for c in g['channels']
                           if 1 <= c <= NUM_CHANNELS}
        self._update_sel_label()
        self._mark_dirty()

    def _osc_recall_retrato(self, n):
        """v6.3 — chama o Look/Retrato n (1-20) via OSC: aplica os níveis
        gravados e junta os canais à selecção (igual ao botão, sem armas)."""
        idx = int(n) - 1
        if not (0 <= idx < len(self.engine.retratos)):
            return
        r = self.engine.retratos[idx]
        levels = r.get('levels') if r else None
        if not levels:
            return
        self.engine.recall_retrato(idx)
        self._selected |= {int(c) for c in levels
                           if 1 <= int(c) <= NUM_CHANNELS}
        self._update_sel_label()
        self._mark_dirty()

    # ── Handlers da consola física (chamados pelo OSC) ──
    def _osc_set_submaster(self, idx, val):
        """Mexe o submaster idx (0-100) via OSC: actualiza engine + slider UI."""
        if not (0 <= idx < len(self._sub_scales)): return
        self.engine.set_submaster_fader(idx, val)
        self._sub_guard = True
        self._sub_scales[idx].set(val)
        self._sub_guard = False
        self._draw_channels()

    def _open_patch_dialog(self):
        """Abre o renumerador. Apos o Aplicar/Fechar: alinha os universos de
        saida (modo automatico — o patch pode ter mudado os universos) e
        envia nomes/alcunhas/curvas/patched para a consola fisica."""
        dlg = PatchDialog(self.root, self.engine)
        self.root.wait_window(dlg)
        self.engine.sync_sacn_outputs()
        self._refresh_status()
        self._push_all_channel_names()

    def _set_release_time(self):
        """Configura o tempo (s) do fade-out do botão LIBERTA. 0 = imediato.
        Pedido do autor 2026-06-13 (o LIBERTA fixo a 1 s ainda era lento)."""
        dlg = ValueDialog(self.root, T('m.rel_title'), T('m.rel_prompt'),
                          f"{self._release_time:g}")
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        v = self._to_float(dlg.result, minimum=0.0)
        if v is None:
            messagebox.showerror(T('m.rel_title'), T('m.err_value'))
            return
        self._release_time = max(0.0, min(60.0, v))

    def _change_show_size(self):
        """Altera o NUM_CHANNELS em runtime, respeitando as regras:
          - Limite: 1..MAX_CHANNELS (512)
          - Se ja ha cues / retratos / grupos / submasters gravados, so
            permite AUMENTAR (encolher apagava memorias).
          - Se nao ha gravacoes ainda, livre nos dois sentidos."""
        bloqueado = self.engine.has_recordings()
        msg = T('showsize.msg_main', cur=NUM_CHANNELS, max=MAX_CHANNELS)
        if NUM_CHANNELS <= 200:
            msg += T('showsize.heavy')
        if bloqueado:
            msg += T('showsize.locked')
        dlg = ValueDialog(self.root, T('showsize.title'), msg, str(NUM_CHANNELS))
        self.root.wait_window(dlg)
        if dlg.result is None: return
        try:
            new_n = int(dlg.result.strip())
        except ValueError:
            messagebox.showerror(T('showsize.invalid_title'),
                                 T('showsize.invalid_int', max=MAX_CHANNELS))
            return
        if not (1 <= new_n <= MAX_CHANNELS):
            messagebox.showerror(T('showsize.invalid_title'),
                                 T('showsize.invalid_range', max=MAX_CHANNELS))
            return
        if new_n == NUM_CHANNELS:
            return
        if bloqueado and new_n < NUM_CHANNELS:
            messagebox.showerror(T('showsize.locked_title'),
                                 T('showsize.locked_msg'))
            return
        self._capture_undo()
        self.engine.resize(new_n)
        self._selected = {c for c in self._selected if c <= new_n}
        # v5: avisa a consola do novo tamanho (redimensiona) + reenvia patch
        self._push_all_channel_names()
        self._refresh()

    def _console_select(self, ch):
        """SELECT: halo amarelo no canal (substitui qualquer selecção anterior).
        Envia nome, alcunha, curva e nivel actual do canal para a consola.
        Origem: a CONSOLA (encoder). Marca _console_sel_sent p/ o
        _sync_console_selection NÃO reenviar /channel/selected de volta (eco)."""
        self._selected.clear()
        self._selected.add(ch)
        self._console_sel_sent = ch     # v6.2: já está seleccionado lá; não ecoa
        self._draw_channels()
        self._push_channel_name(ch)
        self._push_channel_alcunha(ch)
        self._push_channel_curva(ch)
        self._push_channel_level(ch)

    def _console_cue_go(self):
        """>>> da consola — salta para a cue seguinte SEM fade (modo edição)."""
        nxt = self.engine.next_index(self.engine.current_cue_idx)
        if nxt is not None:
            self.engine.set_position(nxt)
            self._refresh_cue_panel()
            self._draw_channels()
            self._schedule_cue_state_push()    # debounced: 60 ms

    def _console_cue_back(self):
        """<<< da consola — salta para a cue anterior SEM fade (modo edição)."""
        prv = self.engine.prev_index(self.engine.current_cue_idx)
        if prv is not None:
            self.engine.set_position(prv)
            self._refresh_cue_panel()
            self._draw_channels()
            self._schedule_cue_state_push()

    def _console_cue_fade(self, key, delta):
        """Soma delta (em segundos) ao fade_in/fade_out da cue actual.
        key = 'fade_in' ou 'fade_out'. delta vem da consola, +/-1 por click."""
        idx = self.engine.current_cue_idx
        if not (0 <= idx < len(self.engine.cues)):
            return
        cue = self.engine.cues[idx]
        cur = float(cue.get(key, cue.get('fade', 0.0)) or 0.0)
        new = max(0.0, cur + float(delta))
        cue[key] = new
        self._refresh_cue_panel()
        # ecoa o novo valor para o OLED da consola
        self._send_console('/cue/state/' + key, float(new))

    def _console_release_all(self, duration_s):
        """LIBERTA TUDO: fade out de todos os canais do programmer.
        v6.4: os canais conduzidos pelo DMX-In ficam de fora (a rampa
        lutava com o tick da escuta e os valores voltavam no fim)."""
        exc = self._din_exc() or set()
        start_levels = {}
        for ch in range(1, NUM_CHANNELS + 1):
            if self.engine.programmer[ch] is not None and ch not in exc:
                start_levels[ch] = self.engine.programmer[ch]
        self._selected.clear()
        if not start_levels:
            self._draw_channels()
            return
        steps = max(1, int(duration_s * 25))   # ~25 FPS
        interval_ms = max(1, int(duration_s * 1000 / steps))

        def step(i):
            if i > steps:
                for ch in start_levels:
                    self.engine.clear_channel(ch)
                self._draw_channels()
                return
            k = 1.0 - (i / steps)
            for ch, start_lvl in start_levels.items():
                self.engine.set_channel(ch, int(start_lvl * k))
            self._draw_channels()
            self.root.after(interval_ms, lambda: step(i + 1))

        step(1)

    # ── show file ─────────────────────────────
    def _new_show(self):
        if not messagebox.askyesno(T('m.new_title'), T('m.new_confirm')):
            return
        # pergunta o numero de canais para o novo show (1..512, default 100)
        dlg = ValueDialog(self.root, T('m.new_title'),
                          T('m.new_chan_prompt', max=MAX_CHANNELS),
                          str(NUM_CHANNELS))
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            new_n = max(1, min(MAX_CHANNELS, int(dlg.result.strip())))
        except ValueError:
            new_n = 100
        # reset total + resize se preciso
        self.engine.reset_show()
        if new_n != NUM_CHANNELS:
            self.engine.resize(new_n)
        self._undo_snap = self._redo_snap = None   # show novo: limpa undo
        self._selected = set()
        for v in self._preset_vars.values():
            v.set("0")
        self._show_file = None
        self._fx_edit = None              # v5
        self._fx_armed = None
        self._refresh_fx_action_btns()
        self._fx_build_editor()
        self._status_var.set(T('m.status_new', n=new_n))
        # v5: sincroniza a consola com o tamanho do novo show
        self._push_all_channel_names()
        self._refresh()
        self._show_snapshot = self.engine.snapshot()

    def _save_show(self):
        """Devolve True se o show ficou gravado."""
        if self._show_file:
            self.engine.save(self._show_file)
            self._show_snapshot = self.engine.snapshot()
            return True
        return self._save_show_as()

    def _save_show_as(self):
        p = filedialog.asksaveasfilename(
            defaultextension='.ldsk',
            filetypes=[("Show MESADELUX", "*.ldsk"), ("JSON", "*.json")])
        if p:
            self._show_file = p
            self.engine.save(p)
            self._show_snapshot = self.engine.snapshot()
            self._status_var.set(f"MESADELUX  |  {p}")
            return True
        return False

    def _import_ascii_show(self):
        """v6.3.2 — importa um USITT ASCII (.asc/.alq) como show NOVO
        (mesma confirmação do «Novo Show»; o aberto perde-se se não estiver
        gravado). No fim mostra o relatório do que entrou e do que ficou."""
        if not messagebox.askyesno(T('ascii.import_title'),
                                   T('ascii.import_confirm')):
            return
        p = filedialog.askopenfilename(
            filetypes=[("USITT ASCII", "*.asc *.alq"),
                       (T('ascii.ft_all'), "*.*")])
        if not p:
            return
        # estilo do FOLLOWON: auto-detecta (marcador nosso / Eos); só
        # pergunta quando o ficheiro não dá pistas (ex.: grandMA)
        estilo = ascii_sniff_follow(p)
        if estilo is None:
            estilo = ('eos' if messagebox.askyesno(T('ascii.folw_title'),
                                                   T('ascii.folw_import_q'))
                      else 'directo')
        try:
            data, rel = import_ascii(p, follow_estilo=estilo)
            with self.engine._lock:      # como Engine.load(path)
                self.engine._load_data(data)
        except Exception as e:
            messagebox.showerror(T('ascii.import_title'),
                                 T('ascii.import_err', msg=str(e)))
            return
        # show novo: mesmo pós-processo do _new_show/_open_show
        self._undo_snap = self._redo_snap = None
        self._selected = set()
        for v in self._preset_vars.values():
            v.set("0")
        self._show_file = None           # NÃO é um .ldsk — «Guardar» pergunta
        self._fx_edit = None
        self._fx_armed = None
        self._refresh_fx_action_btns()
        self._fx_build_editor()
        self._push_all_channel_names()
        self._status_var.set(f"MESADELUX  |  {p}")
        self._refresh()
        self._show_snapshot = self.engine.snapshot()
        det = '\n' + T('ascii.folw_used',
                       estilo=T('ascii.folw_' + rel['follow_estilo']))
        if rel['notas']:
            det += '\n\n' + T('ascii.notas_hdr') + '\n' \
                   + '\n'.join(rel['notas'])
        if rel['exemplos']:
            det += '\n\n' + T('ascii.import_ign_hdr') + '\n' \
                   + '\n'.join(rel['exemplos'])
        messagebox.showinfo(T('ascii.import_title'),
                            T('ascii.import_done', path=p,
                              cues=rel['cues'], chans=rel['channels'],
                              ign=rel['ignoradas']) + det)

    def _export_ascii_show(self):
        """v6.3.2 — exporta o show para USITT ASCII (.asc). Portabilidade
        para outras mesas; o .ldsk continua a ser o formato de gravação."""
        if not messagebox.askokcancel(T('ascii.export_title'),
                                      T('ascii.export_warn')):
            return
        # estilo do FOLLOWON no ficheiro: Eos/USITT (compensado) ou
        # grandMA/directo — escolha do utilizador a cada exportação
        estilo = ('eos' if messagebox.askyesno(T('ascii.folw_title'),
                                               T('ascii.folw_export_q'))
                  else 'directo')
        p = filedialog.asksaveasfilename(
            defaultextension='.asc',
            filetypes=[("USITT ASCII", "*.asc")])
        if not p:
            return
        try:
            info = export_ascii(self.engine._show_data(), p,
                                follow_estilo=estilo)
        except Exception as e:
            messagebox.showerror(T('ascii.export_title'),
                                 T('ascii.export_err', msg=str(e)))
            return
        det = '\n' + T('ascii.folw_used', estilo=T('ascii.folw_' + estilo))
        if info['notas']:
            det += '\n\n' + T('ascii.notas_hdr') + '\n' \
                   + '\n'.join(info['notas'])
        messagebox.showinfo(T('ascii.export_title'),
                            T('ascii.export_done', path=p,
                              cues=info['cues'], chans=info['channels'])
                            + det)

    def _open_show(self):
        p = filedialog.askopenfilename(
            filetypes=[("Show MESADELUX", "*.ldsk"), ("JSON", "*.json")])
        if p:
            try:
                self.engine.load(p)
                self._undo_snap = self._redo_snap = None  # show carregado: limpa undo
                # Se o sACN já estava activo, o load mudou o universo no engine
                # mas os sockets continuam ligados ao universo antigo. Re-liga
                # o sACN com o universo agora carregado do show.
                if self.engine.sacn_enabled and HAS_SACN:
                    bind = self.engine.sacn_bind_ip or self._pick_bind_ip()
                    self.engine.stop_sacn()
                    self.engine.start_sacn(
                        universes=self.engine.sacn_universes,
                        multicast=self.engine.sacn_multicast,
                        unicast_ip=self.engine.sacn_unicast_ip,
                        bind_ip=bind)
                # v4: o show pode trazer Art-Net activo na config de saída
                if self.engine.artnet_enabled:
                    self.engine.start_artnet(self.engine.artnet_broadcast,
                                             self.engine.artnet_dest_ip,
                                             self.engine.artnet_bind_ip
                                             or self._pick_bind_ip())
                else:
                    self.engine.stop_artnet()
                # v4: sincroniza a consola com o patch do show carregado
                self._push_all_channel_names()
                for i in (1, 2):
                    self._preset_vars[i].set(self.engine.presets[i - 1])
                self._show_file = p
                self._fx_edit = None      # v5: edição/armas não sobrevivem
                self._fx_armed = None     # à troca de show
                self._refresh_fx_action_btns()
                self._fx_build_editor()
                self._status_var.set(f"MESADELUX  |  {p}")
                self._refresh()
                self._show_snapshot = self.engine.snapshot()
            except Exception as e:
                messagebox.showerror(T('common.error'), T('m.open_err', e=e))

    # ── DMX-IN (v6.4, Etapa 1: só escuta e visualização) ──────
    def _dmx_in_liga(self, universos, bind):
        """Liga a escuta sACN (DMX-IN). NÃO mexe no motor de saída nem
        no show — só arranca a thread de escuta e o ciclo de UI. Avisa
        se algum universo escutado coincidir com a saída própria activa
        (confusão visual: verias o teu próprio output)."""
        self._dmx_in_desliga()
        esc = EscutaDMXIn(universos, bind=bind)
        esc.iniciar()                       # pode levantar (sem sacn)
        self._dmx_in = esc
        if self.engine.sacn_enabled or self.engine.artnet_enabled:
            comuns = sorted(set(esc.universos)
                            & set(self.engine.out_universes()))
            if comuns:
                messagebox.showwarning(
                    T('din.title'),
                    T('din.aviso_out',
                      u=', '.join('U%d' % u for u in comuns)))
        self._dmx_in_after = self.root.after(100, self._dmx_in_tick)

    def _dmx_in_desliga(self):
        """Desliga a escuta e limpa os crachás da grelha."""
        if self._dmx_in_after is not None:
            try:
                self.root.after_cancel(self._dmx_in_after)
            except Exception:
                pass
            self._dmx_in_after = None
        if self._dmx_in is not None:
            self._dmx_in.parar()
            self._dmx_in = None
        # freeze: os canais conduzidos ficam como programador NORMAL (azul),
        # deixam de ser DMX-In → a libertação volta a funcionar e o look
        # capturado não se perde (grava-se ou liberta-se à vontade).
        self._din_driven = set()
        self._draw_channels()

    def _dmx_in_tick(self):
        """Ciclo de UI (~10x/s, root.after — nunca da thread de escuta):
        alimenta o PROGRAMADOR (azul-ciano) com o que chega por sACN,
        traduzido pelo PATCH (universo+endereço → canal; 16 bits usa o
        coarse, bruto 0-255). Só os canais com valor > 0 entram; um canal
        que caia a 0 é libertado. A partir daqui grava-se com Comprar/
        Actualizar como qualquer look. NÃO escreve no .ldsk."""
        if self._dmx_in is None:
            return
        # v6.4 — re-inscreve no multicast de ~3 em 3 s (30 ticks): o
        # Windows larga a inscrição IGMP e a recepção «recebe e pára»
        self._din_rejoin_c += 1
        if self._din_rejoin_c >= 30:
            self._din_rejoin_c = 0
            self._dmx_in.rejuntar_multicast()
        snap = self._dmx_in.obter_snapshot()
        novos = {}
        for ch in range(1, NUM_CHANNELS + 1):
            e = self.engine.patch.get(ch)
            addrs = e.get('addrs') or []
            if not addrs:
                continue
            dados = snap.get(int(e.get('universe', 1)))
            if not dados:
                continue
            a = int(addrs[0])
            if 1 <= a <= 512:
                v = int(dados[a - 1])
                if v > 0:
                    novos[ch] = v
        mudou = False
        # entram / mudam (reaplica também depois de um Comprar que limpou o
        # programador — o DMX-In continua a mandar)
        for ch, v in novos.items():
            if self.engine.programmer[ch] != v:
                self.engine.set_channel(ch, v)
                mudou = True
        # os que deixaram de receber (>0 → 0/silêncio) libertam-se
        for ch in self._din_driven - set(novos):
            if self.engine.programmer[ch] is not None:
                self.engine.clear_channel(ch)
            mudou = True
        self._din_driven = set(novos)
        if mudou:
            self._draw_channels()
        self._dmx_in_after = self.root.after(100, self._dmx_in_tick)

    def _quit(self):
        # se há alterações por gravar, pergunta antes de sair
        if self.engine.snapshot() != self._show_snapshot:
            ans = messagebox.askyesnocancel(
                T('m.quit_title'), T('m.quit_unsaved'))
            if ans is None:
                return                       # Cancelar — não fecha
            if ans:                          # Sim — gravar
                if not self._save_show():
                    return                   # gravação cancelada → não fecha
            # Não → fecha sem gravar
        self.stop_osc()
        self._close_midi_in()   # v6.3 — fecha MIDI antes de destruir a janela
        self._close_midi_out()
        if self._dmx_in is not None:    # v6.4 — pára a escuta DMX-IN
            self._dmx_in.parar()
            self._dmx_in = None
        self.engine.shutdown()
        self.root.destroy()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
def main():
    # v4: no Windows declara DPI awareness — sem isto o Tkinter fica
    # desfocado em ecrãs com scaling (125 %/150 %), comum no Windows 11.
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    root = tk.Tk()
    root.title("MESADELUX v6.3")

    missing = []
    if not HAS_SACN:
        missing.append("sacn")
    if not HAS_OSC:
        missing.append("python-osc")
    if missing:
        import tkinter.messagebox as mb
        mb.showwarning(
            "Pacotes em falta",
            f"Instala os pacotes para activar sACN/OSC:\n\n"
            f"  pip install {' '.join(missing)}\n\n"
            f"A app funciona em modo offline.")

    app = MesaDeLuxApp(root)
    # v5: rede de segurança — se o mainloop morrer com uma excepção, pára
    # sempre o sACN/OSC. Sem isto, a thread (non-daemon) do emissor sACN
    # mantinha um processo fantasma vivo a emitir para a rede.
    try:
        root.mainloop()
    finally:
        try:
            app.stop_osc()
        except Exception:
            pass
        try:
            app._close_midi_in()    # v6.3 — evita porta bloqueada no Windows
        except Exception:
            pass
        try:
            app._close_midi_out()
        except Exception:
            pass
        app.engine.shutdown()


if __name__ == '__main__':
    main()
