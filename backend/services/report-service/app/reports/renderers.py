import csv
import html
import io
import os
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from app.reports.documents import ReportDocument, ReportSection
from app.reports.utils import format_value, json_bytes


class ReportRenderer(ABC):
    format: str
    media_type: str
    file_extension: str

    @abstractmethod
    def render(self, document: ReportDocument) -> bytes:
        raise NotImplementedError


class JsonReportRenderer(ReportRenderer):
    format = "json"
    media_type = "application/json"
    file_extension = "json"

    def render(self, document: ReportDocument) -> bytes:
        return json_bytes(document.to_dict())


class CsvReportRenderer(ReportRenderer):
    format = "csv"
    media_type = "text/csv; charset=utf-8"
    file_extension = "csv"

    def render(self, document: ReportDocument) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        for section_index, section in enumerate(document.to_sections()):
            if section_index:
                writer.writerow([])
            writer.writerow([section.title])
            self._write_section_rows(writer, section)

        return ("\ufeff" + buffer.getvalue()).encode("utf-8")

    def _write_section_rows(self, writer: csv.writer, section: ReportSection) -> None:
        if not section.rows:
            return

        headers = self._headers(section.rows)
        writer.writerow(headers)
        for row in section.rows:
            writer.writerow([format_value(row.get(header)) for header in headers])

    def _headers(self, rows: list[dict]) -> list[str]:
        headers: list[str] = []
        for row in rows:
            for key in row.keys():
                if key not in headers:
                    headers.append(key)
        return headers


class PdfReportRenderer(ReportRenderer):
    format = "pdf"
    media_type = "application/pdf"
    file_extension = "pdf"

    def render(self, document: ReportDocument) -> bytes:
        try:
            return self._reportlab_pdf(document)
        except ImportError:
            # Local developer environments may not have ReportLab installed yet.
            # The Docker image installs it and renders the full Russian PDF.
            return self._fallback_pdf(document)

    def _reportlab_pdf(self, document: ReportDocument) -> bytes:
        from reportlab.graphics.shapes import Drawing, Rect
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        font_name, bold_font_name = self._register_fonts(pdfmetrics, TTFont)
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title=self._localize_title(document.title),
            author="Мобильный обходчик",
        )

        base_styles = getSampleStyleSheet()
        styles = {
            "title": ParagraphStyle(
                "ObhodTitle",
                parent=base_styles["Title"],
                fontName=bold_font_name,
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#1f2937"),
                spaceAfter=6,
            ),
            "subtitle": ParagraphStyle(
                "ObhodSubtitle",
                parent=base_styles["Normal"],
                fontName=font_name,
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#6b7280"),
                spaceAfter=12,
            ),
            "section": ParagraphStyle(
                "ObhodSection",
                parent=base_styles["Heading2"],
                fontName=bold_font_name,
                fontSize=13,
                leading=16,
                textColor=colors.HexColor("#111827"),
                spaceBefore=12,
                spaceAfter=7,
            ),
            "cell": ParagraphStyle(
                "ObhodCell",
                parent=base_styles["Normal"],
                fontName=font_name,
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#111827"),
            ),
            "header": ParagraphStyle(
                "ObhodHeader",
                parent=base_styles["Normal"],
                fontName=bold_font_name,
                fontSize=8,
                leading=10,
                textColor=colors.white,
                alignment=TA_CENTER,
            ),
            "muted": ParagraphStyle(
                "ObhodMuted",
                parent=base_styles["Normal"],
                fontName=font_name,
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#6b7280"),
            ),
            "right": ParagraphStyle(
                "ObhodRight",
                parent=base_styles["Normal"],
                fontName=font_name,
                fontSize=8,
                leading=10,
                alignment=TA_RIGHT,
            ),
        }

        elements: list[Any] = []
        elements.append(Paragraph(self._localize_title(document.title), styles["title"]))
        generated_at = datetime.now().strftime("%d.%m.%Y %H:%M")
        elements.append(
            Paragraph(
                f"ID отчета: {self._escape(document.report_id)} · сформировано: {generated_at}",
                styles["subtitle"],
            )
        )

        sections = document.to_sections()
        if document.report_id == "analytics":
            self._append_analytics_document(elements, sections, styles, Drawing, Rect, colors)
        else:
            self._append_round_document(elements, sections, styles, Drawing, Rect, colors)

        pdf.build(
            elements,
            onFirstPage=lambda canvas, doc: self._draw_footer(canvas, doc, font_name),
            onLaterPages=lambda canvas, doc: self._draw_footer(canvas, doc, font_name),
        )
        return buffer.getvalue()

    def _append_round_document(
        self,
        elements: list[Any],
        sections: list[ReportSection],
        styles: dict[str, Any],
        drawing_cls: type,
        rect_cls: type,
        colors_module: Any,
    ) -> None:
        from reportlab.platypus import Paragraph, Spacer

        by_title = {section.title: section for section in sections}
        round_row = self._first_row(by_title.get("Round"))

        if round_row:
            elements.append(Paragraph("Сводка обхода", styles["section"]))
            elements.append(self._round_summary_table(round_row, styles, drawing_cls, rect_cls, colors_module))
            elements.append(Spacer(1, 5))
            elements.append(self._key_value_table(round_row, self._round_fields(), styles, colors_module))

        self._append_rows_table(
            elements,
            "Результаты чек-листа",
            by_title.get("Checklist results"),
            [
                ("question", "Пункт чек-листа"),
                ("equipment_name", "Оборудование"),
                ("result_code", "Результат"),
                ("status", "Статус"),
                ("comment", "Комментарий"),
            ],
            styles,
            colors_module,
        )
        self._append_rows_table(
            elements,
            "Показания оборудования",
            by_title.get("Equipment readings"),
            [
                ("equipment_name", "Оборудование"),
                ("parameter_name", "Параметр"),
                ("value", "Значение"),
                ("source", "Источник"),
                ("within_limits", "В норме"),
                ("reading_ts", "Время"),
            ],
            styles,
            colors_module,
            row_mapper=self._reading_row,
        )
        self._append_rows_table(
            elements,
            "Выявленные дефекты",
            by_title.get("Defects"),
            [
                ("title", "Дефект"),
                ("equipment_name", "Оборудование"),
                ("severity", "Критичность"),
                ("status", "Статус"),
                ("detected_at", "Время"),
                ("description", "Описание"),
            ],
            styles,
            colors_module,
        )
        self._append_rows_table(
            elements,
            "Фото и вложения",
            by_title.get("Attachments"),
            [
                ("file_name", "Файл"),
                ("mime_type", "Тип"),
                ("size_bytes", "Размер"),
                ("entity_type", "Привязка"),
                ("download_url", "Ссылка"),
            ],
            styles,
            colors_module,
        )

    def _append_analytics_document(
        self,
        elements: list[Any],
        sections: list[ReportSection],
        styles: dict[str, Any],
        drawing_cls: type,
        rect_cls: type,
        colors_module: Any,
    ) -> None:
        from reportlab.platypus import PageBreak, Paragraph, Spacer

        by_title = {section.title: section for section in sections}
        summary_row = self._first_row(by_title.get("Summary"))

        if summary_row:
            elements.append(Paragraph("Общая сводка", styles["section"]))
            elements.append(self._analytics_summary_table(summary_row, styles, drawing_cls, rect_cls, colors_module))
            elements.append(Spacer(1, 5))
            elements.append(self._key_value_table(summary_row, self._summary_fields(), styles, colors_module))

        self._append_rows_table(
            elements,
            "Аналитика по оборудованию",
            by_title.get("Equipment analytics"),
            [
                ("equipment_name", "Оборудование"),
                ("location", "Локация"),
                ("defects_count", "Дефекты"),
                ("warning_count", "Предупр."),
                ("critical_count", "Критич."),
                ("risk_bar", "Индекс риска"),
                ("last_reading_at", "Последнее показание"),
            ],
            styles,
            colors_module,
            row_mapper=lambda row: self._risk_row(row, drawing_cls, rect_cls, colors_module),
        )
        elements.append(PageBreak())
        self._append_rows_table(
            elements,
            "Аналитика по работникам",
            by_title.get("Employee analytics"),
            [
                ("employee_name", "Работник"),
                ("rounds_total", "Всего"),
                ("rounds_completed", "Завершено"),
                ("confirmed_steps_count", "Точки"),
                ("avg_duration_min", "Среднее время, мин"),
                ("warning_count", "Предупр."),
                ("critical_count", "Критич."),
            ],
            styles,
            colors_module,
        )

    def _round_summary_table(
        self,
        row: dict[str, Any],
        styles: dict[str, Any],
        drawing_cls: type,
        rect_cls: type,
        colors_module: Any,
    ) -> Any:
        completion = int(row.get("completion_pct") or 0)
        data = [
            [
                self._metric_card("Статус", self._localized_value("status", row.get("status")), styles),
                self._metric_card("Выполнение", f"{completion}%", styles),
                self._metric_card("Предупреждения", row.get("warning_count", 0), styles),
                self._metric_card("Критические", row.get("critical_count", 0), styles),
            ],
            [
                "",
                self._progress_bar(completion, drawing_cls, rect_cls, colors_module),
                "",
                "",
            ],
        ]
        return self._cards_table(data, colors_module)

    def _analytics_summary_table(
        self,
        row: dict[str, Any],
        styles: dict[str, Any],
        drawing_cls: type,
        rect_cls: type,
        colors_module: Any,
    ) -> Any:
        completion = int(float(row.get("avg_completion_pct") or 0))
        data = [
            [
                self._metric_card("Обходов всего", row.get("rounds_total", 0), styles),
                self._metric_card("Завершено", row.get("rounds_completed", 0), styles),
                self._metric_card("Открытых дефектов", row.get("defects_open", 0), styles),
                self._metric_card("Критические", row.get("critical_count", 0), styles),
            ],
            [
                self._metric_card("Среднее выполнение", f"{completion}%", styles),
                self._progress_bar(completion, drawing_cls, rect_cls, colors_module),
                "",
                "",
            ],
        ]
        return self._cards_table(data, colors_module)

    def _append_rows_table(
        self,
        elements: list[Any],
        title: str,
        section: ReportSection | None,
        columns: list[tuple[str, str]],
        styles: dict[str, Any],
        colors_module: Any,
        row_mapper: Any | None = None,
    ) -> None:
        from reportlab.platypus import Paragraph

        elements.append(Paragraph(title, styles["section"]))
        if section is None or not section.rows:
            elements.append(Paragraph("Нет данных", styles["muted"]))
            return

        rows = [row_mapper(row) if row_mapper else row for row in section.rows]
        header = [Paragraph(label, styles["header"]) for _, label in columns]
        table_rows = [header]
        for row in rows:
            table_rows.append(
                [
                    self._cell(row.get(key), styles["cell"], key=key)
                    for key, _ in columns
                ]
            )

        table = self._make_table(table_rows, colors_module, repeat_rows=1)
        elements.append(table)

    def _key_value_table(
        self,
        row: dict[str, Any],
        fields: list[tuple[str, str]],
        styles: dict[str, Any],
        colors_module: Any,
    ) -> Any:
        from reportlab.platypus import Paragraph, Table, TableStyle

        data = []
        for key, label in fields:
            data.append(
                [
                    Paragraph(label, styles["header"]),
                    self._cell(self._localized_value(key, row.get(key)), styles["cell"], key=key),
                ]
            )
        table = Table(data, colWidths=[54 * 2.83465, 126 * 2.83465])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors_module.HexColor("#2563eb")),
                    ("BACKGROUND", (1, 0), (1, -1), colors_module.HexColor("#f8fafc")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors_module.HexColor("#d1d5db")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        return table

    def _make_table(self, rows: list[list[Any]], colors_module: Any, repeat_rows: int = 0) -> Any:
        from reportlab.platypus import Table, TableStyle

        table = Table(rows, repeatRows=repeat_rows, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors_module.HexColor("#2563eb")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors_module.white, colors_module.HexColor("#f8fafc")]),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors_module.HexColor("#d1d5db")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def _cards_table(self, data: list[list[Any]], colors_module: Any) -> Any:
        from reportlab.platypus import Table, TableStyle

        table = Table(data, colWidths=[45 * 2.83465, 45 * 2.83465, 45 * 2.83465, 45 * 2.83465])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors_module.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.35, colors_module.HexColor("#d1d5db")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors_module.HexColor("#e5e7eb")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("SPAN", (1, 1), (1, 1)),
                ]
            )
        )
        return table

    def _metric_card(self, label: str, value: Any, styles: dict[str, Any]) -> Any:
        from reportlab.platypus import Paragraph

        return Paragraph(
            f'<font size="7" color="#6b7280">{self._escape(label)}</font><br/>'
            f'<font size="14"><b>{self._escape(format_value(value))}</b></font>',
            styles["cell"],
        )

    def _progress_bar(
        self,
        value: int | float,
        drawing_cls: type,
        rect_cls: type,
        colors_module: Any,
        width: int = 110,
        height: int = 10,
    ) -> Any:
        value = max(0, min(100, float(value or 0)))
        drawing = drawing_cls(width, height)
        drawing.add(rect_cls(0, 1, width, height - 2, fillColor=colors_module.HexColor("#e5e7eb"), strokeColor=None))
        color = "#16a34a" if value >= 90 else "#f59e0b" if value >= 60 else "#dc2626"
        drawing.add(
            rect_cls(0, 1, width * value / 100, height - 2, fillColor=colors_module.HexColor(color), strokeColor=None)
        )
        return drawing

    def _risk_row(
        self,
        row: dict[str, Any],
        drawing_cls: type,
        rect_cls: type,
        colors_module: Any,
    ) -> dict[str, Any]:
        mapped = dict(row)
        score = (
            int(row.get("defects_count") or 0) * 15
            + int(row.get("warning_count") or 0) * 20
            + int(row.get("critical_count") or 0) * 35
        )
        mapped["risk_bar"] = self._progress_bar(min(100, score), drawing_cls, rect_cls, colors_module, width=72, height=9)
        return mapped

    def _reading_row(self, row: dict[str, Any]) -> dict[str, Any]:
        mapped = dict(row)
        value = row.get("value_text")
        if value in (None, ""):
            value = row.get("value_num")
        unit = row.get("unit")
        mapped["value"] = f"{format_value(value)} {unit}".strip() if unit else format_value(value)
        return mapped

    def _cell(self, value: Any, style: Any, key: str | None = None) -> Any:
        from reportlab.platypus import Paragraph

        if hasattr(value, "draw"):
            return value
        return Paragraph(self._escape(self._localized_value(key, value)), style)

    def _localized_value(self, key: str | None, value: Any) -> Any:
        if key in {"status", "result_code", "severity", "source", "within_limits"}:
            return self._translate_value(value)
        return value

    def _translate_value(self, value: Any) -> str:
        if value is True:
            return "да"
        if value is False:
            return "нет"
        translations = {
            "planned": "запланирован",
            "in_progress": "в работе",
            "completed": "завершен",
            "cancelled": "отменен",
            "draft": "черновик",
            "ok": "норма",
            "warning": "предупреждение",
            "critical": "критическое отклонение",
            "low": "низкая",
            "medium": "средняя",
            "high": "высокая",
            "open": "открыт",
            "closed": "закрыт",
            "mobile": "мобильное приложение",
            "sensor": "датчик",
            "manual": "ручной ввод",
        }
        return translations.get(str(value), format_value(value))

    def _round_fields(self) -> list[tuple[str, str]]:
        return [
            ("id", "ID обхода"),
            ("route_name", "Маршрут"),
            ("employee_name", "Работник"),
            ("planned_start", "Плановое начало"),
            ("planned_end", "Плановое завершение"),
            ("actual_start", "Фактическое начало"),
            ("actual_end", "Фактическое завершение"),
            ("confirmed_steps_count", "Подтверждено точек"),
            ("mandatory_steps_total", "Обязательных точек"),
            ("completed_items_count", "Заполнено пунктов"),
            ("required_items_total", "Обязательных пунктов"),
            ("defects_count", "Дефектов"),
        ]

    def _summary_fields(self) -> list[tuple[str, str]]:
        return [
            ("rounds_total", "Всего обходов"),
            ("rounds_planned", "Запланировано"),
            ("rounds_in_progress", "В работе"),
            ("rounds_completed", "Завершено"),
            ("defects_open", "Открытых дефектов"),
            ("warning_count", "Предупреждений"),
            ("critical_count", "Критических отклонений"),
            ("avg_completion_pct", "Среднее выполнение, %"),
        ]

    def _first_row(self, section: ReportSection | None) -> dict[str, Any]:
        if section is None or not section.rows:
            return {}
        return section.rows[0]

    def _localize_title(self, title: str) -> str:
        titles = {
            "Obhod round report": "Отчет по обходу оборудования",
            "Obhod analytics report": "Аналитический отчет по обходам",
        }
        return titles.get(title, title)

    def _register_fonts(self, pdfmetrics: Any, ttfont_cls: type) -> tuple[str, str]:
        regular_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/local/share/fonts/DejaVuSans.ttf",
        ]
        bold_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
        ]
        regular_path = next((path for path in regular_paths if os.path.exists(path)), None)
        bold_path = next((path for path in bold_paths if os.path.exists(path)), None)
        if regular_path is None or bold_path is None:
            return "Helvetica", "Helvetica-Bold"

        if "DejaVuSans" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(ttfont_cls("DejaVuSans", regular_path))
        if "DejaVuSans-Bold" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(ttfont_cls("DejaVuSans-Bold", bold_path))
        return "DejaVuSans", "DejaVuSans-Bold"

    def _draw_footer(self, canvas: Any, doc: Any, font_name: str) -> None:
        canvas.saveState()
        canvas.setFont(font_name, 7)
        canvas.setFillColorRGB(0.42, 0.45, 0.5)
        canvas.drawString(doc.leftMargin, 9 * 2.83465, "АИС «Мобильный обходчик»")
        canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 9 * 2.83465, f"стр. {doc.page}")
        canvas.restoreState()

    def _escape(self, value: Any) -> str:
        return html.escape(format_value(value), quote=False).replace("\n", "<br/>")

    def _fallback_pdf(self, document: ReportDocument) -> bytes:
        lines = self._document_lines(document)
        return self._simple_pdf(lines)

    def _document_lines(self, document: ReportDocument) -> list[str]:
        lines = [document.title, f"Report ID: {document.report_id}", ""]
        for section in document.to_sections():
            lines.append(section.title)
            if not section.rows:
                lines.append("- no data")
                lines.append("")
                continue
            for row in section.rows:
                lines.append("- item")
                for key, value in row.items():
                    lines.append(f"  {key}: {format_value(value)}")
            lines.append("")
        return lines

    def _simple_pdf(self, lines: list[str]) -> bytes:
        page_width = 595
        page_height = 842
        left = 42
        top = 800
        font_size = 10
        line_height = 14
        max_chars = 92
        max_lines_per_page = 52

        wrapped_lines: list[str] = []
        for line in lines:
            ascii_line = self._to_pdf_text(line)
            if not ascii_line:
                wrapped_lines.append("")
                continue
            wrapped_lines.extend(textwrap.wrap(ascii_line, width=max_chars) or [""])

        pages = [
            wrapped_lines[index : index + max_lines_per_page]
            for index in range(0, len(wrapped_lines), max_lines_per_page)
        ] or [[]]

        objects: list[bytes] = []

        def add_object(payload: bytes) -> int:
            objects.append(payload)
            return len(objects)

        catalog_id = add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
        pages_id = add_object(b"")
        font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        page_ids: list[int] = []

        for page_lines in pages:
            commands = ["BT", f"/F1 {font_size} Tf", f"{left} {top} Td"]
            first_line = True
            for line in page_lines:
                if first_line:
                    first_line = False
                else:
                    commands.append(f"0 -{line_height} Td")
                commands.append(f"({self._escape_pdf_text(line)}) Tj")
            commands.append("ET")
            content = "\n".join(commands).encode("ascii")
            content_id = add_object(
                b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream"
            )
            page_id = add_object(
                (
                    f"<< /Type /Page /Parent {pages_id} 0 R "
                    f"/MediaBox [0 0 {page_width} {page_height}] "
                    f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
                    f"/Contents {content_id} 0 R >>"
                ).encode("ascii")
            )
            page_ids.append(page_id)

        kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
        objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")
        objects[catalog_id - 1] = b"<< /Type /Catalog /Pages 2 0 R >>"

        buffer = io.BytesIO()
        buffer.write(b"%PDF-1.4\n")
        offsets = [0]
        for object_id, payload in enumerate(objects, start=1):
            offsets.append(buffer.tell())
            buffer.write(f"{object_id} 0 obj\n".encode("ascii"))
            buffer.write(payload)
            buffer.write(b"\nendobj\n")

        xref_offset = buffer.tell()
        buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        buffer.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
        buffer.write(
            (
                "trailer\n"
                f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                "startxref\n"
                f"{xref_offset}\n"
                "%%EOF\n"
            ).encode("ascii")
        )
        return buffer.getvalue()

    def _to_pdf_text(self, value: str) -> str:
        translit = {
            "А": "A",
            "Б": "B",
            "В": "V",
            "Г": "G",
            "Д": "D",
            "Е": "E",
            "Ё": "E",
            "Ж": "Zh",
            "З": "Z",
            "И": "I",
            "Й": "Y",
            "К": "K",
            "Л": "L",
            "М": "M",
            "Н": "N",
            "О": "O",
            "П": "P",
            "Р": "R",
            "С": "S",
            "Т": "T",
            "У": "U",
            "Ф": "F",
            "Х": "Kh",
            "Ц": "Ts",
            "Ч": "Ch",
            "Ш": "Sh",
            "Щ": "Sch",
            "Ъ": "",
            "Ы": "Y",
            "Ь": "",
            "Э": "E",
            "Ю": "Yu",
            "Я": "Ya",
            "а": "a",
            "б": "b",
            "в": "v",
            "г": "g",
            "д": "d",
            "е": "e",
            "ё": "e",
            "ж": "zh",
            "з": "z",
            "и": "i",
            "й": "y",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "o",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "kh",
            "ц": "ts",
            "ч": "ch",
            "ш": "sh",
            "щ": "sch",
            "ъ": "",
            "ы": "y",
            "ь": "",
            "э": "e",
            "ю": "yu",
            "я": "ya",
            "№": "No",
            "—": "-",
            "–": "-",
            "«": '"',
            "»": '"',
        }
        text = "".join(translit.get(char, char) for char in value)
        return text.encode("latin-1", errors="replace").decode("latin-1")

    def _escape_pdf_text(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
