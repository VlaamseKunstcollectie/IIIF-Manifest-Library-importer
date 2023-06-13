import urllib.request
import validators

from lxml import etree
from models.manifest import Manifest
from urllib.error import HTTPError

lido_xpath = "/OAI:OAI-PMH/OAI:GetRecord/OAI:record/OAI:metadata/lido:lido"
namespaces = {
    "OAI": "http://www.openarchives.org/OAI/2.0/",
    "lido": "http://www.lido-schema.org",
}
lido_fields = [
    {
        "key": "creator",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventActor/lido:actorInRole/lido:actor/lido:nameActorSet/lido:appellationValue[@xml:lang="nl"][1]',
        "lang": "nl",
    },
    {
        "key": "creator",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventActor/lido:actorInRole/lido:actor/lido:nameActorSet/lido:appellationValue[@xml:lang="en"][1]',
        "lang": "en",
    },
    # {
    #     'key': 'creator_role',
    #     'xpath': '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventActor/lido:actorInRole/lido:roleActor/lido:term[@xml:lang="nl"]',
    #     'lang': 'nl'
    # },
    # {
    #     'key': 'creator_role',
    #     'xpath': '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventActor/lido:actorInRole/lido:roleActor/lido:term[@xml:lang="en"]',
    #     'lang': 'en'
    # },
    # {
    #     'key': 'title',
    #     'xpath': '/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:titleWrap/lido:titleSet/lido:appellationValue[@lido:pref="preferred" and (@xml:lang="nl" or not(@xml:lang))][1]',
    #     'lang': 'nl'
    # },
    # {
    #     'key': 'title',
    #     'xpath': '/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:titleWrap/lido:titleSet/lido:appellationValue[@lido:pref="preferred" and @xml:lang="en"][1]',
    #     'lang': 'en'
    # },
    {
        "key": "date",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventDate/lido:displayDate',
        "lang": "en",
    },
    {
        "key": "period",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:periodName[not(@lido:type)]/lido:term[@xml:lang="nl"][1]',
        "lang": "nl",
    },
    {
        "key": "period",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:periodName[not(@lido:type)]/lido:term[@xml:lang="en"][1]',
        "lang": "en",
    },
    {
        "key": "institution",
        "xpath": '/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:repositoryWrap/lido:repositorySet[not(@lido:type)]/lido:repositoryName/lido:legalBodyName/lido:appellationValue[@xml:lang="nl"]',
        "lang": "nl",
    },
    {
        "key": "institution",
        "xpath": '/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:repositoryWrap/lido:repositorySet[not(@lido:type)]/lido:repositoryName/lido:legalBodyName/lido:appellationValue[@xml:lang="en"]',
        "lang": "en",
    },
    {
        "key": "type",
        "xpath": '/lido:descriptiveMetadata/lido:objectClassificationWrap/lido:classificationWrap/lido:classification[@lido:type="object-category"]/lido:term[@xml:lang="nl"][1]',
        "lang": "nl",
    },
    {
        "key": "type",
        "xpath": '/lido:descriptiveMetadata/lido:objectClassificationWrap/lido:classificationWrap/lido:classification[@lido:type="object-category"]/lido:term[@xml:lang="en"][1]',
        "lang": "en",
    },
    {
        "key": "subtype",
        "xpath": '/lido:descriptivemetadata/lido:objectclassificationwrap/lido:objectworktypewrap/lido:objectworktype/lido:term[@xml:lang="nl"][1]',
        "lang": "nl",
    },
    {
        "key": "subtype",
        "xpath": '/lido:descriptivemetadata/lido:objectclassificationwrap/lido:objectworktypewrap/lido:objectworktype/lido:term[@xml:lang="en"][1]',
        "lang": "en",
    },
    {
        "key": "technical_description",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventMaterialsTech/lido:displayMaterialsTech[@xml:lang="nl"][1]',
        "lang": "nl",
    },
    {
        "key": "technical_description",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventMaterialsTech/lido:displayMaterialsTech[@xml:lang="en"][1]',
        "lang": "en",
    },
    {
        "key": "material",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventMaterialsTech/lido:materialsTech/lido:termMaterialsTech[@lido:type="material"]/lido:term[@lido:pref="preferred" and @xml:lang="nl"]',
        "lang": "nl",
    },
    {
        "key": "material",
        "xpath": '/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term="production"]/lido:eventMaterialsTech/lido:materialsTech/lido:termMaterialsTech[@lido:type="material"]/lido:term[@lido:pref="preferred" and @xml:lang="en"]',
        "lang": "en",
    },
    {
        "key": "dimensions",
        "xpath": "/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:objectMeasurementsWrap/lido:objectMeasurementsSet/lido:displayObjectMeasurements[1]",
        "lang": "en",
    },
    {
        "key": "rights",
        "xpath": "/lido:administrativeMetadata/lido:rightsWorkWrap/lido:rightsWorkSet/lido:creditLine",
        "lang": "nl",
    },
    {
        "key": "subject",
        "xpath": '/lido:descriptiveMetadata/lido:objectRelationWrap/lido:subjectWrap/lido:subjectSet/lido:subject[@lido:type="content-motif-general"]/lido:subjectConcept/lido:term[@xml:lang="nl"][1]',
        "lang": "nl",
    },
    {
        "key": "subject",
        "xpath": '/lido:descriptiveMetadata/lido:objectRelationWrap/lido:subjectWrap/lido:subjectSet/lido:subject[@lido:type="content-motif-general"]/lido:subjectConcept/lido:term[@xml:lang="en"][1]',
        "lang": "en",
    },
    {
        "key": "keyword",
        "xpath": '/lido:descriptiveMetadata/lido:objectRelationWrap/lido:subjectWrap/lido:subjectSet/lido:subject[@lido:type="content-motif-specific"]/lido:subjectConcept[lido:conceptID[@lido:source="Iconclass"]]/lido:term[@xml:lang="nl"]',
        "lang": "nl",
    },
    {
        "key": "keyword",
        "xpath": '/lido:descriptiveMetadata/lido:objectRelationWrap/lido:subjectWrap/lido:subjectSet/lido:subject[@lido:type="content-motif-specific"]/lido:subjectConcept[lido:conceptID[@lido:source="Iconclass"]]/lido:term[@xml:lang="en"]',
        "lang": "en",
    },
    {
        "key": "description",
        "xpath": '/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:objectDescriptionWrap/lido:objectDescriptionSet/lido:descriptiveNoteValue[@xml:lang="nl"]',
        "lang": "nl",
    },
    {
        "key": "description",
        "xpath": '/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:objectDescriptionWrap/lido:objectDescriptionSet/lido:descriptiveNoteValue[@xml:lang="en"]',
        "lang": "en",
    },
    {
        "key": "location",
        "xpath": '/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:repositoryWrap/lido:repositorySet[not(@lido:type)]/lido:repositoryLocation/lido:namePlaceSet/lido:appellationValue[@xml:lang="nl"]',
        "lang": "nl",
    },
    {
        "key": "location",
        "xpath": '/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:repositoryWrap/lido:repositorySet[not(@lido:type)]/lido:repositoryLocation/lido:namePlaceSet/lido:appellationValue[@xml:lang="en"]',
        "lang": "en",
    },
]


class LidoManifest(Manifest):
    def _get_lido_urls(self):
        for see_also in self.manifest.get("seeAlso", list()):
            if (
                see_also.get("label", dict()).get("en", list())[0]
                == "Object Description in XML"
            ):
                yield see_also.get("id")

    def _get_lido_metadata(self):
        lido_metadata = list()
        for lido_url in self._get_lido_urls():
            if not validators.url(lido_url, public=True):
                continue
            try:
                with urllib.request.urlopen(lido_url) as lido_xml:
                    tree = etree.fromstring(lido_xml.read())
                    lido_metadata.extend(self.__parse_lido_metadata(tree))
            except (Exception, HTTPError) as ex:
                print(f"Couldn't fetch extra metadata from {lido_url} because of {ex}")
        return lido_metadata

    def __parse_lido_metadata(self, tree):
        for lido_field in lido_fields:
            for value in tree.xpath(
                lido_xpath + lido_field.get("xpath"), namespaces=namespaces
            ):
                yield (
                    self._decorate_metadata_value(
                        lido_field.get("key"), value.text, lido_field.get("lang")
                    )
                )

    def get_metadata(self):
        metadata = super().get_metadata()
        metadata.extend(self._get_lido_metadata())
        return metadata
