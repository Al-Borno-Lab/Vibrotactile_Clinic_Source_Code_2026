def json_key_recursive_find(json_dict, key_to_find, parent=None):
    """
    
    - Recursive function cannot bottom out when finding the desired key because searches will then be stopped.
    - Instead, recursive func bottoms out at the leaf node of the JSON tree.
    """
    
    if parent is None:
        parent = []
    found_paths = []

    if isinstance(json_dict, list):
        for list_idx, list_item in enumerate(json_dict):
            temp_parent = parent + [list_idx]
            found_path = json_key_recursive_find(list_item, key_to_find, temp_parent)
            if found_path is not None: found_paths = found_paths + found_path
        return found_paths

    if isinstance(json_dict, dict):
        for key, value in json_dict.items():

            if key == key_to_find:
                path = parent + [key]
                found_paths.append(path)
                # print(f"Found {key} at {path}")  # DEBUG
            else:
                temp_parent = parent + [key]
                found_path = json_key_recursive_find(value, key_to_find, temp_parent)
                if found_path is not None: found_paths = found_paths + found_path
        return found_paths

    if isinstance(json_dict, str):
        return found_paths

        
def get_nested_json_value(json_obj, record_path):
    
    first_pass = True
    
    for key in record_path:
        if first_pass: 
            first_pass = False
            output = json_obj[key]
        else: 
            output = output[key]
            
    return output