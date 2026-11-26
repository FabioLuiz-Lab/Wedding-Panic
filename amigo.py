"""Amigo — inimigo da Fase 2 / Power PPlay 2.1.

# ALTERAÇÃO: sprite próprio. Andando, upper e queda = 9 quadros; chute-spin = 8 quadros;
# voadora = 16 quadros; dano = 1 quadro.
# 3 hits provocam queda; após a segunda queda é removido.
# Mantém as chamadas usadas pelo main.py e espera entrar totalmente na câmera.
"""
import math
# ALTERAÇÃO: removido import math duplicado; sem efeito sobre a lógica.

from PPlay.sprite import Sprite
from PPlay.gameimage import GameImage
from pathlib import Path
import pygame

# ALTERAÇÃO: compatibiliza spritesheets cujas dimensões não são múltiplas dos quadros.
def _sprite_amigo_novo(arquivo, quadros, duracao_ms, fallback):
    origem = Path(arquivo)
    if not origem.is_file():
        return fallback
    imagem = GameImage(str(origem)).image
    largura, altura = imagem.get_size()
    if largura % quadros:
        cache = Path("assets/.cache_amigo")
        cache.mkdir(parents=True, exist_ok=True)
        quadro_w = round(largura / quadros)
        destino = cache / f"{origem.stem}_{quadros}f_{quadro_w}x{altura}.png"
        if not destino.exists() or destino.stat().st_mtime < origem.stat().st_mtime:
            tira = pygame.Surface((quadro_w * quadros, altura), pygame.SRCALPHA)
            for i in range(quadros):
                x0 = round(i * largura / quadros)
                x1 = round((i + 1) * largura / quadros)
                quadro = imagem.subsurface((x0, 0, x1-x0, altura))
                tira.blit(pygame.transform.smoothscale(quadro, (quadro_w, altura)), (i*quadro_w, 0))
            pygame.image.save(tira, str(destino))
        origem = destino
    sprite = Sprite(str(origem), quadros)
    sprite.set_total_duration(duracao_ms)
    sprite.set_loop(False)
    return sprite


# ALTERAÇÃO: normaliza os 9 quadros de queda (2048px não divide por 9).
# IMPORTANTE: queda-esquerda.png foi desenhada ao contrário: deitado -> em pé.
# Inverte essa tira na cópia em cache, para AMBOS os sentidos serem em pé -> deitado.
def _normalizar_queda_amigo(arquivo, inverter=False):
    origem = Path(arquivo)
    cache = Path("assets/.cache_amigo")
    cache.mkdir(parents=True, exist_ok=True)
    imagem = GameImage(str(origem)).image
    largura, altura = imagem.get_size()
    quadros = 9
    largura_quadro = round(largura / quadros)
    destino = cache / f"{origem.stem}_queda_ordenada_{'inversa' if inverter else 'normal'}_{largura_quadro}x{altura}.png"
    if not destino.exists() or destino.stat().st_mtime < origem.stat().st_mtime:
        tira = pygame.Surface((largura_quadro * quadros, altura), pygame.SRCALPHA)
        for i in range(quadros):
            indice = quadros - 1 - i if inverter else i
            x0 = round(indice * largura / quadros)
            x1 = round((indice + 1) * largura / quadros)
            quadro = imagem.subsurface((x0, 0, x1 - x0, altura))
            if quadro.get_width() != largura_quadro:
                quadro = pygame.transform.smoothscale(quadro, (largura_quadro, altura))
            tira.blit(quadro, (i * largura_quadro, 0))
        pygame.image.save(tira, str(destino))
    return str(destino)


# ALTERAÇÃO: cria um sprite de levantamento SOMENTE com os 3 quadros finais
# da queda em ordem inversa (8, 7, 6). Aplica-se às duas direções.
def _criar_levantamento_curto(arquivo, quadros=(8, 7, 6)):
    origem = Path(arquivo)
    cache = Path("assets/.cache_amigo")
    cache.mkdir(parents=True, exist_ok=True)
    destino = cache / f"{origem.stem}_levantando_3f.png"
    if not destino.exists() or destino.stat().st_mtime < origem.stat().st_mtime:
        imagem = GameImage(str(origem)).image
        largura, altura = imagem.get_size()
        largura_quadro = largura // 9
        tira = pygame.Surface((largura_quadro * 3, altura), pygame.SRCALPHA)
        for posicao, indice in enumerate(quadros):
            x0 = round(indice * largura / 9)
            x1 = round((indice + 1) * largura / 9)
            quadro = imagem.subsurface((x0, 0, x1 - x0, altura))
            if quadro.get_width() != largura_quadro:
                quadro = pygame.transform.smoothscale(quadro, (largura_quadro, altura))
            tira.blit(quadro, (posicao * largura_quadro, 0))
        pygame.image.save(tira, str(destino))
    sprite = Sprite(str(destino), 3)
    sprite.set_loop(False)
    return sprite


# ALTERAÇÃO: redimensiona cada quadro do upper sem mexer nas imagens originais.
def _sprite_upper_escalado(arquivo, quadros, escala):
    origem = Path(arquivo)
    if escala == 1.0:
        return Sprite(str(origem), quadros)
    imagem = GameImage(str(origem)).image
    largura, altura = imagem.get_size()
    if largura % quadros:
        raise ValueError(f'{origem.name}: largura não divisível por {quadros} quadros')
    largura_quadro = largura // quadros
    novo_w = max(1, round(largura_quadro * escala))
    novo_h = max(1, round(altura * escala))
    pasta_cache = Path('assets/.cache_amigo')
    pasta_cache.mkdir(parents=True, exist_ok=True)
    destino = pasta_cache / f'{origem.stem}_upper_{quadros}f_{novo_w}x{novo_h}.png'
    if not destino.exists() or destino.stat().st_mtime < origem.stat().st_mtime:
        tira = pygame.Surface((novo_w * quadros, novo_h), pygame.SRCALPHA)
        for i in range(quadros):
            quadro = imagem.subsurface((i * largura_quadro, 0, largura_quadro, altura))
            tira.blit(pygame.transform.smoothscale(quadro, (novo_w, novo_h)), (i * novo_w, 0))
        pygame.image.save(tira, str(destino))
    return Sprite(str(destino), quadros)


# ============================================================
# CLASSE AMIGO
# ============================================================

class Amigo:

    # --------------------------------------------------------
    # TEMPOS
    # --------------------------------------------------------

    TEMPO_ANDANDO = 1200
    # ALTERAÇÃO: animação idle própria, 16 frames em 3 segundos.
    TEMPO_IDLE = 3000
    TEMPO_ATAQUE = 2500
    TEMPO_TAPA = 500

    # Último frame do tapa permanece visível por 1 segundo.
    TEMPO_TAPA_FINAL = 1.0

    # Precisa ficar próximo e alinhado por 0,5 s.
    TEMPO_ALINHADO_TAPA = 0.5

    TEMPO_DANO = 180  # ALTERAÇÃO: reação curta para permitir novos golpes válidos
    TEMPO_QUEDA = 1400
    GOLPES_POR_QUEDA = 3  # ALTERAÇÃO: 3 hits por queda, como os demais inimigos  # ALTERAÇÃO: padronizado com a Convidada
    TEMPO_CAIDO = 2.0
    TEMPO_CORPO_APOS_MORTE = 2.0  # ALTERAÇÃO: após segunda queda, permanece no chão e desaparece
    # ALTERAÇÃO: primeira queda levanta; a segunda elimina.
    QUEDAS_PARA_ELIMINAR = 2  # ALTERAÇÃO: segunda queda elimina
    TEMPO_LEVANTAR = 0.45  # ALTERAÇÃO: somente 3 últimos frames da queda, em reverso

    # ALTERAÇÃO: combos fechados; a esquiva da Noiva não interrompe a sequência.
    FRAMES_SOCOS = 9              # nove poses visuais enviadas
    FRAMES_CHUTE = 9              # ALTERAÇÃO: novo spritesheet com 9 quadros (2048px, normalizado em cache)
    TEMPO_SOCO_COMBO_MS = 640     # dois socos de abertura
    TEMPO_CHUTE_COMBO_MS = 640    # dois chutes de abertura
    TEMPO_UPPER_FINAL_MS = 880    # finalizador mais demorado
    TEMPO_SPIN_FINAL_MS = 930     # finalizador mais demorado
    AVISO_COMBO_S = 0.35
    DISTANCIA_COMBO_INICIAR = 210
    DISTANCIA_HIT_SOCO = 195
    DISTANCIA_HIT_CHUTE = 215
    TOLERANCIA_COMBO_Y = 115  # faixa de preparação; não é a hitbox do chute
    TOLERANCIA_IMPACTO_SOCO_Y = 65   # ALTERAÇÃO: impactos por linha dos pés
    TOLERANCIA_IMPACTO_CHUTE_Y = 42  # ALTERAÇÃO: chute só atinge com alinhamento em Y próximo
    ESCALA_UPPER = 1.24             # ALTERAÇÃO: aumento visual exclusivo do upper
    TEMPO_AVISO_VOADORA = 0.45
    DISTANCIA_VOADORA_MIN = 270
    DISTANCIA_VOADORA_MAX = 700
    DISTANCIA_MAX_VOADORA = 630
    VELOCIDADE_VOADORA_X = 540
    INTERVALO_VOADORA = 5.5
    ATIVAR_DEBUG_ATAQUE = False

    INTERVALO_ATAQUE = 0.90  # ALTERAÇÃO: recuperação após atacar, sem esperar 3 s

    # ALTERAÇÃO: rodízio de golpes e preparação para dar chance de reação.
    ORDEM_GOLPES = ("tapa", "chute_spin")  # ALTERAÇÃO: só upper e spin; voadora tem gatilho próprio
    TEMPO_PREPARACAO_GOLPE = 0.38  # segundos alinhado antes de qualquer ataque
    TEMPO_CHUTE_SPIN = 640        # ALTERAÇÃO: 8 quadros; duração proporcional à anterior
    FRAMES_CHUTE_SPIN = 8         # ALTERAÇÃO: spritesheet confirmada (1880 / 8 = 235 px)
    FRAME_IMPACTO_SPIN = 5        # ALTERAÇÃO: impacto no meio do movimento, quadro 5 de 8
    DISTANCIA_CHUTE_SPIN = 185

    # ALTERAÇÃO: voadora avança e sobe em arco, sem perseguir a Noiva durante o golpe.
    TEMPO_VOADORA = 1100         # ms; animação de 16 quadros
    VELOCIDADE_VOADORA_X = 420  # pixels/s no sentido definido ao iniciar
    DISTANCIA_MAX_VOADORA = 420 # pixels máximos de avanço
    ALTURA_SALTO_VOADORA = 75   # px, somente visual; preserva colisão no piso
    INICIO_HIT_VOADORA = 0.22   # fração inicial da janela de acerto da voadora
    FIM_HIT_VOADORA = 0.52      # golpe acontece no trecho central do spritesheet
    FRACAO_MOVIMENTO_VOADORA = 0.52  # só avança até o meio útil da animação
    LEVANTAR_QUADROS = (8, 7, 6)     # 3 quadros finais da queda, em reverso
    FRAMES_VOADORA_VISIVEIS = 8     # ALTERAÇÃO: só a primeira metade (0 a 7) em AMBAS as direções

    # ALTERAÇÃO: espera de entrada configurável (s) e orientação inicial.
    TEMPO_IDLE_INICIAL = 2.0
    DIRECAO_INICIAL = "direita"

    # --------------------------------------------------------
    # MOVIMENTO / IA
    # --------------------------------------------------------

    VELOCIDADE = 24  # ALTERAÇÃO: aproximação horizontal mais lenta, com 4 Amigos e 4 Convidadas
    VELOCIDADE_ALINHAMENTO = 35  # ALTERAÇÃO: alinhamento Y mais lento; ataques continuam iguais

    DISTANCIA_ATAQUE = 320  # ALTERAÇÃO: alcance de início da voadora
    DISTANCIA_TAPA = 175  # ALTERAÇÃO: upper próximo

    DISTANCIA_VOADORA_HIT = 140  # ALTERAÇÃO: alcance de impacto, diferente do gatilho
    TOLERANCIA_ALINHAMENTO_Y = 80  # ALTERAÇÃO: margem de preparação pelos pés
    TOLERANCIA_PREPARACAO_Y = 115  # ALTERAÇÃO: inicia golpe mesmo antes de alinhamento perfeito
    TOLERANCIA_IMPACTO_Y = 100      # ALTERAÇÃO: faixa efetiva do golpe, ajustável
    DISTANCIA_PARADA = 105

    # ALTERAÇÃO: zigue-zague na aproximação; diminui perto do alvo para permitir golpes.
    # ALTERAÇÃO: envelopes reais de combate, distintos da distância visual dos PNGs.
    DISTANCIA_PREPARAR_CORPO_A_CORPO = 205  # upper / chute, inclui sobreposição dos corpos
    DISTANCIA_VOADORA_MIN = 230            # ataque de maior alcance, separado do rodízio
    DISTANCIA_VOADORA_MAX = 480
    INTERVALO_VOADORA = 6.0                # recarga independente
    TEMPO_AVISO_VOADORA = 0.42
    TEMPO_RECUPERACAO_APOS_GOLPE = 0.75
    ATIVAR_DEBUG_ATAQUE = False           # imprime estados para diagnóstico

    AMPLITUDE_ZIGUEZAGUE_Y = 70
    PERIODO_ZIGUEZAGUE = 2.8       # segundos por oscilação completa
    DISTANCIA_REDUZ_ZIGUEZAGUE = 400

    # ALTERAÇÃO: flanqueamento com pontos de passagem, sem teleportes nem outra engine.
    ATIVAR_FLANQUEAMENTO = True
    INTERVALO_FLANQUEAMENTO = 8.0  # segundos entre tentativas
    DISTANCIA_INICIAR_FLANQUEAMENTO = 390
    DISTANCIA_PASSAGEM_Y = 115    # diferença segura em relação aos pés da Noiva
    DISTANCIA_ATRAS_NOIVA = 155
    TEMPO_MAX_FLANQUEAMENTO = 7.0
    TOLERANCIA_WAYPOINT = 26
    MULTIPLICADOR_VELOCIDADE_FLANCO = 1.30  # ALTERAÇÃO: flanqueamento mais lento

    # --------------------------------------------------------
    # CORPO / COLISÃO
    # --------------------------------------------------------

    CENTRO_CORPO_X_DIREITA = 150
    CENTRO_CORPO_X_ESQUERDA = 125
    CENTRO_CORPO_Y = 150

    LARGURA_CORPO = 80

    AFASTAMENTO_QUEDA = 60

    # --------------------------------------------------------
    # GARRAFA
    # --------------------------------------------------------

    QUANTIDADE_FRAMES_ATAQUE = 16  # ALTERAÇÃO: spritesheet voadora
    FRAME_DISPARO = 8

    VELOCIDADE_GARRAFA = 450
    VELOCIDADE_GIRO_GARRAFA = 420

    ESCALA_GARRAFA = 1.0

    OFFSET_GARRAFA_X_DIREITA = 1.2
    OFFSET_GARRAFA_X_ESQUERDA = -0.2
    OFFSET_GARRAFA_Y = 0.10


    def __init__(self, x, y, direcao_inicial=None, tempo_idle_inicial=None):

        self.x = x
        self.y = y

        # ALTERAÇÃO: direção e espera inicial por instância.
        self.direcao = direcao_inicial if direcao_inicial in ("direita", "esquerda") else self.DIRECAO_INICIAL
        self.tempo_idle_configurado = (
            max(0.0, float(tempo_idle_inicial)) if tempo_idle_inicial is not None
            else self.TEMPO_IDLE_INICIAL
        )
        self.entrada_liberada = False
        self.entrada_visivel = False
        self.tempo_idle_inicial = 0.0

        # ====================================================
        # SPRITES - ANDANDO
        # ====================================================

        self.andando_direita = Sprite(
            "assets/personagens/amigo/amigo-01-andando-direita.png",
            9
        )

        self.andando_esquerda = Sprite(
            "assets/personagens/amigo/amigo-01-andando-esquerda.png",
            9
        )

        # ALTERAÇÃO: dimensões de referência usadas pelo main.py para ordenar
        # o Amigo pela profundidade (posição dos pés: y + altura).
        # Mantidas fixas conforme a animação de caminhada, que também define
        # os limites de movimento, evitando oscilações entre spritesheets.
        self.largura = self.andando_direita.width
        self.altura = self.andando_direita.height

        # ====================================================
        # ALTERAÇÃO: SPRITES - IDLE (16 FRAMES / 3 SEGUNDOS)
        # ====================================================

        self.idle_direita = Sprite(
            "assets/personagens/amigo/amigo-01-andando-direita.png",
            9
        )
        self.idle_esquerda = Sprite(
            "assets/personagens/amigo/amigo-01-andando-esquerda.png",
            9
        )
        self.idle_direita.set_total_duration(self.TEMPO_IDLE)
        self.idle_esquerda.set_total_duration(self.TEMPO_IDLE)

        self.andando_direita.set_total_duration(self.TEMPO_ANDANDO)
        self.andando_esquerda.set_total_duration(self.TEMPO_ANDANDO)

        # ====================================================
        # SPRITES - ATAQUE COM GARRAFA
        # ====================================================

        self.ataque_direita = Sprite(
            "assets/personagens/amigo/amigo-01-voadora-direita.png",
            16
        )

        self.ataque_esquerda = Sprite(
            "assets/personagens/amigo/amigo-01-voadora-esquerda.png",
            16
        )

        self.ataque_direita.set_total_duration(self.TEMPO_ATAQUE)
        self.ataque_esquerda.set_total_duration(self.TEMPO_ATAQUE)

        self.ataque_direita.set_loop(False)
        self.ataque_esquerda.set_loop(False)

        # ====================================================
        # SPRITES - TAPA
        # ====================================================

        # ALTERAÇÃO: escala exclusiva do upper (cada frame, sem distorcer).
        self.tapa_direita = _sprite_upper_escalado(
            "assets/personagens/amigo/amigo-01-upper-direita.png", 9, self.ESCALA_UPPER)
        self.tapa_esquerda = _sprite_upper_escalado(
            "assets/personagens/amigo/amigo-01-upper-esquerda.png", 9, self.ESCALA_UPPER)

        self.tapa_direita.set_total_duration(self.TEMPO_TAPA)
        self.tapa_esquerda.set_total_duration(self.TEMPO_TAPA)

        self.tapa_direita.set_loop(False)
        self.tapa_esquerda.set_loop(False)

        # ====================================================
        # ALTERAÇÃO: CHUTE SPIN (9 quadros), animação disponível para ataque futuro.
        # ====================================================
        self.chute_spin_direita = Sprite(
            "assets/personagens/amigo/amigo-01-chute-spin-direita.png", self.FRAMES_CHUTE_SPIN)
        self.chute_spin_esquerda = Sprite(
            "assets/personagens/amigo/amigo-01-chute-spin-esquerda.png", self.FRAMES_CHUTE_SPIN)
        self.chute_spin_direita.set_total_duration(self.TEMPO_CHUTE_SPIN)
        self.chute_spin_esquerda.set_total_duration(self.TEMPO_CHUTE_SPIN)
        self.chute_spin_direita.set_loop(False)
        self.chute_spin_esquerda.set_loop(False)

        # ====================================================
        # ALTERAÇÃO: spritesheets dos combos; cópias de cache sem tocar nos PNGs.
        # ALTERAÇÃO: Socos: 9 quadros; chutes: 9 quadros (novos spritesheets).
        # ====================================================
        self.socos_direita = _sprite_amigo_novo(
            "assets/personagens/amigo/amigo-socos-direita.png", self.FRAMES_SOCOS,
            self.TEMPO_SOCO_COMBO_MS, self.tapa_direita)
        self.socos_esquerda = _sprite_amigo_novo(
            "assets/personagens/amigo/amigo-socos-esquerda.png", self.FRAMES_SOCOS,
            self.TEMPO_SOCO_COMBO_MS, self.tapa_esquerda)
        self.chute_combo_direita = _sprite_amigo_novo(
            "assets/personagens/amigo/amigo-chute-direita.png", self.FRAMES_CHUTE,
            self.TEMPO_CHUTE_COMBO_MS, self.chute_spin_direita)
        self.chute_combo_esquerda = _sprite_amigo_novo(
            "assets/personagens/amigo/amigo-chute-esquerda.png", self.FRAMES_CHUTE,
            self.TEMPO_CHUTE_COMBO_MS, self.chute_spin_esquerda)

        # ====================================================
        # SPRITES - DANO
        # ====================================================

        self.dano_direita = Sprite(
            "assets/personagens/amigo/amigo-01-dano-direita.png",
            1
        )

        self.dano_esquerda = Sprite(
            "assets/personagens/amigo/amigo-01-dano-esquerda.png",
            1
        )

        # ====================================================
        # SPRITES - QUEDA
        # ====================================================

        # ALTERAÇÃO: direita já vai de pé para deitado; esquerda vem invertida.
        # As cópias normalizadas mantêm o último quadro SEMPRE deitado.
        self.arquivo_queda_direita = _normalizar_queda_amigo(
            "assets/personagens/amigo/amigo-01-queda-direita.png")
        self.arquivo_queda_esquerda = _normalizar_queda_amigo(
            "assets/personagens/amigo/amigo-01-queda-esquerda.png", inverter=True)
        self.queda_direita = Sprite(self.arquivo_queda_direita, 9)
        self.queda_esquerda = Sprite(self.arquivo_queda_esquerda, 9)

        self.queda_direita.set_total_duration(self.TEMPO_QUEDA)
        self.queda_esquerda.set_total_duration(self.TEMPO_QUEDA)

        self.queda_direita.set_loop(False)
        self.queda_esquerda.set_loop(False)
        # ALTERAÇÃO: sprites separados com APENAS três frames, um para cada direção.
        self.levantar_direita = _criar_levantamento_curto(
            self.arquivo_queda_direita, self.LEVANTAR_QUADROS)
        self.levantar_esquerda = _criar_levantamento_curto(
            self.arquivo_queda_esquerda, self.LEVANTAR_QUADROS)

        # ====================================================
        # ATAQUE
        # ====================================================

        self.atacando = False
        self.tipo_ataque = "garrafa"
        # ALTERAÇÃO: cada Amigo alterna combo de socos e combo de chutes.
        self.proximo_combo = 0
        self.combo_tipo = None
        self.combo_etapa = 0
        self.combo_tempo_etapa = 0.0
        self.combo_dano_registrado = False
        self.combo_sprite = None
        self.combo_duracao_etapa = 0.0


        self.tempo_intervalo = 0
        self.tempo_ataque = 0
        self.tempo_alinhado_tapa = 0
        # ALTERAÇÃO: preparação independente e índice persistente entre ataques.
        self.tempo_preparacao_golpe = 0.0
        self.proximo_golpe_indice = 0
        # ALTERAÇÃO: recarga aérea separada, sem bloquear upper e chute spin.
        self.tempo_recarga_voadora = self.INTERVALO_VOADORA  # ALTERAÇÃO: pronta na primeira oportunidade
        self.tipo_preparacao = None
        self.tempo_preparacao_golpe = 0.0
        self.tempo_recuperacao = 0.0
        self.altura_voadora_visual = 0.0
        self.inicio_voadora_x = self.x
        self.sinal_voadora = 1
        # ALTERAÇÃO: IA com duas etapas de contorno; relógios só avançam após entrada.
        self.tempo_ziguezague = 0.0
        self.tempo_desde_flanco = 0.0
        self.tempo_flanco = 0.0
        self.estado_flanco = None  # None, 'desviar_y', 'passar_x', 'voltar_y'
        self.lado_desvio = 1
        self.alvo_passagem_y = self.y + self.altura

        self.garrafa_disparada = False
        self.tapa_registrado = False

        self.duracao_ataque = self.TEMPO_VOADORA / 1000
        self.duracao_chute_spin = self.TEMPO_CHUTE_SPIN / 1000
        self.duracao_tapa = self.TEMPO_TAPA / 1000

        self.momento_frame_final_tapa = self.duracao_tapa / 2  # ALTERAÇÃO: dano na metade do upper

        self.duracao_total_tapa = (
            self.momento_frame_final_tapa
            + self.TEMPO_TAPA_FINAL
        )

        # ====================================================
        # DANO / QUEDA
        # ====================================================

        self.golpes = 0

        self.recebendo_dano = False
        self.tempo_dano = 0

        self.caindo = False
        self.tempo_queda = 0

        self.derrotado = False
        self.tempo_caido = 0
        # ALTERAÇÃO: estado de levantamento e eliminação definitiva.
        self.quedas = 0
        self.levantando = False
        self.tempo_levantar = 0.0
        self.eliminado = False
        self.removido = False
        self.tempo_corpo_morto = 0.0  # ALTERAÇÃO: separa morte definitiva da primeira queda
        self.direcao_queda = self.direcao  # ALTERAÇÃO: direção fica fixa até terminar a queda

        self.duracao_dano = self.TEMPO_DANO / 1000
        self.duracao_queda = self.TEMPO_QUEDA / 1000

        # Evita que um mesmo ataque da noiva cause dano
        # várias vezes neste Penetra.
        self.ultimo_id_ataque_noiva = -1

        # Cada penetra possui seus próprios projéteis.
        self.garrafas = []


    # ========================================================
    # ALTERAÇÃO: AGUARDA A ENTRADA COMPLETA NA TELA
    # ========================================================

    def atualizar_entrada(self, dt, camera_x, largura_tela, noiva=None, distancia_ativacao=None):
        # ALTERAÇÃO: Amigos da arena só liberam IA se INTEIROS na câmera
        # E se a Noiva estiver próxima. Os Amigos anteriores mantêm sua regra.
        if self.entrada_liberada:
            return

        largura = self.andando_direita.width
        visivel = self.x >= camera_x and self.x + largura <= camera_x + largura_tela
        if not visivel:
            self.entrada_visivel = False
            self.tempo_idle_inicial = 0.0
            return

        self.entrada_visivel = True  # mantém idle visível enquanto espera
        # ALTERAÇÃO: conta o tempo desde que apareceu INTEIRO, mesmo que
        # a Noiva ainda esteja longe. A IA só libera com tempo E proximidade.
        self.tempo_idle_inicial += dt
        if self.tempo_idle_inicial < self.tempo_idle_configurado:
            return
        if (noiva is not None and distancia_ativacao is not None
                and abs(noiva.centro_x - self.centro_x) > distancia_ativacao):
            return
        self.entrada_liberada = True

    # ========================================================
    # CENTROS DO CORPO
    # ========================================================

    @property
    def centro_x(self):

        if self.direcao == "direita":
            return self.x + self.CENTRO_CORPO_X_DIREITA

        return self.x + self.CENTRO_CORPO_X_ESQUERDA


    @property
    def centro_y(self):
        return self.y + self.CENTRO_CORPO_Y


    # ========================================================
    # ALTERAÇÃO: posição dos pés usada em movimento e hitboxes de combate.
    # A Noiva pode saltar, então no impacto usamos o deslocamento vertical
    # da sua hitbox aérea, preservando a possibilidade de escapar de golpes.
    # ========================================================
    @property
    def pes_y(self):
        return self.y + self.altura

    @staticmethod
    def _pes_noiva(noiva, considerar_salto=False):
        base = noiva.y + noiva.altura
        if considerar_salto:
            base += noiva.centro_y_colisao_aerea - noiva.centro_y
        return base

    def _alinhamento_impacto(self, noiva):
        return abs(self.pes_y - self._pes_noiva(noiva, True)) <= self.TOLERANCIA_IMPACTO_Y

    def _mover_para(self, x, pes_y, dt):
        # ALTERAÇÃO: os dois eixos movimentam independentemente por delta time.
        dx = x - self.centro_x
        dy = pes_y - self.pes_y
        if abs(dx) > 1:
            self.x += math.copysign(min(abs(dx), self.VELOCIDADE * self.MULTIPLICADOR_VELOCIDADE_FLANCO * dt), dx)
        if abs(dy) > 1:
            self.y += math.copysign(min(abs(dy), self.VELOCIDADE_ALINHAMENTO * self.MULTIPLICADOR_VELOCIDADE_FLANCO * dt), dy)

    def _iniciar_flanco(self, noiva, altura_mundo):
        # ALTERAÇÃO: escolhe contorno vertical com espaço suficiente na pista.
        pe_noiva = self._pes_noiva(noiva)
        cima = altura_mundo - noiva.ALTURA_PISTA
        baixo = altura_mundo
        # Mantém waypoint dentro da mesma faixa jogável dos pés.
        if pe_noiva - cima >= self.DISTANCIA_PASSAGEM_Y:
            self.lado_desvio = -1
        elif baixo - pe_noiva >= self.DISTANCIA_PASSAGEM_Y:
            self.lado_desvio = 1
        else:
            return False
        self.alvo_passagem_y = max(cima, min(baixo,
            pe_noiva + self.lado_desvio * self.DISTANCIA_PASSAGEM_Y))
        self.estado_flanco = 'desviar_y'
        self.tempo_flanco = 0.0
        self.tempo_desde_flanco = 0.0
        self.tempo_preparacao_golpe = 0.0
        return True

    def _atualizar_flanco(self, noiva, dt, altura_mundo):
        self.tempo_flanco += dt
        if self.tempo_flanco > self.TEMPO_MAX_FLANQUEAMENTO:
            self.estado_flanco = None
            return
        # Atrás = lado oposto ao olhar da Noiva; atualiza alvo em movimento.
        sentido_costas = -1 if noiva.direcao == 'direita' else 1
        alvo_costas_x = noiva.centro_x + sentido_costas * self.DISTANCIA_ATRAS_NOIVA
        pes_noiva = self._pes_noiva(noiva)
        if self.estado_flanco == 'desviar_y':
            self._mover_para(self.centro_x, self.alvo_passagem_y, dt)
            if abs(self.pes_y - self.alvo_passagem_y) <= self.TOLERANCIA_WAYPOINT:
                self.estado_flanco = 'passar_x'
        elif self.estado_flanco == 'passar_x':
            self._mover_para(alvo_costas_x, self.alvo_passagem_y, dt)
            if abs(self.centro_x - alvo_costas_x) <= self.TOLERANCIA_WAYPOINT:
                self.estado_flanco = 'voltar_y'
        elif self.estado_flanco == 'voltar_y':
            self._mover_para(alvo_costas_x, pes_noiva, dt)
            if (abs(self.centro_x - alvo_costas_x) <= self.TOLERANCIA_WAYPOINT
                    and abs(self.pes_y - pes_noiva) <= self.TOLERANCIA_ALINHAMENTO_Y):
                self.estado_flanco = None
                # Pequena preparação: pode atacar em seguida, sem nova volta.
                self.tempo_preparacao_golpe = 0.0
        self.direcao = 'direita' if noiva.centro_x >= self.centro_x else 'esquerda'

    # ========================================================
    # INICIA ATAQUES
    # ========================================================

    # ALTERAÇÃO: somente avança no rodízio quando um ataque realmente começa.
    def _registrar_golpe_iniciado(self):
        self.proximo_golpe_indice = (self.proximo_golpe_indice + 1) % len(self.ORDEM_GOLPES)
        self.tempo_preparacao_golpe = 0.0

    def _iniciar_chute_spin(self):
        self.atacando = True
        self.tipo_ataque = "chute_spin"
        self.tempo_ataque = 0.0
        self.tapa_registrado = False  # um acerto por animação
        self.chute_spin_direita.stop()
        self.chute_spin_esquerda.stop()
        self.chute_spin_direita.play()
        self.chute_spin_esquerda.play()
        self._registrar_golpe_iniciado()

    def _iniciar_tapa(self):

        self.atacando = True
        self.tipo_ataque = "tapa"

        self.tempo_ataque = 0
        self.tempo_alinhado_tapa = 0

        self.tapa_registrado = False

        self.tapa_direita.stop()
        self.tapa_esquerda.stop()

        self.tapa_direita.play()
        self.tapa_esquerda.play()
        self._registrar_golpe_iniciado()


    def _iniciar_garrafa(self):

        self.atacando = True
        self.tipo_ataque = "garrafa"

        self.tempo_ataque = 0
        self.garrafa_disparada = False
        self.inicio_voadora_x = self.x
        self.sinal_voadora = 1 if self.direcao == "direita" else -1
        self.altura_voadora_visual = 0.0

        self.ataque_direita.stop()
        self.ataque_esquerda.stop()

        self.ataque_direita.play()
        self.ataque_esquerda.play()
        # ALTERAÇÃO: voadora não participa do rodízio dos golpes próximos.
        self.tempo_preparacao_golpe = 0.0
        self.tempo_recarga_voadora = 0.0


    # ========================================================
    # ARREMESSA GARRAFA
    # ========================================================

    def _criar_garrafa(self):
        # ALTERAÇÃO: o Amigo usa uma VOADORA, não arremessa garrafas.
        # O acerto é verificado em _atualizar_ataque com a posição atual da Noiva.
        self.garrafa_disparada = True

    def _atualizar_garrafas(self, noiva, dt, largura_mundo):

        for info in self.garrafas[:]:

            info["x"] += info["vx"] * dt

            info["angulo"] += (
                info["velocidade_giro"] * dt
            )

            # ------------------------------------------------
            # IMPACTO NA NOIVA
            # ------------------------------------------------

            if not noiva.recebendo_dano and not noiva.caida:

                centro_garrafa_x = (
                    info["x"]
                    + info["sprite"].width / 2
                )

                centro_garrafa_y = (
                    info["y"]
                    + info["sprite"].height / 2
                )

                distancia_x = abs(
                    centro_garrafa_x - noiva.centro_x
                )

                # A garrafa é lançada alta, então usa uma hitbox
                # específica da região superior da noiva.
                centro_hitbox_garrafa_y = (
                    # ALTERAÇÃO: acompanha a altura visual real do salto.
                    # A garrafa só acerta se cruzar a hitbox da Noiva no ar.
                    noiva.y + noiva.CENTRO_HITBOX_GARRAFA_Y - noiva.altura_pulo
                )

                distancia_y = abs(
                    centro_garrafa_y - centro_hitbox_garrafa_y
                )

                if (
                    distancia_x
                    <= noiva.METADE_LARGURA_HITBOX
                    + info["sprite"].width / 2
                    and distancia_y
                    <= noiva.METADE_ALTURA_HITBOX_GARRAFA
                    + info["sprite"].height / 2
                ):

                    noiva.receber_dano()

                    self.garrafas.remove(info)
                    continue

            # ------------------------------------------------
            # REMOVE FORA DO MUNDO
            # ------------------------------------------------

            if (
                info["x"] < -200
                or info["x"] > largura_mundo + 200
            ):
                self.garrafas.remove(info)


    # ========================================================
    # ATUALIZA ATAQUE EM ANDAMENTO
    # ========================================================

    def _atualizar_ataque_antigo(self, noiva, dt):
        self.tempo_ataque += dt

        # ALTERAÇÃO: voadora com deslocamento horizontal e salto parabólico.
        # Não modifica self.y: a hitbox e os limites da pista continuam no chão.
        if self.tipo_ataque == "garrafa":
            progresso = min(1.0, self.tempo_ataque / max(0.001, self.duracao_ataque))
            avancar = min(self.DISTANCIA_MAX_VOADORA,
                          self.VELOCIDADE_VOADORA_X * self.tempo_ataque)
            self.x = self.inicio_voadora_x + self.sinal_voadora * avancar
            self.altura_voadora_visual = 4 * self.ALTURA_SALTO_VOADORA * progresso * (1 - progresso)

            # ALTERAÇÃO: verifica continuamente o contato enquanto está voando.
            # Uma voadora só causa UM dano; não depende de acertar um frame exato.
            if (not self.garrafa_disparada
                    and self.INICIO_HIT_VOADORA <= progresso <= self.FIM_HIT_VOADORA):
                distancia_x = abs(noiva.centro_x - self.centro_x)
                if (distancia_x <= self.DISTANCIA_VOADORA_HIT
                        and self._alinhamento_impacto(noiva)
                        and not noiva.recebendo_dano and not noiva.caida):
                    if noiva.receber_dano():
                        self.garrafa_disparada = True

            if self.tempo_ataque >= self.duracao_ataque:
                self.atacando = False
                self.tempo_ataque = 0.0
                self.tempo_intervalo = 0.0
                self.garrafa_disparada = False
                self.altura_voadora_visual = 0.0
                self.tempo_recuperacao = self.TEMPO_RECUPERACAO_APOS_GOLPE
                self.tempo_desde_flanco = 0.0  # ALTERAÇÃO: não desvia imediatamente após ataque

        # ALTERAÇÃO: chute giratório tem animação e instante de impacto próprios.
        elif self.tipo_ataque == "chute_spin":
            instante_impacto = ((self.FRAME_IMPACTO_SPIN - 0.5) / self.FRAMES_CHUTE_SPIN) * self.duracao_chute_spin  # ALTERAÇÃO: centro do quadro 5 de 8
            # ALTERAÇÃO: janela do quadro central até o seguinte, sem perder contato
            # por diferença de FPS; um único acerto válido por chute.
            if (not self.tapa_registrado
                    and instante_impacto <= self.tempo_ataque <= instante_impacto + 0.16
                    and abs(noiva.centro_x - self.centro_x) <= self.DISTANCIA_CHUTE_SPIN
                    and self._alinhamento_impacto(noiva)
                    and not noiva.recebendo_dano and not noiva.caida):
                self.tapa_registrado = bool(noiva.receber_dano())
            if self.tempo_ataque >= self.duracao_chute_spin:
                self.atacando = False
                self.tempo_ataque = 0.0
                self.tempo_intervalo = 0.0
                self.tapa_registrado = False
                self.tempo_recuperacao = self.TEMPO_RECUPERACAO_APOS_GOLPE
                self.tempo_desde_flanco = 0.0

        # Upper: mantém os tempos e a hitbox já aprovados.
        else:
            # ALTERAÇÃO: impacto durante janela curta, não só no exato quadro.
            if (not self.tapa_registrado
                    and self.momento_frame_final_tapa <= self.tempo_ataque
                    <= self.momento_frame_final_tapa + 0.18):
                distancia_x = abs(noiva.centro_x - self.centro_x)
                if (distancia_x <= self.DISTANCIA_TAPA
                        and self._alinhamento_impacto(noiva)
                        and not noiva.recebendo_dano and not noiva.caida):
                    self.tapa_registrado = bool(noiva.receber_dano())

            if self.tempo_ataque >= self.duracao_total_tapa:
                self.atacando = False
                self.tempo_ataque = 0.0
                self.tempo_intervalo = 0.0
                self.tempo_alinhado_tapa = 0.0
                self.tapa_registrado = False
                self.tempo_recuperacao = self.TEMPO_RECUPERACAO_APOS_GOLPE
                self.tempo_desde_flanco = 0.0


    # ========================================================
    # IA / MOVIMENTO
    # ========================================================

    def _atualizar_ia_antiga(self, noiva, dt, offset_y=0):
        # ALTERAÇÃO: ataque oportunista tem prioridade sobre zigue-zague e flanco.
        # O Amigo NÃO aguarda rodízio de três golpes nem distância mínima em X
        # para bater quando está colado/sobreposto à Noiva.
        self.tempo_intervalo += dt
        self.tempo_ziguezague += dt
        self.tempo_desde_flanco += dt
        self.tempo_recarga_voadora += dt
        self.tempo_recuperacao = max(0.0, self.tempo_recuperacao - dt)

        dx = noiva.centro_x - self.centro_x
        distancia_x = abs(dx)
        pe_noiva = self._pes_noiva(noiva)
        diferenca_y = pe_noiva - self.pes_y
        distancia_y = abs(diferenca_y)
        alinhado_para_preparar = distancia_y <= self.TOLERANCIA_PREPARACAO_Y
        pode_agir = self.tempo_recuperacao <= 0.0
        alcance_corpo = distancia_x <= self.DISTANCIA_PREPARAR_CORPO_A_CORPO
        alcance_aereo = (self.DISTANCIA_VOADORA_MIN <= distancia_x <= self.DISTANCIA_VOADORA_MAX
                         and self.tempo_recarga_voadora >= self.INTERVALO_VOADORA)

        # 1) Seleção: golpe próximo sempre que estiver na área; voadora quando longe.
        # A intenção permanece fixa durante o aviso para dar chance de esquiva.
        if not alinhado_para_preparar or not pode_agir:
            self.tipo_preparacao = None
            self.tempo_preparacao_golpe = 0.0
        elif alcance_corpo:
            if self.tipo_preparacao != 'corpo':
                self.tipo_preparacao = 'corpo'
                self.tempo_preparacao_golpe = 0.0
            self.tempo_preparacao_golpe += dt
        elif alcance_aereo:
            if self.tipo_preparacao != 'voadora':
                self.tipo_preparacao = 'voadora'
                self.tempo_preparacao_golpe = 0.0
            self.tempo_preparacao_golpe += dt
        else:
            self.tipo_preparacao = None
            self.tempo_preparacao_golpe = 0.0

        preparando = self.tipo_preparacao is not None
        if preparando:
            # ALTERAÇÃO: pausa a movimentação no aviso e vira para o alvo.
            # Isto evita atravessar a Noiva enquanto o temporizador avança.
            self.estado_flanco = None
            self.direcao = 'direita' if dx >= 0 else 'esquerda'
            tempo_necessario = (self.TEMPO_AVISO_VOADORA if self.tipo_preparacao == 'voadora'
                               else self.TEMPO_PREPARACAO_GOLPE)
            if self.tempo_preparacao_golpe >= tempo_necessario:
                if self.tipo_preparacao == 'voadora':
                    self._iniciar_garrafa()
                elif self.proximo_golpe_indice == 0:
                    self._iniciar_tapa()
                else:
                    self._iniciar_chute_spin()
                self.tipo_preparacao = None
                self.tempo_preparacao_golpe = 0.0
                if self.ATIVAR_DEBUG_ATAQUE:
                    print(f'[Amigo] ataque={self.tipo_ataque} dx={distancia_x:.0f} dy={distancia_y:.0f}')
            return

        # 2) Só considera flanqueamento quando NÃO há oportunidade de ataque.
        if self.estado_flanco is not None:
            self._atualizar_flanco(noiva, dt, self._altura_mundo_atual)
            return
        frente_noiva = 1 if noiva.direcao == 'direita' else -1
        esta_na_frente = (self.centro_x - noiva.centro_x) * frente_noiva > 0
        if (self.ATIVAR_FLANQUEAMENTO and pode_agir
                and self.tempo_desde_flanco >= self.INTERVALO_FLANQUEAMENTO
                and self.DISTANCIA_PREPARAR_CORPO_A_CORPO < distancia_x
                <= self.DISTANCIA_INICIAR_FLANQUEAMENTO and esta_na_frente):
            if self._iniciar_flanco(noiva, self._altura_mundo_atual):
                return

        # 3) Zigue-zague só longe do alcance de ataque; fecha faixa Y ao chegar.
        fator = min(1.0, max(0.0,
            (distancia_x - self.DISTANCIA_PREPARAR_CORPO_A_CORPO) /
            max(1.0, self.DISTANCIA_REDUZ_ZIGUEZAGUE)))
        deslocamento_y = (math.sin(2 * math.pi * self.tempo_ziguezague
            / max(0.1, self.PERIODO_ZIGUEZAGUE)) * self.AMPLITUDE_ZIGUEZAGUE_Y * fator)
        alvo_pes_y = pe_noiva + offset_y + deslocamento_y
        self.direcao = 'direita' if dx >= 0 else 'esquerda'
        if distancia_x > self.DISTANCIA_PARADA:
            self.x += math.copysign(min(distancia_x - self.DISTANCIA_PARADA,
                                        self.VELOCIDADE * dt), dx)
        diferenca_alvo_y = alvo_pes_y - self.pes_y
        if abs(diferenca_alvo_y) > 1:
            self.y += math.copysign(min(abs(diferenca_alvo_y),
                                        self.VELOCIDADE_ALINHAMENTO * dt), diferenca_alvo_y)


    # ========================================================
    # ALTERAÇÃO: COMBATE POR COMBOS COMPLETOS + VOADORA INDEPENDENTE
    # ========================================================
    def _iniciar_combo(self):
        self.atacando = True
        self.tipo_ataque = "combo"
        self.combo_tipo = "socos" if self.proximo_combo == 0 else "chutes"
        self.proximo_combo = 1 - self.proximo_combo
        self.combo_etapa = 0
        self.tempo_preparacao_golpe = 0.0
        self.estado_flanco = None
        self._iniciar_etapa_combo()
        if self.ATIVAR_DEBUG_ATAQUE:
            print(f"[Amigo] Iniciou combo {self.combo_tipo}")

    def _iniciar_etapa_combo(self):
        self.combo_tempo_etapa = 0.0
        self.combo_dano_registrado = False
        if self.combo_tipo == "socos":
            if self.combo_etapa < 2:
                self.combo_sprite = (self.socos_direita if self.direcao == "direita"
                                     else self.socos_esquerda)
                tempo_ms = self.TEMPO_SOCO_COMBO_MS
            else:
                self.combo_sprite = (self.tapa_direita if self.direcao == "direita"
                                     else self.tapa_esquerda)
                tempo_ms = self.TEMPO_UPPER_FINAL_MS
        else:
            if self.combo_etapa < 2:
                self.combo_sprite = (self.chute_combo_direita if self.direcao == "direita"
                                     else self.chute_combo_esquerda)
                tempo_ms = self.TEMPO_CHUTE_COMBO_MS
            else:
                self.combo_sprite = (self.chute_spin_direita if self.direcao == "direita"
                                     else self.chute_spin_esquerda)
                tempo_ms = self.TEMPO_SPIN_FINAL_MS
        self.combo_duracao_etapa = tempo_ms / 1000
        self.combo_sprite.set_total_duration(tempo_ms)
        self.combo_sprite.set_loop(False)
        self.combo_sprite.stop()
        self.combo_sprite.set_curr_frame(0)
        self.combo_sprite.play()

    def _atualizar_combo(self, noiva, dt):
        self.combo_tempo_etapa += dt
        progresso = min(1.0, self.combo_tempo_etapa / max(0.001, self.combo_duracao_etapa))
        # Impacto dentro do movimento, de modo que o jogador ainda possa desviar.
        impacto_inicial = 0.43 if self.combo_etapa < 2 else 0.50
        impacto_final = 0.71 if self.combo_etapa < 2 else 0.72
        if not self.combo_dano_registrado and impacto_inicial <= progresso <= impacto_final:
            alcance = self.DISTANCIA_HIT_SOCO if self.combo_tipo == "socos" else self.DISTANCIA_HIT_CHUTE
            dx = abs(noiva.centro_x - self.centro_x)
            # ALTERAÇÃO: mede o impacto pela base no chão (não pelo centro do sprite).
            # O chute tem envelope vertical mais estreito que os socos.
            dy = abs(self._pes_noiva(noiva, considerar_salto=True) - self.pes_y)
            tolerancia_y = (self.TOLERANCIA_IMPACTO_SOCO_Y if self.combo_tipo == 'socos'
                            else self.TOLERANCIA_IMPACTO_CHUTE_Y)
            # A posição visual do salto da Noiva continua permitindo a esquiva.
            desvio_salto = getattr(noiva, 'altura_pulo', 0.0) > 85
            if (dx <= alcance and dy <= tolerancia_y and not desvio_salto
                    and not noiva.caida and not noiva.levantando):
                # ALTERAÇÃO: três impactos do Amigo derrubam, sem alterar outros inimigos.
                if noiva.receber_dano(impactos=1, limiar_queda=3):
                    self.combo_dano_registrado = True
                    if self.ATIVAR_DEBUG_ATAQUE:
                        print(f"[Amigo] contato {self.combo_tipo} etapa={self.combo_etapa+1} dx={dx:.0f}")
        if self.combo_tempo_etapa >= self.combo_duracao_etapa:
            self.combo_etapa += 1
            if self.combo_etapa < 3:
                # ALTERAÇÃO: completa a série mesmo que a Noiva tenha esquivado.
                self._iniciar_etapa_combo()
            else:
                self.atacando = False
                self.tempo_ataque = 0.0
                self.tempo_recuperacao = self.TEMPO_RECUPERACAO_APOS_GOLPE
                self.tempo_desde_flanco = 0.0

    def _atualizar_ataque(self, noiva, dt):
        if self.tipo_ataque == 'combo':
            self._atualizar_combo(noiva, dt)
            return
        if self.tipo_ataque == 'garrafa':
            # ALTERAÇÃO: voadora distante, com um único impacto que provoca queda.
            self.tempo_ataque += dt
            t = min(1.0, self.tempo_ataque / max(0.001, self.duracao_ataque))
            # ALTERAÇÃO: movimento termina no trecho de chute, em ambas as direções.
            # Os quadros visíveis também são limitados a 0..7, no desenho.
            tempo_movimento = self.duracao_ataque * self.FRACAO_MOVIMENTO_VOADORA
            avanço = min(self.DISTANCIA_MAX_VOADORA, self.VELOCIDADE_VOADORA_X * min(self.tempo_ataque, tempo_movimento))
            self.x = self.inicio_voadora_x + self.sinal_voadora * avanço
            self.altura_voadora_visual = 4 * self.ALTURA_SALTO_VOADORA * t * (1 - t)
            if not self.garrafa_disparada and self.INICIO_HIT_VOADORA <= t <= self.FIM_HIT_VOADORA:
                dx = abs(noiva.centro_x - self.centro_x)
                dy = abs(self._pes_noiva(noiva) - self.pes_y)
                if (dx <= self.DISTANCIA_VOADORA_HIT and dy <= self.TOLERANCIA_COMBO_Y
                        and getattr(noiva, 'altura_pulo', 0.0) < 85):
                    if noiva.receber_dano(impactos=3, limiar_queda=3):
                        self.garrafa_disparada = True
                        if self.ATIVAR_DEBUG_ATAQUE:
                            print('[Amigo] VOADORA acertou e derrubou')
            if t >= 1.0:
                self.atacando = False
                self.altura_voadora_visual = 0.0
                self.tempo_recuperacao = self.TEMPO_RECUPERACAO_APOS_GOLPE
                self.tempo_desde_flanco = 0.0
            return
        self._atualizar_ataque_antigo(noiva, dt)

    def _atualizar_ia(self, noiva, dt, offset_y=0):
        self.tempo_recarga_voadora += dt
        self.tempo_recuperacao = max(0.0, self.tempo_recuperacao - dt)
        self.tempo_ziguezague += dt
        self.tempo_desde_flanco += dt
        dx = noiva.centro_x - self.centro_x
        abs_dx = abs(dx)
        dy = self._pes_noiva(noiva) - self.pes_y
        abs_dy = abs(dy)
        self.direcao = 'direita' if dx >= 0 else 'esquerda'
        # Prioridade 1: se entrou no envelope próximo, prepara combo e não flanqueia.
        # Prioridade 2: voadora independente e com maior alcance.
        tipo = None
        if self.tempo_recuperacao <= 0 and abs_dy <= self.TOLERANCIA_PREPARACAO_Y:
            if abs_dx <= self.DISTANCIA_COMBO_INICIAR:
                tipo = 'combo'
            elif (self.DISTANCIA_VOADORA_MIN <= abs_dx <= self.DISTANCIA_VOADORA_MAX
                  and self.tempo_recarga_voadora >= self.INTERVALO_VOADORA):
                tipo = 'voadora'
        if tipo:
            if self.tipo_preparacao != tipo:
                self.tipo_preparacao = tipo
                self.tempo_preparacao_golpe = 0.0
            self.estado_flanco = None
            self.tempo_preparacao_golpe += dt
            if self.tempo_preparacao_golpe >= (self.AVISO_COMBO_S if tipo == 'combo' else self.TEMPO_AVISO_VOADORA):
                if tipo == 'combo':
                    self._iniciar_combo()
                else:
                    self._iniciar_garrafa()
                    self.duracao_ataque = self.TEMPO_VOADORA / 1000
                self.tipo_preparacao = None
                self.tempo_preparacao_golpe = 0.0
            return
        self.tipo_preparacao = None
        self.tempo_preparacao_golpe = 0.0
        # Flanqueamento e zigue-zague permanecem subsidiários ao combate.
        if self.estado_flanco is not None:
            self._atualizar_flanco(noiva, dt, self._altura_mundo_atual)
            return
        frente = 1 if noiva.direcao == 'direita' else -1
        if (self.ATIVAR_FLANQUEAMENTO and self.tempo_recuperacao <= 0
                and self.tempo_desde_flanco >= self.INTERVALO_FLANQUEAMENTO
                and self.DISTANCIA_COMBO_INICIAR < abs_dx <= self.DISTANCIA_INICIAR_FLANQUEAMENTO
                and (self.centro_x - noiva.centro_x) * frente > 0):
            if self._iniciar_flanco(noiva, self._altura_mundo_atual):
                return
        oscilacao = math.sin(2 * math.pi * self.tempo_ziguezague / max(0.1,self.PERIODO_ZIGUEZAGUE))
        fator = min(1.0, max(0.0, (abs_dx-self.DISTANCIA_COMBO_INICIAR)/max(1,self.DISTANCIA_REDUZ_ZIGUEZAGUE)))
        alvo_pe = self._pes_noiva(noiva) + offset_y + oscilacao*self.AMPLITUDE_ZIGUEZAGUE_Y*fator
        if abs_dx > self.DISTANCIA_PARADA:
            self.x += math.copysign(min(max(0,abs_dx-self.DISTANCIA_PARADA), self.VELOCIDADE*dt), dx)
        delta_y = alvo_pe - self.pes_y
        if abs(delta_y) > 1:
            self.y += math.copysign(min(abs(delta_y), self.VELOCIDADE_ALINHAMENTO*dt), delta_y)

    # ========================================================
    # RECEBE GOLPE DA NOIVA
    # ========================================================

    def verificar_golpe_noiva(self, noiva):

        if (self.caindo or self.derrotado or self.levantando
                or self.eliminado or self.removido or not self.entrada_liberada
                or self.recebendo_dano):
            return

        if not noiva.ataque_pode_causar_dano():
            return

        # Este Penetra já recebeu este ataque específico.
        if self.ultimo_id_ataque_noiva == noiva.id_ataque:
            return

        # ALTERAÇÃO: o golpe da noiva só alcança inimigos à sua frente.
        # Mantém a hitbox e os alcances já ajustados para o combate.
        # ALTERAÇÃO: considera a largura do corpo, não apenas o ponto central.
        # Amigo andando para a esquerda pode ter corpo parcialmente sobreposto
        # ao da Noiva; nesse caso o soco ainda precisa acertar pela frente.
        if noiva.direcao == "direita" and self.centro_x + self.LARGURA_CORPO / 2 < noiva.centro_x:
            return
        if noiva.direcao == "esquerda" and self.centro_x - self.LARGURA_CORPO / 2 > noiva.centro_x:
            return

        distancia_centros_x = abs(
            noiva.centro_x - self.centro_x
        )

        distancia_y = abs(
            noiva.centro_y - self.centro_y
        )

        distancia_entre_corpos = (
            distancia_centros_x
            - noiva.LARGURA_CORPO / 2
            - self.LARGURA_CORPO / 2
        )

        if distancia_entre_corpos < 0:
            distancia_entre_corpos = 0

        if (
            distancia_entre_corpos <= noiva.alcance_ataque_atual()
            and distancia_y <= noiva.TOLERANCIA_GOLPE_Y
        ):

            self.ultimo_id_ataque_noiva = noiva.id_ataque
            self._receber_golpe(noiva)


    def _receber_golpe(self, noiva):

        self.golpes += 1

        # Interrompe qualquer ataque.
        self.atacando = False
        self.tempo_ataque = 0
        self.tempo_intervalo = 0
        # ALTERAÇÃO: interrompido pela Noiva, encerra a série em andamento.
        self.combo_tipo = None
        self.combo_sprite = None

        self.garrafa_disparada = False
        self.tapa_registrado = False
        self.tempo_alinhado_tapa = 0
        # ALTERAÇÃO: golpe interrompido não deixa a imagem suspensa no ar.
        self.altura_voadora_visual = 0.0
        self.tempo_preparacao_golpe = 0.0
        self.estado_flanco = None  # ALTERAÇÃO: dano cancela contorno, sem perseguir waypoint antigo.

        self.ataque_direita.stop()
        self.ataque_esquerda.stop()

        self.tapa_direita.stop()
        self.tapa_esquerda.stop()

        # ----------------------------------------------------
        # TERCEIRO GOLPE -> QUEDA
        # ----------------------------------------------------

        if self.golpes >= self.GOLPES_POR_QUEDA:

            self.recebendo_dano = False

            self.caindo = True
            self.tempo_queda = 0
            self.quedas = self.quedas + 1  # ALTERAÇÃO: conta quedas, não golpes.
            self.direcao_queda = self.direcao  # ALTERAÇÃO: congela orientação da animação de queda
            self.tempo_corpo_morto = 0.0

            # Afasta ligeiramente da noiva.
            if self.centro_x >= noiva.centro_x:
                self.x += self.AFASTAMENTO_QUEDA
            else:
                self.x -= self.AFASTAMENTO_QUEDA

            self.queda_direita.stop()
            self.queda_esquerda.stop()

            self.queda_direita.play()
            self.queda_esquerda.play()

        # ----------------------------------------------------
        # PRIMEIROS 2 GOLPES -> DANO
        # ----------------------------------------------------

        else:

            self.recebendo_dano = True
            self.tempo_dano = 0


    # ========================================================
    # ATUALIZAÇÃO PRINCIPAL
    # ========================================================

    # ALTERAÇÃO: assinatura padronizada com a Convidada.
    # altura_mundo permite aplicar os mesmos limites da pista.
    def atualizar(self, noiva, dt, largura_mundo, altura_mundo, offset_y=0):

        self._altura_mundo_atual = altura_mundo  # ALTERAÇÃO: usado no flanqueamento.
        # ALTERAÇÃO: morte definitiva é independente do levantamento da primeira queda.
        # A segunda queda termina no chão e o corpo desaparece após um breve tempo.
        if self.removido:
            return
        if self.eliminado:
            self.tempo_corpo_morto += dt
            if self.tempo_corpo_morto >= self.TEMPO_CORPO_APOS_MORTE:
                self.removido = True
            return

        # Projéteis continuam existindo mesmo que o penetra
        # esteja recebendo dano ou caído.
        pass  # ALTERAÇÃO: Amigo não tem projéteis de garrafa

        # ----------------------------------------------------
        # DANO
        # ----------------------------------------------------

        if self.recebendo_dano:

            self.tempo_dano += dt

            if self.tempo_dano >= self.duracao_dano:
                self.recebendo_dano = False
                self.tempo_dano = 0

        # ----------------------------------------------------
        # QUEDA
        # ----------------------------------------------------

        if self.caindo:

            self.tempo_queda += dt

            if self.tempo_queda >= self.duracao_queda:

                self.caindo = False
                self.derrotado = True
                self.queda_direita.set_curr_frame(8)
                self.queda_esquerda.set_curr_frame(8)

                self.tempo_queda = self.duracao_queda
                self.tempo_caido = 0

        # ----------------------------------------------------
        # CAÍDO
        # ----------------------------------------------------

        if self.derrotado and not self.eliminado:

            # ALTERAÇÃO: na segunda queda, NÃO inicia levantamento.
            # Termina a animação no último quadro, depois desaparece.
            if self.quedas >= self.QUEDAS_PARA_ELIMINAR:
                self.eliminado = True
                self.levantando = False
                self.tempo_corpo_morto = 0.0
                self.queda_direita.set_curr_frame(8)
                self.queda_esquerda.set_curr_frame(8)
                return

            self.tempo_caido += dt

            if self.tempo_caido >= self.TEMPO_CAIDO:
                self.tempo_caido = 0
                # ALTERAÇÃO: SOMENTE a primeira queda pode levantar.
                self.derrotado = False
                self.levantando = True
                self.tempo_levantar = 0.0
                self.levantar_direita.set_curr_frame(0)
                self.levantar_esquerda.set_curr_frame(0)

        # ALTERAÇÃO: retrocede manualmente os nove quadros da queda.
        if self.levantando:
            self.tempo_levantar = self.tempo_levantar + dt
            progresso = min(1.0, self.tempo_levantar / max(self.TEMPO_LEVANTAR, 0.001))
            # ALTERAÇÃO: os sprites de levantamento CONTÊM somente 3 quadros.
            quadro = min(2, int(progresso * 3))
            self.levantar_direita.set_curr_frame(quadro)
            self.levantar_esquerda.set_curr_frame(quadro)
            if progresso >= 1.0:
                self.levantando = False
                self.recebendo_dano = False
                self.caindo = False
                self.atacando = False
                self.tempo_queda = 0
                self.tempo_dano = 0
                self.tempo_ataque = 0
                self.golpes = 0
                self.tempo_intervalo = 0
                self.tempo_alinhado_tapa = 0
                self.tempo_preparacao_golpe = 0.0
                self.altura_voadora_visual = 0.0
                self.estado_flanco = None  # ALTERAÇÃO: reinicia navegação após levantar
                self.tipo_preparacao = None
                self.tempo_recuperacao = 0.0

        # ----------------------------------------------------
        # IA / ATAQUE
        # ----------------------------------------------------

        if (
            not self.recebendo_dano
            and not self.caindo
            and not self.derrotado
            and not self.levantando
            and not self.eliminado
            and self.entrada_liberada
        ):

            if self.atacando:
                self._atualizar_ataque(noiva, dt)
            else:
                self._atualizar_ia(noiva, dt, offset_y)

        # ALTERAÇÃO: mesma limitação de posição usada pela Convidada.
        # Preserva a área jogável e evita sair pelos lados do mundo.
        if self.x < 0:
            self.x = 0
        if self.x > largura_mundo - self.andando_direita.width:
            self.x = largura_mundo - self.andando_direita.width

        limite_superior = altura_mundo - noiva.ALTURA_PISTA - self.andando_direita.height
        limite_inferior = altura_mundo - self.andando_direita.height
        if self.y < limite_superior:
            self.y = limite_superior
        if self.y > limite_inferior:
            self.y = limite_inferior


    # ========================================================
    # DESENHA GARRAFAS
    # ========================================================

    def desenhar_garrafas(self):
        # ALTERAÇÃO: compatibilidade com a chamada no main.py.
        # O Amigo não lança garrafas; sua voadora é um ataque corporal.
        pass

    def _sprite_ativo(self):

        # ALTERAÇÃO: a orientação da queda fica travada para não trocar
        # spritesheets ao morrer para a esquerda.
        if self.levantando:
            return self.levantar_direita if self.direcao_queda == "direita" else self.levantar_esquerda
        if self.eliminado or self.derrotado or self.caindo:
            return self.queda_direita if self.direcao_queda == "direita" else self.queda_esquerda

        # ALTERAÇÃO: usa o novo sprite idle durante a espera inicial.
        if not self.entrada_liberada:
            return self.idle_direita if self.direcao == "direita" else self.idle_esquerda

        if self.recebendo_dano:
            return self.dano_direita if self.direcao == "direita" else self.dano_esquerda

        if self.atacando:
            if self.tipo_ataque == "combo":
                return self.combo_sprite
            if self.tipo_ataque == "tapa":
                return self.tapa_direita if self.direcao == "direita" else self.tapa_esquerda
            if self.tipo_ataque == "chute_spin":
                return self.chute_spin_direita if self.direcao == "direita" else self.chute_spin_esquerda
            return self.ataque_direita if self.direcao == "direita" else self.ataque_esquerda

        return self.andando_direita if self.direcao == "direita" else self.andando_esquerda

    # ========================================================
    # ALTERAÇÃO: ATUALIZA ANIMAÇÃO SEPARADAMENTE DO DESENHO
    # ========================================================

    def atualizar_animacao(self):

        if self.removido or self.eliminado or self.derrotado or self.recebendo_dano or self.levantando:
            return
        if not self.entrada_liberada:
            # ALTERAÇÃO: anima a pose idle continuamente enquanto aguarda.
            sprite = self._sprite_ativo()
            # ALTERAÇÃO: Amigo não possui spritesheet idle; aguarda parado no quadro zero.
            sprite.set_curr_frame(0)
            return

        sprite = self._sprite_ativo()

        if self.caindo:
            sprite.update()

        elif self.atacando:
            # ALTERAÇÃO: NÃO atualizar a voadora automaticamente: isso percorria
            # os 16 quadros, apesar do deslocamento limitado à metade.
            if self.tipo_ataque == "garrafa":
                progresso = min(0.999, self.tempo_ataque / max(0.001, self.duracao_ataque))
                quadro = min(self.FRAMES_VOADORA_VISIVEIS - 1,
                             int(progresso * self.FRAMES_VOADORA_VISIVEIS))
                self.ataque_direita.set_curr_frame(quadro)
                self.ataque_esquerda.set_curr_frame(quadro)
            elif self.tipo_ataque != "tapa" or self.tempo_ataque < self.duracao_tapa:
                sprite.update()

        else:
            sprite.play()
            sprite.update()

    # ========================================================
    # DESENHO
    # ========================================================

    def desenhar(self):

        # ALTERAÇÃO: o cadáver permanece visível após a segunda queda.
        # O estado eliminado conserva o sprite de queda no último quadro.
        if self.removido:
            return
        # ALTERAÇÃO: posiciona apenas o sprite selecionado.
        sprite = self._sprite_ativo()
        # ALTERAÇÃO: durante a queda e após ela, os dois sentidos usam o
        # quadro correto. Não depende do avanço automático da PPlay.
        if self.caindo:
            progresso_queda = min(0.999, self.tempo_queda / max(0.001, self.duracao_queda))
            sprite.set_curr_frame(min(8, int(progresso_queda * 9)))
        elif self.derrotado or self.eliminado:
            sprite.set_curr_frame(8)
        # ALTERAÇÃO: trava os quadros da voadora também no desenho, garantindo
        # o mesmo resultado nas spritesheets direita e esquerda.
        if self.atacando and self.tipo_ataque == "garrafa":
            progresso = min(0.999, self.tempo_ataque / max(0.001, self.duracao_ataque))
            sprite.set_curr_frame(min(self.FRAMES_VOADORA_VISIVEIS - 1,
                                      int(progresso * self.FRAMES_VOADORA_VISIVEIS)))
        # ALTERAÇÃO: o novo idle tem 203 px, enquanto andar tem 300 px.
        # Centraliza os sprites sem alterar posição de mundo nem hitbox.
        ajuste_x = (self.andando_direita.width - sprite.width) / 2
        # ALTERAÇÃO: somente o desenho sobe na voadora; self.y permanece na pista.
        # ALTERAÇÃO: sprite do upper é maior; mantém os PÉS na mesma linha de chão.
        # No salto da voadora a elevação visual continua independente.
        ajuste_y_upper = (self.altura - sprite.height) if (self.atacando and
            ((self.tipo_ataque == 'combo' and self.combo_tipo == 'socos' and self.combo_etapa == 2)
             or self.tipo_ataque == 'tapa')) else 0
        sprite.set_position(self.x + ajuste_x, self.y + ajuste_y_upper - self.altura_voadora_visual)
        sprite.draw()
