from typing import List
from extensions import db
from flask import abort

from models.bruker import Bruker


class Kommentar:
    def __init__(self,
                 id: int = None,
                 innhold: int = None,
                 dato: str = None,
                 brukernavn: str = None,
                 innlegg_id: int = None):
        self.id = id
        self.innhold = innhold
        self.dato = dato
        self.brukernavn = brukernavn
        self.innlegg_id = innlegg_id
        self._bruker = None

    @property
    def bruker(self) -> Bruker:
        if not self._bruker:
            self._bruker = Bruker.get_user(self.brukernavn)
        return self._bruker

    @staticmethod
    def get_all(innlegg_id: int) -> List["Kommentar"]:
        query = """
        select 
            kommentar_id, kommentar_innhold, kommentar_dato, bruker_navn, innlegg_id
        from kommentar
        where innlegg_id = %s
        order by kommentar_dato
        """
        db.cursor.execute(query, (innlegg_id,))
        result = [Kommentar(*x) for x in db.cursor.fetchall()]
        return result

    @staticmethod
    def get_kommentar(kommentar_id: int) -> "Kommentar":
        query = """
        select 
            kommentar_id, kommentar_innhold, kommentar_dato, bruker_navn, innlegg_id
        from kommentar
        where kommentar_id = %s
        """
        db.cursor.execute(query, (kommentar_id,))
        result = db.cursor.fetchone()
        if result:
            return Kommentar(*result)
        else:
            abort(404)

    def insert_kommentar(self) -> "Kommentar":
        query = """
        insert into kommentar(kommentar_innhold, bruker_navn, innlegg_id )
        values(%s, %s, %s) 
        """
        db.cursor.execute(query, (self.innhold, self.brukernavn, self.innlegg_id))
        db.connection.commit()
        return self.get_kommentar(db.cursor.lastrowid)

    def delete_kommentar(self):
        query = """ 
        delete from kommentar
        where kommentar_id = %s"""
        db.cursor.execute(query, (self.id,))
        db.connection.commit()
