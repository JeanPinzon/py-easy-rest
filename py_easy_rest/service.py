import json
import logging

from py_easy_rest.exceptions import PYRInputNotValidError, PYRNotFoundError
from py_easy_rest.caches import PYRDummyCache
from py_easy_rest.repos import PYRMemoryRepo
from py_easy_rest.dictionary_utils import merge

from jsonschema import Draft7Validator


class PYRService():

    def __init__(
        self,
        api_config,
        repo=PYRMemoryRepo(),
        cache=PYRDummyCache(),
        cache_list_seconds_ttl=10,
        cache_get_seconds_ttl=60 * 30,  # thirty minutes
    ):
        self._repo = repo
        self._api_config = api_config
        self._cache = cache
        self._cache_list_seconds_ttl = cache_list_seconds_ttl
        self._cache_get_seconds_ttl = cache_get_seconds_ttl
        self._logger = logging.getLogger(__name__)

        self._schemas = self._api_config["schemas"]

    async def list(self, slug, page, size):
        if page is not None:
            page = int(page)

        if size is not None:
            size = int(size)

        cache_key = f"{slug}.list.page-{page}.size-{size}"

        cached = await self._cache.get(cache_key)

        if cached is not None:
            self._logger.info(f"Found cache result with key {cache_key}")
            result = json.loads(cached)
            return result

        self._logger.info(f"Not found cache result with key {cache_key}")

        result = await self._repo.list(slug, page, size)

        await self._cache.set(cache_key, json.dumps(result), ttl=self._cache_list_seconds_ttl)

        return result

    async def get(self, slug, id):
        cache_key = f"{slug}.get.id-{id}"

        cached = await self._cache.get(cache_key)

        if cached is not None:
            self._logger.info(f"Found cache result with key {cache_key}")
            result = json.loads(cached)
            return result

        self._logger.info(f"Not found cache result with key {cache_key}")

        result = await self._repo.get(slug, id)

        if result:
            await self._cache.set(cache_key, json.dumps(result), ttl=self._cache_get_seconds_ttl)
            return result

        raise PYRNotFoundError(f"{slug} {id} not found")

    async def create(self, slug, data, id=None):
        errors = self._validate(data, slug)

        if errors:
            raise PYRInputNotValidError(errors)

        resource_id = await self._repo.create(slug, data, id)

        cache_key = f"{slug}.get.id-{resource_id}"
        await self._cache.delete(cache_key)

        return resource_id

    async def replace(self, slug, data, id):
        existent_doc = await self._repo.get(slug, id)

        if not existent_doc:
            raise PYRNotFoundError(f"{slug} {id} not found")

        errors = self._validate(data, slug)

        if errors:
            raise PYRInputNotValidError(errors)

        await self._repo.replace(slug, id, data)

        cache_key = f"{slug}.get.id-{id}"
        await self._cache.delete(cache_key)

    async def partial_update(self, slug, data, id):
        existent_doc = await self._repo.get(slug, id)

        if not existent_doc:
            raise PYRNotFoundError(f"{slug} {id} not found")

        doc = merge(data, existent_doc)
        doc.pop("_id", None)

        errors = self._validate(data, slug)

        if errors:
            raise PYRInputNotValidError(errors)

        await self._repo.replace(slug, id, doc)

        cache_key = f"{slug}.get.id-{id}"
        await self._cache.delete(cache_key)

    async def delete(self, slug, id):
        existent_doc = await self._repo.get(slug, id)

        if not existent_doc:
            raise PYRNotFoundError(f"{slug} {id} not found")

        await self._repo.delete(slug, id)

        cache_key = f"{slug}.get.id-{id}"
        await self._cache.delete(cache_key)

    def set_logger(self, logger):
        self._logger = logger

    def _validate(self, data, slug):
        schema = next(schema for schema in self._schemas if schema["slug"] == slug)

        validator = Draft7Validator(schema)

        errors = []

        for error in validator.iter_errors(data):
            errors.append(error.message)

        if len(errors) > 0:
            return errors

        return None
