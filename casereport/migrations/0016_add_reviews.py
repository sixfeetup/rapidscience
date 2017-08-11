from django.db import migrations


def add_reviews(apps, schema_editor):
    CaseReport = apps.get_model('casereport', 'CaseReport')
    CaseReportReview = apps.get_model('casereport', 'CaseReportReview')
    for cr in CaseReport.objects.all():
        if not cr.review:
            cr.review = CaseReportReview.objects.create()
            cr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('casereport', '0015_casereport_review'),
    ]

    operations = [migrations.RunPython(add_reviews)]
