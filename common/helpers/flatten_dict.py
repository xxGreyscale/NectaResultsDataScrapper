def flatten_dict(obj, parent_key=''):
    """
    Flatten a nested dictionary by concatenating keys with an underscore.
    Handles nested dictionaries and lists of dictionaries/primitives.
    Includes special handling for lists of dictionaries that have 'key' and 'value' fields,
    transforming them into a direct 'key': 'value' mapping.

    :param obj: The dictionary or list to flatten.
    :param parent_key: The prefix for the keys (used in recursive calls).
    :return: A new, flattened dictionary.
    """
    new_dict = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                if (isinstance(v, list) and
                        len(v) > 0 and
                        all(isinstance(item, dict) and 'key' in item and 'value' in item for item in v)):
                    # This block handles the specific 'metadata' list-of-dicts format
                    for item in v:
                        if 'key' in item and 'value' in item:
                            new_dict[item['key']] = item['value']
                elif (isinstance(v, list) and
                        len(v) > 0 and
                        all(isinstance(item, dict) and 'subject' in item and 'grade' in item for item in v)):
                    # This block handles the specific 'subjects' list-of-dicts format
                    for item in v:
                        if 'subject' in item and 'grade' in item:
                            new_dict[item['subject']] = item['grade']
                else:
                    # For other dicts or lists, proceed with standard flattening
                    new_dict.update(flatten_dict(v, new_key))
            else:
                new_dict[new_key] = v
    elif isinstance(obj, list):
        # This part handles generic lists (not the special 'metadata' type if it was nested)
        for i, item in enumerate(obj):
            new_key_with_index = f"{parent_key}_{i}"
            if isinstance(item, (dict, list)):
                new_dict.update(flatten_dict(item, new_key_with_index))
            else:
                new_dict[new_key_with_index] = item
    return new_dict
