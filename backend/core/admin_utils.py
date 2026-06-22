import json

from django.utils.html import format_html, format_html_join


def format_html_list(items: list) -> str:
    if not items:
        return "—"
    return format_html("<ul>{}</ul>", format_html_join("", "<li>{}</li>", ((item,) for item in items)))


def format_json_block(data) -> str:
    if not data:
        return "—"
    try:
        texto = json.dumps(data, ensure_ascii=False, indent=2)
    except TypeError:
        texto = str(data)
    return format_html("<pre style='white-space: pre-wrap;'>{}</pre>", texto)
