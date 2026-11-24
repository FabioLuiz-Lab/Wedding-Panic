from PPlay.sprite import Sprite


# ============================================================
# CLASSE NOIVA
# ============================================================

class Noiva:

    # --------------------------------------------------------
    # TEMPOS DAS ANIMAÇÕES
    # --------------------------------------------------------

    TEMPO_IDLE = 1200  # ALTERAÇÃO: sprite anteriormente chamado de parada
    TEMPO_ANDANDO = 1600  # ALTERAÇÃO: nova caminhada com 16 frames em 3 segundos
    TEMPO_SALTO = 1500
    TEMPO_JAB = 450  # ALTERAÇÃO: cadência um pouco mais espaçada
    TEMPO_DIRETO = 550  # ALTERAÇÃO: cadência um pouco mais espaçada
    TEMPO_CHUTE = 350  # ALTERAÇÃO: chute um pouco mais legível
    TEMPO_DANO = 300  # ALTERAÇÃO: reação mais curta para melhorar a responsividade
    TEMPO_CAIDA = 1.0  # ALTERAÇÃO: metade do tempo anterior (2 s).
    TEMPO_INVULNERAVEL_APOS_LEVANTAR = 2.0  # ALTERAÇÃO: proteção extra após a recuperação
    # ALTERAÇÃO: limite reservado para o futuro sistema de vidas.
    # Por enquanto, a Noiva não é eliminada após as quedas.
    QUEDAS_PARA_ELIMINAR = 3  # ALTERAÇÃO: a cada três quedas, perde uma vida.
    VIDAS_INICIAIS = 5  # ALTERAÇÃO: sistema de vidas.
    TEMPO_LEVANTAR = 0.8  # animação de queda atual tem um único quadro
    INTERVALO_PISCADA_MORTE = 0.16  # ALTERAÇÃO: período do piscar ao perder a última vida

    # --------------------------------------------------------
    # MOVIMENTO E ÁREA JOGÁVEL
    # --------------------------------------------------------

    VELOCIDADE = 250
    ALTURA_SALTO = 330  # ALTERAÇÃO: salto 50% mais alto; mantém a duração atual.
    ALTURA_PISTA = 250

    # ALTERAÇÃO: animações e cadência do aplicador de chantilly.
    TEMPO_ANDANDO_ARMADA = 1600
    TEMPO_SALTO_ARMADA = 1500
    TEMPO_TIRO = 650             # duração visual do disparo (ms)
    INTERVALO_ENTRE_TIROS = 0.45 # segundos entre disparos


    # --------------------------------------------------------
    # HITBOX / ALCANCE
    # --------------------------------------------------------

    CENTRO_CORPO_X = 240
    CENTRO_CORPO_Y = 150

    LARGURA_CORPO = 80

    DISTANCIA_GOLPE = 100
    DISTANCIA_CHUTE = 150

    TOLERANCIA_GOLPE_Y = 80

    METADE_LARGURA_HITBOX = 45
    METADE_ALTURA_HITBOX = 110
    
    CENTRO_HITBOX_GARRAFA_Y = 90
    # ALTERAÇÃO: hitbox vertical específica da garrafa, sem sobrescrever a hitbox geral.
    METADE_ALTURA_HITBOX_GARRAFA = 45


    def __init__(self, x, y):

        # ====================================================
        # POSIÇÃO E ESTADO
        # ====================================================

        self.x = x
        self.y = y

        self.direcao = "direita"
        self.andando = False

        # ====================================================
        # SPRITES - IDLE
        # ====================================================

        self.idle_direita = Sprite(
            "assets/personagens/noiva/noiva-01-idle-direita.png",
            5
        )

        self.idle_esquerda = Sprite(
            "assets/personagens/noiva/noiva-01-idle-esquerda.png",
            5
        )

        self.idle_direita.set_total_duration(self.TEMPO_IDLE)
        self.idle_esquerda.set_total_duration(self.TEMPO_IDLE)

        # ====================================================
        # SPRITES - ANDANDO
        # ====================================================

        self.andando_direita = Sprite(
            "assets/personagens/noiva/noiva-01-andando-direita.png",
            16  # ALTERAÇÃO: 16 frames na spritesheet nova
        )

        self.andando_esquerda = Sprite(
            "assets/personagens/noiva/noiva-01-andando-esquerda.png",
            16  # ALTERAÇÃO: a versão esquerda também precisa ter 16 frames
        )

        self.andando_direita.set_total_duration(self.TEMPO_ANDANDO)
        self.andando_esquerda.set_total_duration(self.TEMPO_ANDANDO)

        # ====================================================
        # SPRITES - SALTO
        # ====================================================

        self.salto_direita = Sprite(
            "assets/personagens/noiva/noiva-01-salto-direita.png",
            4
        )

        self.salto_esquerda = Sprite(
            "assets/personagens/noiva/noiva-01-salto-esquerda.png",
            4
        )

        self.salto_direita.set_total_duration(self.TEMPO_SALTO)
        self.salto_esquerda.set_total_duration(self.TEMPO_SALTO)

        self.salto_direita.set_loop(False)
        self.salto_esquerda.set_loop(False)

        # ====================================================
        # SPRITES - JAB
        # ====================================================

        self.jab_direita = Sprite(
            "assets/personagens/noiva/noiva-01-jab-direita.png",
            6
        )

        self.jab_esquerda = Sprite(
            "assets/personagens/noiva/noiva-01-jab-esquerda.png",
            6
        )

        self.jab_direita.set_total_duration(self.TEMPO_JAB)
        self.jab_esquerda.set_total_duration(self.TEMPO_JAB)

        self.jab_direita.set_loop(False)
        self.jab_esquerda.set_loop(False)

        # ====================================================
        # SPRITES - DIRETO
        # ====================================================

        self.direto_direita = Sprite(
            "assets/personagens/noiva/noiva-01-direto-direita.png",
            10
        )

        self.direto_esquerda = Sprite(
            "assets/personagens/noiva/noiva-01-direto-esquerda.png",
            10
        )

        self.direto_direita.set_total_duration(self.TEMPO_DIRETO)
        self.direto_esquerda.set_total_duration(self.TEMPO_DIRETO)

        self.direto_direita.set_loop(False)
        self.direto_esquerda.set_loop(False)

        # ====================================================
        # SPRITES - CHUTE
        # ====================================================

        self.chute_direita = Sprite(
            "assets/personagens/noiva/noiva-01-chute-1-direita.png",
            2
        )

        self.chute_esquerda = Sprite(
            "assets/personagens/noiva/noiva-01-chute-1-esquerda.png",
            2
        )

        self.chute_direita.set_total_duration(self.TEMPO_CHUTE)
        self.chute_esquerda.set_total_duration(self.TEMPO_CHUTE)

        self.chute_direita.set_loop(False)
        self.chute_esquerda.set_loop(False)

        # ====================================================
        # SPRITES - DANO
        # ====================================================

        self.dano_direita = Sprite(
            "assets/personagens/noiva/noiva-01-dano-direita.png",
            1
        )

        self.dano_esquerda = Sprite(
            "assets/personagens/noiva/noiva-01-dano-esquerda.png",
            1
        )

        # ====================================================
        # SPRITES - QUEDA
        # ====================================================

        self.queda_direita = Sprite(
            "assets/personagens/noiva/noiva-01-queda-direita.png",
            1
        )

        self.queda_esquerda = Sprite(
            "assets/personagens/noiva/noiva-01-queda-esquerda.png",
            1
        )

        # ====================================================
        # ALTERAÇÃO: SPRITES - NOIVA ARMADA (16 FRAMES)
        # ====================================================

        self.andando_armada_direita = Sprite("assets/personagens/noiva/noiva-01-andando-armada-direita.png", 16)
        self.andando_armada_esquerda = Sprite("assets/personagens/noiva/noiva-01-andando-armada-esquerda.png", 16)
        self.salto_armada_direita = Sprite("assets/personagens/noiva/noiva-01-salto-armado-direita.png", 16)
        self.salto_armada_esquerda = Sprite("assets/personagens/noiva/noiva-01-salto-armado-esquerda.png", 16)
        self.tiro_chao_direita = Sprite("assets/personagens/noiva/noiva-01-chantily-direita.png", 16)
        self.tiro_chao_esquerda = Sprite("assets/personagens/noiva/noiva-01-chantily-esquerda.png", 16)
        self.tiro_aereo_direita = Sprite("assets/personagens/noiva/noiva-01-tiro-aereo-direita.png", 16)
        self.tiro_aereo_esquerda = Sprite("assets/personagens/noiva/noiva-01-tiro-aereo-esquerda.png", 16)

        for sprite in [self.andando_armada_direita, self.andando_armada_esquerda]:
            sprite.set_total_duration(self.TEMPO_ANDANDO_ARMADA)
        for sprite in [self.salto_armada_direita, self.salto_armada_esquerda]:
            sprite.set_total_duration(self.TEMPO_SALTO_ARMADA)
            sprite.set_loop(False)
        for sprite in [self.tiro_chao_direita, self.tiro_chao_esquerda,
                       self.tiro_aereo_direita, self.tiro_aereo_esquerda]:
            sprite.set_total_duration(self.TEMPO_TIRO)
            sprite.set_loop(False)

        # ====================================================
        # ESTADO DO SALTO
        # ====================================================

        self.pulando = False
        self.tempo_salto = 0
        self.altura_pulo = 0
        # ALTERAÇÃO: elevação independente para caminhar sobre o tampo da mesa.
        self.altura_plataforma = 0.0

        self.duracao_salto = self.TEMPO_SALTO / 1000

        # ALTERAÇÃO: arma é obtida apenas quando o aplicador é recolhido.
        self.armada = False
        self.atirando = False
        self.tempo_tiro = 0.0
        self.tempo_recarga_tiro = 0.0
        self.disparo_pendente = False


        # ====================================================
        # ESTADO DOS ATAQUES
        # ====================================================

        self.atacando = False
        self.tempo_ataque = 0
        self.tipo_ataque = "jab"

        self.combo = 0
        self.ataque_pendente = False
        self.chute_pendente = False  # ALTERAÇÃO: guarda um chute solicitado durante outro ataque

        self.duracao_jab = self.TEMPO_JAB / 1000
        self.duracao_direto = self.TEMPO_DIRETO / 1000
        self.duracao_chute = self.TEMPO_CHUTE / 1000

        # O chute só causa dano quando chega ao segundo frame.
        self.momento_impacto_chute = self.duracao_chute / 2

        # Identifica cada golpe individualmente.
        # Cada Penetra guarda o último id que já recebeu.
        self.id_ataque = 0

        # ====================================================
        # ESTADO DE DANO / QUEDA
        # ====================================================

        self.impactos = 0

        self.recebendo_dano = False
        self.tempo_dano = 0

        self.caida = False
        self.tempo_caida = 0
        self.quedas = 0
        self.vidas = self.VIDAS_INICIAIS  # ALTERAÇÃO: vidas restantes.
        self.levantando = False
        self.tempo_levantar = 0.0
        self.tempo_invulneravel = 0.0  # ALTERAÇÃO: proteção pós-queda compartilhada entre inimigos
        self.eliminada = False
        self.removida = False

        self.duracao_dano = self.TEMPO_DANO / 1000


    # ========================================================
    # PROPRIEDADES DE POSIÇÃO
    # ========================================================

    @property
    def largura(self):
        return self.andando_direita.width

    @property
    def altura(self):
        return self.andando_direita.height

    @property
    def centro_x(self):
        return self.x + self.CENTRO_CORPO_X

    @property
    def centro_y(self):
        return self.y + self.CENTRO_CORPO_Y

    # ========================================================
    # ALTERAÇÃO: HITBOX AÉREA PARA PROJÉTEIS E GOLPES DURANTE O SALTO
    # ========================================================

    @property
    def centro_y_colisao_aerea(self):
        # A coordenada de solo (centro_y) continua sendo usada pela IA
        # e pela profundidade. Somente colisões de dano usam o Y visual elevado.
        return self.centro_y - self.altura_pulo - self.altura_plataforma


    # ========================================================
    # INICIA ATAQUES
    # ========================================================

    def _iniciar_jab_ou_direto(self):

        self.combo += 1

        if self.combo == 3:

            self.tipo_ataque = "direto"

            self.direto_direita.stop()
            self.direto_esquerda.stop()

            self.direto_direita.play()
            self.direto_esquerda.play()

            self.combo = 0

        else:

            self.tipo_ataque = "jab"

            self.jab_direita.stop()
            self.jab_esquerda.stop()

            self.jab_direita.play()
            self.jab_esquerda.play()

        self.atacando = True
        self.tempo_ataque = 0

        self.id_ataque += 1


    def _iniciar_chute(self):

        self.tipo_ataque = "chute"

        self.atacando = True
        self.tempo_ataque = 0

        # Chute é independente do combo de socos.
        self.ataque_pendente = False
        self.chute_pendente = False  # ALTERAÇÃO: consumiu o chute armazenado

        self.chute_direita.stop()
        self.chute_esquerda.stop()

        self.chute_direita.play()
        self.chute_esquerda.play()

        self.id_ataque += 1


    # ========================================================
    # RECEBE DANO
    # ========================================================

    def receber_dano(self, impactos=1, limiar_queda=2):

        if (self.recebendo_dano or self.caida or self.levantando
                or self.eliminada or self.tempo_invulneravel > 0):
            return False

        # ALTERAÇÃO: o Amigo usa 3 hits comuns; voadora soma 3 de uma vez.
        # Os demais inimigos continuam usando os padrões: 1 impacto, queda com 2.
        self.impactos += impactos
        self.limiar_queda_dano = limiar_queda

        self.recebendo_dano = True
        self.tempo_dano = 0

        # Interrompe qualquer ação.
        self.atacando = False
        self.atirando = False  # ALTERAÇÃO: interrompe o tiro se receber dano.
        self.pulando = False
        self.ataque_pendente = False
        self.chute_pendente = False  # ALTERAÇÃO: limpa o comando de chute ao receber dano
        self.andando = False

        self.tempo_ataque = 0
        self.tempo_salto = 0
        self.altura_pulo = 0

        return True


    # ========================================================
    # ALTERAÇÃO: DISPARO DA NOIVA ARMADA
    # ========================================================

    def _iniciar_tiro(self):
        if self.tempo_recarga_tiro > 0 or self.eliminada or self.caida or self.recebendo_dano:
            return
        self.atirando = True
        self.tempo_tiro = 0.0
        self.tempo_recarga_tiro = self.INTERVALO_ENTRE_TIROS
        self.disparo_pendente = True  # o main cria o projétil uma única vez.
        for sprite in [self.tiro_chao_direita, self.tiro_chao_esquerda,
                       self.tiro_aereo_direita, self.tiro_aereo_esquerda]:
            sprite.stop()
            sprite.play()

    # ========================================================
    # ATAQUE ATIVO CONTRA INIMIGOS
    # ========================================================

    def ataque_pode_causar_dano(self):

        if not self.atacando:
            return False

        if self.tipo_ataque == "chute":
            return self.tempo_ataque >= self.momento_impacto_chute

        return True


    def alcance_ataque_atual(self):

        if self.tipo_ataque == "chute":
            return self.DISTANCIA_CHUTE

        return self.DISTANCIA_GOLPE


    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    def atualizar(self, teclado, dt, largura_mundo, altura_mundo):

        self.andando = False
        # ALTERAÇÃO: avança a imunidade mesmo que a Noiva esteja andando/atacando.
        self.tempo_invulneravel = max(0.0, self.tempo_invulneravel - dt)

        # ALTERAÇÃO: temporizador de disparos independente do salto.
        self.tempo_recarga_tiro = max(0.0, self.tempo_recarga_tiro - dt)
        if self.atirando:
            self.tempo_tiro += dt
            if self.tempo_tiro >= self.TEMPO_TIRO / 1000:
                self.atirando = False

        if (self.armada and not self.atacando and not self.recebendo_dano
                and not self.caida and not self.levantando and not self.eliminada
                and (teclado.key_down("Z") or teclado.key_down("C"))):
            self._iniciar_tiro()

        # ----------------------------------------------------
        # DANO
        # ----------------------------------------------------

        if self.recebendo_dano:

            self.tempo_dano += dt

            if self.tempo_dano >= self.duracao_dano:

                self.recebendo_dano = False
                self.tempo_dano = 0

                # No segundo impacto, depois da pose de dano,
                # a noiva entra na pose de queda.
                if self.impactos >= getattr(self, "limiar_queda_dano", 2):
                    self.caida = True
                    self.tempo_caida = 0
                    self.quedas = self.quedas + 1
                    # ALTERAÇÃO: perde exatamente uma vida após duas quedas.
                    # Não retira vida em cada golpe ou em cada queda isolada.
                    if self.quedas >= self.QUEDAS_PARA_ELIMINAR:
                        self.vidas = max(0, self.vidas - 1)
                        self.quedas = 0
                        if self.vidas == 0:
                            self.eliminada = True

        # ----------------------------------------------------
        # TEMPO CAÍDA
        # ----------------------------------------------------

        if self.caida:

            self.tempo_caida += dt

            # ALTERAÇÃO: na morte definitiva, permanece caída até o menu
            # de pontuação; não entra novamente no estado levantando.
            if self.tempo_caida >= self.TEMPO_CAIDA and not self.eliminada:

                self.caida = False
                self.tempo_caida = 0
                # ALTERAÇÃO: sem sistema de vidas, a Noiva sempre se levanta.
                # O quadro único da queda permanece visível durante a recuperação.
                self.levantando = True
                self.tempo_levantar = 0.0

        if self.levantando:
            self.tempo_levantar = self.tempo_levantar + dt
            if self.tempo_levantar >= self.TEMPO_LEVANTAR:
                self.levantando = False
                self.tempo_levantar = 0.0
                # ALTERAÇÃO: evita ser atingida imediatamente ao levantar cercada de Amigos.
                self.tempo_invulneravel = self.TEMPO_INVULNERAVEL_APOS_LEVANTAR
                self.impactos = 0
                # ALTERAÇÃO: preserva o contador de quedas entre recuperações.
                # Ele só é zerado ao perder uma vida (segunda queda).

        # ----------------------------------------------------
        # SALTO
        # ----------------------------------------------------

        if (
            teclado.key_down("SPACE")
            and not self.pulando
            and not self.atacando
            and not self.recebendo_dano
            and not self.caida
            and not self.levantando
            and not self.eliminada
        ):

            self.pulando = True
            self.tempo_salto = 0

            self.salto_direita.stop()
            self.salto_esquerda.stop()

            self.salto_direita.play()
            self.salto_esquerda.play()
            # ALTERAÇÃO: reinicia a spritesheet de salto armado na decolagem.
            self.salto_armada_direita.stop()
            self.salto_armada_esquerda.stop()
            self.salto_armada_direita.play()
            self.salto_armada_esquerda.play()

        self.altura_pulo = 0

        if self.pulando:

            self.tempo_salto += dt

            progresso = self.tempo_salto / self.duracao_salto

            self.altura_pulo = (
                4
                * self.ALTURA_SALTO
                * progresso
                * (1 - progresso)
            )

            if self.tempo_salto >= self.duracao_salto:

                self.pulando = False
                self.tempo_salto = 0
                self.altura_pulo = 0

        # ----------------------------------------------------
        # CHUTE - C
        # ----------------------------------------------------

        if (
            teclado.key_down("C")
            and not self.pulando
            and not self.recebendo_dano
            and not self.caida
            and not self.levantando
            and not self.eliminada
            and not self.armada  # ALTERAÇÃO: C dispara quando armada.
        ):
            # ALTERAÇÃO: armazena o chute se a Noiva já estiver atacando.
            # O comando será executado ao terminar a animação em andamento.
            if self.atacando:
                self.chute_pendente = True
                self.ataque_pendente = False
            else:
                self._iniciar_chute()

        # ----------------------------------------------------
        # SOCO - Z
        # ----------------------------------------------------

        if (
            teclado.key_down("Z")
            and not self.pulando
            and not self.recebendo_dano
            and not self.caida
            and not self.levantando
            and not self.eliminada
            and not self.armada  # ALTERAÇÃO: Z dispara quando armada.
        ):

            if self.atacando:

                # Durante o chute, Z não entra no buffer.
                if self.tipo_ataque != "chute" and not self.chute_pendente:
                    self.ataque_pendente = True

            else:
                self._iniciar_jab_ou_direto()

        # ----------------------------------------------------
        # TEMPO DO ATAQUE
        # ----------------------------------------------------

        if self.atacando:

            self.tempo_ataque += dt

            if self.tipo_ataque == "jab":
                duracao_ataque = self.duracao_jab

            elif self.tipo_ataque == "direto":
                duracao_ataque = self.duracao_direto

            else:
                duracao_ataque = self.duracao_chute

            if self.tempo_ataque >= duracao_ataque:

                tipo_finalizado = self.tipo_ataque

                self.atacando = False
                self.tempo_ataque = 0

                # ALTERAÇÃO: comandos armazenados são executados ao finalizar o golpe.
                # O chute tem prioridade; socos continuam usando o buffer anterior.
                if self.chute_pendente and not self.pulando:
                    self.chute_pendente = False
                    self._iniciar_chute()
                elif (
                    self.ataque_pendente
                    and not self.pulando
                    and tipo_finalizado != "chute"
                ):

                    self.ataque_pendente = False
                    self._iniciar_jab_ou_direto()

        # ----------------------------------------------------
        # MOVIMENTO
        # ----------------------------------------------------

        if (
            not self.atacando
            and not self.recebendo_dano
            and not self.caida
            and not self.levantando
            and not self.eliminada
        ):

            if teclado.key_pressed("RIGHT"):
                self.x += self.VELOCIDADE * dt
                self.direcao = "direita"
                self.andando = True

            if teclado.key_pressed("LEFT"):
                self.x -= self.VELOCIDADE * dt
                self.direcao = "esquerda"
                self.andando = True

            if teclado.key_pressed("UP"):
                self.y -= self.VELOCIDADE * dt
                self.andando = True

            if teclado.key_pressed("DOWN"):
                self.y += self.VELOCIDADE * dt
                self.andando = True

        # ----------------------------------------------------
        # LIMITES DO MUNDO
        # ----------------------------------------------------

        if self.x < 0:
            self.x = 0

        if self.x > largura_mundo - self.largura:
            self.x = largura_mundo - self.largura

        limite_superior = (
            altura_mundo
            - self.ALTURA_PISTA
            - self.altura
        )

        limite_inferior = (
            altura_mundo
            - self.altura
        )

        if self.y < limite_superior:
            self.y = limite_superior

        if self.y > limite_inferior:
            self.y = limite_inferior


    # ========================================================
    # ALTERAÇÃO: SELECIONA SOMENTE O SPRITE ATIVO
    # ========================================================

    def _sprite_ativo(self):

        # ALTERAÇÃO: armada tem prioridade visual sobre ataques desarmados.
        if self.armada and not (self.caida or self.levantando or self.recebendo_dano):
            if self.pulando and self.atirando:
                return self.tiro_aereo_direita if self.direcao == "direita" else self.tiro_aereo_esquerda
            if self.pulando:
                return self.salto_armada_direita if self.direcao == "direita" else self.salto_armada_esquerda
            if self.atirando:
                return self.tiro_chao_direita if self.direcao == "direita" else self.tiro_chao_esquerda
            if self.andando:
                return self.andando_armada_direita if self.direcao == "direita" else self.andando_armada_esquerda
            # ALTERAÇÃO: parado armado usa o primeiro quadro da caminhada armada.
            sprite = self.andando_armada_direita if self.direcao == "direita" else self.andando_armada_esquerda
            sprite.set_curr_frame(0)
            return sprite

        if self.caida or self.levantando:
            return self.queda_direita if self.direcao == "direita" else self.queda_esquerda

        if self.recebendo_dano:
            return self.dano_direita if self.direcao == "direita" else self.dano_esquerda

        if self.pulando:
            return self.salto_direita if self.direcao == "direita" else self.salto_esquerda

        if self.atacando:
            if self.tipo_ataque == "jab":
                return self.jab_direita if self.direcao == "direita" else self.jab_esquerda
            if self.tipo_ataque == "direto":
                return self.direto_direita if self.direcao == "direita" else self.direto_esquerda
            return self.chute_direita if self.direcao == "direita" else self.chute_esquerda

        if self.andando:
            return self.andando_direita if self.direcao == "direita" else self.andando_esquerda

        return self.idle_direita if self.direcao == "direita" else self.idle_esquerda

    # ========================================================
    # ALTERAÇÃO: ATUALIZA ANIMAÇÃO SEPARADAMENTE DO DESENHO
    # ========================================================

    def atualizar_animacao(self):

        if self.caida or self.levantando or self.eliminada or self.recebendo_dano:
            return  # Poses fixas não avançam frames.

        sprite = self._sprite_ativo()

        # ALTERAÇÃO: pose armada parada mantém o quadro 0 congelado.
        if self.armada and not self.pulando and not self.atirando and not self.andando:
            return
        # Preserva o play() contínuo da caminhada e do idle.
        if not self.pulando and not self.atacando and not self.atirando:
            sprite.play()
        sprite.update()

    # ========================================================
    # DESENHO
    # ========================================================

    def desenhar(self):

        # ALTERAÇÃO: guarda preservada para o futuro sistema de vidas.
        # A Noiva não é marcada como removida nesta versão.
        if self.removida:
            return

        # ALTERAÇÃO: pisca o sprite de queda somente após perder a ÚLTIMA vida.
        # Usa o tempo da própria queda (DT), sem temporizador externo nem
        # modificar a imagem original. As quedas normais não piscam.
        if self.eliminada and self.caida:
            if (self.tempo_caida % self.INTERVALO_PISCADA_MORTE) < self.INTERVALO_PISCADA_MORTE / 2:
                return

        sprite = self._sprite_ativo()

        # ALTERAÇÃO: posiciona só o sprite que será desenhado.
        # ALTERAÇÃO: posições de mundo; Sprite.draw() aplica a câmera.
        # ALTERAÇÃO: centraliza sprites de larguras diferentes na mesma
        # referência visual (idle de 480 px; caminhada de 224 px).
        # Mantém o centro do corpo próximo à hitbox existente (X = 240).
        ajuste_x = (self.idle_direita.width - sprite.width) / 2
        x_mundo = self.x + ajuste_x
        y_mundo = self.y - self.altura_pulo - self.altura_plataforma
        sprite.set_position(x_mundo, y_mundo)
        sprite.draw()
