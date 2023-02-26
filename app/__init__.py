import os
from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        DATABASE_HOST=os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD=os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER=os.environ.get('FLASK_DATABASE_USER'),
        DATABASE=os.environ.get('FLASK_DATABASE'),
        UPLOAD_FOLDER = 'app/static/images/slide',
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    )

    

    from . import db
    db.init_app(app)

    from . import slideshow
    app.register_blueprint(slideshow.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
