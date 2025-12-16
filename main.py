from flask import Flask, redirect, render_template
from flask_login import LoginManager, login_required, logout_user, login_user, current_user

from data import db_session
from data.user import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '123456'

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
def index():
    if not current_user:
        return render_template('index.html')
    return render_template('index.html', current_user=current_user)


if __name__ == '__main__':
    db_session.global_init('db/dobro.db')
    app.run(port=8080, host='127.0.0.1')