import pygame
import random

# --- CONFIGURAÇÕES TÉCNICAS ---
pygame.init()
TAM = 30
COL, LIN = 10, 20
LARGURA, ALTURA = COL * TAM, LIN * TAM
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Tetris Fire Neon - Score Colorido")

# --- CORES E PALETAS ---
CORES_NEON = [
    (0, 255, 255), (255, 0, 255), (255, 255, 0),
    (0, 255, 0), (255, 100, 0), (0, 0, 255), (255, 0, 0)
]
BORDA_BRILHO = (255, 255, 255)

# --- ALGORITMO DO FOGO (DOOM FIRE) CORRIGIDO ---
FIRE_W, FIRE_H = COL, LIN
fire_pixels = [0] * (FIRE_W * FIRE_H)

def criar_paleta_segura():
    """Gera uma paleta de cores RGB garantindo que os valores fiquem entre 0 e 255."""
    pal = []
    # De preto para vermelho
    for i in range(15):
        pal.append((min(i * 10, 255), 0, 0))
    # De vermelho para laranja/amarelo
    for i in range(15):
        pal.append((255, min(i * 12, 255), 0))
    # De amarelo para branco
    for i in range(15):
        pal.append((255, 255, min(i * 15, 255)))
    return pal

palette = criar_paleta_segura()

def propagar_fogo():
    """Calcula a propagação das chamas de baixo para cima."""
    for x in range(FIRE_W):
        fire_pixels[(FIRE_H - 1) * FIRE_W + x] = len(palette) - 1
        
    for y in range(0, FIRE_H - 1):
        for x in range(FIRE_W):
            src = (y + 1) * FIRE_W + x
            pixel = fire_pixels[src]
            decay = random.randint(0, 2)
            dst = src - FIRE_W - decay + 1
            if 0 <= dst < len(fire_pixels):
                novo_valor = pixel - (decay & 1)
                fire_pixels[dst] = max(0, novo_valor)

# --- LÓGICA DO TETRIS ---
FORMAS = [
    [[1, 1, 1, 1]], [[1, 1], [1, 1]], [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]], [[1, 1, 0], [0, 1, 1]]
]

class Peca:
    def __init__(self):
        self.tipo = random.randint(0, len(FORMAS)-1)
        self.forma = FORMAS[self.tipo]
        self.cor = CORES_NEON[self.tipo]
        self.x = COL // 2 - len(self.forma[0]) // 2
        self.y = 0

    def rotacionar(self):
        nova_forma = [list(res) for res in zip(*self.forma[::-1])]
        if not verificar_colisao(self.x, self.y, nova_forma):
            self.forma = nova_forma

def verificar_colisao(x, y, forma):
    for i, linha in enumerate(forma):
        for j, bloco in enumerate(linha):
            if bloco:
                if x + j < 0 or x + j >= COL or y + i >= LIN:
                    return True
                if y + i >= 0 and grade[y+i][x+j]:
                    return True
    return False

grade = [[None for _ in range(COL)] for _ in range(LIN)]

def remover_linhas():
    global grade
    linhas_antes = len(grade)
    grade = [linha for linha in grade if not all(linha)]
    linhas_removidas = linhas_antes - len(grade)
    for _ in range(linhas_removidas):
        grade.insert(0, [None for _ in range(COL)])
    return linhas_removidas

# --- FUNÇÕES DE DESENHO ---
def desenhar_tudo(peca, score):
    tela.fill((0, 0, 0))
    
    # 1. Desenhar Fogo
    propagar_fogo()
    for i, p_idx in enumerate(fire_pixels):
        if p_idx > 0:
            x, y = (i % FIRE_W) * TAM, (i // FIRE_W) * TAM
            cor_fogo = palette[min(p_idx, len(palette)-1)]
            pygame.draw.rect(tela, cor_fogo, (x, y, TAM, TAM))

    # 2. Desenhar Grade Fixa
    for y, linha in enumerate(grade):
        for x, cor in enumerate(linha):
            if cor:
                pygame.draw.rect(tela, cor, (x*TAM, y*TAM, TAM, TAM))
                pygame.draw.rect(tela, (255, 255, 255), (x*TAM, y*TAM, TAM, TAM), 1)

    # 3. Desenhar Peça Fantasma
    gy = peca.y
    while not verificar_colisao(peca.x, gy + 1, peca.forma):
        gy += 1
    for i, linha in enumerate(peca.forma):
        for j, bloco in enumerate(linha):
            if bloco:
                pygame.draw.rect(tela, (60, 60, 60), ((peca.x+j)*TAM, (gy+i)*TAM, TAM, TAM), 1)

    # 4. Desenhar Peça Atual
    for i, linha in enumerate(peca.forma):
        for j, bloco in enumerate(linha):
            if bloco:
                px, py = (peca.x + j)*TAM, (peca.y + i)*TAM
                pygame.draw.rect(tela, peca.cor, (px, py, TAM, TAM))
                pygame.draw.rect(tela, BORDA_BRILHO, (px, py, TAM, TAM), 2)

    # 5. UI - PLACAR EM LARANJA NEON COM SOMBRA
    fonte = pygame.font.SysFont("Consolas", 28, bold=True)
    cor_score = (255, 140, 0) 
    
    # Sombra
    sombra = fonte.render(f"PONTOS: {score}", True, (0, 0, 0))
    tela.blit(sombra, (17, 17))
    # Principal
    msg = fonte.render(f"PONTOS: {score}", True, cor_score)
    tela.blit(msg, (15, 15))

# --- LOOP PRINCIPAL ---
clock = pygame.time.Clock()
peca_atual = Peca()
score = 0
tempo_queda = 0
rodando = True

while rodando:
    dt = clock.tick(30)
    tempo_queda += dt
    velocidade = max(100, 500 - (score // 1000) * 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and not verificar_colisao(peca_atual.x-1, peca_atual.y, peca_atual.forma):
                peca_atual.x -= 1
            if event.key == pygame.K_RIGHT and not verificar_colisao(peca_atual.x+1, peca_atual.y, peca_atual.forma):
                peca_atual.x += 1
            if event.key == pygame.K_DOWN and not verificar_colisao(peca_atual.x, peca_atual.y+1, peca_atual.forma):
                peca_atual.y += 1
            if event.key == pygame.K_UP:
                peca_atual.rotacionar()
            if event.key == pygame.K_SPACE:
                while not verificar_colisao(peca_atual.x, peca_atual.y+1, peca_atual.forma):
                    peca_atual.y += 1
                tempo_queda = velocidade

    if tempo_queda >= velocidade:
        if not verificar_colisao(peca_atual.x, peca_atual.y + 1, peca_atual.forma):
            peca_atual.y += 1
        else:
            for i, linha in enumerate(peca_atual.forma):
                for j, bloco in enumerate(linha):
                    if bloco:
                        if peca_atual.y + i < 0:
                            rodando = False
                        else:
                            grade[peca_atual.y + i][peca_atual.x + j] = peca_atual.cor
            
            score += remover_linhas() * 100
            peca_atual = Peca()
            if verificar_colisao(peca_atual.x, peca_atual.y, peca_atual.forma):
                rodando = False
        tempo_queda = 0

    desenhar_tudo(peca_atual, score)
    pygame.display.flip()

pygame.quit()