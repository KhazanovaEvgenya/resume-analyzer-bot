from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        raise ValueError("Не удалось извлечь текст из PDF. Возможно, это скан без текстового слоя.")

    return full_text