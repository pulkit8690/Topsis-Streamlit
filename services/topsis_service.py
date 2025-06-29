def calculate_custom_score(data, weights, impacts):
    normalized_data = data.iloc[:, 1:].apply(lambda x: x / np.sqrt(np.sum(x**2)), axis=0)
    weighted_normalized_data = normalized_data * list(map(float, weights.split(',')))
    ideal_best = weighted_normalized_data.max() if impacts[0] == '+' else weighted_normalized_data.min()
    ideal_worst = weighted_normalized_data.min() if impacts[0] == '+' else weighted_normalized_data.max()
    custom_score = np.sqrt(np.sum((weighted_normalized_data - ideal_best)**2, axis=1)) / (
            np.sqrt(np.sum((weighted_normalized_data - ideal_best)**2, axis=1)) +
            np.sqrt(np.sum((weighted_normalized_data - ideal_worst)**2, axis=1))
    )
    return custom_score

def process_dataset(data, weights, impacts):
    custom_score = calculate_custom_score(data, weights, impacts)
    data['Custom Score'] = custom_score
    data['Rank'] = data['Custom Score'].rank(ascending=False)
    return data