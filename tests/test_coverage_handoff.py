import unittest

from requirements_validator.coverage_handoff import build, verify


def matrix(key="language", owner="Z-1", status="дополнить"):
    return dict(key=key, finding_id=owner, status=status, decision="Источник языка до регистрации",
                known="Клиент открывает каталог", checked=["R-1"], distinction="Регистрации ещё нет",
                question="Откуда каталог получает язык до регистрации?",
                test="Открыть каталог без регистрации и сверить язык.", outcomes=["Язык устройства", "Язык витрины"])


def decision(ident="Z-1", action="оставить", mode="сохранить", owner=""):
    return dict(id=ident, action=action, question_mode=mode, same_decision_as=owner, reason="Проведена рецензия")


def group(*members, question=None, test=None):
    return dict(findings=list(members), question=question or matrix()["question"], test=test or matrix()["test"])


def disposition(key="language", owner="Z-1"):
    return dict(key=key, status="покрыто", owner=owner, question_quote="каталог получает язык до регистрации",
                test_quote="каталог без регистрации", source_id="", source_quote="", reason="")


class CoverageHandoffTests(unittest.TestCase):
    def test_unchanged_rows_and_source_defined_decisions_require_no_extra_proof(self):
        row = matrix()
        raw = dict(decisions=[decision(mode="заменить")])
        public = [group("Z-1", question="Для владельца. " + row["question"], test=row["test"].rstrip(".") + "!")]
        accepted = [dict(id="Z-1", question=public[0]["question"])]
        self.assertEqual(build([row, matrix("known", status="задано")], raw, accepted, public), [])
        existing = matrix(status="уже проверено")
        del existing["question"], existing["test"]
        self.assertFalse(build([existing], raw, accepted, public, [dict(row, id="Z-1")]))
        self.assertFalse(build([existing], dict(decisions=[]), [dict(id="Z-1", missing_target="A-3")], []))

    def test_ordinary_removal_empty_queue_and_unchanged_but_suppressed_question(self):
        row = matrix()
        self.assertEqual(build([row], dict(decisions=[decision(action="снять", mode="убрать")]), [], [])[0]
                         ["transition"], "снят")
        raw = dict(decisions=[decision(mode="убрать")])
        handoff, = build([row], raw, [dict(id="Z-1", question="")], [])
        self.assertIsNone(handoff["published"])
        self.assertEqual(handoff["transition"], "нет опубликованного вопроса")
        with self.assertRaisesRegex(ValueError, "key"):
            verify([handoff], [], [], {}, raw)

    def test_merged_removal_needs_quotes_from_current_public_owner_and_its_combined_test(self):
        raw = dict(decisions=[decision(action="снять", mode="убрать", owner="Z-2"), decision("Z-2")])
        group2 = group("Z-2", question="Как каталог получает язык до регистрации?")
        kept = [dict(id="Z-2", question=group2["question"])]
        handoffs = build([matrix()], raw, kept, [group2])
        self.assertEqual(handoffs[0]["transition"], "объединён")
        self.assertEqual(handoffs[0]["published"]["owner"], "Z-2")
        receipt = disposition(owner="Z-2")
        verify(handoffs, [receipt], [group2], {}, raw)
        for changed in [dict(owner="Z-1"), dict(question_quote="Откуда каталог получает язык"),
                        dict(test_quote="каталог"), dict(source_id="R-1"),
                        dict(question_quote="язык"), dict(test_quote="установить язык автоматически")]:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                verify(handoffs, [dict(receipt, **changed)], [group2], {}, raw)

    def test_retained_member_may_precede_owner_and_only_owner_question_is_published(self):
        row = matrix()
        raw = dict(decisions=[decision(owner="Z-2"), decision("Z-2")])
        published = group("Z-1", "Z-2", question="Как каталог получает язык до регистрации?",
                          test="Запустить устройство. Открыть каталог без регистрации и сверить язык.")
        retained = [dict(id="Z-1", question=row["question"]), dict(id="Z-2", question=published["question"])]
        handoffs = build([row], raw, retained, [published])
        verify(handoffs, [disposition(owner="Z-2")], [published], {}, raw)
        with self.assertRaises(ValueError):
            verify(handoffs, [dict(disposition(owner="Z-2"), question_quote=row["question"])], [published], {}, raw)

    def test_previously_unlinked_duplicate_can_be_covered_by_an_existing_public_group(self):
        raw = dict(decisions=[decision(action="снять", mode="убрать"), decision("Z-2")])
        public = group("Z-2")
        rows = build([matrix()], raw, [dict(id="Z-2", question=public["question"])], [public])
        self.assertIsNone(rows[0]["published"])
        verify(rows, [disposition(owner="Z-2")], [public], {}, raw)

    def test_replacement_losing_an_old_condition_is_sent_to_proof_and_an_existing_decision_can_be_restored(self):
        raw = dict(decisions=[decision(mode="заменить")])
        narrowed = group("Z-1", question="Как каталог получает настройки?", test="Запустить каталог и сверить настройки.")
        old, = build([matrix()], raw, [dict(id="Z-1", question=narrowed["question"])], [narrowed])
        self.assertEqual(old["previous"]["outcomes"], matrix()["outcomes"])
        self.assertNotEqual(old["previous"]["test"], old["published"]["test"])
        with self.assertRaises(ValueError):
            verify([old], [disposition()], [narrowed], {}, raw)
        withdrawn = dict(decisions=[decision(action="снять", mode="убрать")])
        restored = build([matrix()], withdrawn, [], [])
        verify(restored, [disposition()], [group("Z-1")], {}, raw)

    def test_source_closure_needs_exact_quote_and_specific_explanation_may_use_new_source(self):
        raw = dict(decisions=[decision(action="снять", mode="убрать")])
        handoffs = build([matrix()], raw, [], [])
        source = {"R-4": "До регистрации каталог получает язык витрины из настроек сайта."}
        receipt = dict(key="language", status="закрыто", owner="", question_quote="", test_quote="",
                       source_id="R-4", source_quote="каталог получает язык витрины из настроек сайта",
                       reason="Для каталога до регистрации установлен язык витрины из настроек сайта.")
        verify(handoffs, [receipt], [], source, raw)
        for change in [dict(source_id="R-1"), dict(source_quote="каталог получает язык устройства"),
                       dict(source_quote="каталог"), dict(reason="Ответ указан в документе"),
                       dict(reason=receipt["source_quote"]), dict(reason="Задержку регулирует будильник."),
                       dict(owner="Z-1"), dict(test_quote="каталог без регистрации")]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify(handoffs, [dict(receipt, **change)], [], source, raw)

    def test_reject_duplicate_unknown_and_substantive_but_unrelated_witnesses(self):
        raw = dict(decisions=[decision(action="снять", mode="убрать", owner="Z-2"), decision("Z-2")])
        public = group("Z-2", question="Где видна очередь печати?", test="Отправить страницу принтеру.")
        handoffs = build([matrix()], raw, [dict(id="Z-2", question=public["question"])], [public])
        receipt = dict(disposition(owner="Z-2"), question_quote="очередь печати", test_quote="Отправить страницу принтеру")
        for dispositions in ([receipt, receipt], [dict(receipt, key="другое")], [receipt]):
            with self.subTest(dispositions=dispositions), self.assertRaises(ValueError):
                verify(handoffs, dispositions, [public], {}, raw)

    def test_single_repair_message_names_both_receipts_and_every_invalid_quote(self):
        raw = dict(decisions=[decision(action="снять", mode="убрать", owner="Z-2"), decision("Z-2"),
                              decision("Z-3", action="снять", mode="убрать")])
        public = group("Z-2")
        kept = [dict(id="Z-2", question=public["question"])]
        order = dict(matrix("order", "Z-3"), decision="Порядок заявок", known="Очередь заявок",
                     question="Как сортируются заявки?", test="Добавить две заявки и проверить порядок.",
                     distinction="У заявок разные даты", outcomes=["Сначала ранняя", "Сначала поздняя"])
        rows = build([matrix(), order], raw, kept, [public])
        source = {"R-8": "Очередь заявок сортируется по дате создания."}
        covered = disposition(owner="Z-2")
        closed = dict(key="order", status="закрыто", owner="", question_quote="", test_quote="",
                      source_id="R-8", source_quote="сортируется по дате создания",
                      reason="Порядок заявок определяет дата создания.")
        verify(rows, [covered, closed], [public], source, raw)
        with self.assertRaises(ValueError) as caught:
            verify(rows, [dict(covered, question_quote="чужой вопрос", test_quote="чужой тест"),
                          dict(closed, source_quote="сортируется по номеру", reason="задано")], [public], source, raw)
        message = str(caught.exception)
        for field in ("(key=language).question_quote:", "(key=language).test_quote:",
                      "(key=order).source_quote:", "(key=order).reason:"):
            self.assertIn(field, message)


if __name__ == "__main__":
    unittest.main()
