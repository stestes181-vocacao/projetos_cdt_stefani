# ===============================================
# Projeto: Snake Run (Cobrinha) com Pygame
# Descrição: Implementação do clássico jogo Snake com Power-Ups
# ===============================================

import pygame
import random
import sys

# -----------------------------------------------
# 1. Configurações Globais do Jogo
# -----------------------------------------------

# Dimensões da tela em pixels
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
# Tamanho de cada bloco (quadrícula) da grade
GRID_SIZE = 10
# Taxa de quadros por segundo (Frame Rate)
FPS = 60
# Intervalo de tempo base (em milissegundos) entre cada movimento da cobra.
# Um valor menor = mais rápido.
BASE_MOVE_INTERVAL = 70  # 🐌 70ms entre cada movimento (velocidade padrão)

# Cálculo das dimensões da grade em número de blocos
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# -----------------------------------------------
# 2. Variáveis de Estado do Jogo
# -----------------------------------------------

# Lista de tuplas (x, y) que representa as coordenadas do corpo da cobra.
corpo_cobra = []
# Tupla (dx, dy) que representa a direção atual do movimento.
# (10, 0) é para a direita (GRID_SIZE, 0).
direcao = (GRID_SIZE, 0)
# Dicionário que armazena a posição da comida normal.
comida_normal = {}
# Lista de dicionários para as comidas especiais (ex: [{'pos': (x,y), 'type': 'slow'}]).
comidas_especiais = []

# Cor da cobra (verde)
cor_cobra = (0.0, 255.0, 0.0)
target_color = cor_cobra # Variável não utilizada, mas mantida.
# Estado atual do jogo: 'menu', 'running', 'game_over'
game_state = 'menu'
# Pontuação do jogador
score = 0
# Contador para o crescimento da cobra (quantidade de segmentos a serem adicionados)
grow = 0
# Tempo restante do efeito 'slow' (em segundos)
slow_time = 0.0
# Tempo restante do efeito 'freeze' (em segundos)
freeze_time = 0.0
# Acumulador de tempo para controlar a velocidade de movimento da cobra.
# Usado para garantir que a cobra se mova em intervalos fixos, independente do FPS.
move_accumulator = 0

# -----------------------------------------------
# 3. Inicialização do Pygame
# -----------------------------------------------
pygame.init()
# Cria a janela do jogo
tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Define o título da janela
pygame.display.set_caption("Snake Run")
# Configura as fontes para exibição de texto
font_small = pygame.font.Font(None, 24)
font_big = pygame.font.Font(None, 48)
# O objeto Clock para controlar o tempo e o FPS
clock = pygame.time.Clock()

# -----------------------------------------------
# 4. Funções de Lógica do Jogo
# -----------------------------------------------

def spawn_comida_normal():
    """Gera uma nova posição aleatória para a comida normal."""
    while True:
        # Gera uma posição aleatória baseada na grade
        pos = (
            random.randrange(GRID_WIDTH) * GRID_SIZE,
            random.randrange(GRID_HEIGHT) * GRID_SIZE
        )
        # Garante que a comida não apareça dentro do corpo da cobra
        if pos not in corpo_cobra:
            return {'pos': pos}

def try_spawn_comida_especial():
    """Tenta gerar uma comida especial aleatoriamente, com baixa probabilidade."""
    # Limita o número máximo de comidas especiais na tela
    if len(comidas_especiais) >= 2:
        return

    r = random.random() # Número aleatório entre 0.0 e 1.0
    
    # 2% de chance para a comida 'freeze' (Congelar)
    if r < 0.02:
        tipo = 'freeze'
    # 3% de chance (de 0.02 a 0.05) para a comida 'slow' (Devagar)
    elif r < 0.05:
        tipo = 'slow'
    # Se r for maior que 0.05, não gera comida especial
    else:
        return

    # Encontra uma posição para a comida especial que não conflite com outros objetos
    while True:
        pos = (
            random.randrange(GRID_WIDTH) * GRID_SIZE,
            random.randrange(GRID_HEIGHT) * GRID_SIZE
        )
        # Verifica se a posição está vazia
        if (
            pos not in corpo_cobra and
            pos != comida_normal['pos'] and
            pos not in [c['pos'] for c in comidas_especiais]
        ):
            # Adiciona a nova comida especial à lista
            comidas_especiais.append({'pos': pos, 'type': tipo})
            break

def reset_game():
    """Reinicia todas as variáveis de estado para iniciar um novo jogo."""
    global corpo_cobra, direcao, comida_normal, comidas_especiais
    global score, grow, slow_time, freeze_time, move_accumulator, game_state

    # Posição inicial da cobra (dois segmentos)
    corpo_cobra = [(100, 50), (90, 50)]
    # Direção inicial (para a direita)
    direcao = (GRID_SIZE, 0)
    # Gera a primeira comida
    comida_normal = spawn_comida_normal()
    comidas_especiais = []
    score = 0
    grow = 0
    slow_time = 0
    freeze_time = 0
    move_accumulator = 0
    # Define o estado do jogo como 'running' (rodando)
    game_state = 'running'

def do_move():
    """Realiza um passo de movimento da cobra e verifica colisões/interações."""
    global comida_normal, score, grow, slow_time, freeze_time, game_state

    # Calcula a posição da nova cabeça
    nova = (
        corpo_cobra[0][0] + direcao[0],
        corpo_cobra[0][1] + direcao[1]
    )
    # Insere a nova cabeça no início da lista
    corpo_cobra.insert(0, nova)

    # 1. Colisão com Comida Normal (vermelha)
    if nova == comida_normal['pos']:
        grow += 1           # Incrementa o contador de crescimento
        score += 1          # Incrementa a pontuação
        comida_normal = spawn_comida_normal() # Gera nova comida
        return              # Sai da função para evitar remover a cauda

    # 2. Colisão com Comidas Especiais
    for c in comidas_especiais:
        if nova == c['pos']:
            if c['type'] == 'slow':
                slow_time = 7   # Ativa o slow por 7 segundos
            elif c['type'] == 'freeze':
                freeze_time = 4 # Ativa o freeze por 4 segundos
            comidas_especiais.remove(c) # Remove a comida especial
            return              # Sai da função para evitar remover a cauda

    # 3. Gerenciamento da Cauda (Movimento ou Crescimento)
    if grow > 0:
        grow -= 1           # Usa um "crédito" de crescimento
    else:
        corpo_cobra.pop()   # Remove o último segmento (movimento normal)

    # 4. Colisão com o Próprio Corpo
    # Verifica se a nova cabeça está em qualquer segmento do corpo (exceto ela mesma)
    if nova in corpo_cobra[1:]:
        game_state = 'game_over'

    # 5. Colisão com as Bordas da Tela
    if not (0 <= nova[0] < SCREEN_WIDTH and 0 <= nova[1] < SCREEN_HEIGHT):
        game_state = 'game_over'

def update_game(dt):
    """Atualiza o estado do jogo com base no tempo decorrido (dt)."""
    global move_accumulator, slow_time, freeze_time

    # Converte o tempo decorrido de milissegundos para segundos
    dt_sec = dt / 1000
    # Diminui os tempos de power-up, garantindo que não sejam negativos
    slow_time = max(0, slow_time - dt_sec)
    freeze_time = max(0, freeze_time - dt_sec)

    # Se estiver congelado, não permite o movimento da cobra
    if freeze_time > 0:
        return

    # Calcula o intervalo de movimento: 
    # Dobra se o 'slow' estiver ativo (70 * 2 = 140ms)
    interval = BASE_MOVE_INTERVAL * (2 if slow_time > 0 else 1)
    # Acumula o tempo passado
    move_accumulator += dt

    # Enquanto o tempo acumulado for maior que o intervalo de movimento necessário,
    # executa um passo de movimento lógico.
    while move_accumulator >= interval and game_state == 'running':
        do_move()
        # Subtrai o intervalo do acumulador para que o tempo restante seja mantido
        move_accumulator -= interval

# -----------------------------------------------
# 5. Funções de Desenho (Renderização)
# -----------------------------------------------

def draw():
    """Desenha todos os elementos do jogo na tela."""
    # Preenche o fundo da tela com preto
    tela.fill((0, 0, 0))

    # Desenha a cobra (verde)
    for p in corpo_cobra:
        pygame.draw.rect(tela, (0, 255, 0), (*p, GRID_SIZE, GRID_SIZE))

    # Desenha a comida normal (vermelha)
    pygame.draw.rect(
        tela, (255, 0, 0),
        (*comida_normal['pos'], GRID_SIZE, GRID_SIZE)
    )

    # Desenha as comidas especiais
    for c in comidas_especiais:
        # Roxo para 'slow', Azul para 'freeze'
        cor = (120, 0, 180) if c['type'] == 'slow' else (0, 120, 255)
        pygame.draw.rect(tela, cor, (*c['pos'], GRID_SIZE, GRID_SIZE))

    # Exibe a pontuação
    score_txt = font_small.render(f"Score: {score}", True, (255, 255, 255))
    tela.blit(score_txt, (10, 10))

    # Atualiza a tela para exibir o que foi desenhado
    pygame.display.update()

# -----------------------------------------------
# 6. Loop Principal do Jogo
# -----------------------------------------------

# Chama a função de reset para iniciar o jogo (ou ir para o estado 'running')
reset_game()
rodando = True

while rodando:
    # 1. Controle de Tempo e FPS
    # Retorna o tempo decorrido desde o último frame (em ms)
    dt = clock.tick(FPS)

    # 2. Processamento de Eventos (Entrada do Usuário)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            rodando = False # Se fechar a janela, encerra o loop

        # Processa as teclas de direção apenas se o jogo estiver rodando
        if e.type == pygame.KEYDOWN and game_state == 'running':
            # UP: Define a direção para cima, impede reversão imediata (não pode ir para baixo)
            if e.key == pygame.K_UP and direcao != (0, GRID_SIZE):
                direcao = (0, -GRID_SIZE)
            # DOWN: Define a direção para baixo, impede reversão imediata (não pode ir para cima)
            elif e.key == pygame.K_DOWN and direcao != (0, -GRID_SIZE):
                direcao = (0, GRID_SIZE)
            # LEFT: Define a direção para esquerda, impede reversão imediata (não pode ir para direita)
            elif e.key == pygame.K_LEFT and direcao != (GRID_SIZE, 0):
                direcao = (-GRID_SIZE, 0)
            # RIGHT: Define a direção para direita, impede reversão imediata (não pode ir para esquerda)
            elif e.key == pygame.K_RIGHT and direcao != (-GRID_SIZE, 0):
                direcao = (GRID_SIZE, 0)

    # 3. Atualização da Lógica do Jogo
    if game_state == 'running':
        try_spawn_comida_especial()
        update_game(dt) # Chama a atualização principal com o tempo decorrido

    # 4. Renderização
    draw()

# -----------------------------------------------
# 7. Finalização do Pygame e do Sistema
# -----------------------------------------------
pygame.quit()
sys.exit()