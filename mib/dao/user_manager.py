from mib.dao.manager import Manager
from mib.models.user import User
import string


class UserManager(Manager):

    @staticmethod
    def create_user(user: User):
        Manager.create(user=user)

    @staticmethod
    def retrieve_by_id(id) -> User:
        Manager.check_none(id=id)
        return User.query.filter(User.id == id).first()

    @staticmethod
    def retrieve_all_users():
        return User.query.all()

    @staticmethod
    def retrieve_by_email(email) -> User:
        Manager.check_none(email=email)
        return User.query.filter(User.email == email).first()

    @staticmethod
    def update_user(user: User):
        Manager.update(user=user)
    
    @staticmethod
    def retrieve_users_by_blacklist(id: int, blacklist):
        Manager.check_none(id=id)
        Manager.check_none(blacklist=blacklist)
        all_users = User.query.filter(User.id != id).filter(~User.id.in_(blacklist))\
            .filter(User.is_active == True).filter(User.is_admin == False).all()
        
        return all_users

    @staticmethod
    def search_users(id: int, firstname: string, lastname: string, email: string, blacklist):
        Manager.check_none(id=id)
        Manager.check_none(blacklist=blacklist)
        
        available_users = UserManager.retrieve_users_by_blacklist(id,blacklist)

        matching_users = []

        for user in available_users:
            if (firstname != '' and firstname in user.firstname) or\
                (lastname != '' and lastname in user.lastname) or\
                (email != '' and email in user.email):

                matching_users.append(user)

        return matching_users

    @staticmethod
    def delete_user(user: User):
        Manager.delete(user=user)

    @staticmethod
    def delete_user_by_id(id : int):
        user = UserManager.retrieve_by_id(id)
        UserManager.delete_user(user)
