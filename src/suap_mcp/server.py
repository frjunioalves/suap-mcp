import logging

from mcp.server.fastmcp import FastMCP
from suap_api import SuapClient

from suap_mcp.config import load_config
from suap_mcp.log import setup_logging
from suap_mcp.tools import comum, edu, token

setup_logging()
logger = logging.getLogger(__name__)


def build_server() -> FastMCP:
    """Inicializa configuração, cliente SUAP e registra todas as ferramentas MCP."""
    cfg = load_config()

    # Uma única instância compartilhada entre todas as chamadas de ferramentas.
    # O token é estático (sem refresh automático), portanto não há mutação de estado entre requisições.
    client = SuapClient(cfg.base_url, token=cfg.token)

    mcp = FastMCP("SUAP")

    token.register(mcp, client, cfg.token)
    comum.register(mcp, client)
    edu.register(mcp, client)

    logger.info("Servidor SUAP MCP inicializado — %d ferramentas registradas", 13)
    return mcp


def main() -> None:
    mcp = build_server()
    mcp.run()


if __name__ == "__main__":
    main()
