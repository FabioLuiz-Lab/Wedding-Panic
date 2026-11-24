from PPlay.sprite import Sprite


# ============================================================
# CLASSE PENETRA
# ============================================================

class Penetra:

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
    GOLPES_POR_QUEDA = 3  # ALTERAÇÃO: padronizado com a Convidada
    TEMPO_CAIDO = 2.0
    # ALTERAÇÃO: primeira queda levanta; a segunda elimina.
    QUEDAS_PARA_ELIMINAR = 2
    TEMPO_LEVANTAR = 1.0  # segundos, frames da queda em ordem inversa

    INTERVALO_ATAQUE = 3.0

    # ALTERAÇÃO: espera de entrada configurável (s) e orientação inicial.
    TEMPO_IDLE_INICIAL = 2.0
    DIRECAO_INICIAL = "direita"

    # --------------------------------------------------------
    # MOVIMENTO / IA
    # --------------------------------------------------------

    VELOCIDADE = 25
    VELOCIDADE_ALINHAMENTO = 35

    DISTANCIA_ATAQUE = 950
    DISTANCIA_TAPA = 220

    TOLERANCIA_ALINHAMENTO_Y = 35
    DISTANCIA_PARADA = 160

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

    QUANTIDADE_FRAMES_ATAQUE = 12
    FRAME_DISPARO = 6

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
            "assets/personagens/penetra/penetra-01-andando-direita.png",
            6
        )

        self.andando_esquerda = Sprite(
            "assets/personagens/penetra/penetra-01-andando-esquerda.png",
            6
        )

        # ====================================================
        # ALTERAÇÃO: SPRITES - IDLE (16 FRAMES / 3 SEGUNDOS)
        # ====================================================

        self.idle_direita = Sprite(
            "assets/personagens/penetra/penetra-01-idle-direita.png", 16
        )
        self.idle_esquerda = Sprite(
            "assets/personagens/penetra/penetra-01-idle-esquerda.png", 16
        )
        self.idle_direita.set_total_duration(self.TEMPO_IDLE)
        self.idle_esquerda.set_total_duration(self.TEMPO_IDLE)

        self.andando_direita.set_total_duration(self.TEMPO_ANDANDO)
        self.andando_esquerda.set_total_duration(self.TEMPO_ANDANDO)

        # ====================================================
        # SPRITES - ATAQUE COM GARRAFA
        # ====================================================

        self.ataque_direita = Sprite(
            "assets/personagens/penetra/penetra-01-ataque-direita.png",
            12
        )

        self.ataque_esquerda = Sprite(
            "assets/personagens/penetra/penetra-01-ataque-esquerda.png",
            12
        )

        self.ataque_direita.set_total_duration(self.TEMPO_ATAQUE)
        self.ataque_esquerda.set_total_duration(self.TEMPO_ATAQUE)

        self.ataque_direita.set_loop(False)
        self.ataque_esquerda.set_loop(False)

        # ====================================================
        # SPRITES - TAPA
        # ====================================================

        self.tapa_direita = Sprite(
            "assets/personagens/penetra/penetra-01-tapa-direita.png",
            2
        )

        self.tapa_esquerda = Sprite(
            "assets/personagens/penetra/penetra-01-tapa-esquerda.png",
            2
        )

        self.tapa_direita.set_total_duration(self.TEMPO_TAPA)
        self.tapa_esquerda.set_total_duration(self.TEMPO_TAPA)

        self.tapa_direita.set_loop(False)
        self.tapa_esquerda.set_loop(False)

        # ====================================================
        # SPRITES - DANO
        # ====================================================

        self.dano_direita = Sprite(
            "assets/personagens/penetra/penetra-01-dano-direita.png",
            1
        )

        self.dano_esquerda = Sprite(
            "assets/personagens/penetra/penetra-01-dano-esquerda.png",
            1
        )

        # ====================================================
        # SPRITES - QUEDA
        # ====================================================

        self.queda_direita = Sprite(
            "assets/personagens/penetra/penetra-01-queda-direita.png",
            7
        )

        self.queda_esquerda = Sprite(
            "assets/personagens/penetra/penetra-01-queda-esquerda.png",
            7
        )

        self.queda_direita.set_total_duration(self.TEMPO_QUEDA)
        self.queda_esquerda.set_total_duration(self.TEMPO_QUEDA)

        self.queda_direita.set_loop(False)
        self.queda_esquerda.set_loop(False)

        # ====================================================
        # ATAQUE
        # ====================================================

        self.atacando = False
        self.tipo_ataque = "garrafa"

        self.tempo_intervalo = 0
        self.tempo_ataque = 0
        self.tempo_alinhado_tapa = 0

        self.garrafa_disparada = False
        self.tapa_registrado = False

        self.duracao_ataque = self.TEMPO_ATAQUE / 1000
        self.duracao_tapa = self.TEMPO_TAPA / 1000

        self.momento_frame_final_tapa = self.duracao_tapa / 2

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
        if self.entrada_liberada:
            return

        # A posição é do frame de caminhada, em coordenadas de mundo.
        largura = self.andando_direita.width
        visivel = self.x >= camera_x and self.x + largura <= camera_x + largura_tela
        if not visivel:
            self.entrada_visivel = False
            self.tempo_idle_inicial = 0.0
            return

        self.entrada_visivel = True
        # ALTERAÇÃO: permanece em idle, parado e animado, até a Noiva se aproximar.
        # Mantém entrada_visivel=True para desenhar a animação de espera.
        if (noiva is not None and distancia_ativacao is not None
                and abs(noiva.centro_x - self.centro_x) > distancia_ativacao):
            self.tempo_idle_inicial = 0.0
            return
        self.tempo_idle_inicial = self.tempo_idle_inicial + dt
        if self.tempo_idle_inicial >= self.tempo_idle_configurado:
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
    # INICIA ATAQUES
    # ========================================================

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


    def _iniciar_garrafa(self):

        self.atacando = True
        self.tipo_ataque = "garrafa"

        self.tempo_ataque = 0
        self.garrafa_disparada = False

        self.ataque_direita.stop()
        self.ataque_esquerda.stop()

        self.ataque_direita.play()
        self.ataque_esquerda.play()


    # ========================================================
    # ARREMESSA GARRAFA
    # ========================================================

    def _criar_garrafa(self):

        garrafa = Sprite(
            "assets/objetos/garrafa-whisky-01.png",
            1
        )

        # Escala original (1.0): não é necessário chamar set_scale().

        if self.direcao == "direita":

            x_garrafa = (
                self.x
                + self.ataque_direita.width
                * self.OFFSET_GARRAFA_X_DIREITA
            )

            velocidade_x = self.VELOCIDADE_GARRAFA
            velocidade_giro = self.VELOCIDADE_GIRO_GARRAFA

        else:

            x_garrafa = (
                self.x
                + self.ataque_esquerda.width
                * self.OFFSET_GARRAFA_X_ESQUERDA
            )

            velocidade_x = -self.VELOCIDADE_GARRAFA
            velocidade_giro = -self.VELOCIDADE_GIRO_GARRAFA

        y_garrafa = (
            self.y
            + self.andando_direita.height
            * self.OFFSET_GARRAFA_Y
        )

        self.garrafas.append({
            "sprite": garrafa,
            "x": x_garrafa,
            "y": y_garrafa,
            "vx": velocidade_x,
            "angulo": 0,
            "velocidade_giro": velocidade_giro
        })

        self.garrafa_disparada = True


    # ========================================================
    # ATUALIZA GARRAFAS
    # ========================================================

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

    def _atualizar_ataque(self, noiva, dt):

        self.tempo_ataque += dt

        # ----------------------------------------------------
        # GARRAFA
        # ----------------------------------------------------

        if self.tipo_ataque == "garrafa":

            duracao_frame = (
                self.duracao_ataque
                / self.QUANTIDADE_FRAMES_ATAQUE
            )

            momento_disparo = (
                (self.FRAME_DISPARO - 1)
                * duracao_frame
            )

            if (
                not self.garrafa_disparada
                and self.tempo_ataque >= momento_disparo
            ):
                self._criar_garrafa()

            if self.tempo_ataque >= self.duracao_ataque:

                self.atacando = False
                self.tempo_ataque = 0
                self.tempo_intervalo = 0
                self.garrafa_disparada = False

        # ----------------------------------------------------
        # TAPA
        # ----------------------------------------------------

        else:

            # Dano acontece quando entra no segundo frame.
            if (
                not self.tapa_registrado
                and self.tempo_ataque
                >= self.momento_frame_final_tapa
            ):

                self.tapa_registrado = True

                distancia_x = abs(
                    noiva.centro_x - self.centro_x
                )

                # ALTERAÇÃO: o tapa considera a altura real da Noiva no salto.
                # A IA continua utilizando centro_y (posição no chão).
                distancia_y = abs(
                    noiva.centro_y_colisao_aerea - self.centro_y
                )

                if (
                    distancia_x <= self.DISTANCIA_TAPA
                    and distancia_y <= noiva.TOLERANCIA_GOLPE_Y
                    and not noiva.recebendo_dano
                    and not noiva.caida
                ):
                    noiva.receber_dano()

            # Mantém o último frame durante o tempo configurado.
            if self.tempo_ataque >= self.duracao_total_tapa:

                self.atacando = False
                self.tempo_ataque = 0
                self.tempo_intervalo = 0
                self.tempo_alinhado_tapa = 0
                self.tapa_registrado = False


    # ========================================================
    # IA / MOVIMENTO
    # ========================================================

    def _atualizar_ia(self, noiva, dt, offset_y=0):

        # O penetra principal recebe offset_y = 0.
        # Os demais podem receber um deslocamento positivo ou negativo
        # para se aproximarem da noiva por linhas diferentes.
        alvo_y = noiva.centro_y + offset_y

        # Primeiro estima a direção usando o centro geral do frame.
        centro_estimado_x = (
            self.x + self.andando_direita.width / 2
        )

        if noiva.centro_x - centro_estimado_x >= 0:
            self.direcao = "direita"
        else:
            self.direcao = "esquerda"

        diferenca_x = noiva.centro_x - self.centro_x
        diferenca_y = alvo_y - self.centro_y

        distancia_x = abs(diferenca_x)
        distancia_y = abs(diferenca_y)

        alinhado_em_y = (
            distancia_y <= self.TOLERANCIA_ALINHAMENTO_Y
        )

        dentro_distancia_tapa = (
            distancia_x <= self.DISTANCIA_TAPA
        )

        self.tempo_intervalo += dt

        # ----------------------------------------------------
        # ALINHAMENTO EM Y
        # ----------------------------------------------------

        if not alinhado_em_y:

            if diferenca_y > 0:
                self.y += self.VELOCIDADE_ALINHAMENTO * dt
            else:
                self.y -= self.VELOCIDADE_ALINHAMENTO * dt

        # ----------------------------------------------------
        # APROXIMAÇÃO EM X
        # ----------------------------------------------------

        if distancia_x > self.DISTANCIA_PARADA:

            if diferenca_x > 0:
                self.x += self.VELOCIDADE * dt
            else:
                self.x -= self.VELOCIDADE * dt

        # ----------------------------------------------------
        # PREPARAÇÃO DO TAPA
        # ----------------------------------------------------

        if dentro_distancia_tapa and alinhado_em_y:
            self.tempo_alinhado_tapa += dt
        else:
            self.tempo_alinhado_tapa = 0

        # ----------------------------------------------------
        # TAPA TEM PRIORIDADE
        # ----------------------------------------------------

        if (
            self.tempo_intervalo >= self.INTERVALO_ATAQUE
            and dentro_distancia_tapa
            and alinhado_em_y
            and self.tempo_alinhado_tapa >= self.TEMPO_ALINHADO_TAPA
        ):
            self._iniciar_tapa()

        # ----------------------------------------------------
        # GARRAFA FORA DA DISTÂNCIA DO TAPA
        # ----------------------------------------------------

        elif (
            self.tempo_intervalo >= self.INTERVALO_ATAQUE
            and alinhado_em_y
            and distancia_x <= self.DISTANCIA_ATAQUE
            and not dentro_distancia_tapa
        ):
            self._iniciar_garrafa()


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
        if noiva.direcao == "direita" and self.centro_x < noiva.centro_x:
            return
        if noiva.direcao == "esquerda" and self.centro_x > noiva.centro_x:
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

        self.garrafa_disparada = False
        self.tapa_registrado = False
        self.tempo_alinhado_tapa = 0

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

        # ALTERAÇÃO: após a morte, apenas os projéteis existentes continuam.
        if self.removido:
            self._atualizar_garrafas(noiva, dt, largura_mundo)
            return

        # Projéteis continuam existindo mesmo que o penetra
        # esteja recebendo dano ou caído.
        self._atualizar_garrafas(noiva, dt, largura_mundo)

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
                self.queda_direita.set_curr_frame(6)
                self.queda_esquerda.set_curr_frame(6)

                self.tempo_queda = self.duracao_queda
                self.tempo_caido = 0

        # ----------------------------------------------------
        # CAÍDO
        # ----------------------------------------------------

        if self.derrotado:

            self.tempo_caido += dt

            if self.tempo_caido >= self.TEMPO_CAIDO:
                self.derrotado = False
                self.tempo_caido = 0
                if self.quedas >= self.QUEDAS_PARA_ELIMINAR:
                    # ALTERAÇÃO: segunda queda = eliminação definitiva.
                    self.eliminado = True
                    self.removido = True
                else:
                    # ALTERAÇÃO: na primeira queda, levanta ao contrário.
                    self.levantando = True
                    self.tempo_levantar = 0.0
                    self.queda_direita.set_curr_frame(6)
                    self.queda_esquerda.set_curr_frame(6)

        # ALTERAÇÃO: retrocede manualmente os sete quadros da queda.
        if self.levantando:
            self.tempo_levantar = self.tempo_levantar + dt
            progresso = min(1.0, self.tempo_levantar / max(self.TEMPO_LEVANTAR, 0.001))
            quadro = max(0, 6 - int(progresso * 7))
            self.queda_direita.set_curr_frame(quadro)
            self.queda_esquerda.set_curr_frame(quadro)
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

        for info in self.garrafas:

            sprite = info["sprite"]

            sprite.set_position(
                info["x"],  # ALTERAÇÃO: Sprite.draw() aplica a câmera.
                info["y"]
            )

            sprite.rotation = info["angulo"]

            sprite.draw()


    # ========================================================
    # ALTERAÇÃO: SELECIONA SOMENTE O SPRITE ATIVO
    # ========================================================

    def _sprite_ativo(self):

        if self.derrotado or self.caindo or self.levantando:
            return self.queda_direita if self.direcao == "direita" else self.queda_esquerda

        # ALTERAÇÃO: usa o novo sprite idle durante a espera inicial.
        if not self.entrada_liberada:
            return self.idle_direita if self.direcao == "direita" else self.idle_esquerda

        if self.recebendo_dano:
            return self.dano_direita if self.direcao == "direita" else self.dano_esquerda

        if self.atacando:
            if self.tipo_ataque == "tapa":
                return self.tapa_direita if self.direcao == "direita" else self.tapa_esquerda
            return self.ataque_direita if self.direcao == "direita" else self.ataque_esquerda

        return self.andando_direita if self.direcao == "direita" else self.andando_esquerda

    # ========================================================
    # ALTERAÇÃO: ATUALIZA ANIMAÇÃO SEPARADAMENTE DO DESENHO
    # ========================================================

    def atualizar_animacao(self):

        if self.removido or self.derrotado or self.recebendo_dano or self.levantando:
            return
        if not self.entrada_liberada:
            # ALTERAÇÃO: anima a pose idle continuamente enquanto aguarda.
            sprite = self._sprite_ativo()
            sprite.play()
            sprite.update()
            return

        sprite = self._sprite_ativo()

        if self.caindo:
            sprite.update()

        elif self.atacando:
            # Mantém o quadro final do tapa quando a animação acaba.
            if self.tipo_ataque != "tapa" or self.tempo_ataque < self.duracao_tapa:
                sprite.update()

        else:
            sprite.play()
            sprite.update()

    # ========================================================
    # DESENHO
    # ========================================================

    def desenhar(self):

        # ALTERAÇÃO: o cadáver desaparece após a segunda queda.
        if self.removido:
            return
        # ALTERAÇÃO: posiciona apenas o sprite selecionado.
        sprite = self._sprite_ativo()
        # ALTERAÇÃO: o novo idle tem 203 px, enquanto andar tem 300 px.
        # Centraliza os sprites sem alterar posição de mundo nem hitbox.
        ajuste_x = (self.andando_direita.width - sprite.width) / 2
        sprite.set_position(self.x + ajuste_x, self.y)  # ALTERAÇÃO: coordenadas de mundo.
        sprite.draw()
