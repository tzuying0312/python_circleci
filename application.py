from flask import Flask
application = Flask(__name__)

@application.route('/', methods=['GET'])
def home():
    return "Hello World!"

def init_api():
    application.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    init_api()
