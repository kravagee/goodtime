import datetime
from datetime import date
import json

from flask import Flask, redirect, render_template, request
from flask_login import LoginManager, login_required, logout_user, login_user, current_user

from data import db_session
from data.event import Event
from data.organization import Organization
from data.stats_users import StatsUser
from data.user import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '123456'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    db_sess.close()
    return user


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        surname = request.form['surname']
        last_name = request.form['last_name']
        year, month, day = [int(i) for i in request.form['birthday'].split('-')]
        birthday = date(year, month, day)
        password = request.form['password']
        db_sess = db_session.create_session()

        user = User()
        if db_sess.query(User).filter(User.username == username).first():
            return render_template('register.html', error={'username':
                                                               'Пользователь с таким логином уже существует'},
                                   current_user=current_user)
        user.username = username
        user.name = name
        user.surname = surname
        user.last_name = last_name
        user.birthday = birthday
        user.set_password(password)

        db_sess.add(user)
        db_sess.commit()

        stats = StatsUser()
        stats.user_id = user.id
        stats.events_count = 0
        stats.hours_count = 0
        stats.orgs_owned = 0

        db_sess.add(stats)
        db_sess.commit()
        login_user(user)
        db_sess.close()
        return redirect('/home')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            login_user(user)
            db_sess.close()
            return redirect('/home')
        else:
            error = 'Неверное имя пользователя или пароль'
    return render_template('login.html', error=error)


@app.route('/home')
@login_required
def home():
    db_sess = db_session.create_session()
    stats = db_sess.query(StatsUser).filter(StatsUser.user_id == current_user.id).first()
    db_sess.close()
    return render_template('home.html', current_user=current_user, stats=stats)


@app.route('/events_list', methods=['GET'])
def events_list():
    db_sess = db_session.create_session()
    query = db_sess.query(Event)

    city = request.args.get('city')
    if city:
        query = query.filter(Event.city == city)

    date_from = request.args.get('date_from')
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(Event.date >= date_from_obj)

    date_to = request.args.get('date_to')
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        query = query.filter(Event.date <= date_to_obj)

    status = request.args.get('status')

    for ev in query:
        if ev.date < datetime.datetime.now():
            ev.done = True

    if status == 'upcoming':

        query = query.filter(Event.done == False)
    elif status == 'completed':
        query = query.filter(Event.done == True)


    my_events = request.args.get('my_events')
    if my_events == 'true' and current_user.is_authenthicated:
        us = db_sess.query(User).filter(User.id == current_user.id).first()
        if us.registred_on:
            rgst = json.loads(us.registred_on)['id']
            evs = query.filter(Event.id.in_(rgst)).all()
        else:
            rgst = []
            evs = query.filter(Event.id.is_(None)).all()
    else:
        evs = query.all()

    all_cities = db_sess.query(Event.city).distinct().all()
    cities = [city[0] for city in all_cities if city[0]]

    db_sess.close()
    return render_template('events_list.html',
                           evs=evs,
                           cities=cities,
                           selected_city=city,
                           date_from=date_from,
                           date_to=date_to,
                           status=status,
                           now=datetime.datetime.now(), current_user=current_user)


@app.route('/create_organization', methods=['POST', 'GET'])
@login_required
def create_organization():
    error = ''
    if request.method == 'POST':
        name = request.form['name']
        owner_id = current_user.id
        db_sess = db_session.create_session()
        if db_sess.query(Organization).filter(Organization.name == name).first():
            error = 'Неверное имя пользователя'
            db_sess.close()
            return render_template('create_organization.html', error=error, current_user=current_user)
        organization = Organization()
        organization.name = name
        organization.owner_id = owner_id
        db_sess.add(organization)
        db_sess.commit()

        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if user.owned_orgs:
            org_list = json.loads(user.owned_orgs)
            org_list['id'].append(organization.id)
            user.owned_orgs = json.dumps(org_list)
        else:
            org_list = dict()
            org_list['id'] = [organization.id]
            user.owned_orgs = json.dumps(org_list)

        stats = db_sess.query(StatsUser).filter(StatsUser.user_id == current_user.id).first()
        stats.orgs_owned += 1

        db_sess.commit()
        db_sess.close()
    return render_template('create_organization.html', error=error, current_user=current_user)


@app.route('/organizations_list', methods=['GET'])
@login_required
def organizations_list():
    db_sess = db_session.create_session()
    ev = 0
    orgs = db_sess.query(Organization).filter(Organization.owner_id == current_user.id).all()
    db_sess.close()
    return render_template('organizations_list.html', orgs=orgs, ev=ev, current_user=current_user)


@app.route('/organization_events/<int:org_id>', methods=['GET'])
@login_required
def organization_events(org_id):
    db_sess = db_session.create_session()
    org = db_sess.query(Organization).filter(Organization.id == org_id).first()
    if org.owner_id != current_user.id:
        db_sess.close()
        return redirect('/access_denied')
    events = db_sess.query(Event).filter(Event.organization_id == org_id).all()
    for ev in events:
        if ev.date < datetime.datetime.now():
            ev.done = True
            db_sess.commit()
            db_sess.close()
    return render_template('organizations_events.html', events=events, org_id=org_id, current_user=current_user)


@app.route('/access_denied')
def access_denied():
    return render_template('access_denied.html')


@app.route('/create_event/<int:org_id>', methods=['GET', 'POST'])
@login_required
def create_event(org_id):
    if request.method == 'POST':
        db_sess = db_session.create_session()
        org = db_sess.query(Organization).filter(Organization.id == org_id).first()

        if org.owner_id != current_user.id:
            db_sess.close()
            return redirect('/access_denied')

        event = Event()
        event.name = request.form['name']
        event.description = request.form['description']
        event.city = request.form['city']

        year, month, day = [int(i) for i in request.form['datetime'].split('T')[0].split('-')]
        hours, minutes = [int(i) for i in request.form['datetime'].split('T')[1].split(':')]

        event.date = datetime.datetime(year, month, day, hours, minutes)
        event.hours = request.form['hours']
        event.organization_id = org_id
        db_sess.add(event)
        db_sess.commit()

        if org.events_list:
            ev_list = json.loads(org.events_list)
            ev_list['id'].append(event.id)
            org.events_list = json.dumps(ev_list)
        else:
            ev_list = dict()
            ev_list['id'] = [event.id]
            org.events_list = json.dumps(ev_list)

        org.events_count = org.events_count + 1 if org.events_count else 1

        db_sess.commit()
        db_sess.close()
    return render_template('create_event.html', current_user=current_user)


@app.route('/event_detail/<int:event_id>', methods=['GET'])
def event_detail(event_id):
    db_sess = db_session.create_session()
    reg = False
    ev = db_sess.query(Event).filter(Event.id == event_id).first()
    if current_user.is_authenticated and current_user.registred_on:
        regst = json.loads(current_user.registred_on)
        reg = True if event_id in regst['id'] else False
    db_sess.close()
    return render_template('event_detail.html', reg=reg, ev=ev, current_user=current_user)


@app.route('/register_to_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def register_to_event(event_id):
    db_sess = db_session.create_session()
    us = db_sess.query(User).filter(User.id == current_user.id).first()
    event = db_sess.query(Event).filter(Event.id == event_id).first()
    stats = db_sess.query(StatsUser).filter(StatsUser.user_id == current_user.id).first()

    if us.registred_on:
        regst = json.loads(us.registred_on)
        regst['id'].append(event_id)
        us.registred_on = json.dumps(regst)
    else:
        regst = dict()
        regst['id'] = [event_id]
        us.registred_on = json.dumps(regst)

    if event.saint_persons_list:
        pers = json.loads(event.saint_persons_list)
        pers['id'].append(us.id)
        event.saint_persons_list = json.dumps(pers)
    else:
        pers = dict()
        pers['id'] = [us.id]
        event.saint_persons_list = json.dumps(pers)

    event.saint_persons_count = event.saint_persons_count + 1 if event.saint_persons_count else 1

    stats.events_count = stats.events_count + 1 if stats.events_count else 1
    stats.hours_count = stats.hours_count + event.hours if stats.hours_count else event.hours
    db_sess.commit()
    db_sess.close()
    return redirect(f'/event_detail/{event_id}')


@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('unauthorized.html'), 401


db_session.global_init('db/dobro.db')
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
