Feature: Auditoria de forca bruta com Medusa em ambiente controlado
  Como estudante de seguranca da DIO
  Quero validar a resistencia de servicos a ataques de forca bruta
  Para documentar o aprendizado e propor mitigacoes adequadas

  Background: Ambiente de laboratorio isolado
    Given o VirtualBox 7.2.22 esteja instalado no host Windows
    And o adaptador "VirtualBox Host-Only Ethernet Adapter" esteja configurado em 192.168.56.1/24 com DHCP desativado
    And a VM "kali-linux-2026.3-virtualbox-amd64" esteja na rede host-only com IP 192.168.56.102
    And a VM "Metasploitabl" esteja na rede host-only com IP 192.168.56.101
    And as VMs estejam isoladas da internet

  @setup @vms
  Scenario: Iniciar as maquinas virtuais do desafio
    Given as VMs estejam inicialmente desligadas
    When executo "VBoxManage startvm kali-linux-2026.3-virtualbox-amd64 --type headless"
    And executo "VBoxManage startvm Metasploitabl --type headless"
    Then ambas devem aparecer em "VBoxManage list runningvms"
    And "VBoxManage showvminfo" deve reportar VMState="running" para as duas

  @recon @rede
  Scenario: Descobrir o endereco do alvo na rede host-only
    Given as VMs estejam rodando
    When faço varredura ICMP em 192.168.56.1/254 a partir do host
    Then os hosts 192.168.56.1, .100, .101 e .102 devem responder
    And a correlacao IP/MAC via "arp -a" deve identificar 192.168.56.101 como Metasploitable e 192.168.56.102 como Kali

  @recon @portas
  Scenario: Enumera servicos expostos no alvo
    Given o alvo 192.168.56.101 esteja alcancavel
    When executo "nmap -sV -Pn 192.168.56.101"
    Then devem ser encontradas as portas 21 (FTP vsFTPd 2.3.4), 80 (HTTP/DVWA), 445 (Samba) e 3306 (MySQL)
    E a pagina http://192.168.56.101/ deve responder HTTP 200 com link para /dvwa/

  @ftp @medusa @creditencial-fraca
  Scenario: Forca bruta bem sucedida em FTP com wordlist simples
    Given o servico FTP do Metasploitable esteja ativo na porta 21
    And existam as wordlists users.txt e passwords.txt
    When executo "medusa -h 192.168.56.101 -U users.txt -P passwords.txt -M ftp -t 4"
    Then a credencial "msfadmin:msfadmin" deve ser reportada como VALID
    E o acesso deve ser validado com "ftp 192.168.56.101" e comando "ls"
    E a saida deve ser salva em images/04-medusa-ftp.txt

  @ftp @anonimo
  Scenario: Acesso anonimo ao FTP sem forca bruta
    Given o servico FTP esteja ativo
    When envio "USER anonymous" e "PASS anonymous@test.com"
    Then o servidor deve responder "230 Login successful"
    E este achado deve ser registrado como evidencia em images/02-servicos-validados.txt

  @web @dvwa @automacao
  Scenario: Automacao de tentativas de login no formulario DVWA
    Given o DVWA esteja disponivel em http://192.168.56.101/dvwa/ com seguranca "low"
    And a wordlist de senhas esteja disponivel
    When executo "bash ~/desafio/dvwa_web_brute.sh"
    And cada tentativa usa um cookie jar novo e segue o redirect com curl -L
    Then a combinacao "admin:password" deve ser aceita
    E a URL final deve ser /index.php ( falha resulta em /login.php )
    E o resultado deve ser documentado em images/06-automacao-web-dvwa.txt
    E o limite do modulo web-form do Medusa deve ser registrado em images/14-medusa-webform-observacao.txt

  @smb @enum @spray
  Scenario: Password spraying em SMB apos enumeracao de usuarios
    Given o servico Samba esteja ativo na porta 445
    When executo "enum4linux -U 192.168.56.101"
    Then devem ser listados usuarios como msfadmin, user, postgres, service, sys e backup
    E esses usuarios devem ser salvos em wordlists/users-enum.txt
    When executo "medusa -h 192.168.56.101 -U users-enum.txt -P spray.txt -M smbnt -t 3"
    Then o spray com "password" nao deve encontrar contas fracas
    When executo "medusa -h 192.168.56.101 -u msfadmin -p msfadmin -M smbnt"
    Then devo ver "ACCOUNT FOUND ... msfadmin:msfadmin [SUCCESS (ADMIN$ - Access Allowed)]"
    E o acesso deve ser validado com "smbclient //192.168.56.101/msfadmin -U msfadmin%msfadmin -c 'ls'"

  @mitigacao
  Scenario: Recomendar medidas corretivas para cada vulnerabilidade
    Given os ataques tenham sido executados com sucesso no laboratorio
    Then devem ser documentadas mitigacoes para FTP, DVWA, SMB e enumeracao
    E as recomendacoes devem estar em images/08-mitigacoes.md e no README.md

  @entrega
  Scenario: Publicar o projeto como portfolio tecnico
    Given README.md, wordlists e pasta images estejam completos
    When faço commit e push para repositorio publico no GitHub
    Then o link do repositorio deve ser enviado no botao "Entregar Projeto" da DIO
