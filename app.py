#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import sys
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import literal, func, cast, Date

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), unique=True)
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))


#     {
#     "city": "San Francisco",
#     "state": "CA",
#     "venues": [{
#       "id": 1,
#       "name": "The Musical Hop",
#       "num_upcoming_shows": 0,
#     }, {
#       "id": 3,
#       "name": "Park Square Live Music & Coffee",
#       "num_upcoming_shows": 1,
#     }]
#   }

    # TODO implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500), unique=True)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    # create a relationship between an artist and their show(s)
    # shows = db.relationship('Show', backref='artist', lazy=True)
    
    def __repr__(self):
      return f'''<Artist id({self.id})
       name: {self.name},
       city:{self.city},
       genres:{self.genres}
       >'''


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_name = db.Column(db.String(120), db.ForeignKey('Venue.name'), unique=False)
    artist_name = db.Column(db.String(120), db.ForeignKey('Artist.name'), unique=False)
    venue_image_link = db.Column(db.String(500), db.ForeignKey('Venue.image_link'), unique=False)
    artist_image_link = db.Column(db.String(500), db.ForeignKey('Artist.image_link'), unique=False)
    start_time = db.Column(db.String(200))



    # TODO implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # TODO replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #       Group query by city and state

  all_areas = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

  for area in all_areas:
    area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in area_venues:
      venue_data.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(cast(Show.start_time, Date)>datetime.now()).all())
      })
    data.append({
      "city": area.city,
      "state": area.state, 
      "venues": venue_data
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  venue.genres = venue.genres.split(',')

  past_shows_list = Show.query.join(Artist, Artist.id == Show.artist_id).filter(Show.venue_id == venue.id).filter(cast(Show.start_time,Date) < datetime.now()).all()

  upcoming_shows_list = Show.query.join(Artist, Artist.id == Show.artist_id).filter(Show.venue_id == venue.id).filter(cast(Show.start_time,Date) > datetime.now()).all()

  past_shows = []
  upcoming_shows = []

  for show in past_shows_list:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": show.start_time
    })

  for show in upcoming_shows_list:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": show.start_time
    })


  past_shows_count = len(past_shows_list)
  upcoming_shows_count = len(upcoming_shows_list)

  venue.past_shows = past_shows
  venue.upcoming_shows = upcoming_shows
  venue.past_shows_count = len(past_shows)
  venue.upcoming_shows_count = len(upcoming_shows)

  print(venue)

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO insert form data as a new Venue record in the db, instead
  # TODO modify data to be the data object returned from db insertion
  venueForm = request.form.copy()
  error = False
  try:
    genresString = ",".join(venueForm.getlist('genres'))
    newVenue = Venue(name=venueForm['name'], 
      city=venueForm['city'], state=venueForm['state'], address=venueForm['address'], 
      phone=venueForm['phone'], facebook_link=venueForm['facebook_link'], image_link=venueForm['image_link'], 
      genres=genresString)

    db.session.add(newVenue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:  
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      return render_template('pages/home.html')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venueName = ""
  error = False
  try:
    venueToDelete = Venue.query.get(venue_id)
    venueName = venueToDelete.name
    db.session.delete(venueToDelete)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('an error occured while deleting Venue ' + venueName + '!')
    return render_template('pages/home.html')
  else:
    flash('Venue ' + venueName + ' was successfully deleted!')
    return render_template('pages/home.html')
    # return redirect(url_for('index'))
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO replace with real data returned from querying the database
  artists = Artist.query.all()
  print(artists)

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = (request.form.get('search_term', ''))
  search_result = Artist.query.filter(func.lower(Artist.name).contains(search_term.lower())).all()
  print(search_result)

  response={
    "count": len(search_result),
    "data": search_result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO replace with real venue data from the venues table, using venue_id

      #TODO  divide all shows into past & upcoming based on show date
      #       implement past/upcoming show count based on the query 
  
  artist = Artist.query.get(artist_id)
  artist.genres = artist.genres.split(',')
  

  past_shows_list = Show.query.join(Venue, Venue.id == Show.venue_id).filter(Show.artist_id == artist.id).filter(cast(Show.start_time,Date) < datetime.now()).all()

  upcoming_shows_list = Show.query.join(Venue, Venue.id == Show.venue_id).filter(Show.artist_id == artist.id).filter(cast(Show.start_time,Date) > datetime.now()).all()

  past_shows = []
  upcoming_shows = []

  for show in past_shows_list:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "venue_image_link": show.venue_image_link,
      "start_time": show.start_time
    })

  for show in upcoming_shows_list:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "venue_image_link": show.venue_image_link,
      "start_time": show.start_time
    })

  print(past_shows)

  past_shows_count = len(past_shows_list)
  upcoming_shows_count = len(upcoming_shows_list)

  artist.past_shows = past_shows
  artist.upcoming_shows = upcoming_shows
  artist.past_shows_count = len(past_shows)
  artist.upcoming_shows_count = len(upcoming_shows)
  
  print(artist)

  
  return render_template('pages/show_artist.html', artist=artist)
  # TODO UPCOMING & PAST Shows
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist.genres = artist.genres.split(',')
  print(artist)
  # TODO  populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    artistForm = request.form.copy()
    error = False

    try:
      genresString = ",".join(artistForm.getlist('genres'))
      
      artist = Artist.query.get(artist_id)

      artist.name=artistForm['name'], 
      artist.city=artistForm['city']
      artist.state=artistForm['state']
      artist.phone=artistForm['phone'],
      artist.facebook_link=artistForm['facebook_link']
      artist.image_link=artistForm['image_link']
      artist.genres=genresString

      db.session.commit()

    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    
    finally:
      db.session.close()
      if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
        return redirect(url_for('show_artist', artist_id=artist_id))
      else:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
        return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue.genres = venue.genres.split(',')
  print(venue)
  # TODO  populate form with fields from venue with ID <venue_ID>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    venueForm = request.form.copy()
    error = False

    try:
      genresString = ",".join(venueForm.getlist('genres'))
      
      venue = Venue.query.get(venue_id)

      venue.name=venueForm['name'], 
      venue.city=venueForm['city']
      venue.state=venueForm['state']
      venue.phone=venueForm['phone'],
      venue.facebook_link=venueForm['facebook_link']
      venue.image_link=venueForm['image_link']
      venue.genres=genresString

      db.session.commit()

    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    
    finally:
      db.session.close()
      if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
        return redirect(url_for('show_venue', venue_id=venue_id))
      else:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
        return redirect(url_for('show_venue', venue_id=venue_id))
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO insert form data as a new Venue record in the db, instead
  # TODO modify data to be the data object returned from db insertion
  artistForm = request.form.copy()
  error = False
  try:
    genresString = ",".join(artistForm.getlist('genres'))
    newArtist = Artist(name=artistForm['name'], 
      city=artistForm['city'], state=artistForm['state'], phone=artistForm['phone'],
      facebook_link=artistForm['facebook_link'], image_link=artistForm['image_link'], 
      genres=genresString)

    db.session.add(newArtist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:  
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      return render_template('pages/home.html')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.all()

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO insert form data as a new Show record in the db, instead
  form_data = request.form.copy()
  error = False

  try:
    print(form_data)
    artist = Artist.query.get(form_data['artist_id'])
    venue = Venue.query.get(form_data['venue_id'])

    newShow = Show(venue_id = venue.id, artist_id = artist.id, venue_name = venue.name, artist_name = artist.name, venue_image_link = venue.image_link, artist_image_link = artist.image_link, start_time = form_data['start_time'])

    db.session.add(newShow)
    db.session.commit()

  except:
    db.session.rollback()
    error = True
    print(sys.exc_info)

  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
      # abort(400)
      return render_template('pages/home.html')
    else:
      flash('Show was successfully listed!')
      return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
