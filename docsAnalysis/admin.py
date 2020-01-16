from django.contrib import admin
from docsAnalysis.models import Document


# Register your models here.
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('did', 'content', 'keywords', 'proj')
    search_fields = ('did', 'content', 'keywords', 'proj')


# class DocSimilarityAdmin(admin.ModelAdmin):
#     list_display = ('doc1', 'doc2', 'similarity')
#     search_fields = ('doc1', 'doc2', 'similarity')

admin.site.register(Document, DocumentAdmin)
# admin.site.register(DocSimilarity, DocSimilarityAdmin)
