const { defineConfig } = require('cypress');
const { execFile } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const VBOX = 'C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe';
const VM = 'kali-linux-2026.3-virtualbox-amd64';
const USER = 'kali';
const PASS = 'kali';

const RAIZ = __dirname;
const IMG = path.join(RAIZ, '..', 'images');
const SCREENSHOTS = path.join(RAIZ, 'cypress', 'screenshots');
const PORTA = 3123;

function executarNoKali(comando) {
  const args = [
    'guestcontrol', VM, 'run',
    '--exe', '/bin/bash',
    '--username', USER, '--password', PASS,
    '--wait-stdout', '--', '-lc', comando
  ];
  return new Promise((resolve, reject) => {
    execFile(VBOX, args, { maxBuffer: 12 * 1024 * 1024, timeout: 240000 },
      (erro, stdout, stderr) => {
        const saida = `${stdout || ''}${stderr ? '\n' + stderr : ''}`.trim();
        if (erro && !saida) return reject(erro);
        resolve(saida);
      });
  });
}

function copiarScreenshots() {
  fs.mkdirSync(IMG, { recursive: true });
  if (!fs.existsSync(SCREENSHOTS)) return { copiados: 0 };
  let copiados = 0;
  const pastas = fs.readdirSync(SCREENSHOTS, { withFileTypes: true })
    .filter(d => d.isDirectory()).map(d => path.join(SCREENSHOTS, d.name));
  for (const pasta of pastas) {
    for (const arquivo of fs.readdirSync(pasta)) {
      if (!arquivo.toLowerCase().endsWith('.png')) continue;
      const destino = path.join(IMG, `cypress-${arquivo.replace(/[^\w.-]/g, '_')}`);
      fs.copyFileSync(path.join(pasta, arquivo), destino);
      copiados++;
    }
  }
  return { copiados };
}

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      fs.mkdirSync(IMG, { recursive: true });

      // Servidor local que entrega a pagina do "terminal Kali" para o Cypress
      const servidor = http.createServer((req, res) => {
        const arquivo = path.join(RAIZ, 'terminal.html');
        fs.readFile(arquivo, (erro, conteudo) => {
          if (erro) { res.writeHead(404); res.end('terminal.html nao encontrado'); return; }
          res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
          res.end(conteudo);
        });
      });
      servidor.listen(PORTA, '127.0.0.1');

      on('after:run', () => servidor.close());

      on('task', {
        kaliRun(comando) {
          return executarNoKali(comando);
        },
        salvarEvidencia({ nome, conteudo }) {
          fs.writeFileSync(path.join(IMG, nome), conteudo, 'utf8');
          return { salvo: nome };
        },
        copiarScreenshots() {
          return copiarScreenshots();
        },
        listarEvidencias() {
          return fs.readdirSync(IMG).filter(f => f.endsWith('.txt'));
        }
      });

      config.env = Object.assign({}, config.env, {
        alvo: '192.168.56.101',
        atacante: '192.168.56.102'
      });
      return config;
    },
    specPattern: 'cypress/e2e/**/*.cy.js',
    supportFile: false,
    screenshotsFolder: 'cypress/screenshots',
    video: false,
    defaultCommandTimeout: 15000,
    pageLoadTimeout: 60000
  }
});
