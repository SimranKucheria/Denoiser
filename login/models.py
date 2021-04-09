from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
import db
import uuid


class User:
    def create_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    def signup(self):
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }

        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        if db.db.users.find_one({'email': user['email']}):
            return jsonify({"error": "Email ID is already in use"}), 400

        if db.db.users.insert_one(user):
            return self.create_session(user)

        return jsonify({"error": "Error during signup"}), 400

    def signout(self):
        session.clear()
        return redirect('/')

    def login(self):
        user = db.db.users.find_one({
            'email': request.form.get('email')
        })

        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.create_session(user)

        return jsonify({"error": "Invalid login credentials"}), 401
