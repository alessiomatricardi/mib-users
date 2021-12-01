from werkzeug.security import generate_password_hash, check_password_hash

from mib import db

# default library salt length is 8
# adjusting it to 16 allow us to improve the strongness of the password
_SALT_LENGTH = 16


class User(db.Model):
    """Representation of User model."""

    # The name of the table that we explicitly set
    __tablename__ = 'User'

    # A list of fields to be serialized TODO CONTROLLARE
    SERIALIZE_LIST = ['id', 'email', 'is_active', 'firstname', 'lastname', 'date_of_birth', 'lottery_points', 'has_picture', 'content_filter_enabled']

    # All fields of user
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), unique=True, nullable=False) # TODO insert again 
    firstname = db.Column(db.Unicode(128), nullable=False)
    lastname = db.Column(db.Unicode(128), nullable=False)
    password = db.Column(db.Unicode(128), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    authenticated = db.Column(db.Boolean, default=True)
    has_picture = db.Column(db.Boolean, default=False)  # has the user a personal profile picture
    lottery_points = db.Column(db.Integer, default=0)
    content_filter_enabled = db.Column(db.Boolean, default=False)
    is_anonymous = False

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self.authenticated = False

    def set_password(self, password):
        '''
        According to https://werkzeug.palletsprojects.com/en/2.0.x/utils/#werkzeug.security.generate_password_hash
        generate_password_hash returns a string in the format below
        pbkdf2:sha256:num_of_iterations$salt$hash
        '''
        self.password = generate_password_hash(password, salt_length = _SALT_LENGTH)

    def set_email(self, email):
        self.email = email

    def set_first_name(self, name):
        self.firstname = name

    def set_last_name(self, name):
        self.lastname = name

    def is_authenticated(self):
        return self.authenticated

    def set_birthday(self, date_of_birth):
        self.date_of_birth = date_of_birth

    def authenticate(self, password):
        # an user no more active couldn't authenticate himself
        if not self.is_active:
            return False
        
        checked = check_password_hash(self.password, password)
        self.authenticated = checked
        return self.authenticated

    def serialize(self):
        return dict([(k, self.__getattribute__(k)) for k in self.SERIALIZE_LIST])
