__author__ = 'admin'

from django import template

register = template.Library()

@register.simple_tag
def tag_cheng_add(x,y,z):
    if int(x)-1==0:
        return z
    return (int(x)-1)*int(y)+int(z)