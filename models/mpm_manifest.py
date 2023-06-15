from models.manifest import Manifest


class MpmManifest(Manifest):
    def __label_to_snake_case(self, label):
        return label.lower().replace(" ", "_")

    def get_inventory_number(self):
        for metadata in self.manifest.get("metadata", list()):
            if metadata.get("label", "") == "Object ID":
                return metadata.get("value", "")

    def get_manifest_id(self):
        for sequence in self.manifest.get("sequences", list()):
            return sequence.get("@id")

    def get_metadata(self):
        metadata = list()
        for manifest_metadata in self.manifest.get("metadata", list()):
            metadata.append(
                self._decorate_metadata_value(
                    self.__label_to_snake_case(manifest_metadata.get("label")),
                    manifest_metadata.get("value"),
                    "nl",
                )
            )
        return metadata
