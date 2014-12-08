import random
from django import template
from accounts.utils import get_profile_model
 
register = template.Library()


@register.inclusion_tag('users_list.html')
def show_users():
    profile_model = get_profile_model()
    queryset = profile_model.objects.all()
    #  get_visible_profiles(request.user)
    return {'profile_model': queryset}


@register.inclusion_tag('csrf_code.html')
def add_protection():
    return {}


@register.filter
def shuffle(arg):
    tmp = list(arg)[:]
    random.shuffle(tmp)
    return tmp