# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-05-26 17:18
from __future__ import unicode_literals

import logging
from django.db import migrations

from casereport.models import CaseReport, MolecularAbberation


logger = logging.getLogger(__name__)


def update_aberrations(apps, schema_editor):
    options = [
        "t(X;18)(SYT;SSX) translocation",
        "KRAS amplification",
        "FGF23 amplification",
        "FGF6 amplification",
        "ERBB2 amplification",
        "TP53 splice site 97-1G&gt:A",
        "MDM2 negative (FISH)",
        "FKHR negative (FISH)",
        "PAX7 negative transcript (RTPCR)",
        "PIK3CA amplification",
        "FBXW7 splice site 1645-2A&gt;T",
        "FGFR2 amplification",
        "JAK2 amplification",
        "MYC amplification",
        "SOX2 amplification",
        "TP53:H179R",
        "BRCA1:S713",
        "COL1A1-PDGFB fusion",
        "FGFR2 p.C382R substitution",
        "CDKN2A loss",
        "MCL1 amplification",
        "SS18-SSX fusion",
        "SYT-SSX fusion",
        "t(X;18)(p11;q11) translocation",
        "TET2 loss",
        "COL1A1-PDGFB positive (FISH)",
        "t(4;19)(q35;q13.1) CIC-DUX4 fusion",
        "RANBP2-ALK translocation",
        "KIT exon 11 involving codons 557-558",
        "ERBB2 overexpression",
        "CCND2 amplification",
        "SS18-SYT/SSX fusion",
        "CBL mutation",
        "CIC-DUX4 fusion",
        "CALM1 gene",
        "CAMLG gene",
        "ABCB1 overexpression",
        "TSC2 mutation",
        "NF1 mutation",
        "PTEN loss",
        "TFE3 expression (intense immunostaining)",
        "SATB2 positive (IHC)",
        "ALK fusion",
        "ROS1 rearrangement",
    ]

    # go through the existing case resports and save the ones with entries that
    # match the new options and log any orphans
    allcases = CaseReport.objects.all()
    allkeep = []
    for case in allcases:
        casekeep = []
        for aberration in case.aberrations.all():
            newname = aberration.molecule.strip() + " "\
                      + aberration.name.strip()
            if newname not in options:
                logger.debug("No matching aberration: %s", str(case.id)+": "+ str(aberration))
            else:
                casekeep.append(newname)
        if len(casekeep) > 0:
            allkeep.append([case.id, casekeep])

    # delete the existing MolecularAberrations
    MolecularAbberation.objects.all().delete()

    # repopulate the MolecularAberrations with the new names
    for option in options:
        item, created = MolecularAbberation.objects.get_or_create(name=option)

    # reassociate casereports with aberrations for the ones that matched
    for matched in allkeep:
        case = CaseReport.objects.get(id=matched[0])
        abslist = []
        for item in matched[1]:
            abslist.append(MolecularAbberation.objects.get(name=item))
        case.aberrations = abslist


class Migration(migrations.Migration):

    dependencies = [
        ('casereport', '0036_aberrations_molecule_null'),
    ]

    operations = [
        migrations.RunPython(update_aberrations),
    ]
