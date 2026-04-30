import logging

from mcp.server.fastmcp import FastMCP
from suap_api import SuapClient
from suap_api.exceptions import SuapError

from suap_mcp.errors import handle_suap_error
from suap_mcp.log import log_tool

logger = logging.getLogger(__name__)


def register(mcp: FastMCP, client: SuapClient) -> None:
    """Registra as ferramentas do módulo comum no servidor MCP."""

    @mcp.tool()
    def get_my_data() -> dict:
        """Retorna os dados pessoais do usuário autenticado no SUAP.

        Inclui nome, CPF, e-mail, matrícula, vínculo institucional e URLs de foto.
        """
        with log_tool(logger, "get_my_data"):
            try:
                result = client.comum.get_my_data().raw
                logger.debug("  → dict(%d campos)", len(result))
                return result
            except SuapError as exc:
                handle_suap_error(exc)
