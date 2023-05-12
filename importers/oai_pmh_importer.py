import validators

from datetime import datetime
from importers.base_importer import BaseImporter
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry


class OaiPmhImporter(BaseImporter):
    def __init__(self, urls, metadata_prefix, reader):
        self.clients = list()
        self.urls = urls
        self.metadata_prefix = metadata_prefix
        self.reader = reader
        registry = MetadataRegistry()
        registry.registerReader(self.metadata_prefix, self.reader)
        for oai_url in self.urls:
            if validators.url(oai_url):
                self.clients.append(Client(oai_url, registry))

    def get_manifests(self, from_date=None, until_date=None):
        for client in self.clients:
            for record in client.listRecords(metadataPrefix=self.metadata_prefix):
                for manifest_url in record[1].getField("manifests"):
                    print(manifest_url)
