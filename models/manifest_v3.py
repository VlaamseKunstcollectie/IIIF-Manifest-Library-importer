import json
import urllib.request

class ManifestV3:
    def __init__(self, manifest):
        self.manifest = manifest
        
    def as_dict(self):
        return self.manifest

    @classmethod
    def from_url(cls, manifest_url):
        if not manifest_url.endswith("manifest.json"):
            return cls(dict())
        with urllib.request.urlopen(manifest_url) as url:
            manifest = json.load(url)
            return cls(manifest)
