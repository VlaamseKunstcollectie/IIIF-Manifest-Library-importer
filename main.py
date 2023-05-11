from importers.oai_pmh_importer import OaiPmhImporter

importers = [OaiPmhImporter()]

def main():
    for importer in importers:
        importer.get_new_manifests() 

if __name__ == "__main__":
    main()
