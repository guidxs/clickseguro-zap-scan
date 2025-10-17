from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse

class Handler(SimpleHTTPRequestHandler):
    # Adiciona cabeçalhos inseguros em TODAS as respostas (proposital para gerar High)
    def end_headers(self):
        # CORS totalmente aberto com credenciais: configuração perigosa (trigger de High)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        # Cookie sem HttpOnly/Secure/SameSite
        self.send_header("Set-Cookie", "sessionid=abc123; Path=/")
        super().end_headers()

    def do_GET(self):
        # Mostra formulário de login em /login
        if self.path.startswith("/login"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Login</title></head>
                <body>
                    <h2>Formul\xc3\xa1rio de Login (vulneravel)</h2>
                    <form method="POST" action="/login">
                        Usuario: <input type="text" name="username"><br>
                        Senha: <input type="password" name="password"><br>
                        <input type="submit" value="Entrar">
                    </form>
                    <!-- Dados sens
veis propositalmente inseridos para gatilhar detectores de PII -->
                    <!-- CC: 4111 1111 1111 1111 | SSN: 123-45-6789 -->
                    <p><a href="/login?username=test&password=secret">Exemplo de URL com credenciais (inseguro)</a></p>
                    <p>Para testes com ZAP: tente enviar payloads no campo "usuario".</p>
                </body>
                </html>
            """)
        elif self.path.startswith("/pii"):
            # Página contendo dados sensíveis para acionar regras High (Cartão de crédito e chave privada)
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            body = """
                <html>
                <body>
                    <h1>Dados Sensíveis (DEMO)</h1>
                    <p>Cartao de Credito (exemplo): 4111 1111 1111 1111</p>
                    <p>Visa (exemplo): 4539 1488 0343 6467</p>
                    <p>Mastercard (exemplo): 5500 0000 0000 0004</p>
                    <pre>
-----BEGIN PRIVATE KEY-----
MIIBVwIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEAxZ0v2xW2r8m9j9dC
fFakeKeyBlockForDemoOnlyDoNotUseInProductiony2d8mY1lq9H0Z+3J1p3b
QIDAQABAkAdemoPrivateKeyBlockThatShouldTriggerDetectors==
-----END PRIVATE KEY-----
                    </pre>
                    <p>Exemplo de chave exposta (PROPOSITAL para teste ZAP)</p>
                </body>
                </html>
            """
            self.wfile.write(body.encode("utf-8"))
        else:
            # Serve arquivos estáticos normalmente
            # Adiciona cabeçalhos CORS inseguros em todas as respostas
            super().do_GET()

    def do_POST(self):
        # Processa POST em /login
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            # Vulnerabilidade proposital:
            # - refletir o username diretamente no HTML (XSS refletido)
            # - exibir a senha (exposição de informação sensível)
            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            # Cabeçalhos inseguros propositalmente para fins de teste
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.end_headers()

            # ATENÇÃO: Intencionalmente inseguro para fins de teste
            resp = f"""
                <html>
                <body>
                    <h1>Bem-vindo, {username}!</h1>
                    <p>Sua senha é: {password}</p>
                    <p>(Esta pagina intencionalmente reflete dados sem validacao.)</p>
                </body>
                </html>
            """
            self.wfile.write(resp.encode('utf-8'))
        else:
            # Se outro POST, usar comportamento padrão
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("Servidor rodando em http://localhost:8080")
    server.serve_forever()
