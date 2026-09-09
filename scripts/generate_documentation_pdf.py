#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate the navigable PDF handbook from the executable payment catalog."""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from generate_case_guides import CASE_SCENARIOS  # noqa: E402
from pypdf import PdfReader, PdfWriter  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from payments_lab.catalog import enriched_catalog  # noqa: E402

OUTPUT = ROOT / "output" / "pdf" / "universal-payments-engineering-lab.pdf"
GITHUB = "https://github.com/vladimiracunadev-create/universal-payments-engineering-lab"
PAGES = "https://vladimiracunadev-create.github.io/universal-payments-engineering-lab"
INK = colors.HexColor("#10231e")
MUTED = colors.HexColor("#52665f")
ACCENT = colors.HexColor("#087f5b")
MINT = colors.HexColor("#dff7ef")
PANEL = colors.HexColor("#f3f8f6")
LINE = colors.HexColor("#b7d1c8")


def clean(value: object) -> str:
    return html.escape(str(value).replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-").strip())


class Handbook(BaseDocTemplate):
    def __init__(self, filename: str) -> None:
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title="Universal Payments Engineering Lab - Manual navegable",
            author="Universal Payments Engineering Lab",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="content")
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self.decorate))

    def decorate(self, canvas, doc) -> None:
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, A4[1] - 13 * mm, A4[0] - 18 * mm, A4[1] - 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, A4[1] - 10 * mm, "Universal Payments Engineering Lab")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Página {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable) -> None:
        bookmark = getattr(flowable, "bookmark_name", None)
        outline = getattr(flowable, "outline_title", None)
        if bookmark:
            self.canv.bookmarkPage(bookmark)
        if bookmark and outline:
            self.canv.addOutlineEntry(outline, bookmark, level=getattr(flowable, "outline_level", 0))


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=29, leading=33, textColor=INK, alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverLead", parent=styles["BodyText"], fontSize=13, leading=19, textColor=MUTED, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="CaseTitle", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=INK, spaceAfter=10))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=ACCENT, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=INK, spaceAfter=4))
styles.add(ParagraphStyle(name="Tiny", parent=styles["BodyText"], fontSize=7.2, leading=9.4, textColor=INK))
styles.add(ParagraphStyle(name="IndexLink", parent=styles["BodyText"], fontSize=9, leading=12, textColor=ACCENT, spaceAfter=3))


def anchored(text: str, style: str, bookmark: str, level: int = 0) -> Paragraph:
    paragraph = Paragraph(clean(text), styles[style])
    paragraph.bookmark_name = bookmark
    paragraph.outline_title = text
    paragraph.outline_level = level
    return paragraph


def section(text: str) -> Paragraph:
    return Paragraph(clean(text), styles["Section"])


def body(text: object, *, style: str = "BodySmall") -> Paragraph:
    return Paragraph(clean(text), styles[style])


def rich(text: str, *, style: str = "BodySmall") -> Paragraph:
    return Paragraph(text, styles[style])


def bullets(items: list[object]) -> list[Paragraph]:
    return [Paragraph(f"- {clean(item)}", styles["BodySmall"]) for item in items]


def styled_table(rows: list[list[object]], widths: list[float], *, header: bool = True) -> Table:
    converted = [[item if hasattr(item, "wrap") else body(item, style="Tiny") for item in row] for row in rows]
    table = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT if header else PANEL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white if header else INK),
    ]
    table.setStyle(TableStyle(commands))
    return table


def flow_diagram(number: int, journey: dict[str, str]) -> list[object]:
    width = 112
    rows = [[
        rich(f"<b>1. Inicio</b><br/>{clean(journey['start'])}", style="Tiny"),
        rich("-&gt;", style="Tiny"),
        rich(f"<b>2. Proceso</b><br/>{clean(journey['process'])}", style="Tiny"),
        rich("-&gt;", style="Tiny"),
        rich(f"<b>3. Confirmar</b><br/>{clean(journey['confirm'])}", style="Tiny"),
        rich("-&gt;", style="Tiny"),
        rich(f"<b>4. Cerrar</b><br/>{clean(journey['close'])}", style="Tiny"),
    ]]
    table = Table(rows, colWidths=[width, 16, width, 16, width, 16, width], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("ALIGN", (3, 0), (3, 0), "CENTER"),
        ("ALIGN", (5, 0), (5, 0), "CENTER"),
        ("BOX", (0, 0), (0, 0), 1, ACCENT),
        ("BOX", (2, 0), (2, 0), 1, ACCENT),
        ("BOX", (4, 0), (4, 0), 1, ACCENT),
        ("BOX", (6, 0), (6, 0), 1, ACCENT),
        ("BACKGROUND", (0, 0), (0, 0), PANEL),
        ("BACKGROUND", (2, 0), (2, 0), PANEL),
        ("BACKGROUND", (4, 0), (4, 0), MINT),
        ("BACKGROUND", (6, 0), (6, 0), PANEL),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    recovery = Table(
        [[rich("<b>Ruta de fallo:</b> sin respuesta -&gt; UNKNOWN -&gt; consultar la misma referencia -&gt; confirmar sin duplicar", style="Tiny")]],
        colWidths=[496],
    )
    recovery.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#d28b26")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff5df")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [Paragraph(f"Figura {number}. Flujo verificable del caso", styles["Section"]), table, Spacer(1, 4), recovery]


def build_story() -> list[object]:
    families = enriched_catalog()
    story: list[object] = [
        Spacer(1, 36 * mm),
        anchored("Universal Payments Engineering Lab", "CoverTitle", "cover"),
        Paragraph("Manual navegable de 28 modalidades de pago", styles["CoverLead"]),
        Paragraph("Desde el inicio de una orden hasta confirmación, ledger, fallos, seguridad y conciliación.", styles["CoverLead"]),
        Spacer(1, 8 * mm),
        styled_table(
            [
                ["Markdown", "Fuente única revisable en GitHub"],
                ["HTML", "Sitio generado para navegar y visualizar Mermaid"],
                ["PDF", "Manual descargable con índice y enlaces internos"],
            ],
            [85, 411],
            header=False,
        ),
        Spacer(1, 12 * mm),
        Paragraph(f'<link href="{PAGES}/FORMATS_AND_TRACEABILITY.html">Abrir explicación de formatos en GitHub Pages</link>', styles["IndexLink"]),
        PageBreak(),
        anchored("Índice de casos", "CaseTitle", "contents"),
        body("Selecciona un caso. El enlace salta dentro de este PDF; no abre otra aplicación."),
    ]
    index_cells = []
    for number, family in enumerate(families, 1):
        rail_id = clean(family["id"])
        title = clean(family["title"])
        index_cells.append(Paragraph(f'<link href="#case-{rail_id}">{number:02d}. {title}</link>', styles["IndexLink"]))
    story.append(Table([index_cells[i : i + 2] for i in range(0, len(index_cells), 2)], colWidths=[248, 248]))
    story.extend([
        Spacer(1, 8 * mm),
        section("Cómo leer cada caso"),
        body("Cada capítulo conserva el mismo orden: necesidad, ejemplo, recorrido, fallo, implementación, configuración, seguridad, pruebas y checklist LIVE. El diagrama aparece en todos los casos y no depende de Mermaid ni de conexión a Internet."),
    ])

    for number, family in enumerate(families, 1):
        guide = family["playbook"]
        journey = guide["journey"]
        teaching = guide["teaching"]
        configuration = guide["configuration"]
        rail_id = str(family["id"])
        title = str(family["title"])
        story.extend([
            CondPageBreak(120 * mm),
            anchored(f"{number:02d}. {title}", "CaseTitle", f"case-{rail_id}"),
            Paragraph(
                f'<link href="#contents">Volver al índice</link> | '
                f'<link href="{GITHUB}/blob/main/docs/payment-methods/cases/{rail_id}.md">Fuente Markdown</link> | '
                f'<link href="{PAGES}/payment-methods/cases/{rail_id}.html">HTML público</link>',
                styles["IndexLink"],
            ),
            section("En una frase"),
            rich(f"<b>Sirve para:</b> {clean(journey['when'])}"),
            rich(f"<b>Modelo mental:</b> {clean(teaching['mental_model'])}"),
            section("Ejemplo concreto"),
            styled_table(
                [
                    ["Situación", "Detrás de la pantalla", "Se acepta como pagado cuando"],
                    [
                        CASE_SCENARIOS[rail_id],
                        f"{journey['start']} {journey['process']}",
                        f"{journey['confirm']} Después: {journey['close']}",
                    ],
                ],
                [165, 165, 166],
            ),
            Spacer(1, 6),
            *flow_diagram(number, journey),
            section("Recorrido de comienzo a fin"),
            styled_table(
                [
                    ["Etapa", "Qué ocurre", "Pregunta de control"],
                    ["1. Inicio", journey["start"], "¿Hay referencia, monto, moneda y expiración?"],
                    ["2. Proceso", journey["process"], "¿Qué sistema puede producir el efecto financiero?"],
                    ["3. Confirmación", journey["confirm"], "¿La evidencia viene de una fuente autoritativa?"],
                    ["4. Cierre", journey["close"], "¿Ledger, proveedor y banco explican el resultado?"],
                ],
                [65, 245, 186],
            ),
            section("Qué ocurre si falla"),
            rich(f"<b>Fallo característico:</b> {clean(journey['failure'])}"),
            body("Un timeout no equivale a rechazo. Conserva UNKNOWN, consulta con la misma referencia y no generes un segundo efecto a ciegas."),
            section("Cómo llevarlo a una aplicación real"),
            *bullets(teaching["development_path"]),
            rich(f"<b>Evidencia de éxito:</b> {clean(teaching['success_evidence'])}"),
            rich(f"<b>Construcción concreta:</b> {clean(journey['real'])}"),
            styled_table(
                [
                    ["Capa", "Tecnología / responsabilidad"],
                    ["Frontend", guide["stack"]["frontend"]],
                    ["Backend", guide["stack"]["backend"]],
                    ["API", guide["stack"]["api"]],
                    ["Datos", guide["stack"]["storage"]],
                    ["Operación", guide["stack"]["operations"]],
                ],
                [90, 406],
            ),
            section("Alta, costo y decisión"),
            rich(f"<b>Dónde comenzar:</b> {clean(guide['access'])}"),
            rich(f"<b>Costo:</b> {clean(guide['pricing'])}"),
            rich(f"<b>Decisión:</b> {clean(guide['decision'])}"),
            section("Variables y callbacks"),
        ])
        variables = [*configuration["global_variables"], *configuration["provider_variables"]]
        variable_rows = [["Variable", "Req.", "Secreta", "Propósito"]]
        variable_rows.extend([
            [item["name"], "Sí" if item["required"] else "No", "Sí" if item["sensitive"] else "No", item["purpose"]]
            for item in variables
        ])
        story.append(styled_table(variable_rows, [135, 35, 45, 281]))
        story.extend([rich(f"<b>Callbacks:</b> {clean('; '.join(configuration['callbacks']) or 'No aplica hasta elegir proveedor.')}")])
        story.extend([section("Seguridad"), *bullets(guide["security"])])
        story.extend([section("Pruebas mínimas"), *bullets(guide["testing"])])
        story.extend([section("Checklist antes de LIVE"), *bullets(guide["go_live"])])
        story.append(section("Fuentes"))
        for source in guide["sources"]:
            story.append(Paragraph(f'- <link href="{html.escape(source["url"], quote=True)}">{clean(source["title"])}</link>', styles["BodySmall"]))
    return story


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Handbook(str(OUTPUT)).build(build_story())
    reader = PdfReader(OUTPUT)
    pages_by_title = {
        str(destination.title): reader.get_destination_page_number(destination)
        for destination in reader.outline
        if hasattr(destination, "title")
    }
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.add_named_destination("contents", pages_by_title["Índice de casos"])
    for number, family in enumerate(enriched_catalog(), 1):
        title = f"{number:02d}. {family['title']}"
        writer.add_named_destination(f"case-{family['id']}", pages_by_title[title])
    temporary = OUTPUT.with_suffix(".tmp.pdf")
    with temporary.open("wb") as stream:
        writer.write(stream)
    temporary.replace(OUTPUT)
    print(f"Generated {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
