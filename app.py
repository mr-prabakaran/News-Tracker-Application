from flask import Flask,render_template,session,redirect,url_for,request
import ibm_db
import re
import hashlib
from newsapi import NewsApiClient
import os
app = Flask(__name__)
app.secret_key = os.urandom(16)


try:
    conn = ibm_db.connect(os.getenv('KEY'),'','')
except Exception as err:
     print("Exception occurs->", err)



@app.route('/')
def index():
    if not session:
        return render_template('login.html')
    return redirect(url_for('home'))

@app.route('/login')
def login():
    if not session or not session['login_status']:
        return render_template('login.html')
    return redirect(url_for('home'))

@app.route('/registration')
def registration():
    return render_template('registration.html')
@app.route('/home')
def home():
    api_key = os.getenv('NEWS_API')
    
    newsapi = NewsApiClient(api_key=api_key)

    top_headlines = newsapi.get_top_headlines(sources = "bbc-news")
    all_articles = newsapi.get_everything(sources = "bbc-news")

    t_articles = top_headlines['articles']
    a_articles = all_articles['articles']

    news = []
    desc = []
    img = []
    p_date = []
    url = []

    for i in range (len(t_articles)):
        main_article = t_articles[i]

        news.append(main_article['title'])
        desc.append(main_article['description'])
        img.append(main_article['urlToImage'])
        p_date.append(main_article['publishedAt'])
        url.append(main_article['url'])

        contents = zip( news,desc,img,p_date,url)

    news_all = []
    desc_all = []
    img_all = []
    p_date_all = []   
    url_all = []

    for j in range(len(a_articles)): 
        main_all_articles = a_articles[j]   

        news_all.append(main_all_articles['title'])
        desc_all.append(main_all_articles['description'])
        img_all.append(main_all_articles['urlToImage'])
        p_date_all.append(main_all_articles['publishedAt'])
        url_all.append(main_article['url'])
        
        all = zip( news_all,desc_all,img_all,p_date_all,url_all)

    return render_template('home.html',contents=contents,all = all)

@app.route('/do_register',methods=['GET','POST'])
def do_register():
    if request.method == 'POST':
        email = request.form['email']
        #------------------
        # password hashing
        password = request.form['pwd']
        cnf_password = request.form['pwd-repeat']
        if password != cnf_password:
            msg = "Password Doesn't Match"
            return msg
        
        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()

        # case 1: check if user does exists already
        sql = "SELECT * FROM users WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if acc:
            msg = "Account already Exists, Please login "
            return msg

        # case 2: validate the input if it matches the required pattern
        if not re.match(r"^\S+@\S+\.\S+$", email):
            msg =  "Please Enter Valid Email Address "
            return msg

        insert_sql = "INSERT INTO  users VALUES (?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.bind_param(prep_stmt, 2, password)
        ibm_db.execute(prep_stmt)

        return redirect(url_for('login'))
    return redirect(url_for('registration'))











@app.route('/do_login',methods=['GET','POST'])
def do_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pswrd']
        # salt the password 
        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()

        #query the db
        sql = "SELECT * FROM users WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if not acc:
           return "<h1> User Not exists</h1>"
        if acc:
            session['login_status'] = True
            session['username'] = username
            session['user_id'] = username.split('@')[0]
            return redirect(url_for('home'))
    return redirect('registration.html')


@app.route('/logout')
def logout():
    session.pop('login_status',None)
    session.pop('user_id',None)
    session.pop('username',None)


    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

