import csv
import io
import textwrap
from abc import ABC, abstractmethod

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
