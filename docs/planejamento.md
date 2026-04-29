# Planejamento: SUAP MCP Server

## Visão Geral

Este documento planeja a construção de um servidor MCP (Model Context Protocol) que expõe a API do SUAP — Sistema Unificado de Administração Pública — como um conjunto de ferramentas (`tools`) consumíveis por agentes de IA (Claude, etc.).

O servidor será um wrapper thin sobre a biblioteca [`suap-api-wrapper`](https://github.com/seu-usuario/suap-api-wrapper), configurável via variáveis de ambiente (`.env`), sem gerenciar sessão local nem armazenar credenciais em disco.

---

## Objetivos

- Expor os recursos do SUAP como ferramentas MCP bem definidas.
- Autenticar via token estático fornecido em `.env`, sem interação do usuário.
- Manter o servidor sem estado (`stateless`): cada chamada de ferramenta é independente.
- Estrutura de código clara, com responsabilidades separadas e comentários nos pontos não óbvios.
- Facilitar extensão futura sem quebrar contratos existentes.

---

## Configuração via `.env`

O servidor precisa apenas de duas variáveis para funcionar:

```env
# URL base da instância SUAP da instituição
# Exemplos: https://suap.ifpi.edu.br | https://suap.ifrn.edu.br
SUAP_BASE_URL=https://suap.ifpi.edu.br

# Token JWT de acesso (obtido via SUAP web ou CLI do suap-api-wrapper)
SUAP_TOKEN=eyJ...
```

> **Por que token e não usuário/senha?**  
> Passar credenciais em `.env` de longa duração é arriscado: se o arquivo vazar, a conta é comprometida permanentemente. Um token tem validade limitada e pode ser revogado sem trocar a senha.  
> O servidor não faz refresh automático — o token deve ser renovado externamente quando expirar.

---

## Arquitetura

```
┌────────────────────────────────────────────────────────────┐
│  Agente IA (Claude Desktop / Claude Code / outro cliente)  │
└─────────────────────────┬──────────────────────────────────┘
                          │  MCP (stdio / SSE)
┌─────────────────────────▼──────────────────────────────────┐
│                     suap-mcp server                        │
│                                                            │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────────┐  │
│  │  tool/comum  │   │  tool/edu    │   │  tool/token   │  │
│  │  get_my_data │   │  get_periods │   │  verify_token │  │
│  └──────┬───────┘   └──────┬───────┘   └──────┬────────┘  │
│         │                  │                   │           │
│  ┌──────▼──────────────────▼───────────────────▼────────┐  │
│  │              SuapClient (suap-api-wrapper)            │  │
│  │         SuapClient(base_url, token=SUAP_TOKEN)        │  │
│  └──────────────────────────┬────────────────────────────┘  │
└─────────────────────────────│──────────────────────────────┘
                              │  HTTPS / JWT
                    ┌─────────▼─────────┐
                    │   SUAP REST API   │
                    └───────────────────┘
```

### Camadas

| Camada | Responsabilidade |
|--------|-----------------|
| `server.py` | Ponto de entrada: inicializa o cliente e registra ferramentas no MCP |
| `config.py` | Leitura e validação das variáveis de ambiente |
| `tools/comum.py` | Ferramentas do módulo `comum` da API |
| `tools/edu.py` | Ferramentas do módulo `edu` da API |
| `tools/token.py` | Ferramenta de verificação de token |
| `errors.py` | Mapeamento de exceções do wrapper para erros MCP |

---

## Estrutura de Diretórios

```
suap-mcp/
├── .env.example            # Variáveis necessárias (sem valores reais)
├── pyproject.toml          # Metadados e dependências do pacote
├── README.md               # Instruções de uso rápido
├── docs/
│   └── planejamento.md     # Este arquivo
└── src/
    └── suap_mcp/
        ├── __init__.py
        ├── server.py       # Entrypoint: cria o servidor MCP e monta as tools
        ├── config.py       # Lê e valida SUAP_BASE_URL e SUAP_TOKEN do .env
        ├── errors.py       # Converte SuapError → McpError com mensagem legível
        └── tools/
            ├── __init__.py
            ├── comum.py    # Tool: get_my_data
            ├── edu.py      # Tools: períodos, diários, disciplinas, etc.
            └── token.py    # Tool: verify_token
```

> **Convenção:** cada arquivo de `tools/` exporta uma função `register(mcp, client)` que recebe a instância do servidor MCP e o `SuapClient` já autenticado e declara suas ferramentas. `server.py` chama cada `register` na inicialização.

---

## Ferramentas MCP Planejadas

Cada ferramenta segue o padrão:
- **Nome:** snake_case, sem namespace (o agente entende pelo contexto).
- **Descrição:** frase curta em português para o agente de IA.
- **Parâmetros:** JSON Schema com `type`, `description` e `required` explícitos.
- **Retorno:** JSON serializável (dataclasses convertidos via `dataclasses.asdict`).

### `tools/token.py`

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `verify_token` | Verifica se o token configurado ainda é válido | — |

> Esta ferramenta é útil para o agente checar a saúde da conexão antes de chamar outras ferramentas.

---

### `tools/comum.py`

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `get_my_data` | Retorna dados pessoais do usuário autenticado | — |

---

### `tools/edu.py`

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `get_periods` | Lista semestres letivos disponíveis | — |
| `get_diaries` | Lista diários de um semestre | `semestre: string` (ex: `"2024.1"`) |
| `get_diary_professors` | Lista professores de um diário | `id_diario: integer` |
| `get_diary_classes` | Lista aulas registradas em um diário | `id_diario: integer` |
| `get_diary_materials` | Lista materiais de um diário | `id_diario: integer` |
| `get_material` | Retorna detalhes de um material | `id_material: integer` |
| `get_diary_assignments` | Lista trabalhos/avaliações de um diário | `id_diario: integer` |
| `get_disciplines` | Lista disciplinas e notas de um semestre | `semestre: string` |
| `get_student_data` | Retorna dados acadêmicos do aluno | — |
| `get_graduation_requirements` | Retorna requisitos para conclusão do curso | — |
| `get_messages` | Lista mensagens da caixa de entrada | `status: string` (`"nao_lidas"` \| `"lidas"` \| `"todas"`) |

> **Nota sobre `get_material_pdf`:** downloads binários (PDF) são excluídos desta versão inicial. O MCP não tem semântica de arquivo binário nativa; seria necessário retornar base64, o que não é amigável para o agente. Pode ser adicionado em versão futura via `resources` MCP.

---

## Tratamento de Erros (`errors.py`)

O `suap-api-wrapper` possui hierarquia própria de exceções. O mapeamento para erros MCP segue o princípio de menor surpresa:

```
SuapAuthError           → McpError (code: UNAUTHORIZED)   "Token inválido ou expirado"
SuapTokenExpiredError   → McpError (code: UNAUTHORIZED)   "Token expirado; renove o SUAP_TOKEN"
SuapNotFoundError       → McpError (code: NOT_FOUND)       "Recurso não encontrado"
SuapForbiddenError      → McpError (code: FORBIDDEN)       "Sem permissão para acessar este recurso"
SuapValidationError     → McpError (code: INVALID_PARAMS)  "Parâmetro inválido: {detalhes}"
SuapConnectionError     → McpError (code: INTERNAL_ERROR)  "Falha de rede ao acessar o SUAP"
SuapServerError         → McpError (code: INTERNAL_ERROR)  "Erro interno no servidor SUAP"
SuapRequestError        → McpError (code: INTERNAL_ERROR)  "Erro inesperado: {detalhes}"
```

> Nunca repassar o stack trace Python para o agente — expõe detalhes internos desnecessários. Logar localmente (stderr), retornar mensagem limpa via MCP.

---

## Cuidados Arquiteturais

### 1. Sem estado em memória entre chamadas
O `SuapClient` é instanciado **uma vez** na inicialização do servidor e compartilhado entre todas as chamadas. Como o cliente usa apenas token estático (sem refresh), não há mutação de estado entre requisições — isso é seguro.

```
# Correto: uma instância, token imutável, sem sessão em disco
client = SuapClient(base_url=cfg.base_url, token=cfg.token)
```

### 2. Validação de configuração na inicialização
`config.py` deve falhar rapidamente (`fail-fast`) se `SUAP_BASE_URL` ou `SUAP_TOKEN` estiverem ausentes, antes de registrar qualquer ferramenta. Melhor erro claro no startup do que falha opaca em runtime.

### 3. Serialização segura dos modelos
Os dataclasses do wrapper não são JSON-serializáveis diretamente. Usar `dataclasses.asdict()` em todos os retornos. Campos `None` devem ser preservados (não omitidos) para que o agente possa inspecionar a estrutura completa.

### 4. Sem lógica de negócio nas tools
As funções de tool são finas: validam tipos básicos de parâmetro, chamam o método do cliente, convertem o retorno. Toda lógica de negócio fica no wrapper subjacente.

### 5. Descrições de ferramentas como contrato
As descrições das tools são consumidas pelo agente — são tão importantes quanto a assinatura de função. Devem ser específicas, mencionar o formato dos parâmetros e citar exemplos quando ambíguos (`semestre: "2024.1"`).

### 6. Logging estruturado
Usar `logging` padrão do Python (não `print`). Nível `DEBUG` para requisições, `WARNING` para erros recuperáveis, `ERROR` para falhas que afetam a ferramenta. O servidor MCP roda em stdio — logs **devem** ir para `stderr`, nunca `stdout`.

### 7. Transport: stdio por padrão
O servidor usará transport `stdio` (padrão MCP para integração com Claude Desktop / Claude Code). SSE pode ser adicionado como opção futura via flag `--transport sse`.

---

## Dependências

```toml
[project]
name = "suap-mcp"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
    "mcp[cli]>=1.0",          # SDK oficial do Model Context Protocol
    "suap-api-wrapper>=0.1",  # Wrapper da API SUAP — instalado diretamente do PyPI
    "python-dotenv>=1.0",     # Leitura do .env
]

[project.scripts]
suap-mcp = "suap_mcp.server:main"
```

---

## Comentários no Código: Diretrizes

Comentar **apenas o que não é óbvio** para um leitor familiarizado com Python e MCP:

| Situação | Comentar? | Exemplo |
|----------|-----------|---------|
| Nome da função já diz tudo | Não | `def get_periods(...)` |
| Workaround ou limitação da API | Sim | `# A API retorna lista vazia (não 404) quando o semestre não existe` |
| Decisão arquitetural não óbvia | Sim | `# client é criado uma vez e reutilizado: token estático, sem estado mutável` |
| Mapeamento de erro não intuitivo | Sim | `# SuapTokenExpiredError também cobre refresh falho — tratar igual a AuthError` |
| Formato de parâmetro ambíguo | Na docstring da tool | `semestre: Semestre no formato "YYYY.N", ex: "2024.1"` |
| Bloco de código autoexplicativo | Não | loop, list comprehension simples |

---

## Fases de Implementação

### Fase 1 — Fundação
- [ ] `pyproject.toml` com dependências
- [ ] `.env.example` com as duas variáveis
- [ ] `config.py`: leitura e validação de env vars com `fail-fast`
- [ ] `errors.py`: mapeamento de exceções
- [ ] `server.py`: esqueleto do servidor MCP, sem tools ainda

### Fase 2 — Ferramentas Core
- [ ] `tools/token.py`: `verify_token`
- [ ] `tools/comum.py`: `get_my_data`
- [ ] `tools/edu.py`: `get_periods`, `get_diaries`, `get_disciplines`, `get_student_data`

### Fase 3 — Ferramentas de Detalhe
- [ ] `tools/edu.py`: `get_diary_professors`, `get_diary_classes`, `get_diary_materials`, `get_material`, `get_diary_assignments`
- [ ] `tools/edu.py`: `get_graduation_requirements`, `get_messages`

### Fase 4 — Qualidade
- [ ] Testes de integração com mock do `SuapClient`
- [ ] Documentação de uso no `README.md`
- [ ] Validação com Claude Desktop (instalação local via `mcp install`)

---

## Referências

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [suap-api-wrapper — PyPI](https://pypi.org/project/suap-api-wrapper/)
- [SUAP API v2 — documentação oficial da instância](https://suap.ifpi.edu.br/api/docs/)
