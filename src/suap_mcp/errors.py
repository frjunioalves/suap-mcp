import logging

from suap_api.exceptions import (
    SuapAuthError,
    SuapConnectionError,
    SuapError,
    SuapForbiddenError,
    SuapNotFoundError,
    SuapRequestError,
    SuapServerError,
    SuapTokenExpiredError,
    SuapValidationError,
)

logger = logging.getLogger(__name__)


def handle_suap_error(exc: SuapError) -> None:
    """Converte exceções do suap-api-wrapper para erros com mensagens legíveis pelo agente.

    Loga detalhes internos no stderr e levanta RuntimeError/ValueError limpos,
    sem expor stack traces ou detalhes de implementação para o agente de IA.
    """
    logger.error("Erro ao acessar SUAP: %s", exc)

    # SuapTokenExpiredError também cobre falha no refresh automático — tratar igual a AuthError
    if isinstance(exc, (SuapAuthError, SuapTokenExpiredError)):
        raise RuntimeError(
            "Token inválido ou expirado. Renove o SUAP_TOKEN no arquivo .env."
        ) from exc

    if isinstance(exc, SuapNotFoundError):
        raise RuntimeError("Recurso não encontrado no SUAP.") from exc

    if isinstance(exc, SuapForbiddenError):
        raise RuntimeError("Sem permissão para acessar este recurso.") from exc

    # ValueError sinaliza parâmetro inválido — FastMCP converte para INVALID_PARAMS
    if isinstance(exc, SuapValidationError):
        raise ValueError(f"Parâmetro inválido: {exc}") from exc

    if isinstance(exc, SuapConnectionError):
        raise RuntimeError(
            "Falha de rede ao acessar o SUAP. Verifique SUAP_BASE_URL e a conectividade."
        ) from exc

    if isinstance(exc, (SuapServerError, SuapRequestError)):
        raise RuntimeError(f"Erro no servidor SUAP: {exc}") from exc

    raise RuntimeError(f"Erro inesperado: {exc}") from exc
