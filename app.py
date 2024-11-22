from flask import Flask
from controllers import model
from controllers.database import db
from controllers.routes import main as main_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbms_se.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(main_routes)
app.secret_key ='achutha2704'
db.init_app(app) 

with app.app_context():
    db.create_all()  

if __name__ == '__main__': 
    app.run(debug=True)
 