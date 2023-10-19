import argparse
import hashlib
import os
import validators

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


def add_or_update_entity(entity):
    try:
        entity = elody_client.add_object("entities", entity)
    except NonUniqueException as error:
        for identifier in entity.get("identifiers", []):
            if not validators.url(identifier) and not "/" in identifier:
                print(f"Updating {identifier} instead of adding")
                try:
                    entity = elody_client.update_object("entities", identifier, entity)
                except:
                    entity = None
                    print(
                        "Something went wrong updating, probably incorrect use of inventory numbers"
                    )
                break
    return entity


def create_entity_for_importer(importer_name):
    entity = {
        "type": "importer",
        "identifiers": [hashlib.md5(importer_name.encode()).hexdigest()],
        "metadata": [
            {
                "key": "title",
                "value": importer_name,
                "lang": "nl",
            }
        ],
    }
    return add_or_update_entity(entity)


def get_is_in_relation(target_entity, label, relation_value):
    return [
        {
            "value": relation_value,
            "label": label,
            "key": target_entity.get("_id"),
            "type": "isIn",
        }
    ]


def main():
    args = parser.parse_args()
    from_date = datetime.fromisoformat(args.from_time) if args.from_time else None
    until_date = datetime.fromisoformat(args.until_time) if args.until_time else None
    for importer in importers:
        importer_entity = create_entity_for_importer(importer.get_importer_name())
        for manifest in importer.get_manifests(
            from_date=from_date, until_date=until_date, limit=args.limit
        ):
            institution = manifest.get_institution()
            if not institution:
                continue
            institution_title = institution.get("metadata", [dict()])[0].get("value")
            institution_entity = add_or_update_entity(institution)
            entity = add_or_update_entity(manifest.as_elody_entity())
            if entity:
                elody_client.update_object_relations(
                    "entities",
                    entity.get("_id"),
                    get_is_in_relation(
                        importer_entity, "importer", importer.get_importer_name()
                    ),
                )
                elody_client.update_object_relations(
                    "entities",
                    entity.get("_id"),
                    get_is_in_relation(
                        institution_entity, "institution", institution_title
                    ),
                )


if __name__ == "__main__":
    main()
