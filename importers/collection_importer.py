import json
import os
import urllib.request

from importers.base_importer import BaseImporter
from models.manifest import Manifest, NoValidManifest


class CollectionImporter(BaseImporter):
    def __init__(self, collection_urls=None):
        self.collection_urls = collection_urls or os.getenv(
            "COLLECTION_URLS", ""
        ).split(",")

    def _get_manifest(self, manifest_item):
        if manifest_item.get("type") == "Manifest":
            try:
                return Manifest.from_url(manifest_item.get("id"))
            except NoValidManifest as ex:
                print(f"Couldn't parse manifest {manifest_url} because of {ex}")

    def get_manifests(self, from_date=None, until_date=None, limit=None):
        counter = 1
        for collection_url in self.collection_urls:
            print(f"Imporing assets from {collection_url}")
            with urllib.request.urlopen(collection_url) as url:
                collection = json.load(url)
                for manifest_item in collection.get("items", list()):
                    if limit:
                        if counter > limit:
                            break
                        print(f"Importing manifest {counter}/{limit}")
                    yield self._get_manifest(manifest_item)
                    counter += 1
