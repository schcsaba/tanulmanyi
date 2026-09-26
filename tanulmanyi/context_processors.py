from django.utils.functional import SimpleLazyObject

from tanulmanyi.permissions import is_oktato


def is_proper_processor(request):
    user = request.user
    return {
        'is_logged_in': user.is_authenticated,
        # Lazy, so pages that never check it don't pay for the group query.
        'is_oktato': SimpleLazyObject(lambda: is_oktato(user)),
        'is_staff': user.is_staff,
    }
