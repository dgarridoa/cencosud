from cencosud.question_1.random_generator import HumanResourcesGenerator
from cencosud.question_1.human_resources import HumanResources


class TestHumanResources:
    hrg = HumanResourcesGenerator()
    hrg.sample()
    hr = HumanResources()
    hr.create_populated_db(hrg)

    def test_get_avg_children_per_marriage(self):
        assert self.hr.get_avg_children_per_marriage() == 2.4

    def test_get_person_with_max_number_grandchildren(self):
        person_id = self.hr.get_person_with_max_number_grandchildren()["id"]
        assert (person_id == 768)
