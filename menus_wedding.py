"""Menus, pausa e ranking do Wedding Panic — PPlay 2.1/Pygame.

# ALTERAÇÃO: interface separada do gameplay e salvamento em ranking.txt.
Formato do ranking do Space Invaders: nome; pontos; data (5 melhores exibidos).
"""
from pathlib import Path
from datetime import datetime
import pygame

PASTA_JOGO = Path(__file__).resolve().parent
ARQUIVO_RANKING = PASTA_JOGO / 'ranking.txt'
LIMITE_EXIBIDO = 5
MAXIMO_REGISTROS = 100
LIMITE_NOME = 14

COR_FUNDO = (18, 21, 35)
COR_PAINEL = (35, 39, 61)
COR_TEXTO = (247, 239, 234)
COR_DESTAQUE = (255, 183, 129)
COR_BOTAO = (67, 53, 81)
COR_BOTAO_ATIVO = (120, 68, 104)


def ler_ranking():
    """Lê ranking.txt, ignorando linhas incompletas sem travar o jogo."""
    registros = []
    if ARQUIVO_RANKING.is_file():
        try:
            for linha in ARQUIVO_RANKING.read_text(encoding='utf-8-sig').splitlines():
                partes = [campo.strip() for campo in linha.split(';')]
                if len(partes) != 3:
                    continue
                nome, pontos, data = partes
                try:
                    pontos = int(pontos)
                except ValueError:
                    continue
                if nome and pontos >= 0:
                    registros.append((nome, pontos, data))
        except OSError as erro:
            print('[Ranking] Não foi possível ler:', erro)
    return sorted(registros, key=lambda registro: -registro[1])[:MAXIMO_REGISTROS]


def registrar_pontuacao(nome, pontos):
    nome = ' '.join(nome.replace(';', ' ').split())[:LIMITE_NOME] or 'NOIVA'
    registros = ler_ranking()
    registros.append((nome, max(0, int(pontos)), datetime.now().strftime('%d/%m/%Y')))
    registros.sort(key=lambda registro: -registro[1])
    registros = registros[:MAXIMO_REGISTROS]
    try:
        ARQUIVO_RANKING.write_text(
            ''.join(f'{jogador}; {valor}; {data}\n' for jogador, valor, data in registros),
            encoding='utf-8'
        )
    except OSError as erro:
        print('[Ranking] Não foi possível salvar:', erro)
        return False
    return True


class MenusWedding:
    """Interface de menus em coordenadas da janela; não altera a câmera."""

    def __init__(self, janela):
        self.janela = janela
        # ALTERAÇÃO: desenhar no buffer da PPlay, apresentado por janela.update().
        self.tela = janela.screen
        self.tela_menu = 'principal'
        self.opcao = 0
        self.nome = ''
        self.pontos_finais = 0
        self.mensagem = ''
        self.fonte_titulo = pygame.font.SysFont('arial', 74, bold=True)
        self.fonte = pygame.font.SysFont('arial', 33, bold=True)
        self.fonte_menor = pygame.font.SysFont('arial', 24)
        self.fonte_pontos = pygame.font.SysFont('arial', 30)
        self._mouse_pressionado = False
        self._teclas_anteriores = set()
        # ALTERAÇÃO: imagem original do menu principal, sem título/subtítulo sobrepostos.
        self.fundo_menu_principal = pygame.image.load(str(
            PASTA_JOGO / 'assets' / 'img-fundos' / 'menu.png'
        )).convert()
        self.fundo_menu_principal = pygame.transform.smoothscale(
            self.fundo_menu_principal, (self.janela.width, self.janela.height)
        )

    def abrir(self, tela, pontos=0):
        self.tela_menu = tela
        self.opcao = 0
        self._mouse_pressionado = bool(pygame.mouse.get_pressed()[0])
        self._teclas_anteriores.clear()
        self.mensagem = ''
        if tela == 'nome':
            self.nome = ''
            self.pontos_finais = int(pontos)

    def _pressionou(self, tecla):
        pressionado = bool(pygame.key.get_pressed()[tecla])
        anterior = tecla in self._teclas_anteriores
        if pressionado:
            self._teclas_anteriores.add(tecla)
        else:
            self._teclas_anteriores.discard(tecla)
        return pressionado and not anterior

    def _opcoes(self):
        if self.tela_menu == 'principal':
            return [('JOGAR', 'jogar'), ('RANKING', 'ranking'), ('CONTROLES', 'controles'), ('SAIR', 'sair')]
        if self.tela_menu == 'pausa':
            return [('CONTINUAR', 'continuar'), ('REINICIAR', 'reiniciar'),
                    ('ENCERRAR E SALVAR', 'encerrar'), ('MENU PRINCIPAL', 'menu')]
        if self.tela_menu == 'ranking':
            return [('VOLTAR', 'voltar')]
        if self.tela_menu == 'controles':
            return [('VOLTAR', 'voltar')]
        if self.tela_menu == 'nome':
            return [('SALVAR PONTUACAO', 'salvar')]
        return []

    def atualizar(self):
        """Retorna uma ação somente após interação. Não atualiza o gameplay."""
        pygame.event.pump()
        evento_texto = []
        for evento in pygame.event.get([pygame.QUIT, pygame.KEYDOWN, pygame.TEXTINPUT]):
            if evento.type == pygame.QUIT:
                return 'sair'
            if evento.type == pygame.TEXTINPUT:
                evento_texto.append(evento.text)
            elif evento.type == pygame.KEYDOWN and self.tela_menu == 'nome':
                if evento.key == pygame.K_BACKSPACE:
                    self.nome = self.nome[:-1]
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return self._executar('salvar')
                elif evento.key == pygame.K_ESCAPE:
                    return self._executar('salvar')

        if self.tela_menu == 'nome':
            for trecho in evento_texto:
                trecho = trecho.replace(';', ' ')
                self.nome = (self.nome + ''.join(c for c in trecho if c.isprintable()))[:LIMITE_NOME]
        opcoes = self._opcoes()
        if self._pressionou(pygame.K_UP):
            self.opcao = (self.opcao - 1) % len(opcoes)
        if self._pressionou(pygame.K_DOWN):
            self.opcao = (self.opcao + 1) % len(opcoes)
        if self.tela_menu != 'nome' and (self._pressionou(pygame.K_RETURN) or self._pressionou(pygame.K_KP_ENTER)):
            return self._executar(opcoes[self.opcao][1])
        if self._pressionou(pygame.K_ESCAPE):
            if self.tela_menu in ('ranking', 'controles'):
                self.abrir('principal')
            elif self.tela_menu == 'pausa':
                return 'continuar'
        mx, my = pygame.mouse.get_pos()
        clicado = bool(pygame.mouse.get_pressed()[0])
        for i, (_, acao) in enumerate(opcoes):
            if self._retangulo(i, len(opcoes)).collidepoint(mx, my):
                self.opcao = i
                if clicado and not self._mouse_pressionado:
                    self._mouse_pressionado = clicado
                    return self._executar(acao)
        self._mouse_pressionado = clicado
        return None

    def _executar(self, acao):
        if acao in ('ranking', 'controles'):
            self.abrir(acao)
            return None
        if acao == 'voltar':
            self.abrir('principal')
            return None
        if acao == 'salvar':
            if registrar_pontuacao(self.nome, self.pontos_finais):
                self.abrir('ranking')
            else:
                self.mensagem = 'ERRO AO SALVAR O RANKING'
            return None
        return acao

    def _retangulo(self, indice, total):
        largura, altura = 410, 66
        primeiro_y = 520 if self.tela_menu == 'principal' else (520 if self.tela_menu == 'pausa' else 733)
        if self.tela_menu == 'principal':
            primeiro_y = 470
        if self.tela_menu == 'pausa':
            primeiro_y = 470
        return pygame.Rect((self.janela.width - largura) // 2,
                           primeiro_y + indice * 79, largura, altura)

    def _escrever(self, texto, fonte, cor, centro_x, y):
        superficie = fonte.render(str(texto), True, cor)
        retangulo = superficie.get_rect(midtop=(centro_x, y))
        self.tela.blit(superficie, retangulo)

    def desenhar(self, fundo_pausado=False):
        # ALTERAÇÃO: desenhar no buffer virtual que Window.update() apresenta.
        # pygame.display.get_surface() é a janela física e pode ser sobrescrita.
        self.tela = self.janela.screen
        if fundo_pausado:
            camada = pygame.Surface((self.janela.width, self.janela.height), pygame.SRCALPHA)
            camada.fill((12, 10, 24, 204))
            self.tela.blit(camada, (0, 0))
        else:
            # ALTERAÇÃO: o menu principal usa a arte pronta, sem textos adicionais.
            if self.tela_menu == 'principal':
                self.tela.blit(self.fundo_menu_principal, (0, 0))
            else:
                self.tela.fill(COR_FUNDO)
        cx = self.janela.width // 2
        if self.tela_menu == 'principal':
            pass  # ALTERAÇÃO: somente os botões são desenhados sobre a imagem.
        elif self.tela_menu == 'pausa':
            self._escrever('JOGO PAUSADO', self.fonte_titulo, COR_DESTAQUE, cx, 190)
            self._escrever('ESC para continuar', self.fonte_menor, COR_TEXTO, cx, 285)
        elif self.tela_menu == 'ranking':
            self._escrever('RANKING - TOP 5', self.fonte_titulo, COR_DESTAQUE, cx, 100)
            registros = ler_ranking()[:LIMITE_EXIBIDO]
            if not registros:
                self._escrever('Nenhuma pontuacao registrada.', self.fonte, COR_TEXTO, cx, 350)
            for indice, (nome, pontos, data) in enumerate(registros, 1):
                self._escrever(f'{indice:02d}    {nome:<14}    {pontos:>6}    {data}',
                               self.fonte_pontos, COR_TEXTO, cx, 260 + (indice-1)*75)
        elif self.tela_menu == 'controles':
            self._escrever('CONTROLES', self.fonte_titulo, COR_DESTAQUE, cx, 105)
            for i, linha in enumerate(('SETAS: movimentar', 'ESPAÇO: saltar',
                                      'Z: soco / tiro com aplicador',
                                      'C: chute / tiro com aplicador',
                                      'ESC: pausar o jogo')):
                self._escrever(linha, self.fonte_pontos, COR_TEXTO, cx, 275 + i*63)
        elif self.tela_menu == 'nome':
            self._escrever('FIM DE JOGO', self.fonte_titulo, COR_DESTAQUE, cx, 130)
            self._escrever(f'PONTUACAO: {self.pontos_finais}', self.fonte, COR_TEXTO, cx, 275)
            self._escrever('Digite seu nome:', self.fonte, COR_TEXTO, cx, 365)
            pygame.draw.rect(self.tela, COR_PAINEL, (cx-240, 420, 480, 65), border_radius=8)
            self._escrever((self.nome or 'NOIVA') + ' |', self.fonte, COR_DESTAQUE, cx, 433)
            if self.mensagem:
                self._escrever(self.mensagem, self.fonte_menor, (255, 100, 100), cx, 520)
        opcoes = self._opcoes()
        mouse = pygame.mouse.get_pos()
        for i, (rotulo, _) in enumerate(opcoes):
            rect = self._retangulo(i, len(opcoes))
            destaque = i == self.opcao or rect.collidepoint(mouse)
            pygame.draw.rect(self.tela, COR_BOTAO_ATIVO if destaque else COR_BOTAO, rect, border_radius=10)
            self._escrever(rotulo, self.fonte_menor, COR_TEXTO, cx, rect.y + 18)
        # ALTERAÇÃO: remover o texto de instrução apenas do menu principal.
        if self.tela_menu != 'principal':
            self._escrever('Mouse ou setas + ENTER', self.fonte_menor, (178, 174, 193), cx, 846)
