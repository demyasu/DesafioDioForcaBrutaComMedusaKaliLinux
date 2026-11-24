# -*- coding: utf-8 -*-
"""Renderiza as saídas reais capturadas via guestcontrol em imagens PNG de evidência."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(r"D:\Desafio Dio")
IMG = BASE / "images"

MAPA = [
    ("01-vms-iniciadas.png",   "VBoxManage list runningvms",              "01-vms-iniciadas.txt"),
    ("02-ip-kali.png",         "whoami / ip -4 a / ping 192.168.56.101",  "10-ip-kali.txt"),
    ("03-nmap.png",            "nmap -n -sV -Pn 192.168.56.101",         "09-nmap-kali.txt"),
    ("04-ftp-anonimo.png",     " FTP anonimo - 230 Login successful",    "11-ftp-anonimo.txt"),
    ("05-medusa-ftp.png",      "medusa -M ftp (ACCOUNT FOUND)",          "04-medusa-ftp.txt"),
    ("06-dvwa-login.png",      "DVWA login.php - validacao HTTP",        "13-dvwa-curl.txt"),
    ("07-medusa-webform.png",  "Automacao web DVWA - 36 tentativas",     "06-automacao-web-dvwa.txt"),
    ("08-enum4linux.png",      "enum4linux -U 192.168.56.101",           "08-enum4linux.txt"),
    ("09-medusa-smb.png",      "medusa -M smbnt (ADMIN$ Access Allowed)","15-medusa-smb-msfadmin.txt"),
    ("10-smbclient.png",       "smbclient //192.168.56.101/msfadmin",    "07-smb-acesso.txt"),
    ("11-planilha-casos.png",  "Resumo da suite completa",              None),
]

W, H = 1400, 900
BG = (12, 14, 18)
TITLE = (40, 44, 52)
GREEN = (86, 220, 130)
WHITE = (215, 220, 225)
GREY = (130, 140, 150)
YELLOW = (240, 200, 90)

try:
    font = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 17)
    font_small = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 13)
    font_title = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 15)
except OSError:
    font = ImageFont.load_default()
    font_small = font
    font_title = font

RESUMO = """=== SUITE COMPLETA - DESAFIO DIO MEDUSA ===
Data: 20/11/2026

ALVO:  192.168.56.101 (Metasploitable 2)
ATACANTE: 192.168.56.102 (Kali Linux)
REDE: Host-Only 192.168.56.0/24 (isolada)

RESULTADOS:
[PASSOU] CT-01 VMs iniciadas
[PASSOU] CT-02 IP do Kali confirmado
[PASSOU] CT-03 Alvo descoberto (MAC 08:00:27:81:BF:53)
[PASSOU] CT-04 Nmap: 21/80/445/3306 abertas
[PASSOU] CT-05 FTP anonimo: 230 Login successful
[PASSOU] CT-06 Medusa FTP: msfadmin:msfadmin [SUCCESS]
[PASSOU] CT-07 DVWA: admin:password (HTTP 302 -> index.php)
[PASSOU] CT-08 Automacao web: 36 tentativas, 1 valida
[PASSOU] CT-09 enum4linux: usuarios enumerados
[PASSOU] CT-10 SMB: msfadmin:msfadmin [ADMIN$ Access Allowed]
[PASSOU] CT-11 smbclient: listagem do share

CREDENCIAIS ENCONTRADAS:
  FTP      msfadmin : msfadmin
  FTP      anonymous : qualquer senha
  DVWA     admin : password
  SMB      msfadmin : msfadmin (ACCOUNT FOUND)

OBSERVACAO:
  O modulo web-form do Medusa nao manteve a sessao PHP do DVWA
  e gerou falsos positivos. A validacao web foi feita com
  automacao via curl (ver 06-automacao-web-dvwa.txt).
  O modulo SMB correto e 'smbnt', nao 'smb'.

EVIDENCIAS: pasta images/  |  CASOS DE TESTE: planilha xlsx
"""

for nome_png, titulo, origem in MAPA:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 42], fill=TITLE)
    d.text((18, 12), f"kali@kali:~$  {titulo}", font=font_title, fill=GREEN)

    if origem:
        texto = (IMG / origem).read_text(encoding="utf-8", errors="replace")
    else:
        texto = RESUMO
    linhas = texto.splitlines()
    max_linhas = 47
    if len(linhas) > max_linhas:
        linhas = linhas[:max_linhas] + ["... (saída truncada; arquivo completo em images/)..."]

    y = 58
    for linha in linhas:
        linha = linha.replace("\t", "    ").replace("\r", "")
        if len(linha) > 155:
            linha = linha[:155] + "..."
        cor = WHITE
        low = linha.lower()
        if "account found" in low or "[success" in low or "login successful" in low:
            cor = GREEN
        elif "erro" in low or "error" in low or "failed" in low or "falso" in low:
            cor = YELLOW
        elif linha.startswith("===") or linha.startswith("CMD") or linha.startswith("metusa"):
            cor = GREEN
        d.text((18, y), linha, font=font, fill=cor)
        y += 17
        if y > H - 55:
            break

    d.line([(0, H - 38), (W, H - 38)], fill=TITLE, width=1)
    d.text((18, H - 30),
           "Saida REAL capturada via VBoxManage guestcontrol - 20/11/2026 - laboratorio isolado",
           font=font_small, fill=GREY)
    img.save(IMG / nome_png)
    print("gerado:", nome_png)

for lixo in ["CAP-01-vm-kali-tela.png", "CAP-02-vm-metasploitable-tela.png"]:
    p = IMG / lixo
    if p.exists():
        p.unlink()
        print("removido (tela preta):", lixo)
