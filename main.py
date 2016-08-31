#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Posts(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    date = db.DateProperty(auto_now_add = True)

class MainPage(Handler):
    def render_blog(self):
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY date DESC")
        self.render("blog.html", posts = posts)

    def get(self):
        self.render_blog()

class NewPost(Handler):
    def render_form(self, subject="", content="", error=""):
        self.render("newpost.html", subject = subject, content = content, error = error)

    def get(self):
        self.render_form()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Posts(subject = subject, content = content)
            p.put()

            self.redirect("/%s" % str(p.key().id()))
        else:
            error = "subject and content required"
            self.render_form(subject, content, error)

class PermaLink(Handler):
    def get(self, post_id):
        post = Posts.get_by_id(int(post_id))

        self.render("permalink.html", subject = post.subject,
                    content = post.content, date = post.date)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    ('/(\d+)', PermaLink)
], debug=True)
