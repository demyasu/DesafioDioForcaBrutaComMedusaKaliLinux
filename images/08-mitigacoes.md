# Mitigações recomendadas — Desafio Medusa

| Vulnerabilidade encontrada | Evidência | Mitigação |
|----------------------------|-----------|-----------|
| FTP com login anônimo (`230 Login successful`) | `02-servicos-validados.txt` | Desabilitar `anonymous_enable=YES` no vsFTPd; migrar para SFTP; aplicar fail2ban; MFA |
| Credenciais fracas (`msfadmin:msfadmin`, `admin:password`) | `04-medusa-ftp.txt`, `06-medusa-webform.txt` | Política de senhas fortes; MFA; rotação periódica; nunca usar credenciais padrão |
| DVWA sem rate limiting | `06-medusa-webform.txt` | Limite de tentativas por IP; CAPTCHA; bloqueio progressivo; logs e alertas |
| Enumeração de usuários via SMB/NetBIOS | `07-smb-acesso.txt` | Respostas genéricas de erro; desabilitar SMBv1 e NetBIOS; firewall restritivo |
| Password spraying em SMB | `07-smb-acesso.txt` | Lockout de conta após N falhas; monitorar Event ID 4625; MFA; senhas únicas por serviço |
| Superfície ampla de portas (21, 23, 445, 3306...) | `03-portas-abertas.txt` | Firewall com default-deny; desabilitar serviços não usados (telnet, rlogin); segmentação de rede |

## Recomendação geral de laboratório

Manter as VMs vulneráveis **sempre** em rede Host-Only/Internal, nunca em NAT com
port forwarding ou bridge para a rede corporativa. Após o estudo, desligar as VMs
ou restaurar os snapshots.
