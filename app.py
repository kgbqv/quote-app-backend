import random
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

def load_quotes():
    df = pd.read_csv('quotes.csv')
    df['category'] = df['tags'].apply(lambda x: str(x).split(';'))
    df = df.drop('tags', axis=1)
    return df

df_quotes = load_quotes()

@app.route('/random-quote', methods=['GET'])
def random_quote():
    random_row = df_quotes.sample(n=1).iloc[0]
    return jsonify({
        'id': str(random_row['index']),
        'quote': random_row['quote'],
        'author': random_row['author'],
        'category': random_row['category']
    })

@app.route('/search', methods=['POST'])
def search_quote():
    query = request.get_json().get('query', '')
    
    filtered_df = df_quotes[
        df_quotes['quote'].str.contains(query, case=False, na=False) |
        df_quotes['category'].apply(lambda categories: any(query in category.lower() for category in categories))
    ]
    
    if not filtered_df.empty:
        filtered_df.sort_values('likes', inplace=True,ascending=False)
        random_row = filtered_df.sample(n=1).iloc[0]
        return jsonify({
            'id': str(random_row['index']),
            'quote': random_row['quote'],
            'author': random_row['author'],
            'category': random_row['category']
        })
    else:
        return jsonify({"error": "No matching quotes found."})

@app.route('/fetch-quote', methods=['POST'])
def fetch_quote():
    quote_id = request.get_json().get('id', '')
    
    filtered_df = df_quotes[
        df_quotes['index'] == int(quote_id)
    ]
    
    if not filtered_df.empty:
        random_row = filtered_df.iloc[0]
        return jsonify({
            'id': str(random_row['index']),
            'quote': random_row['quote'],
            'author': random_row['author'],
            'category': random_row['category']
        })
    else:
        return jsonify({"error": "Quote not found."})

if __name__ == '__main__':
    app.run(debug=True)
