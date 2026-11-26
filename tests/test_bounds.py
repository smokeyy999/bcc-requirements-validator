import unittest
from types import SimpleNamespace

from requirements_validator.bounds import capacity_pairs, missing_capacity_basis, unresolved_capacity
from requirements_validator.engine import DraftError, OPERATION, VALUE, _final_decisions, _set_result


LIMIT = "Один альбом содержит не более 8 кадров."
OVERSIZED = "При импорте альбома из 11 кадров редактор принимает альбом и разрешает публикацию."
TRANSFORM = "Перед публикацией редактор сокращает альбом до 8 кадров."


def source(*passages):
    blocks = [SimpleNamespace(id=f"B{i}", text=text) for i, text in enumerate(passages, 1)]
    claims = [dict(block=b.id, id=f"R-{b.id}-01", quote=b.text, status="проверяемо") for b in blocks]
    return blocks, claims, capacity_pairs(blocks, claims)


class CapacityTests(unittest.TestCase):
    def test_text_limits_match_full_unit_and_implicit_text_or_same_named_field(self):
        limit = "Reject an item when its text exceeds 12 Unicode code points."
        for accepted in ("An item of 13 Unicode code points is accepted.",
                         "The editor accepts an item with text of 13 Unicode code points."):
            with self.subTest(accepted=accepted):
                _, _, (pair,) = source(limit, accepted)
                self.assertEqual((pair["subject"], pair["length_field"], pair["unit"]), ("item", "text", "unicode code point"))
                self.assertEqual((pair["limit"], pair["accepted"]), (12, 13))
                self.assertTrue(unresolved_capacity(pair, [], {}))
        _, _, (named,) = source("Reject a parcel if its title contains more than 9 characters.",
                                "A parcel whose title has 10 characters is accepted.")
        self.assertEqual(named["length_field"], "title")

    def test_text_overflow_does_not_confuse_fields_units_or_the_entire_record(self):
        limit = "Reject an item when its text exceeds 12 Unicode code points."
        for accepted in ("An item of 13 Unicode code units is accepted.",
                         "An item of 13 UTF-16 code units is accepted.",
                         "An item of 13 bytes is accepted.",
                         "An item with label of 13 Unicode code points is accepted.",
                         "An envelope of 13 Unicode code points is accepted.",
                         "An item of 12 Unicode code points is accepted.",
                         "An item of 13 Unicode code points is not accepted.",
                         "An item of 13 Unicode code points is skipped; the next item is accepted.",
                         "An item of 13 Unicode code points including the header is accepted."):
            with self.subTest(accepted=accepted):
                self.assertEqual(source(limit, accepted)[2], [])
        bare = "An item of 13 Unicode code points is accepted."
        for extra in ("The length of an item includes the header.",
                      "Reject an item when its label exceeds 12 Unicode code points."):
            self.assertEqual(source(limit, bare, extra)[2], [])
        for prefix in ("Unless marked as imported, ", "Never ", "When closed, "):
            self.assertEqual(source(prefix + limit, bare)[2], [])
        self.assertEqual(source(limit, "If used for preview, an item of 13 Unicode code points is accepted.")[2], [])

    def test_source_based_exception_applies_to_the_same_text_and_quantity(self):
        limit = "Reject a label when its text exceeds 7 characters."
        instance = "A label with text of 8 characters is accepted."
        accepted = "On import truncate the label text to 7 characters."
        waiver = "A label with text of 8 characters is exempt from the text length limit."
        _, _, (pair,) = source(limit, instance, accepted,
                               "Truncate the label title to 7 characters; keep its text.",
                               "Never truncate the label text to 7 characters.",
                               "Truncate the label text to 8 characters.", waiver,
                               "A label with text of 9 characters is exempt from the text length limit.")
        self.assertEqual(pair["qualification_ids"], ["R-B3-01", "R-B7-01"])
        self.assertFalse(unresolved_capacity(pair, [], {"R-B2-01":dict(supports=["R-B3-01"])}))

    def test_raw_quotes_show_same_container_and_exceeded_count(self):
        blocks, claims, pairs = source(LIMIT, OVERSIZED)
        clone = dict(claims[0], id="R-B1-02")
        pair, = capacity_pairs(blocks, claims + [clone])
        self.assertEqual((pair["limit"], pair["accepted"]), (8, 11))
        self.assertEqual(pair["limit_ids"], ["R-B1-01", "R-B1-02"])
        self.assertEqual(pair["instance_ids"], ["R-B2-01"])
        self.assertFalse(pair["qualification_ids"])
        self.assertEqual(len(pairs), 1)

    def test_different_objects_units_named_fields_and_restricted_next_stage_are_quiet(self):
        for left, right in (
                (LIMIT, "При импорте каталога из 11 кадров редактор разрешает публикацию."),
                (LIMIT, "При импорте альбома из 11 дорожек редактор разрешает публикацию."),
                ("Архивный альбом вмещает максимум 3 кадра.", "Входной альбом из 9 кадров принят."),
                ("rollId contains up to 3 letters.", "An entryId with 5 letters is accepted."),
                (LIMIT, "Альбом из 11 кадров принимается для просмотра, но его публикация запрещена."),
                (LIMIT, "Альбом из 11 кадров отклоняется."),
                (LIMIT, "Альбом из 8 кадров принят."),
                ("Packet contains at most 7 records.", "A packet with 8 records is rejected.")):
            with self.subTest(right=right):
                self.assertEqual(source(left, right)[2], [])

    def test_quantity_is_read_from_the_source_and_preserves_english_terms(self):
        _, _, (pair,) = source("Packet holds at most 7 records.", "A packet with 12 records is accepted.")
        self.assertEqual((pair["limit"], pair["accepted"]), (7, 12))

    def test_a_separate_quoted_prohibition_can_limit_approval_to_intake(self):
        refusal = "Альбом из 11 кадров передавать запрещено."
        _, claims, (pair,) = source(LIMIT, "При импорте альбом из 11 кадров принимается.", refusal)
        self.assertEqual(pair["qualification_ids"], [claims[2]["id"]])
        _, _, (explicit_onward,) = source(LIMIT, OVERSIZED, refusal)
        self.assertEqual(explicit_onward["qualification_ids"], [])

    def test_a_subset_in_the_reviewers_explanation_is_not_a_source_rule(self):
        blocks, claims, (pair,) = source(LIMIT, OVERSIZED)
        left, right = [c["id"] for c in claims]
        gap = dict(kind="Предполагаемый пробел", category="Полнота", ids=[left, right])
        self.assertTrue(unresolved_capacity(pair, [gap], {}))
        self.assertFalse(unresolved_capacity(pair, [dict(gap, kind="Дефект", category="Противоречивость")], {}))
        raw = dict(assessment="Готово.", readiness="Готово.", priorities=[], traces=[], findings=[],
                   scope={"operations": left, "values": right}, resolved=[
                       dict(id=c["id"], reason="Редактор выбирает удобное подмножество.", supports=[left, right])
                       for c in claims])
        with self.assertRaisesRegex(DraftError, "предел 8"):
            _set_result(raw, claims, {b.id: b for b in blocks}, {OPERATION: [], VALUE: []}, {}, capacities=[pair])

    def test_positive_exception_requires_a_verbatim_quote_for_the_same_object(self):
        _, claims, (pair,) = source(LIMIT, OVERSIZED, TRANSFORM,
            "Перед публикацией редактор сокращает каталог до 8 кадров.",
            "Перед публикацией редактор не сокращает альбом до 8 кадров.",
            "Перед публикацией редактор сокращает альбом до 10 кадров.")
        left, right, valid, other, negated, insufficient = [c["id"] for c in claims]
        self.assertEqual(pair["qualification_ids"], [valid])
        ids = [left, right]
        evidence = [dict(id=c["id"], quote=c["quote"]) for c in claims[:2]]
        candidate = dict(id="Z-001", kind="Дефект", category="Противоречивость", counted=True, ids=ids,
                         evidence=evidence, proposal_options=[dict(anchor=e) for e in evidence])
        case = dict(status="разные условия", condition="Размер изменяется отдельным правилом.", effect="", anchors=evidence)
        d = dict(id="Z-001", action="снять", reason="Состав сокращён.", question_mode="убрать", blocking=False,
                 question="", test="", supports=[], case_check=case, severity="Низкая", question_check=[],
                 same_decision_as="")
        audit = dict(assessment="Рассмотрено.", readiness="Готово.", priorities=[], decisions=[d])
        by_id = {c["id"]: c["quote"] for c in claims}
        for ident, excerpt in [(valid, "Перед публикацией"), (other, by_id[other]),
                               (negated, by_id[negated]), (insufficient, by_id[insufficient])]:
            with self.subTest(excerpt=excerpt), self.assertRaisesRegex(DraftError, "предел 8"):
                case["anchors"] = evidence + [dict(id=ident, quote=excerpt)]
                _final_decisions(audit, [candidate], claims, capacities=[pair])
        case["anchors"] = evidence + [dict(id=valid, quote=TRANSFORM)]
        self.assertEqual(_final_decisions(audit, [candidate], claims, capacities=[pair])[0], [])
        self.assertFalse(unresolved_capacity(pair, [], {right: dict(supports=[valid])}))
        self.assertTrue(unresolved_capacity(pair, [], {right: dict(supports=[other])}))

    def test_final_downgrade_needs_the_source_exception_even_if_ids_were_retained(self):
        _, claims, (pair,) = source(LIMIT, OVERSIZED)
        ids = [c["id"] for c in claims]
        original = dict(id="Z-003", ids=ids, category="Противоречивость", kind="Дефект")
        kept = [dict(original, kind="Предполагаемый пробел", category="Полнота")]
        decision = dict(id="Z-003", case_check=dict(anchors=claims))
        self.assertEqual(missing_capacity_basis(pair, kept, [decision], {"Z-003": original}), [0])
        self.assertEqual(missing_capacity_basis(pair, [original], [decision], {"Z-003": original}), [])
