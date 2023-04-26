import datetime
from os import abort

from flask import Flask, request, make_response, render_template, send_file, jsonify, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from flask_uploads import UploadSet, configure_uploads
from forms.application import ProjectsForm
import projects_api
from data import db_session, projects_resources
from data.application import Projects
from data.user import User
from forms.logins import LoginForm
from forms.log import RegisterForm

app = Flask(__name__)
login_manager = LoginManager()

UPLOAD_FOLDER = '/templates/images'

# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)
IMAGES = ['jpg', 'jpeg', 'png', 'gif']
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
configure_uploads(app, photos)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'file' in request.files:
        filename = photos.save(request.files['file'])
        return f'Файл {filename} успешно загружен!'
    return render_template('upll.html')


def abort_if_projects_not_found(projects_id):
    session = db_session.create_session()
    projects = session.query(Projects).get(projects_id)
    if not projects:
        abort(404, message=f"Projects {projects_id} not found")


@app.route('/download_docx/<int:id>')
@login_required
def download_docx(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    return send_file('applications\\text\\' + projects.fullnames + '.docx')


def main():
    db_session.global_init("db/db.db")
    app.run()

    print('Старт!')


def convert_to_binary_data(file):
    if file != '':
        # Преобразование данных в двоичный формат
        with open(file, 'rb') as file:
            blob_data = file.read()
        return blob_data


# User

# профиль юзера
@app.route('/user_profile')
@login_required
def user_profile():
    if current_user.is_authenticated:
        db_ses = db_session.create_session()
        user = db_ses.query(User).filter(User.id == current_user.get_id()).first()
        id = current_user.get_id()
        projects = db_ses.query(Projects).filter(Projects.user_id == id).all()

        if user.about:
            return render_template('profile.html', about_me=user.about, projects=projects)
        else:
            return render_template('profile.html', about_me='Пока пусто :(')


# изменение информации о себе в профиле
@app.route('/edit_user_profile', methods=['post', 'get'])
def edit_user_profile():
    if current_user.is_authenticated:
        if request.method == 'POST':
            about_me1 = request.form.get('aboutme')
            db_ses = db_session.create_session()
            user = db_ses.query(User).filter(User.id == current_user.get_id()).first()
            user.about = about_me1
            db_ses.commit()
            if about_me1:
                return render_template('profile.html', about_me=about_me1)
            else:
                return render_template('profile.html', about_me='Пока пусто :(')
        return render_template('edit_profile.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/ege')
def ege():
    return render_template('ege.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/approved_panel", methods=['GET', 'POST'])
def approved_panel():
    db_sess = db_session.create_session()
    if request.method == "POST":
        db_sess = db_session.create_session()
        search = request.form.get('text')
        projects1 = db_sess.query(Projects).filter(Projects.title.like(f"%{search.capitalize()}%") |
                                                   Projects.title.like(f"%{search.lower()}%") |
                                                   Projects.title.like(f"%{search.upper()}%")).all()
        return render_template("approved_application.html", projects=projects1)

    projects = db_sess.query(Projects).filter()

    return render_template("approved_application.html", projects=projects)


@app.route("/edit_news", methods=['GET', 'POST'])
def edit_news():
    db_sess = db_session.create_session()
    if request.method == "POST":
        db_sess = db_session.create_session()
        search = request.form.get('text')
        projects1 = db_sess.query(Projects).filter(Projects.title.like(f"%{search.capitalize()}%") |
                                                   Projects.title.like(f"%{search.lower()}%") |
                                                   Projects.title.like(f"%{search.upper()}%")).all()
        return render_template("edit_news.html", projects=projects1)

    projects = db_sess.query(Projects).filter()

    return render_template("edit_news.html", projects=projects)


@app.route('/viewing_project/<int:id>', methods=['GET', 'POST'])
def viewing_project(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()

    if request.method == 'POST':
        project_comment(id)

    with open('static/comments.txt', 'r') as f:
        comments = f.readlines()
    comments = [i.rstrip('\n') for i in comments[:-1]]
    comments_new = []
    for i in comments:
        new = i.split(':')
        nick = db_sess.query(User).filter(User.id == new[1]).first()
        if projects.id == int(new[2]):
            comments_new.append([new[0], nick])

    return render_template("viewing_project.html", projects=projects, comments=comments_new)


@app.route('/project_comment/<int:id>', methods=['GET', 'POST'])
def project_comment(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if request.form.get('text'):
        with open('static/comments.txt', 'a') as f:
            f.write(f'{request.form.get("text")}:{current_user.get_id()}:{id}\n')
        with open('static/comments.txt', 'r') as f:
            comments = f.readlines()
        comments = [i.rstrip('\n') for i in comments[:-1]]
        comments_new = []
        for i in comments:
            new = i.split(':')
            nick = db_sess.query(User).filter(User.id == new[1]).first()
            if projects.id == int(new[2]):
                comments_new.append([new[0], nick])
    return redirect(f'/viewing_project/{id}')


@app.route('/like_projects/<int:id>', methods=['GET', 'POST'])
def like_project(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if current_user.likes == str(current_user.likes):
        list_likes = current_user.likes.split()
    else:
        list_likes = [str(current_user.likes)]
    if current_user.dislikes == str(current_user.dislikes):
        list_dislikes = current_user.dislikes.split()
    else:
        list_dislikes = [str(current_user.dislikes)]

    if str(id) not in list_likes:
        if str(id) not in list_dislikes:
            list_likes.append(str(id))
            projects.like += 1
            current_user.likes = ' '.join(list_likes)
        else:
            del list_dislikes[list_dislikes.index(str(id))]
            projects.dislike -= 1
            current_user.dislikes = ' '.join(list_dislikes)
            list_likes.append(str(id))
            projects.like += 1
            current_user.likes = ' '.join(list_likes)
    else:
        del list_likes[list_likes.index(str(id))]
        projects.like -= 1
        current_user.likes = ' '.join(list_likes)
    db_sess.merge(current_user)
    db_sess.commit()
    return redirect(f'/viewing_project/{id}')


@app.route('/dislike_projects/<int:id>', methods=['GET', 'POST'])
@login_required
def dislike_project(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if current_user.likes == str(current_user.likes):
        list_likes = current_user.likes.split()
    else:
        list_likes = [str(current_user.likes)]
    if current_user.dislikes == str(current_user.dislikes):
        list_dislikes = current_user.dislikes.split()
    else:
        list_dislikes = [str(current_user.dislikes)]

    if str(id) not in list_dislikes:
        if str(id) not in list_likes:
            list_dislikes.append(str(id))
            projects.dislike += 1
            current_user.dislikes = ' '.join(list_dislikes)
        else:
            del list_likes[list_likes.index(str(id))]
            projects.like -= 1
            current_user.likes = ' '.join(list_likes)
            list_dislikes.append(str(id))
            projects.dislike += 1
            current_user.dislikes = ' '.join(list_dislikes)
    else:
        del list_dislikes[list_dislikes.index(str(id))]
        projects.dislike -= 1
        current_user.dislikes = ' '.join(list_dislikes)
    db_sess.merge(current_user)
    db_sess.commit()
    return redirect(f'/viewing_project/{id}')


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.get_id()).first()
        search = request.form.get('text')
        projects1 = db_sess.query(Projects).filter(Projects.title.like(f"%{search.capitalize()}%") |
                                                   Projects.title.like(f"%{search.lower()}%") |
                                                   Projects.title.like(f"%{search.upper()}%")).all()
        return render_template("index1.html", user=user)
    user = db_sess.query(User).filter(User.id == current_user.get_id()).first()
    if current_user.is_authenticated:
        projects = db_sess.query(Projects).filter(
            (Projects.user == current_user))
    else:
        projects = db_sess.query(Projects).filter()

    return render_template("index1.html", user=user)


# Отправляем заявку


@app.route('/application_submission', methods=['GET', 'POST'])
@login_required
def application_submission():
    form = ProjectsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        projects = Projects()
        projects.heading = form.heading.data
        projects.annotation = form.annotation.data
        filename = photos.save(request.files['file'])
        projects.image = filename
        current_user.projects.append(projects)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('application_submission.html', title='Добавление проекта',
                           form=form)


@app.route('/projects/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_projects(id):
    form = ProjectsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id).first()
        if projects.is_confirmed:
            projects.is_confirmed = False
        if projects:
            form.title.data = projects.title
            form.content.data = projects.content
            form.is_private.data = projects.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id).first()
        if projects.is_confirmed:
            projects.is_confirmed = False
        if projects:
            projects.title = form.title.data
            projects.content = form.content.data
            projects.is_private = form.is_private.data
            f = form.image.data
            if f.filename != '':
                save_to = f'static/temporary_img/{f.filename}'
                f.save(save_to)
                projects.image = convert_to_binary_data(save_to)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('projects.html',
                           title='Редактирование проекта',
                           form=form
                           )


@app.route('/projects_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def projects_delete(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if projects:
        projects.is_deleted = True
        db_sess.commit()
    else:
        abort(404)
    return redirect('/edit_news')


def main():
    db_session.global_init("db/db.db")
    app.register_blueprint(projects_api.blueprint)
    app.run()
    # для списка объектов
    api.add_resource(projects_resources.ProjectsListResource, '/api/v2/projects')

    # для одного объекта
    api.add_resource(projects_resources.ProjectsResource, '/api/v2/projects/<int:projects_id>')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
