import time
import mysql.connector


class HumanResources:
    """
    This class manage human resources data in a relational database.

    Create a conection with a MySQL database.

    Attributes
    ----------
    conection : MySQLConnection
        Object that open a conetion to a MySQL database.
    """

    def __init__(self, max_timeout=60, acc=0):
        try:
            conection = mysql.connector.connect(
                host="mysqldb",
                user="root",
                password="secret",
                connect_timeout=100
            )
            self.conection = conection
        except mysql.connector.errors.DatabaseError as error:
            if acc > max_timeout:
                raise error

            time.sleep(10)
            acc += 10
            self.__init__(max_timeout, acc)

    def create_db(self):
        "Create the databse hhrr to stores human resources data."
        cursor = self.conection.cursor()
        cursor.execute("DROP DATABASE IF EXISTS hhrr")
        cursor.execute("CREATE DATABASE hhrr")
        cursor.close()

        return "init database"

    def create_tbl_personas(self):
        "Create the table personas in the database hhrr."
        cursor = self.conection.cursor()
        cursor.execute("DROP TABLE IF EXISTS hhrr.personas")
        cursor.execute("""
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
        cursor.close()
        return "tbl personas"

    def create_tbl_conyuges(self):
        "Create the table conyuge in the database hhrr."
        cursor = self.conection.cursor()
        cursor.execute("DROP TABLE IF EXISTS hhrr.conyuge")
        cursor.execute("""
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
        cursor.close()
        return "tbl conyuges"

    def create_tbl_hijos(self):
        "Create the table hijos in the database hhrr."
        cursor = self.conection.cursor()
        cursor.execute("DROP TABLE IF EXISTS hhrr.hijos")
        cursor.execute("""
        CREATE TABLE hhrr.hijos(
          id INT,
          id_padre INT,
          id_hijo INT,
          PRIMARY KEY (id),
          FOREIGN KEY (id_padre) REFERENCES hhrr.personas(id),
          FOREIGN KEY (id_hijo) REFERENCES hhrr.personas(id)
        )
        """)
        cursor.close()
        return "tbl hijos"

    def truncate_db(self, sample):
        """
        Truncate hhrr tables with new data.

        Parameters
        ----------
        sample: HumanResourcesGenerator
            Object with random data for all tables in hhrr.
        """

        cursor = self.conection.cursor()
        cursor.execute("DELETE FROM hhrr.conyuges")
        cursor.execute("DELETE FROM hhrr.hijos")
        cursor.execute("DELETE FROM hhrr.personas")

        cursor.executemany("""
        INSERT INTO hhrr.personas (id, nombre, rut, dv, nacimiento, defuncion)
        VALUES (
        %(id)s, %(nombre)s, %(rut)s, %(dv)s, %(nacimiento)s, %(defuncion)s)
        """, sample.personas)

        cursor.executemany("""
        INSERT INTO hhrr.conyuges (id, id_persona_1, id_persona_2, celebracion)
        VALUES (%(id)s, %(id_persona_1)s, %(id_persona_2)s, %(celebracion)s)
        """, sample.conyuges)

        cursor.executemany("""
        INSERT INTO hhrr.hijos (id, id_padre, id_hijo)
        VALUES (%(id)s, %(id_padre)s, %(id_hijo)s)
        """, sample.hijos)

        self.conection.commit()

        cursor.close()

        return "db populated"

    def create_random_db(self, sample):
        """
        Create the hhrr database and populate it with random data.

        Parameters
        ----------
        sample: HumanResourcesGenerator
            Object with random data for all tables in hhrr.
        """
        self.create_db()
        self.create_tbl_personas()
        self.create_tbl_conyuges()
        self.create_tbl_hijos()
        self.truncate_db(sample)
        return "random db created"

    def get_avg_children_per_marriage(self):
        """
        Get the average number of children per marriage.

        Returns
        -------
        result: float
            Average number of children per marriage.
        """
        cursor = self.conection.cursor()
        cursor.execute("""
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
        result = float(cursor.fetchall()[0][0])
        cursor.close()
        return result

    def get_person_with_max_number_grandchildren(self):
        """
        Get the person with the maximum number of grandchildren.
        Return
        -------
        result: dit
            Dictionary with the data of the person with the maximum number of
            grandchildren.
        """
        cursor = self.conection.cursor()
        cursor.execute("""
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
            cursor.fetchall()[0]))
        cursor.close()
        return result
