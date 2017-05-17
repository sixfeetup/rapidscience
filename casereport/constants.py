__author__ = 'yaseen'


GENDER = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('transgender_male', 'Transgender Male'),
    ('transgender_female', 'Transgender Female'),
    ('other', 'Other'),
)


class WorkflowState(object):
    # visualize with:
    # ./manage.py graph_transitions casereport.CaseReport  > t.dot; dot -O -Tpng t.dot; open t.dot.png

    DRAFT = 'draft'
    ADMIN_REVIEW = 'processing'
    AUTHOR_REVIEW = 'author review'
    LIVE = 'live'
    RETRACTED = 'retracted'  # this is a tranistional state that is held only
                             # long enough for the system to push it back to
                             # ADMIN_REVIEW or AUTHOR_REVIEW

    CHOICES = (
        (DRAFT, DRAFT.title()),
        (ADMIN_REVIEW, ADMIN_REVIEW.title()),
        (AUTHOR_REVIEW, AUTHOR_REVIEW.title()),
        (LIVE,LIVE.title())
    )

    INITIAL_STATE = DRAFT

    ICONS = {
        DRAFT:          'fa fa-clock-o',
        AUTHOR_REVIEW:  'fa fa-clock-o',
        ADMIN_REVIEW:   'fa fa-check',
        LIVE:           'fa fa-file-text-o',
        RETRACTED:      None
    }



TYPE = (
            ('test', 'Test'),
            ('treatment', 'Treatment'),
            ('diagnosis', 'Diagnosis'),

    )

TREATMENT_INTENT = (
    ('Neoadjuvant', 'Neoadjuvant'),
    ('Adjuvant', 'Adjuvant'),
    ('Metastatic/Advanced', 'Metastatic/Advanced'),
    ('Palliative', 'Palliative'),
)

APPROVED = 'approved'

SARCOMA_TYPE = (
            ("Fat tissue tumours", "Fat tissue tumours"),
            ("Muscle tissue tumours", "Muscle tissue tumours"),
            ("Peripheral nerve tumours", "Peripheral nerve tumours"),
            ("Fibrous tissue tumours", "Fibrous tissue tumours"),
            ("Joint tissue tumours", "Joint tissue tumours"),
            ("Blood and lymph vessel tumours", "Blood and lymph vessel tumours"),
            ("Rarer types of sarcoma", "Rarer types of sarcoma"),
            ("Alveolar soft part sarcoma", "Alveolar soft part sarcoma"),
            ("Dermatofibrosarcoma protuberans (DFSP)", "Dermatofibrosarcoma protuberans (DFSP)"),
            ("Epithelioid sarcoma", "Epithelioid sarcoma"),
            ("Extraskeletal myxoid chondrosarcoma", "Extraskeletal myxoid chondrosarcoma"),
            ("Giant cell fibroblastoma (GCF)", "Giant cell fibroblastoma (GCF)"),
            ("Acute lymphoblastic leukaemia", "Acute lymphoblastic leukaemia"),
            ("Acute myeloid leukaemia", "Acute myeloid leukaemia"),
            ("Ewing's sarcoma", "Ewing's sarcoma"),
            ("Hodgkin lymphoma", "Hodgkin lymphoma"),
            ("Brain tumours", "Brain tumours"),
            ("Germ cell tumours", "Germ cell tumours"),
            ("Neuroblastoma", "Neuroblastoma"),
            ("Retinoblastoma", "Retinoblastoma"),
            ("Wilms' tumour", "Wilms' tumour"),
            ("Osteosarcoma", "Osteosarcoma"),
            ("Sarcoma", "Sarcoma"),
            ("Lipoma", "Lipoma"),
            ("Lipomatosis", "Lipomatosis"),
            ("Lipoma of nerve", "Lipoma of nerve"),
            ("Lipoblastoma/Lipoblastomatosis", "Lipoblastoma/Lipoblastomatosis"),
            ("Angiolipoma", "Angiolipoma"),
            ("Myolipoma", "Myolipoma"),
            ("Chondriod lipoma", "Chondriod lipoma"),
            ("Extra-renal angiolipoma", "Extra-renal angiolipoma"),
            ("Extra-adrenal myelolipoma", "Extra-adrenal myelolipoma"),
            ("Spindle cell/pleomorphic lipoma", "Spindle cell/pleomorphic lipoma"),
            ("Malignant peripheral nerve sheath tumour", "Malignant peripheral nerve sheath tumour"),
            ("Epithelioid malignant peripheral nerve sheath tumour", "Epithelioid malignant peripheral nerve sheath tumour"),
            ("Malignant Triton tumour", "Malignant Triton tumour"),
            ("Malignant granular cell tumour", "Malignant granular cell tumour"),
            ("Ectomesenchymoma", "Ectomesenchymoma"),
            ("Acral fibromyxoma", "Acral fibromyxoma"),
            ("Intramuscular myxoma", "Intramuscular myxoma"),
            ("Juxta-articular myxoma", "Juxta-articular myxoma"),
            ("Deep ('aggressive') angiomyxoma", "Deep ('aggressive') angiomyxoma"),
            ("Pleomorphic hyalinizing angiectatic tumour", "Pleomorphic hyalinizing angiectatic tumour"),
            ("Ectopic hamartornatous thymoma", "Ectopic hamartornatous thymoma"),
            ("Haemosiderotic fibrolipomatous tumour", "Haemosiderotic fibrolipomatous tumour"),
            ("Atypical fibroxanthorma", "Atypical fibroxanthorma"),
            ("Angiomatoid fibrous histiocytoma", "Angiomatoid fibrous histiocytoma"),
            ("Ossifying fibromyxoid tumour", "Ossifying fibromyxoid tumour"),
            ("Mixed tumour NOS", "Mixed tumour NOS"),
            ("Mixed tumour NOS, malignant", "Mixed tumour NOS, malignant"),
            ("Myoepitheliorna", "Myoepitheliorna"),
            ("Myoepithelial carcinoma", "Myoepithelial carcinoma"),
            ("Phosphaturic mesenchymal tumour, benign", "Phosphaturic mesenchymal tumour, benign"),
            ("Phosphaturic mesenchymal tumour, malignant", "Phosphaturic mesenchymal tumour, malignant"),
            ("Synovial sarcoma NOS", "Synovial sarcoma NOS"),
            ("Synovial sarcoma, spindle cell", "Synovial sarcoma, spindle cell"),
            ("Synovial sarcoma, biphasic", "Synovial sarcoma, biphasic"),
            ("Clear cell sarcoma of soft tissue", "Clear cell sarcoma of soft tissue"),
            ("Extraskeletal Ewing sarcoma", "Extraskeletal Ewing sarcoma"),
            ("Desmoplastic small round cell tumour", "Desmoplastic small round cell tumour"),
            ("Extra-renal rhabdoid tumour", "Extra-renal rhabdoid tumour"),
            ("Neoplasms with perivascular epithelioid", "Neoplasms with perivascular epithelioid"),
            ("Cell differentiation (PEComa)", "Cell differentiation (PEComa)"),
            ("PEComa NOS, benign", "PEComa NOS, benign"),
            ("PEComa NOS, malignant", "PEComa NOS, malignant"),
            ("Undifferentiated spindle cell sarcoma", "Undifferentiated spindle cell sarcoma"),
            ("Undifferentiated pleomorphic sarcoma", "Undifferentiated pleomorphic sarcoma"),
            ("Undifferentiated round cell sarcoma", "Undifferentiated round cell sarcoma"),
            ("Undifferentiated sarcoma NOS", "Undifferentiated sarcoma NOS"),
            ('Hybrid nerve sheath tumours','Hybrid nerve sheath tumours'),
            ("Granular cell tumour","Granular cell tumour"),
            ("Malignant perineurioma","Malignant perineurioma"),
            ("Angiosarcoma of soft tissue","Angiosarcoma of soft tissue"),
            ("Hibernoma", "Hibernoma"),
            ("Atypical lipomatous tumour/well differentiated liposarcoma", "Atypical lipomatous tumour/well differentiated liposarcoma"),
            ("Differentiated liposarcoma", "Differentiated liposarcoma"),
            ("Myxoid liposarcoma", "Myxoid liposarcoma"),
            ("Pleomorphic liposarcoma", "Pleomorphic liposarcoma"),
            ("Liposarcoma", "Liposarcoma"),
            ("Nodular fasciitis", "Nodular fasciitis"),
            ("Proliferative fasciitis", "Proliferative fasciitis"),
            ("Proliferative myositis", "Proliferative myositis"),
            ("Myositis ossificans","Myositis ossificans"),
            ("Fibro-osseous pseudotumour of digits", "Fibro-osseous pseudotumour of digits"),
            ("Ischaemic fasciitis", "Ischaemic fasciitis"),
            ("Elastafibroma", "Elastafibroma"),
            ("Fibrous hamartoma of infancy", "Fibrous hamartoma of infancy"),
            ("Fibromatosis colli", "Fibromatosis colli"),
            ("Juvenile hyaline fibromatosis", "Juvenile hyaline fibromatosis"),
            ("Inclusion body fibromatosis ", "Inclusion body fibromatosis "),
            ("Fibroma of tendon sheath", "Fibroma of tendon sheath"),
            ("Mammary-type myofibroblastoma ", "Mammary-type myofibroblastoma"),
            ("Catcifying aponeurotic fibroma ", "Catcifying aponeurotic fibroma "),
            ("Cellular angiofibroma ", "Cellular angiofibroma "),
            ("Angiomyofibroblastoma", "Angiomyofibroblastoma"),
            ("Nuchal-type fibroma", "Nuchal-type fibroma"),
            ("Gardner fibroma", "Gardner fibroma"),
            ("Calcifying fibrous ", "Calcifying fibrous "),
            ("Palmar/plantar  fibromatosis", "Palmar/plantar  fibromatosis"),
            ("Desmoid-type fibromatosis", "Desmoid-type fibromatosis"),
            ("Lipofibromatosis", "Lipofibromatosis"),
            ("Giant semi fibrobiastoma", "Giant semi fibrobiastoma"),
            ("Dermatafibrosarcoma protuberans ", "Dermatafibrosarcoma protuberans "),
            ("Protubarans", "Protubarans"),
            ("Solitary fibrous tumour", "Solitary fibrous tumour"),
            ("Inflammatory myofibroblastic tumour", "Inflammatory myofibroblastic tumour"),
            ("Inflammatory myxoinflammatory fibroblastic", "Inflammatory myxoinflammatory fibroblastic"),
            ("Atypical myxoinflammatory fibroblastic tumour ", "Atypical myxoinflammatory fibroblastic tumour "),
            ("Low-grade  myxoinflammatory Sarcoma", "Low-grade  myxoinflammatory Sarcoma"),
            ("Infantile fibrosarcoma", "Infantile fibrosarcoma"),
            ("Adult fibrosarcoma", "Adult fibrosarcoma"),
            ("Myxofibrosarcoma", "Myxofibrosarcoma"),
            ("Low-grade fibromyxoid sarcoma", "Low-grade fibromyxoid sarcoma"),
            ("Sclerosing epithelioid fibrosarcoma", "Sclerosing epithelioid fibrosarcoma"),
            ("Tenosynovial giant cell tumour", "Tenosynovial giant cell tumour"),
            ("Deep benign fibrous histiocytoma", "Deep benign fibrous histiocytoma"),
            ("Plexiform fibrohistiocytic tumour ", "Plexiform fibrohistiocytic tumour "),
            ("Giant cell tumour of soft tissues", "Giant cell tumour of soft tissues"),
            ("Deep leiomyoma", "Deep lelomyoma"),
            ("Leiomyosarcoma (excluding skin)", "Leiomyosarcoma (excluding skin)"),
            ("Glomangiomatosis", "Glomangiomatosis"),
            ("Glomus tumour (and variants)", "Glomus tumour (and variants)"),
            ("Malignant glomus tumour", "Malignant glomus tumour"),
            ("Myopericytoma", "Myopericytoma"),
            ("Myofibroma", "Myofibroma"),
            ("Myofibromatosis", "Myofibromatosis"),
            ("Angioleiomyoma", "Angioleiomyoma"),
            ("Rhabdomyoma", "Rhabdomyoma"),
            ("Adult type ", "Adult type "),
            ("Fetal type ", "Fetal type "),
            ("Genital type ", "Genital type "),
            ("Embryonal rhabdomyosarcoma", "Embryonal rhabdomyosarcoma"),
            ("Alveolar rhabdomyosarcoma", "Alveolar rhabdomyosarcoma"),
            ("Plaomorphic rhabdomyosarcoma", " Plaomorphic rhabdomyosarcoma"),
            ("Spindle cell/sclerosing rhabdomyosarcoma", "Spindle cell/sclerosing rhabdomyosarcoma"),
            ("Osteochondroma", "Osteochondroma"),
            ("Chondroma", "Chondroma"),
            ("Enchondroma", "Enchondroma"),
            ("Periosteal Chondroma", "Periosteal Chondroma"),
            ("Osteochondromyxoma", "Osteochondromyxoma"),
            ("Sublingual exostosis", "Sublingual exostosis"),
            ("Bizarre parosteal osteochondromatous", "Bizarre parosteal osteochondromatous"),
            ("Proliferation", "Proliferation"),
            ("Synovial chondromatosis", "Synovial chondromatosis"),
            ("Chondromyxoid fibroma", "Chondromyxoid fibroma"),
            ("Atypical cartilaginous tumour/ Chondrosarcoma grade I", "Atypical cartilaginous tumour/ Chondrosarcoma grade I"),
            ("Chondroblastoma", "Chondroblastoma"),
            ("Chondrosarcoma Grade II", "Chondrosarcoma Grade II"),
            ("Chondrosarcoma Grade II", "Chondrosarcoma Grade III"),
            ("Dedifferentiated chondrosarcoma", "Dedifferentiated chondrosarcoma"),
            ("Mesenchymal chondrosarcoma", "Mesenchymal chondrosarcoma chondrosarcoma"),
            ("Clear cell chondrosarcoma", "Clear cell chondrosarcoma"),
            ("Osteoma", "Osteoma"),
            ("Osteoid osteoma", "Osteoid osteoma"),
            ("Osteoblastoma", "Osteoblastoma"),
            ("Low-grade central osteosarcoma", "Low-grade central osteosarcoma"),
            ("Conventional osteosarcoma", "Conventional osteosarcoma"),
            ("Chondroblastic osteosarcoma", "Chondroblastic osteosarcoma"),
            ("Fibroblastic osteosarcoma", "Fibroblastic osteosarcoma"),
            ("Osteoblastic osteosarcoma", "Osteoblastic osteosarcoma"),
            ("Telangiectatic osteosarcoma", "Telangiectatic osteosarcoma"),
            ("Small cell osteosarcoma", "Small cell osteosarcoma"),
            ("Secondary osteosarcoma", "Secondary osteosarcoma"),
            ("Parosteal osteosarcoma", "Parosteal osteosarcoma"),
            ("Periosteal osteosarcoma", "Periosteal osteosarcoma"),
            ("High-grade surface osteosarcoma", "High-grade surface osteosarcoma"),
            ("Desmoplastic fibroma of bone ", "Desmoplastic fibroma of bone "),
            ("Fibrosarcoma of bone", "Fibrosarcoma of bone"),
            ("Benign fibrous histiocytoma/ Non-ossifying fibroma", "Benign fibrous histiocytoma/ Non-ossifying fibroma"),
            ("Plasma cell myeloma", "Plasma cell myeloma"),
            ("Solitary plasmacytoma of bone", "Solitary plasmacytoma of bone"),
            ("Primary non-Hodgkin lymphoma of bone", "Primary non-Hodgkin lymphoma of bone"),
            ("Giant cell lesion of the small bones", "Giant cell lesion of the small bones"),
            ("Giant cell tumour of bone", "Giant cell tumour of bone"),
            ("Malignancy in giant cell tumour of bone", "Malignancy in giant cell tumour of bone"),
            ("Benign notochordal tumour", "Benign notochordal tumour"),
            ("Chordoma", "Chordoma"),
            ("Haemangioma", "Haemangioma"),
            ("Epithelioid haemangioma", "Epithelioid haemangioma"),
            ("Angiosarcoma", "Angiosarcoma"),
            ("Malignant Liposarcoma of bone", "Malignant Liposarcoma of bone"),
            ("Aneurysmal bone cyst", "Aneurysmal bone cyst"),
            ("Langerhans cell histiocytosis", "Langerhans cell histiocytosis"),
            ("Erdheim-Chester disease", "Erdheim-Chester disease"),
            ("Ewing sarcoma", "Ewing sarcoma"),
            ("Adamantinoma", "Adamantinoma"),
            ("Undifferentiated high-grade pleomorphic sarcoma of bone", "Undifferentiated high-grade pleomorphic sarcoma of bone"),
            ("Lipoma of bone", "Lipoma of bone"),
            ("Lipomasarcoma of bone", "Lipomasarcoma of bone"),
            ("Simple bone cyst", "Simple bone cyst"),
            ("Fibrous dyplasia", "Fibrous dyplasia"),
            ("Osteofibrcus dysplasia", "Osteofibrcus dysplasia"),
            ("Chondromesenchymal hamartoma", "Chondromesenchymal hamartoma"),
            ("Rosai-Dorfman disease", "Rosai-Dorfman disease"),
            ("Other","Other")
    )

COUNTRIES = [
    ("AF", "Afghanistan"),
    ("AX", "Aland Islands"),
    ("AL", "Albania"),
    ("DZ", "Algeria"),
    ("AS", "American Samoa"),
    ("AD", "Andorra"),
    ("AO", "Angola"),
    ("AI", "Anguilla"),
    ("AQ", "Antarctica"),
    ("AG", "Antigua and Barbuda"),
    ("AR", "Argentina"),
    ("AM", "Armenia"),
    ("AW", "Aruba"),
    ("AU", "Australia"),
    ("AT", "Austria"),
    ("AZ", "Azerbaijan"),
    ("BS", "Bahamas"),
    ("BH", "Bahrain"),
    ("BD", "Bangladesh"),
    ("BB", "Barbados"),
    ("BY", "Belarus"),
    ("BE", "Belgium"),
    ("BZ", "Belize"),
    ("BJ", "Benin"),
    ("BM", "Bermuda"),
    ("BT", "Bhutan"),
    ("BO", "Bolivia (Plurinational State of)"),
    ("BQ", "Bonaire, Sint Eustatius and Saba"),
    ("BA", "Bosnia and Herzegovina"),
    ("BW", "Botswana"),
    ("BV", "Bouvet Island"),
    ("BR", "Brazil"),
    ("IO", "British Indian Ocean Territory"),
    ("BN", "Brunei Darussalam"),
    ("BG", "Bulgaria"),
    ("BF", "Burkina Faso"),
    ("BI", "Burundi"),
    ("CV", "Cabo Verde"),
    ("KH", "Cambodia"),
    ("CM", "Cameroon"),
    ("CA", "Canada"),
    ("KY", "Cayman Islands"),
    ("CF", "Central African Republic"),
    ("TD", "Chad"),
    ("CL", "Chile"),
    ("CN", "China"),
    ("CX", "Christmas Island"),
    ("CC", "Cocos (Keeling) Islands"),
    ("CO", "Colombia"),
    ("KM", "Comoros"),
    ("CD", "Congo (the Democratic Republic of the)"),
    ("CG", "Congo"),
    ("CK", "Cook Islands"),
    ("CR", "Costa Rica"),
    ("CI", "Cote d'Ivoire"),
    ("HR", "Croatia"),
    ("CU", "Cuba"),
    ("CW", "Curacao"),
    ("CY", "Cyprus"),
    ("CZ", "Czech Republic"),
    ("DK", "Denmark"),
    ("DJ", "Djibouti"),
    ("DM", "Dominica"),
    ("DO", "Dominican Republic"),
    ("EC", "Ecuador"),
    ("EG", "Egypt"),
    ("SV", "El Salvador"),
    ("GQ", "Equatorial Guinea"),
    ("ER", "Eritrea"),
    ("EE", "Estonia"),
    ("ET", "Ethiopia"),
    ("FK", "Falkland Islands  [Malvinas]"),
    ("FO", "Faroe Islands"),
    ("FJ", "Fiji"),
    ("FI", "Finland"),
    ("FR", "France"),
    ("GF", "French Guiana"),
    ("PF", "French Polynesia"),
    ("TF", "French Southern Territories"),
    ("GA", "Gabon"),
    ("GM", "Gambia"),
    ("GE", "Georgia"),
    ("DE", "Germany"),
    ("GH", "Ghana"),
    ("GI", "Gibraltar"),
    ("GR", "Greece"),
    ("GL", "Greenland"),
    ("GD", "Grenada"),
    ("GP", "Guadeloupe"),
    ("GU", "Guam"),
    ("GT", "Guatemala"),
    ("GG", "Guernsey"),
    ("GN", "Guinea"),
    ("GW", "Guinea-Bissau"),
    ("GY", "Guyana"),
    ("HT", "Haiti"),
    ("HM", "Heard Island and McDonald Islands"),
    ("VA", "Holy See"),
    ("HN", "Honduras"),
    ("HK", "Hong Kong"),
    ("HU", "Hungary"),
    ("IS", "Iceland"),
    ("IN", "India"),
    ("ID", "Indonesia"),
    ("IR", "Iran (Islamic Republic of)"),
    ("IQ", "Iraq"),
    ("IE", "Ireland"),
    ("IM", "Isle of Man"),
    ("IL", "Israel"),
    ("IT", "Italy"),
    ("JM", "Jamaica"),
    ("JP", "Japan"),
    ("JE", "Jersey"),
    ("JO", "Jordan"),
    ("KZ", "Kazakhstan"),
    ("KE", "Kenya"),
    ("KI", "Kiribati"),
    ("KP", "Korea (the Democratic People's Republic of)"),
    ("KR", "Korea (the Republic of)"),
    ("KW", "Kuwait"),
    ("KG", "Kyrgyzstan"),
    ("LA", "Lao People's Democratic Republic"),
    ("LV", "Latvia"),
    ("LB", "Lebanon"),
    ("LS", "Lesotho"),
    ("LR", "Liberia"),
    ("LY", "Libya"),
    ("LI", "Liechtenstein"),
    ("LT", "Lithuania"),
    ("LU", "Luxembourg"),
    ("MO", "Macao"),
    ("MK", "Macedonia (the former Yugoslav Republic of)"),
    ("MG", "Madagascar"),
    ("MW", "Malawi"),
    ("MY", "Malaysia"),
    ("MV", "Maldives"),
    ("ML", "Mali"),
    ("MT", "Malta"),
    ("MH", "Marshall Islands"),
    ("MQ", "Martinique"),
    ("MR", "Mauritania"),
    ("MU", "Mauritius"),
    ("YT", "Mayotte"),
    ("MX", "Mexico"),
    ("FM", "Micronesia (Federated States of)"),
    ("MD", "Moldova (the Republic of)"),
    ("MC", "Monaco"),
    ("MN", "Mongolia"),
    ("ME", "Montenegro"),
    ("MS", "Montserrat"),
    ("MA", "Morocco"),
    ("MZ", "Mozambique"),
    ("MM", "Myanmar"),
    ("NA", "Namibia"),
    ("NR", "Nauru"),
    ("NP", "Nepal"),
    ("NL", "Netherlands"),
    ("NC", "New Caledonia"),
    ("NZ", "New Zealand"),
    ("NI", "Nicaragua"),
    ("NE", "Niger"),
    ("NG", "Nigeria"),
    ("NU", "Niue"),
    ("NF", "Norfolk Island"),
    ("MP", "Northern Mariana Islands"),
    ("NO", "Norway"),
    ("OM", "Oman"),
    ("PK", "Pakistan"),
    ("PW", "Palau"),
    ("PS", "Palestine, State of"),
    ("PA", "Panama"),
    ("PG", "Papua New Guinea"),
    ("PY", "Paraguay"),
    ("PE", "Peru"),
    ("PH", "Philippines"),
    ("PN", "Pitcairn"),
    ("PL", "Poland"),
    ("PT", "Portugal"),
    ("PR", "Puerto Rico"),
    ("QA", "Qatar"),
    ("RE", "Reunion"),
    ("RO", "Romania"),
    ("RU", "Russian Federation"),
    ("RW", "Rwanda"),
    ("BL", "Saint Barthelemy"),
    ("SH", "Saint Helena, Ascension and Tristan da Cunha"),
    ("KN", "Saint Kitts and Nevis"),
    ("LC", "Saint Lucia"),
    ("MF", "Saint Martin (French part)"),
    ("PM", "Saint Pierre and Miquelon"),
    ("VC", "Saint Vincent and the Grenadines"),
    ("WS", "Samoa"),
    ("SM", "San Marino"),
    ("ST", "Sao Tome and Principe"),
    ("SA", "Saudi Arabia"),
    ("SN", "Senegal"),
    ("RS", "Serbia"),
    ("SC", "Seychelles"),
    ("SL", "Sierra Leone"),
    ("SG", "Singapore"),
    ("SX", "Sint Maarten (Dutch part)"),
    ("SK", "Slovakia"),
    ("SI", "Slovenia"),
    ("SB", "Solomon Islands"),
    ("SO", "Somalia"),
    ("ZA", "South Africa"),
    ("GS", "South Georgia and the South Sandwich Islands"),
    ("SS", "South Sudan"),
    ("ES", "Spain"),
    ("LK", "Sri Lanka"),
    ("SD", "Sudan"),
    ("SR", "Suriname"),
    ("SJ", "Svalbard and Jan Mayen"),
    ("SZ", "Swaziland"),
    ("SE", "Sweden"),
    ("CH", "Switzerland"),
    ("SY", "Syrian Arab Republic"),
    ("TW", "Taiwan (Province of China)"),
    ("TJ", "Tajikistan"),
    ("TZ", "Tanzania, United Republic of"),
    ("TH", "Thailand"),
    ("TL", "Timor-Leste"),
    ("TG", "Togo"),
    ("TK", "Tokelau"),
    ("TO", "Tonga"),
    ("TT", "Trinidad and Tobago"),
    ("TN", "Tunisia"),
    ("TR", "Turkey"),
    ("TM", "Turkmenistan"),
    ("TC", "Turks and Caicos Islands"),
    ("TV", "Tuvalu"),
    ("UG", "Uganda"),
    ("UA", "Ukraine"),
    ("AE", "United Arab Emirates"),
    ("GB", "United Kingdom of Great Britain and Northern Ireland"),
    ("UM", "United States Minor Outlying Islands"),
    ("US", "United States of America"),
    ("UY", "Uruguay"),
    ("UZ", "Uzbekistan"),
    ("VU", "Vanuatu"),
    ("VE", "Venezuela (Bolivarian Republic of)"),
    ("VN", "Viet Nam"),
    ("VG", "Virgin Islands (British)"),
    ("VI", "Virgin Islands (U.S.)"),
    ("WF", "Wallis and Futuna"),
    ("EH", "Western Sahara"),
    ("YE", "Yemen"),
    ("ZM", "Zambia"),
    ("ZW", "Zimbabwe"),
]



INDEXES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6)
)

PERFORMANCE_STATUS = (
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)

OBJECTIVE_RESPONSES = (
    ('No Response', 'No Response'),
    ('Partial Response', 'Partial Response'),
    ('Disease Progression', 'Disease Progression'),
    ('Complete Response', 'Complete Response')
)

TREATMENT_TYPES = (
    ('Chemoradiotherapy', 'Chemoradiotherapy'),
    ('Chemotherapy', 'Chemotherapy'),
    ('Immunotherapy', 'Immunotherapy'),
    ('Radiotherapy', 'Radiotherapy'),
    ('Surgery', 'Surgery'),
    ('Systemic Therapy', 'Systemic Therapy'),
    ('Targeted Therapy', 'Targeted Therapy'),
)
