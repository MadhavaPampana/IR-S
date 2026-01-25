import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from deepface import DeepFace
import os
import shutil
import numpy as np
from scipy.spatial.distance import cosine

app = FastAPI()
MODEL = "Facenet512"

# Warmup
try:
    DeepFace.represent(img_path = np.zeros((500, 500, 3), dtype = np.uint8), model_name = MODEL,
                       enforce_detection = False)
except:
    pass


@app.post("/verify-selfie")
async def verify_selfie(file: UploadFile = File(...), student_folder_path: str = Form(...)):
    with open("temp.jpg", "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        # Get embedding of the selfie
        target_emb = DeepFace.represent("temp.jpg", model_name = MODEL, enforce_detection = True)[0]["embedding"]
        min_score = 1.0
        
        # Check against photos in student's folder
        if os.path.exists(student_folder_path):
            for img in os.listdir(student_folder_path):
                try:
                    ref_path = os.path.join(student_folder_path, img)
                    ref_emb = DeepFace.represent(ref_path, model_name = MODEL, enforce_detection = False)[0][
                        "embedding"]
                    
                    score = cosine(target_emb, ref_emb)
                    if score < min_score:
                        min_score = score
                except:
                    pass
        
        # --- THE FIX IS HERE ---
        # We explicitly convert the numpy result to a Python boolean
        is_match = bool(min_score < 0.4)
        
        return {"match": is_match}
    
    except Exception as e:
        print(f"Error verifying: {e}")
        return {"match": False}


@app.post("/process-class-photo")
async def process_class(file: UploadFile = File(...), class_folder_path: str = Form(...)):
    with open("temp_class.jpg", "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    found = []
    try:
        faces = DeepFace.extract_faces("temp_class.jpg", enforce_detection = False)
        known = {}
        
        # Load known embeddings from the class folder
        if os.path.exists(class_folder_path):
            for stu_dir in os.listdir(class_folder_path):  # e.g. "stu_1"
                path = os.path.join(class_folder_path, stu_dir)
                if os.path.isdir(path):
                    known[stu_dir] = []
                    for img in os.listdir(path)[:3]:
                        try:
                            emb = \
                            DeepFace.represent(os.path.join(path, img), model_name = MODEL, enforce_detection = False)[
                                0]["embedding"]
                            known[stu_dir].append(emb)
                        except:
                            pass
        
        for face_obj in faces:
            face_img = face_obj["face"]
            if face_img.max() <= 1: face_img = (face_img * 255).astype(np.uint8)
            face_img = face_img[:, :, ::-1]
            
            try:
                target_emb = DeepFace.represent(face_img, model_name = MODEL, enforce_detection = False)[0]["embedding"]
                best_score = 0.5
                best_stu = None
                
                for s_id, embs in known.items():
                    for ref in embs:
                        score = cosine(target_emb, ref)
                        if score < best_score:
                            best_score = score
                            best_stu = s_id
                
                if best_stu:
                    found.append(best_stu.replace("stu_", ""))
            except:
                pass
    except:
        pass
    return {"found": found}


if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 8001)