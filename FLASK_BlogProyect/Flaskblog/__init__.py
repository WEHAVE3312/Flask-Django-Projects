from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

app.config['SECRET_KEY'] = 'SecretsIsRevealed'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/BDblog'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
#en caso de no estar logeado,redireccionara a la pagina login
login_manager.login_view = 'login'
#Agrega la clase de bootstrap 'info' a todos los mensajes
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "testyosu@gmail.com"
app.config['MAIL_PASSWORD'] = 'yosuetesting'
mail = Mail(app)

from Flaskblog import routes