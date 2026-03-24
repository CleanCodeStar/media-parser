import os

from flask import Flask

from src.api import parse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# 注册API蓝图
app.register_blueprint(parse.bp, url_prefix='/parse/api')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8051)
