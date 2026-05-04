import requests
from bs4 import BeautifulSoup


def get_vacancy_text(user_text: str) -> str:
    """
    Если пользователь прислал ссылку на hh.ru — пробуем достать текст вакансии.
    Если это не ссылка — считаем, что пользователь прислал текст вакансии.
    """

    user_text = user_text.strip()

    if "hh.ru" not in user_text:
        return user_text

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(user_text, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("h1")
        title_text = title.get_text(" ", strip=True) if title else ""

        vacancy_body = soup.find(attrs={"data-qa": "vacancy-description"})
        body_text = vacancy_body.get_text(" ", strip=True) if vacancy_body else ""

        result = f"{title_text}\n\n{body_text}".strip()

        if not result:
            return user_text

        return result

    except Exception:
        return user_text