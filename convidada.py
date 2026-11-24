import random

from PPlay.sprite import Sprite


# ============================================================
# CLASSE CONVIDADA
# ============================================================

class Convidada:

    # --------------------------------------------------------
    # VELOCIDADE / TEMPOS (AJUSTÁVEIS)
    # --------------------------------------------------------

    VELOCIDADE = 45
    VELOCIDADE_ALINHAMENTO = 35

    TEMPO_ANDANDO = 4000       # 9 frames: caminhada mais lenta (ms)
    TEMPO_IDLE = 3000         # 9 frames (ms)
    TEMPO_BOLSADA = 3000       # 9 frames (ms)
    TEMPO_VOMITAR = 4000       # 9 frames (ms)
    TEMPO_VOMITO = 600        # 9 frames do efeito (ms), após o atraso
    ATRASO_VOMITO = 1.2       # segundos após iniciar a animação de vomitar

    # --------------------------------------------------------
    # DANO / QUEDA (AJUSTÁVEIS)
    # --------------------------------------------------------

    TEMPO_DANO = 300  # ALTERAÇÃO: reação reduzida para o próximo golpe ser aceito          # duração da pose de dano (ms)
    TEMPO_QUEDA = 1800        # duração da animação de queda (ms)
    TEMPO_CAIDA = 2.0         # tempo no chão após a primeira queda (s)
    TEMPO_CAIDA_FINAL = 2.0   # ALTERAÇÃO: tempo deitada após a segunda queda, sem levantar (s)
    TEMPO_LEVANTAR = 1.0     # ALTERAÇÃO: duração dos frames reversos (s)
    # ALTERAÇÃO: a spritesheet esquerda tem os 9 quadros na ordem inversa.
    QUEDA_TOTAL_FRAMES = 9
    # ALTERAÇÃO: quadros finais reais nos PNGs originais (não modificar imagens).
    QUEDA_FRAME_DEITADA_DIREITA = 8
    QUEDA_FRAME_DEITADA_ESQUERDA = 0
    GOLPES_POR_QUEDA = 3  # ALTERAÇÃO: padronizado com o Penetra
    QUEDAS_PARA_ELIMINAR = 2
    LARGURA_CORPO = 80

    # ALTERAÇÃO: entrada configurável; sprite idle definitivo da Convidada.
    TEMPO_IDLE_INICIAL = 2.0
    DIRECAO_INICIAL = "esquerda"

    INTERVALO_IDLE_MIN = 4.0  # segundos
    INTERVALO_IDLE_MAX = 8.0  # segundos

    INTERVALO_ATAQUE = 2.0     # segundos entre ataques
    DISTANCIA_APROXIMACAO = 160
    DISTANCIA_BOLSADA = 200
    DISTANCIA_VOMITO = 390
    TOLERANCIA_ATAQUE_Y = 90

    # --------------------------------------------------------
    # COLISÃO / POSIÇÃO DOS EFEITOS (AJUSTÁVEIS)
    # --------------------------------------------------------

    # As spritesheets têm 300 px de altura; usamos seu centro
    # para acompanhar a noiva sem depender do fundo transparente.
    CENTRO_CORPO_Y = 150
    CENTRO_CORPO_X = 80

    # Ajuste fino da origem do efeito em relação à convidada.
    OFFSET_VOMITO_X_DIREITA = 105
    OFFSET_VOMITO_X_ESQUERDA = -505
    OFFSET_VOMITO_Y = 12      # mais baixo que o posicionamento anterior (-60)

    # --------------------------------------------------------
    # SPRITES
    # --------------------------------------------------------

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
        self.estado = "andando"
        self.tempo_estado = 0
        self.tempo_ate_idle = random.uniform(
            self.INTERVALO_IDLE_MIN,
            self.INTERVALO_IDLE_MAX
        )
        self.tempo_caminhando = 0
        self.tempo_intervalo_ataque = 0
        self.ataque_registrado = False
        self.vomito_iniciado = False
        self.tipo_ataque = "bolsa"

        # Cada golpe da noiva é contado uma única vez.
        self.golpes = 0
        self.quedas = 0
        self.ultimo_id_ataque_noiva = -1
        self.derrotada = False
        self.tempo_levantar = 0.0
        # ALTERAÇÃO: congela a orientação ao iniciar uma queda.
        self.direcao_queda = self.direcao

        self.andando_direita = Sprite(
            "assets/personagens/convidada/convidada-01-andar-direita.png", 9
        )
        self.andando_esquerda = Sprite(
            "assets/personagens/convidada/convidada-01-andar-esquerda.png", 9
        )
        self.bolsada_direita = Sprite(
            "assets/personagens/convidada/convidada-01-bolsada-direita.png", 9
        )
        self.bolsada_esquerda = Sprite(
            "assets/personagens/convidada/convidada-01-bolsada-esquerda.png", 9
        )
        self.idle_direita = Sprite(
            "assets/personagens/convidada/convidada-01-idle-direita.png", 9
        )
        self.idle_esquerda = Sprite(
            "assets/personagens/convidada/convidada-01-idle-esquerda.png", 9
        )
        self.vomitar_direita = Sprite(
            "assets/personagens/convidada/convidada-01-vomitar-direita.png", 9
        )
        self.vomitar_esquerda = Sprite(
            "assets/personagens/convidada/convidada-01-vomitar-esquerda.png", 9
        )

        # Sprites de dano (1 quadro) e queda (9 quadros).
        self.dano_direita = Sprite(
            "assets/personagens/convidada/convidada-01-dano-direita.png", 1
        )
        self.dano_esquerda = Sprite(
            "assets/personagens/convidada/convidada-01-dano-esquerda.png", 1
        )
        self.queda_direita = Sprite(
            "assets/personagens/convidada/convidada-01-queda-direita.png", 9
        )
        self.queda_esquerda = Sprite(
            "assets/personagens/convidada/convidada-01-queda-esquerda.png", 9
        )

        # O efeito de vômito fica na pasta objetos.
        self.vomito_direita = Sprite("assets/objetos/vomito-direita.png", 9)
        self.vomito_esquerda = Sprite("assets/objetos/vomito-esquerda.png", 9)

        self.andando_direita.set_total_duration(self.TEMPO_ANDANDO)
        self.andando_esquerda.set_total_duration(self.TEMPO_ANDANDO)
        self.idle_direita.set_total_duration(self.TEMPO_IDLE)
        self.idle_esquerda.set_total_duration(self.TEMPO_IDLE)
        self.bolsada_direita.set_total_duration(self.TEMPO_BOLSADA)
        self.bolsada_esquerda.set_total_duration(self.TEMPO_BOLSADA)
        self.vomitar_direita.set_total_duration(self.TEMPO_VOMITAR)
        self.vomitar_esquerda.set_total_duration(self.TEMPO_VOMITAR)
        self.vomito_direita.set_total_duration(self.TEMPO_VOMITO)
        self.vomito_esquerda.set_total_duration(self.TEMPO_VOMITO)
        self.queda_direita.set_total_duration(self.TEMPO_QUEDA)
        self.queda_esquerda.set_total_duration(self.TEMPO_QUEDA)

        # ALTERAÇÃO: idle deve repetir continuamente enquanto a Convidada aguarda.
        # Ataques e queda continuam sem loop, como no código original.
        self.idle_direita.set_loop(True)
        self.idle_esquerda.set_loop(True)

        for sprite in [
            self.bolsada_direita, self.bolsada_esquerda,
            self.vomitar_direita, self.vomitar_esquerda,
            self.vomito_direita, self.vomito_esquerda,
            self.queda_direita, self.queda_esquerda
        ]:
            sprite.set_loop(False)

    # ========================================================
    # ALTERAÇÃO: AGUARDA A ENTRADA COMPLETA NA TELA
    # ========================================================

    def atualizar_entrada(self, dt, camera_x, largura_tela, noiva=None, distancia_ativacao=None):
        if self.entrada_liberada:
            return

        # A posição é do frame de caminhada, em coordenadas de mundo.
        largura = self.andando_direita.width
        visivel = self.x >= camera_x and self.x + largura <= camera_x + largura_tela
        if not visivel:
            self.entrada_visivel = False
            self.tempo_idle_inicial = 0.0
            return

        if not self.entrada_visivel:
            # ALTERAÇÃO: começa o idle no primeiro quadro quando aparece.
            self.idle_direita.stop()
            self.idle_esquerda.stop()
            self.idle_direita.play()
            self.idle_esquerda.play()
        self.entrada_visivel = True
        # ALTERAÇÃO: permanece em idle, parado e animado, até a Noiva se aproximar.
        # Mantém entrada_visivel=True para desenhar a animação de espera.
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
    # POSIÇÃO
    # ========================================================

    @property
    def centro_x(self):
        return self.x + self.CENTRO_CORPO_X

    @property
    def centro_y(self):
        return self.y + self.CENTRO_CORPO_Y

    # ========================================================
    # INICIA IDLE / ATAQUE
    # ========================================================

    def _iniciar_idle(self):
        self.estado = "idle"
        self.tempo_estado = 0
        self.idle_direita.stop()
        self.idle_esquerda.stop()
        self.idle_direita.play()
        self.idle_esquerda.play()

    def _iniciar_ataque(self, tipo):
        self.tipo_ataque = tipo
        self.estado = "atacando"
        self.tempo_estado = 0
        self.ataque_registrado = False
        self.vomito_iniciado = False

        if tipo == "bolsa":
            self.bolsada_direita.stop()
            self.bolsada_esquerda.stop()
            self.bolsada_direita.play()
            self.bolsada_esquerda.play()
        else:
            self.vomitar_direita.stop()
            self.vomitar_esquerda.stop()
            self.vomito_direita.stop()
            self.vomito_esquerda.stop()
            self.vomitar_direita.play()
            self.vomitar_esquerda.play()
            # O efeito começa apenas após ATRASO_VOMITO.
            # O play() será executado na atualização do ataque.

    def _voltar_a_andar(self):
        self.estado = "andando"
        self.tempo_estado = 0
        self.tempo_caminhando = 0
        self.tempo_ate_idle = random.uniform(
            self.INTERVALO_IDLE_MIN,
            self.INTERVALO_IDLE_MAX
        )

    # ========================================================
    # RECEBE GOLPE DA NOIVA
    # ========================================================

    def verificar_golpe_noiva(self, noiva):

        # Não recebe golpes enquanto está reagindo, caindo ou eliminada.
        if self.estado in ["dano", "caindo", "caida", "levantando", "eliminada", "removida"] or not self.entrada_liberada:
            return

        if not noiva.ataque_pode_causar_dano():
            return

        # Impede que o mesmo ataque seja contado em vários frames.
        if self.ultimo_id_ataque_noiva == noiva.id_ataque:
            return

        # ALTERAÇÃO: o golpe da noiva só alcança inimigos à sua frente.
        # Mantém a hitbox e os alcances já ajustados para o combate.
        if noiva.direcao == "direita" and self.centro_x < noiva.centro_x:
            return
        if noiva.direcao == "esquerda" and self.centro_x > noiva.centro_x:
            return

        distancia_centros_x = abs(noiva.centro_x - self.centro_x)
        distancia_y = abs(noiva.centro_y - self.centro_y)
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
            self._receber_golpe()
            return True  # ALTERAÇÃO: informa acerto válido ao main.py para pontuação na Fase 2.

    def _receber_golpe(self):

        self.golpes = self.golpes + 1
        self.estado = "dano"
        self.tempo_estado = 0

        # Interrompe idle e ataques; não produz efeito de vômito.
        self.ataque_registrado = True
        self.vomito_iniciado = False
        self.tempo_intervalo_ataque = 0
        self.bolsada_direita.stop()
        self.bolsada_esquerda.stop()
        self.vomitar_direita.stop()
        self.vomitar_esquerda.stop()
        self.vomito_direita.stop()
        self.vomito_esquerda.stop()

    def _iniciar_queda(self):

        self.quedas = self.quedas + 1
        self.estado = "caindo"
        self.tempo_estado = 0
        # ALTERAÇÃO: evita trocar de orientação durante queda e recuperação.
        self.direcao_queda = self.direcao
        # ALTERAÇÃO: controlar os quadros manualmente evita diferenças
        # entre a animação direita (em pé -> deitada) e esquerda (deitada -> em pé).
        self.queda_direita.stop()
        self.queda_esquerda.stop()
        self.queda_direita.set_curr_frame(0)
        self.queda_esquerda.set_curr_frame(self.QUEDA_TOTAL_FRAMES - 1)

    # ========================================================
    # ALTERAÇÃO: POSE DEITADA FIXA NAS DUAS DIREÇÕES
    # ========================================================

    def _fixar_pose_deitada(self):
        # Nos PNGs atuais a direita termina no frame 8 e a esquerda no 0.
        # Nunca chamar play() ou update() para a animação de queda já concluída.
        self.queda_direita.set_curr_frame(self.QUEDA_FRAME_DEITADA_DIREITA)
        self.queda_esquerda.set_curr_frame(self.QUEDA_FRAME_DEITADA_ESQUERDA)

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    # ALTERAÇÃO: assinatura padronizada com o Penetra.
    # offset_y é opcional: zero mantém a perseguição atual.
    def atualizar(self, noiva, dt, largura_mundo, altura_mundo, offset_y=0):

        if self.estado == "removida":
            return
        self.tempo_estado = self.tempo_estado + dt
        if self.entrada_liberada:
            self.tempo_intervalo_ataque = self.tempo_intervalo_ataque + dt

        distancia_x = abs(noiva.centro_x - self.centro_x)
        distancia_y = abs(noiva.centro_y - self.centro_y)

        if self.estado == "dano":
            if self.tempo_estado >= self.TEMPO_DANO / 1000:
                if self.golpes >= self.GOLPES_POR_QUEDA:
                    self.golpes = 0
                    self._iniciar_queda()
                else:
                    self._voltar_a_andar()

        elif self.estado == "caindo":
            # ALTERAÇÃO: quadros da direita e esquerda têm ordens opostas
            # nas spritesheets atuais. A posição deitada é o último quadro
            # à direita e o primeiro quadro à esquerda.
            progresso = min(1.0, self.tempo_estado / max(self.TEMPO_QUEDA / 1000, 0.001))
            quadro_direita = min(self.QUEDA_TOTAL_FRAMES - 1, int(progresso * self.QUEDA_TOTAL_FRAMES))
            quadro_esquerda = self.QUEDA_TOTAL_FRAMES - 1 - quadro_direita
            self.queda_direita.set_curr_frame(quadro_direita)
            self.queda_esquerda.set_curr_frame(quadro_esquerda)

            if progresso >= 1.0:
                # ALTERAÇÃO: termina a queda na pose deitada, inclusive
                # na segunda queda, sem passar por frames de levantamento.
                self._fixar_pose_deitada()
                if self.quedas >= self.QUEDAS_PARA_ELIMINAR:
                    self.estado = "eliminada"
                    self.derrotada = True
                else:
                    self.estado = "caida"
                self.tempo_estado = 0

        elif self.estado == "caida":
            # ALTERAÇÃO: mantém a pose deitada durante todo o intervalo.
            self._fixar_pose_deitada()
            if self.tempo_estado >= self.TEMPO_CAIDA:
                # ALTERAÇÃO: só levanta após a primeira queda.
                # Mesmo que este estado seja alcançado na segunda queda,
                # nunca reproduz os frames de levantamento antes de sumir.
                if self.quedas >= self.QUEDAS_PARA_ELIMINAR:
                    self.estado = "removida"
                else:
                    self.estado = "levantando"
                self.tempo_estado = 0

        elif self.estado == "levantando":
            # ALTERAÇÃO: proteção adicional contra levantamento na queda final.
            if self.quedas >= self.QUEDAS_PARA_ELIMINAR:
                # ALTERAÇÃO: jamais levantar após a segunda queda.
                self.estado = "eliminada"
                self.tempo_estado = 0
                self._fixar_pose_deitada()
                return
            # ALTERAÇÃO: reproduz o movimento contrário da queda,
            # respeitando a ordem original de cada spritesheet.
            progresso = min(1.0, self.tempo_estado / max(self.TEMPO_LEVANTAR, 0.001))
            quadro_direita = max(0, self.QUEDA_TOTAL_FRAMES - 1 - int(progresso * self.QUEDA_TOTAL_FRAMES))
            quadro_esquerda = self.QUEDA_TOTAL_FRAMES - 1 - quadro_direita
            self.queda_direita.set_curr_frame(quadro_direita)
            self.queda_esquerda.set_curr_frame(quadro_esquerda)
            if progresso >= 1.0:
                self._voltar_a_andar()

        elif self.estado == "eliminada":
            # ALTERAÇÃO: na segunda queda, permanece deitada antes
            # de desaparecer, nas duas direções.
            self._fixar_pose_deitada()
            if self.tempo_estado >= self.TEMPO_CAIDA_FINAL:
                self.estado = "removida"

        elif self.estado == "andando" and self.entrada_liberada:

            if noiva.centro_x < self.centro_x:
                self.direcao = "esquerda"
            else:
                self.direcao = "direita"

            # Quando próxima, prioriza o ataque em vez do idle.
            if (
                distancia_x <= self.DISTANCIA_VOMITO
                and distancia_y <= self.TOLERANCIA_ATAQUE_Y
                and self.tempo_intervalo_ataque >= self.INTERVALO_ATAQUE
            ):
                if distancia_x <= self.DISTANCIA_BOLSADA:
                    tipo = random.choice(["bolsa", "vomito"])
                else:
                    tipo = "vomito"
                self._iniciar_ataque(tipo)

            else:
                self.tempo_caminhando = self.tempo_caminhando + dt

                if self.tempo_caminhando >= self.tempo_ate_idle:
                    self._iniciar_idle()
                else:
                    if distancia_x > self.DISTANCIA_APROXIMACAO:
                        if self.direcao == "direita":
                            self.x = self.x + self.VELOCIDADE * dt
                        else:
                            self.x = self.x - self.VELOCIDADE * dt

                    # ALTERAÇÃO: offset opcional, como no Penetra.
                    # Com offset_y = 0, o comportamento é idêntico ao anterior.
                    alvo_y = noiva.centro_y + offset_y
                    distancia_alvo_y = abs(alvo_y - self.centro_y)
                    if distancia_alvo_y > self.TOLERANCIA_ATAQUE_Y / 2:
                        if alvo_y > self.centro_y:
                            self.y = self.y + self.VELOCIDADE_ALINHAMENTO * dt
                        else:
                            self.y = self.y - self.VELOCIDADE_ALINHAMENTO * dt

        elif self.estado == "idle":
            if self.tempo_estado >= self.TEMPO_IDLE / 1000:
                self._voltar_a_andar()

        elif self.estado == "atacando":
            if self.tipo_ataque == "bolsa":
                duracao = self.TEMPO_BOLSADA / 1000
                alcance = self.DISTANCIA_BOLSADA
            else:
                duracao = self.TEMPO_VOMITAR / 1000
                alcance = self.DISTANCIA_VOMITO

            # Inicia o efeito de vômito 0,8 s depois do movimento da convidada.
            if (
                self.tipo_ataque == "vomito"
                and not self.vomito_iniciado
                and self.tempo_estado >= self.ATRASO_VOMITO
            ):
                self.vomito_iniciado = True
                self.vomito_direita.play()
                self.vomito_esquerda.play()

            # Uma única tentativa de dano: no início do efeito de vômito,
            # ou na metade da animação da bolsada.
            momento_dano = duracao / 2
            if self.tipo_ataque == "vomito":
                momento_dano = self.ATRASO_VOMITO

            if not self.ataque_registrado and self.tempo_estado >= momento_dano:
                self.ataque_registrado = True

                distancia_x = abs(noiva.centro_x - self.centro_x)
                # ALTERAÇÃO: bolsada e vômito usam a altura da Noiva no salto.
                # A perseguição da Convidada continua usando a posição de solo.
                distancia_y = abs(noiva.centro_y_colisao_aerea - self.centro_y)

                if (
                    distancia_x <= alcance
                    and distancia_y <= self.TOLERANCIA_ATAQUE_Y
                    and not noiva.recebendo_dano
                    and not noiva.caida
                ):
                    noiva.receber_dano()

            if self.tempo_estado >= duracao:
                self.tempo_intervalo_ataque = 0
                self._voltar_a_andar()

        # Mantém a convidada dentro do mundo e da pista jogável.
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
    # ALTERAÇÃO: SEPARA A ATUALIZAÇÃO DOS FRAMES DO DESENHO
    # ========================================================

    def atualizar_animacao(self):

        if self.estado == "removida" or (not self.entrada_liberada and not self.entrada_visivel):
            return

        sprite = self._sprite_ativo()

        # Poses fixas mantêm o quadro atual.
        if self.estado not in ["caindo", "caida", "levantando", "eliminada", "dano"]:
            sprite.update()

        if self.estado == "atacando" and self.tipo_ataque == "vomito" and self.vomito_iniciado:
            efeito = self.vomito_direita if self.direcao == "direita" else self.vomito_esquerda
            efeito.update()

    # ========================================================
    # ALTERAÇÃO: RETORNA O SPRITE DA ANIMAÇÃO ATIVA
    # ========================================================

    def _sprite_ativo(self):

        if self.estado == "removida":
            return

        if self.estado == "dano":
            if self.direcao == "direita":
                sprite = self.dano_direita
            else:
                sprite = self.dano_esquerda

        elif self.estado in ["caindo", "caida", "levantando", "eliminada"]:
            # ALTERAÇÃO: direção travada durante a queda/levantamento.
            if self.direcao_queda == "direita":
                sprite = self.queda_direita
            else:
                sprite = self.queda_esquerda

        elif self.estado == "idle" or not self.entrada_liberada:
            # ALTERAÇÃO: usa o sprite idle durante a espera inicial.
            if self.direcao == "direita":
                sprite = self.idle_direita
            else:
                sprite = self.idle_esquerda

        elif self.estado == "atacando":
            if self.tipo_ataque == "bolsa":
                if self.direcao == "direita":
                    sprite = self.bolsada_direita
                else:
                    sprite = self.bolsada_esquerda
            else:
                if self.direcao == "direita":
                    sprite = self.vomitar_direita
                else:
                    sprite = self.vomitar_esquerda
        else:
            if self.direcao == "direita":
                sprite = self.andando_direita
            else:
                sprite = self.andando_esquerda

        return sprite

    # ========================================================
    # DESENHO
    # ========================================================

    def desenhar(self):

        if self.estado == "removida":
            return

        # ALTERAÇÃO: reforça a pose deitada imediatamente antes do draw.
        # Evita que a segunda queda mostre qualquer frame de levantamento.
        if self.estado in ["caida", "eliminada"]:
            self._fixar_pose_deitada()

        sprite = self._sprite_ativo()

        # Mantém o centro visual no mesmo lugar entre spritesheets
        # de larguras diferentes (andar, idle e bolsada).
        ajuste_x = (self.andando_direita.width - sprite.width) / 2
        sprite.set_position(self.x + ajuste_x, self.y)  # ALTERAÇÃO: coordenadas de mundo.
        # ALTERAÇÃO: desenha mesmo durante dano e queda (quadro congelado).
        sprite.draw()

        # Efeito visual do vômito durante o ataque correspondente.
        if self.estado == "atacando" and self.tipo_ataque == "vomito" and self.vomito_iniciado:
            if self.direcao == "direita":
                efeito = self.vomito_direita
                efeito_x = self.x + self.OFFSET_VOMITO_X_DIREITA
            else:
                efeito = self.vomito_esquerda
                efeito_x = self.x + self.OFFSET_VOMITO_X_ESQUERDA

            efeito.set_position(
                efeito_x,  # ALTERAÇÃO: Sprite.draw() aplica a câmera.
                self.y + self.OFFSET_VOMITO_Y
            )
            efeito.draw()
