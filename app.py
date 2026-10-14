import os
from flask import send_from_directory
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)
from werkzeug.utils import secure_filename
from sqlalchemy import func
from models import db, Farmer, Crop, Admin, Contact
# ---------------- AI ---------------- #

# ---------------- APP CONFIG ---------------- #
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db_path = os.path.join(BASE_DIR, "database", "agriculture.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "smart_agriculture_secret"
db.init_app(app)
# ============================================================
# HOME
# ============================================================
@app.route("/")
def home():

    total_farmers = Farmer.query.count()
    total_crops = Crop.query.count()
    total_land = db.session.query(func.sum(Farmer.land)).scalar() or 0

    crop_data = db.session.query(
        Crop.crop_name,
        func.count(Crop.id)
    ).group_by(Crop.crop_name).all()

    crop_labels = [item[0] for item in crop_data]
    crop_counts = [item[1] for item in crop_data]

    village_data = db.session.query(
        Farmer.village,
        func.count(Farmer.id)
    ).group_by(Farmer.village).all()

    village_labels = [item[0] for item in village_data]
    village_counts = [item[1] for item in village_data]
    return render_template(
        "index.html",
        total_farmers=total_farmers,
        total_crops=total_crops,
        total_land=round(total_land, 2),
        crop_labels=crop_labels,
        crop_counts=crop_counts,
        village_labels=village_labels,
        village_counts=village_counts
    )


#----------------------NEWS---------------------#
@app.route("/news")
def news():

    API_KEY = "760d8ed193423fd877e71eec21eff9ec"

    url = "https://gnews.io/api/v4/search"

    params = {
        "q": "agriculture farming crops",
        "country": "in",
        "lang": "en",
        "max": 12,
        "apikey": API_KEY
    }

    articles = []

    try:
        response = requests.get(url, params=params)
        print("STATUS:", response.status_code)
        print("DATA:", response.text[:500])


        data = response.json()

        for item in data.get("articles", []):

            articles.append({
                "title": item.get("title"),
                "description": item.get("description"),
                "urlToImage": item.get("image"),
                "url": item.get("url")
            })

        print("NEWS COUNT:", len(articles))

    except Exception as e:
        print(e)


    return render_template(
        "news.html",
        articles=articles
    )
# ============================================================
# DASHBOARD
# ============================================================
@app.route("/dashboard")

def dashboard():

    farmer_count = Farmer.query.count()
    crop_count = Crop.query.count()
    contact_count = Contact.query.count()
    admin_count = Admin.query.count()

    recent_farmers = Farmer.query.order_by(Farmer.id.desc()).limit(5).all()

    recent_contacts = Contact.query.order_by(Contact.id.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        farmer_count=farmer_count,
        crop_count=crop_count,
        contact_count=contact_count,
        admin_count=admin_count,
        recent_farmers=recent_farmers,
        recent_contacts=recent_contacts
    )
# ============================================================
# ADMIN LOGIN
# ============================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "admin123":
            session["admin"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid Username or Password"
    return render_template(
        "login.html",
        error=error
    )
# ============================================================
# LOGOUT
# ============================================================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(
        url_for("login")
    )
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# FARMER MANAGEMENT
# ============================================================

@app.route("/farmers")
@login_required
def farmers():

    search = request.args.get("search", "").strip()

    if search:

        all_farmers = Farmer.query.filter(
            Farmer.name.ilike(f"%{search}%")
        ).all()

    else:

        all_farmers = Farmer.query.all()

    return render_template(
        "farmers.html",
        farmers=all_farmers,
        search=search
    )


@app.route("/add_farmer", methods=["GET", "POST"])
@login_required
def add_farmer():

    if request.method == "POST":

        farmer = Farmer(

            name=request.form["name"],

            village=request.form["village"],

            mobile=request.form["mobile"],

            land=float(request.form["land"])

        )

        db.session.add(farmer)

        db.session.commit()
        flash("Farmer added successfully!", "success")

        return redirect(url_for("farmers"))

    return render_template("add_farmer.html")


@app.route("/edit_farmer/<int:id>", methods=["GET", "POST"])
@login_required
def edit_farmer(id):

    farmer = Farmer.query.get_or_404(id)

    if request.method == "POST":

        farmer.name = request.form["name"]

        farmer.village = request.form["village"]

        farmer.mobile = request.form["mobile"]

        farmer.land = float(request.form["land"])

        db.session.commit()

        return redirect(url_for("farmers"))

    return render_template(
        "add_farmer.html",
        farmer=farmer
    )


@app.route("/delete_farmer/<int:id>")
@login_required
def delete_farmer(id):

    farmer = Farmer.query.get_or_404(id)

    # Pehle us farmer ke saare crops delete karo
    Crop.query.filter_by(farmer_id=id).delete()

    # Ab farmer delete karo
    db.session.delete(farmer)

    db.session.commit()
    flash("Farmer deleted successfully!", "success")


    return redirect(url_for("farmers"))
@app.route("/farmer/<int:id>")
def farmer_details(id):

    farmer = Farmer.query.get_or_404(id)

    return render_template(
        "farmer_details.html",
        farmer=farmer
    )


# ============================================================
# CROP MANAGEMENT
# ============================================================

@app.route("/crops")
@login_required
def crops():

    all_crops = Crop.query.all()

    return render_template(
        "crops.html",
        crops=all_crops
    )


@app.route("/add_crop", methods=["GET", "POST"])
@login_required
def add_crop():

    farmers = Farmer.query.all()

    if request.method == "POST":

        crop = Crop(

            farmer_id=int(request.form["farmer_id"]),

            crop_name=request.form["crop_name"],

            season=request.form["season"],

            area=float(request.form["area"])

        )

        db.session.add(crop)

        db.session.commit()
        flash("Crop added successfully!", "success")


        return redirect(url_for("crops"))

    return render_template(
        "add_crop.html",
        farmers=farmers
    )


# ============================================================
# FERTILIZER RECOMMENDATION
# ============================================================

@app.route("/fertilizer", methods=["GET", "POST"])
def fertilizer():

    recommendation = None

    if request.method == "POST":

        crop = request.form["crop"]
        soil = request.form["soil"]

        if crop == "Rice":
            recommendation = "Urea + Potash"

        elif crop == "Wheat":
            recommendation = "Urea + DAP"

        elif crop == "Cotton":
            recommendation = "NPK (20:20:20)"

        elif crop == "Maize":
            recommendation = "Urea + Compost"

        else:
            recommendation = "No recommendation available."

    return render_template(
        "fertilizer.html",
        recommendation=recommendation
    )
# ============================================================
# WEATHER
# ============================================================

@app.route("/weather", methods=["GET", "POST"])
def weather():

    weather = None

    error = None

    if request.method == "POST":

        city = request.form["city"].strip()

        API_KEY = "1db5ab746858c2f03e834923963bb336"

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={API_KEY}&units=metric"
        )

        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()

            weather = {

                "city": data["name"],

                "temperature": data["main"]["temp"],

                "humidity": data["main"]["humidity"],

                "wind": data["wind"]["speed"],

                "condition": data["weather"][0]["main"]

            }

        else:

            error = "City not found."

    return render_template(
        "weather.html",
        weather=weather,
        error=error
    )
# ============================================================
# CROP RECOMMENDATION
# ============================================================
@app.route("/crop_recommendation", methods=["GET", "POST"])
def crop_recommendation():
    crop = None

    if request.method == "POST":

        soil = request.form["soil"]
        season = request.form["season"]
        ph = float(request.form["ph"])

        if soil == "Loamy" and season == "Kharif" and 6 <= ph <= 7:
            crop = "Rice"

        elif soil == "Black Soil" and season == "Kharif":
            crop = "Cotton"

        elif soil == "Clay" and season == "Rabi":
            crop = "Wheat"

        elif soil == "Sandy" and season == "Rabi":
            crop = "Groundnut"

        else:
            crop = "Maize"

    return render_template(
        "crop_recommendation.html",
        crop=crop
    )
# ============================================================
# IRRIGATION CALCULATOR
# ============================================================
@app.route("/irrigation", methods=["GET", "POST"])
def irrigation():
    result = None
    if request.method == "POST":
        crop = request.form["crop"]
        area = float(request.form["area"])
        water_per_acre = {
            "Rice": 12000,
            "Wheat": 5000,
            "Cotton": 7000,
            "Maize": 6000,
            "Groundnut": 4500
        }
        water = water_per_acre.get(crop, 5000) * area
        result = {
            "crop": crop,
            "area": area,
            "water": water
        }
    return render_template(
        "irrigation.html",
        result=result
    )
# ============================================================
# REPORTS
# ============================================================
@app.route("/reports")
@login_required
def reports():
    total_farmers = Farmer.query.count()
    total_crops = Crop.query.count()
    total_land = db.session.query(
        func.sum(Farmer.land)
    ).scalar() or 0
    farmers = Farmer.query.all()
    crops = Crop.query.all()
    return render_template(
        "reports.html",
        total_farmers=total_farmers,
        total_crops=total_crops,
        total_land=round(total_land, 2),
        farmers=farmers,
        crops=crops
    )
# ============================================================
# MANUAL DISEASE DIAGNOSIS
# ============================================================
@app.route("/disease", methods=["GET", "POST"])
def disease():
    result = None
    if request.method == "POST":
        crop = request.form["crop"]
        symptom = request.form["symptom"]
        diseases = {
            ("Rice", "Yellow Leaves"): {
                "disease": "Nitrogen Deficiency",
                "treatment": "Apply Urea fertilizer.",
                "prevention": "Maintain proper nutrient management."
            },
            ("Rice", "Brown Spots"): {
                "disease": "Brown Spot Disease",
                "treatment": "Spray Mancozeb fungicide.",
                "prevention": "Use disease-resistant varieties."
            },
            ("Wheat", "Yellow Leaves"): {
                "disease": "Yellow Rust",
                "treatment": "Apply Propiconazole fungicide.",
                "prevention": "Grow resistant wheat varieties."
            },
            ("Cotton", "Leaf Curl"): {
                "disease": "Leaf Curl Virus",
                "treatment": "Control whiteflies using recommended insecticides.",
                "prevention": "Use virus-free seeds."
            },
            ("Maize", "Brown Spots"): {
                "disease": "Leaf Blight",
                "treatment": "Spray Azoxystrobin fungicide.",
                "prevention": "Rotate crops regularly."
            }
        }
        result = diseases.get(
            (crop, symptom),
            {
                "disease": "No disease detected",
                "treatment": "No treatment required.",
                "prevention": "Keep monitoring the crop."
            }
        )
    return render_template(
        "disease.html",
        result=result
    )
# ============================================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )
# ----------------SOIL ANALYSIS-------------#
@app.route("/soil", methods=["GET", "POST"])
def soil():

    result = None

    if request.method == "POST":

        soil_type = request.form["soil_type"]
        ph = float(request.form["ph"])
        nitrogen = int(request.form["nitrogen"])
        phosphorus = int(request.form["phosphorus"])
        potassium = int(request.form["potassium"])

        # Soil Health
        if 6 <= ph <= 7.5 and nitrogen >= 50 and phosphorus >= 40 and potassium >= 40:
            health = "Soil is Healthy"
        else:
            health = "Soil Needs Improvement"

        # pH Status
        if ph < 6.5:
            ph_status = "Acidic Soil"
        elif ph <= 7.5:
            ph_status = "Neutral Soil"
        else:
            ph_status = "Alkaline Soil"

        # Fertilizer Recommendation
        recommendation = []

        if nitrogen < 50:
            recommendation.append("Apply Urea Fertilizer.")

        if phosphorus < 40:
            recommendation.append("Apply DAP Fertilizer.")

        if potassium < 40:
            recommendation.append("Apply MOP Fertilizer.")

        if not recommendation:
            recommendation.append("No fertilizer required.")

        result = {
            "soil_type": soil_type,
            "health": health,
            "ph_status": ph_status,
            "recommendation": recommendation
        }

    return render_template(
        "soil.html",
        result=result
    )
# ---------------------CONTACT-------------------------#
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        new_message = Contact(
            name=request.form["name"],
            email=request.form["email"],
            subject=request.form["subject"],
            message=request.form["message"]
        )
        db.session.add(new_message)
        db.session.commit()
        flash("Your message has been sent successfully!", "success")
        return render_template(
            "contact.html",
            success="Your message has been sent successfully."
        )
    return render_template("contact.html")
# ----------- 404-error -----------#
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
# --------------MAIN--------------#
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )