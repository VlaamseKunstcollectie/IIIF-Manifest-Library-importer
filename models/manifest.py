import json
import re
import ssl
import urllib.request

from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class Manifest:
    presentation_contexts = [
        "http://iiif.io/api/presentation/2/context.json",
        "http://iiif.io/api/presentation/3/context.json",
    ]

    def __init__(self, manifest, manifest_url=None):
        self.manifest = manifest
        self.manifest_url = manifest_url
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
        return cls(manifest, manifest_url)

    def get_attribution(self):
        required_statement = self.manifest.get("requiredStatement", dict())
        label = required_statement.get("label")
        value = required_statement.get("value")
        if required_statement and label and value:
            for language, attribution in value.items():
                yield self._decorate_metadata_value(
                    self.label_to_snake_case(label[language][0]),
                    attribution[0],
                    language,
                )

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
        for metadata in self.manifest.get("metadata", list()):
            if (
                isinstance(metadata, dict)
                and metadata.get("label") == "Alternative Identifier"
            ):
                return metadata.get("value")

    def get_manifest_id(self):
        for item in self.manifest.get("items", list()):
            if "id" in item:
                return item.get("id")
        if "@id" in self.manifest:
            return self.manifest.get("@id")

    def get_metadata(self):
        metadata = list()
        metadata.extend(self.get_title())
        metadata.extend(self.get_photographer())
        metadata.extend(self.get_attribution())
        metadata.extend(self.get_rights())
        metadata.extend(self.get_manifest_url_as_metadata())
        metadata.extend(self.get_manifest_version_as_metadata())
        for manifest_metadata in self.manifest.get("metadata", list()):
            if isinstance(manifest_metadata, dict):
                label = manifest_metadata.get("label")
                value = manifest_metadata.get("value")
                if isinstance(label, str) and isinstance(value, str):
                    metadata.append(
                        self._decorate_metadata_value(
                            self.label_to_snake_case(label), value, "en"
                        )
                    )
        return metadata

    def get_object_id(self):
        return self.get_inventory_number()

    def get_institution(self):
        institution_map = {
            "imagehub.mskgent.be": "MSK Gent",
            "resourcespace.muzee.be": "Muzee",
            "dam.museabrugge.be": "Musea Brugge",
            "dams.antwerpen.be": "Museum Plantin-Moretus",
        }
        institutions_in_statement = [
            "Museum voor Schone Kunsten Gent",
            "Mu.ZEE",
            "Passchendaele Museum 1917",
            "Koninklijk Museum voor Schone Kunsten Antwerpen",
        ]
        parsed_uri = urlparse(self.manifest.get("id", self.manifest.get("@id")))
        institution_name = institution_map.get(parsed_uri.netloc)
        if not institution_name:
            required_statement = (
                self.manifest.get("requiredStatement", dict())
                .get("value", dict())
                .get("nl", [""])[0]
            )
            for possible_institution in institutions_in_statement:
                if possible_institution in required_statement:
                    institution_name = possible_institution
        if not institution_name:
            print(self.manifest.get("id", self.manifest.get("@id")))
            institution_search = re.search(
                r"(?<=Provided by ).+", self.manifest.get("attribution", "")
            )
            if not institution_search:
                return False
            institution_name = institution_search.group(0)
        return {
            "type": "institution",
            "metadata": [
                {
                    "key": "title",
                    "value": institution_name,
                    "lang": "nl",
                }
            ],
        }

    def get_manifest_url_as_metadata(self):
        if self.manifest_url:
            yield self._decorate_metadata_value(
                "manifest_url",
                self.manifest_url,
                "en",
            )

    def get_manifest_version(self):
        versions = re.findall(r"[0-9]", self.manifest.get("@context"))
        if versions:
            return versions[0]
        return "unknown version"

    def get_manifest_version_as_metadata(self):
        yield self._decorate_metadata_value(
            "manifest_version",
            self.get_manifest_version(),
            "en",
        )

    def get_photographer(self):
        for item in self.manifest.get("items", list()):
            for metadata in item.get("metadata", list()):
                if metadata.get("label", dict()).get("en", [""])[0] == "Photographer":
                    yield self._decorate_metadata_value(
                        "photographer",
                        metadata.get("value", dict()).get("none", [""])[0],
                        "en",
                    )

    def get_rights(self):
        rights = self.manifest.get("rights", self.manifest.get("license"))
        if rights:
            yield self._decorate_metadata_value(
                "rights",
                rights,
                "en",
            )

    def get_title(self):
        if isinstance(self.manifest.get("label", dict()), dict):
            for lang, title_list in self.manifest.get("label", dict()).items():
                yield self._decorate_metadata_value("title", title_list[0], lang)
        elif isinstance(self.manifest.get("label"), str):
            yield self._decorate_metadata_value(
                "title", self.manifest.get("label"), "nl"
            )
        else:
            print(f"This manifest {self.manifest} has a strange label")

    @staticmethod
    def label_to_snake_case(label):
        return label.lower().replace(" ", "_")

    def valid_manifest(self):
        if self.manifest.get("@context") not in self.presentation_contexts:
            raise NoValidManifest("Manifest is not in the valid v3 format")


class NoValidManifest(Exception):
    def __init__(self, message):
        super().__init__(message)
