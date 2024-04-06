from flask import Flask, render_template, request
from flask import render_template
from flask import Flask, flash, request, redirect, url_for
import random
from datetime import datetime
import os
from flask import send_from_directory
from flask import send_file
from steganography import create_image, decode_image

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

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
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/decrypt')
def contact():
    """Renders the contact page."""
    return render_template(
        'decrypt.html',
        title='Decrypt',
        year=datetime.now().year,
        message='Upload your encrypted image along with the key'
    )

@app.route('/encrypt')
def about():
    """Renders the about page."""
    return render_template(
        'encrypt.html',
        title='Encrypt',
        year=datetime.now().year,
        message='Upload the image here'
    )

@app.route('/decrypt1', methods = ['POST'])  
def contact1():  
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
        message='This is your Decrypted image', name = f.filename) 

@app.route('/encrypt1', methods = ['GET','POST'])  
def about1():  
    if request.method == 'POST':  
        global f
        f = request.files['file']  
        f.save(f.filename)  
        key,image=encrypt(f.filename)
        return render_template('encrypt1.html',
        title='Encrypted',
        year=datetime.now().year,
        message='This is your encrypted image', name = f.filename,keys=key,images=image)

@app.route('/return-file')
def return_file():
    return send_file("../enc.jpg",attachment_filename="enc.jpg")

@app.route('/return-file1')
def return_file1():
    return send_file("../dec.jpg",attachment_filename="dec.jpg")

@app.route('/signup',methods=['GET','POST'])
def sign():
    if request.method =='POST':
        #handle request
        pass
    return render_template('signup.html')


## stegnography code
UPLOAD_FOLDER = os.path.join('static/images')
ALLOWED_EXTENSIONS = {'png'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if os.path.exists(app.config['UPLOAD_FOLDER']) is False:
    os.mkdir(app.config['UPLOAD_FOLDER'])


@app.route('/stegnography')
def home():
    return render_template('stegno.html')


@app.route('/encode', methods=['GET', 'POST'])
def encode():
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

        return render_template('result_encode.html', img_path=base_image_path)

    return render_template('encode.html')


@app.route('/decode', methods=['GET', 'POST'])
def decode():

    if request.method == 'POST':

        # LOADING AND SAVING IMAGE
        if 'image' not in request.files:
            return 'there is no image in form!'
        image = request.files['image']
        path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(path)

        # STEGANOGRAPHY

        secret = decode_image(path)
        return render_template('result_decode.html', secret=secret)

    return render_template('decode.html')

if __name__=="__main__":
    app.run(debug=True)