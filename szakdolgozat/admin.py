from django.contrib import admin
from szakdolgozat.models import Temakor, Temavezeto, TemavezetoTemakor, TemaStatusz, Tema, Hallgato, Statusz, Tagozat, Kepzes, HallgatoKepzes, ErdemJegy, HallgatoKepzesTema, Beallitas


class TemakorAdmin(admin.ModelAdmin):
    search_fields = ('cim',)


class TemavezetoAdmin(admin.ModelAdmin):
    search_fields = ('elotag', 'vezeteknev', 'keresztnev', 'neptun_kod', 'max_letszam')
    list_filter = ('temakorok',)
    list_display = ('neptun_kod', 'sorszam', 'elotag', 'vezeteknev', 'keresztnev', 'avatott_nev', 'max_letszam', 'tel', 'email', 'valaszthato', 'inaktiv')
    actions = ['valaszthato', 'nem_valaszthato', 'aktiv', 'inaktiv']

    def valaszthato(self, request, queryset):
        rows_updated = queryset.update(valaszthato=1)
        self.message_user(request, '%s témavezető választható státuszúra lett állítva.' %rows_updated)
    valaszthato.short_description = 'Állítsd a kiválasztott témavezetőket választható státuszúra'

    def nem_valaszthato(self, request, queryset):
        rows_updated = queryset.update(valaszthato=0)
        self.message_user(request, '%s témavezető nem választható státuszúra lett állítva.' %rows_updated)
    nem_valaszthato.short_description = 'Állítsd a kiválasztott témavezetőket nem választható státuszúra'

    def aktiv(self, request, queryset):
        rows_updated = queryset.update(inaktiv=0)
        self.message_user(request, '%s témavezető aktív státuszúra lett állítva.' %rows_updated)
    aktiv.short_description = 'Állítsd a kiválasztott témavezetőket aktív státuszúra'

    def inaktiv(self, request, queryset):
        rows_updated = queryset.update(inaktiv=1)
        self.message_user(request, '%s témavezető inaktív státuszúra lett állítva.' %rows_updated)
    inaktiv.short_description = 'Állítsd a kiválasztott témavezetőket inaktív státuszúra'


class TemavezetoTemakorAdmin(admin.ModelAdmin):
    list_filter = ('temavezeto', 'temakor')
    list_display = ('temavezeto', 'temakor', 'rejtett')
    list_per_page = 500
    actions = ['elrejt', 'felfed']

    def elrejt(self, request, queryset):
        rows_updated = queryset.update(rejtett=True)
        self.message_user(request, '%s témakör lett elrejtve.' %rows_updated)
    elrejt.short_description = 'Állítsd a kiválasztott témaköröket rejtettre'

    def felfed(self, request, queryset):
        rows_updated = queryset.update(rejtett=False)
        self.message_user(request, '%s téma lett felfedve.' %rows_updated)
    felfed.short_description = 'Állítsd a kiválasztott témaköröket láthatóra'


#class HallgatoKepzesTemaInline(admin.TabularInline):
#    model = HallgatoKepzesTema
#    extra = 1

class TemaAdmin(admin.ModelAdmin):
    search_fields = ('cim', 'idegen_nyelv_szukseges', 'megjegyzes')
    list_filter = ('tema_statusz', 'temavezeto_temakor__temavezeto', 'temavezeto_temakor__temakor')
    list_display = ('temavezeto_temakor', 'cim', 'idegen_nyelv_szukseges', 'megjegyzes')
    list_per_page = 500
#    inlines = [
#        HallgatoKepzesTemaInline,
#    ]
    actions = ['szabad', 'idegen_nyelv_nem_szukseges']

    def szabad(self, request, queryset):
        rows_updated = queryset.update(tema_statusz=1)
        self.message_user(request, '%s cím szabad státuszúra lett állítva.' %rows_updated)
    szabad.short_description = 'Állítsd a kiválasztott címeket szabad státuszúra'

    def idegen_nyelv_nem_szukseges(self, request, queryset):
        rows_updated = queryset.update(idegen_nyelv_szukseges='Nem szükséges')
        self.message_user(request, '%s cím idegen nyelv követelménye "Nem szükséges"-re lett állítva.' %rows_updated)
    idegen_nyelv_nem_szukseges.short_description = 'Állítsd a kiválasztott címek idegen nyelv követelményét "Nem szükséges"-re'


class HallgatoAdmin(admin.ModelAdmin):
    search_fields = ('elotag', 'vezeteknev', 'keresztnev', 'neptun_kod')
    list_per_page = 500


class HallgatoKepzesAdmin(admin.ModelAdmin):
    search_fields = ('hallgato__elotag', 'hallgato__vezeteknev', 'hallgato__keresztnev', 'hallgato__neptun_kod')
    list_filter = ('kepzes', 'kezdet', 'veg', 'statusz')
    list_per_page = 500
    list_display = ('hallgato', 'kepzes', 'statusz')


class HallgatoKepzesTemaAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["hallgato_kepzes", "tema"]
        else:
            return []
    list_filter = ('kezdet', 'veg', 'hallgato_kepzes__kepzes', 'tema__tema_statusz', 'tema__temavezeto_temakor__temavezeto', 'erdemjegy', 'szakdolgozat_targyat_felvett', 'sikeres_vedes_datuma')
    list_per_page = 500
    list_display = ('hallgato_kepzes', 'kezdet', 'veg', 'erdemjegy', 'szakdolgozat_targyat_felvett', 'tema', 'sikeres_vedes_datuma')
    search_fields = ('hallgato_kepzes__hallgato__elotag', 'hallgato_kepzes__hallgato__vezeteknev', 'hallgato_kepzes__hallgato__keresztnev', 'hallgato_kepzes__hallgato__neptun_kod', 'tema__cim')
    radio_fields = {'kerveny': admin.VERTICAL}
    actions = ['szakdolgozat_targyat_felvett', 'szakdolgozat_targyat_nem_vett_fel']

    def szakdolgozat_targyat_felvett(self, request, queryset):
        rows_updated = queryset.update(szakdolgozat_targyat_felvett=True)
        self.message_user(request, '%s "Hallgató szakdolgozat címe képzésen" esetében a "Szakdolgozat tárgyat felvett" mező "Igaz"-ra lett állítva.' %rows_updated)
    szakdolgozat_targyat_felvett.short_description = 'Állítsd a kiválasztott "Hallgató szakdolgozat címe képzésen" sor(ok) esetében a "Szakdolgozat tárgyat felvett" mezőt "Igaz"-ra'

    def szakdolgozat_targyat_nem_vett_fel(self, request, queryset):
        rows_updated = queryset.update(szakdolgozat_targyat_felvett=False)
        self.message_user(request, '%s "Hallgató szakdolgozat címe képzésen" esetében a "Szakdolgozat tárgyat felvett" mező "Hamis"-ra lett állítva.' %rows_updated)
    szakdolgozat_targyat_nem_vett_fel.short_description = 'Állítsd a kiválasztott "Hallgató szakdolgozat címe képzésen" sor(ok) esetében a "Szakdolgozat tárgyat felvett" mezőt "Hamis"-ra'


admin.site.register(Temakor, TemakorAdmin)
admin.site.register(Temavezeto, TemavezetoAdmin)
admin.site.register(TemavezetoTemakor, TemavezetoTemakorAdmin)
admin.site.register(TemaStatusz)
admin.site.register(Tema, TemaAdmin)
admin.site.register(Hallgato, HallgatoAdmin)
admin.site.register(Statusz)
admin.site.register(Tagozat)
admin.site.register(Kepzes)
admin.site.register(HallgatoKepzes, HallgatoKepzesAdmin)
admin.site.register(ErdemJegy)
admin.site.register(HallgatoKepzesTema, HallgatoKepzesTemaAdmin)
admin.site.register(Beallitas)
