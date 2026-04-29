# SUAP MCP Server

Servidor [Model Context Protocol (MCP)](https://modelcontextprotocol.io) que expõe a API do SUAP (Sistema Unificado de Administração Pública) como ferramentas para agentes de IA (Claude Desktop, Claude Code, etc.).

Este servidor permite que seu assistente de IA acesse dados acadêmicos, mensagens e informações institucionais diretamente do SUAP.

## Funcionalidades

O servidor oferece ferramentas para:

- **Dados Pessoais:** Consultar perfil do usuário autenticado.
- **Acadêmico:** Listar períodos letivos, diários de classe, notas, disciplinas e requisitos de graduação.
- **Comunicação:** Ler mensagens da caixa de entrada do SUAP.
- **Utilitários:** Verificar a validade do token de acesso.

## Pré-requisitos

- Python 3.10 ou superior.
- Um token de acesso (JWT) do SUAP.
- URL da instância do SUAP da sua instituição (ex: `https://suap.ifpi.edu.br`).

## Instalação

### Usando `uv` (Recomendado)

Se você utiliza o [uv](https://github.com/astral-sh/uv), pode rodar o servidor diretamente:

```bash
uvx suap-mcp
```

### Instalação Manual

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/suap-mcp.git
   cd suap-mcp
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # ou
   .venv\Scripts\activate     # Windows
   pip install .
   ```

## Configuração

O servidor é configurado via variáveis de ambiente ou um arquivo `.env` na raiz do projeto.

1. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```

2. Edite o `.env` com suas credenciais:
   ```env
   SUAP_BASE_URL=https://suap.suainstituicao.edu.br
   SUAP_TOKEN=seu_token_jwt_aqui
   ```

> **Nota:** O servidor não gerencia renovação de tokens. Você deve fornecer um token válido.

## Uso com Claude Desktop

Para usar com o Claude Desktop, adicione a seguinte configuração ao seu arquivo `claude_desktop_config.json`:

### Usando `uvx` (mais simples)

```json
{
  "mcpServers": {
    "suap": {
      "command": "uvx",
      "args": ["suap-mcp"],
      "env": {
        "SUAP_BASE_URL": "https://suap.suainstituicao.edu.br",
        "SUAP_TOKEN": "seu_token_jwt_aqui"
      }
    }
  }
}
```

### Usando Python instalado

```json
{
  "mcpServers": {
    "suap": {
      "command": "python",
      "args": ["-m", "suap_mcp.server"],
      "env": {
        "SUAP_BASE_URL": "https://suap.suainstituicao.edu.br",
        "SUAP_TOKEN": "seu_token_jwt_aqui"
      }
    }
  }
}
```

## Ferramentas Disponíveis

| Nome | Descrição |
|------|-----------|
| `verify_token` | Verifica se o token configurado ainda é válido. |
| `get_my_data` | Retorna dados pessoais do usuário autenticado. |
| `get_periods` | Lista semestres letivos disponíveis. |
| `get_diaries` | Lista diários de um semestre específico. |
| `get_disciplines` | Lista disciplinas e notas de um semestre. |
| `get_student_data` | Retorna dados acadêmicos consolidados do aluno. |
| `get_messages` | Lista mensagens (lidas, não lidas ou todas). |
| ... e mais. | |

## Desenvolvimento

Para rodar em modo de desenvolvimento com recarregamento automático (usando o MCP Inspector):

```bash
npx @modelcontextprotocol/inspector suap-mcp
```

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.
