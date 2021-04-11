from django.db import models


class Participant(models.Model):
    # """
    # A participant ingested from ParticipantFeed
    # """

    participant_code = models.PositiveIntegerField(primary_key=True)
    job_title = models.CharField(max_length=32)
    department = models.CharField(max_length=32)
    birth_date = models.DateField()

    # """Last (latest) feed from which this participant was inserted or updated"""
    # feed = models.ForeignKey('ParticipantFeed', on_delete=models.PROTECT, related_name='participants',
    #                          related_query_name='participant')
