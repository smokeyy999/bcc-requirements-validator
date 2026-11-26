from types import SimpleNamespace
import unittest

from requirements_validator.data_boundary import data_boundary_error, storage_units


def rules(*rows):
    blocks = [SimpleNamespace(id=f"B{i}", text=text) for i, text in enumerate(rows)]
    claims = [dict(id="R" + block.id, block=block.id, quote=block.text) for block in blocks]
    return storage_units(blocks, claims)


class DataBoundaryTests(unittest.TestCase):
    stored = "Хранить номер заявки, массу пробы в граммах и дату приёмки."
    incoming = "Весы передают станции событие взвешивания."
    neutral = "Из какого источника станция получает массу пробы?"

    def check(self, question, scenario="", *, outcomes=(), sources=()):
        finding = dict(ids=["RB0", "RB1"], question=question, test=scenario,
                       question_basis=dict(checked_ids=[], outcomes=outcomes))
        return data_boundary_error(finding, rules(self.stored, self.incoming, *sources))

    def test_wrong_unit_on_inbound_question_or_its_two_test_branches(self):
        self.assertTrue(self.check("Откуда станция получает идентификатор образца, массу пробы в граммах и дату?"))
        self.assertTrue(self.check(self.neutral, "Подать в пакете массу пробы в граммах, проверить запись."))
        outcomes = ["Если датчик основной, он передаёт массу пробы в граммах.",
                    "Резервный датчик передаёт массу пробы в граммах."]
        self.assertTrue(self.check(self.neutral, outcomes=outcomes))

    def test_storage_unit_checked_after_input_and_conversion_is_valid(self):
        test = "Подать событие с согласованным значением, проверить преобразование и запись массы пробы в граммах."
        outcomes = ["Датчик передаёт исходное значение, станция сохраняет массу пробы в граммах.",
                    "Станция находит значение по номеру, затем записывает массу пробы в граммах."]
        self.assertFalse(self.check(self.neutral, test, outcomes=outcomes))
        self.assertFalse(self.check("В каком источнике хранится масса пробы в граммах?"))
        self.assertFalse(self.check("В какой единице весы передают массу пробы: в граммах или килограммах?"))

    def test_real_input_declaration_can_specify_its_own_representation(self):
        question = "Из какого датчика станция получает массу пробы в граммах?"
        self.assertFalse(self.check(question, sources=["Входной пакет содержит массу пробы в граммах."]))
        self.assertTrue(self.check(question, sources=["Входной пакет содержит массу тары в граммах."]))
        self.assertTrue(self.check(question, sources=["Входной пакет содержит массу пробы в килограммах."]))

    def test_an_open_unit_question_may_illustrate_different_wire_encodings(self):
        question = "В какой единице станция получает массу пробы?"
        self.assertFalse(self.check(question, outcomes=["Станция получает массу пробы в граммах.",
                                                        "Станция получает массу пробы в килограммах."]))
        self.assertTrue(self.check(question, outcomes=["Станция получает массу пробы в граммах из пакета.",
                                                       "Станция получает массу пробы в граммах из справочника."]))

    def test_a_partial_quote_can_inherit_the_storage_operation_from_its_own_block(self):
        blocks = [SimpleNamespace(id="B1", text="Хранить код заказа, сумму услуги в центах и состояние оплаты.")]
        claims = [dict(id="R1", block="B1", quote="Хранить код заказа"),
                  dict(id="R2", block="B1", quote="сумму услуги в центах")]
        scopes = storage_units(blocks, claims)
        selected = dict(ids=["R2"], question="Как терминал получает сумму услуги в центах?", test="")
        self.assertTrue(data_boundary_error(selected, scopes))
        self.assertFalse(data_boundary_error(dict(selected, ids=["unrelated"]), scopes))

    def test_measurement_unit_in_english_is_not_assigned_to_the_sensor(self):
        scopes = rules("Store duration in milliseconds.", "The sensor sends a reading.")
        item = dict(ids=["RB0"], question="Which input carries duration in milliseconds?", test="")
        self.assertTrue(data_boundary_error(item, scopes))
        item["question"] = "Which input carries duration?"
        item["test"] = "Read the sensor and verify stored duration in milliseconds."
        self.assertFalse(data_boundary_error(item, scopes))
