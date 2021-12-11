def is_proper_processor(request):
    is_logged_in = request.user.is_authenticated
    is_oktato = request.user.groups.filter(name='Oktatok')
    is_staff = request.user.is_staff
    return {'is_logged_in': is_logged_in, 'is_oktato': is_oktato, 'is_staff': is_staff}
