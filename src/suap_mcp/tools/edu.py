import json
import logging
from typing import Literal

from mcp.server.fastmcp import FastMCP
from suap_api import SuapClient
from suap_api.exceptions import SuapError

from suap_mcp.errors import handle_suap_error
from suap_mcp.log import log_response, log_tool


def _json(value: object) -> str:
    """Serializa para JSON garantindo um único TextContent no protocolo MCP."""
    return json.dumps(value, ensure_ascii=False)

logger = logging.getLogger(__name__)


def register(mcp: FastMCP, client: SuapClient) -> None:
    """Registra as ferramentas do módulo edu no servidor MCP."""

    @mcp.tool()
    def get_periods() -> str:
        """Lista todos os semestres letivos disponíveis no SUAP."""
        with log_tool(logger, "get_periods"):
            try:
                periods = client.edu.get_periods()
                result = [p.raw for p in periods]
                logger.debug("  → %d período(s)", len(result))
                log_response(logger, result)
                return _json(result)
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_diaries(semestre: str) -> str:
        """Lista os diários de classe de um semestre letivo.

        Args:
            semestre: Semestre no formato "YYYY.N". Exemplos: "2024.1", "2024.2".
        """
        with log_tool(logger, "get_diaries", semestre=semestre):
            try:
                diaries = client.edu.get_diaries(semestre)
                result = [d.raw for d in diaries]
                logger.debug("  → %d diário(s)", len(result))
                log_response(logger, result)
                return _json(result)
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_diary_professors(id_diario: int) -> str:
        """Lista os professores vinculados a um diário de classe.

        Args:
            id_diario: ID numérico do diário (obtido via get_diaries).
        """
        with log_tool(logger, "get_diary_professors", id_diario=id_diario):
            try:
                professors = client.edu.get_diary_professors(id_diario)
                result = [p.raw for p in professors]
                logger.debug("  → %d professor(es)", len(result))
                log_response(logger, result)
                return _json(result)
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_diary_classes(id_diario: int) -> str:
        """Lista as aulas registradas em um diário, com data, conteúdo e faltas.

        Args:
            id_diario: ID numérico do diário (obtido via get_diaries).
        """
        with log_tool(logger, "get_diary_classes", id_diario=id_diario):
            try:
                classes = client.edu.get_diary_classes(id_diario)
                result = [c.raw for c in classes]
                logger.debug("  → %d aula(s)", len(result))
                log_response(logger, result)
                return _json(result)
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_diary_materials(id_diario: int) -> str:
        """Lista os materiais de aula disponíveis em um diário.

        Args:
            id_diario: ID numérico do diário (obtido via get_diaries).
        """
        with log_tool(logger, "get_diary_materials", id_diario=id_diario):
            try:
                materials = client.edu.get_diary_materials(id_diario)
                result = [m.raw for m in materials]
                logger.debug("  → %d material(is)", len(result))
                log_response(logger, result)
                return _json(result)
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_material(id_material: int) -> dict:
        """Retorna os detalhes de um material de aula específico.

        Args:
            id_material: ID numérico do material (obtido via get_diary_materials).
        """
        with log_tool(logger, "get_material", id_material=id_material):
            try:
                result = client.edu.get_material(id_material).raw
                logger.debug("  → dict(%d campos)", len(result))
                log_response(logger, result)
                return result
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_diary_assignments(id_diario: int) -> str:
        """Lista os trabalhos e avaliações de um diário, com título e data de entrega.

        Args:
            id_diario: ID numérico do diário (obtido via get_diaries).
        """
        with log_tool(logger, "get_diary_assignments", id_diario=id_diario):
            try:
                assignments = client.edu.get_diary_assignments(id_diario)
                result = [a.raw for a in assignments]
                logger.debug("  → %d trabalho(s)", len(result))
                log_response(logger, result)
                return _json(result)
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_disciplines(semestre: str) -> str:
        """Lista as disciplinas de um semestre com notas, frequência e situação.

        Args:
            semestre: Semestre no formato "YYYY.N". Exemplos: "2024.1", "2024.2".
        """
        with log_tool(logger, "get_disciplines", semestre=semestre):
            try:
                disciplines = client.edu.get_disciplines(semestre)
                result = [d.raw for d in disciplines]
                logger.debug("  → %d disciplina(s)", len(result))
                log_response(logger, result)
                return _json(result)
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_student_data() -> dict:
        """Retorna os dados acadêmicos do aluno autenticado.

        Inclui curso, IRA, período de referência, situação e informações de matrícula.
        """
        with log_tool(logger, "get_student_data"):
            try:
                result = client.edu.get_student_data().raw
                logger.debug("  → dict(%d campos)", len(result))
                log_response(logger, result)
                return result
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_graduation_requirements() -> dict:
        """Retorna os requisitos para conclusão do curso do aluno autenticado.

        Inclui carga horária total, carga horária cumprida e pendências.
        """
        with log_tool(logger, "get_graduation_requirements"):
            try:
                result = client.edu.get_graduation_requirements().raw
                logger.debug("  → dict(%d campos)", len(result))
                log_response(logger, result)
                return result
            except SuapError as exc:
                handle_suap_error(exc)

    @mcp.tool()
    def get_messages(
        status: Literal["nao_lidas", "lidas", "todas"] = "nao_lidas",
    ) -> str:
        """Lista as mensagens da caixa de entrada do usuário autenticado.

        Args:
            status: Filtro de leitura. "nao_lidas" (padrão), "lidas" ou "todas".
        """
        with log_tool(logger, "get_messages", status=status):
            try:
                messages = client.edu.get_messages(status)
                result = [m.raw for m in messages]
                logger.debug("  → %d mensagem(ns)", len(result))
                log_response(logger, result)
                return _json(result)
            except SuapError as exc:
                handle_suap_error(exc)
