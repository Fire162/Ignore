from flask import Flask, request, jsonify, render_template
import sqlite3
import json

app = Flask(__name__)

@app.before_request
def init_db():
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS data_store (
                            key TEXT PRIMARY KEY,
                            data TEXT NOT NULL
                        )''')
        conn.commit()

@app.route('/getData', methods=['GET'])
def get_data():
    key = request.args.get('key')
    if not key:
        return jsonify({'error': 'Key is required'}), 400

    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM data_store WHERE key = ?', (key,))
        row = cursor.fetchone()
        if row:
            value = json.loads(row[0])
            return jsonify({'data': value}), 200
        return jsonify({'error': 'Key not found'}), 404

@app.route('/saveData', methods=['POST'])
def save_data():
    data = request.json
    key = data.get('key')
    value = data.get('data')
    if not key or value is None:
        return jsonify({'success': False, 'error': 'Invalid key or data'}), 400

    value_str = json.dumps(value)

    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO data_store (key, data) VALUES (?, ?)', (key, value_str))
            conn.commit()
            return jsonify({'success': True}), 200
        except sqlite3.Error as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
    
