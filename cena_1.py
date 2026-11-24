"""Cena 1 — abertura do Wedding Panic, compatível com Power PPlay 2.1.

Use Cena1() via SceneManager.change_scene(Cena1()).
As configurações da cena ficam concentradas no topo deste arquivo.
Execute `python cena_1.py` para visualizar isoladamente (pela raiz do projeto).
"""

from pathlib import Path
import pygame
from PPlay.sprite import Sprite
from PPlay.gameimage import GameImage  # ALTERAÇÃO: fundo fixo via PPlay 2.1
from PPlay.scenemanager import Scene, SceneManager


# ============================================================
# CONFIGURAÇÕES GERAIS DA CENA — EDITE AQUI
# ============================================================
LARGURA_CENA = 1600
ALTURA_CENA = 900
COR_FUNDO = (13, 18, 29)
# ALTERAÇÃO: cena_1.py fica junto de main.py; os recursos ficam em ./cenas.
PASTA_CENAS = Path(__file__).resolve().parent / 'cenas'
PASTA_CACHE = PASTA_CENAS / '.cache_escala'
ARQUIVO_CENARIO = 'cenario-cena-1-900.png'

# Se desejar, desative a marcação temporária do Noivo caso sua imagem falte.
DESENHAR_NOIVO_PROVISORIO = True
MOSTRAR_DEBUG = False              # True: imprime cronômetro e estados na tela.
FIM_CENA_APOS_NOIVA_MS = 4000      # A cena termina este tempo após a Noiva terminar de observar.

# ALTERAÇÃO: cada personagem tem posição, escala, tempo de início,
# quantidade de frames, duração da animação (ms) e velocidade (px/s).
# Posições representam o canto superior esquerdo da spritesheet.
# As escalas são multiplicadores (1.0 = altura original de 300 px).
AMIGOS_ANDANDO = {
    'arquivo': 'spritesheet_amigos-andando.png',
    'frames': 16, 'x': 20, 'y': 255, 'escala': 0.85,
    'inicio': 0.5, 'duracao_ms': 3000, 'velocidade': 100,
}
AMIGOS_CARREGANDO = {
    'arquivo': 'spritesheet-amigos-carregando.png',
    'frames': 16, 'x': 55, 'y': 255, 'escala': 1.1,
    'inicio': 0.0, 'duracao_ms': 3000, 'velocidade': 150,
    'espera_antes_mover': 0.5,
}
NOIVO_PARADO = {
    # ALTERAÇÃO: este arquivo não estava no ZIP de recursos verificado.
    # Ajuste este nome para o arquivo verdadeiro quando disponibilizá-lo.
    'arquivo': 'sprite-noivo-parado.png',
    'frames': 1, 'x': 590, 'y': 250, 'escala': 0.85,
    'inicio': 0.0, 'duracao_ms': 1000, 'velocidade': 0,
    'largura_provisoria': 115, 'altura_provisoria': 255,
}
SOGRA_PARADA = {
    'arquivo': 'spritesheet-sogra-parada.png',
    'frames': 1, 'x': 950, 'y': 250, 'escala': 0.85,
    'inicio': 0.0, 'duracao_ms': 3000, 'velocidade': 0,
}
SOGRA_ANDANDO = {
    'arquivo': 'spritesheet_sogra-andando.png',
    'frames': 16, 'x': 950, 'y': 250, 'escala': 0.85,
    'inicio': 0.0, 'duracao_ms': 3000, 'velocidade': 150,
    'deslocamento_gatilho_x': 230,
}
DAMA_ANDANDO = {
    'arquivo': 'spritesheet_dama-andando.png',
    'frames': 16, 'x': 1080, 'y': 250, 'escala': 0.85,
    'inicio': 0.0, 'duracao_ms': 3000, 'velocidade': 150,
    # ALTERAÇÃO: gatilho independente da Sogra (distância em px após o centro da Dama).
    'deslocamento_gatilho_x': 290,
}
NOIVA_OBSERVA = {
    'arquivo': 'spritesheet-noiva-observa.png',
    'frames': 16, 'x': 700, 'y': 600, 'escala': 1.0,
    'inicio': 0.0, 'duracao_ms': 3000, 'velocidade': 0,
    'gatilho_borda_direita': 5,
}


# ============================================================
# ANIMAÇÃO INDIVIDUAL ESCALÁVEL
# ============================================================
class AtorCena:
    def __init__(self, config, nome):
        self.config = config
        self.nome = nome
        self.x = float(config['x'])
        self.y = float(config['y'])
        self.frames = int(config['frames'])
        self.escala = float(config['escala'])
        self.duracao = max(0.001, config['duracao_ms'] / 1000)
        self.velocidade = float(config['velocidade'])
        self.tempo_animacao = 0.0
        self.visivel = True
        self.animando = False
        self.sprite = None
        self.fallback = False
        self.largura = float(config.get('largura_provisoria', 100))
        self.altura = float(config.get('altura_provisoria', 300))

        origem = PASTA_CENAS / config['arquivo']
        if not origem.exists():
            self.fallback = True
            print(f'[Cena 1] Arquivo ausente ({nome}): {origem}')
            return

        # ALTERAÇÃO: Sprite 2.1 não possui set_scale().
        # Redimensionamos a tira UMA VEZ antes de instanciar o Sprite.
        # Os arquivos originais NÃO são sobrescritos.
        PASTA_CACHE.mkdir(exist_ok=True)
        imagem = pygame.image.load(str(origem)).convert_alpha()
        largura_original, altura_original = imagem.get_size()
        if largura_original % self.frames != 0:
            raise ValueError(f'{config["arquivo"]}: a largura não é divisível por {self.frames} frames')
        largura_frame = largura_original // self.frames
        largura_escalada_frame = max(1, round(largura_frame * self.escala))
        altura_escalada = max(1, round(altura_original * self.escala))
        self.largura = largura_escalada_frame
        self.altura = altura_escalada

        if abs(self.escala - 1.0) < 0.0001:
            arquivo_sprite = origem
        else:
            nome_cache = f'{origem.stem}_{self.frames}f_{largura_escalada_frame}x{altura_escalada}.png'
            arquivo_sprite = PASTA_CACHE / nome_cache
            if not arquivo_sprite.exists() or origem.stat().st_mtime > arquivo_sprite.stat().st_mtime:
                # Redimensionar separadamente cada quadro mantém larguras uniformes.
                tira = pygame.Surface((largura_escalada_frame * self.frames, altura_escalada), pygame.SRCALPHA)
                for quadro in range(self.frames):
                    recorte = imagem.subsurface((quadro * largura_frame, 0, largura_frame, altura_original))
                    escalado = pygame.transform.smoothscale(recorte, (largura_escalada_frame, altura_escalada))
                    tira.blit(escalado, (quadro * largura_escalada_frame, 0))
                pygame.image.save(tira, str(arquivo_sprite))

        self.sprite = Sprite(str(arquivo_sprite), self.frames)
        self.sprite.set_total_duration(config['duracao_ms'])
        self.sprite.set_loop(True)
        self.sprite.stop()  # frame zero para todos os personagens que começam parados

    @property
    def centro_x(self):
        return self.x + self.largura / 2

    @property
    def borda_direita(self):
        return self.x + self.largura

    def iniciar(self):
        if not self.animando:
            self.animando = True
            self.tempo_animacao = 0.0
            if self.sprite is not None:
                self.sprite.set_curr_frame(0)

    def atualizar(self, dt, deslocamento_x=0, repetir=True):
        if not self.visivel:
            return
        self.x += deslocamento_x
        if self.animando:
            self.tempo_animacao += dt
            if repetir:
                progresso = (self.tempo_animacao % self.duracao) / self.duracao
            else:
                progresso = min(1.0, self.tempo_animacao / self.duracao)
            frame = min(self.frames - 1, int(progresso * self.frames))
            if self.sprite is not None:
                self.sprite.set_curr_frame(frame)
            if not repetir and self.tempo_animacao >= self.duracao:
                self.animando = False

    def desenhar(self, tela):
        if not self.visivel:
            return
        if self.sprite is not None:
            self.sprite.set_position(self.x, self.y)
            self.sprite.draw()
        elif self.fallback and self.nome == 'Noivo' and DESENHAR_NOIVO_PROVISORIO:
            # Apenas marca visual temporária; substituída pelo PNG real automaticamente.
            rect = pygame.Rect(round(self.x), round(self.y), round(self.largura), round(self.altura))
            pygame.draw.rect(tela, (65, 92, 135), rect, 3)
            font = pygame.font.Font(None, 25)
            tela.blit(font.render('NOIVO', True, (255, 255, 255)), (rect.x + 14, rect.y + 20))


# ============================================================
# CENA DE ABERTURA (SCENE / SCENEMANAGER DA PPLAY 2.1)
# ============================================================
class Cena1(Scene):
    def __init__(self):
        super().__init__()  # obrigatório: inicializa janela, teclado, mouse no PPlay 2.1

        self.tempo_cena = 0.0
        self.tempo_carregando = 0.0
        self.tempo_final = 0.0
        self.concluida = False
        self.proxima_cena = None  # pode ser um callback/instância definido pela integração futura

        # ALTERAÇÃO: carregar e desenhar o fundo com GameImage da PPlay 2.1.
        # O arquivo deve estar dentro da subpasta "cenas", ao lado deste script.
        caminho_fundo = PASTA_CENAS / ARQUIVO_CENARIO
        if not caminho_fundo.is_file():
            raise FileNotFoundError(f'Imagem de fundo não encontrada: {caminho_fundo}')
        self.fundo = GameImage(str(caminho_fundo))
        self.fundo.set_position(0, 0)
        # ALTERAÇÃO: ajustar o fundo para preencher a janela sem mudar o PNG original.
        if (self.fundo.width, self.fundo.height) != (self.janela.width, self.janela.height):
            self.fundo.image = pygame.transform.smoothscale(
                self.fundo.image, (self.janela.width, self.janela.height)
            )
            self.fundo.width, self.fundo.height = self.janela.width, self.janela.height
        print(f'[Cena 1] Fundo carregado: {caminho_fundo} ({self.fundo.width} x {self.fundo.height})')

        self.amigos_andando = AtorCena(AMIGOS_ANDANDO, 'Amigos andando')
        self.amigos_carregando = AtorCena(AMIGOS_CARREGANDO, 'Amigos carregando')
        self.noivo = AtorCena(NOIVO_PARADO, 'Noivo')
        self.sogra_parada = AtorCena(SOGRA_PARADA, 'Sogra parada')
        self.sogra_andando = AtorCena(SOGRA_ANDANDO, 'Sogra andando')
        self.dama = AtorCena(DAMA_ANDANDO, 'Dama')
        self.noiva = AtorCena(NOIVA_OBSERVA, 'Noiva observa')

        self.amigos_carregando.visivel = False
        self.sogra_andando.visivel = False
        self.estado_amigos = 'parados'
        self.sogra_ativada = False
        self.dama_ativada = False  # ALTERAÇÃO: a Dama começa a andar por gatilho próprio.
        self.noiva_ativada = False
        self.tempo_noiva = 0.0

    def loop(self):
        if self.concluida:
            return
        dt = min(self.janela.delta_time(), 0.10)
        self.tempo_cena += dt

        # ----------------------------------------------------
        # AMIGOS: parados -> andando -> carregando parado -> saindo
        # ----------------------------------------------------
        if self.estado_amigos == 'parados' and self.tempo_cena >= AMIGOS_ANDANDO['inicio']:
            self.estado_amigos = 'andando'
            self.amigos_andando.iniciar()

        if self.estado_amigos == 'andando':
            self.amigos_andando.atualizar(dt, self.amigos_andando.velocidade * dt)
            # ALTERAÇÃO: gatilho exato pelo CENTRO, como solicitado.
            if self.amigos_andando.centro_x >= self.noivo.centro_x:
                centro_grupo = self.amigos_andando.centro_x
                self.amigos_andando.visivel = False
                self.noivo.visivel = False
                self.amigos_carregando.visivel = True
                self.amigos_carregando.x = centro_grupo - self.amigos_carregando.largura / 2
                # ALTERAÇÃO: compensa a diferença de altura causada pelas escalas.
                # Alinha os pés com o sprite anterior quando ambos usam o mesmo Y.
                # O Y próprio dos amigos carregando continua ajustável no dicionário.
                self.amigos_carregando.y = (
                    AMIGOS_CARREGANDO['y']
                    + self.amigos_andando.altura
                    - self.amigos_carregando.altura
                )
                self.amigos_carregando.iniciar()
                self.tempo_carregando = 0
                self.estado_amigos = 'carregando_parados'

        elif self.estado_amigos == 'carregando_parados':
            self.tempo_carregando += dt
            # Mantém os amigos parados 0,5s; a animação continua.
            self.amigos_carregando.atualizar(dt)
            if self.tempo_carregando >= AMIGOS_CARREGANDO['espera_antes_mover']:
                self.estado_amigos = 'saindo'

        elif self.estado_amigos == 'saindo':
            self.amigos_carregando.atualizar(dt, self.amigos_carregando.velocidade * dt)

        # ----------------------------------------------------
        # ALTERAÇÃO: SOGRA e DAMA têm gatilhos de início independentes.
        # Cada distância é medida a partir do centro do seu próprio sprite.
        # ----------------------------------------------------
        if (self.estado_amigos == 'saindo' and not self.sogra_ativada and
                self.amigos_carregando.centro_x >=
                self.sogra_parada.centro_x + SOGRA_ANDANDO['deslocamento_gatilho_x']):
            self.sogra_ativada = True
            self.sogra_parada.visivel = False
            self.sogra_andando.visivel = True
            self.sogra_andando.x = self.sogra_parada.x
            self.sogra_andando.y = self.sogra_parada.y
            self.sogra_andando.iniciar()

        # ALTERAÇÃO: a Dama agora aguarda seu próprio gatilho.
        if (self.estado_amigos == 'saindo' and not self.dama_ativada and
                self.amigos_carregando.centro_x >=
                self.dama.centro_x + DAMA_ANDANDO['deslocamento_gatilho_x']):
            self.dama_ativada = True
            self.dama.iniciar()

        if self.sogra_ativada:
            self.sogra_andando.atualizar(dt, self.sogra_andando.velocidade * dt)

        if self.dama_ativada:
            self.dama.atualizar(dt, self.dama.velocidade * dt)

        # ----------------------------------------------------
        # NOIVA: começa quando a borda direita dos amigos chega a 5px
        # da borda da janela. Anima uma única vez (sem loop).
        # ----------------------------------------------------
        if (self.estado_amigos == 'saindo' and not self.noiva_ativada and
                self.amigos_carregando.borda_direita >=
                self.janela.width - NOIVA_OBSERVA['gatilho_borda_direita']):
            self.noiva_ativada = True
            self.noiva.iniciar()
            self.tempo_noiva = 0.0
            # ALTERAÇÃO: não ocultar nem interromper os amigos carregando.
            # O estado continua 'saindo', portanto caminham até sair da tela naturalmente.

        if self.noiva_ativada:
            self.noiva.atualizar(dt, repetir=False)
            self.tempo_noiva += dt
            if self.tempo_noiva >= self.noiva.duracao + FIM_CENA_APOS_NOIVA_MS / 1000:
                self.concluida = True
                # Não forçamos mudança para menu/fase inexistente nesta etapa.

    def draw(self):
        # ALTERAÇÃO: GameImage desenha no buffer da PPlay; o fundo vem antes dos sprites.
        self.fundo.draw()
        tela = pygame.display.get_surface()
        self.sogra_parada.desenhar(tela)
        self.sogra_andando.desenhar(tela)
        self.dama.desenhar(tela)
        self.noivo.desenhar(tela)
        self.amigos_andando.desenhar(tela)
        self.amigos_carregando.desenhar(tela)
        self.noiva.desenhar(tela)
        if MOSTRAR_DEBUG:
            fonte = pygame.font.Font(None, 26)
            linhas = [f'tempo: {self.tempo_cena:.2f}s',
                      f'amigos: {self.estado_amigos}',
                      f'sogra: {self.sogra_ativada} | noiva: {self.noiva_ativada}',
                      f'concluida: {self.concluida}']
            for i, linha in enumerate(linhas):
                tela.blit(fonte.render(linha, True, (255, 240, 30)), (15, 15 + 28 * i))


# ============================================================
# EXECUÇÃO ISOLADA PARA TESTE, SEM TOCAR NO MAIN.PY ATUAL
# ============================================================
if __name__ == '__main__':
    from PPlay.window import Window

    janela = Window(LARGURA_CENA, ALTURA_CENA, 'Wedding Panic — Cena 1')
    SceneManager.change_scene(Cena1())
    while True:
        SceneManager.run()
        janela.update()
