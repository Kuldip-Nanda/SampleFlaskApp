from flask import Flask
from flask import request
from flaskext.mysql import MySQL
from flask_restful import Resource, Api, reqparse


class Database:
    def __init__(self):
        self.mysql = MySQL()
        self.user = 'root'
        self.password = 'passw0rd'
        self.db = 'empdata'
        self.host = 'localhost'

    def set_app(self, myapp):
        myapp.config['MYSQL_DATABASE_USER'] = self.user
        myapp.config['MYSQL_DATABASE_PASSWORD'] = self.password
        myapp.config['MYSQL_DATABASE_DB'] = self.db
        myapp.config['MYSQL_DATABASE_HOST'] = self.host
        self.mysql.init_app(myapp)

    def get_connection(self):
        return self.mysql.connect()

    def checkIfExist(self, user, password):
        try:
            connection = db.get_connection()
            cursor = connection.cursor()
            if password:
                cmd = u"SELECT * from user where name='" + \
                      user + u"' and password='" + password + "'"
            else:
                cmd = u"SELECT * from user where name='" + user + u"' "
            cursor.execute(cmd)
            data = cursor.fetchone()
            if data is None:
                cursor.close()
                connection.close()
                return False
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            cursor.close()
            connection.close()
            raise

    def addUser(self, name, email, password):
        try:
            connection = db.get_connection()
            cursor = connection.cursor()
            cmd = u"insert into user(name, password, email)  " \
                  u"values ('" + name + u"','" + password + \
                  u"','" + email + u"')"
            cursor.execute(cmd)
            connection.commit()
            connection.close()
        except Exception as ex:
            connection.rollback()
            connection.close()
            raise

    def delUser(self, name):
        try:
            connection = db.get_connection()
            cursor = connection.cursor()
            cmd = u"delete from user where name = '" + name + u"'"
            cursor.execute(cmd)
            connection.commit()
        except:
            connection.rollback()
            connection.close()
            raise


class Test(Resource):
    def get(self):
        return "this is a test app"


class Authenticate(Resource):
    def get(self):
        try:
            name = request.args.get('user')
            password = request.args.get('password')

            if not db.checkIfExist(name, password):
                return "Username or Password is wrong"
            else:
                return "Logged in successfully"
        except:
            return "Username or Password is wrong"


class CreateUser(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('user', type=str, help='create user')
            parser.add_argument('email', type=str,
                                help='Email address to create user')
            parser.add_argument('password', type=str,
                                help='Password to create user')
            args = parser.parse_args()

            if db.checkIfExist(args['user'], ""):
                raise Exception("user already exist")
            else:
                db.addUser(args['user'], args['email'], args['password'])

            return {'User': args['user'],
                    'Email': args['email'],
                    'Password': args['password']}

        except Exception as ex:
            return {'error': str(ex)}


class DeleteUser(Resource):
    def delete(self):
        try:
            user = request.args.get('user')
            if not db.checkIfExist(user, ""):
                return "user does not exist"
            else:
                db.delUser(user)
                return "User deleted"
        except Exception as ex:
            return {'error': str(ex)}


if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Test, "/")
    api.add_resource(Authenticate, '/Authenticate')
    api.add_resource(CreateUser, '/CreateUser')
    api.add_resource(DeleteUser, '/DeleteUser')
    db = Database()

    db.set_app(app)

    app.run()
