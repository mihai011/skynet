from fastapi import FastAPI, File, UploadFile,Form
import cv2
import numpy as np

app = FastAPI()


@app.post("/upload")
async def upload_image(stream_name: str = Form(...), image: UploadFile = File(...), ):
    # Read the uploaded file
    image_bytes = await image.read()
    
    # Convert the file to a NumPy array
    image_np = np.frombuffer(image_bytes, np.uint8)
    
    # Decode the image
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    
    # Display the image using OpenCV
    cv2.namedWindow(stream_name, cv2.WINDOW_NORMAL)
    cv2.imshow(stream_name, image)
    cv2.waitKey(1)
    # cv2.destroyAllWindows()

    return 1