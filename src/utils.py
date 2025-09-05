def is_url(t):
    return isinstance(t,str) and t.startswith(("http://","https://"))
