from __future__ import absolute_import, division, print_function

from operator import itemgetter

from mock import patch
from utils import assert_ordered_conflicts, validate_subschema

from inspire_json_merger.api import merge
from inspire_json_merger.config import (ArxivOnArxivOperations,
                                        ArxivOnPublisherOperations,
                                        ErratumOnPublisherOperations,
                                        PublisherOnArxivOperations,
                                        PublisherOnPublisherOperations)


@patch(
    "inspire_json_merger.api.get_configuration",
    return_value=PublisherOnPublisherOperations,
)
def test_merging_same_documents_publisher_on_publisher(fake_get_config):
    root = {
        "documents": [
            {
                "key": "pdf1.pdf",
                "description": "paper",
                "source": "arXiv",
                "fulltext": True,
                "url": "http://example.com/files/1234-1234-1234-1234/pdf1.pdf",
            },
            {
                "key": "pdf.tex",
                "description": "latex version",
                "source": "arXiv",
                "url": "http://example.com/files/1234-1234-1234-1234/pdf.tex",
            },
        ]
    }
    head = root
    update = root
    expected_merged = update
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


@patch(
    "inspire_json_merger.api.get_configuration", return_value=PublisherOnArxivOperations
)
def test_merging_same_documents_publisher_on_arxiv(fake_get_config):
    root = {
        "documents": [
            {
                "key": "pdf1.pdf",
                "description": "paper",
                "source": "arXiv",
                "fulltext": True,
                "url": "http://example.com/files/1234-1234-1234-1234/pdf1.pdf",
            },
            {
                "key": "pdf.tex",
                "description": "latex version",
                "source": "arXiv",
                "url": "http://example.com/files/1234-1234-1234-1234/pdf.tex",
            },
        ]
    }
    head = root
    update = root
    expected_merged = update
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


@patch("inspire_json_merger.api.get_configuration", return_value=ArxivOnArxivOperations)
def test_merging_same_documents_arxiv_on_arxiv(fake_get_config):
    root = {
        "documents": [
            {
                "key": "pdf1.pdf",
                "description": "paper",
                "source": "arXiv",
                "fulltext": True,
                "url": "http://example.com/files/1234-1234-1234-1234/pdf1.pdf",
            },
            {
                "key": "pdf.tex",
                "description": "latex version",
                "source": "arXiv",
                "url": "http://example.com/files/1234-1234-1234-1234/pdf.tex",
            },
        ]
    }
    head = root
    update = root
    expected_merged = head
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


@patch(
    "inspire_json_merger.api.get_configuration", return_value=ArxivOnPublisherOperations
)
def test_merging_same_documents_arxiv_on_publisher(fake_get_config):
    root = {
        "documents": [
            {
                "key": "pdf1.pdf",
                "description": "paper",
                "source": "arXiv",
                "fulltext": True,
                "url": "http://example.com/files/1234-1234-1234-1234/pdf1.pdf",
            },
            {
                "key": "pdf.tex",
                "description": "latex version",
                "source": "arXiv",
                "url": "http://example.com/files/1234-1234-1234-1234/pdf.tex",
            },
        ]
    }
    head = root
    update = root
    expected_merged = update
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_real_record_merge_regression_1_authors_mismatch_on_update():
    root = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "authors": [
            {"full_name": "Elliott"},
            {"full_name": "Chris"},
            {"full_name": "Gwilliam"},
            {"full_name": "Owen"},
        ],
        "titles": [
            {
                "source": "arXiv",
                "title": "Spontaneous symmetry breaking: a view from derived "
                "geometry",
            }
        ],
    }

    head = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "authors": [
            {
                "affiliations": [
                    {
                        "record": {
                            "$ref": "https://inspirehep.net/api/institutions/945696"
                        },
                        "value": "UMass Amherst",
                    },
                    {
                        "record": {
                            "$ref": "https://inspirehep.net/api/institutions/1272963"
                        },
                        "value": "UMASS, Amherst, Dept. Math. Stat.",
                    },
                ],
                "emails": ["celliott@math.umass.edu"],
                "full_name": "Elliott",
                "ids": [{"schema": "INSPIRE BAI", "value": "Elliott.1"}],
                "signature_block": "ELAT",
                "uuid": "65aa01c7-99ec-4c35-ac6b-bbc667a4343e",
            },
            {
                "full_name": "Chris",
                "ids": [{"schema": "INSPIRE BAI", "value": "Chris.1"}],
                "signature_block": "CHR",
                "uuid": "36b3a255-f8f2-46a6-bfae-9e9d00335434",
            },
            {
                "affiliations": [
                    {
                        "record": {
                            "$ref": "https://inspirehep.net/api/institutions/945696"
                        },
                        "value": "UMass Amherst",
                    },
                    {
                        "record": {
                            "$ref": "https://inspirehep.net/api/institutions/1272963"
                        },
                        "value": "UMASS, Amherst, Dept. Math. Stat.",
                    },
                ],
                "emails": ["gwilliam@math.umass.edu"],
                "full_name": "Gwilliam",
                "ids": [{"schema": "INSPIRE BAI", "value": "Gwilliam.1"}],
                "signature_block": "GWALAN",
                "uuid": "66f5722f-e649-4438-a7f5-d01247371f22",
            },
            {
                "full_name": "Owen",
                "ids": [{"schema": "INSPIRE BAI", "value": "Owen.1"}],
                "signature_block": "OWAN",
                "uuid": "27de5ee5-d21a-47b2-b22c-fd44231128f9",
            },
        ],
        "titles": [
            {
                "source": "arXiv",
                "title": "Spontaneous symmetry breaking: a view from derived "
                "geometry",
            }
        ],
    }

    update = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "authors": [{"full_name": "Elliott, Chris"}, {"full_name": "Gwilliam, Owen"}],
        "titles": [
            {
                "source": "arXiv",
                "title": "Spontaneous symmetry breaking: a view from derived "
                "geometry",
            }
        ],
    }
    expected_merged = dict(head)

    expected_conflicts = [
        {
            "path": "/authors/3",
            "op": "replace",
            "value": {"full_name": "Gwilliam, Owen"},
            "$type": "SET_FIELD",
        },
        {
            "path": "/authors/2",
            "op": "replace",
            "value": {"full_name": "Gwilliam, Owen"},
            "$type": "SET_FIELD",
        },
        {
            "path": "/authors/0",
            "op": "replace",
            "value": {"full_name": "Elliott, Chris"},
            "$type": "SET_FIELD",
        },
        {
            "path": "/authors/1",
            "op": "replace",
            "value": {"full_name": "Elliott, Chris"},
            "$type": "SET_FIELD",
        },
    ]

    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert sorted(conflict, key=itemgetter("path")) == sorted(
        expected_conflicts, key=itemgetter("path")
    )


@patch(
    "inspire_json_merger.api.get_configuration", return_value=PublisherOnArxivOperations
)
def test_merging_acquisition_source_publisher_on_arxiv(fake_get_config):
    root = {
        "acquisition_source": {
            "datetime": "2021-05-11T02:35:43.387350",
            "method": "hepcrawl",
            "source": "arXiv",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c0",
        }
    }
    head = {
        "acquisition_source": {
            "datetime": "2021-05-11T02:35:43.387350",
            "method": "hepcrawl",
            "source": "arXiv",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c0",
        }
    }
    update = {
        "acquisition_source": {
            "datetime": "2021-05-12T02:35:43.387350",
            "method": "beard",
            "source": "other source",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c1",
        }
    }
    expected_merged = update
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


@patch(
    "inspire_json_merger.api.get_configuration", return_value=PublisherOnArxivOperations
)
def test_merging_cleans_acquisition_source_for_publisher_on_arxiv(fake_get_config):
    root = {
        "acquisition_source": {
            "datetime": "2021-05-11T02:35:43.387350",
            "method": "hepcrawl",
            "source": "desy",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c0",
        }
    }
    head = {
        "acquisition_source": {
            "datetime": "2021-05-11T02:35:43.387350",
            "method": "hepcrawl",
            "source": "arXiv",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c0",
        }
    }
    update = {
        "acquisition_source": {
            "datetime": "2021-05-12T02:35:43.387350",
            "method": "hepcrawl",
            "source": "desy",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c1",
        }
    }

    merged, conflict = merge(root, head, update)
    assert merged["acquisition_source"]["source"] == "desy"


@patch(
    "inspire_json_merger.api.get_configuration",
    return_value=PublisherOnPublisherOperations,
)
def test_merging_cleans_acquisition_source_for_publisher_on_publisher(fake_get_config):
    root = {
        "acquisition_source": {
            "datetime": "2021-05-11T02:35:43.387350",
            "method": "hepcrawl",
            "source": "desy",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c0",
        }
    }
    head = {
        "acquisition_source": {
            "datetime": "2021-05-11T02:35:43.387350",
            "method": "hepcrawl",
            "source": "elsevier",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c0",
        }
    }
    update = {
        "acquisition_source": {
            "datetime": "2021-05-12T02:35:43.387350",
            "method": "hepcrawl",
            "source": "desy",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c1",
        }
    }

    merged, conflict = merge(root, head, update)
    assert merged["acquisition_source"]["source"] == "desy"


@patch(
    "inspire_json_merger.api.get_configuration", return_value=ArxivOnPublisherOperations
)
def test_merging_cleans_acquisition_source_for_arxiv_on_publisher(fake_get_config):
    root = {
        "acquisition_source": {
            "datetime": "2021-05-11T02:35:43.387350",
            "method": "arXiv",
            "source": "arXiv",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c0",
        }
    }
    head = {
        "acquisition_source": {
            "datetime": "2021-05-11T02:35:43.387350",
            "method": "hepcrawl",
            "source": "desy",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c0",
        }
    }
    update = {
        "acquisition_source": {
            "datetime": "2021-05-12T02:35:43.387350",
            "method": "hepcrawl",
            "source": "arXiv",
            "submission_number": "c8a0e3e0b20011eb8d930a580a6402c1",
        }
    }

    merged, conflict = merge(root, head, update)
    assert merged["acquisition_source"]["source"] == "arXiv"


@patch(
    "inspire_json_merger.api.get_configuration", return_value=ArxivOnPublisherOperations
)
def test_merging_publication_info_for_arxiv_on_publisher(fake_get_config):
    root = {
        "publication_info": [
            {
                "year": 2021,
                "artid": "051701",
                "material": "publication",
                "journal_issue": "5",
                "journal_title": "root title",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1613970"
                },
                "journal_volume": "104",
            }
        ]
    }
    head = {
        "publication_info": [
            {
                "year": 2021,
                "artid": "051701",
                "material": "publication",
                "journal_issue": "5",
                "journal_title": "head title",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1613970"
                },
                "journal_volume": "104",
            }
        ]
    }
    update = {
        "publication_info": [
            {
                "year": 2021,
                "artid": "051701",
                "material": "publication",
                "journal_issue": "5",
                "journal_title": "update title",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1613970"
                },
                "journal_volume": "104",
            }
        ]
    }

    merged, conflict = merge(root, head, update)
    assert len(merged["publication_info"]) == 1
    assert merged["publication_info"][0]["journal_title"] == "head title"


@patch(
    "inspire_json_merger.api.get_configuration",
    return_value=ErratumOnPublisherOperations,
)
def test_merging_erratum(fake_get_config):
    root = {
        "publication_info": [
            {
                "year": 2021,
                "artid": "051701",
                "material": "publication",
                "journal_issue": "5",
                "journal_title": "root title",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1613970"
                },
                "journal_volume": "104",
            }
        ]
    }
    head = {
        "authors": [{"full_name": "Test, Chris"}],
        "dois": [
            {
                "value": "10.1016/j.newast.2021.101676",
                "source": "Elsevier B.V.",
                "material": "publication",
            }
        ],
        "publication_info": [
            {
                "year": 2021,
                "artid": "051701",
                "material": "publication",
                "journal_issue": "5",
                "journal_title": "head title",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1613970"
                },
                "journal_volume": "104",
            }
        ],
        "references": [
            {
                "reference": {
                    "label": "Capozziello and Laurentis, 2011",
                    "authors": [
                        {"full_name": "Laurentis, M.D.", "inspire_role": "author"}
                    ],
                    "publication_info": {
                        "year": 2011,
                        "page_start": "167",
                        "journal_title": "Phys.Rept.",
                        "journal_volume": "509",
                    },
                },
            }
        ],
    }
    update = {
        "authors": [{"full_name": "Elliott, Chris"}, {"full_name": "Gwilliam, Owen"}],
        "dois": [
            {
                "value": "10.1016/j.newast.2021.101678",
                "source": "Elsevier B.V.",
                "material": "publication",
            }
        ],
        "publication_info": [
            {
                "year": 2022,
                "artid": "051703",
                "material": "publication",
                "journal_issue": "10",
                "journal_title": "head title",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1613970"
                },
                "journal_volume": "105",
            }
        ],
        "references": [
            {
                "record": {"$ref": "https://inspirehep.net/api/literature/581605"},
                "reference": {
                    "curated": True,
                    "label": "Capozziello, 2002",
                    "authors": [
                        {"full_name": "Capozziello, S.", "inspire_role": "author"}
                    ],
                    "publication_info": {
                        "year": 2002,
                        "page_start": "483",
                        "journal_title": "Int.J.Mod.Phys.D",
                        "journal_record": {
                            "$ref": "https://inspirehep.net/api/journals/1613976"
                        },
                        "journal_volume": "11",
                    },
                },
            }
        ],
    }

    merged, conflict = merge(root, head, update)
    assert len(merged["publication_info"]) == 2
    assert len(merged["dois"]) == 2
    assert len(merged["references"]) == 2
    assert len(conflict) == 1  # author delete


@patch(
    "inspire_json_merger.api.get_configuration",
    return_value=ErratumOnPublisherOperations,
)
def test_merging_erratum_doesnt_remove_fields(fake_get_config):
    root = {
        "authors": [{"full_name": "Test, Chris"}],
        "dois": [
            {
                "value": "10.1016/j.newast.2021.101676",
                "source": "Elsevier B.V.",
                "material": "publication",
            }
        ],
        "publication_info": [
            {
                "year": 2021,
                "artid": "051701",
                "material": "publication",
                "journal_issue": "5",
                "journal_title": "head title",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1613970"
                },
                "journal_volume": "104",
            }
        ],
        "references": [
            {
                "reference": {
                    "label": "Capozziello and Laurentis, 2011",
                    "authors": [
                        {"full_name": "Laurentis, M.D.", "inspire_role": "author"}
                    ],
                    "publication_info": {
                        "year": 2011,
                        "page_start": "167",
                        "journal_title": "Phys.Rept.",
                        "journal_volume": "509",
                    },
                },
            }
        ],
        "inspire_categories": [{"term": "Lattice"}],
    }
    head = {
        "authors": [{"full_name": "Test, Chris"}],
        "dois": [
            {
                "value": "10.1016/j.newast.2021.101676",
                "source": "Elsevier B.V.",
                "material": "publication",
            }
        ],
        "publication_info": [
            {
                "year": 2021,
                "artid": "051701",
                "material": "publication",
                "journal_issue": "5",
                "journal_title": "head title",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1613970"
                },
                "journal_volume": "104",
            }
        ],
        "references": [
            {
                "reference": {
                    "label": "Capozziello and Laurentis, 2011",
                    "authors": [
                        {"full_name": "Laurentis, M.D.", "inspire_role": "author"}
                    ],
                    "publication_info": {
                        "year": 2011,
                        "page_start": "167",
                        "journal_title": "Phys.Rept.",
                        "journal_volume": "509",
                    },
                },
            }
        ],
        "inspire_categories": [{"term": "Lattice"}],
    }
    update = {
        "authors": [{"full_name": "Elliott, Chris"}, {"full_name": "Gwilliam, Owen"}],
        "dois": [
            {
                "value": "10.1016/j.newast.2021.101678",
                "source": "Elsevier B.V.",
                "material": "publication",
            }
        ],
    }

    merged, conflict = merge(root, head, update)
    assert "publication_info" in merged
    assert "authors" in merged
    assert "references" in merged
    assert "inspire_categories" in merged
    assert len(merged["dois"]) == 2


@patch(
    "inspire_json_merger.api.get_configuration",
    return_value=ErratumOnPublisherOperations,
)
def test_merging_copyright(fake_get_config):
    root = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "abstracts": [
            {
                "source": "arXiv",
                "value": "Based on previously published multi-wavelength modelling of the GRB 170817A jet afterglow, that includes information from the VLBI centroid motion, we construct the posterior probability density distribution on the total energy in the bipolar jets launched by the GW170817 merger remnant. By applying a new numerical-relativity-informed fitting formula for the accretion disk mass, we construct the posterior probability density distribution of the GW170817 remnant disk mass. By combining the two, we estimate the accretion-to-jet energy conversion efficiency in this system, carefully accounting for uncertainties. The accretion-to-jet energy conversion efficiency in GW170817 is $\\eta\\sim 10^{-3}$ with an uncertainty of slightly less than two orders of magnitude. This low efficiency is in good agreement with expectations from the $\\nu\\bar\\nu$ mechanism, which therefore cannot be excluded by this measurement alone. Such an efficiency also agrees with that anticipated for the Blandford-Znajek mechanism, provided that the magnetic field in the disk right after the merger is predominantly toroidal (which is expected as a result of the merger dynamics).",
            }
        ],
        "acquisition_source": {
            "datetime": "2022-04-21T02:32:36.958272",
            "method": "hepcrawl",
            "source": "arXiv",
            "submission_number": "f12410b0c11a11eca59ef61506530229",
        },
        "arxiv_eprints": [{"categories": ["astro-ph.HE"], "value": "2006.07376"}],
        "authors": [
            {
                "full_name": "Salafia, Om S.",
                "raw_affiliations": [
                    {
                        "value": "INAF -Osservatorio Astronomico di Brera, via E. Bianchi 46, I-23807 Merate (LC), Italy"
                    },
                    {
                        "value": "INFN -Sezione di Milano-Bicocca, Piazza della Scienza 3, I-20126 Milano (MI), Italy"
                    },
                ],
            },
            {
                "full_name": "Giacomazzo, Bruno",
                "raw_affiliations": [
                    {
                        "value": "INAF -Osservatorio Astronomico di Brera, via E. Bianchi 46, I-23807 Merate (LC), Italy"
                    },
                    {
                        "value": "INFN -Sezione di Milano-Bicocca, Piazza della Scienza 3, I-20126 Milano (MI), Italy"
                    },
                    {
                        "value": 'Universit\xe0 degli Studi di Milano-Bicocca, Dip. di Fisica "G. Occhialini", Piazza della Scienza 3, I-20126 Milano, Italy'
                    },
                ],
            },
        ],
        "citeable": True,
        "curated": False,
        "document_type": ["article"],
        "documents": [
            {
                "fulltext": True,
                "hidden": True,
                "key": "2006.07376.pdf",
                "material": "preprint",
                "original_url": "http://export.arxiv.org/pdf/2006.07376",
                "source": "arxiv",
                "url": "/api/files/f09c7613-e9c7-414f-a74e-b8c2f81f308b/2006.07376.pdf",
            }
        ],
        "dois": [
            {
                "material": "publication",
                "source": "arXiv",
                "value": "10.1051/0004-6361/202038590e",
            }
        ],
        "figures": [
            {
                "caption": "GW170817 accretion disc mass posterior distributions. The solid red line shows the posterior probability distribution of the logarithm of the accretion disc mass (in solar masses) for the low-spin LVC priors. The dashed blue line shows the corresponding result that would have been obtained using the disc mass fitting formula from \\citet{Radice2018}.",
                "key": "disk_mass.png",
                "label": "fig:disc_mass_posterior",
                "material": "preprint",
                "source": "arxiv",
                "url": "/api/files/f09c7613-e9c7-414f-a74e-b8c2f81f308b/disk_mass.png",
            }
        ],
        "inspire_categories": [{"source": "arxiv", "term": "Astrophysics"}],
        "license": [
            {
                "license": "arXiv nonexclusive-distrib 1.0",
                "material": "preprint",
                "url": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
            }
        ],
        "number_of_pages": 11,
        "preprint_date": "2020-06-12",
        "public_notes": [
            {
                "source": "arXiv",
                "value": "11 pages, 6 figures, reflects the A&A published version, with\n equation 1 corrected as described in the corrigendum published on A&A",
            }
        ],
        "publication_info": [
            {
                "artid": "C1",
                "journal_title": "Astron.Astrophys.",
                "journal_volume": "660",
                "material": "publication",
                "page_start": "C1",
                "pubinfo_freetext": "A&A 660, C1 (2022)",
                "year": 2022,
            }
        ],
        "titles": [
            {
                "source": "arXiv",
                "title": "Accretion-to-jet energy conversion efficiency in GW170817",
            }
        ],
    }

    head = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "_private_notes": [
            {"value": "Astrophysical processes"},
            {"value": "DOKIFILE:aanda2022.04"},
            {"value": "added fieldcode by note"},
        ],
        "abstracts": [
            {
                "source": "EDP Sciences",
                "value": "Gamma-ray bursts (GRBs) are thought to be produced by short-lived, supercritical accretion onto a newborn compact object. Some process is believed to tap energy from the compact object, or the accretion disc, powering the launch of a relativistic jet. For the first time, we can construct independent estimates of the GRB jet energy and of the mass in the accretion disc in its central engine; this is thanks to gravitational wave observations of the GW170817 binary neutron star merger by the Laser Interferometer Gravitational wave Observatory (LIGO) and Virgo interferometers, as well as a global effort to monitor the afterglow of the associated short gamma-ray burst GRB 170817A on a long-term, high-cadence, multi-wavelength basis. In this work, we estimate the accretion-to-jet energy conversion efficiency in GW170817, that is, the ratio of the jet total energy to the accretion disc rest mass energy, and we compare this quantity with theoretical expectations from the Blandford-Znajek and neutrino-antineutrino annihilation (\u03bd\u03bd\u0304) jet-launching mechanisms in binary neutron star mergers. Based on previously published multi-wavelength modelling of the GRB 170817A jet afterglow, we construct the posterior probability density distribution of the total energy in the bipolar jets launched by the GW170817 merger remnant. By applying a new numerical-relativity-informed fitting formula for the accretion disc mass, we construct the posterior probability density distribution of the GW170817 remnant disc mass. Combining the two, we estimate the accretion-to-jet energy conversion efficiency in this system, carefully accounting for uncertainties. The accretion-to-jet energy conversion efficiency in GW170817 is \u03b7\u2004\u223c\u200410\u22123, with an uncertainty of slightly less than two orders of magnitude. This low efficiency is in agreement with expectations from the mechanism, which therefore cannot be excluded by this measurement alone. The low efficiency also agrees with that anticipated for the Blandford-Znajek mechanism, provided that the magnetic field in the disc right after the merger is predominantly toroidal (which is expected as a result of the merger dynamics). This is the first estimate of the accretion-to-jet energy conversion efficiency in a GRB that combines independent estimates of the jet energy and accretion disc mass. Future applications of this method to a larger number of systems will reduce the uncertainties in the efficiency and reveal whether or not it is universal. This, in turn, will provide new insights into the jet-launching conditions in neutron star mergers.Key words: relativistic processes / gamma-ray burst: individual: GRB 170817A / stars: neutron / gravitational waves",
            },
            {
                "source": "arXiv",
                "value": "Based on previously published multi-wavelength modelling of the GRB 170817A jet afterglow, that includes information from the VLBI centroid motion, we construct the posterior probability density distribution on the total energy in the bipolar jets launched by the GW170817 merger remnant. By applying a new numerical-relativity-informed fitting formula for the accretion disk mass, we construct the posterior probability density distribution of the GW170817 remnant disk mass. By combining the two, we estimate the accretion-to-jet energy conversion efficiency in this system, carefully accounting for uncertainties. The accretion-to-jet energy conversion efficiency in GW170817 is $\\eta\\sim 10^{-3}$ with an uncertainty of slightly less than two orders of magnitude. This low efficiency is in good agreement with expectations from the $\\nu\\bar\\nu$ mechanism, which therefore cannot be excluded by this measurement alone. Such an efficiency also agrees with that anticipated for the Blandford-Znajek mechanism, provided that the magnetic field in the disk right after the merger is predominantly toroidal (which is expected as a result of the merger dynamics).",
            },
        ],
        "acquisition_source": {
            "datetime": "2022-04-21T02:32:36.958272",
            "method": "hepcrawl",
            "source": "arXiv",
            "submission_number": "4204775",
        },
        "arxiv_eprints": [{"categories": ["astro-ph.HE"], "value": "2006.07376"}],
        "authors": [
            {
                "curated_relation": True,
                "full_name": "Salafia, Om S.",
                "ids": [
                    {"schema": "ORCID", "value": "0000-0003-4924-7322"},
                    {"schema": "INSPIRE BAI", "value": "O.S.Salafia.1"},
                ],
                "raw_affiliations": [
                    {
                        "value": "INAF -Osservatorio Astronomico di Brera, via E. Bianchi 46, I-23807 Merate (LC), Italy"
                    },
                    {
                        "value": "INFN -Sezione di Milano-Bicocca, Piazza della Scienza 3, I-20126 Milano (MI), Italy"
                    },
                ],
                "record": {"$ref": "https://inspirehep.net/api/authors/1598567"},
                "signature_block": "SALAFo",
                "uuid": "255571f0-f7da-478b-a4e5-9453faa93567",
            },
            {
                "curated_relation": True,
                "full_name": "Giacomazzo, Bruno",
                "ids": [
                    {"schema": "ORCID", "value": "0000-0002-6947-4023"},
                    {"schema": "INSPIRE BAI", "value": "B.Giacomazzo.1"},
                ],
                "raw_affiliations": [
                    {
                        "value": "INAF -Osservatorio Astronomico di Brera, via E. Bianchi 46, I-23807 Merate (LC), Italy"
                    },
                    {
                        "value": "INFN -Sezione di Milano-Bicocca, Piazza della Scienza 3, I-20126 Milano (MI), Italy"
                    },
                    {
                        "value": 'Universit\xe0 degli Studi di Milano-Bicocca, Dip. di Fisica "G. Occhialini", Piazza della Scienza 3, I-20126 Milano, Italy'
                    },
                ],
                "record": {"$ref": "https://inspirehep.net/api/authors/1056614"},
                "signature_block": "GACANASb",
                "uuid": "a6ce958e-0a59-449c-88ca-957ea5ff7d04",
            },
        ],
        "citeable": True,
        "control_number": 1801194,
        "curated": True,
        "document_type": ["article"],
        "documents": [
            {
                "filename": "2006.07376.pdf",
                "fulltext": True,
                "hidden": True,
                "key": "c36bfb47ee8e15627a042a65a0d7f348",
                "material": "preprint",
                "original_url": "http://export.arxiv.org/pdf/2006.07376",
                "source": "arxiv",
                "url": "https://inspirehep.net/files/c36bfb47ee8e15627a042a65a0d7f348",
            }
        ],
        "dois": [
            {
                "material": "publication",
                "source": "arXiv",
                "value": "10.1051/0004-6361/202038590",
            },
            {
                "material": "erratum",
                "source": "EDP Sciences",
                "value": "10.1051/0004-6361/202038590e",
            },
        ],
        "figures": [
            {
                "caption": "GW170817 accretion disc mass posterior distributions. The solid red line shows the posterior probability distribution of the logarithm of the accretion disc mass (in solar masses) for the low-spin LVC priors. The dashed blue line shows the corresponding result that would have been obtained using the disc mass fitting formula from \\citet{Radice2018}.",
                "filename": "disk_mass.png",
                "key": "3a646ab3fbde76e1d6aa2489de70076d",
                "label": "fig:disc_mass_posterior",
                "material": "preprint",
                "source": "arxiv",
                "url": "https://inspirehep.net/files/3a646ab3fbde76e1d6aa2489de70076d",
            }
        ],
        "imprints": [{"date": "2021-01-01"}, {"date": "2022-04-01"}],
        "inspire_categories": [
            {"source": "arxiv", "term": "Astrophysics"},
            {"term": "Astrophysics"},
        ],
        "keywords": [
            {"source": "author", "value": "relativistic processes"},
            {"source": "author", "value": "gamma-ray burst: individual: GRB 170817A"},
            {"source": "author", "value": "stars: neutron"},
            {"source": "author", "value": "gravitational waves"},
            {"source": "author", "value": "errata, addenda"},
        ],
        "legacy_creation_date": "2020-06-16",
        "legacy_version": "20210227185457.0",
        "license": [
            {
                "license": "arXiv nonexclusive-distrib 1.0",
                "material": "preprint",
                "url": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
            }
        ],
        "number_of_pages": 1,
        "preprint_date": "2020-06-12",
        "public_notes": [
            {
                "source": "arXiv",
                "value": "11 pages, 6 figures, reflects the A&A published version, with\n equation 1 corrected as described in the corrigendum published on A&A",
            }
        ],
        "publication_info": [
            {
                "artid": "A93",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1214902"
                },
                "journal_title": "Astron.Astrophys.",
                "journal_volume": "645",
                "material": "publication",
                "page_start": "A93",
                "pubinfo_freetext": "A&A 645, A93 (2021)",
                "year": 2021,
            },
            {
                "artid": "C1",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1214902"
                },
                "journal_title": "Astron.Astrophys.",
                "journal_volume": "660",
                "material": "erratum",
                "page_start": "C1",
                "year": 2022,
            },
        ],
        "refereed": True,
        "self": {"$ref": "https://inspirehep.net/api/literature/1801194"},
        "texkeys": ["Salafia:2020jro"],
        "titles": [
            {
                "source": "EDP Sciences",
                "title": "Accretion-to-jet energy conversion efficiency in GW170817 (Corrigendum)",
            },
            {
                "source": "arXiv",
                "title": "Accretion-to-jet energy conversion efficiency in GW170817",
            },
        ],
    }

    update = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "_files": [
            {
                "bucket": "be3526f9-36cc-4ac8-902d-13afc47c5305",
                "checksum": "md5:3afbe8b304ce8389c32405781f8cf026",
                "file_id": "5888b3fb-681d-445d-98ea-79541cc052b6",
                "key": "document",
                "size": 121813,
                "version_id": "2e30f486-49a8-407d-94af-3fbb1377b2fb",
            }
        ],
        "_private_notes": [
            {"value": "Erratum"},
            {
                "value": "1 combined refs (0 IDs differ, 1 IDs coincide, 0 DOIs/0 bulls added from SISSA, 0 IDs missing in SISSA)"
            },
            {"value": "DOKIFILE:jhep2205.140-2130"},
        ],
        "acquisition_source": {
            "datetime": "2022-05-22T09:59:37.368617",
            "method": "hepcrawl",
            "source": "desy",
            "submission_number": "b2125716d9b511eca1ec027989e7b925",
        },
        "arxiv_eprints": [{"value": "2007.15018"}],
        "authors": [
            {
                "affiliations_identifiers": [
                    {"schema": "GRID", "value": "grid.27755.32"}
                ],
                "emails": ["parnold@virginia.ed"],
                "full_name": "Arnold, Peter",
                "raw_affiliations": [
                    {
                        "value": "Department of Physics, University of Virginia, 22904-4714 Charlottesville, Virginia, USA"
                    }
                ],
            },
            {
                "affiliations_identifiers": [
                    {"schema": "GRID", "value": "grid.27755.32"},
                    {"schema": "GRID", "value": "grid.6546.1"},
                ],
                "full_name": "Gorda, Tyler",
                "ids": [{"schema": "ORCID", "value": "0000-0003-3469-7574"}],
                "raw_affiliations": [
                    {
                        "value": "Department of Physics, University of Virginia, 22904-4714 Charlottesville, Virginia, USA"
                    },
                    {
                        "value": "Technische Universit\xe4t Darmstadt, Department of Physics, 64289 Darmstadt, Germany"
                    },
                ],
            },
            {
                "affiliations_identifiers": [
                    {"schema": "GRID", "value": "grid.411407.7"}
                ],
                "full_name": "Iqbal, Shahin",
                "ids": [{"schema": "ORCID", "value": "0000-0001-8640-9963"}],
                "raw_affiliations": [
                    {
                        "value": "Institute of Particle Physics, Central China Normal University, 430079 Wuhan, China"
                    }
                ],
            },
        ],
        "citeable": True,
        "curated": False,
        "document_type": ["article"],
        "documents": [
            {
                "fulltext": True,
                "key": "document",
                "url": "/api/files/be3526f9-36cc-4ac8-902d-13afc47c5305/document",
            }
        ],
        "dois": [{"source": "Springer", "value": "10.1007/JHEP05(2022)114"}],
        "imprints": [{"date": "2022-05-18"}],
        "license": [
            {
                "imposing": "Springer",
                "license": "CC-BY-4.0",
                "url": "http://creativecommons.org/licenses/by/4.0/",
            }
        ],
        "publication_info": [
            {
                "artid": "114",
                "journal_record": {
                    "$ref": "https://inspirehep.net/api/journals/1213103"
                },
                "journal_title": "JHEP",
                "journal_volume": "05",
                "page_start": "114",
                "year": 2022,
            }
        ],
        "refereed": True,
        "titles": [
            {
                "source": "Springer",
                "title": "Erratum to: The LPM effect in sequential bremsstrahlung: nearly complete results for QCD [doi: 10.1007/JHEP11(2020)053]",
            }
        ],
    }

    merged, conflict = merge(root, head, update)
    assert "copyright" not in merged
    assert "persistent_identifiers" not in merged
