from django.contrib import admin
from docsAnalysis.models import Document, DocSim


# Register your models here.
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('did', 'content', 'keywords')
    search_fields = ('did', 'content', 'keywords')


class DocSimAdmin(admin.ModelAdmin):
    list_display = ('sid', 'doc1', 'doc2', 'value')
    search_fields = ('sid', 'doc1', 'doc2', 'value')


admin.site.register(Document, DocumentAdmin)
admin.site.register(DocSim, DocSimAdmin)
