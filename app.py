from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3, os, time

app = Flask(__name__)
app.secret_key = "niranjan123"
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs("uploads", exist_ok=True)

def db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ===== DATABASE =====
conn=db()

conn.execute("""
CREATE TABLE IF NOT EXISTS followers(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
insta TEXT,
link TEXT,
img TEXT,
day TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS settings(
id INTEGER PRIMARY KEY,
current_day TEXT
)
""")

conn.execute("INSERT OR IGNORE INTO settings(id,current_day) VALUES(1,'Day 1')")
conn.commit()
conn.close()

# ===== HOME PAGE =====
@app.route("/")
def home():
    conn=db()
    followers=conn.execute("SELECT * FROM followers ORDER BY id DESC").fetchall()
    day=conn.execute("SELECT current_day FROM settings WHERE id=1").fetchone()[0]
    conn.close()
    return render_template("index.html", followers=followers, day=day)

# ===== LOGIN =====
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form["password"]=="niranjan123":
            session["admin"]=True
            return redirect("/admin")
    return render_template("login.html")

# ===== ADMIN PAGE =====
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "admin" not in session:
        return redirect("/login")

    if request.method=="POST":

        # Update current day
        if "setday" in request.form:
            conn=db()
            conn.execute("UPDATE settings SET current_day=?", (request.form["currentday"],))
            conn.commit()
            conn.close()
            return redirect("/admin")

        # Add follower
        file=request.files["img"]
        filename=str(time.time())+file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn=db()
        conn.execute(
            "INSERT INTO followers(name,insta,link,img,day) VALUES(?,?,?,?,?)",
            (
                request.form["name"],
                request.form["insta"],
                request.form["link"],
                filename,
                request.form["day"]
            )
        )
        conn.commit()
        conn.close()
        return redirect("/admin")

    conn=db()
    followers=conn.execute("SELECT * FROM followers").fetchall()
    day=conn.execute("SELECT current_day FROM settings WHERE id=1").fetchone()[0]
    conn.close()
    return render_template("admin.html", followers=followers, day=day)

@app.route("/delete/<int:id>")
def delete(id):
    conn=db()
    conn.execute("DELETE FROM followers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

app.run(debug=True)
