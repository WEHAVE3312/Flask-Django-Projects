
import email
import os
from PIL import Image
import secrets
from flask import render_template, url_for , flash , redirect, request, abort
from Flaskblog import app, db , bcrypt, mail
from Flaskblog.models import User,Post
from Flaskblog.forms import (RegistrationForm,LoginForm,UpdateAccountForm,
                             PostForm,RequestResetForm,ResetPasswordForm)
from flask_login import login_user, current_user, logout_user,login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    #paginacion-SQLAlchemy
    #Otra manera de enviar parametros por medio de url
    #de esta manera se puede asignar un delfault y no altera el url
    #no es necesario el atributo
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template("home.html",posts = posts)


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/register', methods=['GET','POST'] )
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created, Now you can Log in!','success')
        #Url_for retorna a la direccion de la ruta en flask(el nombre de la funcion), no al url de pagina
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    #current user es una intancia de flask-login, es un variable que se activa si un usuario esta logeado
    #Si una usuario esta logeado, retornara a la pagina home en lugar de la pagina login/register
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        #compara las contraseñas encriptadas, base de datos - campos password del formulario
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            #si el usuario intento acceder a un pagina que necesita de un usuario, almacenara esta pagina
            #Y una vez logeado lo retornara a ella
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful.Please check email and password','danger')
    return render_template('Login.html',title='login',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    #crea un nombre aleatorio para la imagen
    random_hex = secrets.token_hex(8)
    #Separa el nombre y la extencion del archivo
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics', picture_fn)
    
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    i.save(picture_path)
    
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'default.jpg':
        os.remove(prev_picture)
    
    return picture_fn
    
    
    

@app.route('/account', methods=['GET','POST'])
#El decorador login_required es usado para señalar las paginas que necesitan que un usuario este logeado
#para ingresar a ellas
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/'+ current_user.image_file)
    return render_template('account.html',title='Account', image_file=image_file,form=form)


@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='New Post',form=form,legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    #si el post no existe, retorna 404
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title,post=post)

@app.route("/post/<int:post_id>/update", methods=['GET','POST'] )
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been update!','success')
        return redirect(url_for('post',post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        return render_template('create_post.html',title='Update Post', form=form, legend='Update Post')
    
    
@app.route("/post/<int:post_id>/delete", methods=['POST'] )
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!','success')
    return redirect(url_for('home'))

#Obtiene todos los posts pertenecientes al usuario
@app.route('/user/<string:username>')
def user_posts(username):
    #paginacion-SQLAlchemy
    #Otra manera de enviar parametros por medio de url
    #de esta manera se puede asignar un default y no altera el url
    #no es necesario el atributo
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=5)
    return render_template("user_post.html",posts=posts,user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',sender='noreplay@demo.com',recipients=[user.email])
    msg.body = f'''To reset your password, visit de following link:
    {url_for('reset_token',token=token, _external=True)}
    
    if you did not make this request then simply ignore this email and no change anything.
    '''
    mail.send(msg)
    


@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset Password',form=form)


@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has benn update! You are now able to log in','success')
        #Url_for retorna a la direccion de la ruta en flask(el nombre de la funcion), no al url de pagina
        return redirect(url_for('login'))
    return render_template('reset_token.html',title='Reset Password',form=form)


