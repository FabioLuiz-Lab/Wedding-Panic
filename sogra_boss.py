import math
import random

from PPlay.sprite import Sprite


# ============================================================
# CLASSE SOGRA BOSS - FINAL DA FASE 1
# ============================================================

class SograBoss:

    # --------------------------------------------------------
    # ANIMAÇÕES (AJUSTÁVEIS)
    # --------------------------------------------------------

    FRAMES_IDLE = 36
    FRAMES_ATAQUE = 16
    TEMPO_IDLE = 4000          # ms para os 36 quadros
    TEMPO_ATAQUE = 3000        # ms para os 16 quadros

    # --------------------------------------------------------
    # MOVIMENTO CIRCULAR NA METADE DIREITA DA TELA
    # --------------------------------------------------------

    PERIODO_ORBITA = 5.5       # segundos por volta completa (lento)
    RAIO_HORIZONTAL = 900      # pixels de deslocamento na horizontal
    RAIO_VERTICAL = 900         # pixels de deslocamento na vertical
    MARGEM_LATERAL = 10        # pixels de folga nas bordas da área permitida
    # ALTERAÇÃO: restringe a órbita ao setor direito da metade da Boss.
    # A fração é da largura VISÍVEL: 0.70 = começa em 70% da tela.
    # Mantém a cabeça longe da posição inicial da Noiva na arena.
    INICIO_AREA_X = 0.0
    LIMITE_SUPERIOR = 0     # a cabeça nunca fica mais alta que y=200
    MARGEM_INFERIOR = 0       # distância mínima até a borda inferior

    # --------------------------------------------------------
    # ATAQUES (AJUSTÁVEIS)
    # --------------------------------------------------------

    INTERVALO_ATAQUE_MIN = 2.0  # ALTERAÇÃO: menor espera para disparos recorrentes
    INTERVALO_ATAQUE_MAX = 3.5  # ALTERAÇÃO: evita longos períodos sem bolas de fogo

    # ALTERAÇÃO: novo sprite circular da bola de fogo; 9 quadros, sem rotação.
    ARQUIVO_BOLA_FOGO = "assets/objetos/bola-fogo.png"
    FRAMES_BOLA_FOGO = 9
    TEMPO_BOLA_FOGO = 1350      # ALTERAÇÃO: 9 quadros, preservando 150 ms por quadro
    VELOCIDADE_BOLA_FOGO = 380  # pixels por segundo (usa dt)
    RAIO_COLISAO_BOLA = 35     # raio lógico, independente do desenho circular
    MOMENTO_DISPARO = 0.50     # fração da animação de ataque (0.5 = metade)
    MARGEM_SAIDA_BOLA = 380    # espera o sprite todo sair da área visível

    # --------------------------------------------------------
    # ALTERAÇÃO: DANO E DERROTA DA BOSS (AJUSTÁVEIS)
    # --------------------------------------------------------
    HITS_PARA_DERROTAR = 8    # número de tiros válidos para vencer
    # ALTERAÇÃO: subida rápida após cada hit, até acima da Noiva.
    VELOCIDADE_RECUO_APOS_HIT = 850.0
    DISTANCIA_ACIMA_NOIVA = 60.0
    DURACAO_RETORNO_ORBITA = 1.2
    TEMPO_DANO_BOSS = 0.65     # segundos imóvel, mostrando o sprite de dano
    TEMPO_DERROTA = 3.0       # segundos do efeito de balão esvaziando
    FRAMES_DERROTA = 24      # quadros da spritesheet reduzida progressivamente
    INTERVALO_ZIGUEZAGUE = 0.14  # segundos entre mudanças de direção
    VELOCIDADE_DERROTA_X = 330  # px/s: intensidade horizontal
    VELOCIDADE_DERROTA_Y = 200  # px/s: intensidade vertical

    def __init__(self):
        # ALTERAÇÃO: nomes exatamente como aparecem nos assets originais.
        # A palavra "atque" está assim no nome dos arquivos fornecidos.
        pasta = "assets/personagens/sogra-boss/"
        self.idle_direita = Sprite(pasta + "sogra-boss-idle-direita.png", self.FRAMES_IDLE)
        self.idle_esquerda = Sprite(pasta + "sogra-boss-idle-esquerda.png", self.FRAMES_IDLE)
        self.ataque_direita = Sprite(pasta + "sogra-boss-atque-direita.png", self.FRAMES_ATAQUE)
        self.ataque_esquerda = Sprite(pasta + "sogra-boss-atque-esquerda.png", self.FRAMES_ATAQUE)
        # ALTERAÇÃO: sprite já fornecido; exibido durante a pausa após cada hit.
        self.dano_direita = Sprite(pasta + "sogra-boss-dano-direita.png", 1)
        self.dano_esquerda = Sprite(pasta + "sogra-boss-dano-esquerda.png", 1)
        # ALTERAÇÃO: frames gerados a partir do sprite de dano original,
        # reduzindo gradualmente a Sogra, sem precisar alterar PPlay/Sprite.
        self.derrota_direita = Sprite(pasta + "sogra-boss-derrota-direita.png", self.FRAMES_DERROTA)
        self.derrota_esquerda = Sprite(pasta + "sogra-boss-derrota-esquerda.png", self.FRAMES_DERROTA)
        self.derrota_direita.set_total_duration(int(self.TEMPO_DERROTA * 1000))
        self.derrota_esquerda.set_total_duration(int(self.TEMPO_DERROTA * 1000))
        self.derrota_direita.set_loop(False)
        self.derrota_esquerda.set_loop(False)

        self.idle_direita.set_total_duration(self.TEMPO_IDLE)
        self.idle_esquerda.set_total_duration(self.TEMPO_IDLE)
        self.ataque_direita.set_total_duration(self.TEMPO_ATAQUE)
        self.ataque_esquerda.set_total_duration(self.TEMPO_ATAQUE)
        self.ataque_direita.set_loop(False)
        self.ataque_esquerda.set_loop(False)

        self.ativa = False
        self.estado = "idle"
        self.direcao = "esquerda"  # olha inicialmente para a Noiva
        self.tempo_estado = 0.0
        self.tempo_proximo_ataque = random.uniform(
            self.INTERVALO_ATAQUE_MIN, self.INTERVALO_ATAQUE_MAX
        )
        self.tempo_orbita = 0.0
        self.x = 0.0              # posição no MUNDO (para Sprite.draw + Camera)
        self.y = 0.0
        # ALTERAÇÃO: lista de projéteis independentes da posição futura da Noiva.
        self.bolas_fogo = []
        self.bola_disparada = False
        # ALTERAÇÃO: controla a remoção do primeiro projétil para liberar o aplicador.
        self.total_bolas_criadas = 0
        self.primeira_bola_encerrada = False
        # ALTERAÇÃO: golpes válidos, pausa de dano e sequência final de derrota.
        self.hits_recebidos = 0
        self.tempo_dano_boss = 0.0
        # ALTERAÇÃO: controles do reposicionamento após receber um tiro.
        self.retorno_orbita = 0.0
        self.deslocamento_retorno_x = 0.0
        self.deslocamento_retorno_y = 0.0
        self.derrotada = False
        self.tempo_derrota = 0.0
        self.tempo_ziguezague = 0.0
        self.velocidade_derrota_x = 0.0
        self.velocidade_derrota_y = 0.0
        self.camera_x_atual = 0.0
        self.largura_tela_atual = 0
        self.altura_tela_atual = 0

    def ativar(self):
        # ALTERAÇÃO: boss só começa seus temporizadores na última tela da fase.
        if self.ativa or self.derrotada:
            return
        self.ativa = True
        self.estado = "idle"
        self.tempo_estado = 0.0
        self.tempo_orbita = 0.0
        self.tempo_proximo_ataque = random.uniform(
            self.INTERVALO_ATAQUE_MIN, self.INTERVALO_ATAQUE_MAX
        )
        self.bolas_fogo.clear()
        self.bola_disparada = False
        self.total_bolas_criadas = 0
        self.primeira_bola_encerrada = False
        self.hits_recebidos = 0
        self.tempo_dano_boss = 0.0
        # ALTERAÇÃO: reinicia o recuo após hit em cada nova partida.
        self.retorno_orbita = 0.0
        self.deslocamento_retorno_x = 0.0
        self.deslocamento_retorno_y = 0.0
        self.tempo_derrota = 0.0
        self.tempo_ziguezague = 0.0
        self.idle_direita.play()
        self.idle_esquerda.play()

    def _iniciar_ataque(self):
        self.estado = "atacando"
        self.tempo_estado = 0.0
        self.bola_disparada = False  # ALTERAÇÃO: um tiro por ataque.
        self.ataque_direita.stop()
        self.ataque_esquerda.stop()
        self.ataque_direita.play()
        self.ataque_esquerda.play()

    def _finalizar_ataque(self):
        self.estado = "idle"
        self.tempo_estado = 0.0
        self.tempo_proximo_ataque = random.uniform(
            self.INTERVALO_ATAQUE_MIN, self.INTERVALO_ATAQUE_MAX
        )
        self.idle_direita.play()
        self.idle_esquerda.play()

    # ========================================================
    # ALTERAÇÃO: CADA ACERTO VÁLIDO CONGELA A BOSS TEMPORARIAMENTE
    # ========================================================

    def receber_dano(self):
        # Não pontua golpes que cheguem durante a animação de dano.
        if not self.ativa or self.derrotada or self.estado in ("dano", "derrota"):
            return False
        self.hits_recebidos += 1
        self.estado = "dano"
        self.tempo_dano_boss = 0.0
        self.tempo_estado = 0.0
        # Interrompe a animação de ataque, sem disparar outra bola.
        self.bola_disparada = False
        return True

    def _iniciar_derrota(self):
        # ALTERAÇÃO: inicia o voo descontrolado; não pode disparar nem tomar hits.
        self.estado = "derrota"
        self.tempo_derrota = 0.0
        self.tempo_ziguezague = self.INTERVALO_ZIGUEZAGUE
        self.bolas_fogo.clear()   # sem projéteis da Sogra após a vitória
        self.derrota_direita.stop()
        self.derrota_esquerda.stop()
        self.derrota_direita.play()
        self.derrota_esquerda.play()

    def _atualizar_derrota(self, dt):
        self.tempo_derrota += dt
        self.tempo_ziguezague += dt
        if self.tempo_ziguezague >= self.INTERVALO_ZIGUEZAGUE:
            self.tempo_ziguezague = 0.0
            # ALTERAÇÃO: muda repetidamente a direção, como balão esvaziando.
            self.velocidade_derrota_x = random.uniform(-1, 1) * self.VELOCIDADE_DERROTA_X
            self.velocidade_derrota_y = random.uniform(-1, 1) * self.VELOCIDADE_DERROTA_Y - 70
        self.x += self.velocidade_derrota_x * dt
        self.y += self.velocidade_derrota_y * dt
        # Não deixa o efeito escapar totalmente antes de terminar.
        largura_sprite = self.derrota_direita.width
        altura_sprite = self.derrota_direita.height
        x_min = self.camera_x_atual - largura_sprite / 2
        x_max = self.camera_x_atual + self.largura_tela_atual - largura_sprite / 2
        self.x = max(x_min, min(self.x, x_max))
        self.y = max(-altura_sprite / 2, min(self.y, self.altura_tela_atual - altura_sprite / 2))
        if self.tempo_derrota >= self.TEMPO_DERROTA:
            self.ativa = False
            self.derrotada = True

    def _sprite_ativo(self):
        if self.estado == "dano":
            return self.dano_esquerda if self.direcao == "esquerda" else self.dano_direita
        if self.estado == "derrota":
            return self.derrota_esquerda if self.direcao == "esquerda" else self.derrota_direita
        if self.estado == "atacando":
            # ALTERAÇÃO: os sprites de ataque foram renomeados e agora estão
            # com a mesma orientação dos sprites idle (direita/esquerda).
            # Não inverter a seleção: a direção segue a posição da Noiva.
            return self.ataque_esquerda if self.direcao == "esquerda" else self.ataque_direita
        return self.idle_esquerda if self.direcao == "esquerda" else self.idle_direita

    # ========================================================
    # ALTERAÇÃO: DISPARO INSTANTÂNEO EM DIREÇÃO À NOIVA
    # ========================================================

    def _criar_bola_fogo(self, noiva):
        # Usa o centro da cabeça no INSTANTE do disparo.
        sprite_boss = self._sprite_ativo()
        largura_referencia = max(self.idle_direita.width, self.ataque_direita.width)
        ajuste_x = (largura_referencia - sprite_boss.width) / 2
        origem_x = self.x + ajuste_x + sprite_boss.width / 2
        origem_y = self.y + sprite_boss.height * 0.65

        dx = noiva.centro_x - origem_x
        dy = noiva.centro_y - origem_y
        distancia = math.hypot(dx, dy)
        if distancia < 0.001:
            # Fallback raro: se os centros coincidirem, dispara para a esquerda.
            dx, dy, distancia = -1.0, 0.0, 1.0

        vx = dx / distancia * self.VELOCIDADE_BOLA_FOGO
        vy = dy / distancia * self.VELOCIDADE_BOLA_FOGO

        # ALTERAÇÃO: a nova bola é circular e dispensa rotação.
        # O vetor vx/vy é calculado somente no disparo.

        bola = Sprite(self.ARQUIVO_BOLA_FOGO, self.FRAMES_BOLA_FOGO)
        bola.set_total_duration(self.TEMPO_BOLA_FOGO)
        bola.play()
        # Cada bola tem seu próprio sprite e seu próprio vetor de velocidade.
        self.total_bolas_criadas += 1  # ALTERAÇÃO: identifica a primeira bola disparada.
        self.bolas_fogo.append({
            "primeira": self.total_bolas_criadas == 1,
            "sprite": bola,
            "x": origem_x,
            "y": origem_y,
            "vx": vx,
            "vy": vy,
        })

    def _atualizar_bolas_fogo(self, noiva, dt):
        for bola in self.bolas_fogo[:]:
            # ALTERAÇÃO: NÃO recalcula vx/vy; a bola não persegue a Noiva.
            bola["x"] += bola["vx"] * dt
            bola["y"] += bola["vy"] * dt
            bola["sprite"].update()

            # Colisão circular contra a hitbox retangular da Noiva.
            # Este teste não depende do retângulo visual girado do sprite.
            metade_largura = noiva.METADE_LARGURA_HITBOX
            metade_altura = noiva.METADE_ALTURA_HITBOX
            distancia_x = max(0.0, abs(bola["x"] - noiva.centro_x) - metade_largura)
            # ALTERAÇÃO: considera a altura do salto ao testar o impacto.
            # centro_y continua reservado para a posição no solo / mira.
            distancia_y = max(0.0, abs(bola["y"] - noiva.centro_y_colisao_aerea) - metade_altura)
            colisao = (distancia_x ** 2 + distancia_y ** 2 <= self.RAIO_COLISAO_BOLA ** 2)
            if colisao:
                # A Noiva mantém sua proteção natural contra dano repetido.
                noiva.receber_dano()
                # ALTERAÇÃO: só libera a arma quando o primeiro tiro desaparece.
                if bola.get("primeira"):
                    self.primeira_bola_encerrada = True
                self.bolas_fogo.remove(bola)
                continue

            margem = self.MARGEM_SAIDA_BOLA
            x_tela = bola["x"] - self.camera_x_atual
            if (x_tela < -margem or x_tela > self.largura_tela_atual + margem
                    or bola["y"] < -margem or bola["y"] > self.altura_tela_atual + margem):
                # ALTERAÇÃO: desaparecimento por saída da área visível.
                if bola.get("primeira"):
                    self.primeira_bola_encerrada = True
                self.bolas_fogo.remove(bola)

    def desenhar_bolas_fogo(self):
        if not self.ativa:
            return
        for bola in self.bolas_fogo:
            sprite = bola["sprite"]
            # ALTERAÇÃO: x/y são o centro lógico; largura e altura vêm do novo sprite.
            sprite.set_position(bola["x"] - sprite.width / 2,
                                bola["y"] - sprite.height / 2)
            # ALTERAÇÃO: sem rotação; sprite circular já funciona em qualquer direção.
            sprite.draw()

    def atualizar(self, dt, camera_x, largura_tela, altura_tela, noiva=None):
        if not self.ativa:
            return

        # ALTERAÇÃO: informações da câmera para retirar projéteis fora da tela.
        self.camera_x_atual = camera_x
        self.largura_tela_atual = largura_tela
        self.altura_tela_atual = altura_tela

        # Os projéteis existentes continuam mesmo depois que a Boss volta ao idle.
        if noiva is not None:
            self._atualizar_bolas_fogo(noiva, dt)

        # ALTERAÇÃO: durante o dano, congela a órbita e os ataques.
        if self.estado == "dano":
            self.tempo_dano_boss += dt
            if self.tempo_dano_boss >= self.TEMPO_DANO_BOSS:
                if self.hits_recebidos >= self.HITS_PARA_DERROTAR:
                    self._iniciar_derrota()
                else:
                    # ALTERAÇÃO: depois do dano, subir rapidamente acima da Noiva.
                    self.estado = "recuo_apos_hit"
                    self.tempo_estado = 0.0
                    # ALTERAÇÃO: após cada hit, preparar o próximo ataque mais cedo.
                    # O tempo de espera conta a partir do fim do recuo, sem aguardar
                    # novamente até 10 segundos entre os disparos.
                    self.tempo_proximo_ataque = random.uniform(1.0, 2.0)
                    self.idle_direita.play()
                    self.idle_esquerda.play()
            return

        if self.estado == "derrota":
            self._atualizar_derrota(dt)
            return

        # ALTERAÇÃO: recuo rápido para a região ACIMA da Noiva após cada hit.
        # Ao alcançar o destino, volta suavemente à órbita (sem teleporte).
        if self.estado == "recuo_apos_hit":
            largura_sprite = max(self.idle_direita.width, self.ataque_direita.width)
            altura_sprite = max(self.idle_direita.height, self.ataque_direita.height)
            if noiva is not None:
                destino_x = max(camera_x + self.MARGEM_LATERAL,
                                min(noiva.centro_x - largura_sprite / 2,
                                    camera_x + largura_tela - largura_sprite - self.MARGEM_LATERAL))
                destino_y = max(0.0, min(altura_tela - altura_sprite,
                                          noiva.y - altura_sprite - self.DISTANCIA_ACIMA_NOIVA))
            else:
                destino_x = self.x
                destino_y = 0.0
            dx, dy = destino_x - self.x, destino_y - self.y
            distancia = math.hypot(dx, dy)
            passo = self.VELOCIDADE_RECUO_APOS_HIT * dt
            if distancia <= passo or distancia < 1.0:
                self.x, self.y = destino_x, destino_y
                self.estado = "idle"
                self.tempo_estado = 0.0
                # ALTERAÇÃO: a órbita retoma de onde a Boss está, suavemente.
                self.retorno_orbita = self.DURACAO_RETORNO_ORBITA
                self.deslocamento_retorno_x = self.x
                self.deslocamento_retorno_y = self.y
            else:
                self.x += dx / distancia * passo
                self.y += dy / distancia * passo
            return

        # ALTERAÇÃO: usa dt para ser independente do FPS.
        self.tempo_orbita += dt
        self.tempo_estado += dt

        # ALTERAÇÃO: liberar toda a largura/altura da janela na arena final.
        # Os limites garantem que o sprite inteiro permaneça visível.
        largura_sprite = max(self.idle_direita.width, self.ataque_direita.width)
        altura_sprite = max(self.idle_direita.height, self.ataque_direita.height)
        x_min = self.MARGEM_LATERAL
        x_max = max(x_min, largura_tela - largura_sprite - self.MARGEM_LATERAL)
        y_min = 0.0
        y_max = max(y_min, altura_tela - altura_sprite - self.MARGEM_INFERIOR)

        centro_x = (x_min + x_max) / 2
        centro_y = (y_min + y_max) / 2
        raio_x = min(self.RAIO_HORIZONTAL, max(0, (x_max - x_min) / 2))
        raio_y = min(self.RAIO_VERTICAL, max(0, (y_max - y_min) / 2))

        angulo = 2 * math.pi * (self.tempo_orbita / max(self.PERIODO_ORBITA, 0.001))
        # ALTERAÇÃO: no Pygame, Y aumenta para baixo. O sinal negativo
        # no seno produz translação anti-horária na tela.
        x_tela = centro_x + raio_x * math.cos(angulo)
        y_tela = centro_y - raio_y * math.sin(angulo)

        # Sprite.draw() já transforma coordenadas de mundo usando a Camera.
        # ALTERAÇÃO: após o recuo por hit, retomar a órbita progressivamente.
        # Os deslocamentos guardam a última posição do recuo, sem salto brusco.
        if self.retorno_orbita > 0.0:
            fracao = min(1.0, dt / max(self.retorno_orbita, 0.001))
            x_orbita = camera_x + x_tela
            self.x = self.x + (x_orbita - self.x) * fracao
            self.y = self.y + (y_tela - self.y) * fracao
            self.retorno_orbita = max(0.0, self.retorno_orbita - dt)
        else:
            self.x = camera_x + x_tela
            self.y = y_tela

        # ALTERAÇÃO: a direção do rosto acompanha a posição da Noiva,
        # e NÃO a direção da órbita. A órbita continua independente.
        # Usa o centro visual da Boss (mesma referência de desenhar()).
        if noiva is not None:
            centro_rosto_x = self.x + largura_sprite / 2
            self.direcao = "esquerda" if noiva.centro_x < centro_rosto_x else "direita"

        if self.estado == "idle":
            if self.tempo_estado >= self.tempo_proximo_ataque:
                self._iniciar_ataque()
        elif self.estado == "atacando":
            # ALTERAÇÃO: mira UMA VEZ, no momento escolhido da animação.
            momento = self.TEMPO_ATAQUE / 1000 * self.MOMENTO_DISPARO
            if not self.bola_disparada and self.tempo_estado >= momento and noiva is not None:
                self._criar_bola_fogo(noiva)
                self.bola_disparada = True
            if self.tempo_estado >= self.TEMPO_ATAQUE / 1000:
                self._finalizar_ataque()

    def atualizar_animacao(self):
        if not self.ativa:
            return
        sprite = self._sprite_ativo()
        sprite.update()

    def desenhar(self):
        if not self.ativa:
            return
        sprite = self._sprite_ativo()
        # ALTERAÇÃO: centraliza animações que possam ter larguras diferentes.
        largura_referencia = max(self.idle_direita.width, self.ataque_direita.width)
        ajuste_x = (largura_referencia - sprite.width) / 2
        sprite.set_position(self.x + ajuste_x, self.y)
        sprite.draw()
