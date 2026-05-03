import os
import uuid

from flask import Flask, render_template, redirect, request
from dotenv import load_dotenv
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from data.chats import Chat
from data.users import User
from data.messages import Message
from forms.edit_form import EditForm
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from werkzeug.utils import secure_filename

load_dotenv('.env')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'static/images/messages'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

login_manager = LoginManager()
login_manager.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_log_in():
    if not current_user.is_authenticated:
        return True


def check_friends_status():
    friends_data = {}
    if current_user.is_authenticated and current_user.friends:
        session = db_session.create_session()
        friend_ids = [int(fid.strip()) for fid in current_user.friends.split(',') if fid.strip()]
        friends = session.query(User).filter(User.id.in_(friend_ids), User.is_deleted == 0).all()
        friends_data = {friend.id: friend for friend in friends}
        session.close()
    return friends_data


@login_manager.user_loader
def user_loader(user_id):
    session = db_session.create_session()
    return session.get(User, user_id)


@app.route('/sign')
def sign():
    return render_template('sign.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(
            User.email == login_form.email.data
        ).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me)
            return redirect('/')
        return render_template('login.html', form=login_form, message='Ошибка входа')
    return render_template('login.html', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == register_form.email.data).first()
        if user:
            return render_template('register.html', form=register_form, message='Почта уже занята')
        user = session.query(User).filter(User.username == register_form.username.data).first()
        if user:
            return render_template('register.html', form=register_form, message='Никнейм уже занят')
        avatar_filename = uuid.uuid4().hex + '.png'
        if register_form.avatar.data:
            print(1)
            with open('static/images/avatars/' + avatar_filename, mode='wb') as avatar_file:
                avatar_file.write(register_form.avatar.data.read())
                print(register_form.avatar.data.read())
        else:
            print(2)
            with open('static/images/system/system_avatar.png', mode='rb') as system_avatar:
                with open('static/images/avatars/' + avatar_filename, mode='wb') as avatar_file:
                    avatar_file.write(system_avatar.read())
        new_user = User(
            username=register_form.username.data, surname=register_form.surname.data, name=register_form.name.data,
            age=register_form.age.data, description=register_form.description.data,
            avatar='static/images/avatars/' + avatar_filename,
            email=register_form.email.data, hashed_password=register_form.hashed_password.data, friends='',
            is_deleted=False
        )
        new_user.hash_password(new_user.hashed_password)
        session.add(new_user)
        session.commit()
        login_user(new_user)
        return redirect('/')
    return render_template('register.html', form=register_form)


@app.route('/')
def index():
    if check_log_in():
        return redirect('/sign')
    friends_data = check_friends_status()
    return render_template('base.html', title='ZeK', friends_data=friends_data)


@app.route('/logout')
def logout():
    if check_log_in():
        return redirect('/sign')
    logout_user()
    return redirect('/')


@app.route('/settings')
def settings():
    if check_log_in():
        return redirect('/sign')
    friends_data = check_friends_status()
    return render_template('settings.html', title='Параметры аккаунта', friends_data=friends_data)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if check_log_in():
        return redirect('/sign')
    friends_data = check_friends_status()

    edit_form = EditForm()

    if edit_form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        email_exists = session.query(User).filter(
            User.email == edit_form.email.data,
            User.id != current_user.id
        ).first()
        if email_exists:
            return render_template('edit_profile.html', form=edit_form, message='Почта уже занята')
        username_exists = session.query(User).filter(
            User.username == edit_form.username.data,
            User.id != current_user.id
        ).first()
        if username_exists:
            return render_template('edit_profile.html', form=edit_form, message='Никнейм уже занят')
        with open(current_user.avatar, mode='wb') as avatar_file:
            avatar_file.write(edit_form.avatar.data.read())
        user.username = edit_form.username.data
        user.surname = edit_form.surname.data
        user.name = edit_form.name.data
        user.age = edit_form.age.data
        user.description = edit_form.description.data
        user.email = edit_form.email.data

        session.commit()
        login_user(user)

        return redirect('/')

    return render_template('edit_profile.html', title='Редактировать профиль', friends_data=friends_data,
                           form=edit_form)


@app.route('/messenger')
@login_required
def messenger():
    session = db_session.create_session()

    search_query = request.args.get('search', '').strip().lower()

    all_chats = session.query(Chat).all()
    chats_data = []

    for chat in all_chats:
        if not chat.members:
            continue
        members_list = [int(mid.strip()) for mid in chat.members.split(',') if mid.strip()]
        if current_user.id in members_list:
            chat_name = chat.name
            is_group = True

            if not chat_name or chat_name.strip() == '':
                is_group = False
                other_members = [m for m in members_list if m != current_user.id]
                if other_members:
                    other_user = session.query(User).get(other_members[0])
                    if other_user:
                        chat_name = f"{other_user.name} {other_user.surname}"

            if search_query and search_query not in chat_name.lower():
                continue

            last_message_text = 'Нет сообщений'
            last_message_time = ''

            if chat.messages and chat.messages.strip():
                message_ids = [int(mid.strip()) for mid in chat.messages.split(',') if mid.strip()]
                if message_ids:
                    last_msg = session.query(Message).filter(Message.id.in_(message_ids)).order_by(
                        Message.id.desc()).first()
                    if last_msg:
                        if last_msg.type == 'image':
                            last_message_text = '📷 Изображение'
                        else:
                            last_message_text = last_msg.message[:50]
                            if len(last_msg.message) > 50:
                                last_message_text += '...'
                        if hasattr(last_msg, 'created_at') and last_msg.created_at:
                            last_message_time = last_msg.created_at.strftime('%H:%M')

            chats_data.append({
                'id': chat.id,
                'name': chat_name,
                'is_group': is_group,
                'last_message': last_message_text,
                'last_message_time': last_message_time,
                'unread': 0,
                'avatar': None
            })

    chat_id = request.args.get('chat_id', type=int)
    selected_chat = None
    messages = []

    if chat_id:
        chat = session.query(Chat).get(chat_id)
        if chat and chat.members:
            members_list = [int(mid.strip()) for mid in chat.members.split(',') if mid.strip()]
            if current_user.id in members_list:
                chat_name = chat.name
                is_group = True
                if not chat_name or chat_name.strip() == '':
                    is_group = False
                    other_members = [m for m in members_list if m != current_user.id]
                    if other_members:
                        other_user = session.query(User).get(other_members[0])
                        if other_user:
                            chat_name = f"{other_user.name} {other_user.surname}"

                selected_chat = {
                    'id': chat.id,
                    'name': chat_name,
                    'is_group': is_group,
                    'avatar': None
                }

                if chat.messages and chat.messages.strip():
                    message_ids = [int(mid.strip()) for mid in chat.messages.split(',') if mid.strip()]
                    msgs = session.query(Message).filter(Message.id.in_(message_ids)).order_by(Message.id).all()
                    for msg in msgs:
                        messages.append({
                            'id': msg.id,
                            'type': msg.type,
                            'message': msg.message,
                            'time': msg.created_at.strftime('%H:%M') if hasattr(msg,
                                                                                'created_at') and msg.created_at else '12:00',
                            'is_sent': msg.owner == current_user.id
                        })

    friends_list = []
    if current_user.friends and current_user.friends.strip():
        friend_ids = [int(fid.strip()) for fid in current_user.friends.split(',') if fid.strip()]
        friends = session.query(User).filter(User.id.in_(friend_ids), User.is_deleted == 0).all()
        for friend in friends:
            friends_list.append({
                'id': friend.id,
                'name': friend.name,
                'surname': friend.surname
            })

    friends_data = check_friends_status()

    return render_template('messenger.html',
                           title='Мессенджер',
                           friends_data=friends_data,
                           friends_list=friends_list,
                           chats=chats_data,
                           selected_chat=selected_chat,
                           messages=messages,
                           search_query=search_query)


@app.route('/create_chat', methods=['POST'])
@login_required
def create_chat():
    chat_name = request.form.get('chat_name', '')
    member_ids = request.form.getlist('members')

    members = [int(mid) for mid in member_ids if mid]
    if current_user.id not in members:
        members.append(current_user.id)

    session = db_session.create_session()

    if len(members) == 2 and not chat_name:
        existing_chat = session.query(Chat).filter(
            Chat.members.like(f'%{members[0]}%'),
            Chat.members.like(f'%{members[1]}%')
        ).first()
        if existing_chat:
            session.close()
            return redirect(f'/messenger?chat_id={existing_chat.id}')

    new_chat = Chat(
        name=chat_name if chat_name else 'Новый чат',
        members=','.join(map(str, members)),
        messages=''
    )
    session.add(new_chat)
    session.commit()
    chat_id = new_chat.id
    session.close()

    return redirect(f'/messenger?chat_id={chat_id}')


@app.route('/send_message/<int:chat_id>', methods=['POST'])
@login_required
def send_message(chat_id):
    message_text = request.form.get('message', '').strip()
    image_file = request.files.get('image')

    session = db_session.create_session()
    chat = session.query(Chat).get(chat_id)

    if not chat:
        session.close()
        return redirect('/messenger')

    if chat.members:
        members_list = [int(mid.strip()) for mid in chat.members.split(',') if mid.strip()]
        if current_user.id not in members_list:
            session.close()
            return redirect('/messenger')

    if image_file and image_file.filename and allowed_file(image_file.filename):
        filename = uuid.uuid4().hex + '_' + secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        new_message = Message(
            type='image',
            message=f'/static/images/messages/{filename}',
            owner=current_user.id
        )
    elif message_text:
        new_message = Message(
            type='text',
            message=message_text,
            owner=current_user.id
        )
    else:
        session.close()
        return redirect(f'/messenger?chat_id={chat_id}')

    session.add(new_message)
    session.flush()

    if chat.messages and chat.messages.strip():
        chat.messages = chat.messages + f',{new_message.id}'
    else:
        chat.messages = str(new_message.id)

    session.commit()

    return redirect(f'/messenger?chat_id={chat_id}')


if __name__ == '__main__':
    db_session.global_init('db/Zek.db')
    app.run('127.0.0.1', 8080)
