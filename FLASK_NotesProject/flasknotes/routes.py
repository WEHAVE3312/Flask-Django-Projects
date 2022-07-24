from flask import Flask, redirect, render_template, request,url_for,flash
from datetime import datetime
from flasknotes.models import Notes, User
from flasknotes import app, db , bcrypt
from flask_login import login_user, current_user, logout_user,login_required
from flasknotes.forms import LoginForm,RegistrationForm,NewNote

# form = PostForm()
#     if form.validate_on_submit():
#         post = Post(title=form.title.data, content=form.content.data, author=current_user)
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created','success')
#         return redirect(url_for('home'))
#     return render_template('create_post.html',title='New Post',form=form,legend='New Post')


@app.route('/', methods=['POST','GET'])
@login_required
def index():
    form = NewNote()
    if form.validate_on_submit():
        note = Notes(note= form.content.data, author = current_user)
        db.session.add(note)
        db.session.commit()
        flash('Note added!')
        return redirect(url_for('index'))
    tasks = Notes.query.filter_by(author=current_user)
    user = User.query.filter_by(username=current_user.username).first_or_404()
    tasks = Notes.query.filter_by(author=user)\
            .order_by(Notes.date.desc())
    #print(tasks)
    return render_template('index.html', tasks=tasks,form=form)
    

@app.route('/register', methods=['GET','POST'] )
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,password=hashed_password)
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
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #compara las contraseñas encriptadas, base de datos - campos password del formulario
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            #si el usuario intento acceder a un pagina que necesita de un usuario, almacenara esta pagina
            #Y una vez logeado lo retornara a ella
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful.Please check email and password','danger')
    return render_template('Login.html',title='login',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


#Se declara una ruta que recibira de parametro el id de la task
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    #Busca en la base de datos la nota que contenga el ID
    noteDelete = Notes.query.get_or_404(id)
    if current_user == noteDelete.author:
        try:
            #Elimina la nota 
            db.session.delete(noteDelete)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a error deleting the note'
    else:
        return redirect('/')

        
  
#Ya que renderizara una pagina, se usara el metodo GET para obtener los parametros del enlace   
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
    #Busca en la base de datos la nota que contenga el ID
    task = Notes.query.get_or_404(id)
    #Si el request es del tipo POST, tomara el valor del input y modificara la nota
    if request.method == 'POST':
        task.note = request.form['input_note']
        if current_user == task.author:
            try:
                db.session.commit()
                return redirect('/')
            except:
                return 'There was an issue updating the note'
    else:
        #Si el metodo es de tipo GET renderiza la pagina y envia la task
        return render_template('update.html', task=task)
        
      