"""Mesa 2 — objeto escalável e colisão experimental da Fase 2 (PPlay 2.1)."""
from pathlib import Path
import pygame
from PPlay.sprite import Sprite

# ============================================================
# ALTERAÇÃO: AJUSTES DA MESA (COORDENADAS DO MUNDO DA FASE 2)
# ============================================================
MESA_2 = {
    'arquivo': 'assets/objetos/mesa-2.png',
    'escala': 0.42,                # altura do PNG 1086 * 0.42 = 456 px; sprite da Noiva ~300 px
    'deslocamento_x': 0,         # deslocamento relativo ao centro da fase
    'y': 390,                    # canto superior do PNG, incluindo transparências
    'altura_tampo': 125,         # altura física acima do chão (px do jogo)
    # Região física aproximada, em proporção à imagem redimensionada.
    # A borda transparente do arquivo NÃO faz parte da colisão.
    'hitbox_x_inicio': 0.10,
    'hitbox_x_fim': 0.90,
    'hitbox_y_inicio': 0.44,
    'hitbox_y_fim': 0.68,
    'velocidade_descida': 480,   # queda ao deixar o tampo (px/s)
}

class Mesa2:
    def __init__(self, centro_mundo_x):
        cfg = MESA_2
        arquivo = Path(__file__).resolve().parent / cfg['arquivo']
        if not arquivo.is_file():
            raise FileNotFoundError(f'Mesa 2 não encontrada: {arquivo}')
        imagem = pygame.image.load(str(arquivo)).convert_alpha()
        larg, alt = imagem.get_size()
        self.largura = max(1, round(larg * cfg['escala']))
        self.altura = max(1, round(alt * cfg['escala']))
        cache = arquivo.parent / '.cache_escala'
        cache.mkdir(exist_ok=True)
        destino = cache / f'mesa-2_{self.largura}x{self.altura}.png'
        if not destino.exists() or arquivo.stat().st_mtime > destino.stat().st_mtime:
            pygame.image.save(pygame.transform.smoothscale(imagem, (self.largura, self.altura)), str(destino))
        self.sprite = Sprite(str(destino))
        self.x = float(centro_mundo_x + cfg['deslocamento_x'] - self.largura / 2)
        self.y = float(cfg['y'])
        self.altura_tampo = float(cfg['altura_tampo'])
        self.noiva_no_tampo = False
        self.altura_salto_anterior = 0.0
        self.y_ordenacao = self.y + self.altura * 0.35

    def _dentro_area(self, noiva):
        cfg = MESA_2
        return (self.x + self.largura * cfg['hitbox_x_inicio'] <= noiva.centro_x <=
                self.x + self.largura * cfg['hitbox_x_fim'] and
                self.y + self.altura * cfg['hitbox_y_inicio'] <= noiva.centro_y <=
                self.y + self.altura * cfg['hitbox_y_fim'])

    def atualizar_colisao(self, noiva, x_anterior, y_anterior, dt):
        """Bloqueia a base e permite pousar no tampo ao descer do salto."""
        dentro = self._dentro_area(noiva)

        # ALTERAÇÃO: se está sobre a mesa, permanece elevado até sair da sua área.
        if self.noiva_no_tampo:
            if not dentro:
                self.noiva_no_tampo = False
            else:
                noiva.altura_plataforma = self.altura_tampo

        # ALTERAÇÃO: ao sair, desce sem teletransporte instantâneo.
        if not self.noiva_no_tampo and noiva.altura_plataforma > 0:
            noiva.altura_plataforma = max(
                0.0, noiva.altura_plataforma - MESA_2['velocidade_descida'] * dt
            )

        # ALTERAÇÃO: aterrissagem na descida, após ultrapassar a altura do tampo.
        if (not self.noiva_no_tampo and dentro and noiva.pulando
                and noiva.tempo_salto >= noiva.duracao_salto / 2
                and self.altura_salto_anterior >= self.altura_tampo
                and noiva.altura_pulo <= self.altura_tampo):
            self.noiva_no_tampo = True
            noiva.altura_plataforma = self.altura_tampo
            noiva.altura_pulo = 0
            noiva.pulando = False
            noiva.tempo_salto = 0

        # ALTERAÇÃO: a Noiva não atravessa a mesa no chão.
        if (not self.noiva_no_tampo and dentro and
                noiva.altura_pulo + noiva.altura_plataforma < self.altura_tampo):
            # Resolver separadamente os eixos preserva o movimento tangencial.
            x_novo, y_novo = noiva.x, noiva.y
            noiva.x = x_anterior
            if self._dentro_area(noiva):
                noiva.x = x_novo
                noiva.y = y_anterior
                if self._dentro_area(noiva):
                    noiva.x, noiva.y = x_anterior, y_anterior
            # Se x_anterior sozinho resolve, manter o y já atualizado.

        self.altura_salto_anterior = noiva.altura_pulo

    def desenhar(self):
        # Sprite.draw() utiliza automaticamente a câmera nativa da PPlay 2.1.
        self.sprite.set_position(self.x, self.y)
        self.sprite.draw()
