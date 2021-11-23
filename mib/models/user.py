from werkzeug.security import generate_password_hash, check_password_hash

from mib import db


class User(db.Model):
    """Representation of User model."""

    # The name of the table that we explicitly set
    __tablename__ = 'User'

    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'email', 'is_active', 'authenticated', 'is_anonymous']

    # All fields of user
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    first_name = db.Column(db.Unicode(128), nullable=False, unique=False)
    last_name = db.Column(db.Unicode(128), nullable=False, unique=False)
    password = db.Column(db.Unicode(128))
    birthdate = db.Column(db.Date())
    phone = db.Column(db.Unicode(128), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    authenticated = db.Column(db.Boolean, default=True)
    is_anonymous = False

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self.authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def set_email(self, email):
        self.email = email

    def set_first_name(self, name):
        self.first_name = name

    def set_last_name(self, name):
        self.last_name = name

    def is_authenticated(self):
        return self.authenticated

    def set_birthday(self, birthdate):
        self.birthdate = birthdate

    def set_phone(self, phone):
        self.phone = phone

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self.authenticated = checked
        return self.authenticated

    def serialize(self):
        return dict([(k, self.__getattribute__(k)) for k in self.SERIALIZE_LIST])
