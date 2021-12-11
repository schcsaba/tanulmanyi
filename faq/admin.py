from django.contrib import admin
from faq.models import Kerdes


class KerdesAdmin(admin.ModelAdmin):
    list_display = ('kerdes', 'publikalt')
    actions = ['publikalt', 'nempublikalt']

    def publikalt(self, request, queryset):
        rows_updated = queryset.update(publikalt=True)
        self.message_user(request, '%s kérdés publikáltra lett állítva.' %rows_updated)
    publikalt.short_description = 'Állítsd a kiválasztott kérdéseket publikáltra'

    def nempublikalt(self, request, queryset):
        rows_updated = queryset.update(publikalt=False)
        self.message_user(request, '%s kérdés nem publikáltra lett állítva.' %rows_updated)
    nempublikalt.short_description = 'Állítsd a kiválasztott kérdéseket nem publikáltra'



admin.site.register(Kerdes, KerdesAdmin)