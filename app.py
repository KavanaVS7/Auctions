from flask import Flask,render_template,request,jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
#import bcrypt
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Corrected MongoDB URI
mongo_uri = "mongodb+srv://varsha:%40Hello12345%23@cluster0.s14ztnw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)

db = client["auction_platform"] 
 # Use your actual database name
users =db["USERS"]
users_collection = db["USERS"]
temp_users = db["TEMP_USERS"]
def send_otp_email(email,otp):
    sender = "kavanav1111@gmail.com"
    password = "mlil angg spmn hbyk"
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = email
    msg["Subject"] = "Your OTP Code"
    msg.attach(MIMEText(f"Your OTP is {otp}","plain"))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender,password)
        server.send_message(msg)





@app.route("/users")
def get_users():
    users = list(users_collection.find({}, {"_id": 0}))  # This hides _id
    return jsonify(users)
@app.route('/help')
def help():
    return render_template('help.html')
@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/auctions')
def auctions():
    return render_template('auctions.html')
@app.route('/categories')
def categories():
    return render_template('categories.html')
@app.route("/login",methods=["POST"])
def login():
    #name = data.get('name')
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error":"Email and password are required"}),400
    
    user = users.find_one({"email":email})
    if not user:
        return jsonify({"error":"User not found"}),404
    if user["password"]!=password:
        return jsonify({"error":"Incorrect password"}),401
    return jsonify({"message":"Login successful"})
   # return render_template('help.html')
@app.route("/signup",methods=["POST"])
def signup():
    data = request.get_json()
    name= data.get("name")
    email= data.get("email")
    password= data.get("password")
    confirm_password= data.get("confirm_password")
    if password!=confirm_password:
        return jsonify({"error":"Passwords do not match"}),400
    if users.find_one({"email":email}):
        return jsonify({"error":"Email already registered"}),400
    otp=str(random.randint(100000,999999))
    temp_users.insert_one({"name":name,"email":email,"password":password,"otp":otp})
    send_otp_email(email,otp)
    return jsonify({"message:":"OTP sent to email"})
@app.route("/verify_otp",methods=["POST"])
def verify_otp():
    data = request.get_json()
    email=data.get("email")
    otp=data.get("otp")
    temp_user=temp_users.find_one({"email":email,"otp":otp})
    if not temp_user:
        return jsonify({"error":"Invalid OTP or Email"}),400
    users.insert_one({"name":temp_user["name"],"email":temp_user["email"],"password":temp_user["password"]})
    temp_users.delete_one({"_id":temp_user["_id"]})
    return jsonify({"message":"Account verified and created"})
@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = users.find_one({"email": email})
    if not user:
        return jsonify({"error": "Email not found"}), 404

    otp = str(random.randint(100000, 999999))
    
    # Store the OTP for this user
    temp_users.update_one(
        {"email": email},
        {"$set": {"otp": otp}},
        upsert=True
    )

    send_otp_email(email, otp)
    return jsonify({"message": "OTP sent to email"}), 200

@app.route("/reset_password", methods=["POST"])
def reset_password():

    data = request.get_json()
    email = data.get("email")
    otp = str(data.get("otp"))  # Ensure it's a string
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Make sure OTP matches
    temp_user = temp_users.find_one({"email": email, "otp": otp})
    if not temp_user:
        return jsonify({"error": "Invalid OTP or email"}), 400

    # Update user's password
    result = users.update_one(
        {"email": email},
        {"$set": {"password": new_password}}
    )

    #if result.matched_count == 0:
       # return jsonify({"error": "User not found"}), 404

    # Delete OTP record
    temp_users.delete_one({"email": email})

    return jsonify({"message": "Password reset successful"}), 200


if __name__ == "__main__":
    app.run(debug=True)
