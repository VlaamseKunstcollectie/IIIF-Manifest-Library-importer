from importers.lido_oai_pmh_importer import LidoOaiPmhImporter

importers = [LidoOaiPmhImporter()]


def main():
    for importer in importers:
        importer.get_manifests()


if __name__ == "__main__":
    main()
