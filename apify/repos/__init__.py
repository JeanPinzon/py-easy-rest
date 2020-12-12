"""
Module with repositories to be used connected with api.
"""

class DatabaseError(Exception):
    """
    Error to raise in case of database errors.
    """

    def __init__(self, error_message, user_message=None, extra_params={}):
        self.error_message = error_message
        self.user_message = user_message
        self.extra_params = extra_params


class Repo():
    """
    Interface to define contract to repositories.
    All methods raises an <DatabaseError> in case of error.
    """
    
    async def get(self, id):
        """
        Receives <id> and return a dictionary with the result.
        If it not found a data with this <id>, return None.
        """
        raise NotImplementedError

    async def list(self, page=0, size=10):
        """
        Receives <page> and <size> and return a list of dictionaries with the result.
        If result is empty, return a empty list.
        """
        raise NotImplementedError

    async def create(self, data, id=None):
        """
        Receives <data> with the resource to be saved, 
        save it into db, and return the resource id.
        If receive <id>, set this id to the document and return this id.
        """
        raise NotImplementedError

    async def replace(self, id, data):
        """
        Receives <data> with the resource to be saved and <id>, 
        replace the resource in db.
        """
        raise NotImplementedError

    async def update(self, id, data):
        """
        Receives <data> with the partial resource to be saved and <id>, 
        replace just the partial resource received in db.
        """
        raise NotImplementedError

    async def delete(self, id):
        """
        Receives the <id> and delete it from db.
        """
        raise NotImplementedError