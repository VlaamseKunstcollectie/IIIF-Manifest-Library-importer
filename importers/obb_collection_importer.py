import json
import os
import urllib.request

from importers.base_importer import BaseImporter
from models.manifest import Manifest, NoValidManifest


class ObbCollectionImporter(BaseImporter):
    def __init__(self, collection_urls=None):
        self.collection_urls = collection_urls or os.getenv(
            "COLLECTION_URLS_OBB", ""
        ).split(",")

    def _get_manifest(self, manifest_item):
        if manifest_item.get("@type") == "sc:Manifest":
            try:
                return Manifest.from_url(manifest_item.get("@id"))
            except NoValidManifest as ex:
                print(f"Couldn't parse manifest {manifest_url} because of {ex}")

    def get_importer_name(self):
        return "Collection importer for OBB"

    def get_manifests(self, from_date=None, until_date=None, limit=None):
        counter = 1
        for collection_url in self.collection_urls:
            with urllib.request.urlopen(collection_url) as url:
                collection = json.load(url)
                if "first" in collection:
                    next_collection_url = collection.get("first")
                while next_collection_url:
                    print(f"Traversing {next_collection_url}")
                    with urllib.request.urlopen(next_collection_url) as url:
                        current_collection = json.load(url)
                        next_collection_url = current_collection.get("next")
                        for manifest_item in current_collection.get(
                            "manifests", list()
                        ):
                            if limit:
                                if counter > limit:
                                    break
                                print(f"Importing manifest {counter}/{limit}")
                            yield self._get_manifest(manifest_item)
                            counter += 1
