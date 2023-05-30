import json
import ssl
import urllib.request

from urllib.error import HTTPError, URLError

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class Manifest:
    presentation_contexts = [
        "http://iiif.io/api/presentation/2/context.json",
        "http://iiif.io/api/presentation/3/context.json",
    ]

    def __init__(self, manifest):
        self.manifest = manifest
        self.valid_manifest()

    def _decorate_metadata_value(self, key, value, lang="en"):
        return {
            "key": key,
            "value": value,
            "lang": lang,
        }

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
            with urllib.request.urlopen(manifest_url, context=ctx) as url:
                manifest = json.load(url)
        except HTTPError as ex:
            print(f"Couldn't fetch manifest {manifest_url} because of {ex}")
        except URLError as ex:
            print(f"Couldn't fetch manifest {manifest_url} because of {ex}")
        except Exception as ex:
            print(f"Couldn't fetch manifest {manifest_url} because of {ex}")
        return cls(manifest)

    def get_identifiers(self):
        return [
            self.get_inventory_number(),
            self.get_manifest_id(),
        ]

    def get_inventory_number(self):
        for item in self.manifest.get("items", list()):
            for metadata in item.get("metadata", list()):
                if metadata.get("label", dict()).get("en", [""])[0] == "Inventory no.":
                    return metadata.get("value", dict()).get("none", [""])[0]

    def get_manifest_id(self):
        for item in self.manifest.get("items", list()):
            if "id" in item:
                return item.get("id")

    def get_metadata(self):
        metadata = list()
        metadata.extend(self.get_title())
        metadata.extend(self.get_photographer())
        return metadata

    def get_object_id(self):
        return self.get_inventory_number()

    def get_photographer(self):
        for item in self.manifest.get("items", list()):
            for metadata in item.get("metadata", list()):
                if metadata.get("label", dict()).get("en", [""])[0] == "Photographer":
                    yield self._decorate_metadata_value(
                        "photographer",
                        metadata.get("value", dict()).get("none", [""])[0],
                        "en",
                    )

    def get_title(self):
        for lang, title_list in self.manifest.get("label", dict()).items():
            yield self._decorate_metadata_value("title", title_list[0], lang)

    def valid_manifest(self):
        if self.manifest.get("@context") not in self.presentation_contexts:
            raise NoValidManifest("Manifest is not in the valid v3 format")


class NoValidManifest(Exception):
    def __init__(self, message):
        super().__init__(message)
