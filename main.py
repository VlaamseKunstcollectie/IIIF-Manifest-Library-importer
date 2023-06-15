import argparse
import os

from elody import Client
from elody.exceptions import NonUniqueException
from importers.collection_importer import CollectionImporter
from importers.lido_oai_pmh_importer import LidoOaiPmhImporter
from importers.mpm_oai_pmh_importer import MpmOaiPmhImporter
from datetime import datetime

importers = [CollectionImporter(), LidoOaiPmhImporter(), MpmOaiPmhImporter()]
elody_client = Client()
parser = argparse.ArgumentParser()
parser.add_argument("--from_time", type=str, help="Start date for OAI parse")
parser.add_argument("--until_time", type=str, help="End date for OAI parse")


def main():
    args = parser.parse_args()
    from_date = datetime.fromisoformat(args.from_time) if args.from_time else None
    until_date = datetime.fromisoformat(args.until_time) if args.until_time else None
    for importer in importers:
        for manifest in importer.get_manifests(
            from_date=from_date, until_date=until_date
        ):
            print(manifest.as_elody_entity())
            try:
                elody_client.add_object("entities", manifest.as_elody_entity())
            except NonUniqueException:
                print("Manifest is already present in the system")


if __name__ == "__main__":
    main()
