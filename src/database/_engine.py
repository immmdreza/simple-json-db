from pathlib import Path

import aiofiles


class Engine:
    def __init__(self, base_path: Path):
        self._base_path = base_path
        self._initialize_path(base_path)

    def _initialize_path(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True)

    def collection_path_builder(self, collection_name: str):
        return self._base_path / collection_name

    def collection_tmp_path_builder(
        self, collection_name: str, instance_number: int = 1
    ):
        return self._base_path / f"__{collection_name}_{instance_number}__"

    def collection_exists(self, collection_name: str) -> bool:
        collection_path = self.collection_path_builder(collection_name)
        return collection_path.exists()

    async def create_collection(self, collection_name: str):
        collection_path = self.collection_path_builder(collection_name)
        async with aiofiles.open(collection_path, "w") as f:
            await f.write("")
