# Automação visual do desafio (VS Code + Cypress)

Este projeto roda a suíte do desafio com **visualização**: você vê o comando
sendo digitado em um terminal na tela e, na sequência, o comando é **executado
de verdade** dentro da VM Kali (`192.168.56.102`) via `VBoxManage guestcontrol`.
Depois, o Cypress abre o **DVWA** no navegador, faz login e tira capturas.

> ⚠️ Tudo acontece no laboratório isolado (Host-Only). Nenhum ataque sai para a internet.

## Pré-condições

1. VirtualBox com as VMs ligadas:
   ```powershell
   & 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' list runningvms
   ```
   Devem aparecer `kali-linux-2026.3-virtualbox-amd64` e `Metasploitabl`.
2. Wordlists já presentes no Kali em `/home/kali/desafio/wordlists/`.
3. Node 18+ (testado com Node 22) e, para o modo Cypress, Chrome/Edge instalado.

## Opção 1 — Cypress (recomendado, com navegador visível)

Abra esta pasta no **VS Code** e, no terminal integrado:

```powershell
npm install
npm run open
```

Na janela do Cypress, selecione `suite-desafio.cy.js`. Você verá:

- o terminal `/terminal.html` com os comandos sendo digitados;
- a saída real de `whoami`, `ip`, `ping`, `nmap`, `medusa`, `enum4linux`, `smbclient`;
- a abertura do DVWA, login com `admin/password` e capturas de tela.

Para executar sem abrir a interface:

```powershell
npm run run
```

As capturas ficam em `cypress/screenshots/` e são copiadas automaticamente
para `../images/` com o prefixo `cypress-`.

**Validação executada em 20/11/2026:** `npm run run` → **2 testes passando**,
**11 capturas geradas**. O teste 1 cobre o terminal (7 comandos reais no Kali) e
o teste 2 cobre o DVWA (login + página de brute force). Eles foram separados
porque o Cypress exige `cy.origin()`/testes distintos ao trocar de origem
(`127.0.0.1` → `192.168.56.101`).

### O que cada task faz (`cypress.config.js`)

| Task | Função |
|------|--------|
| `kaliRun` | Executa o comando dentro do Kali via `VBoxManage guestcontrol run` |
| `salvarEvidencia` | Grava a saída em `images/cypress-<nome>.txt` |
| `copiarScreenshots` | Copia os PNGs do Cypress para `images/` |

## Opção 2 — Script Python no VS Code (sem Cypress)

```powershell
python executar_vscode.py
```

Ele imprime os comandos com efeito de digitação no terminal, executa no Kali,
salva `images/vscode-*.txt` e abre o DVWA no navegador padrão. Se `pyautogui`
estiver instalado (`pip install pyautogui`), salva também `vscode-tela-final.png`.

## Estrutura

```text
automacao/
├── package.json
├── cypress.config.js        # tasks + servidor local do terminal
├── terminal.html            # terminal visual com efeito de digitação
├── cypress/e2e/suite-desafio.cy.js
├── executar_vscode.py       # alternativa Python
└── README.md
```

## Solução de problemas

- **`Could not load "smb"`**: use `-M smbnt` (já corrigido nos comandos).
- **DVWA não abre**: confirme que o Metasploitable está em `192.168.56.101`.
- **Terminal aparece mas não executa**: confirme que o Kali está ligado e que
  o usuário é `kali`/`kali`.
- **Cypress não inicia**: rode `npx cypress verify`.
