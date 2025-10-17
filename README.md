# clickseguro-zap-scan

Projeto simples para demonstrar um pipeline de segurança com OWASP ZAP (Baseline) no GitHub Actions, varrendo um servidor local vulnerável de propósito.

## Como rodar localmente

1. Requisitos: Python 3.8+.
2. Inicie o servidor local:

	 - Windows (PowerShell):
		 ```powershell
		 python .\server.py
		 ```
	 - Linux/macOS:
		 ```bash
		 python3 server.py
		 ```

3. Abra http://localhost:8080 no navegador.

O servidor serve `index.html` e expõe uma rota `/login` com vulnerabilidades propositalmente inseridas para fins de teste (por exemplo XSS refletido).

## Pipeline GitHub Actions (ZAP Baseline)

O workflow em `.github/workflows/zap-scan.yml` faz o seguinte:

- Faz checkout do repositório.
- Sobe o servidor local em background na porta 8080.
- Executa o ZAP Baseline usando a action `zaproxy/action-baseline` apontando para `http://host.docker.internal:8080` (necessário para o container do ZAP acessar o serviço do runner).
- Publica os relatórios (HTML e JSON) como artefatos.
- Falha o job se forem encontrados alertas de severidade High.

Os relatórios são salvos em `zap-reports/report.html` e `zap-reports/report.json` dentro do workspace do runner e enviados como artefatos.

## Ajustes úteis

- Para mudar o alvo ou a severidade que falha o pipeline, edite a etapa "Fail if High alerts exist" do workflow.
- Para adicionar exclusões/contexts/policies no ZAP, use `cmd_options` da action (ver docs da action para opções avançadas).

## Aviso

As vulnerabilidades em `server.py` são intencionais e servem apenas para testes de ferramentas de análise. Não use esse código em produção.
