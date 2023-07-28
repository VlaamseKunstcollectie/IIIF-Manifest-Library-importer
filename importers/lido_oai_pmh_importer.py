import os

from oaipmh.metadata import MetadataReader
from importers.oai_pmh_importer import OaiPmhImporter
from models.lido_manifest import LidoManifest
from models.manifest import NoValidManifest

lido_reader = MetadataReader(
    fields={
        "manifests": (
            "textList",
            "lido:lido/lido:administrativeMetadata/lido:resourceWrap/lido:resourceSet/lido:resourceID/text()",
        ),
        "types": (
            "textList",
            "lido:lido/lido:administrativeMetadata/lido:resourceWrap/lido:resourceSet/lido:resourceType/lido:term/text()",
        ),
    },
    namespaces={
        "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "lido": "http://www.lido-schema.org",
    },
)


class LidoOaiPmhImporter(OaiPmhImporter):
    def __init__(self):
        lido_urls = os.getenv("LIDO_URLS", "").split(",")
        super().__init__(lido_urls, "oai_lido", lido_reader, "manifests", "types")

    def _get_manifests_from_oai(
        self, client, from_date=None, until_date=None, limit=None
    ):
        counter = 1
        for record in client.listRecords(
            metadataPrefix=self.metadata_prefix, from_=from_date, until=until_date
        ):
            if limit and counter > limit:
                break
            manifest_urls = list()
            if self.manifest_definition_field:
                types = record[1].getField(self.manifest_definition_field)
                if "IIIF Manifest" in types:
                    manifest_urls.append(
                        record[1].getField(self.manifest_field)[
                            types.index("IIIF Manifest")
                        ]
                    )
            else:
                manifest_urls = record[1].getField(self.manifest_field)
            for manifest_url in manifest_urls:
                try:
                    if limit:
                        print(f"Importing manifest {counter}/{limit}")
                    yield LidoManifest.from_url(manifest_url)
                    counter += 1
                except NoValidManifest as ex:
                    print(f"Couldn't parse manifest {manifest_url} because of {ex}")
