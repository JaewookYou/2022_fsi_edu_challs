import flask
import logging, traceback
logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(level=logging.WARNING)

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
        query = f"select userid from chatdb.user where userid='{req['userid']}'"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        
        if result != ():
            return True
        else:
            return False

    def doLogin(self, req):
        req = self.safeQuery(req)
        query = f"select userid from fsi2022.users where userid='{req['userid']}' and userpw='{req['userpw']}'"
        logging.info(f"[+] query(login) - {query}")
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        logging.info(f"[+] result(login) - {query}")
        return result

    def doRegister(self, req):
        req = self.safeQuery(req)        
        if self.duplicatedCheck(req):
            return "[x] duplicated id"

        query = f"insert into fsi2022.users (userid, userpw) values('{req['userid']}', '{req['userpw']}')"
        logging.info(f"[+] query(register) - {query}")
        self.cursor.execute(query)
        self.conn.commit()
        
        if self.duplicatedCheck(req):
            return resp
        else:
            return False

db = mysqlapi()



def checkUserIDPW(userid, userpw):
    if re.search(r"[^\w]",userid) or len(userid) == 0 or len(userid) > 50 or len(userpw) == 0 or len(userpw) > 50:
        return False
    else:
        return True
        
def secureFileName(filename):
    # replace all regex 바꾸기
    filteringList = ["..","\\","\x00","'",'"']
    for filterChar in filteringList:
        filename = filename.replace(filterChar, "")
    return filename

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

    return flask.render_template("board.html")


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
        

        queryResult = db.doLoginQuery({
            'userid':flask.request.form["userid"], 
            'userpw':hashlib.sha256(flask.request.form["userpw"].encode()).hexdigest()
        })

        if "userid" in queryResult:
            flask.session["userid"] = queryResult["userid"]
            flask.session["isLogin"] = True
            
            resp = flask.make_response(flask.redirect(flask.url_for("board")))
            resp.set_cookie('userid', userid)
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

        resp = doRegisterQuery({
            'userid': flask.request.form["userid"], 
            'userpw': hashlib.sha256(flask.request.form["userpw"].encode()).hexdigest()
        })

        return flask.render_template("login.html", msg=resp)