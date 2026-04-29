import logging

from mcp.server.fastmcp import FastMCP
from suap_api import SuapClient
from suap_api.exceptions import SuapError

from suap_mcp.errors import handle_suap_error

logger = logging.getLogger(__name__)


def register(mcp: FastMCP, client: SuapClient, access_token: str) -> None:
    """Registra a ferramenta de verificação de token no servidor MCP."""

    @mcp.tool()
    def verify_token() -> dict:
        """Verifica se o token SUAP configurado ainda é válido.

        Use esta ferramenta antes de chamar outras para confirmar
        que a autenticação está ativa.
        """
        try:
            valid = client.token.verify(access_token)
            return {"valid": valid}
        except SuapError as exc:
            handle_suap_error(exc)
