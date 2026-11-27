import unittest
from types import SimpleNamespace

from requirements_validator.engine import review
from requirements_validator.references import has_independent_basis, missing_references, reference_findings, repeats_reference
from requirements_validator.source import _index_page
from tests.test_engine import Responses, checked_question


def blocks(lines, page=None):
    result = []
    _index_page('\n'.join(lines), page, [], result)
    return result


class NamedReferenceTest(unittest.TestCase):
    def test_named_target_after_an_attribution_without_a_section_label(self):
        source = blocks(["# Audio catalogue", "AX-1. Play the tone defined in AX-37.",
                         "AX-2. See ax-8 for the recorded voice.", "AX-8. Use voice B.",
                         "AX-3. Вывести сообщение, приведённое в AX-42.",
                         "AX-4. Use the option specified in AX-71 of the external manual.",
                         "AX-5. Display the literal label AX-63.", "AX-6. Read the value listed in BZ-99.",
                         "AX-7. Use the colour listed in ax-48."])
        self.assertEqual({r["target"] for r in missing_references(source)}, {"AX-37", "AX-42", "ax-48"})

    def test_existing_targets_tables_headings_and_external_scopes(self):
        source = blocks(['# Calibration', 'AX-1. Вычислить по правилу AX-17.', 'AX-17. Приставить груз.',
                         'AX-2. См. правило AX-19.', '## AX-19 Проверка', 'AX-3. Открыть по пункту AX-21.',
                         '| ID | Результат |', '|---|---|', '| AX-21 | Закрыто |',
                         'AX-4. See rule [AX-26](other.txt).', 'AX-5. Проверить по правилу AX-27 внешнего регламента.',
                         'AX-6. Follow the external specification under rule AX-28.',
                         'AX-7. По правилу BK-81 оформить акт.', 'AX-8. Отобразить код AX-95.',
                         'AX-9. См. правило AX-62 из документа «Контракт прибора».',
                         'AX-10. См. правило [AX-65](#calibration).',
                         'AX-12. См. правило AX-64.', '<a id="AX-64"></a>'])
        self.assertEqual(missing_references(source), [])
        pdf = blocks(['AX-1. See rule AX-7.', 'Code  Meaning', 'AX-7  Calibrated'], page=1)
        self.assertIsNone(pdf[-1].source_id)
        self.assertEqual(missing_references(pdf), [])

    def test_group_per_target_preserves_exact_addresses_and_independent_missing_targets(self):
        source = blocks(['# Экран', 'КБ-6. Включить по правилу КБ-23.',
                         'КБ-7. См. требование КБ‑23.', 'КБ-8. Сверить по пункту КБ-24.'])
        references = missing_references(source)
        self.assertEqual([r['target'] for r in references], ['КБ-23', 'КБ‑23', 'КБ-24'])
        claims = []
        context = [{'block': b.id, 'role': 'контекст'} for b in source]
        found = reference_findings(references, claims, {b.id: b for b in source}, context)
        self.assertEqual(context, [{"block": "M0001", "role": "контекст"}])
        first, second = found
        self.assertEqual([e['location'] for e in first['evidence']], ['строка 2', 'строка 3'])
        self.assertEqual([e['quote'] for e in first['evidence']], ['по правилу КБ-23', 'См. требование КБ‑23'])
        self.assertEqual(len(first['ids']), 2)
        self.assertEqual(second['evidence'][0]['location'], 'строка 4')
        self.assertEqual((first['category'], first['question'], first['counted']), ('Трассируемость', '', True))
        self.assertTrue(repeats_reference(dict(topic='Нет правила КБ-23', category='Трассируемость', ids=first['ids'][:1]), found))
        self.assertFalse(repeats_reference(dict(topic='Нет допуска при перегрузке КБ-23', category='Полнота', ids=first['ids']), found))
        self.assertTrue(repeats_reference(dict(topic='Адрес', category='Полнота', ids=first['ids'],
                                               question='Какой идентификатор указать вместо КБ-23?'), found))

    def test_pointer_alone_cannot_substantiate_an_additional_behavior(self):
        citation = 'по правилу КБ-54'
        ref = dict(ids=['r'], evidence=[dict(quote=citation)])
        obligation = 'Отметить результат по правилу КБ-54.'
        finding = dict(kind='Предполагаемый пробел', question='Что вывести?', ids=['r'],
                       question_basis=dict(obligation_id='r', decision='Нужен новый результат «по правилу КБ-54».'))
        self.assertFalse(has_independent_basis(finding, [ref], {'r': obligation}))
        finding['question_basis']['decision'] = 'Обязателен «вывод сообщения». Какого именно?'
        self.assertFalse(has_independent_basis(finding, [ref], {'r': obligation}))
        finding['question_basis']['decision'] = 'Требуется «Отметить результат». Какое значение предъявить проверяющему?'
        self.assertTrue(has_independent_basis(finding, [ref], {'r': obligation}))

    def test_full_review_keeps_editorial_defect_and_independent_business_question(self):
        source = blocks(['# Насос', '## Н-1. Показать объём по правилу Н-17. После сбоя насос переходит в аварийное состояние.',
                         'Н-2. На дисплее указывается объём в литрах.'])
        title, rule, description = source
        label, fault, display = 'Показать объём по правилу Н-17.', 'После сбоя насос переходит в аварийное состояние.', description.text
        local = dict(claims=[dict(block=b.id, quote=q, summary=q, assessment='Проверить условие.',
                                  status='проверяемо', trace='локально')
                             for b, q in ((rule, label), (rule, fault), (description, display))],
                     context=[dict(block=title.id, role='контекст')])
        anchor = 'R-M0002-02'
        question = 'В какое состояние должен перейти насос после сбоя?'
        gap = dict(topic='Состояние после сбоя', kind='Предполагаемый пробел', category='Полнота',
                   severity='Существенная', reason='Аварийное состояние не определено.', scenario='Вызвать сбой.',
                   consequence='Не известен ожидаемый переход.', evidence=[dict(id=anchor, quote=fault)],
                   interpretations=[], question=question, test='После сбоя проверить состояние насоса.', blocking=False,
                   fix='', reference='')
        whole = dict(findings=[gap], resolved=[], traces=[], scope=dict(operations=anchor, values=anchor),
                     assessment='Проверена ссылка и аварийный переход.', readiness='Исправить замечания.',
                     priorities=['Определить переход.'])
        decision = dict(id='Z-001', action='оставить', basis='Прямое обязательство', severity='Существенная',
                        reason='Названо аварийное состояние без результата.', blocking=False, supports=[],
                        question_mode='сохранить', question='', test='', same_decision_as='',
                        case_check=dict(status='не применимо', condition='', anchors=[], effect=''),
                        question_check=checked_question(anchor, 'После сбоя обязателен переход.', 'Что делает насос?',
                                                        'Насос остановлен.', 'Насос работает.'))
        audit = dict(decisions=[decision], assessment='Два замечания.', readiness='Нужно определить переход.',
                     priorities=[dict(ids=['Z-001', 'Z-002'], step='Определить аварийный переход и восстановить ссылку.')])
        provider = Responses(local, whole, audits=[audit])
        result = review(SimpleNamespace(blocks=source), provider)
        self.assertEqual([f['category'] for f in result['findings']], ['Полнота', 'Трассируемость'])
        self.assertEqual([q['question'] for q in result['questions']], [question])
        self.assertIn('verified_references', provider.calls[-1][0])
