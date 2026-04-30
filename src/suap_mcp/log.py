import json
import logging
import os
import sys
import time
from contextlib import contextmanager
from typing import Any, Generator


def setup_logging() -> None:
    """Configura logging controlado pela variável SUAP_MCP_LOG.

    Valores aceitos:
      DEBUG, 1, true, yes  → nível DEBUG (verboso)
      INFO                 → nível INFO
      WARNING              → nível WARNING
      ERROR                → nível ERROR
      ausente / 0 / false  → WARNING (silencioso, padrão)

    Logs são sempre escritos em stderr — stdout é reservado para o protocolo MCP.
    """
    raw = os.getenv("SUAP_MCP_LOG", "").strip().upper()

    level_map: dict[str, int] = {
        "1": logging.DEBUG,
        "TRUE": logging.DEBUG,
        "YES": logging.DEBUG,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    level = level_map.get(raw, logging.WARNING)

    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        force=True,
    )

    if level <= logging.DEBUG:
        logging.getLogger("suap_mcp").debug(
            "Logging ativo — nível %s", logging.getLevelName(level)
        )


@contextmanager
def log_tool(logger: logging.Logger, name: str, **kwargs) -> Generator[None, None, None]:
    """Loga entrada, erros e tempo de execução de uma ferramenta MCP.

    Uso:
        with log_tool(logger, "get_periods"):
            ...
            logger.debug("  → %d item(s)", len(result))

    Só produz saída se o nível DEBUG estiver ativo, sem custo em produção.
    """
    if not logger.isEnabledFor(logging.DEBUG):
        yield
        return

    args_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items()) if kwargs else ""
    logger.debug("[▶] %s(%s)", name, args_str)
    start = time.monotonic()
    try:
        yield
    except Exception as exc:
        elapsed = time.monotonic() - start
        logger.debug("[✗] %s → %s: %s (%.3fs)", name, type(exc).__name__, exc, elapsed)
        raise
    else:
        logger.debug("[✓] %s concluído (%.3fs)", name, time.monotonic() - start)


_MAX_PAYLOAD_BYTES = 4000


def log_response(logger: logging.Logger, result: Any) -> None:
    """Loga o payload exato que a ferramenta devolve ao FastMCP (antes da serialização MCP).

    Trunca em 4 KB para não poluir o log com respostas gigantes.
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return
    try:
        text = json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        text = repr(result)
    size = len(text.encode())
    if size > _MAX_PAYLOAD_BYTES:
        preview = text[:_MAX_PAYLOAD_BYTES] + "\n  ...[truncado]"
    else:
        preview = text
    logger.debug("  ↩ payload (%d bytes):\n%s", size, preview)
