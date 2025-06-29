def validate_email(email):
    if not email:
        return True  # If email is empty, allow it
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email.strip())

def validate_numeric_values(data):
    non_numeric_columns = data.iloc[:, 1:].applymap(lambda x: not np.isreal(x)).any()
    return not non_numeric_columns.any()

def validate_weights_impacts(weights, impacts, num_columns):
    try:
        weights_list = list(map(float, weights.split(',')))
    except ValueError:
        return False

    impacts_list = impacts.split(',')

    if len(weights_list) != num_columns - 1 or len(impacts_list) != num_columns - 1:
        return False

    if not all(impact in ['+', '-'] for impact in impacts_list):
        return False

    return True