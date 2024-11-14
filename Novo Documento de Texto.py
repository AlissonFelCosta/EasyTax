import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style, ttk

# Função de cálculo de imposto
def calcular_imposto():
    try:
        renda = float(entry_renda.get())
        deducoes = float(entry_deducoes.get())
        dependentes = int(entry_dependentes.get())

        # Exemplo de cálculo básico (ajuste conforme regras do imposto local)
        base_calculo = renda - (deducoes + (dependentes * 189.59))
        
        if base_calculo <= 22847.76:
            imposto = 0
        elif base_calculo <= 33919.80:
            imposto = base_calculo * 0.075 - 1713.58
        elif base_calculo <= 45012.60:
            imposto = base_calculo * 0.15 - 4257.57
        elif base_calculo <= 55976.16:
            imposto = base_calculo * 0.225 - 7633.51
        else:
            imposto = base_calculo * 0.275 - 10432.32

        # Exibe o imposto calculado na tela principal
        label_resultado.config(text=f"Imposto devido: R$ {imposto:.2f}")
        
        # Chama a função para abrir a tela de visualização detalhada
        abrir_tela_visualizacao(renda, deducoes, dependentes, base_calculo, imposto)
    
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira valores válidos.")

# Função para abrir a tela de visualização detalhada
def abrir_tela_visualizacao(renda, deducoes, dependentes, base_calculo, imposto):
    tela_visualizacao = tk.Toplevel(app)
    tela_visualizacao.title("Detalhes do Cálculo de Imposto")
    tela_visualizacao.geometry("350x300")

    # Exibindo os detalhes na nova janela
    ttk.Label(tela_visualizacao, text="Detalhes do Cálculo", font=("Helvetica", 14, "bold")).pack(pady=10)
    
    # Labels detalhados
    ttk.Label(tela_visualizacao, text=f"Renda Anual: R$ {renda:.2f}").pack(anchor="w", padx=10, pady=5)
    ttk.Label(tela_visualizacao, text=f"Deduções Totais: R$ {deducoes:.2f}").pack(anchor="w", padx=10, pady=5)
    ttk.Label(tela_visualizacao, text=f"Número de Dependentes: {dependentes}").pack(anchor="w", padx=10, pady=5)
    ttk.Label(tela_visualizacao, text=f"Base de Cálculo: R$ {base_calculo:.2f}").pack(anchor="w", padx=10, pady=5)
    ttk.Label(tela_visualizacao, text=f"Imposto Devido: R$ {imposto:.2f}", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=10)

    # Botão para fechar a janela
    ttk.Button(tela_visualizacao, text="Fechar", command=tela_visualizacao.destroy).pack(pady=10)

# Configuração do estilo com ttkbootstrap
style = Style(theme="cosmo")  # Pode mudar para outros temas: 'darkly', 'flatly', 'solar', etc.

# Criação da janela principal
app = style.master
app.title("Calculadora de Impostos")
app.geometry("400x400")

# Cabeçalho
header_label = tk.Label(app, text="Calculadora de Impostos de Pessoa Física", font=("Helvetica", 16, "bold"), fg="#007acc")
header_label.pack(pady=15)

# Frame para organizar entradas
frame = tk.Frame(app)
frame.pack(pady=10, padx=20, fill="x")

# Campo de Renda
ttk.Label(frame, text="Renda Anual (R$):", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w")
entry_renda = ttk.Entry(frame, width=25, font=("Helvetica", 10))
entry_renda.grid(row=0, column=1, pady=5, padx=5)

# Campo de Deduções
ttk.Label(frame, text="Deduções Totais (R$):", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w")
entry_deducoes = ttk.Entry(frame, width=25, font=("Helvetica", 10))
entry_deducoes.grid(row=1, column=1, pady=5, padx=5)

# Campo de Dependentes
ttk.Label(frame, text="Número de Dependentes:", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w")
entry_dependentes = ttk.Entry(frame, width=25, font=("Helvetica", 10))
entry_dependentes.grid(row=2, column=1, pady=5, padx=5)

# Botão de cálculo
btn_calcular = ttk.Button(app, text="Calcular Imposto", command=calcular_imposto, style="success.TButton")
btn_calcular.pack(pady=20)

# Label para exibir o resultado
label_resultado = ttk.Label(app, text="", font=("Helvetica", 12, "bold"))
label_resultado.pack(pady=10)

# Executa a aplicação
app.mainloop()
