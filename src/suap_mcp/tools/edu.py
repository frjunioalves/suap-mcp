import dataclasses
import logging
from typing import Literal

from mcp.server.fastmcp import FastMCP
from suap_api import SuapClient
from suap_api.exceptions import SuapError

from suap_mcp.errors import handle_suap_error

logger = logging.getLogger(__name__)


def register(mcp: FastMCP, client: SuapClient) -> None:
    """Registra as ferramentas do módulo edu no servidor MCP."""

    @mcp.tool()
    def get_periods() -> list[dict]:
        """Lista todos os semestres letivos disponíveis no SUAP."""
        try:
            periods = client.edu.get_periods()
            return [dataclasses.asdict(p) for p in periods]
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_diaries(semestre: str) -> list[dict]:
        """Lista os diários de classe de um semestre letivo.

        Args:
            semestre: Semestre no formato "YYYY.N". Exemplos: "2024.1", "2024.2".
        """
        try:
            diaries = client.edu.get_diaries(semestre)
            return [dataclasses.asdict(d) for d in diaries]
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_diary_professors(id_diario: int) -> list[dict]:
        """Lista os professores vinculados a um diário de classe.

        Args:
            id_diario: ID numérico do diário (obtido via get_diaries).
        """
        try:
            professors = client.edu.get_diary_professors(id_diario)
            return [dataclasses.asdict(p) for p in professors]
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_diary_classes(id_diario: int) -> list[dict]:
        """Lista as aulas registradas em um diário, com data, conteúdo e faltas.

        Args:
            id_diario: ID numérico do diário (obtido via get_diaries).
        """
        try:
            classes = client.edu.get_diary_classes(id_diario)
            return [dataclasses.asdict(c) for c in classes]
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_diary_materials(id_diario: int) -> list[dict]:
        """Lista os materiais de aula disponíveis em um diário.

        Args:
            id_diario: ID numérico do diário (obtido via get_diaries).
        """
        try:
            materials = client.edu.get_diary_materials(id_diario)
            return [dataclasses.asdict(m) for m in materials]
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_material(id_material: int) -> dict:
        """Retorna os detalhes de um material de aula específico.

        Args:
            id_material: ID numérico do material (obtido via get_diary_materials).
        """
        try:
            material = client.edu.get_material(id_material)
            return dataclasses.asdict(material)
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_diary_assignments(id_diario: int) -> list[dict]:
        """Lista os trabalhos e avaliações de um diário, com título e data de entrega.

        Args:
            id_diario: ID numérico do diário (obtido via get_diaries).
        """
        try:
            assignments = client.edu.get_diary_assignments(id_diario)
            return [dataclasses.asdict(a) for a in assignments]
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_disciplines(semestre: str) -> list[dict]:
        """Lista as disciplinas de um semestre com notas, frequência e situação.

        Args:
            semestre: Semestre no formato "YYYY.N". Exemplos: "2024.1", "2024.2".
        """
        try:
            disciplines = client.edu.get_disciplines(semestre)
            return [dataclasses.asdict(d) for d in disciplines]
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_student_data() -> dict:
        """Retorna os dados acadêmicos do aluno autenticado.

        Inclui curso, IRA, período de referência, situação e informações de matrícula.
        """
        try:
            data = client.edu.get_student_data()
            return dataclasses.asdict(data)
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_graduation_requirements() -> dict:
        """Retorna os requisitos para conclusão do curso do aluno autenticado.

        Inclui carga horária total, carga horária cumprida e pendências.
        """
        try:
            requirements = client.edu.get_graduation_requirements()
            return dataclasses.asdict(requirements)
        except SuapError as exc:
            handle_suap_error(exc)

    @mcp.tool()
    def get_messages(
        status: Literal["nao_lidas", "lidas", "todas"] = "nao_lidas",
    ) -> list[dict]:
        """Lista as mensagens da caixa de entrada do usuário autenticado.

        Args:
            status: Filtro de leitura. "nao_lidas" (padrão), "lidas" ou "todas".
        """
        try:
            messages = client.edu.get_messages(status)
            return [dataclasses.asdict(m) for m in messages]
        except SuapError as exc:
            handle_suap_error(exc)
