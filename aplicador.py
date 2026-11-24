import math
from PPlay.sprite import Sprite


# ============================================================
# ALTERAÇÃO: APLICADOR DE CHANTILLY - COLETA E PROJÉTEIS
# ============================================================

class Aplicador:
    VELOCIDADE_QUEDA = 450          # px/s até tocar o chão
    VELOCIDADE_TIRO = 720          # px/s, não persegue o alvo
    RAIO_TIRO = 22                 # raio lógico do chantilly
    MARGEM_SAIDA = 100
    TEMPO_ANIMACAO_TIRO = 450      # 3 quadros de 150 ms
    PONTOS_INIMIGO = 30
    PONTOS_BOSS = 50

    def __init__(self):
        self.sprite_chao = Sprite("assets/objetos/aplicador-coleta.png", 1)
        self.ativa = False
        self.coletada = False
        self.caindo = False
        self.x = 0.0
        self.y = 0.0
        self.y_chao = 0.0
        self.tiros = []

    def soltar(self, camera_x, largura_tela, altura_tela, noiva):
        # ALTERAÇÃO: só ocorre uma vez, após o primeiro projétil da Boss desaparecer.
        if self.ativa or self.coletada:
            return
        self.ativa = True
        self.caindo = True
        # Posição do aplicador é em coordenadas do mundo, sobre o chão da arena.
        self.x = camera_x + largura_tela * 0.42 - self.sprite_chao.width / 2
        self.y = 170
        # Referência de chão baseada nos pés da Noiva no instante da queda.
        self.y_chao = min(altura_tela - self.sprite_chao.height - 24,
                          max(altura_tela - 230,
                              noiva.y + noiva.altura - self.sprite_chao.height))

    def atualizar_coleta(self, dt, noiva):
        if not self.ativa or self.coletada:
            return
        if self.caindo:
            self.y = min(self.y_chao, self.y + self.VELOCIDADE_QUEDA * dt)
            if self.y >= self.y_chao:
                self.caindo = False
        else:
            # ALTERAÇÃO: coleta ao passar pela arma no chão; salto não é obrigatório.
            centro_arma_x = self.x + self.sprite_chao.width / 2
            pe_noiva_y = noiva.y + noiva.altura
            pe_arma_y = self.y + self.sprite_chao.height
            if (abs(noiva.centro_x - centro_arma_x) <= 85
                    and abs(pe_noiva_y - pe_arma_y) <= 110
                    and not noiva.eliminada):
                noiva.armada = True
                self.coletada = True
                self.ativa = False

    def disparar(self, noiva, sogra_boss):
        # ALTERAÇÃO: arma dispara uma única vez por solicitação de Z ou C.
        sprite = Sprite("assets/objetos/chantilly-projetil.png", 3)
        sprite.set_total_duration(self.TEMPO_ANIMACAO_TIRO)
        sprite.play()

        sinal = 1 if noiva.direcao == "direita" else -1
        origem_x = noiva.centro_x + sinal * 105
        origem_y = noiva.centro_y_colisao_aerea - 22
        vx = sinal * self.VELOCIDADE_TIRO
        vy = 0.0

        # ALTERAÇÃO: mira na Boss uma única vez, se ela estiver à frente.
        # Fora da arena, o tiro segue horizontalmente como num beat 'em up.
        if sogra_boss.ativa:
            sprite_boss = sogra_boss._sprite_ativo()
            alvo_x = sogra_boss.x + sprite_boss.width / 2
            alvo_y = sogra_boss.y + sprite_boss.height / 2
            dx = alvo_x - origem_x
            dy = alvo_y - origem_y
            if dx * sinal > 0:
                distancia = max(0.001, math.hypot(dx, dy))
                vx = dx / distancia * self.VELOCIDADE_TIRO
                vy = dy / distancia * self.VELOCIDADE_TIRO

        self.tiros.append({"sprite": sprite, "x": origem_x, "y": origem_y,
                           "vx": vx, "vy": vy})

    def atualizar_tiros(self, dt, camera_x, largura_tela, altura_tela, inimigos, sogra_boss, noiva, dama_boss=None):
        pontos = 0
        for tiro in self.tiros[:]:
            tiro["x"] += tiro["vx"] * dt
            tiro["y"] += tiro["vy"] * dt
            tiro["sprite"].update()

            # ALTERAÇÃO: testa primeiro os inimigos comuns no caminho do projétil.
            acertou = False
            for inimigo in inimigos:
                if not inimigo.entrada_liberada:
                    continue
                if hasattr(inimigo, "removido"):
                    inativo = (inimigo.removido or inimigo.caindo or inimigo.derrotado
                               or inimigo.levantando or inimigo.recebendo_dano)
                else:
                    inativo = (inimigo.estado in ["removida", "eliminada", "caindo",
                                               "caida", "levantando", "dano"])
                if inativo:
                    continue
                if (abs(tiro["x"] - inimigo.centro_x) <= inimigo.LARGURA_CORPO / 2 + self.RAIO_TIRO
                        and abs(tiro["y"] - inimigo.centro_y) <= 80):
                    # Mesma rotina que conta os golpes e inicia a queda.
                    if hasattr(inimigo, "removido"):
                        inimigo._receber_golpe(noiva)
                    else:
                        inimigo._receber_golpe()
                    pontos += self.PONTOS_INIMIGO
                    acertou = True
                    break

            if acertou:
                self.tiros.remove(tiro)
                continue

            # ALTERAÇÃO: acerto na cabeça da Sogra vale 50 pontos.
            # Durante a pose de dano o projétil pode sumir, mas não dá novo hit.
            if sogra_boss.ativa and sogra_boss.estado != "derrota":
                sprite_boss = sogra_boss._sprite_ativo()
                cx = sogra_boss.x + sprite_boss.width / 2
                cy = sogra_boss.y + sprite_boss.height / 2
                raio_x = min(125, sprite_boss.width * 0.34)
                raio_y = min(125, sprite_boss.height * 0.34)
                if (abs(tiro["x"] - cx) <= raio_x + self.RAIO_TIRO
                        and abs(tiro["y"] - cy) <= raio_y + self.RAIO_TIRO):
                    # ALTERAÇÃO: o Boss decide se é um hit válido (não repete
                    # pontuação durante a pausa de dano ou a animação final).
                    if sogra_boss.receber_dano():
                        pontos += self.PONTOS_BOSS
                    self.tiros.remove(tiro)
                    continue

            # ALTERAÇÃO: projéteis da Fase 2 também acertam a Dama, se vulnerável.
            # O tiro é consumido ao tocar o corpo, mesmo se ela estiver invulnerável.
            if dama_boss is not None and dama_boss.estado != 'derrotada':
                cx = dama_boss.centro_x
                cy = dama_boss.centro_y
                if (abs(tiro["x"] - cx) <= dama_boss.largura * 0.28 + self.RAIO_TIRO
                        and abs(tiro["y"] - cy) <= dama_boss.altura * 0.40 + self.RAIO_TIRO):
                    if dama_boss.receber_dano():
                        pontos += dama_boss.PONTOS_TIROS_DAMA
                    self.tiros.remove(tiro)
                    continue

            x_tela = tiro["x"] - camera_x
            if (x_tela < -self.MARGEM_SAIDA
                    or x_tela > largura_tela + self.MARGEM_SAIDA
                    or tiro["y"] < -self.MARGEM_SAIDA
                    or tiro["y"] > altura_tela + self.MARGEM_SAIDA):
                self.tiros.remove(tiro)

        return pontos

    def desenhar(self):
        if self.ativa and not self.coletada:
            self.sprite_chao.set_position(self.x, self.y)
            self.sprite_chao.draw()
        for tiro in self.tiros:
            sprite = tiro["sprite"]
            sprite.set_position(tiro["x"] - sprite.width / 2,
                                tiro["y"] - sprite.height / 2)
            sprite.draw()
