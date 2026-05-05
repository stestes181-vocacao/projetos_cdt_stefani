# Importa a biblioteca Tkinter, usada para criar interfaces gráficas.
import tkinter as tk
# Importa a caixa de mensagem para exibir mensagens pop-up.
from tkinter import messagebox

# --- Lógica do Jogo ---

jogador_atual = "X"
tabuleiro = [["" for _ in range(3)] for _ in range(3)]

def verificar_vitoria(tab, jogador):
    for i in range(3):
        if all([celula == jogador for celula in tab[i]]):
            return True

    for i in range(3):
        if all([tab[j][i] == jogador for j in range(3)]):
            return True

    if all([tab[i][i] == jogador for i in range(3)]):
        return True

    if all([tab[i][2 - i] == jogador for i in range(3)]):
        return True

    return False

def verificar_empate():
    for linha in tabuleiro:
        if "" in linha:
            return False
    return True

# --- Funções da Interface Gráfica ---

def clique_botao(linha, coluna):
    global jogador_atual

    if tabuleiro[linha][coluna] == "":
        tabuleiro[linha][coluna] = jogador_atual

        # Define cor da fonte conforme o jogador
        cor = "blue" if jogador_atual == "X" else "red"
        botoes[linha][coluna].config(text=jogador_atual, fg=cor)

        if verificar_vitoria(tabuleiro, jogador_atual):
            # Emoji conforme o jogador vencedor
            emoji = "🏆❌" if jogador_atual == "X" else "🏆⭕"

            messagebox.showinfo(
                "Fim de Jogo",
                f"Parabéns! O jogador {jogador_atual} venceu! {emoji}"
            )
            desabilitar_botoes()
            return

        if verificar_empate():
            messagebox.showinfo("Fim de Jogo", "Fim do Jogo! Empate 🤝")
            return

        jogador_atual = "O" if jogador_atual == "X" else "X"
        rotulo_status.config(
            text=f"Vez do jogador: {jogador_atual}",
            fg="green"
        )

def reiniciar_jogo():
    global jogador_atual

    jogador_atual = "X"
    rotulo_status.config(
        text=f"Vez do jogador: {jogador_atual}",
        fg="green"
    )

    for i in range(3):
        for j in range(3):
            tabuleiro[i][j] = ""
            botoes[i][j].config(text="", state="normal", fg="black")

def desabilitar_botoes():
    for i in range(3):
        for j in range(3):
            botoes[i][j]["state"] = "disabled"

# --- Configuração da Janela Principal ---

janela = tk.Tk()
janela.title("Jogo da Velha")

rotulo_status = tk.Label(
    janela,
    text=f"Vez do jogador: {jogador_atual}",
    font=("Arial", 16),
    fg="green"
)
rotulo_status.grid(row=0, column=0, columnspan=3, pady=10)

botoes = [[None for _ in range(3)] for _ in range(3)]
for i in range(3):
    for j in range(3):
        botao = tk.Button(
            janela,
            text="",
            font=("Arial", 30),
            width=5,
            height=2,
            command=lambda i=i, j=j: clique_botao(i, j)
        )
        botao.grid(row=i+1, column=j, padx=5, pady=5)
        botoes[i][j] = botao

botao_reiniciar = tk.Button(
    janela,
    text="Reiniciar Jogo",
    font=("Arial", 12),
    command=reiniciar_jogo
)
botao_reiniciar.grid(row=4, column=0, columnspan=3, pady=10)

janela.mainloop()
