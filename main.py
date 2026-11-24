from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.camera import Camera  # ALTERAÇÃO: câmera nativa da Power PPlay 2.1
from PPlay.sprite import Sprite  # ALTERAÇÃO: animações do Noivo na cena final

from noiva_1 import Noiva
from penetra import Penetra
from amigo import Amigo  # ALTERAÇÃO: novo oponente da Fase 2; arte de Penetra provisória.
from convidada import Convidada
from sogra_boss import SograBoss  # ALTERAÇÃO: boss da última tela da Fase 1
from aplicador import Aplicador    # ALTERAÇÃO: arma coletável e tiros de chantilly
from dama_boss import DamaBoss, BancoBistro, BANCO_SUPERIOR_DIREITO, BANCO_INFERIOR_ESQUERDO, MOSTRAR_CONTAGEM_DAMA, TEMPO_DESPERTAR  # ALTERAÇÃO: arena e despertar da Boss da Fase 2
# ALTERAÇÃO: menus/ranking em módulo independente, abertura preservada.
import pygame
from PIL import Image  # ALTERAÇÃO: leitura dos quadros e tempos reais dos GIFs finais
from menus_wedding import MenusWedding
from cena_1 import Cena1

# ============================================================
# ALTERAÇÃO: CHAVES TEMPORÁRIAS PARA TESTAR A FASE 2
# Volte as três para False ao concluir os testes.
# ============================================================
TESTE_INICIAR_FASE_2 = False
TESTE_INICIAR_NA_ARENA_DAMA = False  # ALTERAÇÃO: False inicia pouco antes da última tela.
TESTE_PULAR_ABERTURA_E_MENU = False
TESTE_NOIVA_X_LOCAL_F2 = 700  # Usado somente se iniciar DENTRO da arena.
TESTE_INICIAR_NO_COMECO_FASE_2 = True  # ALTERAÇÃO: teste começa no X=100 da Fase 2.
TESTE_DISTANCIA_ANTES_DA_ARENA = 420  # ALTERAÇÃO: usado somente no teste próximo da arena.

# ALTERAÇÃO: ampliação da faixa vertical APENAS na arena final da Fase 2.
ALTURA_EXTRA_Y_ARENA_DAMA = 150  # ALTERAÇÃO: reduz 200 para 150px somente na arena final.

# ============================================================
# ALTERAÇÃO: EPÍLOGO DA FASE 2 — NOIVO E PEDIDO
# ============================================================
ESPERA_APOS_DERROTA_DAMA = 5.0       # segundos antes de a Noiva se movimentar
VELOCIDADE_NOIVA_CENA_FINAL = 230.0 # px/s até o centro da pista
VELOCIDADE_NOIVO_CENA_FINAL = 250.0 # px/s entrando pela direita
DISTANCIA_PEDIDO_NOIVO = 125.0      # diferença X entre centro da Noiva e Noivo
DURACAO_NOIVO_ANDANDO = 0.85        # duração de um ciclo de 4 quadros, em s
DURACAO_NOIVO_PEDIDO = 2.1         # 16 quadros uma única vez
TEMPO_POSE_PEDIDO = 5.0            # tempo de exibição depois da animação
MARGEM_LATERAL_NOIVA_ARENA = 2     # só para a Noiva, na arena final

# ============================================================
# ALTERAÇÃO: TELA DE DESTINO DA LUA DE MEL — PONTUAÇÃO
# ============================================================
DURACAO_ENCHIMENTO_DESTINO = 4.0   # a barra cresce por 4 segundos
TEMPO_RESULTADO_DESTINO = 4.0      # pontuação final permanece por mais 4 segundos
PONTOS_TERCO_DESTINO = 500         # 0–500 / 500–1000 / 1000–1500+
PONTUACAO_TOPO_DESTINO = 3 * PONTOS_TERCO_DESTINO
# ALTERAÇÃO: após a barra, mostrar o destino correspondente por 10 segundos.
TEMPO_GIF_DESTINO = 10.0
# Até 500: Petrópolis; 501 a 1000: Paris; acima de 1000: Maldivas.
ARQUIVOS_GIFS_DESTINO = (
    "cenas/1-petropolis.gif",
    "cenas/2-paris.gif",
    "cenas/3-maldivas.gif",
)



# ============================================================
# JANELA
# ============================================================

janela = Window(1600, 900, "Wedding Panic")
teclado = janela.get_keyboard()
# ALTERAÇÃO: cena de abertura -> menu principal -> jogo; ESC abre pausa.
menus = MenusWedding(janela)
abertura = Cena1()
estado_tela = 'jogo' if TESTE_INICIAR_FASE_2 and TESTE_PULAR_ABERTURA_E_MENU else 'abertura'
# ALTERAÇÃO: evita que o ESC usado para retomar abra novamente a pausa.
bloquear_esc_ate_soltar = False
# ALTERAÇÃO: guardar o último frame do jogo para exibir sob o menu de pausa.
ultima_tela_jogo = None
# ALTERAÇÃO: exibe a Noiva caída piscando antes do menu de pontuação.
TEMPO_EXIBICAO_MORTE_NOIVA = 1.2
tempo_exibicao_morte_noiva = 0.0

# ALTERAÇÃO: uma única câmera global para todo o jogo.
camera = Camera(janela.width, janela.height)


# ============================================================
# FUNDOS - FASE 1
# ============================================================

# PARTE 1
parallax_1 = GameImage(
    "assets/img-fundos/01-Fase1-Parte1-parallax.png"
)

cenario_1 = GameImage(
    "assets/img-fundos/01-Fase1-Parte1-cena.png"
)

overlay_1 = GameImage(
    "assets/img-fundos/01-Fase1-Parte1-overlay.png"
)


# PARTE 2
parallax_2 = GameImage(
    "assets/img-fundos/01-Fase1-Parte2-parallax.png"
)

cenario_2 = GameImage(
    "assets/img-fundos/01-Fase1-Parte2-cena.png"
)

overlay_2 = GameImage(
    "assets/img-fundos/01-Fase1-Parte2-overlay.png"
)


# PARTE 3
parallax_3 = GameImage(
    "assets/img-fundos/01-Fase1-Parte3-parallax.png"
)

cenario_3 = GameImage(
    "assets/img-fundos/01-Fase1-Parte3-cena.png"
)

overlay_3 = GameImage(
    "assets/img-fundos/01-Fase1-Parte3-overlay.png"
)


# PARTE 4
parallax_4 = GameImage(
    "assets/img-fundos/01-Fase1-Parte4-parallax.png"
)

cenario_4 = GameImage(
    "assets/img-fundos/01-Fase1-Parte4-cena.png"
)

overlay_4 = GameImage(
    "assets/img-fundos/01-Fase1-Parte4-overlay.png"
)


# ============================================================
# FUNDOS - FASE 2
# ============================================================

# REPETIÇÃO 1
parallax_f2_1 = GameImage(
    "assets/img-fundos/02-Fase2-parallax.png"
)

cenario_f2_1 = GameImage(
    "assets/img-fundos/02-Fase2-cena.png"
)

overlay_f2_1 = GameImage(
    "assets/img-fundos/02-Fase2-overlay.png"
)

# REPETIÇÃO 2
parallax_f2_2 = GameImage(
    "assets/img-fundos/02-Fase2-parallax.png"
)

cenario_f2_2 = GameImage(
    "assets/img-fundos/02-Fase2-cena.png"
)

overlay_f2_2 = GameImage(
    "assets/img-fundos/02-Fase2-overlay.png"
)

# REPETIÇÃO 3
parallax_f2_3 = GameImage(
    "assets/img-fundos/02-Fase2-parallax.png"
)

cenario_f2_3 = GameImage(
    "assets/img-fundos/02-Fase2-cena.png"
)

overlay_f2_3 = GameImage(
    "assets/img-fundos/02-Fase2-overlay.png"
)

# PARTE FINAL
parallax_f2_final = GameImage(
    "assets/img-fundos/02-Fase2-parallax.png"
)

cenario_f2_final = GameImage(
    "assets/img-fundos/02-Fase2-ParteFinal-cena.png"
)

overlay_f2_final = GameImage(
    "assets/img-fundos/02-Fase2-overlay.png"
)


# ============================================================
# TAMANHO DO MUNDO - FASE 1
# ============================================================

LARGURA_PARTE_1 = cenario_1.width
LARGURA_PARTE_2 = cenario_2.width
LARGURA_PARTE_3 = cenario_3.width
LARGURA_PARTE_4 = cenario_4.width

INICIO_PARTE_1 = 0
INICIO_PARTE_2 = LARGURA_PARTE_1
INICIO_PARTE_3 = LARGURA_PARTE_1 + LARGURA_PARTE_2
INICIO_PARTE_4 = (
    LARGURA_PARTE_1
    + LARGURA_PARTE_2
    + LARGURA_PARTE_3
)

LARGURA_CENARIO = (
    LARGURA_PARTE_1
    + LARGURA_PARTE_2
    + LARGURA_PARTE_3
    + LARGURA_PARTE_4
)

ALTURA_CENARIO = cenario_1.height


# ============================================================
# TAMANHO DO MUNDO - FASE 2
# ============================================================

LARGURA_F2 = cenario_f2_1.width
LARGURA_F2_FINAL = cenario_f2_final.width

INICIO_F2_1 = 0
INICIO_F2_2 = LARGURA_F2
INICIO_F2_3 = LARGURA_F2 * 2
INICIO_F2_FINAL = LARGURA_F2 * 3

LARGURA_CENARIO_F2 = (
    LARGURA_F2 * 3
    + LARGURA_F2_FINAL
)

ALTURA_CENARIO_F2 = cenario_f2_1.height

# ALTERAÇÃO: Amigo nasce a partir da SEGUNDA tela, em coordenadas do mundo.
# Ele permanece imóvel até estar completamente visível pela câmera.
AMIGOS_F2_POSICOES = [(620, 500), (840, 560)]  # ALTERAÇÃO: dupla original na segunda tela
AMIGOS_F2_POSICOES_FINAL = [(1150, 430), (1260, 530)]  # ALTERAÇÃO: Y mais baixo; X real definido no limite da tela.
# ALTERAÇÃO: duas Convidadas após a tela dos Amigos (terceira tela da Fase 2).
CONVIDADAS_F2_POSICOES = [(650, 480), (1030, 550)]  # X local da terceira tela, Y mundo
# ALTERAÇÃO: mais duas Convidadas ao fundo da arena da Dama (última tela).
CONVIDADAS_F2_POSICOES_FINAL = [(1020, 470), (1120, 560)]  # ALTERAÇÃO: Y mais baixo e defasado; X real no limite da tela.
# ALTERAÇÃO: mantém os sprites idle até a Noiva chegar perto; depois libera IA.
DISTANCIA_ATIVACAO_CONVIDADA = 245  # ALTERAÇÃO: quase no alcance da bolsada (200 px)
DISTANCIA_ATIVACAO_CONVIDADA_FINAL = 200  # ALTERAÇÃO: só acorda ao se aproximar MUITO na arena
DISTANCIA_ATIVACAO_PENETRA = 250  # ALTERAÇÃO: próximo ao alcance do tapa (220 px)
DISTANCIA_ATIVACAO_AMIGO_FINAL = 150  # ALTERAÇÃO: distância reduzida na arena; exige visibilidade completa
# ALTERAÇÃO: a Noiva fica 42% à esquerda da largura da janela; mais visão adiante.
POSICAO_NOIVA_CAMERA = 0.50
CONVIDADA_F2_TEMPO_ESPERA_VISIVEL = 0.0  # espera até entrar inteiramente no enquadramento
AMIGO_F2_TEMPO_ESPERA_VISIVEL = 0.0  # ALTERAÇÃO: os Amigos da segunda tela mantêm entrada original
# ALTERAÇÃO: os quatro inimigos da arena final permanecem em idle por 7s após aparecerem INTEIROS.
TEMPO_ESPERA_INIMIGOS_FINAIS = 7.0

# ALTERAÇÃO: Mesa 2 temporariamente desativada; nenhum cálculo de colisão.
# ALTERAÇÃO: bancos posicionados na ÚLTIMA tela da Fase 2 (coordenadas locais).
banco_superior = BancoBistro(INICIO_F2_FINAL, BANCO_SUPERIOR_DIREITO)
banco_inferior = BancoBistro(INICIO_F2_FINAL, BANCO_INFERIOR_ESQUERDO)
# ALTERAÇÃO: Dama Boss inicialmente sentada no banco superior direito.
dama_boss = DamaBoss(banco_superior)
# ALTERAÇÃO: possibilita descanso no banco inferior também.
dama_boss.banco_inferior = banco_inferior



# ============================================================
# PERSONAGENS
# ============================================================

noiva = Noiva(
    300,
    500
)

# ALTERAÇÃO: coordenadas diretas dos inimigos da Fase 1 (cada tela tem 1900 px).
# Segunda tela: X 1900 a 3800, centro X=2850.
# Quarta tela: X 5700 a 7600, centro X=6650.

# ALTERAÇÃO: dois Penetras 200px mais à direita na SEGUNDA tela.
# Mantidos os Y originais e 100 px de separação horizontal.

penetras = [
    Penetra(3000, 500),  # ALTERAÇÃO: opcionais direcao_inicial="esquerda", tempo_idle_inicial=3.0
#	Penetra(1200, 540),
    Penetra(3300, 460)
]


#penetras = []


# Distância vertical usada pelos penetras secundários.
# O mais próximo da noiva busca alinhamento direto.
# Os demais se aproximam por linhas deslocadas em Y.
OFFSET_FLANCO_Y = 90

# ALTERAÇÃO: duas Convidadas próximas ao centro da QUARTA tela (X=6650).
# ALTERAÇÃO: duas Convidadas na quarta tela, com coordenadas diretas.
convidadas_f1 = [Convidada(6600, 500), Convidada(6850, 540)]

# ALTERAÇÃO: lista geral para operações compartilhadas dos inimigos.
# A IA coordenada dos Penetras continua usando a lista "penetras".
# Para novos tipos, inclua a instância nesta lista geral.
inimigos = penetras + convidadas_f1

# ALTERAÇÃO: os quatro inimigos finais começam NO LIMITE DIREITO REAL do mundo,
# sem margens reservadas para inimigos. A margem da Noiva permanece independente.
# As posições em Y são defasadas para não ficarem em uma linha só.
def posicionar_inimigos_direita_final(amigos, convidadas):
    # ALTERAÇÃO: alinhar a BORDA DIREITA dos sprites de caminhada à borda
    # direita da última tela, independente da largura de cada personagem.
    for inimigo in amigos[-2:]:
        # ALTERAÇÃO: desloca os dois Amigos finais 80 px à esquerda do limite anterior.
        inimigo.x = LARGURA_CENARIO_F2 - inimigo.andando_direita.width - 80
    for inimigo in convidadas[-2:]:
        # ALTERAÇÃO: desloca as duas Convidadas finais 150 px à esquerda.
        inimigo.x = LARGURA_CENARIO_F2 - inimigo.andando_direita.width - 220

# ALTERAÇÃO: o Amigo é independente da lista de inimigos da Fase 1.
amigos_f2 = ([Amigo(INICIO_F2_2 + x, y, direcao_inicial="esquerda",
                           tempo_idle_inicial=AMIGO_F2_TEMPO_ESPERA_VISIVEL)
              for x, y in AMIGOS_F2_POSICOES]
             # ALTERAÇÃO: os dois novos Amigos são independentes e só ativam ao aparecer na tela final.
             + [Amigo(INICIO_F2_FINAL + x, y, direcao_inicial="esquerda",
                      tempo_idle_inicial=TEMPO_ESPERA_INIMIGOS_FINAIS)
                for x, y in AMIGOS_F2_POSICOES_FINAL])
# ALTERAÇÃO: Convidadas exclusivas da Fase 2, ativadas somente ao aparecerem na câmera.
convidadas_f2 = ([Convidada(INICIO_F2_3 + x, y, direcao_inicial="esquerda",
                            tempo_idle_inicial=CONVIDADA_F2_TEMPO_ESPERA_VISIVEL)
                  for x, y in CONVIDADAS_F2_POSICOES]
                 + [Convidada(INICIO_F2_FINAL + x, y, direcao_inicial="esquerda",
                              tempo_idle_inicial=TEMPO_ESPERA_INIMIGOS_FINAIS)
                    for x, y in CONVIDADAS_F2_POSICOES_FINAL])

# ALTERAÇÃO: posiciona ao fundo-direito somente os inimigos da tela final.
posicionar_inimigos_direita_final(amigos_f2, convidadas_f2)

# ALTERAÇÃO: boss independente; não participa dos golpes dos inimigos comuns.
sogra_boss = SograBoss()
# ALTERAÇÃO: aplicador surge depois que a primeira bola de fogo desaparecer.
aplicador = Aplicador()
# ALTERAÇÃO: a Fase 2 tem seu próprio aplicador, inicialmente não disponível.
aplicador_f2 = Aplicador()

# ============================================================
# ALTERAÇÃO: PONTUAÇÃO POR GOLPE VÁLIDO
# ============================================================
PONTOS_SOCO = 30  # Jab e direto
PONTOS_CHUTE = 10
pontuacao = 0


# ============================================================
# CONTROLE DE FASE / CÂMERA
# ============================================================

fase_atual = 2 if TESTE_INICIAR_FASE_2 else 1  # ALTERAÇÃO: teste reversível.
camera_x = 0  # ALTERAÇÃO: usado somente pelos GameImage (não pelos Sprite).
# ALTERAÇÃO: trava a arena final da Fase 2 assim que a Noiva entra nela.
arena_dama_ativa = False
camera.set_world_bounds(LARGURA_CENARIO, ALTURA_CENARIO)
# ALTERAÇÃO: no teste, inicia sem aplicador e (opcionalmente) na arena da Dama.
if TESTE_INICIAR_FASE_2:
    noiva.x = (100 if TESTE_INICIAR_NO_COMECO_FASE_2 else
               (INICIO_F2_FINAL + TESTE_NOIVA_X_LOCAL_F2) if TESTE_INICIAR_NA_ARENA_DAMA else
               max(100, INICIO_F2_FINAL - TESTE_DISTANCIA_ANTES_DA_ARENA))
    noiva.y = 500
    noiva.altura_plataforma = 0.0
    noiva.armada = False
    noiva.atirando = False
    noiva.disparo_pendente = False
    camera.set_world_bounds(LARGURA_CENARIO_F2, ALTURA_CENARIO_F2)
    # A lógica existente ativa o bloqueio da arena ao alcançar o centro da tela final.


# ============================================================
# ALTERAÇÃO: sprites do Noivo (4 quadros andando, 16 quadros pedido)
# Os PNGs ficam em cenas/, na raiz do projeto, sem editar os originais.
# ============================================================
noivo_andando = Sprite("cenas/noivo-andando.png", 4)
noivo_pedido = Sprite("cenas/noivo-pedido.png", 16)
noivo_andando.set_loop(True)
noivo_pedido.set_loop(False)

# ALTERAÇÃO: tela fixa de destino, desenhada sem câmera sobre toda a janela.
# Os limites são proporcionais à arte original de 1672 x 941 pixels.
imagem_destino = pygame.image.load("cenas/Destino.png").convert_alpha()
imagem_destino = pygame.transform.smoothscale(imagem_destino, (janela.width, janela.height))
FATOR_X_DESTINO = janela.width / 1672
FATOR_Y_DESTINO = janela.height / 941
BARRA_DESTINO_X = int(713 * FATOR_X_DESTINO)
BARRA_DESTINO_LARGURA = int(224 * FATOR_X_DESTINO)
BARRA_DESTINO_TOPO = int(241 * FATOR_Y_DESTINO)
BARRA_DESTINO_BASE = int(843 * FATOR_Y_DESTINO)
BARRA_DESTINO_ALTURA = BARRA_DESTINO_BASE - BARRA_DESTINO_TOPO
fonte_destino_total = pygame.font.Font(None, max(26, int(34 * FATOR_Y_DESTINO)))
fonte_destino_marcas = pygame.font.Font(None, max(20, int(24 * FATOR_Y_DESTINO)))
tempo_tela_destino = 0.0

# ALTERAÇÃO: ler todos os quadros dos GIFs, respeitando sua duração original.
# PPlay/Pygame não reproduzem GIF animado diretamente pelo Sprite.
# Cada quadro é convertido uma única vez em Surface para desenhar no jogo.
def carregar_gif_destino(caminho):
    quadros = []
    duracoes = []
    with Image.open(caminho) as gif:
        for indice in range(gif.n_frames):
            gif.seek(indice)
            quadro_rgba = gif.convert("RGBA")
            quadro_rgba.thumbnail((janela.width, janela.height), Image.Resampling.NEAREST)
            surface = pygame.image.fromstring(quadro_rgba.tobytes(),
                                              quadro_rgba.size, "RGBA").convert_alpha()
            quadros.append(surface)
            duracoes.append(max(0.02, gif.info.get("duration", 100) / 1000.0))
    return quadros, duracoes, sum(duracoes)

# ALTERAÇÃO: carregar somente o GIF escolhido, após a pontuação.
quadros_gif_destino = []
duracoes_gif_destino = []
duracao_ciclo_gif_destino = 0.0
tempo_gif_destino = 0.0
# ALTERAÇÃO: quadros controlados manualmente, independentes do FPS.

# ALTERAÇÃO: estados da cena final são reiniciados com a partida.
cena_final_estado = None        # None, espera, centralizando, entrada_noivo, pedido, pose
cena_final_tempo = 0.0
noivo_cena_x = 0.0
noivo_cena_pe_y = 0.0

# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    # ========================================================
    # ALTERAÇÃO: ABERTURA, MENU PRINCIPAL, PAUSA E RANKING
    # ========================================================
    if estado_tela == 'abertura':
        abertura.loop()
        abertura.draw()
        if abertura.concluida:
            # ALTERAÇÃO: desenhar o menu no buffer virtual da PPlay.
            # O Window.update() apresenta esse buffer e não apaga os botões.
            estado_tela = 'menu'
            menus.abrir('principal')
            menus.desenhar(fundo_pausado=False)
        janela.update()
        continue

    if estado_tela in ('menu', 'nome', 'pausa'):
        acao_menu = menus.atualizar()
        if acao_menu == 'sair':
            pygame.quit()
            break
        if acao_menu == 'continuar':
            # ALTERAÇÃO: pausa também pode retomar destino ou GIF final.
            estado_tela = estado_antes_pausa
            bloquear_esc_ate_soltar = True
        elif acao_menu == 'menu':
            estado_tela = 'menu'
            menus.abrir('principal')
        elif acao_menu == 'encerrar':
            estado_tela = 'nome'
            menus.abrir('nome', pontuacao)
        elif acao_menu in ('jogar', 'reiniciar'):
            # ALTERAÇÃO: nova partida reinicia apenas o estado do gameplay.
            noiva = Noiva(300, 500)
            tempo_exibicao_morte_noiva = 0.0  # ALTERAÇÃO: reinicia piscada final
            # ALTERAÇÃO: reinicia a Dama sentada para uma nova partida.
            dama_boss = DamaBoss(banco_superior)
            dama_boss.banco_inferior = banco_inferior
            arena_dama_ativa = False  # ALTERAÇÃO: reset da arena na nova partida.
            cena_final_estado = None  # ALTERAÇÃO: reinicia o epílogo ao reiniciar partida.
            tempo_tela_destino = 0.0  # ALTERAÇÃO: reinicia barra da lua de mel.
            quadros_gif_destino = []  # ALTERAÇÃO: limpa o GIF do jogo anterior.
            duracoes_gif_destino = []
            duracao_ciclo_gif_destino = 0.0
            tempo_gif_destino = 0.0
            cena_final_tempo = 0.0
            noivo_cena_x = 0.0
            noivo_cena_pe_y = 0.0
            penetras = [Penetra(3000, 500), Penetra(3300, 460)]
            # ALTERAÇÃO: recria as duas Convidadas da Fase 1 no reinício.
            convidadas_f1 = [Convidada(6600, 500), Convidada(6850, 540)]
            inimigos = penetras + convidadas_f1
            # ALTERAÇÃO: reiniciar também o Amigo na segunda tela.
            amigos_f2 = ([Amigo(INICIO_F2_2 + x, y, direcao_inicial="esquerda",
                           tempo_idle_inicial=AMIGO_F2_TEMPO_ESPERA_VISIVEL)
              for x, y in AMIGOS_F2_POSICOES]
             # ALTERAÇÃO: os dois novos Amigos são independentes e só ativam ao aparecer na tela final.
             + [Amigo(INICIO_F2_FINAL + x, y, direcao_inicial="esquerda",
                      tempo_idle_inicial=TEMPO_ESPERA_INIMIGOS_FINAIS)
                for x, y in AMIGOS_F2_POSICOES_FINAL])
            # ALTERAÇÃO: recria Convidadas da Fase 2 no reinício.
            convidadas_f2 = ([Convidada(INICIO_F2_3 + x, y, direcao_inicial="esquerda",
                                        tempo_idle_inicial=CONVIDADA_F2_TEMPO_ESPERA_VISIVEL)
                              for x, y in CONVIDADAS_F2_POSICOES]
                             + [Convidada(INICIO_F2_FINAL + x, y, direcao_inicial="esquerda",
                                          tempo_idle_inicial=TEMPO_ESPERA_INIMIGOS_FINAIS)
                                for x, y in CONVIDADAS_F2_POSICOES_FINAL])
            # ALTERAÇÃO: aplica a posição final também no reinício da partida.
            posicionar_inimigos_direita_final(amigos_f2, convidadas_f2)
            sogra_boss = SograBoss()
            aplicador = Aplicador()
            aplicador_f2 = Aplicador()
            pontuacao = 0
            # ALTERAÇÃO: Reiniciar/Jogar respeitam as chaves de teste da Fase 2.
            fase_atual = 2 if TESTE_INICIAR_FASE_2 else 1
            if TESTE_INICIAR_FASE_2:
                noiva.x = (100 if TESTE_INICIAR_NO_COMECO_FASE_2 else
                           (INICIO_F2_FINAL + TESTE_NOIVA_X_LOCAL_F2)
                           if TESTE_INICIAR_NA_ARENA_DAMA else
                           max(100, INICIO_F2_FINAL - TESTE_DISTANCIA_ANTES_DA_ARENA))
                noiva.y = 500
                noiva.armada = False
                noiva.atirando = False
                noiva.disparo_pendente = False
            camera_x = 0
            camera.set_world_bounds(
                LARGURA_CENARIO_F2 if TESTE_INICIAR_FASE_2 else LARGURA_CENARIO,
                ALTURA_CENARIO_F2 if TESTE_INICIAR_FASE_2 else ALTURA_CENARIO
            )
            estado_tela = 'jogo'
            bloquear_esc_ate_soltar = True
        if estado_tela != 'jogo':
            if estado_tela == 'pausa':
                janela.screen.blit(tela_pausa, (0, 0))
                menus.desenhar(fundo_pausado=True)
            else:
                menus.desenhar(fundo_pausado=False)
            janela.update()
            continue

    # ALTERAÇÃO: pausa por ESC, ANTES de qualquer atualização da partida.
    if not pygame.key.get_pressed()[pygame.K_ESCAPE]:
        bloquear_esc_ate_soltar = False
    if not bloquear_esc_ate_soltar and teclado.key_down('ESC'):
        estado_antes_pausa = estado_tela  # ALTERAÇÃO: retomar jogo, destino ou GIF final.
        estado_tela = 'pausa'
        menus.abrir('pausa')
        # ALTERAÇÃO: o buffer virtual já foi limpo pelo update() anterior.
        # Recuperar a última imagem completa da partida para o fundo da pausa.
        tela_pausa = ultima_tela_jogo.copy() if ultima_tela_jogo is not None else janela.screen.copy()
        janela.screen.blit(tela_pausa, (0, 0))
        menus.desenhar(fundo_pausado=True)
        janela.update()
        continue

    # ALTERAÇÃO: limita o primeiro dt após menus/pausa para evitar saltos de tempo.
    dt = min(janela.delta_time(), 0.05)

    # ========================================================
    # ALTERAÇÃO: TELA DE DESTINO — 4s preenchendo + 4s de leitura
    # ========================================================
    # Estado independente: não atualiza a Noiva, Boss nem inimigos.
    # A pontuação real é preservada inclusive acima da escala visual (1500).
    if estado_tela == 'destino':
        tempo_tela_destino += dt
        janela.screen.blit(imagem_destino, (0, 0))

        progresso_tempo = min(1.0, tempo_tela_destino / DURACAO_ENCHIMENTO_DESTINO)
        fracao_pontos = min(1.0, max(0, pontuacao) / PONTUACAO_TOPO_DESTINO)
        altura_preenchida = round(BARRA_DESTINO_ALTURA * progresso_tempo * fracao_pontos)

        # ALTERAÇÃO: linhas horizontais empilhadas de baixo para cima.
        # Cada terço possui uma cor e equivale a 500 pontos.
        for altura in range(0, altura_preenchida, 5):
            posicao_y = BARRA_DESTINO_BASE - altura - 1
            fracao_altura = altura / BARRA_DESTINO_ALTURA
            if fracao_altura < 1 / 3:
                cor_linha = (93, 193, 152)      # 0 a 500
            elif fracao_altura < 2 / 3:
                cor_linha = (245, 186, 81)      # 500 a 1000
            else:
                cor_linha = (228, 112, 111)     # acima de 1000
            pygame.draw.line(janela.screen, cor_linha,
                             (BARRA_DESTINO_X, posicao_y),
                             (BARRA_DESTINO_X + BARRA_DESTINO_LARGURA, posicao_y), 4)

        # ALTERAÇÃO: divisões visíveis dos três terços (500 e 1000 pontos).
        for marco in (1, 2):
            marca_y = BARRA_DESTINO_BASE - round(BARRA_DESTINO_ALTURA * marco / 3)
            pygame.draw.line(janela.screen, (104, 55, 61),
                             (BARRA_DESTINO_X - 5, marca_y),
                             (BARRA_DESTINO_X + BARRA_DESTINO_LARGURA + 5, marca_y), 2)
            rotulo = fonte_destino_marcas.render(f'{marco * PONTOS_TERCO_DESTINO}', True,
                                                 (106, 53, 57))
            janela.screen.blit(rotulo, (BARRA_DESTINO_X + 6, marca_y - rotulo.get_height() - 4))

        # ALTERAÇÃO: total real aparece e cresce junto com a barra.
        pontos_visiveis = round(pontuacao * progresso_tempo)
        texto_total = fonte_destino_total.render(f'TOTAL: {pontos_visiveis}', True, (89, 35, 49))
        centro_coluna = BARRA_DESTINO_X + BARRA_DESTINO_LARGURA // 2
        janela.screen.blit(texto_total,
                          (centro_coluna - texto_total.get_width() // 2,
                           int(183 * FATOR_Y_DESTINO)))

        if tempo_tela_destino >= DURACAO_ENCHIMENTO_DESTINO + TEMPO_RESULTADO_DESTINO:
            # ALTERAÇÃO: selecionar destino pela pontuação e reproduzir GIF por 10s.
            if pontuacao <= PONTOS_TERCO_DESTINO:
                indice_destino = 0       # Petrópolis: 0 a 500
            elif pontuacao <= 2 * PONTOS_TERCO_DESTINO:
                indice_destino = 1       # Paris: 501 a 1000
            else:
                indice_destino = 2       # Maldivas: acima de 1000
            quadros_gif_destino, duracoes_gif_destino, duracao_ciclo_gif_destino = ( 
                carregar_gif_destino(ARQUIVOS_GIFS_DESTINO[indice_destino])
            )
            tempo_gif_destino = 0.0
            estado_tela = 'gif_destino'
            # ALTERAÇÃO: a nova tela será desenhada no próximo frame.
            continue
        # ALTERAÇÃO: preservar imagem da tela do destino ao pausar.
        ultima_tela_jogo = janela.screen.copy()
        janela.update()
        continue

    # ========================================================
    # ALTERAÇÃO: GIF DO DESTINO — 10 SEGUNDOS APÓS A PONTUAÇÃO
    # ========================================================
    # Os quadros seguem os tempos originais do GIF e repetem até completar 10s.
    # O estado independente não atualiza inimigos, câmera nem personagens.
    if estado_tela == 'gif_destino':
        tempo_gif_destino += dt
        if tempo_gif_destino >= TEMPO_GIF_DESTINO:
            estado_tela = 'nome'
            menus.abrir('nome', pontuacao)
            menus.desenhar()
            janela.update()
            continue
        instante_ciclo = tempo_gif_destino % duracao_ciclo_gif_destino
        quadro_atual = 0
        for indice, duracao_quadro in enumerate(duracoes_gif_destino):
            if instante_ciclo < duracao_quadro:
                quadro_atual = indice
                break
            instante_ciclo -= duracao_quadro
        quadro = quadros_gif_destino[quadro_atual]
        janela.screen.fill((0, 0, 0))
        # ALTERAÇÃO: guardar a posição real do GIF para escrever FIM logo abaixo.
        gif_x = (janela.width - quadro.get_width()) // 2
        gif_y = (janela.height - quadro.get_height()) // 2
        janela.screen.blit(quadro, (gif_x, gif_y))
        # ALTERAÇÃO: mensagem amarela durante toda a cena final de 10 segundos.
        fonte_fim = pygame.font.SysFont('arial', 80, bold=True)
        texto_fim = fonte_fim.render('FIM', True, (255, 225, 35))
        sombra_fim = fonte_fim.render('FIM', True, (95, 48, 25))
        texto_x = (janela.width - texto_fim.get_width()) // 2
        texto_y = gif_y + quadro.get_height() + 22
        # Evita corte caso a altura do GIF seja alterada posteriormente.
        texto_y = min(texto_y, janela.height - texto_fim.get_height() - 8)
        janela.screen.blit(sombra_fim, (texto_x + 3, texto_y + 3))
        janela.screen.blit(texto_fim, (texto_x, texto_y))
        ultima_tela_jogo = janela.screen.copy()
        janela.update()
        continue

    # ALTERAÇÃO: na última vida, dá tempo para ver a Noiva caída piscando
    # antes de entrar no menu de pontuação; não interfere nas quedas normais.
    if noiva.eliminada:
        tempo_exibicao_morte_noiva += dt
        if tempo_exibicao_morte_noiva >= TEMPO_EXIBICAO_MORTE_NOIVA:
            estado_tela = 'nome'
            menus.abrir('nome', pontuacao)
            menus.desenhar()
            janela.update()
            continue

    # ========================================================
    # ALTERAÇÃO: EPÍLOGO INICIADO PELA DERROTA REAL DA DAMA
    # ========================================================
    if (fase_atual == 2 and arena_dama_ativa
            and cena_final_estado is None and dama_boss.estado == 'derrotada'
            and not noiva.eliminada):
        cena_final_estado = 'espera'
        cena_final_tempo = 0.0
        # ALTERAÇÃO: interrompe novos golpes e deixa a derrota da Boss em destaque.
        noiva.atacando = False
        noiva.andando = False
        noiva.pulando = False
        noiva.atirando = False
        noiva.armada = False  # ALTERAÇÃO: usar caminhada desarmada no epílogo.
        noiva.altura_pulo = 0.0
        dama_boss.tiros.clear()
        dama_boss.granadas.clear()
        dama_boss.explosoes.clear()

    # ========================================================
    # DEFINE O MUNDO ATUAL
    # ========================================================

    if fase_atual == 1:

        largura_mundo_atual = LARGURA_CENARIO
        altura_mundo_atual = ALTURA_CENARIO

    else:

        largura_mundo_atual = LARGURA_CENARIO_F2
        altura_mundo_atual = ALTURA_CENARIO_F2


    # ========================================================
    # ALTERAÇÃO: ESPERA INICIAL APÓS ENTRAR INTEIRO NA TELA
    # ========================================================
    # A câmera calculada no frame anterior já representa a área visível.
    # Cada inimigo controla seu próprio tempo e direção iniciais.
    if fase_atual == 1:
        for inimigo in inimigos:
            if isinstance(inimigo, Penetra):
                # ALTERAÇÃO: Penetra.atualizar_entrada recebe apenas (dt, camera_x, largura_tela).
                # A proximidade é verificada aqui, sem alterar a classe nem a Fase 2.
                # ALTERAÇÃO: medir a distância LIVRE entre os limites visuais,
                # não entre centros. Assim o Penetra ativa ANTES de a Noiva passar por ele.
                largura_noiva = noiva.andando_direita.width
                largura_penetra = inimigo.andando_direita.width
                distancia_livre = max(0.0, noiva.x - (inimigo.x + largura_penetra),
                                     inimigo.x - (noiva.x + largura_noiva))
                visivel_inteiro = (inimigo.x >= camera_x and
                                   inimigo.x + largura_penetra <= camera_x + janela.width)
                if visivel_inteiro and distancia_livre <= DISTANCIA_ATIVACAO_PENETRA:
                    inimigo.atualizar_entrada(dt, camera_x, janela.width)
                else:
                    # ALTERAÇÃO: aguarda em idle até estar inteiro na tela e perto da Noiva.
                    inimigo.tempo_idle_inicial = 0.0
                    inimigo.entrada_visivel = visivel_inteiro
            else:
                inimigo.atualizar_entrada(dt, camera_x, janela.width, noiva,
                                         DISTANCIA_ATIVACAO_CONVIDADA)

    # ========================================================
    # ATUALIZA OS PENETRAS
    # ========================================================

    # ALTERAÇÃO: preserva a opção de desativar os penetras para testes.
    if fase_atual == 1 and len(penetras) > 0:

        # ----------------------------------------------------
        # IA COORDENADA DOS PENETRAS
        # ----------------------------------------------------
        #
        # O penetra mais próximo da noiva é o agressor principal
        # e busca alinhamento direto em Y.
        #
        # Os outros se aproximam por linhas deslocadas em Y,
        # evitando que todos tentem ocupar exatamente a mesma faixa.
        #
        # A comparação usa a distância entre os centros dos corpos.
        # ALTERAÇÃO: vivos e liberados participam da IA coordenada.
        penetras_ativos = [p for p in penetras if not p.removido and p.entrada_liberada]
        penetra_principal = None
        secundarios = []

        if penetras_ativos:
            penetra_principal = min(
                penetras_ativos,
                key=lambda p: (
                    (p.centro_x - noiva.centro_x) ** 2
                    + (p.centro_y - noiva.centro_y) ** 2
                )
            )

            secundarios = [
                p for p in penetras_ativos
                if p is not penetra_principal
            ]

        # ALTERAÇÃO: todos atualizam os temporizadores de queda e garrafas;
        # apenas os ativos participam da estratégia de flanqueamento.
        for penetra in penetras:
            offset_y = 0
            if penetra in secundarios:
                i = secundarios.index(penetra)
                if len(secundarios) == 1:
                    if penetra.centro_y < noiva.centro_y:
                        offset_y = -OFFSET_FLANCO_Y
                    else:
                        offset_y = OFFSET_FLANCO_Y
                else:
                    if i % 2 == 0:
                        offset_y = -OFFSET_FLANCO_Y
                    else:
                        offset_y = OFFSET_FLANCO_Y

            penetra.atualizar(
                noiva,
                dt,
                LARGURA_CENARIO,
                ALTURA_CENARIO,
                offset_y
            )

    # ========================================================
    # ATUALIZA A CONVIDADA - FASE 1
    # ========================================================

    if fase_atual == 1:
        # ALTERAÇÃO: atualizar as duas Convidadas de forma independente.
        for convidada_f1 in convidadas_f1:
            if convidada_f1.estado != "removida":
                convidada_f1.atualizar(noiva, dt, LARGURA_CENARIO, ALTURA_CENARIO, 0)


    # ========================================================
    # ALTERAÇÃO: AMIGO - FASE 2 (A PARTIR DA SEGUNDA TELA)
    # ========================================================
    if fase_atual == 2 and cena_final_estado is None:  # ALTERAÇÃO: congela IA durante epílogo
        for amigo_f2 in amigos_f2:
            if amigo_f2.removido:
                continue
            # ALTERAÇÃO: na tela da Dama, o Amigo só acorda quando está
            # INTEIRO visível E a Noiva se aproxima de sua posição.
            # ALTERAÇÃO: na arena final, os 150 px são a distância LIVRE
            # entre os corpos visuais, não entre seus centros. A Noiva tem
            # sprites largos e seu X é limitado na borda da arena; comparar
            # centros diretamente podia impedir a ativação dos Amigos finais.
            if amigo_f2.x >= INICIO_F2_FINAL:
                raio_entrada_amigo = (
                    DISTANCIA_ATIVACAO_AMIGO_FINAL
                    + noiva.idle_direita.width / 2
                    + amigo_f2.andando_direita.width / 2
                )
            else:
                raio_entrada_amigo = None
            amigo_f2.atualizar_entrada(dt, camera_x, janela.width,
                                      noiva, raio_entrada_amigo)
            if amigo_f2.entrada_liberada:
                amigo_f2.atualizar(noiva, dt, LARGURA_CENARIO_F2, ALTURA_CENARIO_F2)

    # ========================================================
    # ALTERAÇÃO: CONVIDADAS DA FASE 2 - TERCEIRA TELA E ARENA FINAL
    # ========================================================
    if fase_atual == 2 and cena_final_estado is None:  # ALTERAÇÃO: congelar inimigos durante epílogo
        for convidada_f2 in convidadas_f2:
            if convidada_f2.estado == "removida":
                continue
            # ALTERAÇÃO: as Convidadas finais usam uma distância menor;
            # visibilidade completa continua obrigatória dentro da classe.
            raio_entrada_convidada = (DISTANCIA_ATIVACAO_CONVIDADA_FINAL
                                       if convidada_f2.x >= INICIO_F2_FINAL
                                       else DISTANCIA_ATIVACAO_CONVIDADA)
            convidada_f2.atualizar_entrada(dt, camera_x, janela.width,
                                          noiva, raio_entrada_convidada)
            if convidada_f2.entrada_liberada:
                convidada_f2.atualizar(noiva, dt, LARGURA_CENARIO_F2, ALTURA_CENARIO_F2, 0)

    # ========================================================
    # ALTERAÇÃO: SEPARAÇÃO SUAVE ENTRE INIMIGOS DA ARENA FINAL
    # ========================================================
    # Evita que dois personagens (Amigos ou Convidadas) persigam a Noiva
    # até ocupar praticamente a mesma posição. Só corrige quem já está
    # movimentando; quem está aguardando permanece imóvel no idle.
    if fase_atual == 2 and cena_final_estado is None:  # ALTERAÇÃO: sem separação durante epílogo
        grupo_final = [i for i in amigos_f2[-2:] if i.entrada_liberada and not (
            i.caindo or i.derrotado or i.levantando or i.eliminado or i.removido or i.atacando)]
        grupo_final += [i for i in convidadas_f2[-2:] if i.entrada_liberada and i.estado == "andando"]
        for indice, primeiro in enumerate(grupo_final):
            for segundo in grupo_final[indice + 1:]:
                # ALTERAÇÃO: pés são a referência natural de profundidade.
                pe_primeiro = primeiro.y + primeiro.andando_direita.height
                pe_segundo = segundo.y + segundo.andando_direita.height
                dx = abs(primeiro.centro_x - segundo.centro_x)
                dy = abs(pe_primeiro - pe_segundo)
                if dx < 110 and dy < 80:
                    # ALTERAÇÃO: corrige a faixa Y progressivamente, sem teleporte.
                    # Para posições iguais, desempata pela ordem no grupo.
                    sinal = 1 if pe_primeiro >= pe_segundo else -1
                    passo = min(85 * dt, (80 - dy) / 2)
                    primeiro.y += sinal * passo
                    segundo.y -= sinal * passo
                    for personagem in (primeiro, segundo):
                        minimo = ALTURA_CENARIO_F2 - noiva.ALTURA_PISTA - personagem.andando_direita.height
                        maximo = ALTURA_CENARIO_F2 - personagem.andando_direita.height
                        personagem.y = max(minimo, min(personagem.y, maximo))

    # ========================================================
    # ATUALIZA A NOIVA
    # ========================================================

    # ALTERAÇÃO: somente na arena FINAL da Fase 2, ampliar em 200px
    # a faixa de movimento vertical da Noiva em direção ao topo.
    # O limite superior é calculado dentro de Noiva.atualizar() usando
    # ALTURA_PISTA. Alterar somente o valor desta instância evita
    # interferir na Fase 1 e nas telas anteriores da Fase 2.
    noiva.ALTURA_PISTA = Noiva.ALTURA_PISTA + (
        ALTURA_EXTRA_Y_ARENA_DAMA if fase_atual == 2 and arena_dama_ativa else 0
    )

    # ALTERAÇÃO: durante a cena final, a Noiva é dirigida pelo roteiro,
    # sem leitura de teclado ou novas animações de combate.
    if cena_final_estado is None:
        noiva.atualizar(
            teclado,
            dt,
            largura_mundo_atual,
            altura_mundo_atual
        )
    else:
        cena_final_tempo += dt
        noiva.atacando = False
        noiva.pulando = False
        noiva.atirando = False
        noiva.altura_pulo = 0.0
        noiva.altura_plataforma = 0.0
        noiva.andando = False
        # ALTERAÇÃO: alvo horizontal e vertical no centro da faixa jogável.
        centro_tela_x = max(0, LARGURA_CENARIO_F2 - janela.width) + janela.width / 2
        alvo_noiva_x = centro_tela_x - noiva.CENTRO_CORPO_X
        y_superior = ALTURA_CENARIO_F2 - noiva.ALTURA_PISTA - noiva.altura
        y_inferior = ALTURA_CENARIO_F2 - noiva.altura
        alvo_noiva_y = (y_superior + y_inferior) / 2

        if cena_final_estado == 'espera':
            if cena_final_tempo >= ESPERA_APOS_DERROTA_DAMA:
                cena_final_estado = 'centralizando'
                cena_final_tempo = 0.0

        elif cena_final_estado == 'centralizando':
            # ALTERAÇÃO: move os dois eixos por dt, exibindo a caminhada.
            passo = VELOCIDADE_NOIVA_CENA_FINAL * dt
            dx = alvo_noiva_x - noiva.x
            dy = alvo_noiva_y - noiva.y
            distancia = (dx * dx + dy * dy) ** 0.5
            if distancia > passo and distancia > 0:
                noiva.x += dx / distancia * passo
                noiva.y += dy / distancia * passo
                noiva.andando = True
                noiva.direcao = 'direita' if dx >= 0 else 'esquerda'
            else:
                noiva.x, noiva.y = alvo_noiva_x, alvo_noiva_y
                noiva.direcao = 'direita'  # ALTERAÇÃO: olha para o Noivo.
                cena_final_estado = 'entrada_noivo'
                cena_final_tempo = 0.0
                noivo_cena_x = LARGURA_CENARIO_F2 + 5  # entra totalmente pela direita
                noivo_cena_pe_y = noiva.y + noiva.altura

        elif cena_final_estado == 'entrada_noivo':
            alvo_noivo_x = noiva.centro_x + DISTANCIA_PEDIDO_NOIVO
            noivo_cena_x = max(alvo_noivo_x,
                               noivo_cena_x - VELOCIDADE_NOIVO_CENA_FINAL * dt)
            if noivo_cena_x <= alvo_noivo_x:
                noivo_cena_x = alvo_noivo_x
                cena_final_estado = 'pedido'
                cena_final_tempo = 0.0

        elif cena_final_estado == 'pedido':
            if cena_final_tempo >= DURACAO_NOIVO_PEDIDO:
                cena_final_estado = 'pose'
                cena_final_tempo = 0.0

        elif cena_final_estado == 'pose':
            if cena_final_tempo >= TEMPO_POSE_PEDIDO:
                # ALTERAÇÃO: após o pedido, mostrar a barra de pontos antes do ranking.
                tempo_tela_destino = 0.0
                estado_tela = 'destino'
                continue

    # ========================================================
    # ALTERAÇÃO: ARENA FINAL DA DAMA - FASE 2 (1600 x 900)
    # ========================================================
    # Depois que a Noiva entra na última tela, congela a câmera e impede
    # atravessar as bordas. O gatilho de despertar é independente da arena.
    if fase_atual == 2:
        camera_final_f2_x = max(0, LARGURA_CENARIO_F2 - janela.width)
        # ALTERAÇÃO: só trava após a câmera mostrar quase TODA a última tela.
        # Antes, o gatilho pelo X da Noiva podia causar um salto grande na câmera.
        MARGEM_TRAVAMENTO_ARENA_F2 = 35  # px faltantes para a última tela ocupar a janela
        if (not arena_dama_ativa
                and camera_x >= camera_final_f2_x - MARGEM_TRAVAMENTO_ARENA_F2
                and noiva.centro_x >= INICIO_F2_FINAL):
            arena_dama_ativa = True
        if arena_dama_ativa:
            # ALTERAÇÃO: limitar pelo CENTRO CORPORAL, não pelo PNG de 480 px.
            # Permite chegar bem próximo das duas bordas para alcançar inimigos.
            limite_esquerdo_f2 = (camera_final_f2_x + MARGEM_LATERAL_NOIVA_ARENA
                                  + noiva.METADE_LARGURA_HITBOX - noiva.CENTRO_CORPO_X)
            limite_direito_f2 = (camera_final_f2_x + janela.width
                                 - MARGEM_LATERAL_NOIVA_ARENA
                                 - noiva.METADE_LARGURA_HITBOX - noiva.CENTRO_CORPO_X)
            noiva.x = max(limite_esquerdo_f2, min(noiva.x, limite_direito_f2))

    # ALTERAÇÃO: a Mesa 2 está desativada; os bancos não têm colisão.


    # ========================================================
    # ALTERAÇÃO: LIMITES DA ARENA FINAL DA SOGRA BOSS
    # ========================================================
    # Trava a posição REAL da Noiva, não apenas a câmera.
    # Usa a maior largura visual dos sprites para evitar que
    # parte da personagem saia pelas bordas da última tela.
    if fase_atual == 1 and sogra_boss.ativa:
        camera_final_x = max(0, LARGURA_CENARIO - janela.width)
        margem_arena = 10
        largura_visual_noiva = max(
            noiva.idle_direita.width,
            noiva.andando_direita.width,
            noiva.salto_direita.width,
            noiva.jab_direita.width,
            noiva.direto_direita.width,
            noiva.chute_direita.width,
            noiva.queda_direita.width
        )
        x_min_arena = camera_final_x + margem_arena
        x_max_arena = camera_final_x + janela.width - largura_visual_noiva - margem_arena
        if x_max_arena < x_min_arena:
            x_max_arena = x_min_arena
        noiva.x = max(x_min_arena, min(noiva.x, x_max_arena))

    # ========================================================
    # ALTERAÇÃO: DANO DA NOIVA EM TODOS OS INIMIGOS
    # ========================================================

    if fase_atual == 1 and not noiva.eliminada:
        for inimigo in inimigos:
            # ALTERAÇÃO: o método retorna True apenas para um novo acerto válido.
            # A identificação do ataque impede repetir pontos no mesmo inimigo.
            if inimigo.verificar_golpe_noiva(noiva):
                if noiva.tipo_ataque == "chute":
                    pontuacao += PONTOS_CHUTE
                else:
                    pontuacao += PONTOS_SOCO


    # ========================================================
    # ALTERAÇÃO: golpes da Noiva no Amigo somente após ativação visual.
    # ========================================================
    if fase_atual == 2 and cena_final_estado is None and not noiva.eliminada:  # ALTERAÇÃO: bloqueia combate no epílogo
        for amigo_f2 in amigos_f2:
            if amigo_f2.entrada_liberada and not amigo_f2.removido:
                if amigo_f2.verificar_golpe_noiva(noiva):
                    pontuacao += PONTOS_CHUTE if noiva.tipo_ataque == "chute" else PONTOS_SOCO

    # ALTERAÇÃO: golpes da Noiva também atingem as Convidadas da Fase 2.
    if fase_atual == 2 and cena_final_estado is None and not noiva.eliminada:
        for convidada_f2 in convidadas_f2:
            if convidada_f2.entrada_liberada and convidada_f2.estado != "removida":
                if convidada_f2.verificar_golpe_noiva(noiva):
                    pontuacao += PONTOS_CHUTE if noiva.tipo_ataque == "chute" else PONTOS_SOCO

    # ========================================================
    # TROCA DA FASE 1 PARA A FASE 2
    # ========================================================

    if (
        fase_atual == 1
        # ALTERAÇÃO: mantém a Noiva na arena enquanto a Boss estiver ativa.
        # A passagem para a fase seguinte será liberada com a derrota da Sogra.
        and not sogra_boss.ativa
        and noiva.x >= LARGURA_CENARIO - noiva.largura
    ):

        fase_atual = 2

        noiva.x = 100
        noiva.y = 500
        # ALTERAÇÃO: começa a Fase 2 no nível do chão.
        noiva.altura_plataforma = 0.0
        dama_boss = DamaBoss(banco_superior)
        dama_boss.banco_inferior = banco_inferior
        # ALTERAÇÃO: ao entrar na Fase 2 a Noiva recomeça desarmada.
        noiva.armada = False
        noiva.atirando = False
        noiva.disparo_pendente = False
        aplicador_f2 = Aplicador()
        # ALTERAÇÃO: recria Amigo ao atravessar da Fase 1 para a Fase 2.
        amigos_f2 = ([Amigo(INICIO_F2_2 + x, y, direcao_inicial="esquerda",
                           tempo_idle_inicial=AMIGO_F2_TEMPO_ESPERA_VISIVEL)
              for x, y in AMIGOS_F2_POSICOES]
             # ALTERAÇÃO: os dois novos Amigos são independentes e só ativam ao aparecer na tela final.
             + [Amigo(INICIO_F2_FINAL + x, y, direcao_inicial="esquerda",
                      tempo_idle_inicial=TEMPO_ESPERA_INIMIGOS_FINAIS)
                for x, y in AMIGOS_F2_POSICOES_FINAL])
        # ALTERAÇÃO: recria Convidadas da Fase 2 ao trocar de fase.
        convidadas_f2 = ([Convidada(INICIO_F2_3 + x, y, direcao_inicial="esquerda",
                                    tempo_idle_inicial=CONVIDADA_F2_TEMPO_ESPERA_VISIVEL)
                          for x, y in CONVIDADAS_F2_POSICOES]
                         + [Convidada(INICIO_F2_FINAL + x, y, direcao_inicial="esquerda",
                                      tempo_idle_inicial=TEMPO_ESPERA_INIMIGOS_FINAIS)
                            for x, y in CONVIDADAS_F2_POSICOES_FINAL])
        # ALTERAÇÃO: aplica a posição final na transição entre as fases.
        posicionar_inimigos_direita_final(amigos_f2, convidadas_f2)
        arena_dama_ativa = False  # ALTERAÇÃO: novo encontro da Boss na Fase 2.
        cena_final_estado = None  # ALTERAÇÃO: nova fase recomeça sem epílogo ativo.
        cena_final_tempo = 0.0

        # ALTERAÇÃO: a nova fase tem limites próprios de câmera.
        largura_mundo_atual = LARGURA_CENARIO_F2
        altura_mundo_atual = ALTURA_CENARIO_F2


    # ========================================================
    # CÂMERA
    # ========================================================

    # ALTERAÇÃO: a PPlay aplica automaticamente a câmera em Sprite.draw().
    # Usamos o sprite de caminhada apenas como alvo de acompanhamento,
    # sem criar outro objeto ou alterar a posição real da Noiva.
    # O centro do alvo corresponde a noiva.x, como na câmera anterior.
    camera.set_world_bounds(largura_mundo_atual, altura_mundo_atual)

    # ALTERAÇÃO: ativa o Boss quando a Noiva chega ao enquadramento
    # final; assim a câmera já fica travada neste mesmo frame.
    if fase_atual == 1 and not sogra_boss.ativa and not sogra_boss.derrotada:
        camera_final_x = max(0, LARGURA_CENARIO - janela.width)
        if noiva.x >= camera_final_x + janela.width / 2 - 10:
            sogra_boss.ativar()
            # ALTERAÇÃO: aplica os limites já no frame de ativação da arena.
            margem_arena = 10
            largura_visual_noiva = max(
                noiva.idle_direita.width,
                noiva.andando_direita.width,
                noiva.salto_direita.width,
                noiva.jab_direita.width,
                noiva.direto_direita.width,
                noiva.chute_direita.width,
                noiva.queda_direita.width
            )
            noiva.x = max(camera_final_x + margem_arena, min(
                noiva.x, camera_final_x + janela.width - largura_visual_noiva - margem_arena
            ))

    alvo_camera = noiva.andando_direita
    # ALTERAÇÃO: na última tela da Fase 1, a câmera permanece fixa.
    # A Noiva circula pela arena sem recentralizar a imagem.
    # Antes de chegar à última tela, conserva o acompanhamento original.
    if fase_atual == 1 and sogra_boss.ativa:
        camera_final_x = max(0, LARGURA_CENARIO - janela.width)
        alvo_x = camera_final_x + janela.width / 2
    # ALTERAÇÃO: fixar câmera durante toda a arena final da Dama.
    elif fase_atual == 2 and arena_dama_ativa:
        alvo_x = max(0, LARGURA_CENARIO_F2 - janela.width) + janela.width / 2
    else:
        # ALTERAÇÃO: acompanha a Noiva um pouco atrás do meio da janela.
        # Deslocar o ALVO à frente mantém a Noiva mais à esquerda na imagem.
        # ALTERAÇÃO: acompanhar o CENTRO REAL do corpo, não a borda do PNG.
        # Centraliza assim que há mundo suficiente dos dois lados; no início
        # e no final a câmera respeita set_world_bounds (sem mostrar vazio).
        alvo_x = noiva.centro_x + janela.width * (0.5 - POSICAO_NOIVA_CAMERA)

    alvo_camera.set_position(
        alvo_x - alvo_camera.width / 2,
        janela.height / 2 - alvo_camera.height / 2
    )
    camera.follow(alvo_camera, 1.0)  # 1.0 = acompanhamento imediato.

    # ALTERAÇÃO: GameImage.draw() ignora a câmera. Convertê-lo manualmente
    # mantém o parallax, cenário e overlay alinhados na tela.
    camera_x = camera.transform_x(0) * -1

    # ========================================================
    # ALTERAÇÃO: SOGRA BOSS - SOMENTE ÚLTIMA TELA DA FASE 1
    # ========================================================
    # A câmera chegou ao extremo direito do mundo: última tela visível.
    # Posição é calculada na METADE DIREITA DA TELA, não do mundo.
    if fase_atual == 1:
        # ALTERAÇÃO: a ativação é feita ANTES da câmera ser calculada.
        # Isso evita um frame de ativação com a câmera em outra posição.
        sogra_boss.atualizar(dt, camera_x, janela.width, janela.height, noiva)  # ALTERAÇÃO: mira no disparo.


    # ========================================================
    # ALTERAÇÃO: QUEDA, COLETA E DISPARO DO APLICADOR
    # ========================================================
    if fase_atual == 1:
        # O primeiro projétil deve ter terminado (colisão ou saída da tela).
        if sogra_boss.ativa and sogra_boss.primeira_bola_encerrada:
            aplicador.soltar(camera_x, janela.width, janela.height, noiva)
        aplicador.atualizar_coleta(dt, noiva)
        if noiva.disparo_pendente:
            if noiva.armada:
                aplicador.disparar(noiva, sogra_boss)
            noiva.disparo_pendente = False
        pontuacao += aplicador.atualizar_tiros(
            dt, camera_x, janela.width, janela.height, inimigos, sogra_boss, noiva
        )

    # ========================================================
    # ALTERAÇÃO: FASE 2 - ARMA, DANO E PONTUAÇÃO DA DAMA
    # ========================================================
    if fase_atual == 2 and arena_dama_ativa:
        # Antes de encontrar o novo aplicador, Z e C são soco e chute.
        if cena_final_estado is None and not noiva.eliminada and dama_boss.verificar_golpe_noiva(noiva):
            pontuacao += (dama_boss.PONTOS_CHUTE_DAMA if noiva.tipo_ataque == 'chute'
                          else dama_boss.PONTOS_SOCO_DAMA)
        # Cronômetro começa só após o salto inicial terminar.
        if cena_final_estado is None and dama_boss.tempo_combate >= 120.0 and not noiva.armada:
            aplicador_f2.soltar(camera_x, janela.width, janela.height, noiva)
        if cena_final_estado is None:  # ALTERAÇÃO: não criar novos disparos na celebração
            aplicador_f2.atualizar_coleta(dt, noiva)
            if noiva.disparo_pendente:
                if noiva.armada:
                    aplicador_f2.disparar(noiva, sogra_boss)
                noiva.disparo_pendente = False
            pontuacao += aplicador_f2.atualizar_tiros(
                dt, camera_x, janela.width, janela.height, [], sogra_boss, noiva, dama_boss
            )

    # ========================================================
    # ALTERAÇÃO: ATUALIZA AS ANIMAÇÕES UMA VEZ POR FRAME
    # ========================================================
    # As classes desenham apenas o sprite ativo. A atualização
    # é feita aqui, após a lógica de movimento, ataque e dano.

    noiva.atualizar_animacao()

    # ALTERAÇÃO: animação independente da Sogra Boss.
    if fase_atual == 1:
        sogra_boss.atualizar_animacao()

    if fase_atual == 1:
        # ALTERAÇÃO: atualização visual uniforme para todos os inimigos.
        for inimigo in inimigos:
            inimigo.atualizar_animacao()

    # ALTERAÇÃO: atualiza o sprite do Amigo apenas depois de aparecer na tela.
    if fase_atual == 2:
        for amigo_f2 in amigos_f2:
            if amigo_f2.entrada_visivel and not amigo_f2.removido:
                amigo_f2.atualizar_animacao()

    # ALTERAÇÃO: animação independente das Convidadas da Fase 2.
    if fase_atual == 2:
        for convidada_f2 in convidadas_f2:
            if convidada_f2.entrada_visivel and convidada_f2.estado != "removida":
                convidada_f2.atualizar_animacao()

    # ALTERAÇÃO: animação independente da Dama, somente na última tela da Fase 2.
    if fase_atual == 2 and arena_dama_ativa:
        # ALTERAÇÃO: a proximidade dispara uma única contagem de 30 segundos.
        dama_boss.atualizar(dt, noiva)


    # ========================================================
    # POSICIONAMENTO DAS CAMADAS
    # ========================================================

    # ALTERAÇÃO: mantemos o fator original, sem trocar por ParallaxSystem:
    # as imagens são partes diferentes do cenário, não um fundo repetível.
    fator_parallax = 0.35

    if fase_atual == 1:

        # PARALLAX
        parallax_1.set_position(
            INICIO_PARTE_1 - camera_x * fator_parallax,
            0
        )

        parallax_2.set_position(
            INICIO_PARTE_2 - camera_x * fator_parallax,
            0
        )

        parallax_3.set_position(
            INICIO_PARTE_3 - camera_x * fator_parallax,
            0
        )

        parallax_4.set_position(
            INICIO_PARTE_4 - camera_x * fator_parallax,
            0
        )

        # CENA PRINCIPAL
        cenario_1.set_position(
            INICIO_PARTE_1 - camera_x,
            0
        )

        cenario_2.set_position(
            INICIO_PARTE_2 - camera_x,
            0
        )

        cenario_3.set_position(
            INICIO_PARTE_3 - camera_x,
            0
        )

        cenario_4.set_position(
            INICIO_PARTE_4 - camera_x,
            0
        )

        # OVERLAY
        overlay_1.set_position(
            INICIO_PARTE_1 - camera_x,
            0
        )

        overlay_2.set_position(
            INICIO_PARTE_2 - camera_x,
            0
        )

        overlay_3.set_position(
            INICIO_PARTE_3 - camera_x,
            0
        )

        overlay_4.set_position(
            INICIO_PARTE_4 - camera_x,
            0
        )

    else:

        # PARALLAX
        parallax_f2_1.set_position(
            INICIO_F2_1 - camera_x * fator_parallax,
            0
        )

        parallax_f2_2.set_position(
            INICIO_F2_2 - camera_x * fator_parallax,
            0
        )

        parallax_f2_3.set_position(
            INICIO_F2_3 - camera_x * fator_parallax,
            0
        )

        parallax_f2_final.set_position(
            INICIO_F2_FINAL - camera_x * fator_parallax,
            0
        )

        # CENA PRINCIPAL
        cenario_f2_1.set_position(
            INICIO_F2_1 - camera_x,
            0
        )

        cenario_f2_2.set_position(
            INICIO_F2_2 - camera_x,
            0
        )

        cenario_f2_3.set_position(
            INICIO_F2_3 - camera_x,
            0
        )

        cenario_f2_final.set_position(
            INICIO_F2_FINAL - camera_x,
            0
        )

        # OVERLAY
        overlay_f2_1.set_position(
            INICIO_F2_1 - camera_x,
            0
        )

        overlay_f2_2.set_position(
            INICIO_F2_2 - camera_x,
            0
        )

        overlay_f2_3.set_position(
            INICIO_F2_3 - camera_x,
            0
        )

        overlay_f2_final.set_position(
            INICIO_F2_FINAL - camera_x,
            0
        )


    # ========================================================
    # DESENHO DOS FUNDOS
    # ========================================================

    if fase_atual == 1:

        parallax_1.draw()
        parallax_2.draw()
        parallax_3.draw()
        parallax_4.draw()

        cenario_1.draw()
        cenario_2.draw()
        cenario_3.draw()
        cenario_4.draw()

    else:

        parallax_f2_1.draw()
        parallax_f2_2.draw()
        parallax_f2_3.draw()
        parallax_f2_final.draw()

        cenario_f2_1.draw()
        cenario_f2_2.draw()
        cenario_f2_3.draw()
        cenario_f2_final.draw()


    # ========================================================
    # GARRAFAS
    # ========================================================

    if fase_atual == 1:

        for penetra in penetras:
            penetra.desenhar_garrafas()

    # ALTERAÇÃO: projéteis do Amigo (herda o combate do Penetra provisoriamente).
    if fase_atual == 2:  # ALTERAÇÃO: Amigos também ativos na arena final da Dama
        for amigo_f2 in amigos_f2:
            if amigo_f2.entrada_liberada:
                amigo_f2.desenhar_garrafas()


    # ========================================================
    # ALTERAÇÃO: DESENHO DOS PERSONAGENS POR PROFUNDIDADE (Y)
    # ========================================================

    # Personagens mais altos na tela (menor Y) são desenhados primeiro.
    # Personagens mais baixos na tela (maior Y) são desenhados depois,
    # ficando visualmente à frente dos demais.
    # A ordenação é apenas visual: não altera a IA nem as colisões.
    personagens_para_desenhar = [noiva]

    if fase_atual == 1:
        # ALTERAÇÃO: inclui todos os inimigos, sem distinguir tipos.
        personagens_para_desenhar.extend(inimigos)

    # ALTERAÇÃO: os dois bancos são APENAS DECORATIVOS (sem colisão).
    # O eixo de profundidade usa a base visual do objeto (pé do banco).
    # A Dama permanece sentada e é desenhada após o banco que a sustenta.
    if fase_atual == 2:
        if camera_x + janela.width >= INICIO_F2_FINAL:
            elementos_f2 = [
                (banco_superior.profundidade_y, 0, banco_superior.desenhar),
                (dama_boss.profundidade_y, 1, dama_boss.desenhar),
                (banco_inferior.profundidade_y, 0, banco_inferior.desenhar),
                (noiva.y + noiva.altura, 2, noiva.desenhar),
            ]
            # ALTERAÇÃO: o Amigo usa a mesma ordenação de profundidade, sem duplicar a Noiva.
            # ALTERAÇÃO: desenha também a dupla nova durante o combate da Dama.
            for amigo_f2 in amigos_f2:
                if amigo_f2.entrada_visivel and not amigo_f2.removido:
                    elementos_f2.append((amigo_f2.y + amigo_f2.altura, 2, amigo_f2.desenhar))
            # ALTERAÇÃO: quatro Convidadas da Fase 2 na mesma ordenação de profundidade.
            for convidada_f2 in convidadas_f2:
                if convidada_f2.entrada_visivel and convidada_f2.estado != "removida":
                    elementos_f2.append((convidada_f2.y + convidada_f2.andando_direita.height,
                                         2, convidada_f2.desenhar))
            for _, _, desenhar_elemento in sorted(elementos_f2, key=lambda item: (item[0], item[1])):
                desenhar_elemento()
        else:
            # ALTERAÇÃO: durante as três primeiras telas, desenhar Amigo e Noiva por profundidade.
            elementos_f2 = [(noiva.y + noiva.altura, noiva.desenhar)]
            for amigo_f2 in amigos_f2:
                if amigo_f2.entrada_visivel and not amigo_f2.removido:
                    elementos_f2.append((amigo_f2.y + amigo_f2.altura, amigo_f2.desenhar))
            # ALTERAÇÃO: Convidadas da terceira tela são desenhadas conforme o Y.
            for convidada_f2 in convidadas_f2:
                if convidada_f2.entrada_visivel and convidada_f2.estado != "removida":
                    elementos_f2.append((convidada_f2.y + convidada_f2.andando_direita.height,
                                         convidada_f2.desenhar))
            for _, desenhar_elemento in sorted(elementos_f2, key=lambda item: item[0]):
                desenhar_elemento()
    else:
        personagens_para_desenhar.sort(key=lambda personagem: personagem.y)
        for personagem in personagens_para_desenhar:
            personagem.desenhar()

    # ALTERAÇÃO: Sogra Boss flutua acima dos personagens comuns.
    # Desenha antes dos overlays originais para respeitar o cenário.
    if fase_atual == 1:
        sogra_boss.desenhar()


    # ========================================================
    # ALTERAÇÃO: NOIVO NA FASE 2, EM COORDENADAS DO MUNDO
    # ========================================================
    if fase_atual == 2 and cena_final_estado in ('entrada_noivo', 'pedido', 'pose'):
        if cena_final_estado == 'entrada_noivo':
            sprite_noivo = noivo_andando
            quadro_noivo = int((cena_final_tempo % DURACAO_NOIVO_ANDANDO)
                               / DURACAO_NOIVO_ANDANDO * 4)
        else:
            sprite_noivo = noivo_pedido
            # ALTERAÇÃO: pedido ocorre UMA vez; último quadro fica fixo durante 5s.
            quadro_noivo = min(15, int(cena_final_tempo / DURACAO_NOIVO_PEDIDO * 16)) \
                if cena_final_estado == 'pedido' else 15
        sprite_noivo.set_curr_frame(quadro_noivo)
        sprite_noivo.set_position(noivo_cena_x, noivo_cena_pe_y - sprite_noivo.height)
        sprite_noivo.draw()

    # ========================================================
    # OVERLAYS - SEMPRE NA FRENTE DA NOIVA
    # ========================================================

    if fase_atual == 1:

        overlay_1.draw()
        overlay_2.draw()
        overlay_3.draw()
        overlay_4.draw()

    else:

        overlay_f2_1.draw()
        overlay_f2_2.draw()
        overlay_f2_3.draw()
        overlay_f2_final.draw()


    # ALTERAÇÃO: desenha as bolas DEPOIS dos cenários, da Boss e dos overlays.
    # Assim o projétil não fica escondido atrás de outra camada visual.
    # A atualização/movimento continuam ocorrendo antes, uma vez por frame.
    if fase_atual == 1:
        sogra_boss.desenhar_bolas_fogo()


    # ALTERAÇÃO: efeitos da Dama são desenhados sobre o cenário da Fase 2.
    if fase_atual == 2 and arena_dama_ativa:
        dama_boss.desenhar_efeitos(janela.screen, camera_x)
        aplicador_f2.desenhar()

    # ========================================================
    # ALTERAÇÃO: APLICADOR NO CHÃO E PROJÉTEIS (EM FRENTE AOS OVERLAYS)
    # ========================================================
    if fase_atual == 1:
        aplicador.desenhar()

    # ========================================================
    # ALTERAÇÃO: HUD FIXO - FPS / PONTUAÇÃO / VIDAS
    # ========================================================
    # draw_text() usa coordenadas de tela e não acompanha a câmera.
    # Mantemos o texto por último para não ficar coberto pelos overlays.
    janela.draw_text(f"FPS: {int(janela.get_fps())}", 15, 10,
                     tamanho=24, cor=(255, 255, 255))
    janela.draw_text(f"PONTOS: {pontuacao}", 15, 40,
                     tamanho=24, cor=(255, 255, 255))
    janela.draw_text(f"VIDAS: {noiva.vidas}", 15, 70,
                     tamanho=24, cor=(255, 255, 255))
    # ALTERAÇÃO: acompanhamento opcional do despertar; o relógio só começa
    # no primeiro encontro e é congelado durante o menu de pausa.
    if (fase_atual == 2 and arena_dama_ativa and MOSTRAR_CONTAGEM_DAMA
            and dama_boss.estado in ('sentada', 'aguardando')):
        if dama_boss.despertar_iniciado:
            restante = max(0.0, TEMPO_DESPERTAR - dama_boss.tempo_despertar)
            janela.draw_text(f'DAMA DESPERTA EM: {restante:.1f}s', 15, 105,
                             tamanho=24, cor=(255, 220, 145))

    if noiva.eliminada:
        janela.draw_text("FIM DE JOGO", janela.width / 2 - 125,
                         janela.height / 2 - 30, tamanho=46,
                         cor=(255, 100, 100))

    # ALTERAÇÃO: salvar frame completo ANTES do update() limpar o buffer virtual.
    ultima_tela_jogo = janela.screen.copy()
    janela.update()
