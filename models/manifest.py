import json
import urllib.request

from urllib.error import HTTPError


class Manifest:
    presentation_contexts = [
        "http://iiif.io/api/presentation/2/context.json",
        "http://iiif.io/api/presentation/3/context.json",
    ]

    def __init__(self, manifest):
        self.manifest = manifest
        self.valid_manifest()

    def as_dict(self):
        return self.manifest

    def as_elody_entity(self):
        return {
            "type": "manifest",
            "object_id": self.get_object_id(),
            "identifiers": self.get_identifiers(),
            "metadata": self.get_metadata(),
            "data": self.manifest,
        }

    @classmethod
    def from_url(cls, manifest_url):
        manifest = dict()
        try:
            with urllib.request.urlopen(manifest_url) as url:
                manifest = json.load(url)
        except HTTPError as ex:
            print(f"Couldn't fetch manifest {manifest_url} because of {ex}")
        return cls(manifest)

    def get_identifiers(self):
        return list()

    def get_metadata(self):
        return list()

    def get_object_id(self):
        return str()

    def valid_manifest(self):
        if self.manifest.get("@context") not in self.presentation_contexts:
            raise NoValidManifest("Manifest is not in the valid v3 format")


class NoValidManifest(Exception):
    def __init__(self, message):
        super().__init__(message)
