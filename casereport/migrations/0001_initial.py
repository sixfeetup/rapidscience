# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CaseReportHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('physician', models.TextField(null=True, blank=True)),
                ('molecular_abberations', models.TextField(null=True, blank=True)),
                ('tests', models.TextField(null=True, blank=True)),
                ('treatments', models.TextField(null=True, blank=True)),
                ('diagnosis', models.TextField(null=True, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CRDBBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AuthorizedRep',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('first_name', models.CharField(max_length=200, null=True, blank=True)),
                ('last_name', models.CharField(max_length=200, null=True, blank=True)),
                ('email', models.EmailField(max_length=254)),
            ],
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='CaseFile',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('name', models.CharField(max_length=200)),
                ('document', models.FileField(upload_to=b'')),
            ],
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='CaseReport',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('gender', models.CharField(blank=True, max_length=20, null=True, choices=[(b'male', b'Male'), (b'female', b'Female'), (b'transgender male', b'Transgender Male'), (b'transgender female', b'Transgender Female')])),
                ('age', models.IntegerField(null=True, blank=True)),
                ('sarcoma_type', models.CharField(blank=True, max_length=100, null=True, choices=[(b'Acral fibromyxoma', b'Acral fibromyxoma'), (b'Acute lymphoblastic leukaemia', b'Acute lymphoblastic leukaemia'), (b'Acute myeloid leukaemia', b'Acute myeloid leukaemia'), (b'Adamantinoma', b'Adamantinoma'), (b'Adult fibrosarcoma', b'Adult fibrosarcoma'), (b'Adult type ', b'Adult type '), (b'Alveolar rhabdomyosarcoma', b'Alveolar rhabdomyosarcoma'), (b'Alveolar soft part sarcoma', b'Alveolar soft part sarcoma'), (b'Aneurysmal bone cyst', b'Aneurysmal bone cyst'), (b'Angioleiomyoma', b'Angioleiomyoma'), (b'Angiolipoma', b'Angiolipoma'), (b'Angiomatoid fibrous histiocytoma', b'Angiomatoid fibrous histiocytoma'), (b'Angiomyofibroblastoma', b'Angiomyofibroblastoma'), (b'Angiosarcoma', b'Angiosarcoma'), (b'Angiosarcoma of soft tissue', b'Angiosarcoma of soft tissue'), (b'Atypical cartilaginous tumour/ Chondrosarcoma grade I', b'Atypical cartilaginous tumour/ Chondrosarcoma grade I'), (b'Atypical fibroxanthorma', b'Atypical fibroxanthorma'), (b'Atypical lipomatous tumour/well differentiated liposarcoma', b'Atypical lipomatous tumour/well differentiated liposarcoma'), (b'Atypical myxoinflammatory fibroblastic tumour ', b'Atypical myxoinflammatory fibroblastic tumour '), (b'Benign fibrous histiocytoma/ Non-ossifying fibroma', b'Benign fibrous histiocytoma/ Non-ossifying fibroma'), (b'Benign notochordal tumour', b'Benign notochordal tumour'), (b'Bizarre parosteal osteochondromatous', b'Bizarre parosteal osteochondromatous'), (b'Blood and lymph vessel tumours', b'Blood and lymph vessel tumours'), (b'Brain tumours', b'Brain tumours'), (b'Calcifying fibrous ', b'Calcifying fibrous '), (b'Catcifying aponeurotic fibroma ', b'Catcifying aponeurotic fibroma '), (b'Cell differentiation (PEComa)', b'Cell differentiation (PEComa)'), (b'Cellular angiofibroma ', b'Cellular angiofibroma '), (b'Chondriod lipoma', b'Chondriod lipoma'), (b'Chondroblastic osteosarcoma', b'Chondroblastic osteosarcoma'), (b'Chondroblastoma', b'Chondroblastoma'), (b'Chondroma', b'Chondroma'), (b'Chondromesenchymal hamartoma', b'Chondromesenchymal hamartoma'), (b'Chondromyxoid fibroma', b'Chondromyxoid fibroma'), (b'Chondrosarcoma Grade II', b'Chondrosarcoma Grade II'), (b'Chondrosarcoma Grade II', b'Chondrosarcoma Grade III'), (b'Chordoma', b'Chordoma'), (b'Clear cell chondrosarcoma', b'Clear cell chondrosarcoma'), (b'Clear cell sarcoma of soft tissue', b'Clear cell sarcoma of soft tissue'), (b'Conventional osteosarcoma', b'Conventional osteosarcoma'), (b'Dedifferentiated chondrosarcoma', b'Dedifferentiated chondrosarcoma'), (b"Deep ('aggressive') angiomyxoma", b"Deep ('aggressive') angiomyxoma"), (b'Deep benign fibrous histiocytoma', b'Deep benign fibrous histiocytoma'), (b'Deep leiomyoma', b'Deep lelomyoma'), (b'Dermatafibrosarcoma protuberans ', b'Dermatafibrosarcoma protuberans '), (b'Dermatofibrosarcoma protuberans (DFSP)', b'Dermatofibrosarcoma protuberans (DFSP)'), (b'Desmoid-type fibromatosis', b'Desmoid-type fibromatosis'), (b'Desmoplastic fibroma of bone ', b'Desmoplastic fibroma of bone '), (b'Desmoplastic small round cell tumour', b'Desmoplastic small round cell tumour'), (b'Differentiated liposarcoma', b'Differentiated liposarcoma'), (b'Ectomesenchymoma', b'Ectomesenchymoma'), (b'Ectopic hamartornatous thymoma', b'Ectopic hamartornatous thymoma'), (b'Elastafibroma', b'Elastafibroma'), (b'Embryonal rhabdomyosarcoma', b'Embryonal rhabdomyosarcoma'), (b'Enchondroma', b'Enchondroma'), (b'Epithelioid haemangioma', b'Epithelioid haemangioma'), (b'Epithelioid malignant peripheral nerve sheath tumour', b'Epithelioid malignant peripheral nerve sheath tumour'), (b'Epithelioid sarcoma', b'Epithelioid sarcoma'), (b'Erdheim-Chester disease', b'Erdheim-Chester disease'), (b'Ewing sarcoma', b'Ewing sarcoma'), (b"Ewing's sarcoma", b"Ewing's sarcoma"), (b'Extra-adrenal myelolipoma', b'Extra-adrenal myelolipoma'), (b'Extra-renal angiolipoma', b'Extra-renal angiolipoma'), (b'Extra-renal rhabdoid tumour', b'Extra-renal rhabdoid tumour'), (b'Extraskeletal Ewing sarcoma', b'Extraskeletal Ewing sarcoma'), (b'Extraskeletal myxoid chondrosarcoma', b'Extraskeletal myxoid chondrosarcoma'), (b'Fat tissue tumours', b'Fat tissue tumours'), (b'Fetal type ', b'Fetal type '), (b'Fibro-osseous pseudotumour of digits', b'Fibro-osseous pseudotumour of digits'), (b'Fibroblastic osteosarcoma', b'Fibroblastic osteosarcoma'), (b'Fibroma of tendon sheath', b'Fibroma of tendon sheath'), (b'Fibromatosis colli', b'Fibromatosis colli'), (b'Fibrosarcoma of bone', b'Fibrosarcoma of bone'), (b'Fibrous dyplasia', b'Fibrous dyplasia'), (b'Fibrous hamartoma of infancy', b'Fibrous hamartoma of infancy'), (b'Fibrous tissue tumours', b'Fibrous tissue tumours'), (b'Gardner fibroma', b'Gardner fibroma'), (b'Genital type ', b'Genital type '), (b'Germ cell tumours', b'Germ cell tumours'), (b'Giant cell fibroblastoma (GCF)', b'Giant cell fibroblastoma (GCF)'), (b'Giant cell lesion of the small bones', b'Giant cell lesion of the small bones'), (b'Giant cell tumour of bone', b'Giant cell tumour of bone'), (b'Giant cell tumour of soft tissues', b'Giant cell tumour of soft tissues'), (b'Giant semi fibrobiastoma', b'Giant semi fibrobiastoma'), (b'Glomangiomatosis', b'Glomangiomatosis'), (b'Glomus tumour (and variants)', b'Glomus tumour (and variants)'), (b'Granular cell tumour', b'Granular cell tumour'), (b'Haemangioma', b'Haemangioma'), (b'Haemosiderotic fibrolipomatous tumour', b'Haemosiderotic fibrolipomatous tumour'), (b'Hibernoma', b'Hibernoma'), (b'High-grade surface osteosarcoma', b'High-grade surface osteosarcoma'), (b'Hodgkin lymphoma', b'Hodgkin lymphoma'), (b'Hybrid nerve sheath tumours', b'Hybrid nerve sheath tumours'), (b'Inclusion body fibromatosis ', b'Inclusion body fibromatosis '), (b'Infantile fibrosarcoma', b'Infantile fibrosarcoma'), (b'Inflammatory myofibroblastic tumour', b'Inflammatory myofibroblastic tumour'), (b'Inflammatory myxoinflammatory fibroblastic', b'Inflammatory myxoinflammatory fibroblastic'), (b'Intramuscular myxoma', b'Intramuscular myxoma'), (b'Ischaemic fasciitis', b'Ischaemic fasciitis'), (b'Joint tissue tumours', b'Joint tissue tumours'), (b'Juvenile hyaline fibromatosis', b'Juvenile hyaline fibromatosis'), (b'Juxta-articular myxoma', b'Juxta-articular myxoma'), (b'Langerhans cell histiocytosis', b'Langerhans cell histiocytosis'), (b'Leiomyosarcoma (excluding skin)', b'Leiomyosarcoma (excluding skin)'), (b'Lipoblastoma/Lipoblastomatosis', b'Lipoblastoma/Lipoblastomatosis'), (b'Lipofibromatosis', b'Lipofibromatosis'), (b'Lipoma', b'Lipoma'), (b'Lipoma of bone', b'Lipoma of bone'), (b'Lipoma of nerve', b'Lipoma of nerve'), (b'Lipomasarcoma of bone', b'Lipomasarcoma of bone'), (b'Lipomatosis', b'Lipomatosis'), (b'Liposarcoma', b'Liposarcoma'), (b'Low-grade  myxoinflammatory Sarcoma', b'Low-grade  myxoinflammatory Sarcoma'), (b'Low-grade central osteosarcoma', b'Low-grade central osteosarcoma'), (b'Low-grade fibromyxoid sarcoma', b'Low-grade fibromyxoid sarcoma'), (b'Malignancy in giant cell tumour of bone', b'Malignancy in giant cell tumour of bone'), (b'Malignant Liposarcoma of bone', b'Malignant Liposarcoma of bone'), (b'Malignant Triton tumour', b'Malignant Triton tumour'), (b'Malignant glomus tumour', b'Malignant glomus tumour'), (b'Malignant granular cell tumour', b'Malignant granular cell tumour'), (b'Malignant perineurioma', b'Malignant perineurioma'), (b'Malignant peripheral nerve sheath tumour', b'Malignant peripheral nerve sheath tumour'), (b'Mammary-type myofibroblastoma ', b'Mammary-type myofibroblastoma'), (b'Mesenchymal chondrosarcoma', b'Mesenchymal chondrosarcoma chondrosarcoma'), (b'Mixed tumour NOS', b'Mixed tumour NOS'), (b'Mixed tumour NOS, malignant', b'Mixed tumour NOS, malignant'), (b'Muscle tissue tumours', b'Muscle tissue tumours'), (b'Myoepithelial carcinoma', b'Myoepithelial carcinoma'), (b'Myoepitheliorna', b'Myoepitheliorna'), (b'Myofibroma', b'Myofibroma'), (b'Myofibromatosis', b'Myofibromatosis'), (b'Myolipoma', b'Myolipoma'), (b'Myopericytoma', b'Myopericytoma'), (b'Myositis ossificans', b'Myositis ossificans'), (b'Myxofibrosarcoma', b'Myxofibrosarcoma'), (b'Myxoid liposarcoma', b'Myxoid liposarcoma'), (b'Neoplasms with perivascular epithelioid', b'Neoplasms with perivascular epithelioid'), (b'Neuroblastoma', b'Neuroblastoma'), (b'Nodular fasciitis', b'Nodular fasciitis'), (b'Nuchal-type fibroma', b'Nuchal-type fibroma'), (b'Ossifying fibromyxoid tumour', b'Ossifying fibromyxoid tumour'), (b'Osteoblastic osteosarcoma', b'Osteoblastic osteosarcoma'), (b'Osteoblastoma', b'Osteoblastoma'), (b'Osteochondroma', b'Osteochondroma'), (b'Osteochondromyxoma', b'Osteochondromyxoma'), (b'Osteofibrcus dysplasia', b'Osteofibrcus dysplasia'), (b'Osteoid osteoma', b'Osteoid osteoma'), (b'Osteoma', b'Osteoma'), (b'Osteosarcoma', b'Osteosarcoma'), (b'Other', b'Other'), (b'PEComa NOS, benign', b'PEComa NOS, benign'), (b'PEComa NOS, malignant', b'PEComa NOS, malignant'), (b'Palmar/plantar  fibromatosis', b'Palmar/plantar  fibromatosis'), (b'Parosteal osteosarcoma', b'Parosteal osteosarcoma'), (b'Periosteal Chondroma', b'Periosteal Chondroma'), (b'Periosteal osteosarcoma', b'Periosteal osteosarcoma'), (b'Peripheral nerve tumours', b'Peripheral nerve tumours'), (b'Phosphaturic mesenchymal tumour, benign', b'Phosphaturic mesenchymal tumour, benign'), (b'Phosphaturic mesenchymal tumour, malignant', b'Phosphaturic mesenchymal tumour, malignant'), (b'Plaomorphic rhabdomyosarcoma', b' Plaomorphic rhabdomyosarcoma'), (b'Plasma cell myeloma', b'Plasma cell myeloma'), (b'Pleomorphic hyalinizing angiectatic tumour', b'Pleomorphic hyalinizing angiectatic tumour'), (b'Pleomorphic liposarcoma', b'Pleomorphic liposarcoma'), (b'Plexiform fibrohistiocytic tumour ', b'Plexiform fibrohistiocytic tumour '), (b'Primary non-Hodgkin lymphoma of bone', b'Primary non-Hodgkin lymphoma of bone'), (b'Proliferation', b'Proliferation'), (b'Proliferative fasciitis', b'Proliferative fasciitis'), (b'Proliferative myositis', b'Proliferative myositis'), (b'Protubarans', b'Protubarans'), (b'Rarer types of sarcoma', b'Rarer types of sarcoma'), (b'Retinoblastoma', b'Retinoblastoma'), (b'Rhabdomyoma', b'Rhabdomyoma'), (b'Rosai-Dorfman disease', b'Rosai-Dorfman disease'), (b'Sarcoma', b'Sarcoma'), (b'Sclerosing epithelioid fibrosarcoma', b'Sclerosing epithelioid fibrosarcoma'), (b'Secondary osteosarcoma', b'Secondary osteosarcoma'), (b'Simple bone cyst', b'Simple bone cyst'), (b'Small cell osteosarcoma', b'Small cell osteosarcoma'), (b'Solitary fibrous tumour', b'Solitary fibrous tumour'), (b'Solitary plasmacytoma of bone', b'Solitary plasmacytoma of bone'), (b'Spindle cell/pleomorphic lipoma', b'Spindle cell/pleomorphic lipoma'), (b'Spindle cell/sclerosing rhabdomyosarcoma', b'Spindle cell/sclerosing rhabdomyosarcoma'), (b'Sublingual exostosis', b'Sublingual exostosis'), (b'Synovial chondromatosis', b'Synovial chondromatosis'), (b'Synovial sarcoma NOS', b'Synovial sarcoma NOS'), (b'Synovial sarcoma, biphasic', b'Synovial sarcoma, biphasic'), (b'Synovial sarcoma, spindle cell', b'Synovial sarcoma, spindle cell'), (b'Telangiectatic osteosarcoma', b'Telangiectatic osteosarcoma'), (b'Tenosynovial giant cell tumour', b'Tenosynovial giant cell tumour'), (b'Undifferentiated high-grade pleomorphic sarcoma of bone', b'Undifferentiated high-grade pleomorphic sarcoma of bone'), (b'Undifferentiated pleomorphic sarcoma', b'Undifferentiated pleomorphic sarcoma'), (b'Undifferentiated round cell sarcoma', b'Undifferentiated round cell sarcoma'), (b'Undifferentiated sarcoma NOS', b'Undifferentiated sarcoma NOS'), (b'Undifferentiated spindle cell sarcoma', b'Undifferentiated spindle cell sarcoma'), (b"Wilms' tumour", b"Wilms' tumour")])),
                ('other_sarcoma_type', models.CharField(max_length=200, null=True, blank=True)),
                ('history', models.TextField(null=True, blank=True)),
                ('precision_treatment', models.TextField(null=True, blank=True)),
                ('specimen_analyzed', models.TextField(null=True, blank=True)),
                ('additional_comment', models.TextField(null=True, blank=True)),
                ('previous_treatments', models.TextField(null=True, blank=True)),
                ('status', models.CharField(default=b'processing', max_length=50, choices=[(b'processing', b'Processing'), (b'ready', b'Ready to Review'), (b'approved', b'Approved'), (b'changes', b'Need Changes'), (b'reviewed', b'Reviewed'), (b'edited', b'Edited')])),
                ('index', models.IntegerField(blank=True, max_length=1, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('pathology', models.TextField(null=True, blank=True)),
                ('progression', models.CharField(max_length=250, null=True, blank=True)),
                ('response', models.CharField(blank=True, max_length=2, null=True, choices=[(b'SD', b'Stable Disease'), (b'PR', b'Partial Response'), (b'PD', b'Progressive Disease'), (b'CR', b'Complete Response')])),
                ('tumor_location', models.CharField(max_length=200, null=True, blank=True)),
                ('authorized_reps', models.ManyToManyField(to='casereport.AuthorizedRep', null=True, blank=True)),
                ('casefile', models.ForeignKey(blank=True, to='casereport.CaseFile', null=True)),
            ],
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('name', models.CharField(max_length=255)),
                ('frequency', models.IntegerField(null=True, blank=True)),
                ('date_point', models.CharField(max_length=200, null=True, blank=True)),
                ('end_date_point', models.CharField(max_length=200, null=True, blank=True)),
                ('interval', models.CharField(max_length=200, null=True, blank=True)),
                ('is_negation', models.BooleanField(default=False)),
                ('event_type', models.CharField(blank=True, max_length=15, null=True, choices=[(b'test', b'Test'), (b'treatment', b'Treatment'), (b'diagnosis', b'Diagnosis')])),
            ],
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('address', models.TextField()),
            ],
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='MolecularAbberation',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('name', models.CharField(max_length=255)),
                ('molecule', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Genetic Aberration',
                'verbose_name_plural': 'Genetic Aberrations',
            },
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='Physician',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('affiliation', models.ForeignKey(blank=True, to='casereport.Institution', null=True)),
            ],
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='ResultValueEvent',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('value', models.CharField(max_length=200)),
                ('result_indicator', models.CharField(max_length=200, null=True, blank=True)),
            ],
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('crdbbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.CRDBBase')),
                ('name', models.CharField(max_length=250)),
                ('treatment_type', models.CharField(max_length=250)),
                ('duration', models.CharField(max_length=250, null=True, blank=True)),
                ('dose', models.CharField(max_length=250, null=True, blank=True)),
                ('objective_response', models.CharField(blank=True, max_length=2, null=True, choices=[(b'SD', b'Stable Disease'), (b'PR', b'Partial Response'), (b'PD', b'Progressive Disease'), (b'CR', b'Complete Response')])),
                ('tumor_size', models.CharField(max_length=50, null=True, blank=True)),
                ('status', models.IntegerField(blank=True, max_length=1, null=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('treatment_outcome', models.TextField(null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('casereport', models.ForeignKey(to='casereport.CaseReport')),
            ],
            bases=('casereport.crdbbase',),
        ),
        migrations.CreateModel(
            name='DiagnosisEvent',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.Event')),
                ('specimen', models.CharField(max_length=255, null=True, blank=True)),
                ('symptoms', models.TextField(null=True, blank=True)),
                ('body_part', models.CharField(max_length=255, null=True, blank=True)),
            ],
            bases=('casereport.event',),
        ),
        migrations.CreateModel(
            name='TestEvent',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.Event')),
                ('specimen', models.CharField(max_length=255)),
                ('body_part', models.CharField(max_length=255, null=True, blank=True)),
            ],
            bases=('casereport.event',),
        ),
        migrations.CreateModel(
            name='TreatmentEvent',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='casereport.Event')),
                ('treatment_type', models.CharField(max_length=255)),
                ('followed_by_interval', models.CharField(max_length=50, null=True, blank=True)),
                ('followed_by_interval_unit', models.CharField(max_length=100, null=True, blank=True)),
                ('side_effects', models.TextField(null=True, blank=True)),
                ('outcome', models.TextField(null=True, blank=True)),
                ('combined_with', models.ForeignKey(related_name='combinedwith', blank=True, to='casereport.TreatmentEvent', null=True)),
                ('followed_by', models.ForeignKey(blank=True, to='casereport.TreatmentEvent', null=True)),
            ],
            bases=('casereport.event',),
        ),
        migrations.AddField(
            model_name='event',
            name='casereport',
            field=models.ForeignKey(to='casereport.CaseReport'),
        ),
        migrations.AddField(
            model_name='event',
            name='next_event',
            field=models.ForeignKey(related_name='nextevent', blank=True, to='casereport.Event', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='parent_event',
            field=models.ForeignKey(related_name='parentevent', blank=True, to='casereport.Event', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='previous_event',
            field=models.ForeignKey(related_name='previousevent', blank=True, to='casereport.Event', null=True),
        ),
        migrations.AddField(
            model_name='casereporthistory',
            name='case',
            field=models.ForeignKey(to='casereport.CaseReport'),
        ),
        migrations.AddField(
            model_name='casereport',
            name='molecular_abberations',
            field=models.ManyToManyField(to='casereport.MolecularAbberation', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='casereport',
            name='primary_physician',
            field=models.ForeignKey(related_name='primary_case', to='casereport.Physician'),
        ),
        migrations.AddField(
            model_name='casereport',
            name='referring_physician',
            field=models.ManyToManyField(to='casereport.Physician', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='resultvalueevent',
            name='test',
            field=models.ForeignKey(to='casereport.TestEvent'),
        ),
        migrations.AddField(
            model_name='diagnosisevent',
            name='test',
            field=models.ForeignKey(blank=True, to='casereport.TestEvent', null=True),
        ),
    ]
