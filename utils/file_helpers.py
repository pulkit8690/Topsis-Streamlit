def load_input_data(input_file):
    if input_file.endswith('.csv'):
        data = pd.read_csv(input_file)
    elif input_file.endswith('.xlsx'):
        data = pd.read_excel(input_file)
    else:
        return None
    return data

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS