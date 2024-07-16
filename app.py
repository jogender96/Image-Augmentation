from flask import Flask, request, render_template, send_file, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os
from PIL import Image
import albumentations as A
import cv2
import zipfile

app = Flask(__name__)

# Configure image uploads
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
configure_uploads(app, photos)

def augment_image(image_path):
    image = cv2.imread(image_path)
    transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.Rotate(limit=30, p=0.5),
        A.Zoom(scale=(0.9, 1.1), p=0.5)
    ])
    augmented_images = [transform(image=image)['image'] for _ in range(5)]
    return augmented_images

def save_images(images, original_name):
    filenames = []
    base, ext = os.path.splitext(original_name)
    for i, img in enumerate(images):
        filename = f"{base}_aug_{i}{ext}"
        cv2.imwrite(os.path.join('uploads', filename), img)
        filenames.append(filename)
    return filenames

def create_zip(file_list):
    zip_filename = 'augmented_images.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in file_list:
            zipf.write(os.path.join('uploads', file), file)
    return zip_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'photo' in request.files:
        filenames = []
        for file in request.files.getlist('photo'):
            filename = photos.save(file)
            augmented_images = augment_image(os.path.join('uploads', filename))
            augmented_filenames = save_images(augmented_images, filename)
            filenames.extend(augmented_filenames)
        zip_filename = create_zip(filenames)
        return send_file(zip_filename, as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
