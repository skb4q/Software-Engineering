from flask import Flask, request, jsonify
import json
from wsd import wsddef
app = Flask(__name__)


@app.route('/get_def', methods=['POST'])
def get_definition():
    definition = wsddef.get_def(request.json) 
    #return jsonify(definition)
    return json.dumps(definition, ensure_ascii=False).encode('utf8')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4321, debug=True)
