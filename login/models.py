from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
import db
import uuid
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, TextAreaField


class User:
    def create_session(self, user):
        del user['Password']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    def signup(self):
        user = {
            "_id": uuid.uuid4().hex,
            "Firstname": request.form.get('fname'),
            "Lastname": request.form.get('lname'),
            "Email": request.form.get('email'),
            "Password": request.form.get('password')
        }

        user['Password'] = pbkdf2_sha256.encrypt(user['Password'])

        if db.db.users.find_one({'Email': user['Email']}):
            return jsonify({"error": "Email ID is already in use"}), 400

        if db.db.users.insert_one(user):
            return self.create_session(user)

        return jsonify({"error": "Error during signup"}), 400

    def signout(self):
        session.clear()
        return redirect('/')

    def login(self):
        user = db.db.users.find_one({
            'Email': request.form.get('email')
        })

        if user and pbkdf2_sha256.verify(request.form.get('password'), user['Password']):
            return self.create_session(user)

        return jsonify({"error": "Invalid login credentials"}), 401


class BlogArticleForm(FlaskForm):
    title = StringField('Title')
    body = TextAreaField('Body')
    submit = SubmitField('Submit')


class Article:
    def create_article(self, user):
        article = {
            "_id": uuid.uuid4().hex,
            "author": user["Firstname"] + ' ' + user["Lastname"],
            "user_id": user["_id"],
            "title": request.form.get("title"),
            "body": request.form.get("body")
        }

        if db.db.articles.insert_one(article):
            return jsonify(article), 200
        else:
            return jsonify({"error": "Error while creating article"}), 400

    def get_articles(self):
        return db.db.articles.find()

    def get_article(self, id):
        return db.db.articles.find_one(id)
