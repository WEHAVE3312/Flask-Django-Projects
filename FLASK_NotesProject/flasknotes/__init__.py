from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = "KSFORGLORY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/BDnotes'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
#en caso de no estar logeado,redireccionara a la pagina login
login_manager.login_view = 'login'

from flasknotes import routes