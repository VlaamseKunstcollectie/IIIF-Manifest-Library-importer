import os
import validators

from oaipmh.metadata import oai_dc_reader
from importers.oai_pmh_importer import OaiPmhImporter
from models.manifest import NoValidManifest
from models.mpm_manifest import MpmManifest


class MpmOaiPmhImporter(OaiPmhImporter):
    def __init__(self):
        mpm_urls = os.getenv("MPM_OAI_URLS", "").split(",")
        super().__init__(mpm_urls, "oai_dc", oai_dc_reader)

    def _get_iiif_urls_from_record(self, record):
        for identifier in record[1].getField("identifier"):
            if validators.url(identifier):
                yield identifier.replace("/asset/", "/iiif/") + "/manifest"

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
            if self._is_public_mpm_record(record):
                manifest_urls = self._get_iiif_urls_from_record(record)
            for manifest_url in manifest_urls:
                try:
                    if limit:
                        print(f"Processing entry {counter}/{limit}")
                    yield MpmManifest.from_url(manifest_url)
                    counter += 1
                except NoValidManifest as ex:
                    print(f"Couldn't parse manifest {manifest_url} because of {ex}")

    def _is_public_mpm_record(self, record):
        publishers = record[1].getField("publisher")
        rights = record[1].getField("rights")
        return "public" in rights and "Museum Plantin-Moretus (Antwerpen)" in publishers

    def get_importer_name(self):
        return "OAI-PMH Importer for MPM"
