import validators

from datetime import datetime
from importers.base_importer import BaseImporter
from models.manifest import Manifest, NoValidManifest
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry


class OaiPmhImporter(BaseImporter):
    def __init__(self, urls, metadata_prefix, reader, manifest_field="manifests"):
        self.clients = list()
        self.urls = urls
        self.metadata_prefix = metadata_prefix
        self.reader = reader
        self.manifest_field = manifest_field
        registry = MetadataRegistry()
        registry.registerReader(self.metadata_prefix, self.reader)
        for oai_url in self.urls:
            if validators.url(oai_url):
                self.clients.append(Client(oai_url, registry))

    def _get_manifest_list(self, client):
        manifests = list()
        for record in client.listRecords(metadataPrefix=self.metadata_prefix):
            for manifest_url in record[1].getField(self.manifest_field):
                try:
                    manifests.append(Manifest.from_url(manifest_url).as_dict())
                except NoValidManifest as ex:
                    print(f"Couldn't parse manifest {manifest_url} because of {ex}")
        return manifests

    def get_manifests(self, from_date=None, until_date=None):
        manifests = list()
        for client in self.clients:
            manifests.extend(self._get_manifest_list(client))
        return manifests
