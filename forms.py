from datetime import date, datetime as d
from typing import ValuesView
from flask.helpers import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, ValidationError, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp
from enum import Enum
import phonenumbers
import re

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        format="%Y-%m-%d %H:%M",
        default= d.now()        
    )

    def validate_artist_id(self, artist_id):
        try:
            match = re.search(r'^\d+$', artist_id.data)
            if not match:
                raise ValueError()
        except (ValueError):
            raise ValidationError("The artist id should be a number!")  

    def validate_venue_id(self, venue_id):
        try:
            match = re.search(r'^\d+$', venue_id.data)
            if not match:
                raise ValueError()
        except (ValueError):
            raise ValidationError("The venue id should be a number!")  


    def validate_start_time(self, start_time):
        try:
            startTime = ''
            if start_time.data is not None:
                startTime = start_time.data.strftime("%Y-%m-%d %H:%M")

            match = re.search(r"^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[01]) (2[0-3]|[01][0-9]):[0-5][0-9]$", startTime)
            if not match:
                raise ValueError("Date Fromat should be YYYY-MM-DD HH:MM")            
            elif start_time.data < d.now():
                raise ValueError("The date should be a future date!")
        except (ValueError) as e:
            raise ValidationError(e)


class State(Enum):
    AL = 'AL'
    AK = 'AK'
    AZ = 'AZ'
    AR = 'AR'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DE = 'DE'
    DC = 'DC'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    IA = 'IA'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    ME = 'ME'
    MT = 'MT'
    NE = 'NE'
    NV = 'NV'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NY = 'NY'
    NC = 'NC'
    ND = 'ND'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    MD = 'MD'
    MA = 'MA'
    MI = 'MI'
    MN = 'MN'
    MS = 'MS'
    MO = 'MO'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VT = 'VT'
    VA = 'VA'
    WA = 'WA'
    WV = 'WV'
    WI = 'WI'
    WY = 'WY'

    def __str__(self):
        return self.name

    @classmethod
    def choices(states):
        return [(choice, choice.value) for choice in states]

    @classmethod
    def coerce(state, item):
        return state(int(item)) if not isinstance(item, state) else item

class Genre(Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    Hip_Hop = 'Hip-Hop'
    Heavy_Metal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    Musical_Theatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    R_and_B = 'R&B'
    Reggae = 'Reggae'
    Rock_n_Roll = 'Rock n Roll'
    Soul = 'Soul'
    Other = 'Other'

    def __str__(self):
            return self.name

    @classmethod
    def choices(genres):
        return [(choice, choice.value) for choice in genres]

        
    @classmethod
    def coerce(genre, item):
        return genre(int(item)) if not isinstance(item, genre) else item

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices= State.choices(),
        coerce=State.coerce
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=Genre.choices(),
        coerce=Genre.coerce 
    )
    website = StringField(
        'website', validators=[DataRequired()]
    )
    seeking_talent = BooleanField(
        'seeking_talent', id="seeking_talent"
    )
    seeking_description = StringField(
        'seeking_description', id="seeking_description"
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

    # TODO implement validation logic for state
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data, 'US')
            if not phonenumbers.is_valid_number(p):
                raise ValueError()        
        except (ValueError):
            raise ValidationError('Invalid US phone number')


class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices(),
        coerce=State.coerce
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    website = StringField(
        'website', validators=[DataRequired()]
    )
    seeking_venue = BooleanField(
        'seeking_venue', id="seeking_venue"
    )
    seeking_description = StringField(
        'seeking_description', id="seeking_description"
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=Genre.choices(),
        coerce = Genre.coerce
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
    )

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data, 'US')
            if not phonenumbers.is_valid_number(p):
                raise ValueError()        
        except (ValueError):
            raise ValidationError('Invalid US phone number')

# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM

# My OWN Version of ShowForm
# class ShowForm(FlaskForm):
#     venues = SelectMultipleField(
#         'venues', validators=[DataRequired()],
#     )
#     artists = SelectMultipleField(
#         'artists', validators=[DataRequired()],
#     )
#     start_time = DateTimeField(
#         'start_time', validators=[DataRequired()],
#     )

#     def validate_start_time(self, start_time):
#         try:
#             if start_time.data < d.now():
#                 raise ValueError()
#         except (ValueError):
#             raise ValidationError("The date cannot be in the past!")  