from django import template

register = template.Library()


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def add(value, arg):
    return value + arg


@register.filter
def divide(value, arg):
    return int(value / arg)

@register.filter
def get_by_index(l, i):
    return l[i]
    
@register.filter
def leading_zeros(value, desired_digits):

    num_zeros = int(desired_digits) - len(str(value))
    padded_value = []
    while num_zeros >= 1:
        padded_value.append("0")
        num_zeros = num_zeros - 1
    padded_value.append(str(value))
    return "".join(padded_value)


@register.filter
def at_index(array, index):
    return array[index]