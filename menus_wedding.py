"""Menus, pausa e ranking do Wedding Panic — PPlay 2.1/Pygame.

# ALTERAÇÃO: interface separada do gameplay e salvamento em ranking.txt.
Formato do ranking do Space Invaders: nome; pontos; data (5 melhores exibidos).
"""
from pathlib import Path
from datetime import datetime
from PPlay.gameimage import GameImage
from PPlay.ui import UITheme, UIManager, TextInput

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
        self.tela = janela.screen
        pasta_ui = Path(__file__).resolve().parent / 'assets' / 'ui_pplay'
        self.botao_normal = GameImage(str(pasta_ui / 'botao_normal.png'))
        self.botao_ativo = GameImage(str(pasta_ui / 'botao_ativo.png'))
        self.painel_nome = GameImage(str(pasta_ui / 'painel_nome.png'))
        # Mesma cor e alfa da camada anterior: (12, 10, 24, 204).
        self.camada_pausa_pplay = GameImage(str(pasta_ui / 'camada_pausa_PPlay_1600x900.png'))
        # Se uma fonte ou alinhamento visual divergir, mudar para False restaura o desenho anterior.
        self.usar_texto_pplay = True
        # O PNG auxiliar mantém a mesma proporção e enquadramento que o antigo smoothscale.
        self.fundo_menu_principal = GameImage(str(
            Path(__file__).resolve().parent / 'assets' / 'img-fundos' / 'menu_PPlay_1600x900.png'
        ))
        self.teclado = janela.get_keyboard()
        self.mouse = janela.get_mouse()
        self.tela_menu = 'principal'
        self.opcao = 0
        self.nome = ''
        self.pontos_finais = 0
        self.mensagem = ''
        # Mantidas as mesmas dimensões; _escrever() e centralização permanecem intactos.
        self.fonte_titulo = UITheme.fonte(74, True)
        self.fonte = UITheme.fonte(33, True)
        self.fonte_menor = UITheme.fonte(24, False)
        self.fonte_pontos = UITheme.fonte(30, False)
        self._mouse_pressionado = False
        self._teclas_anteriores = set()
        # ALTERAÇÃO: bloqueia o ESC que acabou de abrir o menu de pausa.
        self._ignorar_esc_ate_soltar = False
        self._ignorar_enter_ate_soltar = False
        # O TextInput não é desenhado: preservamos o painel e texto originais.
        self.ui_nome = UIManager()
        self.campo_nome = TextInput(texto='', largura=460, altura=65,
                                   max_caracteres=LIMITE_NOME,
                                   on_enter=self._confirmar_nome_pplay)
        self.campo_nome.set_position(self.janela.width // 2 - 230, 420)
        self.ui_nome.add(self.campo_nome)
        self._salvar_nome_pendente = False

    def _confirmar_nome_pplay(self, texto):
        # ALTERAÇÃO: callback do ENTER do TextInput; salvar apenas no fluxo de atualizar().
        self.nome = texto
        self._salvar_nome_pendente = True

    def abrir(self, tela, pontos=0):
        self.tela_menu = tela
        self.opcao = 0
        self._mouse_pressionado = bool(self.mouse.button_pressed(1))
        self._teclas_anteriores.clear()
        # Impede que o Enter de VOLTAR no ranking acione JOGAR no menu seguinte.
        self._ignorar_enter_ate_soltar = bool(self.teclado.key_pressed('enter'))
        # ALTERAÇÃO: a tecla que abre a pausa não pode fechá-la no frame seguinte.
        self._ignorar_esc_ate_soltar = (tela == 'pausa' and bool(self.teclado.key_pressed('esc')))
        self.mensagem = ''
        if tela == 'nome':
            self.nome = ''
            self.pontos_finais = int(pontos)
            self.campo_nome.texto = ''
            self._salvar_nome_pendente = False
            self.ui_nome.focar(self.campo_nome)
        else:
            # ALTERAÇÃO: o campo só recebe caracteres na tela de ranking final.
            self.campo_nome.focado = False

    def _pressionou(self, tecla):
        pressionado = bool(self.teclado.key_pressed(tecla))
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
        # UIManager usa janela.eventos e encaminha KEYDOWN ao TextInput.
        if self.tela_menu == 'nome':
            self.ui_nome.update()
            # ALTERAÇÃO: preservar o filtro antigo do ranking e o limite de 14 caracteres.
            self.campo_nome.texto = ''.join(
                c for c in self.campo_nome.texto.replace(';', ' ') if c.isprintable()
            )[:LIMITE_NOME]
            self.nome = self.campo_nome.texto
            if self._salvar_nome_pendente:
                self._salvar_nome_pendente = False
                return self._executar('salvar')
            # ALTERAÇÃO: ESC continua salvando a pontuação como anteriormente.
            if self._pressionou('esc'):
                return self._executar('salvar')
        opcoes = self._opcoes()
        if self._pressionou('up'):
            self.opcao = (self.opcao - 1) % len(opcoes)
        if self._pressionou('down'):
            self.opcao = (self.opcao + 1) % len(opcoes)
        # Aguarda a soltura do Enter usado para abrir esta tela.
        if self._ignorar_enter_ate_soltar:
            if not self.teclado.key_pressed('enter'):
                self._ignorar_enter_ate_soltar = False
        elif self.tela_menu != 'nome' and self._pressionou('enter'):
            return self._executar(opcoes[self.opcao][1])
        # ALTERAÇÃO: aguardar a liberação do ESC que abriu a pausa.
        # Sem isso, o mesmo pressionamento aciona 'continuar' e o menu só pisca.
        if self._ignorar_esc_ate_soltar:
            if not self.teclado.key_pressed('esc'):
                self._ignorar_esc_ate_soltar = False
        elif self._pressionou('esc'):
            if self.tela_menu in ('ranking', 'controles'):
                self.abrir('principal')
            elif self.tela_menu == 'pausa':
                return 'continuar'
        mx, my = self.mouse.get_position()
        clicado = bool(self.mouse.button_pressed(1))
        for i, (_, acao) in enumerate(opcoes):
            if self._ponto_no_retangulo(self._retangulo(i, len(opcoes)), mx, my):
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
            # ALTERAÇÃO: sincronizar o nome digitado no TextInput antes de salvar.
            self.nome = self.campo_nome.texto
            if registrar_pontuacao(self.nome, self.pontos_finais):
                self.abrir('ranking')
            else:
                self.mensagem = 'ERRO AO SALVAR O RANKING'
            return None
        return acao

    @staticmethod
    def _ponto_no_retangulo(retangulo, x, y):
        rx, ry, largura, altura = retangulo
        return rx <= x < rx + largura and ry <= y < ry + altura

    def _retangulo(self, indice, total):
        largura, altura = 410, 66
        primeiro_y = 520 if self.tela_menu == 'principal' else (520 if self.tela_menu == 'pausa' else 733)
        if self.tela_menu == 'principal':
            primeiro_y = 470
        if self.tela_menu == 'pausa':
            primeiro_y = 470
        # ALTERAÇÃO: devolve coordenadas simples (x, y, largura, altura).
        return ((self.janela.width - largura) // 2,
                primeiro_y + indice * 79, largura, altura)

    def _escrever(self, texto, fonte, cor, centro_x, y):
        # central diretamente. Mantemos a medição original para preservar a geometria.
        # O modo original fica como alternativa reversível caso seja necessário.
        if self.usar_texto_pplay:
            texto = str(texto)
            largura_texto = fonte.size(texto)[0]
            tamanho = (74 if fonte is self.fonte_titulo else
                       33 if fonte is self.fonte else
                       30 if fonte is self.fonte_pontos else 24)
            self.janela.draw_text(
                texto, int(centro_x - largura_texto / 2), int(y),
                tamanho=tamanho, cor=cor, fonte='Arial'
            )
        else:
            superficie = fonte.render(str(texto), True, cor)
            retangulo = superficie.get_rect(midtop=(centro_x, y))
            self.tela.blit(superficie, retangulo)

    def desenhar(self, fundo_pausado=False):
        if fundo_pausado:
            self.camada_pausa_pplay.set_position(0, 0)
            self.camada_pausa_pplay.draw()
        else:
            # ALTERAÇÃO: o menu principal exibe novamente a imagem original.
            if self.tela_menu == 'principal':
                self.fundo_menu_principal.set_position(0, 0)
                self.fundo_menu_principal.draw()
            else:
                self.tela.fill(COR_FUNDO)
        cx = self.janela.width // 2
        if self.tela_menu == 'principal':
            pass  # ALTERAÇÃO: título já existe na imagem; evitar texto duplicado.
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
            self.painel_nome.set_position(cx - 240, 420)
            self.painel_nome.draw()
            self._escrever((self.nome or 'NOIVA') + ' |', self.fonte, COR_DESTAQUE, cx, 433)
            if self.mensagem:
                self._escrever(self.mensagem, self.fonte_menor, (255, 100, 100), cx, 520)
        opcoes = self._opcoes()
        mouse = self.mouse.get_position()
        for i, (rotulo, _) in enumerate(opcoes):
            rect = self._retangulo(i, len(opcoes))
            # ALTERAÇÃO: hover e clique permanecem com as mesmas coordenadas originais.
            destaque = i == self.opcao or self._ponto_no_retangulo(rect, *mouse)
            botao = self.botao_ativo if destaque else self.botao_normal
            botao.set_position(rect[0], rect[1])
            botao.draw()
            self._escrever(rotulo, self.fonte_menor, COR_TEXTO, cx, rect[1] + 18)
        self._escrever('Mouse ou setas + ENTER', self.fonte_menor, (178, 174, 193), cx, 846)
