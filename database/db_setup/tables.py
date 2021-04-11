from extensions import db
from mysql.connector import errorcode, Error
from flask import current_app

TABLES = {}

TABLES["brukere"] = """
CREATE TABLE `brukere` (
  `bruker_navn` VARCHAR(24) NOT NULL,
  `bruker_epost` VARCHAR(45) NOT NULL,
  `bruker_passord_hash` VARCHAR(45) NOT NULL,
  `bruker_opprettet` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `bruker_fornavn` VARCHAR(45) NOT NULL,
  `bruker_etternavn` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`bruker_navn`),
  UNIQUE INDEX `bruker_navn_UNIQUE` (`bruker_navn` ASC))
ENGINE = InnoDB
"""

TABLES["blog"] = """
CREATE TABLE `blog` (
  `blog_navn` VARCHAR(20) NOT NULL,
  `blog_tittel` VARCHAR(45) NOT NULL,
  `brukere_bruker_navn` VARCHAR(24) NOT NULL,
  `blog_opprettet` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`blog_navn`, `brukere_bruker_navn`),
  UNIQUE INDEX `blog_navn_UNIQUE` (`blog_navn` ASC),
  INDEX `fk_blog_brukere_idx` (`brukere_bruker_navn` ASC),
  CONSTRAINT `fk_blog_brukere`
    FOREIGN KEY (`brukere_bruker_navn`)
    REFERENCES `brukere` (`bruker_navn`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
"""

TABLES["innlegg"] = """
CREATE TABLE `innlegg` (
  `innlegg_id` INT NOT NULL AUTO_INCREMENT,
  `innlegg_tittel` VARCHAR(100) NOT NULL,
  `innlegg_innhold` TEXT NOT NULL,
  `innlegg_dato` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `innlegg_endret` DATETIME NULL,
  `innlegg_treff` INT NULL DEFAULT 0,
  `blog_blog_navn` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`innlegg_id`, `blog_blog_navn`),
  UNIQUE INDEX `innlegg_id_UNIQUE` (`innlegg_id` ASC),
  INDEX `fk_innlegg_blog1_idx` (`blog_blog_navn` ASC),
  CONSTRAINT `fk_innlegg_blog1`
    FOREIGN KEY (`blog_blog_navn`)
    REFERENCES `blog` (`blog_navn`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB
"""

TABLES["kommentarer"] = """
CREATE TABLE `kommentarer` (
  `kommentar_id` INT NOT NULL AUTO_INCREMENT,
  `kommentar_innhold` TINYTEXT NULL,
  `bruker_navn` VARCHAR(24) NOT NULL,
  `innlegg_id` INT NOT NULL,
  PRIMARY KEY (`kommentar_id`, `bruker_navn`, `innlegg_id`),
  INDEX `fk_kommentarer_brukere1_idx` (`bruker_navn` ASC),
  INDEX `fk_kommentarer_innlegg1_idx` (`innlegg_id` ASC),
  UNIQUE INDEX `kommentar_id_UNIQUE` (`kommentar_id` ASC),
  CONSTRAINT `fk_kommentarer_brukere1`
    FOREIGN KEY (`bruker_navn`)
    REFERENCES `brukere` (`bruker_navn`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_kommentarer_innlegg1`
    FOREIGN KEY (`innlegg_id`)
    REFERENCES `innlegg` (`innlegg_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
"""

TABLES["tagger"] = """
CREATE TABLE `tagger` (
  `tag_navn` VARCHAR(45) NOT NULL,
  `innlegg_innlegg_id` INT NOT NULL,
  PRIMARY KEY (`innlegg_innlegg_id`, `tag_navn`),
  INDEX `fk_tagger_innlegg1_idx` (`innlegg_innlegg_id` ASC),
  CONSTRAINT `fk_tagger_innlegg1`
    FOREIGN KEY (`innlegg_innlegg_id`)
    REFERENCES `innlegg` (`innlegg_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
"""

TABLES["kommentar_logg"] = """
CREATE TABLE `kommentar_logg` (
  `kommentar_id` INT NOT NULL,
  `kommentar_innhold` TINYTEXT NULL,
  `bruker_navn` VARCHAR(24) NOT NULL,
  `innlegg_id` INT NOT NULL,
  `slettet_dato` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`kommentar_id`, `bruker_navn`, `innlegg_id`),
  INDEX `fk_kommentarer_brukere1_idx` (`bruker_navn` ASC),
  INDEX `fk_kommentarer_innlegg1_idx` (`innlegg_id` ASC),
  CONSTRAINT `fk_kommentarer_brukere10`
    FOREIGN KEY (`bruker_navn`)
    REFERENCES `brukere` (`bruker_navn`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_kommentarer_innlegg10`
    FOREIGN KEY (`innlegg_id`)
    REFERENCES `innlegg` (`innlegg_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
"""

TABLES["vedlegg"] = """
CREATE TABLE `vedlegg` (
  `vedlegg_id` INT NOT NULL AUTO_INCREMENT,
  `vedlegg_navn` VARCHAR(45) NOT NULL,
  `vedlegg_beskrivelse` VARCHAR(45) NULL,
  `vedlegg_path` VARCHAR(100) NULL,
  `innlegg_innlegg_id` INT NOT NULL,
  PRIMARY KEY (`vedlegg_id`, `innlegg_innlegg_id`),
  UNIQUE INDEX `vedlegg_id_UNIQUE` (`vedlegg_id` ASC),
  INDEX `fk_vedlegg_innlegg1_idx` (`innlegg_innlegg_id` ASC),
  CONSTRAINT `fk_vedlegg_innlegg1`
    FOREIGN KEY (`innlegg_innlegg_id`)
    REFERENCES `innlegg` (`innlegg_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
"""


def create_tables():
    cursor = db.connection.cursor()
    cursor.execute("USE {}".format(current_app.config['DATABASE_NAME']))
    for table_name, table_definition in TABLES.items():
        try:
            print(f"Creating table {table_name}: ", end='')
            cursor.execute(table_definition)
        except Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    cursor.close()
