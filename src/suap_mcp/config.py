import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    base_url: str
    token: str


def load_config() -> Config:
    """Lê e valida as variáveis de ambiente obrigatórias.

    Falha imediatamente (fail-fast) se qualquer variável estiver ausente,
    evitando erros opacos em runtime durante chamadas de ferramentas.
    """
    load_dotenv()

    base_url = os.getenv("SUAP_BASE_URL", "").strip()
    token = os.getenv("SUAP_TOKEN", "").strip()

    missing = [name for name, val in [("SUAP_BASE_URL", base_url), ("SUAP_TOKEN", token)] if not val]
    if missing:
        raise RuntimeError(
            f"Variáveis de ambiente obrigatórias não definidas: {', '.join(missing)}. "
            "Copie .env.example para .env e preencha os valores."
        )

    return Config(base_url=base_url, token=token)
