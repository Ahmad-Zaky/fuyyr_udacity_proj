#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import backref
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from forms import *
from flask_migrate import Migrate
import sys, traceback
from re import error
from datetime import datetime as d

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Venue, Artist, Show

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  cities = Venue.query.distinct(Venue.city).all()
  data = [{
    "city": city.city,
    "state": city.state,
    "venues": [{
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > d.now().strftime("%Y-%m-%d %H:%M")).count()
    } for venue in Venue.query.filter_by(city=city.city).all()]
  } for city in cities]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%"+search_term+"%")).all()
  
  response={
    "count": len(venues),
    "data":[{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len([show.venue_id for show in Show.query.filter_by(venue_id=venue.id) if show.start_time > d.now()])
    } for venue in venues] if venues else ''
  } 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()

  if venue or shows:
    postShows = [ {
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M')
    } for show in shows if show.start_time < d.now()]

    upcommingShows = [ {
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M')
    } for show in shows if show.start_time > d.now()]  

    data={
      "id": venue_id,
      "name": venue.name,
      "genres": venue.genres.replace("\"","").lstrip('{').rstrip('}').split(','),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": postShows,
      "upcoming_shows": upcommingShows,
      "past_shows_count": len(postShows),
      "upcoming_shows_count": len(upcommingShows),
    }

    data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
    return render_template('pages/show_venue.html', venue=data)
  else:
    flash("Venue with ID ("+str(venue_id)+") is not found!")
    return render_template('pages/home.html')


#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get(venue_id)
  
  if venue:
    form = VenueForm()
    venue={
      "id": venue.id,
      "name": venue.name,
      "genres": json.dumps(venue.genres),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    abort(404)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  form = VenueForm(request.form)
  error = False
  body = {}
  try:
    venue = Venue.query.get(venue_id)
    if venue:
      if form.validate():
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website = form.website.data 
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data

        db.session.commit()
      else:
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    else:
      abort(404)
  except (IntegrityError) as e:
    error = True
    errorInfo = e.orig.args[0]
    
    toFind =  'DETAIL:'
    detailPos = errorInfo.find(toFind)
    
    toFind = 'Key'
    keyPos = errorInfo.find(toFind)

    if detailPos != -1 and keyPos != -1:

      # get field name
      keyEndPos = errorInfo.find(')')
      keyName = errorInfo[keyPos+len(toFind)+2:keyEndPos]

      # get field value
      afterkey = errorInfo[keyEndPos+3:]
      valueEndPos = afterkey.find(')')
      keyValue = afterkey[:valueEndPos]

      flash('Field ('+keyName+') has a duplicate value ('+keyValue +') !')
    else:
      flash('there is a duplicate value!')
      
    db.session.rollback()
    print(sys.exc_info())
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  except (Exception) as e:  
    error = True
    db.session.rollback()
    print(sys.exc_info())
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
  finally:
    db.session.close()

  if error:
    # TODO: on unsuccessful db update, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be updated.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    # on successful db update, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  error = False
  body = {}
  try:
    if form.validate():
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      genres = form.genres.data
      website = form.website.data 
      seeking_talent = form.seeking_talent.data
      seeking_description = form.seeking_description.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      venue = Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        genres=genres,
        website=website,
        seeking_talent=seeking_talent,
        seeking_description=seeking_description,
        image_link=image_link,
        facebook_link=facebook_link
      )
      db.session.add(venue)
      db.session.commit()
    else:
      return render_template('forms/new_venue.html', form=form)
  except (IntegrityError) as e:
    error = True
    errorInfo = e.orig.args[0]
    
    toFind =  'DETAIL:'
    detailPos = errorInfo.find(toFind)
    
    toFind = 'Key'
    keyPos = errorInfo.find(toFind)

    if detailPos != -1 and keyPos != -1:

      # get field name
      keyEndPos = errorInfo.find(')')
      keyName = errorInfo[keyPos+len(toFind)+2:keyEndPos]

      # get field value
      afterkey = errorInfo[keyEndPos+3:]
      valueEndPos = afterkey.find(')')
      keyValue = afterkey[:valueEndPos]

      flash('Field ('+keyName+') has a duplicate value ('+keyValue +') !')
    else:
      flash('there is a duplicate value!')
      
    db.session.rollback()
    print(sys.exc_info())
    return render_template('forms/new_venue.html', form=form)
  except (Exception) as e:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
  finally:
    db.session.close() 
    
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  message = ''
  try:
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    if venue or shows:
      for show in shows:
        db.session.delete(show)

      db.session.delete(venue)
      db.session.commit()
    else:
      error = True
      message = "Venue with ID ("+str(venue_id)+") is not found!"
      flash(message)
      return jsonify({'success': error, 'message': message})
  except (Exception) as e:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()    
    
  if error:
    message = 'An error occurred. Venue: ' + venue.name + ' could not be deleted.'
    flash(message)
  else:
    message = 'Venue: ' + venue.name + ' was successfully deleted!'
    flash(message)
  return jsonify({'success': not error, 'message':message})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = [{
      "id": artist.id,
      "name": artist.name    
    } for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%"+search_term+"%")).all()
  
  response={
    "count": len(artists),
    "data":[{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len([show.artist_id for show in Show.query.filter_by(artist_id=artist.id) if show.start_time > d.now()])
    } for artist in venues] if venues else ''
  } 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()

  if artist or shows:
    postShows = [ {
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M')
    } for show in shows if show.start_time < d.now()]

    upcommingShows = [ {
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M')
    } for show in shows if show.start_time > d.now()]  

    data={
      "id": artist_id,
      "name": artist.name,
      "genres": artist.genres.replace("\"","").lstrip('{').rstrip('}').split(','),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": postShows,
      "upcoming_shows":upcommingShows,
      "past_shows_count": len(postShows),
      "upcoming_shows_count": len(upcommingShows)
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
    return render_template('pages/show_artist.html', artist=data)
  else:
    flash("Artist with ID ("+str(artist_id)+") is not found!")
    return render_template('pages/home.html')

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)

  if artist:

    form = ArtistForm()
    artist={
      "id": artist.id,
      "name": artist.name,
      "genres": json.dumps(artist.genres),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    abort(404)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attribute
  
  form = ArtistForm(request.form)
  error = False
  body = {}
  try:
    artist = Artist.query.get(artist_id)
    if artist:
      if form.validate():
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.website = form.website.data 
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data

        db.session.commit()
      else:
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
      abort(404)
  except (IntegrityError) as e:
    error = True
    errorInfo = e.orig.args[0]
    
    toFind =  'DETAIL:'
    detailPos = errorInfo.find(toFind)
    
    toFind = 'Key'
    keyPos = errorInfo.find(toFind)

    if detailPos != -1 and keyPos != -1:

      # get field name
      keyEndPos = errorInfo.find(')')
      keyName = errorInfo[keyPos+len(toFind)+2:keyEndPos]

      # get field value
      afterkey = errorInfo[keyEndPos+3:]
      valueEndPos = afterkey.find(')')
      keyValue = afterkey[:valueEndPos]

      flash('Field ('+keyName+') has a duplicate value ('+keyValue +') !')
    else:
      flash('there is a duplicate value!')
      
    db.session.rollback()
    print(sys.exc_info())
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  except (Exception) as e:  
    error = True
    db.session.rollback()
    print(sys.exc_info())
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
  finally:
    db.session.close()

  if error:
    # TODO: on unsuccessful db update, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be updated.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    # on successful db update, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  error = False
  body = {}
  try:
    if form.validate():
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      genres = form.genres.data
      website = form.website.data 
      facebook_link = form.facebook_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
      image_link = form.image_link.data
      artist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        genres=genres,
        website=website,
        facebook_link=facebook_link,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description,
        image_link=image_link
        )
      db.session.add(artist)
      db.session.commit()
    else:
      return render_template('forms/new_artist.html', form=form)
  except (IntegrityError) as e:
    error = True
    errorInfo = e.orig.args[0]
    
    toFind =  'DETAIL:'
    detailPos = errorInfo.find(toFind)
    
    toFind = 'Key'
    keyPos = errorInfo.find(toFind)

    if detailPos != -1 and keyPos != -1:

      # get field name
      keyEndPos = errorInfo.find(')')
      keyName = errorInfo[keyPos+len(toFind)+2:keyEndPos]

      # get field value
      afterkey = errorInfo[keyEndPos+3:]
      valueEndPos = afterkey.find(')')
      keyValue = afterkey[:valueEndPos]

      flash('Field ('+keyName+') has a duplicate value ('+keyValue +') !')
    else:
      flash('there is a duplicate value!')
      
    db.session.rollback()
    print(sys.exc_info())
    return render_template('forms/new_artist.html', form=form)
  except (Exception) as e:  
    error = True
    db.session.rollback()
    print(sys.exc_info())
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
  finally:
    db.session.close()

  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')



#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Artist on a Artist Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  message = ''
  try:
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    if artist or shows:
      for show in shows:
        print('here')
        db.session.delete(show)

      db.session.delete(artist)
      db.session.commit()
    else:
      error = True
      message = "Artist with ID ("+str(artist_id)+") is not found!"
      flash(message)
      return jsonify({'success': error, 'message': message})
  except (Exception) as e:
    # db.session.rollback()
    error=True
    print(sys.exc_info())
  # finally:
    # db.session.close()    
    
  if error:
    message = 'An error occurred. Artist: ' + artist.name + ' could not be deleted.'
    flash(message)
  else:
    message = 'Artist: ' + artist.name + ' was successfully deleted!'
    flash(message)
  return jsonify({'success': not error, 'message':message})


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = [{
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time.strftime("%Y-%m-%d %H:%M")
  } for show in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  error = False
  body = {}
  try:
    if form.validate():

      venue_id = form.venue_id.data
      artist_id = form.artist_id.data
      start_time = form.start_time.data


      # Check if venue_id, artist_id exists
      artist = Artist.query.get(artist_id)
      venue = Venue.query.get(venue_id)

      if venue and artist:
        show = Show(
          venue_id=venue_id,
          artist_id=artist_id,
          start_time=start_time
          )
        db.session.add(show)
        db.session.commit()
      else:
        return render_template('forms/new_show.html', form=form)
    else:
      return render_template('forms/new_show.html', form=form)
  except (IntegrityError) as e:
    error = True
    db.session.rollback()

    errorInfo = e.orig.args[0]
    
    toFind =  'DETAIL:'
    detailPos = errorInfo.find(toFind)
    
    toFind = 'Key'
    keyPos = errorInfo.find(toFind)
    
    toFind = 'shows_pkey'
    artist_venue_dup = errorInfo.find(toFind)
    
    toFind = 'unique_artistid_starttime'
    artist_starttime_dup = errorInfo.find(toFind)

    if detailPos != -1 and keyPos != -1 and artist_starttime_dup != -1:

      # get first field name
      keyEndPos = errorInfo.find(')')
      compkeyName = errorInfo[keyPos+len(toFind)+2:keyEndPos]
      firstKeyName = compkeyName[:compkeyName.find(',')]

      # get first field value
      afterkey = errorInfo[keyEndPos+3:]
      valueEndPos = afterkey.find(')')
      compkeyValue = afterkey[:valueEndPos]
      firstKeyValue = compkeyValue[:compkeyValue.find(',')]

      flash('Artist with ID: ('+firstKeyValue+') has another show on the same time!')
    elif artist_venue_dup != -1:
      flash('The show already exists.')
    else:
      flash('The show already exists.')
      
    # print(sys.exc_info())
    return render_template('forms/new_show.html', form=form)
  except (Exception) as e:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
  finally:
    db.session.close()

  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
