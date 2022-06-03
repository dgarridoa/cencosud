import string
import numpy as np
from datetime import datetime, timedelta


class HumanResourcesGenerator:
    """
    Class useful to generate random data to populate a database with the
    tables personas (people), conyuges (marriages) and hijos (children).

    Parameters
    ----------
    n_personas : int
        Number of people to sample.
    n_conyuges : int
        Number of marriages to sample.
    n_hijos : int
        Number of children to sample.
    min_date : datetime
        Minimum random date.
    max_date : datetime
        Maximum random date.
    seed : int
        Random seed.
    personas: list of dict, default=[]
        A list of random people.
    conyuges: list of dict, default=[]
        A list of random marriages.
    hijos: list of dict, default=[]
        A list of random children.

    Examples
    --------
    >>> hrg = HumanResouresGenerator()
    >>> hrg.sample()
    >>> hrg.personas
    [{"id": 0, "nombre": "pvadd", "nacimiento": "1952-05-17",
      "defuncion": "2006-10-22"}, ...]
    >>> hrg.conyuges
    [{"id": 0, "id_persona_1": 10, "id_persona_2": 167,
      "celebracion": "1936-04-04"}, ...]
    >>> hrg.hijos
    [{"id": 0, "id_padre": 262, "id_hijo": 328},
     {"id": 1, "id_padre": 889, "id_hijo": 328}, ...]
    """
    def __init__(
        self,
        n_personas=1000,
        n_conyuges=50,
        n_hijos=120,
        min_date=datetime(1900, 1, 1),
        max_date=datetime(2022, 1, 1),
        seed=0
    ):
        self.n_personas = n_personas
        self.n_conyuges = n_conyuges
        self.n_hijos = n_hijos
        self.min_date = min_date
        self.max_date = max_date
        self.seed = seed
        self.personas = []
        self.conyuges = []
        self.hijos = []

    def _sample_date(self, min_date, max_date):
        """
        Sample random date between min_date and max_date.

        Parameters
        ----------
        min_date : datetime
            Minimum date to be sampled.
        max_date : datetime
            Maximum date to be sampled.

        Returns
        -------
        random_date : str,
            Random date in format "yyyy-mm-dd".
        """
        time_delta = max_date - min_date
        days = np.random.choice(range(0, time_delta.days + 1))
        seconds = np.random.choice(range(0, time_delta.seconds + 1))
        microseconds = np.random.choice(range(0, time_delta.microseconds + 1))

        random_delta = timedelta(int(days), int(seconds), int(microseconds))
        random_date = min_date + random_delta
        random_date = str(random_date.date())

        return random_date

    def _sample_death_date(self, str_birth_date, max_date):
        """
        Sample random death date.

        Add to the birth_date a random time delta that follow a normal
        distribution with mean 80 year and standard deviation 10 year.

        Parameters
        ----------
        str_brith_date : str
          birth date in format "yyyy-mm-dd".
        max_date : datetime
          The random date is set to None if is greather than max_date.

        Returns
        -------
        death_date : str or None
            A random date in format "yyyy-mm-dd" if is not greather than
            max_date else None.
        """
        birth_date = datetime.strptime(str_birth_date, "%Y-%m-%d")
        death_date = birth_date + timedelta(int(np.random.normal(80, 10)*365))

        if max_date < death_date:
            death_date = None
        else:
            death_date = str(death_date.date())

        return death_date

    def _sample_celebration_date(self, persona_1, persona_2, max_date):
        """
        Samples random marriage celebration date.

        Parameters
        ----------
        persona_1 : dict
          A row in table persona with shape {column_name : column_value}.
        persona_2 : dict
          A row in table persona with shape {column_name : column_value}.
        max_date : str
          The maximum possible celebration date.

        Returns
        -------
        celebration_date : str or None
           Random marraige celebration date in format "yyyy-mm-dd".
           The date is generated from the sample of dates where both are 18
           older, both are alive and before max_date, otherwise None.
        """
        start_date_1 = datetime.strptime(persona_1["nacimiento"], "%Y-%m-%d")
        start_date_2 = datetime.strptime(persona_2["nacimiento"], "%Y-%m-%d")
        start_date = max(start_date_1, start_date_2) + timedelta(18*365)

        if not persona_1["defuncion"] and not persona_2["defuncion"]:
            end_date = max_date
        elif persona_1["defuncion"] and not persona_2["defuncion"]:
            end_date = datetime.strptime(persona_1["defuncion"], "%Y-%m-%d")
        elif not persona_1["defuncion"] and persona_2["defuncion"]:
            end_date = datetime.strptime(persona_2["defuncion"], "%Y-%m-%d")
        else:
            end_date_1 = datetime.strptime(persona_1["defuncion"], "%Y-%m-%d")
            end_date_2 = datetime.strptime(persona_2["defuncion"], "%Y-%m-%d")
            end_date = min(end_date_1, end_date_2)

        if start_date < end_date:
            celebration_date = self._sample_date(start_date, end_date)
        else:
            celebration_date = None

        return celebration_date

    def _sample_name(self):
        """
        Samples random name of lenth within [2, 100].
        """
        lenght = np.random.randint(2, 101)
        tokens = list(string.ascii_lowercase + " ")
        name = "".join(np.random.choice(tokens, lenght))
        return name

    def _sample_personas(self):
        """
        Fill .personas atribute with a sample of random people.

        The dict structure is the following:
            - id: int, integer number between [0, self.n_personas).
            - nombre: str, string of length [2, 100] with chars in a-z + " ".
            - rut: int, integer number between [0, 2**31].
            - dv: str, a char in "123456789k".
            - nacimiento: str, a date in format "yyyy-mm-dd".
            - defuncion: str or None, a date in format "yyyy-mm-dd".

        Returns
        -------
        self : object
          Replace self.personas with a list of random dicts with the following
          keys [id, nombre, rut, dv, nacimiento, defuncion].
        """
        data = []
        for i in range(self.n_personas):
            row = {}

            row["id"] = i
            row["nombre"] = self._sample_name()
            row["rut"] = np.random.randint(2**31)
            row["dv"] = np.random.choice(list("123456789k"))
            row["nacimiento"] = self._sample_date(self.min_date, self.max_date)
            row["defuncion"] = self._sample_death_date(row["nacimiento"],
                                                       self.max_date)

            data.append(row)
        self.personas = data
        return self

    def _sample_conyuges(self):
        """
        Fill .conyuges atribute with a sample of random marriages.

        The dict structure is the following:
            - id: int, integer number between [0, self.n_conyuges).
            - id_persona_1: int, integer number between [0, self.n_personas).
            - id_persona_2: int, integer number between [0, self.n_personas).
            - celebracion: str, a date in format "yyyy-mm-dd".

        Returns
        -------
        self : object
          Replace self.conyuges with a list of random dicts with the following
          keys [id, id_persona_1, id_persona_2, celebracion].
        """
        data = []
        i = 0
        while i < self.n_conyuges:
            persona_1, persona_2 = np.random.choice(
                self.personas, 2, replace=False)

            row = {}
            row["id"] = i
            row["id_persona_1"] = persona_1["id"]
            row["id_persona_2"] = persona_2["id"]
            row["celebracion"] = self._sample_celebration_date(
                persona_1, persona_2, self.max_date)

            # add if it is feasible to have a marriage
            if row["celebracion"]:
                data.append(row)
                i += 1

        self.conyuges = data
        return self

    def _sample_hijos(self):
        """
        Fill .hijos atribute with a sample of random children.

        The dict structure is the following:
            - id: int, integer number between [0, self.n_hijos).
            - id_padre: int, integer number between [0, self.n_personas).
            - id_hijo: int, integer number between [0, self.n_personas).

        Returns
        -------
        self : object
          Replace self.hijos with a list of random dicts with the following
          keys [id, id_padre, id_hijo].
        """

        i = 0
        data = []
        while i < 2*self.n_hijos:
            conyuges = np.random.choice(self.conyuges)
            hijo = np.random.choice(self.personas)

            # add if it is feasible to have a child
            if hijo["nacimiento"] > conyuges["celebracion"]:
                data.append({"id": i,
                             "id_padre": conyuges["id_persona_1"],
                             "id_hijo": hijo["id"]})
                data.append({"id": i + 1,
                             "id_padre": conyuges["id_persona_2"],
                             "id_hijo": hijo["id"]})
                i += 2

        self.hijos = data
        return self

    def sample(self):
        """
        Fill atributes .personas, .conyuges and .hijos with random data.

        Returns
        -------
        self : object
        """
        np.random.seed(self.seed)
        self._sample_personas()
        self._sample_conyuges()
        self._sample_hijos()
        return self
