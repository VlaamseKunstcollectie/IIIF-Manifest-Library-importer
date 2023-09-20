import argparse
import os

from elody import Client
from elody.exceptions import NonUniqueException
from importers.collection_importer import CollectionImporter
from importers.lido_oai_pmh_importer import LidoOaiPmhImporter
from importers.mpm_oai_pmh_importer import MpmOaiPmhImporter
from importers.obb_collection_importer import ObbCollectionImporter
from datetime import datetime

importers = [
    ObbCollectionImporter(),
    CollectionImporter(),
    LidoOaiPmhImporter(),
    MpmOaiPmhImporter(),
]
elody_client = Client()
parser = argparse.ArgumentParser()
parser.add_argument("--from_time", type=str, help="Start date for OAI parse")
parser.add_argument("--until_time", type=str, help="End date for OAI parse")
parser.add_argument("--limit", type=int, help="Limit amount of manifests per importer")


def create_entity_for_importer(importer_name):
    entity = {
        "type": "importer",
        "metadata": [
            {
                "key": "title",
                "value": importer_name,
                "lang": "nl",
            }
        ],
    }
    return elody_client.add_object("entities", entity)


def get_is_in_relation(target_entity, label):
    return [
        {
            "label": label,
            "key": target_entity.get("_id"),
            "type": "isIn",
        }
    ]


def main():
    unique_institutions = dict()
    args = parser.parse_args()
    from_date = datetime.fromisoformat(args.from_time) if args.from_time else None
    until_date = datetime.fromisoformat(args.until_time) if args.until_time else None
    for importer in importers:
        importer_entity = create_entity_for_importer(importer.get_importer_name())
        for manifest in importer.get_manifests(
            from_date=from_date, until_date=until_date, limit=args.limit
        ):
            try:
                institution = manifest.get_institution()
                if not institution:
                    continue
                institution_title = institution.get("metadata", [dict()])[0].get(
                    "value"
                )
                if not institution_title in unique_institutions:
                    unique_institutions[institution_title] = elody_client.add_object(
                        "entities", institution
                    )
                institution_entity = unique_institutions.get(institution_title)
                entity = elody_client.add_object("entities", manifest.as_elody_entity())
                elody_client.update_object_relations(
                    "entities",
                    entity.get("_id"),
                    get_is_in_relation(importer_entity, "importer"),
                )
                elody_client.update_object_relations(
                    "entities",
                    entity.get("_id"),
                    get_is_in_relation(institution_entity, "institution"),
                )
            except NonUniqueException:
                print(
                    f"Manifest {manifest.get_manifest_id()} is already present in the system"
                )


if __name__ == "__main__":
    main()
