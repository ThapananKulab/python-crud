from flask import Flask, render_template, url_for, redirect, session, request
import os
import mysql.connector as mysql
import hashlib

app =  Flask(__name__)

app.secret_key = 'Thapanan'


conn = mysql.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    port = 3306,
    database = 'test_abc'
)

app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000


UPLOAD_PIC_FOLDER = os.path.join(os.path.dirname(__file__),"static/picture")

template_folder = os.path.join(os.path.dirname(__file__), "templates/")
app.static_folder = 'static'
app.static_url_path = '/static'

@app.route('/', methods=["GET","POST"])
def index():
    session['user'] = ''
    session['audit'] = False
    return render_template("sign-in.html")

@app.route('/sign-up', methods=["GET","POST"])
def sign_up():
    return render_template("sign-up.html")

@app.route('/validate-sign-up', methods=["GET","POST"])
def validate_sign_up():
    name = request.form['fname']
    user = request.form['user']
    password = request.form['password']
    cfpassword = request.form['cfpassword']

    if name != "" and user != "" and password !="" and password == cfpassword:
        encypt_passwd = hashlib.md5(password.encode()).hexdigest()
        cur = conn.cursor() 
        insert_sql = """
            INSERT INTO username(username,password,fullname,audit)
            VALUES(%s,%s,%s,%s)
        """
        val = (user,encypt_passwd,name,1)
        cur.execute(insert_sql, val)
        conn.commit()
        conn.close()
        return render_template('sign-up-success.html')
    else:
        return render_template('sign-up.html')
    
@app.route('/validate-sign-in', methods=["GET","POST"])
def validate_sign_in():
    user = request.form['user']
    passwd =  request.form['password']
    if user!='' and passwd!='':
        sql = '''
        SELECT password FROM username 
        WHERE username=%s
        '''
        val = (user,)
        
        conn.reconnect()
        cur = conn.cursor()
        cur.execute(sql,val)
        data = cur.fetchone()
        conn.close()

        encypt_passwd = hashlib.md5(passwd.encode()).hexdigest()
        if data[0] == encypt_passwd:
            session['user'] = user
            session['audit'] = True
            return render_template('sign-in-success.html')
        else:
             return render_template('sign-in.html')
    else:
        render_template('sign-in.html')
    
@app.route('/main-program', methods=["GET","POST"])
def main_program():
    if session['audit'] == True:
        return render_template('main.html')
    else:
         return redirect('/')
     
@app.route('/sign-out',methods=["GET","POST"])
def sign_out():
    session.pop('user')
    session.pop('audit')
    return redirect('/')

@app.route('/user',methods=["GET","POST"])
def user():
    conn.reconnect()
    cur = conn.cursor()
    sql = ''' 
            SELECT username,fullname,audit,picture
            FROM username 
    '''
    cur.execute(sql)
    data = cur.fetchall()
    conn.close
    return render_template('user.html',users=data)



@app.route('/user-add',methods=["GET","POST"])
def user_add():
    return render_template('user-add.html')
    
@app.route('/user-add-post',methods=["GET","POST"])
def user_add_post():
    name = request.form['fname']
    user = request.form['user']
    password = request.form['password']
    cfpassword = request.form['cfpassword']
    picture = request.files['picture']
    
    encypt_passwd = hashlib.md5(password.encode()).hexdigest()
    picture.save(os.path.join(UPLOAD_PIC_FOLDER,picture.filename))
    conn.reconnect()
    cur = conn.cursor()
    sql = ''' 
            INSERT INTO username(username,fullname,password,audit,picture)
            VALUES(%s,%s,%s,%s,%s)
    '''
    
    val = (user,name,encypt_passwd,1,picture.filename)
    cur.execute(sql,val)
    conn.commit()
    conn.close()
    return redirect('/user')

    

@app.route('/user-delete/<user>',methods=["GET","POST"])
def user_delete(user):
    conn.reconnect()
    cur = conn.cursor()
    sql = ''' 
           DELETE FROM username WHERE username=%s
    '''     
    val = (user,)
    cur.execute(sql,val)
    conn.commit()
    conn.close()
    return redirect('/user')

     
@app.errorhandler(404)
def paage_not_found(e):
    return render_template("404.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)