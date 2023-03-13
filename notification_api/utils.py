def check_attributes(data, attributes):
    return all(attr in data for attr in attributes)