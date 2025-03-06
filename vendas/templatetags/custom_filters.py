from django import template

register = template.Library()

@register.filter
def sum_values(dictionary):
    """ Soma todos os valores de um dicionário """
    return sum(dictionary.values())


@register.filter
def dict_get(dictionary, key):
    """ Retorna o valor correspondente à chave em um dicionário """
    return dictionary.get(key, 0)  # Retorna 0 se a chave não existir