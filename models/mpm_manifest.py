from models.manifest import Manifest


class MpmManifest(Manifest):
    def get_inventory_number(self):
        for metadata in self.manifest.get("metadata", list()):
            if metadata.get("label", "") == "Object ID":
                return metadata.get("value", "")

    def get_manifest_id(self):
        for sequence in self.manifest.get("sequences", list()):
            return sequence.get("@id")

    def get_metadata(self):
        metadata = list()
        metadata.extend(self.get_attribution())
        metadata.extend(self.get_rights())
        for manifest_metadata in self.manifest.get("metadata", list()):
            metadata.append(
                self._decorate_metadata_value(
                    self.label_to_snake_case(manifest_metadata.get("label")),
                    manifest_metadata.get("value"),
                    "nl",
                )
            )
        return metadata
