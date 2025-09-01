from typing import List, Tuple, Any


def ValidNames(name: str, fuzzy_search: bool = False) -> list:
    """
    Generate a list of valid name variations based on the input.

    Args:
        name (str): The input string to generate variations from.
        fuzzy_search (bool, optional): Whether to generate fuzzy variations.
                                       Defaults to False.

    Returns:
        list: A list of name variations (including the original if fuzzy_search
              is False, or multiple modified forms if True).
    """
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
    """
    Find common elements between two sorted lists using the two-pointer technique.
    This algorithm assumes both `list_a` and `list_b` are sorted in ascending order.

    Args:
        list_a (list): First sorted list.
        list_b (list): Second sorted list.

    Returns:
        list: A list of common elements found in both input lists.
    """
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


def multiway_match_strings(lists: List[List[Any]], names: List[Any] = None) -> Tuple[List[Tuple[str, int, List[Any]]], List[str], List[str], int]:
    """
    Find matches across N sorted lists of unique strings.

    Args:
        lists: list of sorted string lists
        names: optional list of identifiers for the lists (same length as lists) If None, defaults to list indices [0..N-1]

    Returns:
        all_matches: list of tuples (string, count, [list_names])
        full_matches: strings appearing in all lists
        partial_matches: strings appearing in more than one list but not all
        max_count: maximum number of lists any string appeared in
    """
    N = len(lists)
    if names is None:
        names = list(range(N))  # default list identifiers

    # Initialize pointers for each list
    pointers = [0] * N
    all_matches = []

    while True:
        # Gather current values from each list where pointer hasn't reached the end
        current_vals = []
        for i in range(N):
            if pointers[i] < len(lists[i]):
                current_vals.append((lists[i][pointers[i]], i))

        if not current_vals:
            break  # All lists are exhausted

        # Find the smallest string among current pointers
        min_val = min(val for val, _ in current_vals)

        # Track which lists contain this string
        matched_lists = []
        for val, idx in current_vals:
            if val == min_val:
                matched_lists.append(names[idx])
                pointers[idx] += 1  # advance pointer for this list

        # Record the string, count, and list names
        all_matches.append((min_val, len(matched_lists), matched_lists))

    # Extract full matches, partial matches, and maximum overlap
    full_matches = [s for s, count, _ in all_matches if count == N]
    partial_matches = [s for s, count, _ in all_matches if 1 < count < N]
    max_count = max(count for _, count, _ in all_matches) if all_matches else 0

    return all_matches, full_matches, partial_matches, max_count