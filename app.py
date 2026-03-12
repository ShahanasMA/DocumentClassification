from flask import Flask,render_template,request,redirect,session,send_from_directory
import sqlite3,joblib,os
from datetime import datetime
from users import USERS
from werkzeug.security import check_password_hash
from PyPDF2 import PdfReader
from pptx import Presentation

app=Flask(__name__)
app.secret_key="secret"

model=joblib.load("document_classifier.pkl")

BASE="documents"
os.makedirs(BASE,exist_ok=True)

def extract(file,name):

    if name.endswith(".txt"):
        return file.read().decode()

    if name.endswith(".pdf"):
        r=PdfReader(file)
        return "".join(p.extract_text() or "" for p in r.pages)

    if name.endswith(".pptx"):
        prs=Presentation(file)
        text=""
        for s in prs.slides:
            for sh in s.shapes:
                if hasattr(sh,"text"):
                    text+=sh.text
        return text

    return ""

@app.route("/login",methods=["GET","POST"])
def login():

    error=""

    if request.method=="POST":

        u=request.form["username"]
        p=request.form["password"]

        if u in USERS and check_password_hash(USERS[u]["password"],p):

            session["user"]=u
            session["role"]=USERS[u]["role"]

            return redirect("/")

        error="Invalid login"

    return render_template("login.html",error=error)

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("upload.html")

@app.route("/",methods=["POST"])
def upload():

    file=request.files["file"]
    name=file.filename

    text=extract(file,name)

    cat=model.predict([text])[0]
    conf=max(model.predict_proba([text])[0])

    percent=int(conf*100)

    color="green" if conf>=0.7 else "yellow" if conf>=0.4 else "red"

    path=os.path.join(BASE,cat)
    os.makedirs(path,exist_ok=True)

    file.seek(0)

    with open(os.path.join(path,name),"wb") as f:
        f.write(file.read())

    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    cur.execute("""
    INSERT INTO documents(filename,category,confidence,preview,uploaded_by,upload_time,status)
    VALUES(?,?,?,?,?,?,?)
    """,(name,cat,conf,text[:150],session["user"],datetime.now(),"classified"))

    conn.commit()
    conn.close()

    return render_template("upload.html",
                           category=cat,
                           percent=percent,
                           color=color,
                           filename=name)

@app.route("/categories")
def categories():

    cats=os.listdir(BASE)

    return render_template("categories.html",cats=cats)

@app.route("/category/<cat>")
def category(cat):

    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    cur.execute("SELECT filename,confidence,preview,upload_time FROM documents WHERE category=?",(cat,))

    rows=cur.fetchall()

    files=[]

    for r in rows:

        percent=int(r[1]*100)
        color="green" if r[1]>=0.7 else "yellow" if r[1]>=0.4 else "red"

        files.append({
            "filename":r[0],
            "percent":percent,
            "color":color,
            "preview":r[2],
            "time":r[3]
        })

    return render_template("category_view.html",files=files,category=cat)

@app.route("/download/<cat>/<file>")
def download(cat,file):

    return send_from_directory(os.path.join(BASE,cat),file,as_attachment=True)

@app.route("/request_review",methods=["POST"])
def review():

    file=request.form["filename"]
    msg=request.form["message"]

    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    cur.execute("SELECT id FROM documents WHERE filename=?",(file,))
    doc=cur.fetchone()[0]

    cur.execute("INSERT INTO review_requests(document_id,message,status) VALUES(?,?,?)",(doc,msg,"pending"))

    conn.commit()
    conn.close()

    return redirect("/categories")

@app.route("/admin")
def admin():

    if session.get("role")!="admin":
        return "Unauthorized"

    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    cur.execute("""
    SELECT d.id,d.filename,d.category,r.message
    FROM review_requests r
    JOIN documents d ON d.id=r.document_id
    WHERE r.status='pending'
    """)

    rows=cur.fetchall()

    data=[]

    for r in rows:
        data.append({
            "id":r[0],
            "filename":r[1],
            "category":r[2],
            "message":r[3]
        })

    return render_template("admin.html",data=data)

@app.route("/admin/update",methods=["POST"])
def update():

    doc=request.form["doc_id"]
    new=request.form["new_category"]

    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    cur.execute("SELECT filename,category FROM documents WHERE id=?",(doc,))
    f=cur.fetchone()

    old_path=os.path.join(BASE,f[1],f[0])
    new_path=os.path.join(BASE,new)

    os.makedirs(new_path,exist_ok=True)

    os.rename(old_path,os.path.join(new_path,f[0]))

    cur.execute("UPDATE documents SET category=?,status='verified' WHERE id=?",(new,doc))
    cur.execute("UPDATE review_requests SET status='resolved' WHERE document_id=?",(doc,))

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)
