from flask import Flask, render_template, request, url_for, session
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from flask import Flask, flash, request, redirect, url_for
import random
from datetime import datetime
import os
from flask import send_from_directory
from flask import send_file
from steganography import create_image, decode_image

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///imageencrypt.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"]= False
db=SQLAlchemy(app)
app.secret_key="secret_key"


class imageencrypt(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(100), nullable=False)
    phone=db.Column(db.String(100), nullable=False)
    payment=db.Column(db.String(30), nullable=True)
    username=db.Column(db.String(100), nullable=False)
    password=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(150), nullable=False)

    def __repr__(self,sno,fname,password,phone,payment,username,email):
        self.sno = sno
        self.fname = fname
        self.phone = phone
        self.payment = payment
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.username = username
        self.email = email
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        #handle request
        username=request.form['uname']
        password=request.form['password']

        user = imageencrypt.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['name']=user.username
            session['fee']=user.payment
            return redirect('/home')
    elif 'name' in session:
     return redirect('/home')
        
    else:
        return render_template('login.html')
  

@app.route('/signup',methods=['GET','POST'])
def sign():
    if request.method =='POST':
        #handle request
        name=request.form['fname']
        phone=request.form['phone']
        username=request.form['uname']
        password=request.form['password']
        email=request.form['email']

        new_user = imageencrypt(fname=name,phone=phone,username=username,password=password,email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

        pass
    return render_template('signup.html')


def encrypt(file):
    fo = open(file, "rb")
    image=fo.read()
    fo.close()
    image=bytearray(image)
    key=random.randint(0,256)
    for index , value in enumerate(image):
       image[index] = value^key
    fo=open("enc.jpg","wb")
    imageRes="enc.jpg"
    fo.write(image)
    fo.close()
    return (key,imageRes)

def decrypt(key,file):
    fo = open(file, "rb")
    image=fo.read()
    fo.close()
    image=bytearray(image)
    for index , value in enumerate(image):
     image[index] = value^key
    fo=open("dec.jpg","wb")
    imageRes="dec.jpg"
    fo.write(image)
    fo.close()
    return imageRes





@app.route('/home')
def index():
    if 'name' in session:
        user=imageencrypt.query.filter_by(username=session['name']).first()
        """Renders the home page."""
        return render_template('index.html',title='Home Page',year=datetime.now().year,user=user,display="Pay to use feature")
    else:
        return redirect('login')

@app.route('/logout')
def logout():
        session.pop('name',None)
        return redirect('/login')

@app.route('/decrypt')
def contact():
    if 'name' in session:
        user=imageencrypt.query.filter_by(username=session['name']).first()
        """Renders the contact page."""
        return render_template(
            'decrypt.html',
            title='Decrypt',
            year=datetime.now().year,
            message='Upload your encrypted image along with the key',
            user=user
        )
    else:
        return redirect('/login')

@app.route('/encrypt')
def about():
    if 'name' in session:
        user=imageencrypt.query.filter_by(username=session['name']).first()
        """Renders the about page."""
        return render_template(
            'encrypt.html',
            title='Encrypt',
            year=datetime.now().year,
            message='Upload the image here',
            user=user
        )
    else:
        return redirect('/login')

@app.route('/decrypt1', methods = ['POST'])  
def contact1():  
    if 'name' in session:
        user=imageencrypt.query.filter_by(username=session['name']).first()
        if request.method == 'POST':  
            global f
            f = request.files['file']  
            f.save(f.filename)  
            text = request.form['key']
            key=int(text)
            image=decrypt(key,f.filename)
            return render_template('decrypt1.html',
            title='Decrypted',
            year=datetime.now().year,
            message='This is your Decrypted image', name = f.filename,user=user) 
    else:
     return redirect('/login')

@app.route('/encrypt1', methods = ['GET','POST'])  
def about1():  
    if 'name' in session:
        user=imageencrypt.query.filter_by(username=session['name']).first()
        if request.method == 'POST':  
            global f
            f = request.files['file']  
            f.save(f.filename)  
            key,image=encrypt(f.filename)
            return render_template('encrypt1.html',
            title='Encrypted',
            year=datetime.now().year,
            message='This is your encrypted image', name = f.filename,keys=key,images=image,user=user)
    else:
     return redirect('/login')

@app.route('/return-file')
def return_file():
    return send_file("../enc.jpg",attachment_filename="enc.jpg")

@app.route('/return-file1')
def return_file1():
    return send_file("../dec.jpg",attachment_filename="dec.jpg")



## stegnography code
UPLOAD_FOLDER = os.path.join('static/images')
ALLOWED_EXTENSIONS = {'png'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if os.path.exists(app.config['UPLOAD_FOLDER']) is False:
    os.mkdir(app.config['UPLOAD_FOLDER'])


@app.route('/stegnography')
def home():
    if 'name' in session:
     user=imageencrypt.query.filter_by(username=session['name']).first()
     return render_template('stegno.html',user=user)
    
    else:
     return redirect('/login')


@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if 'name' in session:
        user=imageencrypt.query.filter_by(username=session['name']).first()
        if request.method == 'POST':

            # LOADING AND SAVING IMAGE
            if 'image' not in request.files:
                return 'there is no image in form!'
            image = request.files['image']
            path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)

            # delete cached file
            if os.path.isfile(path):
                os.remove(path)

            image.save(path)

            # STEGANOGRAPHY

            secret_message = request.form['secret_message']

            base_image_path = path
            create_image(secret_message, base_image_path)

            return render_template('result_encode.html', img_path=base_image_path,user=user)

        return render_template('encode.html',user=user)
    else:
        return redirect('/login')


@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if 'name' in session:
        user=imageencrypt.query.filter_by(username=session['name']).first()
        if request.method == 'POST':

            # LOADING AND SAVING IMAGE
            if 'image' not in request.files:
                return 'there is no image in form!'
            image = request.files['image']
            path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(path)

            # STEGANOGRAPHY

            secret = decode_image(path)
            return render_template('result_decode.html', secret=secret,user=user)

        return render_template('decode.html',user=user)
    else:
        return redirect('/login')

# Virus file detection Code

@app.route('/virusfile')
def virus():
    if 'name' in session:
     user=imageencrypt.query.filter_by(username=session['name']).first()
     return render_template('virus.html',user=user)
    else:
        return redirect('/login')

@app.route('/output', methods = ['GET', 'POST'])
def detect():
    user=imageencrypt.query.filter_by(username=session['name']).first()
    if 'name' in session:
        if request.method == 'POST':
                global file
                file = request.files['file']  
                file_name,extension = os.path.splitext(file.filename)
                if str(extension)==".exe":
                    return render_template('virus.html', 
                    output="File Detected:: ",
                    message=file_name+extension+" file is a virus file",user=user)
                else:
                    return render_template('virus.html', 
                    output="File Detected:: ",
                    message=file_name+extension+" file is not a virus file",user=user)
        return redirect('/virusfile')
    return redirect('/login')

@app.route('/<data>/pay',methods=['GET', 'POST'])
def pay(data):
    if 'name' in session:
        if request.method=='POST':
         pay=request.form['pay']
         user=imageencrypt.query.filter_by(username=data).first()
         if  user:
            user.payment=pay           
            db.session.commit()
            return redirect('/home')
    else:
        return render_template('/home',message="You have not paid")

@app.route('/pay')
def pay_page():
    if 'name' in session:
        user=imageencrypt.query.filter_by(username=session['name']).first()
        data=imageencrypt.query.filter_by(payment=session['fee'])
        return render_template('card.html',user=user,data=data)
    return redirect('/login')

if __name__=="__main__":
    app.run(debug=True)