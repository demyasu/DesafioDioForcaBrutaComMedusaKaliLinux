# -*- coding: utf-8 -*-
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

XLSX = Path(r"D:\\Desafio Dio\\Desafio Entregar\\Casos_de_Teste_Medusa.xlsx")
IMG_DIR = Path(r"D:\\Desafio Dio\\Desafio Entregar\\images")
ABA = "Capturas de Tela"

wb = load_workbook(XLSX)
if ABA in wb.sheetnames:
    del wb[ABA]

ws = wb.create_sheet(ABA)
# colocar logo depois de Evidências
idx = wb.sheetnames.index("Evidências") + 1
wb._sheets.remove(ws)
wb._sheets.insert(idx, ws)

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(vertical="top", wrap_text=True)
CENTER = Alignment(vertical="center", horizontal="center", wrap_text=True)

headers = ["ID", "Arquivo (em images/)", "O que deve aparecer", "Onde capturar",
           "Como capturar", "Status", "Prévia", "Observações"]
widths = [8, 34, 42, 18, 48, 16, 26, 40]

ws.append(headers)
for c in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=c)
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = CENTER
    cell.border = BORDER
    ws.column_dimensions[get_column_letter(c)].width = widths[c - 1]
ws.row_dimensions[1].height = 30
ws.freeze_panes = "A2"
ws.sheet_view.showGridLines = False

capturas = [
    ("CAP-01", "01-vms-iniciadas.png", "VirtualBox Manager com Kali e Metasploitable 'running'",
     "Windows", "Snipping Tool ou Win+Shift+S com o VirtualBox em foco", "Pendente",
     "Complementa o .txt já coletado"),
    ("CAP-02", "02-ip-kali.png", "Terminal: whoami, ip -4 a | grep inet e ping -c 2 192.168.56.101",
     "VM Kali", "Host+Shift+S (Host = Ctrl) ou Snipping Tool", "Pendente",
     "Deve mostrar 192.168.56.102/24 e 0% packet loss"),
    ("CAP-03", "03-nmap.png", "Saída do nmap -n -sV -Pn 192.168.56.101",
     "VM Kali", "Host+Shift+S ou Snipping Tool", "Pendente",
     "Evidência em texto: images/09-nmap-kali.txt"),
    ("CAP-04", "04-ftp-anonimo.png", "Sessão FTP com '230 Login successful' e comando ls",
     "VM Kali", "Host+Shift+S ou Snipping Tool", "Pendente",
     "Usuário anonymous / senha anonymous@test.com"),
    ("CAP-05", "05-medusa-ftp.png", "Linha ACCOUNT FOUND do Medusa no módulo FTP",
     "VM Kali", "Host+Shift+S ou Snipping Tool", "Pendente",
     "Substitui o placeholder images/04-medusa-ftp.txt"),
    ("CAP-06", "06-dvwa-login.png", "Validação do login DVWA (HTTP 302 -> index.php)",
     "VM Kali", "Renderização da saída real capturada via guestcontrol", "Pendente",
     "Evidência textual: 13-dvwa-curl.txt"),
    ("CAP-07", "07-medusa-webform.png", "Automação web: 36 tentativas, 1 credencial válida",
     "VM Kali", "Renderização da saída real capturada via guestcontrol", "Pendente",
     "Medusa web-form gerou falsos positivos; ver 14-medusa-webform-observacao.txt"),
    ("CAP-08", "08-enum4linux.png", "Lista de usuários do Samba (msfadmin, user, ...)",
     "VM Kali", "Host+Shift+S ou Snipping Tool", "Pendente",
     "Comando 10 da aba Comandos"),
    ("CAP-09", "09-medusa-smb.png", "Resultado do password spraying -M smb",
     "VM Kali", "Host+Shift+S ou Snipping Tool", "Pendente",
     "Comando 11 da aba Comandos"),
    ("CAP-10", "10-smbclient.png", "Listagem de arquivos do share via smbclient",
     "VM Kali", "Host+Shift+S ou Snipping Tool", "Pendente",
     "Comando 12 da aba Comandos"),
    ("CAP-11", "11-planilha-casos.png", "Planilha de casos de teste aberta no Excel",
     "Windows", "Snipping Tool ou Win+Shift+S", "Pendente",
     "Opcional: mostra a entrega organizada"),
]

for row_idx, cap in enumerate(capturas, start=2):
    cid, nome, visible, onde, como, status, obs = cap
    ws.cell(row=row_idx, column=1, value=cid)
    cell_file = ws.cell(row=row_idx, column=2, value=nome)
    ws.cell(row=row_idx, column=3, value=visible)
    ws.cell(row=row_idx, column=4, value=onde)
    ws.cell(row=row_idx, column=5, value=como)
    ws.cell(row=row_idx, column=6, value=status)
    ws.cell(row=row_idx, column=7, value="—")
    ws.cell(row=row_idx, column=8, value=obs)

    caminho = IMG_DIR / nome
    if caminho.exists():
        ws.cell(row=row_idx, column=6, value="Capturada")
        cell_file.hyperlink = str(caminho)
        cell_file.font = Font(color="0563C1", underline="single")
        try:
            img = XLImage(str(caminho))
            img.width = 190
            img.height = 115
            ws.add_image(img, f"G{row_idx}")
            ws.cell(row=row_idx, column=7, value="Imagem incorporada")
            ws.row_dimensions[row_idx].height = 90
        except Exception as exc:
            ws.cell(row=row_idx, column=7, value=f"Erro ao incorporar: {exc}")

    for col in range(1, 9):
        c = ws.cell(row=row_idx, column=col)
        c.alignment = WRAP
        c.border = BORDER
    if ws.row_dimensions[row_idx].height is None:
        ws.row_dimensions[row_idx].height = 48

ws.auto_filter.ref = f"A1:H{ws.max_row}"

dv = DataValidation(type="list", formula1='"Pendente,Capturada,Descartada"', allow_blank=False)
dv.error = "Selecione uma das opções"
dv.errorTitle = "Status inválido"
ws.add_data_validation(dv)
dv.add(f"F2:F{ws.max_row}")
ws.conditional_formatting.add(
    f"F2:F{ws.max_row}",
    FormulaRule(formula=['$F2="Capturada"'], fill=PatternFill("solid", fgColor="C6EFCE"))
)
ws.conditional_formatting.add(
    f"F2:F{ws.max_row}",
    FormulaRule(formula=['$F2="Pendente"'], fill=PatternFill("solid", fgColor="FFF2CC"))
)

nota_row = ws.max_row + 2
ws.merge_cells(start_row=nota_row, start_column=1, end_row=nota_row, end_column=8)
nota = ws.cell(row=nota_row, column=1)
nota.value = ("As imagens acima são renderizações das saídas REAIS capturadas dentro do Kali via "
              "VBoxManage guestcontrol, com o rodapé identificando a origem. Os arquivos .txt correspondentes "
              "estão em images/. Para capturas literais de tela, use Host+Shift+S no VirtualBox (Host = Ctrl).")
nota.font = Font(italic=True, color="7F6000")
nota.fill = PatternFill("solid", fgColor="FFF2CC")
nota.alignment = Alignment(vertical="center", wrap_text=True)
ws.row_dimensions[nota_row].height = 42

wb.save(XLSX)
print("Aba adicionada:", ABA)
print("Abas:", wb.sheetnames)
print("Capturas listadas:", len(capturas))
print("PNGs encontrados e incorporados:", sum(1 for c in capturas if (IMG_DIR / c[1]).exists()))

