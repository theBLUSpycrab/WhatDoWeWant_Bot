from main import User

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

def TwoPointerSearch(list_a: list, list_b: list) -> list:
    matches = []
    i = 0
    j = 0
    while i < len(list_a) and j < len(list_b):
        if list_a[i] == list_b[j]:
            matches.append(list_a[i])
            i += 1
            j += 1
        elif list_a[i] < list_b[j]:
            i += 1
        else:
            j += 1
    return matches
