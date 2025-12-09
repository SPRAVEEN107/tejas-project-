import os
import cv2
import insightface
from pymongo import MongoClient

# ---------------------------
# CONFIG
# ---------------------------
MONGO_URI = "mongodb+srv://praveen:yourstrongpassword123@attendancedb.tpwmjgs.mongodb.net/?appName=AttendanceDB"
IMAGES_DIR = "images"       # folder containing student images
CTX_ID = -1                 # -1 = CPU, 0 = GPU if available

# ---------------------------
# LOAD ARC FACE MODEL
# ---------------------------
print("Loading ArcFace model (buffalo_l)...")
model = insightface.app.FaceAnalysis(name="buffalo_l")
model.prepare(ctx_id=CTX_ID, det_size=(640, 640))


# ---------------------------
# EXTRACT ROLL & NAME
# Example: 03_praveen.jpg → roll=03, name=praveen
# ---------------------------
def extract_info(filename):
    base = os.path.splitext(filename)[0]
    parts = base.split("_")

    if len(parts) < 2 or not parts[0].isdigit():
        return None, None

    roll = parts[0]
    name = "_".join(parts[1:])
    return roll, name


# ---------------------------
# MAIN ENCODING FUNCTION
# ---------------------------
def create_arcface_encodings():
    client = MongoClient(MONGO_URI)
    db = client["AttendanceDB"]
    students_col = db["students"]

    for fname in os.listdir(IMAGES_DIR):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        roll, name = extract_info(fname)
        if roll is None:
            print("Skipping invalid filename:", fname)
            continue

        img_path = os.path.join(IMAGES_DIR, fname)
        img = cv2.imread(img_path)

        faces = model.get(img)

        if len(faces) == 0:
            print("❌ No face detected in:", fname)
            continue

        # Get ArcFace 512-D embedding
        embedding = faces[0].embedding.astype(float).tolist()

        # Prepare DB document
        student_doc = {
            "rollNo": roll,
            "name": name,
            "face_encoding": embedding,
            "model": "arcface",
            "image_files": [fname]
        }

        # Insert or update
        students_col.update_one(
            {"rollNo": roll},
            {"$set": student_doc},
            upsert=True
        )

        print(f"✔ Saved ArcFace encoding for {roll} ({name})")

    print("\nDONE: All ArcFace encodings stored successfully.")


# ---------------------------
# RUN SCRIPT
# ---------------------------
if __name__ == "__main__":
    create_arcface_encodings()
