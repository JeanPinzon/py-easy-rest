def get_query_string_arg(query_string, arg_name):
    args = query_string.get(arg_name, [])

    if len(args) == 1:
        return args[0]

    if len(args) > 1:
        return args

    return None
