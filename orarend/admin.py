from django.contrib import admin
from django.forms import TextInput
from django.db import models
from orarend.models import Beallitas, OrarendFajl


class BeallitasAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'150'})},
    }


class OrarendFajlAdmin(admin.ModelAdmin):
    list_display = ('aktiv', 'orarendfajl', 'oktatoi_orarendfajl')
    actions = ['aktiv', 'inaktiv', 'hallgatoi', 'oktatoi']

    def aktiv(self, request, queryset):
        rows_updated = queryset.update(aktiv=True)
        self.message_user(request, '%s órarendfájl aktívra lett állítva.' %rows_updated)
    aktiv.short_description = 'Állítsd a kiválasztott órarendfájlokat aktívra'

    def inaktiv(self, request, queryset):
        rows_updated = queryset.update(aktiv=False)
        self.message_user(request, '%s órarendfájl inaktívra lett állítva.' %rows_updated)
    inaktiv.short_description = 'Állítsd a kiválasztott órarendfájlokat inaktívra'

    def hallgatoi(self, request, queryset):
        rows_updated = queryset.update(oktatoi_orarendfajl=False)
        self.message_user(request, '%s órarendfájl hallgatói típusúra lett állítva.' %rows_updated)
    hallgatoi.short_description = 'Állítsd a kiválasztott órarendfájlokat hallgatói típusúra'

    def oktatoi(self, request, queryset):
        rows_updated = queryset.update(oktatoi_orarendfajl=True)
        self.message_user(request, '%s órarendfájl oktatói típusúra lett állítva.' %rows_updated)
    oktatoi.short_description = 'Állítsd a kiválasztott órarendfájlokat oktatói típusúra'


admin.site.register(Beallitas, BeallitasAdmin)
admin.site.register(OrarendFajl, OrarendFajlAdmin)

