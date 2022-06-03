import os
from pydantic import BaseModel, PrivateAttr, NonNegativeInt
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Engine
from cencosud.question_1.random_generator import HumanResourcesGenerator


class HumanResources(BaseModel):
    """
    This class manage human resources data in a relational database.

    Create a conection with a MySQL database.

    Parameters
    ----------
    conection : MySQLConnection
        Object that open a conetion to a MySQL database.
    """
    timeout: NonNegativeInt = 60
    _engine: Engine = PrivateAttr()

    def __init__(self, **data) -> None:
        super().__init__(**data)
        username = os.environ["MYSQL_USER"]
        password = os.environ["MYSQL_PASSWORD"]
        host = os.environ["MYSQL_HOST"]
        port = os.environ["MYSQL_PORT"]

        self._engine = create_engine(
            url=f"mysql+pymysql://{username}:{password}@{host}:{port}",
            connect_args={"connect_timeout": self.timeout}
        )

    def create_db(self) -> None:
        "Create the databse hhrr to stores human resources data."
        with self._engine.begin() as conn:
            conn.execute("DROP DATABASE IF EXISTS hhrr")
            conn.execute("CREATE DATABASE hhrr")

    def create_tbl_personas(self) -> None:
        "Create the table personas in the database hhrr."
        with self._engine.begin() as conn:
            conn.execute("DROP TABLE IF EXISTS hhrr.personas")
            conn.execute("""
            CREATE TABLE hhrr.personas(
              id INT,
              nombre VARCHAR(100),
              rut INT,
              dv CHAR(1),
              nacimiento DATE NOT NULL,
              defuncion DATE,
              PRIMARY KEY (id)
            )
            """)

    def create_tbl_conyuges(self) -> None:
        "Create the table conyuge in the database hhrr."
        with self._engine.begin() as conn:
            conn.execute("DROP TABLE IF EXISTS hhrr.conyuge")
            conn.execute("""
            CREATE TABLE hhrr.conyuges(
              id INT,
              id_persona_1 INT,
              id_persona_2 INT,
              celebracion DATE NOT NULL,
              PRIMARY KEY (id),
              FOREIGN KEY (id_persona_1) REFERENCES hhrr.personas(id),
              FOREIGN KEY (id_persona_2) REFERENCES hhrr.personas(id)
            )
            """)

    def create_tbl_hijos(self) -> None:
        "Create the table hijos in the database hhrr."
        with self._engine.begin() as conn:
            conn.execute("DROP TABLE IF EXISTS hhrr.hijos")
            conn.execute("""
            CREATE TABLE hhrr.hijos(
              id INT,
              id_padre INT,
              id_hijo INT,
              PRIMARY KEY (id),
              FOREIGN KEY (id_padre) REFERENCES hhrr.personas(id),
              FOREIGN KEY (id_hijo) REFERENCES hhrr.personas(id)
            )
            """)

    def truncate_db(self, sample: HumanResourcesGenerator) -> None:
        """
        Truncate hhrr tables with new data.

        Parameters
        ----------
        sample : HumanResourcesGenerator
            Object with data for all tables in hhrr.
        """
        with self._engine.begin() as conn:
            conn.execute("DELETE FROM hhrr.conyuges")
            conn.execute("DELETE FROM hhrr.hijos")
            conn.execute("DELETE FROM hhrr.personas")

            conn.execute(
                text("""
                  INSERT INTO hhrr.personas (id, nombre, rut, dv,
                    nacimiento, defuncion)
                  VALUES (:id, :nombre, :rut, :dv, :nacimiento, :defuncion)
                  """),
                sample.personas)

            conn.execute(
                text("""
                  INSERT INTO hhrr.conyuges (id, id_persona_1, id_persona_2,
                    celebracion)
                  VALUES (:id, :id_persona_1, :id_persona_2, :celebracion)
                  """),
                sample.conyuges)

            conn.execute(
                text("""
                  INSERT INTO hhrr.hijos (id, id_padre, id_hijo)
                  VALUES (:id, :id_padre, :id_hijo)
                  """),
                sample.hijos)

    def create_populated_db(self, sample: HumanResourcesGenerator) -> None:
        """
        Create the hhrr database and populate it with sample.

        Parameters
        ----------
        sample : HumanResourcesGenerator
            Object with data for all tables in hhrr.
        """
        self.create_db()
        self.create_tbl_personas()
        self.create_tbl_conyuges()
        self.create_tbl_hijos()
        self.truncate_db(sample)

    def get_avg_children_per_marriage(self) -> float:
        """
        Get the average number of children per marriage.

        Returns
        -------
        result : float
            Average number of children per marriage.
        """
        with self._engine.connect() as conn:
            result = conn.execute("""
            WITH
              first_parent AS (
                SELECT
                  c.id,
                  c.id_persona_1,
                  c.id_persona_2,
                  h.id_hijo
                FROM hhrr.conyuges AS c
                INNER JOIN hhrr.hijos AS h
                ON c.id_persona_1 = h.id_padre),
              second_parent AS (
                SELECT
                  c.id,
                  c.id_persona_1,
                  c.id_persona_2,
                  h.id_hijo
                FROM hhrr.conyuges AS c
                INNER JOIN hhrr.hijos AS h
                ON c.id_persona_2 = h.id_padre),
              marriages_and_children AS (
                SELECT
                  fp.id,
                  fp.id_hijo
                FROM first_parent AS fp
                INNER JOIN second_parent AS sp
                ON fp.id_persona_1 = sp.id_persona_1
                  AND fp.id_persona_2 = sp.id_persona_2
                  AND fp.id_hijo = sp.id_hijo),
              count_children_by_marriage AS (
                SELECT
                  id,
                  count(*) AS num_children
                FROM marriages_and_children
                GROUP BY id
              )
            SELECT
              AVG(IFNULL(chbm.num_children, 0)) avg_per_marriage
            FROM hhrr.conyuges AS c
            LEFT JOIN count_children_by_marriage AS chbm
            ON c.id = chbm.id
            """)
        return float(result.all()[0][0])

    def get_person_with_max_number_grandchildren(self) -> dict:
        """
        Get the person with the maximum number of grandchildren.

        Return
        -------
        result : dit
            Dictionary with the data of the person with the maximum number of
            grandchildren.
        """

        with self._engine.connect() as conn:
            result = conn.execute("""
            WITH
              count_grandchildren_by_person AS (
                SELECT
                  grandparents.id_padre,
                  count(*) AS num_grandchildren
                FROM hhrr.hijos AS grandparents
                INNER JOIN hhrr.hijos AS parents
                ON grandparents.id_hijo = parents.id_padre
                GROUP BY grandparents.id_padre),
              person_with_max_number_grandchildren AS (
                SELECT
                    id_padre
                FROM count_grandchildren_by_person
                WHERE num_grandchildren = (
                  SELECT
                    MAX(num_grandchildren)
                  FROM count_grandchildren_by_person)
                LIMIT 1)
            SELECT *
            FROM hhrr.personas
            WHERE id = (
              SELECT id_padre
              FROM person_with_max_number_grandchildren)
            """)
            result = dict(zip(
                ("id", "nombre", "rut", "dv", "nacimiento", "defuncion"),
                result.all()[0]))
        return result
