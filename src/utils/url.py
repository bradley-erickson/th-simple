def parse_url_params(url_params):
    """
    Parses the query parameters from a URL string and converts them into a dictionary.

    Args:
    url_params (str): A string containing the URL parameters, e.g., "?a=123&b=456".

    Returns:
    dict: A dictionary with the parsed parameters.
    """
    # Removing the '?' if it's present at the start of the string
    if url_params.startswith('?'):
        url_params = url_params[1:]

    # Splitting the parameters by '&'
    pairs = url_params.split('&')

    # Splitting each pair by '=' and converting to a dictionary
    params_dict = {key: value for key, value in (pair.split('=') for pair in pairs)}

    return params_dict
