from django.db import models


# Create your models here.
class Document(models.Model):
    did = models.IntegerField(primary_key=True)
    content = models.TextField()
    # keywords = models.CharField(max_length=200)
    # proj = models.CharField(max_length=50)


# class DocSimilarity(models.Model):
#     doc1 = models.ForeignKey(Document, on_delete=models.CASCADE, default=None, related_name='doc1')
#     doc2 = models.ForeignKey(Document, on_delete=models.CASCADE, default=None, related_name='doc2')
#     similarity = models.FloatField(default=None)
