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
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2016/03/30$"
__revision__ = "$Date: 2016/03/30 $"
__copyright__ = "Copyright (c) "
__license__ = ""

from datetime import datetime
from sqlalchemy import desc, event
from bootstrap import db

from web.models import Value, Property, User
from web.notifications import notifications

class Shelter(db.Model):
    """
    Represent a shelter.
    """
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    updated_at = db.Column(db.DateTime(), default=datetime.now)
    is_published = db.Column(db.Boolean(), default=False)
    is_commercial = db.Column(db.Boolean(), default=False)

    # relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    properties = db.relationship('Property', backref='shelter', lazy='noload',
                                cascade='all, delete-orphan',
                                order_by=desc('Property.id'))


    def get_values_of_attribute(self, attribute_id=None, attribute_name=None):
        """
        """
        if attribute_id:
            props = Property.query.filter(
                            Property.shelter_id==self.id,
                            Property.attribute_id==attribute_id)
        else:
            props = Property.query.filter(
                            Property.shelter_id==self.id,
                            Property.attribute.has(name=attribute_name))

        for property_elem in props:
            if property_elem.attribute.id == attribute_id or \
                property_elem.attribute.name == attribute_name:
                return property_elem.values
        else:
            empty_value = Value(name="")
            return [empty_value]

    def get_idvalues_of_attribute(self, attribute_id):
        return [value.id for value in self.get_values_of_attribute(attribute_id)]

    def get_property_of_attribute(self, attribute_id):
        prop = Property.query.filter(
                            Property.shelter_id==self.id,
                            Property.attribute_id==attribute_id)
        if prop:
            return prop.first()
        else:
            return 0

    def __str__(self):
        """
        Required for administrative interface.
        """
        return str(self.id)


@event.listens_for(Shelter, "after_insert")
def after_insert(mapper, connection, target):
    user = User.query.filter(User.id==target.user_id).first()
    if not user.is_admin:
        try:
            notifications.new_shelter_creation(target, user)
        except Exception as e:
            print(e)
