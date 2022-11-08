import os
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:eva320281.@localhost:5432'
db = SQLAlchemy(app)
ma = Marshmallow()


class VideoModel(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(500))
    name = db.Column(db.String(80))
    actor = db.Column(db.String(200))
    length = db.Column(db.String(200))
    genre = db.Column(db.String(80))
    review_rating = db.Column(db.Float)

    def __init__(self, video_url, name, actor, length, genre, review_rating):
        self.video_url = video_url
        self.name = name
        self.actor = actor
        self.length = length
        self.genre = genre
        self.review_rating = review_rating


class VideoSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String(required=True)
    video_url = fields.String(required=True)
    actor = fields.String(required=False)
    length = fields.String(required=True)
    genre = fields.String(required=False)
    review_rating = fields.Float(required=False)


videos_schema = VideoSchema(many=True)
video_schema = VideoSchema()

with app.app_context():
    db.create_all()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# add a video POST /video
@app.route('/video', methods=['POST'])
def add_video():
    json_data = request.get_json(force=True)
    if not json_data:
        return {'message': "Input is not valid."}, 400
    video = VideoModel(
        name=json_data['name'],
        video_url=json_data['video_url'],
        actor=json_data['actor'],
        length=json_data['length'],
        genre=json_data['genre'],
        review_rating=json_data['review_rating']
    )
    db.session.add(video)
    db.session.commit()
    result = video_schema.dump(video)
    return {"status": 'success',
            'data': result
            }, 201


# list all videos GET /video
@app.route('/video', methods=['GET'])
def list_all_videos():
    videos = VideoModel.query.all()
    videos = video_schema.dump(videos)
    if not videos:
        return {'status': 'not found'}, 404
    return {'status': 'success',
            'data': videos}, 200


# show video details GET /video/:id
@app.route('/video/<int:id>', methods=['GET'])
def search_video_by_id(id):
    video = VideoModel.query.get(id)
    print(video)
    video = video_schema.dump(video)
    if not video:
        return {'status': 'not found'}, 404
    return {'status': 'success',
            'data': video}, 200


# delete video DELETE/video/:id
@app.route('/video/<int:id>', methods=["DELETE"])
def delete_video(id):
    # video = VideoModel.query.get(id)
    # owner_id = video.owner_id
    video = VideoModel.query.filter_by(id=id).delete()
    db.session.commit()
    result = video_schema.dump(video)
    return {"status": 'success', 'data': result}, 204


# update video detail PUT/video/:id
@app.route('/video/<int:id>', methods=["PUT"])
def update_video(id):
    json_data = request.get_json(force=True)
    if not json_data:
        return {'message': "Input is not valid."}, 400
    video = VideoModel.query.get(id)
    if not video:
        return {'message':
                    'Video does not exist'}, 400
    if 'name' in json_data:
        video.name = json_data['name']
    if 'actor' in json_data:
        video.actor = json_data['actor']
    if 'length' in json_data:
        video.length = json_data['length']
    if 'genre' in json_data:
        video.genre = json_data['genre']
    if 'review_rating' in json_data:
        video.review_rating = json_data['review_rating']
    db.session.commit()
    result = video_schema.dump(video)
    return {"status": 'success',
            'data': result}, 201


if __name__ == "__main__":
    # port = int(os.environ.get('PORT', 80))
    # localhost port
    port = int(os.environ.get('PORT', 5432))
    app.run(debug=True, host='0.0.0.0', port=port)
