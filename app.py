from flask import Flask, render_template, request
from main import parse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    platform = request.form.get('platform')
    url = request.form.get('url')
    
    result = parse(platform, url)
    
    if result is None:
        return "Произошла ошибка: результат равен None"
    
    if 'error' in result:
        return f"Произошла ошибка: {result['error']}"
    
    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
