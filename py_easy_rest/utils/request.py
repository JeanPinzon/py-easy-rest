def get_query_string_arg(query_string, arg_name):
    arg = query_string.get(arg_name, [])

    if type(arg) is not list:
        return arg

    if len(arg) == 1:
        return arg[0]

    if len(arg) > 1:
        return arg
