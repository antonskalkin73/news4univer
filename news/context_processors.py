from .models import Tag


def tag_list(request):
    return {'all_tags': Tag.objects.all()[:50]}
