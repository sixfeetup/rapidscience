from django.db import models

from rlp.core.models import SEOMixin


class Event(SEOMixin):
    description = models.CharField(max_length=500)
    url = models.URLField()
    location = models.CharField(max_length=150)
    image = models.ImageField(upload_to='events')
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['start_date']

    @property
    def duration(self):
        if self.start_date == self.end_date:
            return '{}'.format(self.start_date.strftime('%B %d, %Y'))

        return '{0} - {1}'.format(self.start_date.strftime('%B %d, %Y'), self.end_date.strftime('%B %d, %Y'))
