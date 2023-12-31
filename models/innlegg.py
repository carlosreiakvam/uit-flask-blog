from datetime import datetime
from typing import List

from flask import abort, url_for
from mysql.connector import Error

from extensions import db
from models.blog import Blog
from models.bruker import Bruker
from models.kommentar import Kommentar
from models.tag import Tagger
from models.vedlegg import Vedlegg


class Innlegg:
    def __init__(self,
                 innlegg_id: int = None,
                 innlegg_tittel: str = None,
                 innlegg_innhold: str = None,
                 innlegg_dato: datetime = None,
                 innlegg_endret: datetime = None,
                 innlegg_treff: int = None,
                 blog_prefix: str = None,
                 blog_navn: str = None
                 ):
        self.innlegg_id = innlegg_id
        self.innlegg_tittel = innlegg_tittel
        self.innlegg_innhold = innlegg_innhold
        self.innlegg_dato = innlegg_dato
        self.innlegg_endret = innlegg_endret
        self.innlegg_treff = innlegg_treff
        self.blog_prefix = blog_prefix
        self.blog_navn = blog_navn
        self._kommentarer = None
        self._vedlegg = None
        self._tagger = None
        self._blog = None
        self._bruker = None

    @property
    def kommentarer(self) -> List[Kommentar]:
        if not self._kommentarer:
            self._kommentarer = Kommentar.get_all(self.innlegg_id)
        return self._kommentarer

    @property
    def tagger(self) -> List[Tagger]:
        if not self._tagger:
            self._tagger = Tagger.get_tags(self.innlegg_id)
        return self._tagger

    @property
    def vedlegg(self) -> List[Vedlegg]:
        if not self._vedlegg:
            self._vedlegg = Vedlegg.get_all(self.innlegg_id)
        return self._vedlegg

    @property
    def blog(self) -> Blog:
        if not self._blog:
            self._blog = Blog.get_one(self.blog_prefix)
        return self._blog

    @property
    def bruker(self) -> Bruker:
        if not self._bruker:
            self._bruker = Bruker.get_user_for_blog(self.blog_prefix)
        return self._bruker

    @property
    def url(self) -> str:
        return url_for("blog.vis_innlegg", blog_prefix=self.blog_prefix, innlegg_id=self.innlegg_id)

    @staticmethod
    def get_all(blog_navn: str) -> List["Innlegg"]:
        query = """
        select innlegg_id, 
               innlegg_tittel, 
               innlegg_innhold, 
               innlegg_dato, 
               innlegg_endret, 
               innlegg_treff,
               blog_prefix
        from innlegg where blog_prefix = %s and innlegg_dato > CURRENT_TIMESTAMP
        """

        db.cursor.execute(query, (blog_navn,))
        result = [Innlegg(*x) for x in db.cursor.fetchall()]
        return result

    @staticmethod
    def get_one(innlegg_id: int) -> "Innlegg":
        query = """
        select innlegg_id, 
               innlegg_tittel, 
               innlegg_innhold, 
               innlegg_dato, 
               innlegg_endret, 
               innlegg_treff,
               blog_prefix
        from innlegg where innlegg_id = %s
        """

        db.cursor.execute(query, (innlegg_id,))
        result = db.cursor.fetchone()
        if result:
            return Innlegg(*result)
        else:
            abort(404)

    @staticmethod
    def get_ten_newest() -> List["Innlegg"]:
        query = """
         select innlegg.innlegg_id, 
            innlegg_tittel, 
            innlegg_innhold, 
            innlegg_dato, 
            innlegg_endret, 
            innlegg_treff,
            innlegg.blog_prefix,
            blog.blog_navn
         from innlegg, blog where blog.blog_prefix = innlegg.blog_prefix order by innlegg_dato desc limit 10
         """

        db.cursor.execute(query)
        result = [Innlegg(*x) for x in db.cursor.fetchall()]
        return result

    @staticmethod
    def get_ten_most_hits() -> List["Innlegg"]:
        query = """
         select innlegg.innlegg_id, 
            innlegg_tittel, 
            innlegg_innhold, 
            innlegg_dato, 
            innlegg_endret, 
            innlegg_treff,
            innlegg.blog_prefix,
            blog.blog_navn
         from innlegg, blog where blog.blog_prefix = innlegg.blog_prefix order by innlegg_treff desc limit 10
         """

        db.cursor.execute(query)
        result = [Innlegg(*x) for x in db.cursor.fetchall()]
        return result

    @staticmethod
    def get_ten_most_commented() -> List["Innlegg"]:
        query = """
         select innlegg.innlegg_id, 
            innlegg_tittel, 
            innlegg_innhold, 
            innlegg_dato, 
            innlegg_endret, 
            innlegg_treff,
            innlegg.blog_prefix,
            blog.blog_navn
         from innlegg, kommentar, blog where blog.blog_prefix = innlegg.blog_prefix and innlegg.innlegg_id = kommentar.innlegg_id group by innlegg.innlegg_id order by COUNT(kommentar.kommentar_id) DESC limit 10
         """

        db.cursor.execute(query)
        result = [Innlegg(*x) for x in db.cursor.fetchall()]
        return result

    @staticmethod
    def update_hit(innlegg_id: int):
        query = """
        update innlegg set innlegg_treff=innlegg_treff+1 where innlegg_id = (%s);
        """
        db.cursor.execute(query, (innlegg_id,))
        db.connection.commit()

    @staticmethod
    def get_with_tag(tag_navn: str) -> List["Innlegg"]:
        query = """
        select innlegg.innlegg_id,
            innlegg_tittel,
            innlegg_innhold,
            innlegg_dato,
            innlegg_endret,
            innlegg_treff,
            innlegg.blog_prefix,
            blog.blog_navn
        from innlegg, blog, tag 
        where blog.blog_prefix = innlegg.blog_prefix 
            and tag.innlegg_id = innlegg.innlegg_id 
            and tag.tag_navn = %s order by innlegg_dato desc
        """
        db.cursor.execute(query, (tag_navn,))
        result = [Innlegg(*x) for x in db.cursor.fetchall()]
        return result

    @staticmethod
    def get_with_blog_prefix(blog_prefix: str) -> List["Innlegg"]:
        query = """
        select innlegg.innlegg_id,
            innlegg_tittel,
            innlegg_innhold,
            innlegg_dato,
            innlegg_endret,
            innlegg_treff,
            innlegg.blog_prefix,
            blog.blog_navn
        from innlegg 
            inner join blog on innlegg.blog_prefix = blog.blog_prefix 
        where blog.blog_prefix = %s 
        order by innlegg_dato desc 
        """
        db.cursor.execute(query, (blog_prefix,))
        result = [Innlegg(*x) for x in db.cursor.fetchall()]
        return result

    @staticmethod
    def search(search_string: str) -> List["Innlegg"]:
        query = """
        select innlegg.innlegg_id,
            innlegg_tittel,
            innlegg_innhold,
            innlegg_dato,
            innlegg_endret,
            innlegg_treff,
            innlegg.blog_prefix,
            blog.blog_navn
        from innlegg 
            inner join blog on innlegg.blog_prefix = blog.blog_prefix 
        where innlegg_innhold like CONCAT('%', %s, '%') 
           or innlegg_tittel like CONCAT('%', %s, '%') 
        """
        db.cursor.execute(query, (search_string, search_string))
        result = [Innlegg(*x) for x in db.cursor.fetchall()]
        return result

    def insert(self) -> "Innlegg":
        query = """
        insert into innlegg(innlegg_tittel, innlegg_innhold, blog_prefix)
        values (%s, %s, %s)
        """
        db.cursor.execute(query, (self.innlegg_tittel, self.innlegg_innhold, self.blog_prefix))
        db.connection.commit()

        return Innlegg.get_one(db.cursor.lastrowid)

    def update(self) -> "Innlegg":
        query = """
        update innlegg set innlegg_tittel = %s, innlegg_innhold = %s, innlegg_endret = CURRENT_TIMESTAMP
        where innlegg_id = %s
        """
        db.cursor.execute(query, (self.innlegg_tittel, self.innlegg_innhold, self.innlegg_id))
        db.connection.commit()

        return Innlegg.get_one(self.innlegg_id)

    def delete(self):
        query = """
        delete from innlegg 
        where innlegg_id = %s
        """
        delete_tags = """
        delete from tag
        where innlegg_id = %s
        """
        delete_comments = """
        delete from kommentar
        where innlegg_id = %s
        """
        delete_comment_log = """
        delete from kommentar_logg
        where innlegg_id = %s
        """
        try:
            db.cursor.execute(delete_tags, (self.innlegg_id,))
            db.cursor.execute(delete_comments, (self.innlegg_id,))
            db.cursor.execute(delete_comment_log, (self.innlegg_id,))
            db.cursor.execute(query, (self.innlegg_id,))
            db.connection.commit()
        except Error as err:
            db.connection.rollback()
            raise err

    def add_tag(self, tag_navn):
        tag = Tagger(tagnavn=tag_navn, innleggid=self.innlegg_id)
        tag.add_tag()

    def add_kommentar(self, kommentar_innhold, bruker_navn) -> Kommentar:
        kommentar = Kommentar(innhold=kommentar_innhold, brukernavn=bruker_navn, innlegg_id=self.innlegg_id)
        return kommentar.insert_kommentar()
