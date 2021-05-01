"""
Module with repositories to be used connected with api.
"""

from py_easy_rest import PYRApplicationError


class DatabaseError(PYRApplicationError):
    """
    Error to raise in case of database errors.
    """

    pass


class Repo():
    """
    Interface to define contract to repositories.
    All methods raises an <DatabaseError> in case of error.
    """

    async def get(self, slug, id):
        """
        Receives <slug> and <id> and return a dictionary with the result.
        If it not found a data with this <id>, return None.
        """
        raise NotImplementedError

    async def list(self, slug, page=0, size=30):
        """
        Receives <slug>, <page> and <size> and return a object with the result, page and size.
        It's possible to put other properties in this result object too.
        If result is empty, return a empty list.
        """
        raise NotImplementedError

    async def create(self, slug, data, id=None):
        """
        Receives <slug> and <data> with the resource to be saved,
        save it into db, and return the resource id.
        If receive <id>, set this id to the document and return this id.
        """
        raise NotImplementedError

    async def replace(self, slug, id, data):
        """
        Receives <slug> and <data> with the resource to be saved and <id>,
        replace the resource in db.
        """
        raise NotImplementedError

    async def delete(self, slug, id):
        """
        Receives <slug> and <id> and delete it from db.
        """
        raise NotImplementedError
