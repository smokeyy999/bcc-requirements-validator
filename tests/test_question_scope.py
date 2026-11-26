import unittest
from types import SimpleNamespace

from requirements_validator.engine import DraftError, _final_decisions
from requirements_validator.question_scope import candidate_scopes, identifier_limits, source_boundaries, unreviewed_boundaries
from tests.test_engine import checked_question


class AcceptanceScopeTests(unittest.TestCase):
    def decide(self, sources, question, test, *, original="", outcomes=None):
        claims = [dict(id=f"R-M0001-{i:02}", quote=source) for i, source in enumerate(sources, 1)]
        ids = [claim["id"] for claim in claims]
        finding = dict(id="Z-001", topic=original or question, question=original or question, test=test,
                       scenario=test, reason="Открытая проверка.", severity="Существенная", counted=False,
                       category="Полнота", kind="Предполагаемый пробел", fix="", ids=ids, evidence=claims)
        check = checked_question(ids[0], sources[0], question, *(outcomes or ("Проходит.", "Отклонён.")))
        check[0]["checked_ids"] = ids
        decision = dict(id="Z-001", action="оставить", basis="Обоснованное ожидание", severity="Существенная",
                        reason="Проверены границы.", blocking=False, supports=[], question_mode="заменить",
                        question=question, test=test, question_check=check, same_decision_as="",
                        case_check=dict(status="не применимо", condition="", anchors=[], effect=""))
        audit = dict(assessment="Оценка.", readiness="Требует решения.", decisions=[decision],
                     priorities=[dict(ids=["Z-001"], step="Согласовать условие.")])
        return _final_decisions(audit, [finding], claims)[0][0]

    def test_multibyte_identifier_requires_a_supported_value(self):
        q = "Для серийного номера ограничение длины действует в байтах или символах?"
        t = "Передать многобайтовый номер, проверить его при граничной длине."
        field = "Серийный номер экспоната назначает музей; размер от 1 до 32."
        for quote in (field, field + " Пример допустимого номера: X-24.",
                      field + " Не допускаются многобайтовые символы."):
            with self.subTest(source=quote), self.assertRaisesRegex(DraftError, "незаявленный алфавит"):
                self.decide([quote], q, t)
        approved = ["Идентификатор может содержать кириллицу.",
                    "Для серийного номера приведён пример: «Зал-41»."]
        for quote in approved:
            with self.subTest(source=quote):
                self.assertEqual(self.decide([field, quote], q, t)["question"], q)

    def test_receiver_timing_distinguishes_acceptance_scope_from_a_promised_deadline(self):
        sources = ["Посетитель узнаёт о готовности в момент выдачи.",
                   "Стойка передаёт извещение диспетчеру в течение минуты."]
        broad = "Какой срок получения извещения посетителем или клиентом допустим?"
        narrowed = "Входит ли получение извещения клиентом в приёмку и, если входит, между какими событиями измерять срок?"
        t = "Проверить известный срок передачи, а при включении клиента в приёмку измерить согласованный интервал."
        with self.assertRaisesRegex(DraftError, "границе приёмки"):
            self.decide(sources, broad, t)
        self.assertEqual(self.decide(sources, narrowed, t, original=broad)["question"], narrowed)
        with self.assertRaisesRegex(DraftError, "границе приёмки"):
            self.decide(sources, narrowed, "В любом случае замерить срок получения извещения клиентом.", original=broad)
        sources.append("Клиент получает извещение не позднее срока, заданного в соглашении для его тарифа.")
        self.assertEqual(self.decide(sources, broad, t)["question"], broad)

    def test_sender_flag_cannot_depend_on_an_unpromised_receiver_acknowledgement(self):
        sources = ["В реестре хранится флаг отправки листа.", "Диспетчер передаёт лист в типографию."]
        q = "Когда ставится флаг отправки листа?"
        broad = "Проверить состояние признака до и после получения листа клиентом."
        with self.assertRaisesRegex(DraftError, "на границе отправителя"):
            self.decide(sources, q, broad)
        t = "Записать состояние до и после выбранного события передачи листа из диспетчерской в типографию."
        self.assertEqual(self.decide(sources, q, t)["test"], t)
        with self.assertRaisesRegex(DraftError, "на границе отправителя"):
            self.decide(sources, q, "Проверить только конечное состояние флага.")
        with self.assertRaisesRegex(DraftError, "на границе отправителя"):
            self.decide([*sources, "Устройство получателя не возвращает квитанцию о получении."], q, broad)
        with self.assertRaisesRegex(DraftError, "на границе отправителя"):
            self.decide(sources, q, t, outcomes=("Флаг ставится при передаче.", "Флаг ставится после получения клиентом."))
        sources.append("Устройство получателя возвращает квитанцию о получении листа.")
        self.assertEqual(self.decide(sources, q, broad)["test"], broad)

    def test_source_hints_are_attached_to_actual_blocks(self):
        rows = ["Архив передаёт пакет на обработку не позднее минуты.", "Пользователь узнаёт об отмене сразу.",
                "Архив хранит время и признак отправки пакета.", "Идентификатор экспоната: строка длиной 8."]
        blocks = [SimpleNamespace(id=f"B{i}", text=text, section="Условия") for i, text in enumerate(rows)]
        self.assertEqual(source_boundaries(blocks), dict(timed_handoff=["B0"], recipient_goals=["B1"], recorded_state=["B2"]))
        self.assertEqual(source_boundaries(blocks[1:]), {})
        self.assertTrue(identifier_limits(blocks))
        self.assertEqual(candidate_scopes([dict(id="Z-001", question="Какой срок доставки адресату?")]),
                         {"Z-001": "граница измерения срока"})

    def test_another_field_does_not_supply_the_alphabet(self):
        q = "Предел длины parcelId применяется в байтах или символах?"
        test = "Передать граничный номер с многобайтовыми символами."
        field = "parcelId — идентификатор посылки, строка длиной до 20."
        with self.assertRaisesRegex(DraftError, "незаявленный алфавит"):
            self.decide([field, "receiverId допускает кириллицу."], q, test)
        self.assertEqual(self.decide([field, "parcel_id допускает кириллицу."], q, test)["question"], q)
        self.assertEqual(candidate_scopes([dict(id="Z-001", question="Is a valid length measured in bytes?")]), {})

    def test_handoff_decisions_are_accounted_for_separately(self):
        boundaries = dict(recipient_goals=["B1"], recorded_state=["B2"])
        claims = [dict(id="R1", block="B1", quote="Клиент узнаёт о готовности сразу."),
                  dict(id="R2", block="B2", quote="Хранить флаг отправки."),
                  dict(id="R3", block="B2", quote="Хранить номер заказа.")]
        timing = dict(ids=["R1"], question="Входит ли получение клиентом в срок приёмки?")
        flag = dict(ids=["R2"], question="Какое событие передачи устанавливает флаг отправки?")
        self.assertEqual(unreviewed_boundaries(boundaries, claims, [timing, flag], {}), [])
        self.assertEqual(len(unreviewed_boundaries(boundaries, claims, [timing], {"R3": {}})), 1)
        self.assertEqual(unreviewed_boundaries(boundaries, claims, [timing], {"R2": {"supports": ["R2"]}}), [])
