
from enum import unique
from app import db
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import backref
from sqlalchemy import UniqueConstraint

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'
  __table_args__ = (UniqueConstraint('artist_id', 'start_time', name='unique_artistid_starttime'),)
  venue_id = db.Column(db.Integer, ForeignKey('venues.id'), primary_key=True)
  artist_id = db.Column(db.Integer, ForeignKey('artists.id'), primary_key=True)
  start_time  = db.Column(db.DateTime, server_default=db.func.now())

  venue = db.relationship("Venue", backref="artist_shows")
  artist = db.relationship("Artist", backref="venue_shows")

  def __repr__(self):
    return f'<Show Venue ID: {self.venue_id}, Artist ID: {self.artist_id}>'


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), unique=True)
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500), unique=True)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.Text)
    facebook_link = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500))

    created_time  = db.Column(db.DateTime, server_default=db.func.now())
    modified_time = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    artists = db.relationship("Artist", secondary="shows")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), unique=True)
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500), unique=True)
    facebook_link = db.Column(db.String(120), unique=True)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.Text)
    image_link = db.Column(db.String(500))
    
    created_time  = db.Column(db.DateTime, server_default=db.func.now())
    modified_time = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
      return f'<Artist ID: {self.id}, Name: {self.name}>'


