"""Index declared response fields and JSON object examples without inferring a schema."""

import json
import re


_REQUEST = re.compile(r"\b(?:requests?|inputs?|запрос(?:а|ы|ов)?|входн\w*)\b", re.I)
_RESPONSE = re.compile(r"\b(?:responses?|outputs?|ответ(?:а|ы|ов)?|выходн\w*)\b", re.I)
_BRANCH = re.compile(r"\b(?:status(?:es)?|статус\w*|коды\s+ответа)\b", re.I)
_STATUS = re.compile(r"^(?:HTTP(?:/\d(?:\.\d)?)?\s+)?([1-5]\d{2})\b", re.I)
_INLINE_CODE = re.compile(r"(?:HTTP(?:/\d(?:\.\d)?)?\s+)?([1-5]\d{2})[.:]?", re.I)
_NAME = {"parameter", "field", "property", "name", "field name", "parameter name", "key", "параметр", "поле",
         "имя", "название", "наименование", "свойство", "ключ", "имя поля", "название поля", "имя параметра",
         "название параметра", "наименование параметра"}
_TYPE = {"type", "format", "data type", "тип", "формат", "тип данных"}
_CONDITION = {"logic", "condition", "conditions", "required", "mandatory", "presence", "constraint", "constraints",
              "allowed values", "логика", "условие", "условия", "обязательность", "обязательный", "обязателен",
              "ограничения", "допустимые значения"}
_DESCRIPTION = {"description", "описание"}


def _section(path):
    parts = path.split(" / ")
    headers = []
    if parts and parts[-1].startswith("Столбцы: "):
        headers = [s.strip() for s in parts.pop().removeprefix("Столбцы: ").split(" · ")]
    return parts, headers


def _role(parts):
    branch_at = None
    for index in range(len(parts) - 1, -1, -1):
        title = parts[index]
        # «Bad Request» is the English status name in a response heading.
        if _STATUS.match(title):
            continue
        if _REQUEST.search(title):
            return "request", index
        if _RESPONSE.search(title):
            return "response", index
        if branch_at is None and _BRANCH.search(title):
            branch_at = index
    return ("branch", branch_at) if branch_at is not None else ("", 0)


def _field(block, headers):
    text = block.text.strip()
    if "|" in text and "\t" not in text:
        values = re.split(r"(?<!\\)\|", text.strip("|"))
    elif "\t" in text:
        values = text.split("\t")
    else:
        values = re.split(r"\s{2,}", text)
    names = [name.casefold() for name in headers]
    if len(values) != len(headers) or not (_TYPE | _CONDITION).intersection(names):
        return None
    values = [value.strip().strip("`").strip() for value in values]
    name = next((v for h,v in zip(names,values) if h in _NAME), "")
    if not name or [v.casefold() for v in values] == names:
        return None
    row = dict(block=block.id, name=name, type=next((v for h,v in zip(names,values) if h in _TYPE), ""),
               conditions={h:v for h,v in zip(headers,values) if h.casefold() in _CONDITION and v})
    description = next((v for h,v in zip(names,values) if h in _DESCRIPTION), "")
    if description:
        row["description"] = description
    return row


def _json_keys(text):
    text = text.strip()
    fenced = re.fullmatch(r"(?P<fence>`{3,}|~{3,})(?:json)?\s*\n(.*)\n(?P=fence)", text, re.I | re.S)
    try:
        body = json.loads(fenced[2] if fenced else text)
    except ValueError:
        return None
    return list(body) if isinstance(body, dict) else None


def response_matrix(blocks):
    """Group response declarations and examples by endpoint, retaining source block IDs."""
    blocks = list(blocks)
    contracts = {}
    samples = []
    for index, block in enumerate(blocks):
        kind = getattr(block, "kind", None)
        if kind not in {"table", "code"}:
            continue
        parts, headers = _section(getattr(block, "section", ""))
        if not parts or not any(parts):
            continue
        role, at = _role(parts)
        if role == "request":
            continue
        context = tuple(parts[:at])
        if kind == "table" and role == "response" and (field := _field(block, headers)):
            contract = contracts.setdefault(context, dict(context=" / ".join(context), fields=[], examples=[]))
            contract["fields"].append(field)
        if kind == "code" and (role in {"response", "branch"} or _STATUS.match(parts[-1])):
            keys = _json_keys(block.text)
            if keys is None:
                continue
            status = next((m[1] for title in reversed(parts) if (m := _STATUS.match(title))), "")
            sample = dict(block=block.id, branch=parts[-1], keys=keys)
            if status:
                sample["heading_status"] = status
            previous = blocks[index - 1] if index else None
            if getattr(previous, "kind", None) == "text" and previous.section == block.section:
                inline = _INLINE_CODE.fullmatch(previous.text.strip().strip("*`").strip())
                if inline:
                    sample.update(inline_status=inline[1], label_block=previous.id)
            samples.append((tuple(parts), sample))
    for parts, sample in samples:
        compatible = [path for path in contracts if parts[:len(path)] == path]
        if compatible:
            contracts[max(compatible, key=len)]["examples"].append(sample)
    return {"contracts": list(contracts.values())} if contracts else {}
