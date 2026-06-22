from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, cv2, json, uuid, hashlib
from datetime import datetime
from size_advisor import suggest_size, get_size_chart, get_body_type

app = Flask(__name__)
app.secret_key = "fitvision-secret-2025"

UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"
DATA_FILE      = "data/users.json"

for d in [UPLOAD_FOLDER, RESULT_FOLDER, "data"]:
    os.makedirs(d, exist_ok=True)

# ── Helpers ──────────────────────────────────────────────────
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return load_users().get(uid)

# ── Auth ─────────────────────────────────────────────────────
@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    pw    = data.get("password", "")
    users = load_users()
    for uid, u in users.items():
        if u["email"] == email and u["password"] == hash_pw(pw):
            session["user_id"] = uid
            return jsonify({"ok": True})
    return jsonify({"error": "Invalid email or password"}), 401

@app.route("/register", methods=["POST"])
def register():
    data  = request.get_json()
    name  = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    pw    = data.get("password", "")
    if not name or not email or not pw:
        return jsonify({"error": "All fields are required"}), 400
    users = load_users()
    for u in users.values():
        if u["email"] == email:
            return jsonify({"error": "Email already registered"}), 409
    uid = str(uuid.uuid4())
    users[uid] = {
        "id": uid, "name": name, "email": email,
        "password": hash_pw(pw),
        "avatar": name[0].upper(),
        "joined": datetime.now().strftime("%B %Y"),
        "history": [],
        "wishlist": [],
        "saved_sizes": {}
    }
    save_users(users)
    session["user_id"] = uid
    return jsonify({"ok": True})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── Pages ────────────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    u = current_user()
    if not u: return redirect(url_for("login"))
    return render_template("dashboard.html", user=u, active="dashboard")

@app.route("/tryon")
def tryon():
    u = current_user()
    if not u: return redirect(url_for("login"))
    return render_template("tryon.html", user=u, active="tryon")

@app.route("/history")
def history():
    u = current_user()
    if not u: return redirect(url_for("login"))
    return render_template("history.html", user=u, active="history")

@app.route("/profile")
def profile():
    u = current_user()
    if not u: return redirect(url_for("login"))
    return render_template("profile.html", user=u, active="profile")

# ── API ──────────────────────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
def predict():
    u = current_user()
    if not u:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        user_img  = request.files.get("user_image")
        cloth_img = request.files.get("cloth_image")
        if not user_img or not cloth_img:
            return jsonify({"error": "Both images are required."}), 400

        height      = float(request.form["height"])
        weight      = float(request.form["weight"])
        gender      = request.form.get("gender", "unisex")
        brand       = request.form.get("brand", "")
        garment_type= request.form.get("garment_type", "top")

        uid_img = str(uuid.uuid4())[:8]
        user_path  = os.path.join(UPLOAD_FOLDER, f"user_{uid_img}_{user_img.filename}")
        cloth_path = os.path.join(UPLOAD_FOLDER, f"cloth_{uid_img}_{cloth_img.filename}")
        user_img.save(user_path)
        cloth_img.save(cloth_path)

        img  = cv2.imread(user_path)
        cloth= cv2.imread(cloth_path)
        if img is None or cloth is None:
            return jsonify({"error": "Could not read images."}), 400

        h, w = img.shape[:2]

        # Position based on garment type
        if garment_type == "top":
            rw, rh = int(w*0.38), int(h*0.42)
            rx, ry = int(w*0.31), int(h*0.17)
        elif garment_type == "bottom":
            rw, rh = int(w*0.40), int(h*0.44)
            rx, ry = int(w*0.30), int(h*0.50)
        else:  # full
            rw, rh = int(w*0.44), int(h*0.70)
            rx, ry = int(w*0.28), int(h*0.14)

        cloth_r = cv2.resize(cloth, (rw, rh))
        roi = img[ry:ry+rh, rx:rx+rw]
        gray = cv2.cvtColor(cloth_r, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        mask_inv = cv2.bitwise_not(mask)
        bg  = cv2.bitwise_and(roi, roi, mask=mask_inv)
        fg  = cv2.bitwise_and(cloth_r, cloth_r, mask=mask)
        img[ry:ry+rh, rx:rx+rw] = cv2.add(bg, fg)

        result_name = f"result_{uid_img}.jpg"
        result_path = os.path.join(RESULT_FOLDER, result_name)
        cv2.imwrite(result_path, img)

        size       = suggest_size(height, weight, gender)
        body_type  = get_body_type(height, weight)
        size_chart = get_size_chart(gender)
        bmi        = round(weight / ((height/100)**2), 1)

        # Save to history
        entry = {
            "id": uid_img,
            "date": datetime.now().strftime("%d %b %Y, %H:%M"),
            "result_image": result_path,
            "cloth_image": cloth_path,
            "size": size,
            "bmi": bmi,
            "height": height,
            "weight": weight,
            "gender": gender,
            "brand": brand,
            "garment_type": garment_type,
            "body_type": body_type["label"]
        }
        users = load_users()
        users[u["id"]]["history"].insert(0, entry)
        users[u["id"]]["history"] = users[u["id"]]["history"][:20]  # keep last 20
        users[u["id"]]["saved_sizes"][brand or "General"] = size
        save_users(users)

        return jsonify({
            "result_image": result_path,
            "size": size, "bmi": bmi,
            "body_type": body_type,
            "size_chart": size_chart,
            "height": height, "weight": weight,
            "entry_id": uid_img
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/wishlist/add", methods=["POST"])
def wishlist_add():
    u = current_user()
    if not u: return jsonify({"error":"Unauthorized"}),401
    data = request.get_json()
    users = load_users()
    item = {
        "id": str(uuid.uuid4())[:8],
        "name": data.get("name",""),
        "brand": data.get("brand",""),
        "size": data.get("size",""),
        "price": data.get("price",""),
        "image": data.get("image",""),
        "added": datetime.now().strftime("%d %b %Y")
    }
    users[u["id"]]["wishlist"].insert(0, item)
    save_users(users)
    return jsonify({"ok": True, "item": item})

@app.route("/api/wishlist/remove", methods=["POST"])
def wishlist_remove():
    u = current_user()
    if not u: return jsonify({"error":"Unauthorized"}),401
    item_id = request.get_json().get("id")
    users = load_users()
    users[u["id"]]["wishlist"] = [w for w in users[u["id"]]["wishlist"] if w["id"] != item_id]
    save_users(users)
    return jsonify({"ok": True})

@app.route("/api/history/delete", methods=["POST"])
def history_delete():
    u = current_user()
    if not u: return jsonify({"error":"Unauthorized"}),401
    entry_id = request.get_json().get("id")
    users = load_users()
    users[u["id"]]["history"] = [h for h in users[u["id"]]["history"] if h["id"] != entry_id]
    save_users(users)
    return jsonify({"ok": True})

@app.route("/api/profile/update", methods=["POST"])
def profile_update():
    u = current_user()
    if not u: return jsonify({"error":"Unauthorized"}),401
    data = request.get_json()
    users = load_users()
    for k in ["name","email","phone","location","style_pref"]:
        if k in data:
            users[u["id"]][k] = data[k]
    save_users(users)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)