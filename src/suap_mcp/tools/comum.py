import dataclasses
import logging

from mcp.server.fastmcp import FastMCP
from suap_api import SuapClient
from suap_api.exceptions import SuapError

from suap_mcp.errors import handle_suap_error

logger = logging.getLogger(__name__)


def register(mcp: FastMCP, client: SuapClient) -> None:
    """Registra as ferramentas do módulo comum no servidor MCP."""

    @mcp.tool()
    def get_my_data() -> dict:
        """Retorna os dados pessoais do usuário autenticado no SUAP.

        Inclui nome, CPF, e-mail, matrícula, vínculo institucional e URLs de foto.
        """
        try:
            data = client.comum.get_my_data()
            return dataclasses.asdict(data)
        except SuapError as exc:
            handle_suap_error(exc)
