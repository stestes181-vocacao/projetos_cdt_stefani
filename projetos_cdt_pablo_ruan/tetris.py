import pygame
import random

pygame.init()

# Configurações
LARGURA, ALTURA = 300, 600
TAM = 30
COL, LIN = 10, 20

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Tetris - Fire Neon com Fundo 'Computer Fire'")

grade = [[(0, 0, 0) for _ in range(COL)] for _ in range(LIN)]

# Formas
FORMAS = [
    [[1,1,1,1]],
    [[1,1],[1,1]],
    [[0,1,0],[1,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]],
    [[1,1,0],[0,1,1]],
    [[0,1,1],[1,1,0]]
]

# Paleta "Fogo Neon" para as peças
CORES = [
    (255, 80, 40),
    (255, 160, 0),
    (255, 0, 0),
    (255, 60, 0),
    (255, 120, 0),
    (255, 40, 0),
    (255, 100, 20)
]

BORDA = (255, 200, 100)

# ---- Parâmetros do fogo pixelado (doom fire) ----
FIRE_W = COL      # largura do fogo em "pixels" (igual às colunas do jogo)
FIRE_H = LIN      # altura do fogo em "pixels" (igual às linhas do jogo)
palette = []      # paleta de cores do fogo (do mais escuro ao mais claro)
FIRE_ENABLED = True  # se quiser desligar o efeito, coloque False

# criar paleta do fogo (de preto -> vermelho -> laranja -> amarelo -> branco-ish)
def criar_paleta():
    pal = []
    # preta -> vermelho escuro
    pal += [(20, 0, 0), (60, 0, 0), (120, 10, 0)]
    # vermelho -> laranja
    pal += [(180, 20, 0), (220, 50, 0), (255, 80, 10)]
    # laranja claro -> amarelo
    pal += [(255, 120, 20), (255, 160, 40), (255, 200, 80)]
    # quase branco
    pal += [(255, 230, 140)]
    return pal

palette = criar_paleta()
PALETTE_SIZE = len(palette)

# buffer do fogo: cada célula contém um índice da paleta (0...PALETTE_SIZE-1)
fire_pixels = [0] * (FIRE_W * FIRE_H)

def init_fire():
    # define a linha de base (bottom) com valor máximo para gerar chamas
    for x in range(FIRE_W):
        fire_pixels[(FIRE_H - 1) * FIRE_W + x] = PALETTE_SIZE - 1

def propagar_fogo():
    # algoritmo clássico "doom fire"
    for y in range(FIRE_H - 1):  # não processa a última linha (base)
        for x in range(FIRE_W):
            src = (y + 1) * FIRE_W + x
            decay = random.randint(0, 2)  # variação da queima
            val = fire_pixels[src] - decay
            if val < 0:
                val = 0
            # espalha um pouco para os lados (efeito de vento)
            dst_x = x - random.randint(0, 1)
            if dst_x < 0:
                dst_x = 0
            fire_pixels[y * FIRE_W + dst_x] = val

def desenhar_fogo():
    # desenha cada "pixel" de fogo na tela escalado pelo TAM
    for y in range(FIRE_H):
        for x in range(FIRE_W):
            idx = fire_pixels[y * FIRE_W + x]
            cor = palette[idx]
            # só desenha onde a grade está vazia; as células preenchidas cobrem por cima depois
            rect = (x * TAM, y * TAM, TAM, TAM)
            pygame.draw.rect(tela, cor, rect)

# -------------------------------------------------

class Peca:
    def __init__(self):
        self.forma = random.choice(FORMAS)
        self.cor = CORES[FORMAS.index(self.forma)]
        self.x = COL // 2 - len(self.forma[0]) // 2
        self.y = 0

    def mover(self, dx, dy):
        if not colisao(self.x + dx, self.y + dy, self.forma):
            self.x += dx
            self.y += dy
            return True
        return False

def colisao(x, y, forma):
    for i, linha in enumerate(forma):
        for j, bloco in enumerate(linha):
            if bloco:
                if x + j < 0 or x + j >= COL or y + i >= LIN:
                    return True
                if y + i >= 0 and grade[y + i][x + j] != (0,0,0):
                    return True
    return False

def fixar(peca):
    for i, linha in enumerate(peca.forma):
        for j, bloco in enumerate(linha):
            if bloco:
                grade[peca.y + i][peca.x + j] = peca.cor

def remover_linhas():
    global grade
    nova = []
    cont = 0
    for linha in grade:
        if (0,0,0) not in linha:
            cont += 1
        else:
            nova.append(linha)
    for _ in range(cont):
        nova.insert(0, [(0,0,0) for _ in range(COL)])
    grade = nova
    return cont

def fundo_gradiente():
    # mantém um degradê por baixo do fogo para reforçar as cores
    for y in range(ALTURA):
        r = 255
        g = int(80 + (y / ALTURA) * 100)
        b = 0
        pygame.draw.line(tela, (r, g, b), (0, y), (LARGURA, y))

def desenhar_peca(peca):
    for i, linha in enumerate(peca.forma):
        for j, bloco in enumerate(linha):
            if bloco:
                x = (peca.x + j)*TAM
                y = (peca.y + i)*TAM
                pygame.draw.rect(tela, peca.cor, (x, y, TAM, TAM))
                pygame.draw.rect(tela, BORDA, (x, y, TAM, TAM), 2)

def desenhar_grade():
    for y in range(LIN):
        for x in range(COL):
            if grade[y][x] != (0,0,0):
                pygame.draw.rect(tela, grade[y][x], (x*TAM, y*TAM, TAM, TAM))
                pygame.draw.rect(tela, BORDA, (x*TAM, y*TAM, TAM, TAM), 2)

def desenhar_score(score):
    font = pygame.font.SysFont("consolas", 22)
    texto = font.render(f"Score: {score}", True, (255, 230, 160))
    tela.blit(texto, (5, 5))

# inicializa fogo
init_fire()

clock = pygame.time.Clock()
peca = Peca()
queda = 0
vel = 20
score = 0
rodando = True

while rodando:
    # desenha o degradê (base)
    fundo_gradiente()

    # atualiza e desenha fogo (se habilitado)
    if FIRE_ENABLED:
        propagar_fogo()
        desenhar_fogo()

    queda += 1

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            rodando = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LEFT: peca.mover(-1,0)
            if e.key == pygame.K_RIGHT: peca.mover(1,0)
            if e.key == pygame.K_DOWN: peca.mover(0,1)

    if queda > vel:
        if not peca.mover(0,1):
            fixar(peca)
            linhas = remover_linhas()
            score += linhas * 100
            peca = Peca()
            if colisao(peca.x, peca.y, peca.forma):
                rodando = False
        queda = 0

    # desenha por cima: grade ocupada, peças e HUD
    desenhar_grade()
    desenhar_peca(peca)
    desenhar_score(score)
    

    pygame.display.update()
    clock.tick(30)

pygame.quit()
