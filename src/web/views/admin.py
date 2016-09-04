#! /usr/bin/env python
#-*- coding: utf-8 -*-

# ***** BEGIN LICENSE BLOCK *****
# This file is part of Shelter Database.
# Copyright (c) 2016 Luxembourg Institute of Science and Technology.
# All rights reserved.
#
#
#
# ***** END LICENSE BLOCK *****

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2016/06/07 $"
__revision__ = "$Date: 2016/07/12 $"
__copyright__ = "Copyright 2016 Luxembourg Institute of Science and Technology"
__license__ = ""

#
# Views generated by Flask-Admin for the database administration.
#
from flask_login import current_user
from flask import current_app
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

from bootstrap import db
from web.models import User, Shelter, Value, Translation

class TranslationView(ModelView):
    column_searchable_list = ('original', 'translated')
    column_filters = ['language_code']
    column_editable_list = ['translated']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class ValueView(ModelView):
    column_searchable_list = ('name',)
    column_filters = ['attribute_id']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class UserView(ModelView):
    column_exclude_list = ['pwdhash']
    column_editable_list = ['email', 'name']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class ShelterView(ModelView):
    column_exclude_list = ['properties']
    form_excluded_columns = ['properties']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

menu_link_back_dashboard = MenuLink(name='Back to dashboard',
                                url='/admin/dashboard')
menu_link_back_home = MenuLink(name='Back to home',
                                url='/')

admin = Admin(current_app,
                name='Management of data',
                template_mode='bootstrap3',
                index_view=AdminIndexView(
                        name='Home',
                        url='/admin/data_management'
                    ))
admin.add_view(UserView(User, db.session))
admin.add_view(ShelterView(Shelter, db.session))
admin.add_view(ValueView(Value, db.session))
admin.add_view(TranslationView(Translation, db.session))
admin.add_link(menu_link_back_home)
admin.add_link(menu_link_back_dashboard)
