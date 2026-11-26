"""Check explicitly local, named cross-references against the complete source index."""

from collections import defaultdict
import re
import unicodedata


_NAME = r"[^\W\d_][\w]*(?:[-‐‑–.]\d+)+"
_ID = re.compile(r"(?<![\w-])" + _NAME + r"(?![\w-]|\.[\w])")
_USE = re.compile(
    r"\b(?:по\s+(?:правилу|пункту|требованию)|согласно\s+(?:правилу|пункту|требованию)|"
    r"см\.\s*(?:правило|пункт|требование)?|(?:see|under|per|according to)\s+"
    r"(?:the\s+)?(?:rule|section|requirement|clause))\s*[«\[`*]*"
    r"(?P<name>" + _NAME + r")(?![\w-]|\.[\w])", re.I)
_EXTERNAL = re.compile(r"\b(?:внешн\w*|стандарт\w*|регламент\w*|договор\w*|приложени\w*|"
                       r"(?:из|в|согласно)\s+(?:спецификаци\w*|ТЗ)\s+(?:клиента|партн[её]ра|заказчика|подрядчика)|"
                       r"документ\w*\s+[«\"\w]|ГОСТ|RFC|ISO|external|separate|other\s+document|"
                       r"standard|contract|manual|appendix|annex|(?:in|of|from)\s+(?:the\s+)?document|"
                       r"specification\s+[A-Z0-9])\b|"
                       r"https?://|\.(?:md|html?|pdf|docx?)\b", re.I)
_LINK = re.compile(r"\[[^\]\n]+\](?:\(([^)\n]+)\)|\[[^\]\n]*\])")
_HTML_ID = re.compile(r'''<(?:a|span|div|h[1-6])\b[^>]*?\b(?:id|name)\s*=\s*['"](''' + _NAME + r''')['"]''', re.I)
_EDITORIAL_QUESTION = re.compile(
    r'\s*(?:какой\s+(?:пункт|идентификатор|номер|адрес)\s+(?:указать|поставить|вставить)\s+вместо|'
    r'на\s+какой\s+пункт\s+(?:заменить|исправить)\s+(?:ссылку\s+)?(?:на\s+)?|'
    r'which\s+(?:identifier|section|requirement|rule)\s+should\s+replace)\s*[«"`]?'
    r'(?P<name>' + _NAME + r')[»"`]?\s*\?\s*', re.I)


def _key(name):
    return unicodedata.normalize('NFC', name).translate(str.maketrans('‐‑–', '---'))


def _family(name):
    return re.split(r'(?=[.-]\d)', name, 1)[0]


def missing_references(blocks):
    """Only assert absence in a locally declared namespace. Keep uncertain scopes silent."""
    declared, possible = set(), set()
    for block in blocks:
        name = getattr(block, 'source_id', None) or ''
        if _ID.fullmatch(name):
            declared.add(_key(name))
        # A heading may be the target. PDF layout tables can retain their visible
        # ID column without a source_id; a standalone cell is a possible definition.
        possible.update(_key(m[0]) for m in _ID.finditer(block.section))
        possible.update(_key(m[1]) for m in _HTML_ID.finditer(block.text))
        if getattr(block, 'kind', None) == 'table':
            for cell in re.split(r'\||\t|\s{2,}', block.text):
                token = cell.strip(' *_`[]:')
                if _ID.fullmatch(token):
                    possible.add(_key(token))
    existing = {name.casefold() for name in declared | possible}
    families = {_family(name) for name in declared}
    found = {}
    for block in blocks:
        if not families or getattr(block, 'kind', None) == 'code':
            continue
        for clause in re.split(r'\n|(?<=[.!?;])(?<!см\.)\s+(?=[^\W\d_])', block.text, flags=re.I):
            if _EXTERNAL.search(clause) or _EXTERNAL.search(block.section.split(' / ')[-1]):
                continue
            links = list(_LINK.finditer(clause))
            for ref in _USE.finditer(clause):
                name = ref['name']
                key = _key(name)
                if key.casefold() in existing or _family(key) not in families:
                    continue
                if any(m.start() <= ref.start('name') < m.end() and _key(m[1] or '') != '#' + key for m in links):
                    continue
                found.setdefault((key, block.id), dict(block=block.id, target=name, citation=ref[0]))
    return list(found.values())


def reference_findings(references, claims, blocks, context):
    """Anchor a structural fact even when extraction omitted the reference fragment."""
    grouped = defaultdict(list)
    for claim in claims:
        grouped[claim['block']].append(claim)
    by_target = {}
    for ref in references:
        block = blocks[ref['block']]
        name, quote = ref['target'], ref['citation']
        rows = grouped[block.id]
        matching = [c for c in rows if quote in c['quote'] or name in c['quote'] and c['quote'] in quote]
        if matching:
            claim = min(matching, key=lambda c: len(c['quote']))
        else:
            claim = dict(block=block.id, id=f'R-{block.id}-{len(rows)+1:02}', source_id=block.source_id,
                         quote=quote, summary=f'Документ ссылается на пункт {name}.', section=block.section,
                         location=block.location, trace='локально', status='проверить',
                         assessment='Проверить адрес ссылки.', findings=[])
            rows.append(claim)
            claims.append(claim)
            context[:] = [row for row in context if not isinstance(row, dict) or row.get('block') != block.id]
        ident = claim['id']
        evidence = dict(id=ident, block=block.id, quote=quote, section=block.section, location=block.location)
        key = _key(name)
        if key in by_target:
            prior = by_target[key]
            if ident not in prior['ids']:
                prior['ids'].append(ident)
            prior['evidence'].append(evidence)
            continue
        by_target[key] = dict(topic=f'Отсутствует цель внутренней ссылки {name}', kind='Дефект',
                             category='Трассируемость', severity='Низкая', counted=True, ids=[ident],
                             evidence=[evidence], reason=f'Именованная ссылка {name} не разрешается в этом документе.',
                             scenario=f'Перейти по ссылке {name} в исходном правиле.',
                             consequence='Читатель не может найти пункт, на который ссылается требование.',
                             fix='Указать действительный адрес правила или включить его полное содержание в исходный пункт. '
                                 'Проверить, что переход из исходного условия ведёт к объявленному правилу и определяет его содержание.',
                             reference=None, interpretations=[], proposal_options=[], question='', test='', blocking=False,
                             missing_target=name)
    return list(by_target.values())


def repeats_reference(finding, verified):
    """Fold a model's second traceability card for the same named citation only."""
    question = finding.get('question', '')
    editorial = _EDITORIAL_QUESTION.fullmatch(question) if question else None
    if question and not editorial or not question and finding['category'] != 'Трассируемость':
        return False
    named = {_key(editorial['name'])} if editorial else {_key(m[0]) for m in _ID.finditer(finding['topic'])}
    return any(_key(ref['missing_target']) in named and set(ref['ids']).intersection(finding['ids']) for ref in verified)


def has_independent_basis(finding, verified, quotes):
    """A separate behavioral question must cite more than a dangling pointer."""
    if finding['kind'] != 'Предполагаемый пробел' or not finding['question']:
        return True
    related = [ref for ref in verified if set(ref['ids']).intersection(finding['ids'])]
    if not related:
        return True
    basis = finding['question_basis']
    obligation = quotes[basis['obligation_id']]
    citations = [e['quote'] for ref in related for e in ref['evidence']]
    for fragment in re.findall(r'«([^»]+)»', basis['decision']):
        if fragment not in obligation:
            continue
        for citation in citations:
            if fragment in citation:
                break
            fragment = fragment.replace(citation, ' ')
        else:
            if re.search(r'[^\W\d_]{2,}', _ID.sub(' ', fragment)):
                return True
    return False


REFERENCE_INSTRUCTION = (
    'verified_references — редакторские дефекты, уже установленные проверкой полного индекса исходника. '
    'Их цитаты и отсутствие указанного пункта проверены. Учитывай их в итоге и порядке исправлений. '
    'Не возвращай повтор этих карточек в findings или decisions. Для самой ссылки достаточно редакторского '
    'исправления. Не угадывай её цель. Не выноси повторное согласование наблюдаемого поведения, если оно '
    'уже установлено другими пунктами. Само отсутствие адресата не обещает дополнительного поведения. '
    'Отдельный бизнес-вопрос требует самостоятельно подтверждённого условия и двух конкретных наблюдаемых '
    'исходов. Если у оставленного предполагаемого пробела общие ID с verified_references, '
    'в question_check.decision заключи в «ёлочки» дословную предметную выдержку из obligation_id, '
    'которая обязывает определить этот отдельный результат. Одна ссылка не является таким основанием.'
)
