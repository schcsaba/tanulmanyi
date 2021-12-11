from django.contrib import admin
from mintatanterv.models import Munkarend, Kovetelmeny, Kurzustipus, Vizsgatipus, Oktatotipus, Oktato, KepzesiSzint, Kepzes, Szak, NagyTargyCsoport, Szakirany, Specializacio, NagyTargyOktato, NagyTargy, Targy, Nyelv, TargyMunkarend, TargyOktato, Mintatanterv, MintatantervTargy, FelvetelTipusa, Felev, Elofeltetel, ElofeltetelMintatantervben

class OktatoAdmin(admin.ModelAdmin):
    list_display = ('neptun_kod', 'elotag', 'vezeteknev', 'keresztnev', 'avatott_nev', 'tel', 'email', 'megjelenites')
    actions = ['megjelenit', 'elrejt']

    def megjelenit(self, request, queryset):
        rows_updated = queryset.update(megjelenites=True)
        self.message_user(request, '%s oktató megjelenítettre lett állítva.' %rows_updated)
    megjelenit.short_description = 'Jelenítsd meg a kiválasztott oktatókat az oktatók elérhetősége oldalon'

    def elrejt(self, request, queryset):
        rows_updated = queryset.update(megjelenites=False)
        self.message_user(request, '%s oktató elrejtettre lett állítva.' %rows_updated)
    elrejt.short_description = 'Rejtsd el a kiválasztott oktatókat az oktatók elérhetősége oldalról'


class NagyTargyOktatoInline(admin.TabularInline):
    model = NagyTargyOktato
    extra = 1

class NagyTargyAdmin(admin.ModelAdmin):
    list_filter = ('szakirany__szak', 'szakirany', 'nagytargycsoport', 'oktato')
    list_display = ('targykod', 'targynev', 'kredit')
    inlines = [
        NagyTargyOktatoInline,
    ]


class TargyMunkarendInline(admin.TabularInline):
    model = TargyMunkarend
    extra = 1
    filter_horizontal = ('oktato',)

class TargyOktatoInline(admin.TabularInline):
    model = TargyOktato
    extra = 1

class MintatantervTargyInline(admin.TabularInline):
    model = MintatantervTargy
    extra = 1
    #filter_horizontal = ('elofeltetel_targy',)
    fieldsets = (
        (None, {
            'fields': ('mintatanterv', 'felev', 'kredit', 'felvetel_tipusa', 'oszi_tavaszi')
        }),
    )

class ElofeltetelInline(admin.TabularInline):
    model = Elofeltetel
    fk_name = 'targy'
    extra = 1

class TargyAdmin(admin.ModelAdmin):
    search_fields = ('targykod', 'targynev')
    filter_horizontal = ('nagytargy', 'elofeltetel_targy', 'ekvivalens_targy', 'mintatanterv')
    list_filter = ('kredit', 'kovetelmeny', 'kurzustipus', 'targymunkarend__vizsgatipus', 'nagytargy', 'oktato', 'elofeltetel_targy')
    list_display = ('targykod', 'targynev', 'kredit', 'kovetelmeny')
    inlines = [
        ElofeltetelInline,
        TargyMunkarendInline,
        TargyOktatoInline,
        MintatantervTargyInline,
    ]
    save_as = True
    fieldsets = (
        (None, {
            'fields': (('targykod', 'targynev', 'kredit', 'kovetelmeny'), 'nagytargy', 'kurzustipus', 'ekvivalens_targy')
        }),
        ('Tematika', {
            'classes': ('collapse',),
            'fields': ('cel', 'targyleiras', 'modszertan', 'evkozi_kov', 'vegso_kov', 'kotelezo_olvasmanyok', 'ajanlott_irodalom'),
        }),
    )


class TargyMunkarendAdmin(admin.ModelAdmin):
    search_fields = ('targy__targykod', 'targy__targynev')
    filter_horizontal = ('oktato',)
    list_filter = ('munkarend', 'vizsgatipus', 'oktato', 'max_letszam', 'kurzustipus')
    list_display = ('targy', 'kurzuskod', 'munkarend', 'orarend_oraszam', 'max_hianyzas', 'max_letszam', 'nem_indul')
    actions = ['max_letszam_5', 'max_letszam_10', 'max_letszam_15', 'max_letszam_20', 'max_letszam_25', 'max_letszam_30', 'max_letszam_35', 'max_letszam_40', 'max_letszam_45', 'max_letszam_50', 'max_letszam_55', 'max_letszam_60', 'max_letszam_65', 'max_letszam_70', 'nem_indul', 'indul']

    def max_letszam_5(self, request, queryset):
        rows_updated = queryset.update(max_letszam=5)
        self.message_user(request, '%s kurzus létszáma lett 5-re állítva.' %rows_updated)
    max_letszam_5.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 5-re'

    def max_letszam_10(self, request, queryset):
        rows_updated = queryset.update(max_letszam=10)
        self.message_user(request, '%s kurzus létszáma lett 10-re állítva.' %rows_updated)
    max_letszam_10.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 10-re'

    def max_letszam_15(self, request, queryset):
        rows_updated = queryset.update(max_letszam=15)
        self.message_user(request, '%s kurzus létszáma lett 15-re állítva.' %rows_updated)
    max_letszam_15.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 15-re'

    def max_letszam_20(self, request, queryset):
        rows_updated = queryset.update(max_letszam=20)
        self.message_user(request, '%s kurzus létszáma lett 20-ra állítva.' %rows_updated)
    max_letszam_20.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 20-ra'

    def max_letszam_25(self, request, queryset):
        rows_updated = queryset.update(max_letszam=25)
        self.message_user(request, '%s kurzus létszáma lett 25-re állítva.' %rows_updated)
    max_letszam_25.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 25-re'

    def max_letszam_30(self, request, queryset):
        rows_updated = queryset.update(max_letszam=30)
        self.message_user(request, '%s kurzus létszáma lett 30-ra állítva.' %rows_updated)
    max_letszam_30.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 30-ra'

    def max_letszam_35(self, request, queryset):
        rows_updated = queryset.update(max_letszam=35)
        self.message_user(request, '%s kurzus létszáma lett 35-re állítva.' %rows_updated)
    max_letszam_35.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 35-re'

    def max_letszam_40(self, request, queryset):
        rows_updated = queryset.update(max_letszam=40)
        self.message_user(request, '%s kurzus létszáma lett 40-re állítva.' %rows_updated)
    max_letszam_40.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 40-re'

    def max_letszam_45(self, request, queryset):
        rows_updated = queryset.update(max_letszam=45)
        self.message_user(request, '%s kurzus létszáma lett 45-re állítva.' %rows_updated)
    max_letszam_45.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 45-re'

    def max_letszam_50(self, request, queryset):
        rows_updated = queryset.update(max_letszam=50)
        self.message_user(request, '%s kurzus létszáma lett 50-re állítva.' %rows_updated)
    max_letszam_50.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 50-re'

    def max_letszam_55(self, request, queryset):
        rows_updated = queryset.update(max_letszam=55)
        self.message_user(request, '%s kurzus létszáma lett 55-re állítva.' %rows_updated)
    max_letszam_55.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 55-re'

    def max_letszam_60(self, request, queryset):
        rows_updated = queryset.update(max_letszam=60)
        self.message_user(request, '%s kurzus létszáma lett 60-ra állítva.' %rows_updated)
    max_letszam_60.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 60-ra'

    def max_letszam_65(self, request, queryset):
        rows_updated = queryset.update(max_letszam=65)
        self.message_user(request, '%s kurzus létszáma lett 65-re állítva.' %rows_updated)
    max_letszam_65.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 65-re'

    def max_letszam_70(self, request, queryset):
        rows_updated = queryset.update(max_letszam=70)
        self.message_user(request, '%s kurzus létszáma lett 70-re állítva.' %rows_updated)
    max_letszam_70.short_description = 'Állítsd a kiválasztott kurzusok maximális létszámát 70-re'

    def nem_indul(self, request, queryset):
        rows_updated = queryset.update(nem_indul=True)
        self.message_user(request, 'Beállítottad, hogy a %s kurzus nem indul.' %rows_updated)
    nem_indul.short_description = 'Annak beállítása, hogy a kiválasztott kurzusok nem indulnak'

    def indul(self, request, queryset):
        rows_updated = queryset.update(nem_indul=False)
        self.message_user(request, 'Beállítottad, hogy a %s kurzus indul.' %rows_updated)
    indul.short_description = 'Annak beállítása, hogy a kiválasztott kurzusok indulnak'


class TargyOktatoAdmin(admin.ModelAdmin):
    search_fields = ('targy__targykod', 'targy__targynev')
    list_filter = ('oktato_tipus', 'oktato')


class MintatantervTargyInline(admin.TabularInline):
    model = MintatantervTargy
    filter_horizontal = ('elofeltetel_targy',)

class MintatantervAdmin(admin.ModelAdmin):
    inlines = [
        MintatantervTargyInline,
    ]
    save_as = True
    list_display = ('kod', 'nev', 'aktualis')


class ElofeltetelMintatantervbenInline(admin.TabularInline):
    model = ElofeltetelMintatantervben
    extra = 1

class MintatantervTargyAdmin(admin.ModelAdmin):
    filter_horizontal = ('elofeltetel_targy',)
    list_filter = ('mintatanterv', 'felev', 'felvetel_tipusa', 'oszi_tavaszi')
    inlines = [
        ElofeltetelMintatantervbenInline,
    ]


class ElofeltetelAdmin(admin.ModelAdmin):
    list_display = ('targy', 'elofeltetel_targy', 'eros_elofeltetel')
    search_fields = ('targy__targykod', 'targy__targynev', 'elofeltetel_targy__targykod', 'elofeltetel_targy__targynev')
    list_filter = ('eros_elofeltetel', 'elofeltetel_targy__kovetelmeny')
    actions = ['eros', 'gyenge']

    def eros(self, request, queryset):
        rows_updated = queryset.update(eros_elofeltetel=True)
        self.message_user(request, 'Beállítottad, hogy %s előfeltétel erős.' %rows_updated)
    eros.short_description = 'Annak beállítása, hogy a kiválasztott előfeltételek erősek'

    def gyenge(self, request, queryset):
        rows_updated = queryset.update(eros_elofeltetel=False)
        self.message_user(request, 'Beállítottad, hogy %s előfeltétel gyenge.' %rows_updated)
    gyenge.short_description = 'Annak beállítása, hogy a kiválasztott előfeltételek gyengék'

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup == 'targy__kovetelmeny__id__exact':
            return True
        return super(ElofeltetelAdmin, self).lookup_allowed(lookup, *args, **kwargs)

class ElofeltetelMintatantervbenAdmin(admin.ModelAdmin):
    list_display = ('targy', 'elofeltetel_targy', 'eros_elofeltetel')
    list_filter = ('eros_elofeltetel', 'elofeltetel_targy__kovetelmeny', 'targy__mintatanterv')
    actions = ['eros', 'gyenge']

    def eros(self, request, queryset):
        rows_updated = queryset.update(eros_elofeltetel=True)
        self.message_user(request, 'Beállítottad, hogy %s előfeltétel erős.' %rows_updated)
    eros.short_description = 'Annak beállítása, hogy a kiválasztott előfeltételek erősek'

    def gyenge(self, request, queryset):
        rows_updated = queryset.update(eros_elofeltetel=False)
        self.message_user(request, 'Beállítottad, hogy %s előfeltétel gyenge.' %rows_updated)
    gyenge.short_description = 'Annak beállítása, hogy a kiválasztott előfeltételek gyengék'

admin.site.register(Munkarend)
admin.site.register(Kovetelmeny)
admin.site.register(Kurzustipus)
admin.site.register(Vizsgatipus)
admin.site.register(Oktatotipus)
admin.site.register(Oktato, OktatoAdmin)
admin.site.register(KepzesiSzint)
admin.site.register(Kepzes)
admin.site.register(Szak)
admin.site.register(NagyTargyCsoport)
admin.site.register(Szakirany)
admin.site.register(Specializacio)
admin.site.register(NagyTargy, NagyTargyAdmin)
admin.site.register(NagyTargyOktato)
admin.site.register(Targy, TargyAdmin)
admin.site.register(Nyelv)
admin.site.register(TargyMunkarend, TargyMunkarendAdmin)
admin.site.register(TargyOktato, TargyOktatoAdmin)
admin.site.register(Mintatanterv, MintatantervAdmin)
admin.site.register(FelvetelTipusa)
admin.site.register(MintatantervTargy, MintatantervTargyAdmin)
admin.site.register(Felev)
admin.site.register(Elofeltetel, ElofeltetelAdmin)
admin.site.register(ElofeltetelMintatantervben, ElofeltetelMintatantervbenAdmin)