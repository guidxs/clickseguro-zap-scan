from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse

class Handler(SimpleHTTPRequestHandler):
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
                    <p>Para testes com ZAP: tente enviar payloads no campo "usuario".</p>
                </body>
                </html>
            """)
        else:
            # Serve arquivos estáticos normalmente
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
            self.end_headers()

            # ATENÇÃO: este output é intencionalmente inseguro para fins de teste
            resp = f"""
                <html>
                <body>
                    <h1>Bem-vindo, {username}!</h1>
                    <p>Sua senha é: {password}</p>
                    <p>(Esta p\xc3\xa1gina intencionalmente reflete dados sem valida\xc3\xa7\xc3\xa3o.)</p>
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
