import tkinter as tk
import firebase_admin
import re
from tkinter import messagebox
from ttkbootstrap import Style, ttk
from firebase_admin import credentials, firestore
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

# Configuração do Firebase
cred = credentials.Certificate("C:/Users/Sexta-feira/Documents/Projets/GitHub/EasyTax/firebasekey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Função para verificar se é um CPF válido
def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)  # Remove caracteres não numéricos
    if len(cpf) != 11:
        return False
    return cpf.isdigit()

# Função para verificar se é um CNPJ válido
def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)  # Remove caracteres não numéricos
    if len(cnpj) != 14:
        return False
    return cnpj.isdigit()

# Função de login
def realizar_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    if not usuario or not senha:
        messagebox.showwarning("Erro", "CPF ou Senha não podem ser vazios!")
        return

    # Verifica se o CPF/CNPJ existe no banco de dados Firebase
    user_ref = db.collection('users').where('cpf_cnpj', '==', usuario)
    docs = user_ref.get()

    if not docs:
        messagebox.showerror("Erro", "Usuário não encontrado!")
        return

    # Verifica se a senha corresponde ao usuário encontrado
    user_doc = docs[0].to_dict()
    if user_doc['senha'] != senha:
        messagebox.showerror("Erro", "Senha incorreta!")
        return

    # Se CPF/CNPJ e senha estiverem corretos, entra na aplicação
    if validar_cpf(usuario):
        abrir_tela_calculo_imposto_renda(usuario)  # Abre a tela de cálculo de Imposto de Renda
    elif validar_cnpj(usuario):
        tela_calculo_icms(usuario)  # Abre a tela de cálculo de ICMS
    else:
        messagebox.showerror("Erro", "CPF ou CNPJ inválido")

# Função para abrir a tela de cadastro
def abrir_tela_cadastro():
    def cadastrar_usuario():
        cpf_cnpj = entry_cpf_cnpj.get()
        senha = entry_senha_cadastro.get()

        if not cpf_cnpj or not senha:
            messagebox.showwarning("Erro", "CPF/CNPJ e Senha são obrigatórios!")
            return

        if not (validar_cpf(cpf_cnpj) or validar_cnpj(cpf_cnpj)):
            messagebox.showerror("Erro", "CPF ou CNPJ inválido!")
            return

        # Verifica se o usuário já existe
        user_ref = db.collection('users').where('cpf_cnpj', '==', cpf_cnpj).get()
        if user_ref:
            messagebox.showerror("Erro", "Usuário já cadastrado!")
            return

        # Salva o novo usuário no Firebase
        db.collection('users').add({
            'cpf_cnpj': cpf_cnpj,
            'senha': senha
        })

        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
        tela_cadastro.destroy()

    tela_cadastro = tk.Toplevel(tela_login)
    tela_cadastro.title("Tela de Cadastro")
    tela_cadastro.geometry("300x300")

    label_cpf_cnpj = ttk.Label(tela_cadastro, text="CPF ou CNPJ:", font=("Helvetica", 12))
    label_cpf_cnpj.pack(pady=10)
    entry_cpf_cnpj = ttk.Entry(tela_cadastro, width=30)
    entry_cpf_cnpj.pack(pady=5)

    label_senha_cadastro = ttk.Label(tela_cadastro, text="Senha:", font=("Helvetica", 12))
    label_senha_cadastro.pack(pady=10)
    entry_senha_cadastro = ttk.Entry(tela_cadastro, width=30, show="*")
    entry_senha_cadastro.pack(pady=5)

    btn_cadastrar = ttk.Button(tela_cadastro, text="Cadastrar", command=cadastrar_usuario)
    btn_cadastrar.pack(pady=20)


# Função para abrir a tela de cálculo de ICMS com abas
def tela_calculo_icms(usuario):
    tela_icms = tk.Toplevel(tela_login)
    tela_icms.title("Cálculo de ICMS")
    tela_icms.geometry("600x400")

    # Criando as abas
    notebook = ttk.Notebook(tela_icms)
    aba_calculo = ttk.Frame(notebook)
    aba_historico = ttk.Frame(notebook)
    aba_exportar = ttk.Frame(notebook)

    notebook.add(aba_calculo, text="Cálculo ICMS")
    notebook.add(aba_historico, text="Histórico")
    notebook.add(aba_exportar, text="Exportar PDF")

    notebook.pack(expand=True, fill="both")

    # Aba de Cálculo ICMS
    ttk.Label(aba_calculo, text="Valor da Operação (R$):", font=("Helvetica", 12), anchor="w").pack(pady=10, padx=20)
    entry_valor = ttk.Entry(aba_calculo, width=30)
    entry_valor.pack(pady=5)

    ttk.Label(aba_calculo, text="Alíquota de ICMS (%):", font=("Helvetica", 12), anchor="w").pack(pady=10, padx=20)
    entry_aliquota = ttk.Entry(aba_calculo, width=30)
    entry_aliquota.pack(pady=5)

    def calcular_icms(usuario):
        try:
            valor = float(entry_valor.get())
            aliquota = float(entry_aliquota.get()) / 100
            
            # Cálculo do ICMS
            icms = valor * aliquota
            
            # Exibe o resultado
            messagebox.showinfo("Resultado", f"ICMS: R$ {icms:.2f}")
            
            # Salvar no Firebase
            user_ref = db.collection('users').where('cpf_cnpj', '==', usuario).get()
            if user_ref:
                db.collection('historico').add({
                    'cpf_cnpj': usuario,
                    'tipo_imposto': 'ICMS',
                    'valor': icms,
                    'data': firestore.SERVER_TIMESTAMP
                })
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos.")
    
    # Botão para realizar o cálculo
    btn_calcular = ttk.Button(aba_calculo, text="Calcular ICMS", command=lambda: calcular_icms(usuario), style="primary.TButton")
    btn_calcular.pack(pady=25)

    # Aba de Histórico
    ttk.Label(aba_historico, text="Histórico de Cálculos de ICMS", font=("Helvetica", 16, "bold")).pack(pady=20)

    treeview = ttk.Treeview(aba_historico, columns=("Tipo de Imposto", "Valor", "Data"), show="headings", height=10)
    treeview.heading("Tipo de Imposto", text="Tipo de Imposto")
    treeview.heading("Valor", text="Valor")
    treeview.heading("Data", text="Data")
    treeview.pack(fill="both", expand=True, padx=20, pady=10)

    # Buscar os cálculos do histórico do usuário no Firebase
    user_ref = db.collection('users').where('cpf_cnpj', '==', usuario).get()
    if user_ref:
        historico_ref = db.collection('historico').where('cpf_cnpj', '==', usuario)
        for doc in historico_ref.stream():
            doc_data = doc.to_dict()
            treeview.insert("", "end", values=(doc_data['tipo_imposto'], f"R$ {doc_data['valor']:.2f}", doc_data['data']))

    # Função para exportar o histórico para PDF
    def exportar_pdf(usuario):
        user_ref = db.collection('users').where('cpf_cnpj', '==', usuario).get()
        if user_ref:
            historico_ref = db.collection('historico').where('cpf_cnpj', '==', usuario)
            file_name = f"Historico_{usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(file_name, pagesize=letter)

            # Cabeçalho
            c.setFont("Helvetica-Bold", 16)
            c.drawString(200, 750, f"Histórico de Cálculos de {usuario}")
            c.setFont("Helvetica", 12)
            c.drawString(50, 730, "Tipo de Imposto")
            c.drawString(200, 730, "Valor")
            c.drawString(350, 730, "Data")

            y_position = 710
            for doc in historico_ref.stream():
                doc_data = doc.to_dict()
                c.drawString(50, y_position, doc_data['tipo_imposto'])
                c.drawString(200, y_position, f"R$ {doc_data['valor']:.2f}")
                c.drawString(350, y_position, doc_data['data'].strftime("%d/%m/%Y"))
                y_position -= 20

            c.save()
            messagebox.showinfo("Sucesso", f"PDF exportado com sucesso! Arquivo: {file_name}")

    # Botão para exportar para PDF
    btn_exportar_pdf = ttk.Button(aba_exportar, text="Exportar Histórico para PDF", command=lambda: exportar_pdf(usuario), style="success.TButton")
    btn_exportar_pdf.pack(pady=20)

    # Botão para voltar para o login
    btn_voltar = ttk.Button(tela_icms, text="Voltar", command=tela_icms.destroy, style="info.TButton")
    btn_voltar.pack(pady=10)

def exportar_pdf_ir(usuario):
    user_ref = db.collection('users').where('cpf_cnpj', '==', usuario).get()
    if user_ref:
        historico_ref = db.collection('historico').where('cpf_cnpj', '==', usuario)
        file_name = f"Historico_IR_{usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(file_name, pagesize=letter)

        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, 750, f"Histórico de Cálculos de IR - {usuario}")
        c.setFont("Helvetica", 12)
        c.drawString(50, 730, "Tipo de Imposto")
        c.drawString(200, 730, "Valor")
        c.drawString(350, 730, "Data")

        y_position = 710
        for doc in historico_ref.stream():
            doc_data = doc.to_dict()
            if doc_data['tipo_imposto'] == 'IR':  # Filtra apenas os cálculos de IR
                c.drawString(50, y_position, doc_data['tipo_imposto'])
                c.drawString(200, y_position, f"R$ {doc_data['valor']:.2f}")
                c.drawString(350, y_position, doc_data['data'].strftime("%d/%m/%Y"))
                y_position -= 20

        c.save()
        messagebox.showinfo("Sucesso", f"PDF exportado com sucesso! Arquivo: {file_name}")


# Função para abrir a tela de cálculo de Imposto de Renda com abas
def abrir_tela_calculo_imposto_renda(usuario):
    tela_imposto_renda = tk.Toplevel(tela_login)
    tela_imposto_renda.title("Cálculo de Imposto de Renda")
    tela_imposto_renda.geometry("600x400")

    # Criando as abas
    notebook = ttk.Notebook(tela_imposto_renda)
    aba_calculo = ttk.Frame(notebook)
    aba_historico = ttk.Frame(notebook)

    notebook.add(aba_calculo, text="Cálculo IR")
    notebook.add(aba_historico, text="Histórico")

    notebook.pack(expand=True, fill="both")

    # Aba de Cálculo IR
    header_label = tk.Label(aba_calculo, text="Calculadora de Impostos de Pessoa Física", font=("Helvetica", 16))
    header_label.pack(pady=10)

    ttk.Label(aba_calculo, text="Rendimento Bruto:", font=("Helvetica", 12)).pack(pady=10)
    entry_rendimento = ttk.Entry(aba_calculo)
    entry_rendimento.pack(pady=5)

    ttk.Label(aba_calculo, text="Descontos:", font=("Helvetica", 12)).pack(pady=10)
    entry_descontos = ttk.Entry(aba_calculo)
    entry_descontos.pack(pady=5)

    ttk.Label(aba_calculo, text="Imposto de Renda a Pagar:", font=("Helvetica", 12)).pack(pady=10)
    label_imposto = ttk.Label(aba_calculo, font=("Helvetica", 12))
    label_imposto.pack(pady=5)

    def calcular_ir(usuario):
        try:
            rendimento_bruto = float(entry_rendimento.get())
            descontos = float(entry_descontos.get())

            # Cálculo do Imposto de Renda
            imposto = rendimento_bruto * 0.15 - descontos
            label_imposto.config(text=f"Imposto de Renda a Pagar: R$ {imposto:.2f}")
            
            # Salvar no Firebase
            user_ref = db.collection('users').where('cpf_cnpj', '==', usuario).get()
            if user_ref:
                db.collection('historico').add({
                    'cpf_cnpj': usuario,
                    'tipo_imposto': 'IR',
                    'valor': imposto,
                    'data': firestore.SERVER_TIMESTAMP
                })
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos.")

    btn_calcular_ir = ttk.Button(aba_calculo, text="Calcular IR", command=lambda: calcular_ir(usuario))
    btn_calcular_ir.pack(pady=10)

    # Aba de Histórico
    ttk.Label(aba_historico, text="Histórico de Cálculos de IR", font=("Helvetica", 16, "bold")).pack(pady=20)

    treeview_ir = ttk.Treeview(aba_historico, columns=("Tipo de Imposto", "Valor", "Data"), show="headings", height=10)
    treeview_ir.heading("Tipo de Imposto", text="Tipo de Imposto")
    treeview_ir.heading("Valor", text="Valor")
    treeview_ir.heading("Data", text="Data")
    treeview_ir.pack(fill="both", expand=True, padx=20, pady=10)

    # Buscar os cálculos do histórico do usuário no Firebase
    user_ref = db.collection('users').where('cpf_cnpj', '==', usuario).get()
    if user_ref:
        historico_ref = db.collection('historico').where('cpf_cnpj', '==', usuario)
        for doc in historico_ref.stream():
            doc_data = doc.to_dict()
            treeview_ir.insert("", "end", values=(doc_data['tipo_imposto'], f"R$ {doc_data['valor']:.2f}", doc_data['data']))

    btn_voltar = ttk.Button(tela_imposto_renda, text="Voltar", command=tela_imposto_renda.destroy, style="info.TButton")
    btn_voltar.pack(pady=10)

    # Botão para exportar para PDF do IR
    btn_exportar_pdf_ir = ttk.Button(aba_historico, text="Exportar Histórico de IR para PDF", command=lambda: exportar_pdf_ir(usuario), style="success.TButton")
    btn_exportar_pdf_ir.pack(pady=20)


# Tela de Login
tela_login = tk.Tk()
tela_login.title("Tela de Login")
tela_login.geometry("300x300")

label_usuario = ttk.Label(tela_login, text="CPF ou CNPJ:", font=("Helvetica", 12))
label_usuario.pack(pady=10)
entry_usuario = ttk.Entry(tela_login, width=30)
entry_usuario.pack(pady=5)

label_senha = ttk.Label(tela_login, text="Senha:", font=("Helvetica", 12))
label_senha.pack(pady=10)
entry_senha = ttk.Entry(tela_login, width=30, show="*")
entry_senha.pack(pady=5)

btn_login = ttk.Button(tela_login, text="Login", command=realizar_login, style="primary.TButton")
btn_login.pack(pady=20)

# Botão de Cadastro
btn_cadastro = ttk.Button(tela_login, text="Cadastrar", command=abrir_tela_cadastro, style="secondary.TButton")
btn_cadastro.pack(pady=5)

tela_login.mainloop()
