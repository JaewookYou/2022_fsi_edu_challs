#-*-coding:utf-8-*-
import flask
import os, pymysql, re, hashlib, time, base64, io
import logging, traceback
logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(level=logging.WARNING)

time.sleep(3)

app = flask.Flask(__name__)
app.secret_key = os.urandom(16)
app.config['MAX_CONTENT_LENGTH'] = 80 * 1024 * 1024

class mysqlapi:
    def __init__(self):
        self.conn = pymysql.connect(
            user = 'user',
            passwd = 'th1s_1s_user_p4ssw0rd',
            host = '172.22.0.5',
            db = 'fsi2022',
            charset = 'utf8'
        ) 
        self.conn.autocommit(True)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def safeQuery(self, req):
        for key in req.keys():
            req[key] = re.sub(r"[\'\"\\\(\)\|\&\[\]\!\@\#\$\%]",r'\\\g<0>', req[key])

        return req

    def duplicatedCheck(self, req):
        req = self.safeQuery(req)
        query = f"select userid from fsi2022.users where userid='{req['userid']}'"
        result = self.doSelectQuery(query)
        
        if result != ():
            return True
        else:
            return False

    def doLogin(self, req):
        req = self.safeQuery(req)
        query = f"select userid from fsi2022.users where userid='{req['userid']}' and userpw='{req['userpw']}'"
        logging.info(f"[+] query(login) - {query}")
        result = self.doSelectQuery(query)
        logging.info(f"[+] result(login) - {result}")
        if result:
            return result[0]
        elif result == ():
            return "id or pw wrong!"
        else:
            return "error!"

    def doRegister(self, req):
        req = self.safeQuery(req)        
        if self.duplicatedCheck(req):
            return "[x] duplicated id"

        query = f"insert into fsi2022.users (userid, userpw) values('{req['userid']}', '{req['userpw']}')"
        logging.info(f"[+] query(register) - {query}")
        self.cursor.execute(query)
        self.conn.commit()
        
        if self.duplicatedCheck(req):
            return "[+] register success"
        else:
            return False

    def getBoardList(self, req):
        req = self.safeQuery(req)
        query = f"select seq, subject, author from fsi2022.board"
        logging.info(f"[+] query(getboardlist) - {query}")
        result = self.doSelectQuery(query)
        if result:
            return list(result)
        else:
            return "error!"

    def writeBoard(self, req):
        req = self.safeQuery(req)
        if req['filepath'] and req['filecontent']:
            if not self.uploadFile(req):
                return "duplicated file or upload error"

        query = f"insert into fsi2022.board (subject, content, author, loginid, filepath) values('{req['subject']}', '{req['content']}', '{req['author']}', '{req['loginid']}', '{req['filepath'] if req['filepath'] != '' else ''}')"

        logging.info(f"[+] query(writeboard) - {query}")
        self.cursor.execute(query)
        self.conn.commit()
        

    def uploadFile(self, req):
        req = self.safeQuery(req)
        isexist = self.checkExistFile(req['filepath'])
        if isexist:
            return "duplicated file"
        
        query = f"select '{req['filecontent']}' into outfile '/upload/{req['filepath']}'"
        result = self.doSelectQuery(query)

        return True

    def getBoardView(self, req):
        req = self.safeQuery(req)
        query = f"select subject, author, content, filepath from fsi2022.board where seq={req['seq']}"
        logging.info(f"[+] query(getBoardView) - {query}")
        result = self.doSelectQuery(query)
        logging.info(f"[+] result(getBoardView) - {result}")

        if result:
            return result
        else:
            return False
    
    def checkExistFile(self, filepath):
        req = self.safeQuery({'filepath':filepath})
        query = f"select count(load_file('/upload/{req['filepath']}'))"
        logging.info(f"[+] query(checkExistFile) - {query}")
        result = self.doSelectQuery(query)
        isExist = list(result[0].values())[0]
        logging.info(f"[+] result(checkExistFile) - {isExist}")
        if isExist:
            return True
        else:
            return False

    def download(self, filepath):
        query = f"select loginid from fsi2022.board where filepath='{filepath}' limit 0,1"
        logging.info(f"[+] query(download) - {query}")
        result = self.doSelectQuery(query)
        if type(result)==str:
            return f"download error.. {result}"

        if len(result)>0:
            fileOwner = list(result[0].values())[0]
            logging.info(f"[+] result(download) - {fileOwner}")
        else:
            return f"select result has no data"

        query = f"select load_file('/upload/{filepath}')"
        self.cursor.execute(query)
        result = base64.b64decode(list(self.cursor.fetchall()[0].values())[0])
        return {'result': result}
        
    
    def doSelectQuery(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            return str(e)


db = mysqlapi()

def checkUserIDPW(userid, userpw):
    if re.search(r"[^\w]",userid) or len(userid) == 0 or len(userid) > 50 or len(userpw) == 0 or len(userpw) > 50:
        return False
    else:
        return True

def sessionCheck(loginCheck=False):   
    if loginCheck:
        if "isLogin" not in flask.session:
            return False
        else:
            return True

    if "isLogin" in flask.session:
        return True
    
    return False


@app.route("/")
def index():
    return flask.redirect(flask.url_for("login"))


@app.route("/logout")
def logout():
    flask.session.pop('isLogin', False)
    return flask.redirect(flask.url_for("login"))


@app.route("/board", methods=["GET"])
def board():
    if not sessionCheck(loginCheck=True):
        return flask.redirect(flask.url_for("login"))

    results = db.getBoardList({'userid':flask.session["userid"]})

    return flask.render_template("board.html", results=results)


@app.route("/board/<seq>")
def viewboard(seq):
    if not sessionCheck(loginCheck=True):
        return flask.redirect(flask.url_for("login"))

    results = db.getBoardView({'userid':flask.session["userid"], 'seq':seq})
    if not results:
        return "<script>alert('?');location.replace('/');</script>"
    return flask.render_template("view.html", results=results[0])


@app.route("/write", methods=["GET", "POST"])
def write():
    if not sessionCheck(loginCheck=True):
        return flask.redirect(flask.url_for("login"))

    if flask.request.method == "GET":
        return flask.render_template("write.html")

    elif flask.request.method == "POST":
        subject = flask.request.form["subject"]
        content = flask.request.form["content"]
        file = flask.request.files["file"]
        filename = file.filename
        filecontent = base64.b64encode(file.read()).decode()
        
        req = {
            'subject':subject,
            'content':content,
            'author':flask.session['userid'],
            'loginid':flask.session['userid'],
            'filepath':filename,
            'filecontent':filecontent
        }

        result = db.writeBoard(req)

        if result:
            return '<script>alert("file upload error..");location.replace("/board");</script>'


        return flask.redirect(flask.url_for("board"))

@app.route("/download", methods=["GET"])
def download():
    if not sessionCheck(loginCheck=True):
        return flask.redirect(flask.url_for("login"))

    filepath = flask.request.args["filepath"]
    
    result = db.download(filepath)
    if type(result) == dict:
        return flask.send_file(
                    io.BytesIO(result['result']),
                    as_attachment=True,
                    attachment_filename=filepath
                )
    else:
        return f'<script>alert(`download err: {result}`);location.replace("/board");</script>'

@app.route("/login", methods=["GET","POST"])
def login():
    if flask.request.method == "GET":
        if sessionCheck(loginCheck=True):
            return flask.redirect(flask.url_for("board"))
        
        if "msg" in flask.request.args:
            msg = flask.request.args["msg"]
        else:
            msg = "false"

        return flask.render_template("login.html", msg=msg)
    else:
        if sessionCheck():
            return flask.redirect(flask.url_for("board"))

        if not checkUserIDPW(flask.request.form["userid"], flask.request.form["userpw"]):
            return flask.render_template("login.html", msg="invalid userid or userpw")
        

        queryResult = db.doLogin({
            'userid':flask.request.form["userid"], 
            'userpw':hashlib.sha256(flask.request.form["userpw"].encode()).hexdigest()
        })

        if "userid" in queryResult:
            flask.session["userid"] = queryResult["userid"]
            flask.session["isLogin"] = True
            
            resp = flask.make_response(flask.redirect(flask.url_for("board")))
            resp.set_cookie('userid', flask.session["userid"])
            return resp
        else:
            return flask.render_template("login.html", msg=queryResult)

    
@app.route("/register", methods=["GET","POST"])
def register():
    if flask.request.method == "GET":
        if sessionCheck(loginCheck=True):
            return flask.redirect(flask.url_for("board"))
        
        if "msg" in flask.request.args:
            msg = flask.request.args["msg"]
        else:
            msg = "false"

        return flask.render_template("register.html", msg=msg)
    else:
        if sessionCheck():
            return flask.redirect(flask.url_for("board"))

        if not checkUserIDPW(flask.request.form["userid"], flask.request.form["userpw"]):
            return flask.render_template("register.html", msg="invalid userid or userpw")

        resp = db.doRegister({
            'userid': flask.request.form["userid"], 
            'userpw': hashlib.sha256(flask.request.form["userpw"].encode()).hexdigest()
        })

        return flask.render_template("login.html", msg=resp)


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=9090, debug=True)
    except Exception as ex:
        logging.info(str(ex))
        pass