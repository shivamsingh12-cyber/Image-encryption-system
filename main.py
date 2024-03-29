from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('login.html')

@app.route('/signup',methos=['GET','POST'])
def sign():
    if request.method =='POST':
        #handle request
        pass
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('dashboard.html')

if __name__=="__main__":
    app.run(debug=True)