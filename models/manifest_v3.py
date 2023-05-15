import json
import urllib.request

from urllib.error import HTTPError


class ManifestV3:
    def __init__(self, manifest):
        self.manifest = manifest
        self.valid_manifest()

    def as_dict(self):
        return self.manifest

    @classmethod
    def from_url(cls, manifest_url):
        manifest = dict()
        try:
            with urllib.request.urlopen(manifest_url) as url:
                manifest = json.load(url)
        except HTTPError as ex:
            print(f"Couldn't fetch manifest {manifest_url} because of {ex}")
        return cls(manifest)

    def valid_manifest(self):
        if (
            self.manifest.get("@context")
            != "http://iiif.io/api/presentation/3/context.json"
        ):
            raise NoValidManifest("Manifest is not in the valid v3 format")


class NoValidManifest(Exception):
    def __init__(self, message):
        super().__init__(message)
