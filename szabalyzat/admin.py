from django.contrib import admin
from szabalyzat.models import Szabalyzat

class SzabalyzatAdmin(admin.ModelAdmin):
    list_display = ('nev', 'szabalyzatfajl', 'csak_oktatoknak')
    actions = ['csak_oktatoknak', 'nem_csak_oktatoknak']

    def csak_oktatoknak(self, request, queryset):
        rows_updated = queryset.update(csak_oktatoknak=True)
        self.message_user(request, '%s link csak oktatóknak jelenik meg.' %rows_updated)
    csak_oktatoknak.short_description = 'Állítsd a kiválasztott linkeket csak oktatóknak megjelenítettre'

    def nem_csak_oktatoknak(self, request, queryset):
        rows_updated = queryset.update(csak_oktatoknak=False)
        self.message_user(request, '%s link nem csak oktatóknak jelenik meg.' %rows_updated)
    nem_csak_oktatoknak.short_description = 'Állítsd a kiválasztott linkeket nem csak oktatóknak megjelenítettre'

admin.site.register(Szabalyzat, SzabalyzatAdmin)