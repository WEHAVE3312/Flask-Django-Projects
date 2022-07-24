from flasknotes import db,login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Modelos de la base de datos BD
class Notes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    note = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default = datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Note('{self.id}','{self.date}')"
    

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.String(60), nullable=False)
    Notes = db.relationship('Notes',backref='author', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}')"