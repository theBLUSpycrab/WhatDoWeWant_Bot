def ValidNames(name: str, fuzzy_search: bool = False) -> list:
    if fuzzy_search:
        valid_names = []
        valid_names.append(name.lower())
        valid_names.append(name.upper())
        valid_names.append(name.replace(" ",""))
        valid_names.append(name.replace("-", ""))
        valid_names.append(name.replace("_",""))
        return valid_names
    else: 
        return [name]
