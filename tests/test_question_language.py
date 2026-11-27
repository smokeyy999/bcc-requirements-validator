import unittest

from requirements_validator.question_language import question_language_error


def review(question, *facts):
    claims = {str(i): text for i, text in enumerate(facts)}
    finding = {"question": question, "ids": list(claims)}
    return question_language_error(finding, claims)


class QuestionLanguageTests(unittest.TestCase):
    def test_singular_attributes_each_keep_their_own_agreement(self):
        self.assertTrue(review("В каких единице и формате поступает длительность?"))
        self.assertTrue(review("В каких кодировке и формате сервис передаёт текст?"))
        self.assertFalse(review("В какой единице и в каком формате поступает длительность?"))
        self.assertFalse(review("В каких форматах и кодировках сервис передаёт текст?"))
        self.assertFalse(review("Нужно ли изменить строку «В каких единице и формате»?"))

    def test_fronted_object_is_not_the_actor_of_the_request(self):
        rule = "Приложение читает и сохраняет настройки через интерфейс."
        self.assertIn("должно", review("Какой HTTP-метод должен вызывать приложение для сохранения?", rule))
        self.assertEqual(review("Какой HTTP-метод должно вызывать приложение для сохранения?", rule), "")
        self.assertEqual(review("Каким методом приложение должно вызывать операцию сохранения?", rule), "")

    def test_other_actor_genders_and_plural(self):
        for actor, correct, wrong in (("устройство", "должно", "должен"), ("станция", "должна", "должны"),
                                      ("терминал", "должен", "должна"), ("клиенты", "должны", "должно")):
            for modal, rejected in ((correct, False), (wrong, True)):
                with self.subTest(actor=actor, modal=modal):
                    self.assertEqual(bool(review(f"Когда {actor} {modal} использовать резервный канал?")), rejected)
        self.assertIn("должна", review("Какой канал должен выбрать станция?", "Станция выбирает канал связи."))

    def test_both_directions_of_a_call_can_be_real(self):
        q = "Какой метод должен вызывать приложение при запуске?"
        self.assertEqual(review(q, "Метод вызывает приложение при запуске."), "")
        self.assertEqual(review(q, "Приложение использует интерфейс.", "При запуске метод вызывает приложение."), "")
        self.assertEqual(review(q, "Приложение читает данные.", "Метод обратного вызова вызывает приложение."), "")
        self.assertEqual(review(q, "Приложение читает данные.", "Приложение вызывается внешним методом."), "")
        self.assertEqual(review(q, "Приложение вызывается после запуска."), "")
        self.assertEqual(review(q, "Таблица описывает доступные команды."), "")

    def test_quoted_grammar_and_contextual_subjects(self):
        source = "Приложение вызывает операцию передачи."
        self.assertEqual(review("Нужно ли исправить текст «Какой метод должен вызывать приложение?»?", source), "")
        self.assertEqual(review("Какой запрос через приложение должен отправить клиент?", source), "")
        self.assertEqual(review("How should the application call the service?", source), "")
        self.assertEqual(question_language_error(None, {}), "")
        self.assertEqual(review("", source), "")

    def test_only_supporting_claims_can_identify_the_actor(self):
        q = "Какой метод должен вызывать приложение?"
        claims = {"A": "Приложение запрашивает данные.", "B": "Параметр обязателен."}
        self.assertEqual(question_language_error({"question": q, "ids": ["B"]}, claims), "")
        f = {"question": q, "ids": ["B"], "question_basis": {"checked_ids": ["A"]}}
        self.assertIn("должно", question_language_error(f, claims))
