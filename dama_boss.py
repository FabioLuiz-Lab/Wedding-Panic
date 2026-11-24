"""Dama Boss e bancos decorativos — Wedding Panic / Power PPlay 2.1.

# ALTERAÇÃO: especial de granada a cada 5 hits, banco a cada 8 hits.
# Todos os PNGs originais permanecem intactos; escala aplicada em cache.
"""
from pathlib import Path
import random
import math
import pygame
from PPlay.sprite import Sprite

PASTA_PROJETO = Path(__file__).resolve().parent
CACHE = PASTA_PROJETO / 'assets' / '.cache_escala_dama'

# ============================================================
# ALTERAÇÃO: POSIÇÕES LOCAIS À ÚLTIMA TELA DA FASE 2 (1600x900)
# X = 0 é a borda esquerda do último fundo, NÃO o início do mundo.
# ============================================================
BANCO_SUPERIOR_DIREITO = {
    'arquivo': 'assets/objetos/banqueta-esq.png',
    'x': 1500, 'y': 205, 'escala': 0.29,
    'espelhar': True,  # usa o mesmo arquivo para a direita
}
BANCO_INFERIOR_ESQUERDO = {
    'arquivo': 'assets/objetos/banqueta-esq.png',
    'x': 220, 'y': 620, 'escala': 0.22,
    'espelhar': False,
}

# ALTERAÇÃO: posição da Dama relativa ao BANCO SUPERIOR DIREITO.
DAMA_SENTADA = {
    'x_offset': -5,              # deslocamento horizontal em relação ao centro do banco
    'y_offset': 0,               # deslocamento vertical extra (px)
    'direcao': 'esquerda',
    'escala': 1.00,              # 392px de altura; maior que a Noiva (~300px)
    'duracao_ms': 2800,
    'intervalo_repeticao': 0.0,  # ALTERAÇÃO: sem pausa; loop contínuo da animação sentada.
    'animar': True,             # False: mantém o primeiro frame
    'altura_assento': 0.63,     # posição do corpo em relação à altura do banco
    'profundidade_offset': 1,   # ordenação na frente do banco
}

# ALTERAÇÃO: escalas INDIVIDUAIS para cada animação futura da Dama.
# Apenas 'sentada' é utilizada neste momento. Nomes e frames editáveis.
DAMA_ANIMACOES = {
    'sentada': {'frames': 36, 'escala': 1.00},
    'andando': {'frames': 16, 'escala': 1.00},
    'atirando': {'frames': 16, 'escala': 1.00},
    'dano': {'frames': 1, 'escala': 1.00},
    'derrota': {'frames': 36, 'escala': 1.00},
    'granada': {'frames': 16, 'escala': 1.00},
    'salto': {'frames': 16, 'escala': 1.00},
    'tiro-aereo': {'frames': 16, 'escala': 1.00},
    # ALTERAÇÃO: opcional; se não existir, usa a pose de caminhada.
    'chute': {'frames': 9, 'escala': 1.00},
}


# ============================================================
# ALTERAÇÃO: ETAPA 1 - DESPERTAR E SALTO INICIAL DA DAMA
# ============================================================
DISTANCIA_ATIVACAO = 600       # pixels horizontais entre Noiva e Dama
TEMPO_DESPERTAR = 30.0        # segundos; inicia somente uma vez
DURACAO_SALTO_CENTRO = 1.8    # segundos para saltar do banco ao salão
ALTURA_ARCO_SALTO = 180       # pixels acima da trajetória linear
DESTINO_SALTO_X = 800        # centro X LOCAL da última tela (1600x900)
DESTINO_SALTO_PE_Y = 770     # linha dos pés ao terminar o salto
DURACAO_ANIMACAO_SALTO_MS = 1800
DURACAO_ANIMACAO_ANDANDO_MS = 1600
MOSTRAR_CONTAGEM_DAMA = True  # mostra cronômetro somente durante a espera

# ============================================================
# ALTERAÇÃO: ETAPA 2 - CONTROLES EDITÁVEIS DE COMBATE
# ============================================================
VELOCIDADE_DAMA_X = 95.0
VELOCIDADE_DAMA_Y = 65.0
DISTANCIA_PARADA_DAMA = 240
# ALTERAÇÃO: alinhamento pela LINHA DOS PÉS, independente da altura dos PNGs.
TOLERANCIA_TIRO_Y = 42       # tolerância para rajada normal (px)
TOLERANCIA_CHUTE_Y = 36      # tolerância exclusiva do chute (px)
TEMPO_ALINHADA_PARA_ATIRAR = 0.9   # atraso contínuo após alinhar (s)
OFFSET_TIRO_ACIMA_DOS_PES = 145    # origem visual do projétil no tiro normal
INTERVALO_SALTO_ESQUIVA = 7.0      # saltos adicionais para dar respiro à Noiva (s)
DURACAO_SALTO_ESQUIVA = 1.6
ALTURA_SALTO_ESQUIVA = 260
DISTANCIA_SALTO_ESQUIVA = 410
INTERVALO_TIRO_AEREO = 11.0        # critério independente da rajada normal (s)
DISTANCIA_MIN_TIRO_AEREO = 230     # não faz esse ataque colada na Noiva (px)
DESLOCAMENTO_X_TIRO_AEREO = 290   # salto aéreo com deslocamento lateral (px)
INTERVALO_RAJADA = 5.0
TIROS_POR_RAJADA = 5
INTERVALO_ENTRE_TIROS_DAMA = 0.18
VELOCIDADE_PROJETIL_DAMA = 510
RAIO_PROJETIL_DAMA = 16
ALTERNAR_TIRO_AEREO = True
# ALTERAÇÃO: pulo REAL da Dama enquanto executa a rajada aérea.
ALTURA_SALTO_TIRO_AEREO = 390  # pixels no ponto mais alto
DURACAO_SALTO_TIRO_AEREO = 2.25  # segundos, ajustável independentemente da cadência de tiro
INTERVALO_GRANADA = 9.0
TEMPO_VOO_GRANADA = 1.2
TEMPO_EXPLOSAO = 0.85
RAIO_EXPLOSAO = 110
DISTANCIA_CHUTE_DAMA = 145
INTERVALO_CHUTE_DAMA = 2.5
RECUO_CHUTE_NOIVA = 10
RECUO_EXPLOSAO_NOIVA = 90
ALTURA_IMPULSO_EXPLOSAO = 80
TEMPO_IMPULSO_EXPLOSAO = 0.65
# ALTERAÇÃO: gatilhos especiais pela quantidade de hits VÁLIDOS recebidos.
HITS_PARA_GRANADA_CANTO = 5      # 5, 10, 15... hits: salta ao canto distante e atira granada.
HITS_PARA_RETORNO_BANCO = 8      # 8, 16... hits: salta a um dos bancos.
MARGEM_CANTO_X = 85              # distância das bordas laterais para o centro da Dama (px).
PE_CANTO_SUPERIOR_Y = 590        # altura dos pés na fileira superior dos cantos (px).
PE_CANTO_INFERIOR_Y = 865        # altura dos pés na fileira inferior dos cantos (px).
DURACAO_SALTO_CANTO = 1.6       # segundos do salto até o canto.
ALTURA_SALTO_CANTO = 220        # altura adicional do arco (px).
TEMPO_RETORNO_BANCO = 30.0      # mantido como referência; retorno agora usa hits, não tempo.
TEMPO_NO_BANCO = 5.0
DURACAO_SALTO_BANCO = 1.5
HITS_DAMA_DERROTA = 20
TEMPO_DANO_DAMA = 0.45
PONTOS_TIROS_DAMA = 50
PONTOS_SOCO_DAMA = 30
PONTOS_CHUTE_DAMA = 10
# ============================================================
# ALTERAÇÃO: EFEITOS VISUAIS REAIS DA PASTA assets/objetos
# Cada escala é individual e não altera as imagens originais.
# ============================================================
ARQUIVO_PROJETIL_DAMA = 'assets/objetos/projetil.png'  # 80 x 24, 1 quadro
ESCALA_PROJETIL_DAMA = 0.85
ARQUIVO_GRANADA_DAMA = 'assets/objetos/granada.png'    # 1254 x 1254, 1 quadro
ESCALA_GRANADA_DAMA = 0.045
ARQUIVO_EXPLOSAO_DAMA = 'assets/objetos/explosao.png'  # 3240 x 350
FRAMES_EXPLOSAO_DAMA = 9    # ALTERAÇÃO: confirmado pelo usuário: 9 x 360 px
ESCALA_EXPLOSAO_DAMA = 0.75

# ALTERAÇÃO: arquivos existentes na pasta sons, conforme captura enviada.
# Se faltar algum arquivo ou o formato não for aceito pelo mixer, continua sem áudio.
SONS_DAMA = {
    'tiro': 'sons/rajada.wav',
    'granada': 'sons/lancar1.mp3',
    'explosao': 'sons/explosao1.wav',
    'dano': None,
    'derrota': 'sons/derrota-1.mp3',
}


def _criar_sprite_escalado(caminho, frames, escala, espelhar=False):
    """# ALTERAÇÃO: cópia dimensionada por QUADRO, evitando distorção da animação."""
    caminho = PASTA_PROJETO / caminho
    if not caminho.is_file():
        raise FileNotFoundError(f'Asset não encontrado: {caminho}')
    imagem = pygame.image.load(str(caminho)).convert_alpha()
    largura, altura = imagem.get_size()
    if largura % frames:
        raise ValueError(f'{caminho.name}: largura {largura} não divisível por {frames} quadros')
    quadro_largura = largura // frames
    novo_w = max(1, round(quadro_largura * escala))
    novo_h = max(1, round(altura * escala))
    CACHE.mkdir(parents=True, exist_ok=True)
    nome = f'{caminho.stem}_{frames}f_{novo_w}x{novo_h}_{"esp" if espelhar else "normal"}.png'
    arquivo = CACHE / nome
    if not arquivo.exists() or caminho.stat().st_mtime > arquivo.stat().st_mtime:
        tira = pygame.Surface((frames * novo_w, novo_h), pygame.SRCALPHA)
        for i in range(frames):
            quadro = imagem.subsurface((i * quadro_largura, 0, quadro_largura, altura))
            quadro = pygame.transform.smoothscale(quadro, (novo_w, novo_h))
            if espelhar:
                quadro = pygame.transform.flip(quadro, True, False)
            tira.blit(quadro, (i * novo_w, 0))
        pygame.image.save(tira, str(arquivo))
    sprite = Sprite(str(arquivo), frames)
    return sprite


class BancoBistro:
    """Banco decorativo sem hitbox; acompanha a câmera nativa por Sprite.draw()."""
    def __init__(self, inicio_ultima_tela, config):
        self.config = config
        self.sprite = _criar_sprite_escalado(config['arquivo'], 1, config['escala'], config['espelhar'])
        self.x = float(inicio_ultima_tela + config['x'])
        self.y = float(config['y'])
        self.largura = self.sprite.width
        self.altura = self.sprite.height

    @property
    def profundidade_y(self):
        return self.y + self.altura

    # ALTERAÇÃO: banco decorativo conserva somente desenho/posição; combate pertence à DamaBoss.
    def desenhar(self):
        self.sprite.set_position(self.x, self.y)
        self.sprite.draw()


class DamaBoss:
    """ALTERAÇÃO: despertar, combate, recuo, bancos e derrota da Fase 2."""
    # ALTERAÇÃO: pontuação consultada pelo main.py e aplicador.py.
    PONTOS_TIROS_DAMA = PONTOS_TIROS_DAMA
    PONTOS_SOCO_DAMA = PONTOS_SOCO_DAMA
    PONTOS_CHUTE_DAMA = PONTOS_CHUTE_DAMA
    def __init__(self, banco):
        self.banco = banco
        # ALTERAÇÃO: mantém ambos os bancos como destinos mesmo depois de trocar o banco atual.
        self.banco_superior = banco
        self.inicio_ultima_tela = banco.x - BANCO_SUPERIOR_DIREITO['x']
        self.estado = 'sentada'
        self.direcao = DAMA_SENTADA['direcao']
        self.tempo_animacao = 0.0
        self._sprites = {}
        self._ativar_sprite('sentada', self.direcao)
        # ALTERAÇÃO: relógio do despertar não reinicia ao afastar a Noiva.
        self.despertar_iniciado = False
        self.tempo_despertar = 0.0
        self.tempo_salto_centro = 0.0
        self.inicio_salto_x = 0.0
        self.inicio_salto_pe_y = 0.0
        self.fim_salto_x = 0.0
        self.fim_salto_pe_y = 0.0
        self.invulneravel = True
        # ALTERAÇÃO: combate começa após o salto, não durante os 30 s de espera.
        self.tempo_combate = 0.0
        self.tempo_alinhada = 0.0
        self.tempo_rajada = 0.0
        self.tempo_granada = 0.0
        self.tempo_chute = 0.0
        # ALTERAÇÃO: relógios independentes para saltos de esquiva e tiro aéreo.
        self.tempo_esquiva = 0.0
        self.tempo_tiro_aereo = 0.0
        self.inicio_tiro_aereo_x = 0.0
        self.fim_tiro_aereo_x = 0.0
        self.tiros = []
        self.granadas = []
        self.explosoes = []
        self.tiros_restantes_rajada = 0
        self.tempo_entre_tiros = 0.0
        self.contador_rajadas = 0
        self.rajada_aerea = False
        self.pe_antes_rajada = 0.0
        self.tempo_salto_tiro_aereo = 0.0  # ALTERAÇÃO: relógio do arco aéreo
        self.momento_banco = 0.0
        # ALTERAÇÃO: só conta golpes aceitos por receber_dano; eventos não se repetem.
        self.evento_apos_dano = None
        self.tempo_salto_canto = 0.0
        self.banco_inferior = None
        self.banco_destino = None
        self.tempo_banco = 0.0
        self.hits_recebidos = 0
        self.ultimo_id_ataque_noiva = -1
        self.tempo_dano = 0.0
        self.estado_apos_dano = 'combatendo'
        self.tempo_pose = 0.0
        self.duracao_pose = 0.0
        # ALTERAÇÃO: imagens com escala individual; carregadas UMA VEZ em cache.
        self.sprite_projetil_direita = _criar_sprite_escalado(
            ARQUIVO_PROJETIL_DAMA, 1, ESCALA_PROJETIL_DAMA)
        self.sprite_projetil_esquerda = _criar_sprite_escalado(
            ARQUIVO_PROJETIL_DAMA, 1, ESCALA_PROJETIL_DAMA, espelhar=True)
        self.sprite_granada = _criar_sprite_escalado(
            ARQUIVO_GRANADA_DAMA, 1, ESCALA_GRANADA_DAMA)
        self.efeito_explosao = _criar_sprite_escalado(
            ARQUIVO_EXPLOSAO_DAMA, FRAMES_EXPLOSAO_DAMA, ESCALA_EXPLOSAO_DAMA)
        self.efeito_explosao.set_total_duration(int(TEMPO_EXPLOSAO * 1000))
        self.efeito_explosao.set_loop(False)
        self.sons = {}
        for nome, caminho in SONS_DAMA.items():
            if caminho and (PASTA_PROJETO / caminho).is_file():
                try:
                    self.sons[nome] = pygame.mixer.Sound(str(PASTA_PROJETO / caminho))
                except (pygame.error, OSError):
                    pass

    # ========================================================
    # ALTERAÇÃO: ETAPA 2 - UTILITÁRIOS PARA ANIMAÇÕES E COMBATE
    # ========================================================
    @property
    def centro_x(self):
        return self.x + self.largura / 2

    @property
    def centro_y(self):
        return self.y + self.altura / 2

    def _tocar(self, nome):
        if nome in self.sons:
            self.sons[nome].play()

    def _trocar_animacao(self, tipo, direcao=None, tempo_ms=1000, loop=True):
        # Não recarregar a spritesheet a cada quadro; preserva centro e pés.
        direcao = direcao or self.direcao
        if (getattr(self, '_pose_atual', None) == (tipo, direcao)):
            return
        cx, pe = self.centro_x, self.y + self.altura
        self.direcao = direcao
        self._ativar_sprite(tipo, direcao)
        self.x, self.y = cx - self.largura / 2, pe - self.altura
        self.duracao = max(0.001, tempo_ms / 1000)
        self.tempo_animacao = 0.0
        self.sprite.set_total_duration(tempo_ms)
        self.sprite.set_loop(loop)
        self.sprite.set_curr_frame(0)
        self._pose_atual = (tipo, direcao)

    def _animar_pose(self, dt):
        self.tempo_animacao += dt
        progresso = self.tempo_animacao / self.duracao
        if self.estado == 'dano':
            return
        if self.estado == 'derrotada':
            progresso = min(0.999, progresso)
        else:
            progresso %= 1.0
        self.sprite.set_curr_frame(min(self.frames - 1, int(progresso * self.frames)))

    # ========================================================
    # ALTERAÇÃO: SENTADA - LOOP CONTÍNUO (intervalo_repeticao = 0)
    # ========================================================
    def _animar_sentada(self, dt):
        if not DAMA_SENTADA['animar']:
            self.sprite.set_curr_frame(0)
            return
        self.tempo_animacao += dt
        ciclo = self.duracao + max(0.0, DAMA_SENTADA['intervalo_repeticao'])
        tempo_no_ciclo = self.tempo_animacao % max(0.001, ciclo)
        if tempo_no_ciclo >= self.duracao:
            # Mantém o quadro final durante a pausa, em vez de repetir sem intervalo.
            quadro = self.frames - 1
        else:
            quadro = min(self.frames - 1, int(tempo_no_ciclo / self.duracao * self.frames))
        self.sprite.set_curr_frame(quadro)

    def receber_dano(self):
        if self.invulneravel or self.estado in ('dano', 'derrotada'):
            return False
        self.hits_recebidos += 1
        # ALTERAÇÃO: evento pendente após a reação de dano; 20º hit prioriza a derrota.
        if self.hits_recebidos < HITS_DAMA_DERROTA:
            if HITS_PARA_RETORNO_BANCO > 0 and self.hits_recebidos % HITS_PARA_RETORNO_BANCO == 0:
                self.evento_apos_dano = 'banco'
            elif HITS_PARA_GRANADA_CANTO > 0 and self.hits_recebidos % HITS_PARA_GRANADA_CANTO == 0:
                self.evento_apos_dano = 'canto'
        self.tempo_dano = 0.0
        self.estado_apos_dano = 'combatendo'
        self.estado = 'dano'
        self.tiros_restantes_rajada = 0
        if self.rajada_aerea:
            self.y = self.pe_antes_rajada - self.altura
            self.rajada_aerea = False
        self._trocar_animacao('dano', tempo_ms=int(TEMPO_DANO_DAMA * 1000), loop=False)
        self._tocar('dano')
        return True

    def verificar_golpe_noiva(self, noiva):
        if self.invulneravel or not noiva.ataque_pode_causar_dano():
            return False
        if self.ultimo_id_ataque_noiva == noiva.id_ataque:
            return False
        if (noiva.direcao == 'direita' and self.centro_x < noiva.centro_x or
                noiva.direcao == 'esquerda' and self.centro_x > noiva.centro_x):
            return False
        distancia_x = max(0.0, abs(self.centro_x - noiva.centro_x) - 80)
        # ALTERAÇÃO: pés alinhados na pista; salto da Noiva ainda pode evitar o golpe.
        distancia_y = abs((self.y + self.altura) - (noiva.y + noiva.altura))
        if distancia_x <= noiva.alcance_ataque_atual() and distancia_y <= noiva.TOLERANCIA_GOLPE_Y:
            if self.receber_dano():
                self.ultimo_id_ataque_noiva = noiva.id_ataque
                return True
        return False

    def _iniciar_rajada(self, aerea=False):
        self.estado = 'rajada'
        self.tiros_restantes_rajada = TIROS_POR_RAJADA
        self.rajada_aerea = aerea
        self.pe_antes_rajada = self.y + self.altura
        self.tempo_salto_tiro_aereo = 0.0  # ALTERAÇÃO: novo salto começa no piso, sem teleporte
        if aerea:
            # ALTERAÇÃO: o salto aéreo atravessa parte do salão, afastando-se da Noiva.
            self.inicio_tiro_aereo_x = self.centro_x
            sinal = -1 if self.direcao == 'direita' else 1
            minimo = self.inicio_ultima_tela + self.largura / 2 + 15
            maximo = self.inicio_ultima_tela + 1600 - self.largura / 2 - 15
            self.fim_tiro_aereo_x = max(minimo, min(maximo,
                self.inicio_tiro_aereo_x + sinal * DESLOCAMENTO_X_TIRO_AEREO))
            self.tempo_tiro_aereo = 0.0
        self.tempo_entre_tiros = 0.0
        tipo = 'tiro-aereo' if aerea else 'atirando'
        self._trocar_animacao(tipo, tempo_ms=1400)
        if aerea:
            # ALTERAÇÃO: preserva a linha original dos pés após trocar de spritesheet.
            self.y = self.pe_antes_rajada - self.altura
        self.contador_rajadas += 1
        self.tempo_alinhada = 0.0
        self.tempo_rajada = 0.0

    def _criar_tiro(self, noiva=None):
        # ALTERAÇÃO: tiro normal segue horizontalmente, depois do alinhamento dos pés.
        # O tiro aéreo mira na posição da Noiva NO INSTANTE do disparo (sem perseguição).
        sinal = 1 if self.direcao == 'direita' else -1
        origem_x = self.centro_x + sinal * 65
        origem_y = self.y + self.altura - OFFSET_TIRO_ACIMA_DOS_PES
        vx = sinal * VELOCIDADE_PROJETIL_DAMA
        vy = 0.0
        if self.rajada_aerea and noiva is not None:
            dx = noiva.centro_x - origem_x
            dy = noiva.centro_y_colisao_aerea - origem_y
            modulo = max(0.001, math.hypot(dx, dy))
            vx = dx / modulo * VELOCIDADE_PROJETIL_DAMA
            vy = dy / modulo * VELOCIDADE_PROJETIL_DAMA
            sinal = 1 if vx >= 0 else -1
        self.tiros.append({'x': origem_x, 'y': origem_y,
                           'vx': vx, 'vy': vy,
                           'direcao': 'direita' if sinal > 0 else 'esquerda'})
        self._tocar('tiro')

    def _criar_granada(self, noiva):
        if noiva is None:
            return
        self.estado = 'granada'
        self.tempo_pose = 0.0
        self._trocar_animacao('granada', tempo_ms=1250, loop=False)
        self.granadas.append({'x0': self.centro_x, 'y0': self.y + self.altura * 0.5,
                              'x': self.centro_x, 'y': self.y + self.altura * 0.5,
                              'alvo_x': noiva.centro_x, 'alvo_y': noiva.centro_y + 70,
                              'tempo': 0.0})
        self.tempo_granada = 0.0
        self._tocar('granada')

    def _aplicar_recuo(self, noiva, distancia, altura=0):
        if not noiva.receber_dano():
            return
        sinal = 1 if noiva.centro_x >= self.centro_x else -1
        # Limites estritos da arena, evitando expulsar a Noiva do cenário.
        esquerda = self.inicio_ultima_tela + 12
        direita = esquerda + 1600 - noiva.idle_direita.width - 12
        destino = noiva.x + sinal * distancia
        if destino < esquerda or destino > direita:
            destino = noiva.x - sinal * distancia * 0.45  # bate na borda e volta
        noiva.x = max(esquerda, min(direita, destino))
        if altura:
            noiva.impulso_visual_dama_max = altura
            noiva.impulso_visual_dama = 0.0
            noiva.tempo_impulso_dama = 0.0

    def _atualizar_projeteis(self, dt, noiva):
        for tiro in self.tiros[:]:
            tiro['x'] += tiro['vx'] * dt
            tiro['y'] += tiro.get('vy', 0.0) * dt  # ALTERAÇÃO: tiro aéreo também tem velocidade vertical.
            if noiva is not None and (abs(tiro['x'] - noiva.centro_x) < noiva.METADE_LARGURA_HITBOX + RAIO_PROJETIL_DAMA and
                   abs(tiro['y'] - noiva.centro_y_colisao_aerea) < noiva.METADE_ALTURA_HITBOX + RAIO_PROJETIL_DAMA):
                self._aplicar_recuo(noiva, RECUO_CHUTE_NOIVA)
                self.tiros.remove(tiro)
            elif not (self.inicio_ultima_tela - 100 <= tiro['x'] <=
                      self.inicio_ultima_tela + 1700):
                self.tiros.remove(tiro)

        for granada in self.granadas[:]:
            granada['tempo'] += dt
            t = min(1.0, granada['tempo'] / TEMPO_VOO_GRANADA)
            granada['x'] = granada['x0'] + (granada['alvo_x'] - granada['x0']) * t
            granada['y'] = granada['y0'] + (granada['alvo_y'] - granada['y0']) * t - 4 * 95 * t * (1-t)
            if t >= 1.0:
                self.explosoes.append({'x': granada['x'], 'y': granada['y'],
                                       'tempo': 0.0, 'atingiu': False})
                self.granadas.remove(granada)
                self._tocar('explosao')

        for explosao in self.explosoes[:]:
            explosao['tempo'] += dt
            if not explosao['atingiu'] and noiva is not None:
                if math.hypot(explosao['x'] - noiva.centro_x,
                              explosao['y'] - noiva.centro_y_colisao_aerea) <= RAIO_EXPLOSAO + 35:
                    self._aplicar_recuo(noiva, RECUO_EXPLOSAO_NOIVA, ALTURA_IMPULSO_EXPLOSAO)
                explosao['atingiu'] = True  # exatamente um teste por explosão
            if explosao['tempo'] >= TEMPO_EXPLOSAO:
                self.explosoes.remove(explosao)

    def _iniciar_salto_banco(self, banco):
        self.banco_destino = banco
        self.inicio_salto_x = self.centro_x
        self.inicio_salto_pe_y = self.y + self.altura
        self.fim_salto_x = banco.x + banco.largura / 2 + DAMA_SENTADA['x_offset']
        self.fim_salto_pe_y = banco.y + banco.altura * DAMA_SENTADA['altura_assento'] + DAMA_SENTADA['y_offset']
        self.tempo_salto_centro = 0.0
        self.estado = 'saltando_banco'
        self.invulneravel = True
        # ALTERAÇÃO: banco esquerdo olha para DIREITA; banco direito olha para ESQUERDA.
        direcao_banco = 'direita' if banco is self.banco_inferior else 'esquerda'
        self._trocar_animacao('salto', direcao_banco,
                             tempo_ms=int(DURACAO_SALTO_BANCO * 1000), loop=False)

    # ========================================================
    # ALTERAÇÃO: após 5 hits, salta ao canto mais distante da Noiva.
    # A escolha considera os QUATRO cantos jogáveis da tela final.
    # ========================================================
    def _iniciar_salto_canto(self, noiva):
        if noiva is None:
            return
        margem = max(self.largura / 2 + 12, MARGEM_CANTO_X)
        esquerda = self.inicio_ultima_tela
        candidatos_x = (esquerda + margem, esquerda + 1600 - margem)
        pe_min = self.altura + 12  # sprite inteiro dentro da tela no pouso
        candidatos_pe_y = (max(pe_min, PE_CANTO_SUPERIOR_Y),
                           max(pe_min, min(888, PE_CANTO_INFERIOR_Y)))
        # Usa o ponto dos pés da Noiva para comparar distâncias reais no plano da arena.
        pe_noiva = noiva.y + noiva.altura
        destino_x, destino_pe_y = max(
            ((cx, py) for cx in candidatos_x for py in candidatos_pe_y),
            key=lambda destino: (destino[0] - noiva.centro_x) ** 2
                                + (destino[1] - pe_noiva) ** 2
        )
        self.inicio_salto_x = self.centro_x
        self.inicio_salto_pe_y = self.y + self.altura
        self.fim_salto_x = destino_x
        self.fim_salto_pe_y = destino_pe_y
        self.tempo_salto_canto = 0.0
        self.estado = 'saltando_canto'
        self.invulneravel = True
        direcao = 'direita' if destino_x > self.centro_x else 'esquerda'
        self._trocar_animacao('salto', direcao,
                             tempo_ms=int(DURACAO_SALTO_CANTO * 1000), loop=False)

    # ========================================================
    # ALTERAÇÃO: salto de esquiva por tempo; não lança granada.
    # Dá tempo para a Noiva se reposicionar entre os ataques.
    # ========================================================
    def _iniciar_salto_esquiva(self, noiva):
        inicio = self.inicio_ultima_tela
        cx = self.centro_x
        pe = self.y + self.altura
        sinal = -1 if noiva.centro_x >= cx else 1
        x_min = inicio + self.largura / 2 + 15
        x_max = inicio + 1600 - self.largura / 2 - 15
        destino = max(x_min, min(x_max, cx + sinal * DISTANCIA_SALTO_ESQUIVA))
        # Se o deslocamento for barrado pela borda, salta para o lado oposto.
        if abs(destino - cx) < 90:
            destino = max(x_min, min(x_max, cx - sinal * DISTANCIA_SALTO_ESQUIVA))
        self.inicio_salto_x = cx
        self.inicio_salto_pe_y = pe
        self.fim_salto_x = destino
        self.fim_salto_pe_y = pe
        self.tempo_salto_esquiva = 0.0
        self.tempo_esquiva = 0.0
        self.estado = 'saltando_esquiva'
        self.invulneravel = True
        self._trocar_animacao('salto', 'direita' if destino >= cx else 'esquerda',
                             tempo_ms=int(DURACAO_SALTO_ESQUIVA * 1000), loop=False)

    def _atualizar_combate(self, dt, noiva):
        # Mesmo durante a pose de dano e nos bancos, projéteis anteriores seguem ativos.
        self._atualizar_projeteis(dt, noiva)
        if self.estado == 'derrotada':
            self._animar_pose(dt)
            return
        if self.estado == 'dano':
            self.tempo_dano += dt
            if self.tempo_dano >= TEMPO_DANO_DAMA:
                if self.hits_recebidos >= HITS_DAMA_DERROTA:
                    self.estado = 'derrotada'
                    self.evento_apos_dano = None
                    self.invulneravel = True
                    self._trocar_animacao('derrota', tempo_ms=3000, loop=False)
                    self._tocar('derrota')
                elif self.evento_apos_dano == 'canto' and noiva is not None:
                    # ALTERAÇÃO: a granada só é lançada ao ATERRISSAR no canto.
                    self.evento_apos_dano = None
                    self._iniciar_salto_canto(noiva)
                elif self.evento_apos_dano == 'banco':
                    self.evento_apos_dano = None
                    bancos = [self.banco_superior]
                    if self.banco_inferior is not None:
                        bancos.append(self.banco_inferior)
                    self._iniciar_salto_banco(random.choice(bancos))
                else:
                    self.estado = 'combatendo'
                    self._trocar_animacao('andando', tempo_ms=DURACAO_ANIMACAO_ANDANDO_MS)
            return

        # ALTERAÇÃO: salto frequente sem ataque especial; invulnerável só no trajeto.
        if self.estado == 'saltando_esquiva':
            self.tempo_salto_esquiva += dt
            t = min(1.0, self.tempo_salto_esquiva / max(0.001, DURACAO_SALTO_ESQUIVA))
            cx = self.inicio_salto_x + (self.fim_salto_x - self.inicio_salto_x) * t
            pe = self.inicio_salto_pe_y + (self.fim_salto_pe_y - self.inicio_salto_pe_y) * t
            self.x = cx - self.largura / 2
            self.y = pe - self.altura - 4 * ALTURA_SALTO_ESQUIVA * t * (1 - t)
            self.sprite.set_curr_frame(min(self.frames - 1, int(t * self.frames)))
            if t >= 1.0:
                self.estado = 'combatendo'
                self.invulneravel = False
                self._trocar_animacao('andando', tempo_ms=DURACAO_ANIMACAO_ANDANDO_MS)
            return

        # ALTERAÇÃO: salto para um dos cantos após cada 5 hits aceitos.
        if self.estado == 'saltando_canto':
            self.tempo_salto_canto += dt
            t = min(1.0, self.tempo_salto_canto / max(0.001, DURACAO_SALTO_CANTO))
            cx = self.inicio_salto_x + (self.fim_salto_x - self.inicio_salto_x) * t
            pe = self.inicio_salto_pe_y + (self.fim_salto_pe_y - self.inicio_salto_pe_y) * t
            self.x = cx - self.largura / 2
            self.y = pe - self.altura - 4 * ALTURA_SALTO_CANTO * t * (1 - t)
            self.sprite.set_curr_frame(min(self.frames - 1, int(t * self.frames)))
            if t >= 1.0:
                self.invulneravel = False
                self.direcao = ('esquerda' if noiva is not None and noiva.centro_x < self.centro_x
                               else 'direita')
                # ALTERAÇÃO: registra alvo da Noiva APENAS aqui, no lançamento.
                self._criar_granada(noiva)
            return

        if self.estado == 'saltando_banco':
            self.tempo_salto_centro += dt
            t = min(1.0, self.tempo_salto_centro / DURACAO_SALTO_BANCO)
            cx = self.inicio_salto_x + (self.fim_salto_x-self.inicio_salto_x)*t
            pe = self.inicio_salto_pe_y + (self.fim_salto_pe_y-self.inicio_salto_pe_y)*t
            self.x = cx-self.largura/2
            self.y = pe-self.altura-4*ALTURA_ARCO_SALTO*t*(1-t)
            self.sprite.set_curr_frame(min(self.frames-1,int(t*self.frames)))
            if t >= 1.0:
                self.banco = self.banco_destino
                self.estado = 'no_banco'
                self.tempo_banco = 0.0
                # ALTERAÇÃO: sentada à esquerda = direita; sentada à direita = esquerda.
                self.direcao = 'direita' if self.banco is self.banco_inferior else 'esquerda'
                self._ativar_sprite('sentada', self.direcao)
                self._pose_atual = ('sentada', self.direcao)
                self.duracao = DAMA_SENTADA['duracao_ms'] / 1000
                self.tempo_animacao = 0.0
            return

        if self.estado == 'no_banco':
            self.tempo_banco += dt
            # ALTERAÇÃO: loop contínuo da spritesheet sentada, sem pausa.
            self._animar_sentada(dt)
            if self.tempo_banco >= TEMPO_NO_BANCO:
                # Retorna ao centro do salão; permanece invulnerável no salto.
                self._iniciar_salto_centro()
            return

        if self.estado == 'saltando_centro':
            return

        if self.estado not in ('combatendo','rajada','granada','chute'):
            return

        # Conta tempo APENAS durante combate; os 30 s iniciais não entram aqui.
        self.tempo_combate += dt
        self.tempo_rajada += dt
        self.tempo_granada += dt
        self.tempo_chute += dt
        self.tempo_esquiva += dt
        self.tempo_tiro_aereo += dt
        # ALTERAÇÃO: não há mais retorno automático ao banco por tempo.
        # O salto é disparado em receber_dano(), a cada 8 hits aceitos.
        self._animar_pose(dt)

        if self.estado == 'rajada':
            # ALTERAÇÃO: durante a rajada aérea, sobe e desce em parábola,
            # preservando a posição dos pés da Dama quando está no chão.
            if self.rajada_aerea:
                self.tempo_salto_tiro_aereo += dt
                progresso_aereo = min(1.0, self.tempo_salto_tiro_aereo / max(0.001, DURACAO_SALTO_TIRO_AEREO))
                altura_aerea = 4 * ALTURA_SALTO_TIRO_AEREO * progresso_aereo * (1 - progresso_aereo)
                self.y = self.pe_antes_rajada - self.altura - altura_aerea
                # ALTERAÇÃO: deslocamento lateral durante a parábola, não teleporte.
                self.x = (self.inicio_tiro_aereo_x
                          + (self.fim_tiro_aereo_x - self.inicio_tiro_aereo_x) * progresso_aereo
                          - self.largura / 2)
            self.tempo_entre_tiros -= dt
            if self.tiros_restantes_rajada and self.tempo_entre_tiros <= 0:
                self._criar_tiro(noiva)
                self.tiros_restantes_rajada -= 1
                self.tempo_entre_tiros = INTERVALO_ENTRE_TIROS_DAMA
            # ALTERAÇÃO: a rajada aérea não termina antes de aterrissar.
            terminou_tiros = self.tiros_restantes_rajada == 0 and self.tempo_entre_tiros <= 0
            aterrissou = not self.rajada_aerea or self.tempo_salto_tiro_aereo >= DURACAO_SALTO_TIRO_AEREO
            if terminou_tiros and aterrissou:
                if self.rajada_aerea:
                    self.y = self.pe_antes_rajada - self.altura
                    self.rajada_aerea = False
                self.estado = 'combatendo'
            return
        if self.estado == 'granada':
            self.tempo_pose += dt
            if self.tempo_pose >= 1.25:
                self.estado = 'combatendo'
            return
        if self.estado == 'chute':
            self.tempo_pose += dt
            if self.tempo_pose >= 0.55:
                self.estado = 'combatendo'
            return
        if noiva is None:
            return
        self.direcao = 'esquerda' if noiva.centro_x < self.centro_x else 'direita'
        dx = noiva.centro_x - self.centro_x
        # ALTERAÇÃO: a referência de profundidade é a BASE (pés) de cada sprite,
        # não seu centro visual, que varia muito com a escala da Dama.
        dy = (noiva.y + noiva.altura) - (self.y + self.altura)
        # ALTERAÇÃO: saltos ocasionais permitem à Noiva respirar/recuar.
        if self.tempo_esquiva >= INTERVALO_SALTO_ESQUIVA:
            self._iniciar_salto_esquiva(noiva)
            return
        # ALTERAÇÃO: tiro aéreo tem gatilho próprio (intervalo + distância horizontal),
        # e pode sair mesmo sem alinhamento em Y; projéteis são mirados no disparo.
        if (ALTERNAR_TIRO_AEREO and self.tempo_tiro_aereo >= INTERVALO_TIRO_AEREO
                and abs(dx) >= DISTANCIA_MIN_TIRO_AEREO):
            self._iniciar_rajada(aerea=True)
            return
        if (abs(dx) <= DISTANCIA_CHUTE_DAMA and abs(dy) <= TOLERANCIA_CHUTE_Y
                and self.tempo_chute >= INTERVALO_CHUTE_DAMA):
            self.estado = 'chute'
            self.tempo_pose = 0.0
            self.tempo_chute = 0.0
            # ALTERAÇÃO: usa chute se existir; senão mantém pose provisória.
            arquivo_chute = PASTA_PROJETO / f'assets/personagens/dama/dama-chute-{self.direcao}.png'
            tipo_chute = 'chute' if arquivo_chute.is_file() else 'andando'
            self._trocar_animacao(tipo_chute, self.direcao, tempo_ms=550)
            self._aplicar_recuo(noiva, RECUO_CHUTE_NOIVA)
            return
        # ALTERAÇÃO: granada não é mais lançada por intervalo fixo;
        # somente ao aterrissar após o salto ao canto (5 hits).
        if abs(dy) <= TOLERANCIA_TIRO_Y:
            self.tempo_alinhada += dt
        else:
            self.tempo_alinhada = 0.0
        if (self.tempo_alinhada >= TEMPO_ALINHADA_PARA_ATIRAR
                and self.tempo_rajada >= INTERVALO_RAJADA):
            # ALTERAÇÃO: tiro NORMAL apenas por alinhamento dos pés e retardo.
            # O aéreo é disparado por seu próprio temporizador acima.
            self._iniciar_rajada(aerea=False)
            return
        if abs(dx) > DISTANCIA_PARADA_DAMA:
            self.x += math.copysign(min(abs(dx), VELOCIDADE_DAMA_X * dt), dx)
        if abs(dy) > TOLERANCIA_TIRO_Y * 0.5:
            self.y += math.copysign(min(abs(dy), VELOCIDADE_DAMA_Y * dt), dy)
        # Limita a Dama ao espaço do salão.
        esquerda = self.inicio_ultima_tela
        self.x = max(esquerda, min(self.x, esquerda + 1600 - self.largura))
        self.y = max(260, min(self.y, 900-self.altura))
        self._trocar_animacao('andando', self.direcao, tempo_ms=DURACAO_ANIMACAO_ANDANDO_MS)

    # ALTERAÇÃO: efeitos em coordenadas do mundo, convertidos para o buffer PPlay.
    def desenhar_efeitos(self, tela, camera_x):
        # ALTERAÇÃO: os sprites usam coordenadas do MUNDO;
        # Sprite.draw() já aplica a câmera nativa PPlay 2.1.
        for tiro in self.tiros:
            sprite_tiro = (self.sprite_projetil_esquerda if tiro['direcao'] == 'esquerda'
                           else self.sprite_projetil_direita)
            sprite_tiro.set_position(tiro['x'] - sprite_tiro.width / 2,
                                    tiro['y'] - sprite_tiro.height / 2)
            sprite_tiro.draw()
        for granada in self.granadas:
            self.sprite_granada.set_position(granada['x'] - self.sprite_granada.width / 2,
                                            granada['y'] - self.sprite_granada.height / 2)
            self.sprite_granada.draw()
        for explosao in self.explosoes:
            # ALTERAÇÃO: cada explosão mantém seu próprio tempo (9 quadros).
            proporcao = min(0.999, explosao['tempo'] / TEMPO_EXPLOSAO)
            self.efeito_explosao.set_curr_frame(int(proporcao * FRAMES_EXPLOSAO_DAMA))
            self.efeito_explosao.set_position(explosao['x'] - self.efeito_explosao.width / 2,
                                              explosao['y'] - self.efeito_explosao.height / 2)
            self.efeito_explosao.draw()

    def _ativar_sprite(self, estado, direcao):
        chave = (estado, direcao)
        if chave not in self._sprites:
            config = DAMA_ANIMACOES[estado]
            # ALTERAÇÃO: cada tipo de sprite tem sua escala ajustável.
            self._sprites[chave] = _criar_sprite_escalado(
                f'assets/personagens/dama/dama-{estado}-{direcao}.png',
                config['frames'], config['escala'] * (DAMA_SENTADA['escala'] if estado == 'sentada' else 1.0)
            )
        self.sprite = self._sprites[chave]
        self.frames = DAMA_ANIMACOES[estado]['frames']
        self.duracao = max(0.001, DAMA_SENTADA['duracao_ms'] / 1000)
        self.largura = self.sprite.width
        self.altura = self.sprite.height
        self.x = self.banco.x + self.banco.largura / 2 - self.largura / 2 + DAMA_SENTADA['x_offset']
        # ALTERAÇÃO: deslocamento relativo ao banco para ajustar a pose sentada.
        self.y = self.banco.y + self.banco.altura * DAMA_SENTADA['altura_assento'] - self.altura + DAMA_SENTADA['y_offset']
        self.sprite.set_curr_frame(0)

    @property
    def profundidade_y(self):
        # ALTERAÇÃO: preserva sobreposição com o banco enquanto está sentada;
        # no salão, usa a linha dos pés, independente da escala do sprite.
        if self.estado in ('sentada', 'aguardando', 'no_banco'):
            return self.banco.profundidade_y + DAMA_SENTADA['profundidade_offset']
        if self.estado == 'saltando_centro':
            # Na trajetória, a linha do chão interpola entre banco e pista.
            progresso = min(1.0, self.tempo_salto_centro / max(0.001, DURACAO_SALTO_CENTRO))
            return self.inicio_salto_pe_y + (self.fim_salto_pe_y - self.inicio_salto_pe_y) * progresso
        return self.y + self.altura

    # ========================================================
    # ALTERAÇÃO: o primeiro contato inicia a espera uma única vez.
    # ========================================================
    def _iniciar_salto_centro(self):
        self.estado = 'saltando_centro'
        self.tempo_salto_centro = 0.0
        # Guarda posição visual atual para impedir saltos bruscos de escala.
        self.inicio_salto_x = self.x + self.largura / 2
        self.inicio_salto_pe_y = self.y + self.altura
        self.fim_salto_x = self.inicio_ultima_tela + DESTINO_SALTO_X
        self.fim_salto_pe_y = DESTINO_SALTO_PE_Y
        self.direcao = 'esquerda' if self.fim_salto_x < self.inicio_salto_x else 'direita'
        self._ativar_sprite('salto', self.direcao)
        self.duracao = max(0.001, DURACAO_ANIMACAO_SALTO_MS / 1000)
        self.sprite.set_loop(False)
        self.sprite.set_curr_frame(0)
        # O início da trajetória mantém o mesmo centro e a mesma base visual.
        self.x = self.inicio_salto_x - self.largura / 2
        self.y = self.inicio_salto_pe_y - self.altura

    def atualizar(self, dt, noiva=None):
        # ALTERAÇÃO: estado sentada continua animando durante a espera de 30s.
        if self.estado in ('sentada', 'aguardando'):
            # ALTERAÇÃO: animação sentada em loop contínuo, sem espera entre ciclos.
            self._animar_sentada(dt)
            if not self.despertar_iniciado and noiva is not None:
                distancia_x = abs(noiva.centro_x - (self.x + self.largura / 2))
                if distancia_x <= DISTANCIA_ATIVACAO:
                    self.despertar_iniciado = True
                    self.estado = 'aguardando'
                    self.tempo_despertar = 0.0
            elif self.despertar_iniciado:
                self.tempo_despertar += dt
                if self.tempo_despertar >= TEMPO_DESPERTAR:
                    self._iniciar_salto_centro()
            return

        if self.estado == 'saltando_centro':
            self.tempo_salto_centro += dt
            progresso = min(1.0, self.tempo_salto_centro / max(0.001, DURACAO_SALTO_CENTRO))
            # Movimento sem depender do FPS, com trajetória parabólica.
            centro_x = self.inicio_salto_x + (self.fim_salto_x - self.inicio_salto_x) * progresso
            base_y = self.inicio_salto_pe_y + (self.fim_salto_pe_y - self.inicio_salto_pe_y) * progresso
            arco = 4 * ALTURA_ARCO_SALTO * progresso * (1 - progresso)
            self.x = centro_x - self.largura / 2
            self.y = base_y - arco - self.altura
            quadro = min(self.frames - 1, int(progresso * self.frames))
            self.sprite.set_curr_frame(quadro)
            if progresso >= 1.0:
                self.estado = 'combatendo'
                self.invulneravel = False
                self._pose_atual = None
                self.tempo_animacao = 0.0
                # ALTERAÇÃO: no salão, a Dama passará a perseguir e atacar.
                # Primeiro quadro da caminhada como pose provisória em pé.
                centro_x = self.fim_salto_x
                base_y = self.fim_salto_pe_y
                self._ativar_sprite('andando', self.direcao)
                self.sprite.set_curr_frame(0)
                self.x = centro_x - self.largura / 2
                self.y = base_y - self.altura
            return

        # ALTERAÇÃO: combate e retorno aos bancos preservam os estados anteriores.
        self._atualizar_combate(dt, noiva)

    def desenhar(self):
        self.sprite.set_position(self.x, self.y)
        self.sprite.draw()
