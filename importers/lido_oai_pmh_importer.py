import os

from oaipmh.metadata import MetadataReader
from importers.oai_pmh_importer import OaiPmhImporter

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
