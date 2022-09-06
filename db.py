from datetime import datetime
from functools import singledispatch
from pathlib import Path
import logging

from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    delete,
    select,
    update,
    tuple_,
)


Base = declarative_base()

logging.basicConfig()
logger = logging.getLogger(__name__)


class TextField(Base):
    __tablename__ = 'textfield'

    key = Column(String, primary_key=True)
    entry_id = Column(String, ForeignKey('entry.id'), primary_key=True)
    value = Column(String)
    rune = Column(String)
    entry = relationship("Entry", back_populates='fields')


class Entry(Base):
    __tablename__ = 'entry'

    id = Column(String, primary_key=True)
    created = Column(DateTime(timezone=True))
    updated = Column(DateTime(timezone=True))
    deleted = Column(Boolean, default=False)
    fields = relationship('TextField', back_populates='entry')



@singledispatch
def to_dict(arg: object):
    raise ValueError("to_dict not implemented for %s" % arg)


@to_dict.register
def _to_dict(entry: Entry, full=False):
    return {
        'id': entry.id,
        'created': entry.created,
        'updated': entry.updated,
        'deleted': entry.deleted,
        **(
            {
                "text_fields": [
                    to_dict(field)
                    for field in entry.fields
                ]
            } if full else {}
        )
    }


@to_dict.register
def _to_dict(text_field: TextField):
    return {
        'rune': text_field.rune,
        'key': text_field.key,
        'value': text_field.value,
    }


def get_engine(path: Path):
    logger.info("loading or creating db at %s", path)
    engine = create_engine(f'sqlite+pysqlite:///{path}')
    logger.info("loading models")
    Base.metadata.create_all(engine)
    logger.info("database ready")
    return engine


def get_entry(engine, entry_id):
    with Session(engine) as session:
        # get the entry or create it
        entry = session.execute(
            select(Entry).where(Entry.id == entry_id)
        ).scalars().one_or_none() or Entry(
            id=entry_id,
            created=datetime.now(),
            updated=datetime.now()
        )
        # session.add(entry)
        # session.commit()
        return to_dict(entry, full=True)


def get_entries(engine):
    with Session(engine) as session:
        entries = session.execute(select(Entry))
        return [
            to_dict(entry[0])
            for entry in entries
        ]


def get_entry_fields(engine, entry_id):
    with Session(engine) as session:
        return [
            to_dict(field)
            for field in
            session.query(TextField).query(entry_id=entry_id)
        ]


def save_entry(engine, data):
    with Session(engine) as session:
        entry = session.execute(
            select(Entry)
            .where(Entry.id == data['id'])
        ).scalars().one_or_none() or Entry(
            id=data['id'],
            created=datetime.now(),
            updated=datetime.now(),
        )
        existing_fields = {field.key for field in entry.fields}  # TODO add sth for multiple key values?
        update_fields = {field['key'] for field in data['text_fields']}  # TODO add sth for multiple key values?

        to_create = update_fields - existing_fields
        to_delete = existing_fields - update_fields
        to_update = update_fields - to_create

        session.execute(
            delete(TextField)
            .where(
                (TextField.entry_id == data['id'])
                & tuple_(TextField.key, TextField.rune).in_(to_delete)
            )
            .execution_options(synchronize_session="fetch")
        )

        session.add_all([
            TextField(rune=item["rune"], key=item["key"], value=item["value"], entry=entry)
            for item in data['text_fields'] if item["key"] in to_create  # TODO add sth for multiple key values?
        ])

        for field in data["text_fields"]:
            if field["key"] not in to_update:
                continue
            session.execute(
                update(TextField)
                .where(
                    (TextField.key == field["key"])  # TODO add sth for multiple key values?
                    & (TextField.entry_id == data["id"])
                )
                .values(value=field["value"])
                .execution_options(synchronize_session="fetch")
            )

        session.commit()


def delete_entry(engine, entry_id, hard=False):
    with Session(engine) as session:
        entry = session.query(Entry).filter_by(id=entry_id).scalars().one_or_none()
        if entry:
            if hard:
                session.execute(Entry.delete().where(Entry.entry_id == entry_id))
            else:
                entry.deleted = True
            session.commit()
        else:
            session.rollback()
