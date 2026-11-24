# Relatório Final — Desafio DIO: Força Bruta com Medusa

**Data:** 20/11/2026  
**Ambiente:** VirtualBox 7.2.22 · rede Host-Only `192.168.56.0/24` (isolada)  
**Atacante:** Kali Linux `192.168.56.102` · **Alvo:** Metasploitable 2 `192.168.56.101`

---

## 1. Resultado consolidado

| ID | Caso de teste | Status | Evidência |
|----|---------------|--------|-----------|
| CT-01 | Iniciar VMs no VirtualBox | ✅ Passou | `images/01-vms-iniciadas.txt` |
| CT-02 | Confirmar IP do Kali (`.102`) | ✅ Passou | `images/10-ip-kali.txt` |
| CT-03 | Descobrir alvo (`.101`, MAC `08:00:27:81:BF:53`) | ✅ Passou | `images/02-servicos-validados.txt` |
| CT-04 | Nmap: 21, 80, 445, 3306 etc. | ✅ Passou | `images/09-nmap-kali.txt` |
| CT-05 | FTP anônimo: `230 Login successful` | ✅ Passou | `images/11-ftp-anonimo.txt` |
| CT-06 | Medusa FTP: `msfadmin:msfadmin` | ✅ Passou | `images/04-medusa-ftp.txt` |
| CT-07 | DVWA `admin:password` (URL final `/index.php`) | ✅ Passou | `images/13-dvwa-curl.txt` |
| CT-08 | Automação web: 36 tentativas, 1 válida | ✅ Passou | `images/06-automacao-web-dvwa.txt` |
| CT-09 | enum4linux: usuários enumerados | ✅ Passou | `images/08-enum4linux.txt` |
| CT-10 | SMB `msfadmin:msfadmin` `[ADMIN$ - Access Allowed]` | ✅ Passou | `images/15-medusa-smb-msfadmin.txt` |
| CT-11 | smbclient: listagem do share | ✅ Passou | `images/07-smb-acesso.txt` |
| CT-12 | Documentação + planilha + pacote | ✅ Passou | `Casos_de_Teste_Medusa.xlsx` |

**12/12 casos passaram.**

## 2. Credenciais encontradas

| Serviço | Usuário | Senha | Evidência |
|---------|---------|-------|-----------|
| FTP (vsFTPd 2.3.4) | `anonymous` | qualquer | `images/02-servicos-validados.txt` |
| FTP (vsFTPd 2.3.4) | `msfadmin` | `msfadmin` | `images/04-medusa-ftp.txt` |
| DVWA | `admin` | `password` | `images/06-automacao-web-dvwa.txt` |
| SMB (Samba 3.x/4.x) | `msfadmin` | `msfadmin` | `images/15-medusa-smb-msfadmin.txt` |

## 3. Comandos que funcionaram

```bash
# FTP
medusa -h 192.168.56.101 -U wordlists/users.txt -P wordlists/passwords.txt -M ftp -t 4

# DVWA (automação com curl, sessão nova por tentativa)
bash scripts/dvwa_web_brute.sh

# SMB (módulo correto é smbnt)
enum4linux -U 192.168.56.101
medusa -h 192.168.56.101 -U wordlists/users-enum.txt -P wordlists/spray.txt -M smbnt -t 3
medusa -h 192.168.56.101 -u msfadmin -p msfadmin -M smbnt
smbclient //192.168.56.101/msfadmin -U msfadmin%msfadmin -c 'ls'
```

## 4. Aprendizados técnicos

1. **`10.0.2.15/24` indica NAT** — a VM do laboratório precisa estar em Host-Only (`192.168.56.102`).
2. **Módulo SMB:** `-M smb` falha nesta instalação; o correto é `-M smbnt`.
3. **Medusa web-form x DVWA:** o módulo não mantém a sessão PHP e gera falsos positivos
   (marcou até a senha `ERRADO` como válida). A automação com `curl` + cookie jar
   novo por tentativa e verificação da URL final após `-L` é confiável.
4. **DVWA 302:** tanto sucesso quanto falha retornam 302; o critério é a URL final
   (`/index.php` = sucesso, `/login.php` = falha).
5. Toda a execução foi feita de forma isolada, sem exposição das VMs vulneráveis.

## 5. Conteúdo do pacote

- `README.md` — documentação completa do desafio
- `Casos_de_Teste_Medusa.xlsx` — 5 abas (Casos de Teste, Comandos, Evidências,
  Capturas de Tela com 11 imagens incorporadas, Ambiente)
- `gherkin/desafio-medusa.feature` — cenários Given/When/Then
- `wordlists/` — users, passwords, spray, users-enum
- `images/` — evidências textuais reais + 11 PNGs
- `scripts/` — scripts executados dentro do Kali
- `automacao/` — projeto Cypress + alternativa Python para VS Code
- `Entendendo o Desafio.md` — enunciado original

## 6. Automação visual (VS Code + Cypress)

Foi incluído o projeto `automacao/` com duas formas de executar a suíte vendo
os comandos sendo digitados:

1. **Cypress** — `npm install` → `npm run open` (ou `npm run run`).
   O terminal `terminal.html` mostra a digitação char a char enquanto o comando
   é executado de verdade no Kali via `VBoxManage guestcontrol`. Em seguida o
   DVWA é aberto no navegador, o login `admin:password` é feito e as telas são
   capturadas. Validação real: **2 testes passando, 11 capturas**.
2. **VS Code/Python** — `python executar_vscode.py` faz o mesmo no terminal
   integrado e abre o DVWA no navegador padrão.

A planilha ganhou as abas **`Automacao Cypress`** (11 etapas, todas `Passou`) e
**`Capturas Cypress`** (11 PNGs incorporados). Os arquivos também estão em
`images/` com prefixo `cypress-`.

> ⚠️ Uso estritamente educacional, em laboratório isolado e com autorização.
