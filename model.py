from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import UserMixin

db=SQLAlchemy()



class Userinfo(db.Model,UserMixin):
    id=db.Column(db.Integer(),primary_key=True)
    First_name=db.Column(db.String(255),nullable=False)
    Last_name=db.Column(db.String(255),nullable=False)
    Username=db.Column(db.String(40),nullable=False,unique=True)
    Password=db.Column(db.String(40),nullable=False)
    Mobile_no=db.Column(db.Integer(),nullable=False,unique=True)
    Normaluser=db.Column(db.Boolean,default=True,nullable=False)
    Creator=db.Column(db.Boolean,default=False,nullable=False)
    LSong=db.relationship('Songs',backref='userinfo')
    LAlbums=db.relationship('Album',backref='userinfo')
    LPlaylist=db.relationship('Playlist',backref='userinfo')
    #creating many to one relationship between userinfo and rating
    Ratings=db.relationship('Rating',backref='userinfo')
    def get_id(self):
        return f"user_{self.id}"
    
class Album(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    Name=db.Column(db.String(255),nullable=False)
    Genre=db.Column(db.String(40),nullable=True)
    Artist=db.Column(db.String(255),nullable=True)
    songs=db.relationship('Songs',backref='album')
    adminflagalbum=db.Column(db.Boolean,default=False,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('userinfo.id'),nullable=False)

class Songs(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    Name=db.Column(db.String(255),nullable=False)
    Lyrics=db.Column(db.String(255),nullable=False)
    Duration=db.Column(db.String(255),nullable=False)
    Artist=db.Column(db.String(255),nullable=False)
    Date_created=db.Column(db.Date,nullable=False)
    Genre=db.Column(db.String(255),nullable=False)
    album_id=db.Column(db.Integer,db.ForeignKey('album.id'),nullable=True)
    user_id=db.Column(db.Integer,db.ForeignKey('userinfo.id'),nullable=False)
    #flag a song
    adminflagsong=db.Column(db.Boolean,default=False,nullable=False)
    #creating many to many relationship between Songs and rating
    S_playlist=db.relationship('Playlist',secondary='song_association_playlist',backref='songs')
    Ratings=db.relationship('Rating',backref='songs')



class Playlist(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    Name=db.Column(db.String(255),nullable=False)
    user_id=db.Column(db.Integer(),db.ForeignKey('userinfo.id'),nullable=False)
    

class Song_association_playlist(db.Model):
    song_id=db.Column(db.Integer(),db.ForeignKey('songs.id'),primary_key=True)
    playlist_id=db.Column(db.Integer(),db.ForeignKey('playlist.id'),primary_key=True)

class Rating(db.Model):
    # id=db.Column(db.Integer(),primary_key=True)
    rating_value=db.Column(db.Integer(),nullable=True)
    #creating many to one  relationship between userinfo and rating
    user_id=db.Column(db.Integer(),db.ForeignKey('userinfo.id'),nullable=True,primary_key=True)
    #creating one to many relationship between songs and rating
    song_id=db.Column(db.Integer(),db.ForeignKey('songs.id'),nullable=True,primary_key=True)

class Adminauth(db.Model,UserMixin):
    id=db.Column(db.Integer(),primary_key=True)
    admin_user_name=db.Column(db.String(40),nullable=False,unique=True)
    admin_password=db.Column(db.String(40),nullable=False)
    def get_id(self):
        return f"admin_{self.id}"