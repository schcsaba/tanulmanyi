from django.contrib.auth.decorators import user_passes_test

OKTATOK_CSOPORT = 'Oktatok'


def is_oktato(user):
    return user.is_authenticated and user.groups.filter(name=OKTATOK_CSOPORT).exists()


oktato_required = user_passes_test(is_oktato)
