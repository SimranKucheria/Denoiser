from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
import db
import uuid
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, TextField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message


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


class EmailForm(FlaskForm):
    email = StringField('Email')
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class ContactUsForm(FlaskForm):
    name = TextField("Name")
    email = TextField("Email")
    subject = TextField("Subject")
    message = TextAreaField("Message")
    submit = SubmitField("Send")


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

    def delete_article(self, id, user):
        article = db.db.articles.find_one(id)
        if(article['user_id'] == user['_id']):
            if db.db.articles.delete_one(id):
                return redirect('/dashboard/')
        else:
            return jsonify({"error": "Error while deleting article"}), 400

    def get_user_articles(self, id, user):
        author = db.db.users.find_one(id)
        if user['_id'] == author['_id']:
            return db.db.articles.find({'user_id': id})
        else:
            return redirect('/dashboard/')


class Comment:
    def create_comment(self, user, article):
        comment = {
            "_id": uuid.uuid4().hex,
            "commenter_id": user['_id'],
            "commenter_name": user['Firstname']+' '+user['Lastname'],
            "article_id": article['_id'],
            "body": request.form.get('body')
        }
        if db.db.comments.insert_one(comment):
            return jsonify(comment), 200
        else:
            return jsonify({"error": "Error while creating comment"}), 400

    def get_comments(self, article):
        return db.db.comments.find({"article_id": article['_id']})


class CommentForm(FlaskForm):
    body = TextAreaField('Body')
    submit = SubmitField('Submit')
