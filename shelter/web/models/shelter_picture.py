#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
__date__ = "$Date: 2016/06/09 $"
__revision__ = "$Date: 2016/06/09 $"
__copyright__ = "Copyright (c) "
__license__ = ""

from bootstrap import db


class ShelterPicture(db.Model):
    """
    Represent a picture for a shelter.
    """

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(), default="")
    is_main_picture = db.Column(db.Boolean(), default=False)

    # relationship
    shelter_id = db.Column(db.Integer, db.ForeignKey("shelter.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
