from django.db import models


# Create your models here.
class Document(models.Model):
    did = models.IntegerField(primary_key=True)
    content = models.TextField()
    keywords = models.CharField(max_length=200)


class DocSim(models.Model):
    sid = models.AutoField(primary_key=True)
    doc1 = models.ForeignKey(Document, on_delete=models.CASCADE, default='', related_name='doc1')
    doc2 = models.ForeignKey(Document, on_delete=models.CASCADE, default='', related_name='doc2')
    value = models.FloatField(default=None)
