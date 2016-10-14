#!/usr/bin/python
from OpenSSL import SSL
from flask import Flask, session, request, redirect, abort
from flaskext.mysql import MySQL
from flask_restful import Resource, Api, reqparse


class Database:
    def __init__(self):
        self.mysql = MySQL()
        self.user = 'appadmin'
        self.password = 'passw0rd'
        self.db = 'empdata'
        self.host = '127.0.0.1'

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


class Login(Resource):
    def post(self):
        try:
            name = request.json['user']
            password = request.json['password']

            if not db.checkIfExist(name, password):
                return "Username or Password is wrong"
            else:
                session['username'] = name
                return "Logged in successfully"
        except:
            return "Username or Password is wrong"


class Logout(Resource):
    def post(self):
        if 'username' not in session:
            return "nothing logged in"
        session.pop("username", None)
        return "logged out"


class CreateUser(Resource):
    def post(self):
        try:
            if 'username' not in session:
                return abort(403)

            user = request.json['user']
            email = request.json['email']
            password = request.json['password']
            if db.checkIfExist(user, ""):
                raise Exception("user already exist")
            else:
                db.addUser(user, email, password)

            return {'User': user,
                    'Email': email,
                    'Password': password}

        except Exception as ex:
            return {'error': str(ex)}


class DeleteUser(Resource):
    def delete(self):
        try:
            if 'username' not in session:
                return abort(403)
            user = request.json['user']
            if not db.checkIfExist(user, ""):
                return "user does not exist"
            else:
                db.delUser(user)
                return "User deleted"
        except Exception as ex:
            return {'error': str(ex)}


if __name__ == "__main__":
    # create security context
    context = ("./conf/server.crt", "./conf/server.key")

    # create the webapp with session
    app = Flask(__name__)
    app.secret_key = 'any random string'
    api = Api(app)

    # set the routes
    api.add_resource(Test, "/")
    api.add_resource(Login, '/Login')
    api.add_resource(Logout, '/Logout')
    api.add_resource(CreateUser, '/CreateUser')
    api.add_resource(DeleteUser, '/DeleteUser')

    # create mysql db connection to flask
    db = Database()
    db.set_app(app)

    # now run
    app.run(host='0.0.0.0', port=5000, ssl_context=context,
            threaded=True, debug=True)
