from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect, current_app, make_response, Response
)
from app.db import get_db

import os
import time

bp = Blueprint('slideshow', __name__, url_prefix='/')

def gen():
    i = 0

    while True:
        
        images = get_all_images()
        image_name = images[i]
        im = open('app/static/images/slide/' + image_name, 'rb').read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + im + b'\r\n')
        i += 1
        if i >= len(images):
            i = 0
        time.sleep(20)

def get_all_images():
    image_folder = 'app/static/images/slide'
    images = [img for img in os.listdir(image_folder)
              if img.endswith(".jpg") or
              img.endswith(".jpeg") or
              img.endswith(".png")]
    return images

@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@bp.route('/slideshow')
def slideshow():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')