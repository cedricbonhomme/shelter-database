#! /usr/bin/env python
#-*- coding: utf-8 -*-

# ***** BEGIN LICENSE BLOCK *****

#
#
# ***** END LICENSE BLOCK *****

__author__ = ""
__version__ = ""
__date__ = ""
__revision__ = ""
__copyright__ = ""
__license__ = ""

from bootstrap import db, app
from sqlalchemy.sql import func, select, desc
from flask import Blueprint, jsonify, request, json, Response, send_from_directory
from collections import defaultdict
from web.models import Shelter, Attribute, AttributePicture, Property, Value, Association, ShelterPicture, ShelterDocument, Category, Tsvector, Translation

import conf, os.path
from web.notifications import notifications
from web.decorators import docstring_formatter

apiv02_bp = Blueprint('development api v0.2', __name__, url_prefix='/api/v0.2')

def tree():
    return defaultdict(tree)
    

def jsonify_utf8(text):
    """Jsonifies the input object and sets the encoding to UTF-8. 
    Useful when serving static files as JSON so UTF-8 characters are shown properly"""
    return Response(json.dumps(text, indent=3, sort_keys=False), mimetype='application/json;charset=utf-8')
    

def populate_dictree(query, catquery, dictree, prettytext=False):
    """
    Populates a multidict tree object with the shelter properties
    """
    
    booleantext = ("no","yes")
    
    for s in query:
    	if not dictree[s.shelter_id]:
    		for c in catquery:
    			if c.name == "Identification":
    				dictree[s.shelter_id][c.name]["Cover"]
    			dictree[s.shelter_id][c.name]["Attributes"]
    			dictree[s.shelter_id][c.name]["Pictures"]
    			#dictree[s.shelter_id][c.name]["Documents"]
    			
    	if prettytext:
    		if s.type == "yes / no":
    			dictree[s.shelter_id][s.supercategory_name]["Attributes"][s.name] = booleantext[int(s.value)]
    		else:
    			dictree[s.shelter_id][s.supercategory_name]["Attributes"][s.name] = s.value
    	else:
    		if s.type == "yes / no":
    			dictree[s.shelter_id][s.supercategory_name]["Attributes"][s.uniqueid] = booleantext[int(s.value)]
    		else:
    			dictree[s.shelter_id][s.supercategory_name]["Attributes"][s.uniqueid] = s.value
    
    return dictree


def populate_pictures(query, dictree, picpath):
    """
    populates pictures in an existing dictree for the shelters it contains
    """
    
    for p in query:
    	if p.shelter_id in dictree:
    		if p.is_main_picture == True:
    			if not dictree[p.shelter_id]["Identification"]["Cover"]:
    				dictree[p.shelter_id]["Identification"]["Cover"] = ["{}/{}/{}".format(picpath, p.shelter_id, p.filename)]
    			else:
    				dictree[p.shelter_id]["Identification"]["Cover"].append("{}/{}/{}".format(picpath, p.shelter_id, p.filename))
    		elif not dictree[p.shelter_id][p.name]["Pictures"]:
    			dictree[p.shelter_id][p.name]["Pictures"] = ["{}/{}/{}".format(picpath, p.shelter_id, p.filename)]
    		else:
    			dictree[p.shelter_id][p.name]["Pictures"].append("{}/{}/{}".format(picpath, p.shelter_id, p.filename))
    
    return dictree

@apiv02_bp.route('/', methods=['GET'])
def apimessage():
    message = tree()
    message["API version"] = 0.2
    message["Message"] = "This is the development API"
    return jsonify(message)

@apiv02_bp.route('/email', methods=['GET'])
def mail():
    query = Shelter.query.first()
    notifications.new_shelter_creation(query)

@apiv02_bp.route('/documentation', methods=['GET'])
def documentation():
    """
    Serves this documentation page
    """
    return send_from_directory('static/documentation','apidoc.html')

@apiv02_bp.route('/glossary', methods=['GET'])
def glossary():
	"""
	Retrieve the glossary in JSON format, readable by Glossarizer
	(https://github.com/PebbleRoad/glossarizer) 
	"""
	
	with app.open_resource('static/data/glossary.json') as f:
		text = json.load(f, encoding='utf-8')
	return jsonify_utf8(text)
	

@apiv02_bp.route('/worldmap', methods=['GET'])
def worldmap():
	#"""
	#Retrieve a world map in GeoJSON format, 
	#with polygons and a centroid point representing each country
	#"""
	
	with app.open_resource('static/data/countries.geojson') as f:
		data = json.load(f, encoding='utf-8')
	return jsonify_utf8(data)


@docstring_formatter(conf.PLATFORM_URL)
@apiv02_bp.route('/attributes/pictures', methods=['GET'])
@apiv02_bp.route('/attributes/pictures/<language_code>', methods=['GET'])
def attribute_pictures(language_code='en'):
    """
    Retrieve attribute pictures in a given language. If no language code prameter supplied, the default language is English.
    
    :param language_code: language code, in lower case two letter format. Example: 'fr' for French
    :type language_code: string
    
    
    **Example requests**:
     
     .. sourcecode:: html
         
         # get attribute pictures in default language (English)
         GET {0}/api/v0.2/attributes/pictures
         
         # get attribute pictures in French
         GET {0}/api/v0.2/attributes/pictures/fr  
    """
    
    result = tree()
    
    picpath = conf.ATTRIBUTES_PICTURES_SITE_PATH
   
    query = db.session.query(Attribute.name, Category.name.label("category_name"), 
                            func.array_agg(picpath + '/' + language_code + '/' + AttributePicture.file_name).label("file_names"))\
    		.join(AttributePicture, Attribute.id==AttributePicture.attribute_id)\
    		.join(Category, Category.id==Attribute.category_id)\
    		.filter(AttributePicture.language_code==language_code)\
    		.group_by(Category.name, Attribute.name)
   
    for a in query:
    	result[a.category_name][a.name] = a.file_names
    
    return jsonify(result)


@docstring_formatter(conf.PLATFORM_URL)
@apiv02_bp.route('/attributes/pictures/has/<uniqueid>', methods=['GET'])
def has_picture(uniqueid):
    """
    Retrieve attribute picture for specific attribute
    
    :param uniqueid: uniqueid of the attribute
    :type uniqueid: string
    
    
    **Example requests**:
     
     .. sourcecode:: html
         
         # get pictures for Foundation Type (uniqueid: foundationtype)
         GET {0}/api/v0.2/attributes/pictures/has/foundationtype
    """
    result = tree()
    
    picpath = conf.ATTRIBUTES_PICTURES_SITE_PATH
    query = db.session.query(AttributePicture.file_name).join(Attribute).filter(Attribute.uniqueid==uniqueid).first()
    
    if query:
        result = {uniqueid:[picpath + '/' + query[0]]}
    else:
        result = {uniqueid:[False]}
    print(query)
    return(jsonify(result))
    

@docstring_formatter(conf.PLATFORM_URL)    		
@apiv02_bp.route('/attributes/<attribute_name>', methods=['GET'])
def getattributes(attribute_name, safetext=False):
    """
    Retrieve available values for a given `attribute_name` 
    separated by semicolons
    
    :param attribute_name: uniqueid of an attribute name
    :type language_code: string
    
    **Example requests**:
     
     .. sourcecode:: html
         
         # get all values for attribute "Foor finish material" (uniqueid: floorfinishmaterial)
         GET {0}/api/v0.2/attributes/floorfinishmaterial
    """
    result= tree()
    
    attributes = Attribute.query.filter(Attribute.uniqueid==attribute_name).\
                                first().associated_values
    
    result[attribute_name] = ";".join([attribute.name for attribute in attributes])
    return jsonify(result)


@apiv02_bp.route('/translation', methods=['GET'])
def available_translations():
    #"""
    #Retrieve language codes of available translations 
    #"""
    result = tree()
    
    subquery = db.session.query(Translation.language_code).group_by(Translation.language_code).subquery()
    query = db.session.query(func.array_agg(subquery.c.language_code)).first()
    #for language in available_languages
    result["languages"]= query[0]
	
    return jsonify_utf8(result)


@apiv02_bp.route('/translation/<language_code>', methods=['GET'])
def translations(language_code=None):
    #"""
    #Retrieve translations for a given `language_code`
    #
    #:param language_code: language code 
    #:type language_code: string
    #"""
    result = tree()

    query = Translation.query.filter(Translation.language_code==language_code)
    phrases = query	
    for phrase in phrases:
    	result[phrase.original]=phrase.translated
    	
    return jsonify_utf8(result)


@docstring_formatter(conf.PLATFORM_URL)    	
@apiv02_bp.route('/shelters', methods=['GET'])
@apiv02_bp.route('/shelters/<int:shelter_id>', methods=['GET'])
def allshelters(shelter_id=None):
    """
    Retrieves shelters with all of their attributes and pictures.
    
    :param shelter_id: a unique shelter ID generated by the server 
    :type shelter_id: int
    
    :query format: 
        if set to ``prettytext``, 
        attribute names are retrieved as nicely formatted text 
        (Capital letters, special characters and spaces allowed)
    
    :query attribute:
        attribute name
    
    :query value: 
       attribute value
    
    :query q: 
        Full text search. Works in English language only.
        
    
    **Example requests**:
     
     .. sourcecode:: html
         
         # get all shelters
         GET {0}/api/v0.2/shelters
         
         # get shelter whith shelter ID 11
         GET {0}/api/v0.2/shelters/11
         
         # get all shelters which have attribute 'storeys' 
         GET {0}/api/v0.2/shelters?attribute=storeys
         
         # get all shelters which have 2 storeys
         GET {0}/api/v0.2/shelters?attribute=storeys&value=2
    """
    result = tree()
    
    picpath = os.path.relpath(conf.SHELTERS_PICTURES_SITE_PATH) 
    docpath = os.path.relpath(conf.SHELTERS_DOCUMENTS_SITE_PATH)
    pretty = False
    
    Supercategory = db.aliased(Category)
    
    querybase = db.session.query(Property.shelter_id, Category.name.label("category_name"), Supercategory.name.label("supercategory_name"), Attribute.name, Attribute.uniqueid, Attribute.type, func.string_agg(Value.name,';').label("value"))\
    		.join(Shelter, Shelter.id==Property.shelter_id)\
    		.join(Category, Category.id==Property.category_id)\
    		.join(Attribute, Attribute.id==Property.attribute_id)\
    		.join(Supercategory, Supercategory.id==Category.parent_id)\
    		.join(Association, Property.id==Association.property_id)\
    		.join(Value, Association.value_id==Value.id)\
    		.group_by(Property.shelter_id, Supercategory.name, Category.name, Attribute.name, Attribute.uniqueid, Attribute.type)
    
    picquerybase = db.session.query(ShelterPicture.shelter_id, ShelterPicture.file_name.label("filename"), ShelterPicture.is_main_picture, Category.name)\
    		.join(Category, Category.id == ShelterPicture.category_id)		
    
    catquery = db.session.query(Category.name).filter(Category.section_id != None)
    
    docquerybase = db.session.query(ShelterDocument.shelter_id, ShelterDocument.file_name.label("filename"), ShelterDocument.category_id, Category.name)\
    		.join(Category, Category.id == ShelterDocument.category_id)
    
    ##queries if no request arguments
    shelter_properties = querybase
    shelter_pictures = picquerybase
    shelter_documents = docquerybase
     
        	
    if shelter_id:
    	shelter_properties = querybase.filter(Property.shelter_id==shelter_id)
    	shelter_pictures = picquerybase.filter(ShelterPicture.shelter_id==shelter_id)
    	shelter_documents = docquerybase.filter(ShelterDocument.shelter_id==shelter_id)
    else:
    	#only query published shelters if no shelter_id supplied
    	shelter_properties = shelter_properties.filter(Shelter.is_published == True)
    
    
    if request.args.getlist('attribute'):
    	attribute = request.args.getlist('attribute')	
    	
    	subquery = db.session.query(Property.shelter_id)\
    			.join(Attribute, Attribute.id==Property.attribute_id)\
    			.filter(Attribute.uniqueid.in_(attribute))\
    			.group_by(Property.shelter_id)
    			
    	shelter_properties = shelter_properties.filter(subquery.subquery().c.shelter_id==Property.shelter_id)
    	shelter_pictures = shelter_pictures.filter(subquery.subquery().c.shelter_id==ShelterPicture.shelter_id)
    	shelter_documents = shelter_documents.filter(subquery.subquery().c.shelter_id==ShelterDocument.shelter_id)
    
    if request.args.getlist('value'):
    	value = request.args.getlist('value')
    	if not request.args.getlist('attribute'):
    		subquery = db.session.query(Property.shelter_id)\
    			.join(Attribute, Attribute.id==Property.attribute_id)\
    			.filter(Property.values.any(Value.name.in_(value)))\
    			.group_by(Property.shelter_id)
    	else:
    		subquery = subquery.filter(Property.values.any(Value.name.in_(value)))
    	
    	shelter_properties = shelter_properties.filter(subquery.subquery().c.shelter_id==Property.shelter_id)
    	shelter_pictures = shelter_pictures.filter(subquery.subquery().c.shelter_id==ShelterPicture.shelter_id)
    	shelter_documents = shelter_documents.filter(subquery.subquery().c.shelter_id==ShelterDocument.shelter_id)
    
    if request.args.get('q'):
    	attribute = request.args.get('q')
    	
    	shelter_properties = shelter_properties.join(Tsvector, Property.shelter_id==Tsvector.shelter_id).filter(Tsvector.lexeme.match(attribute))
    	shelter_pictures = shelter_pictures.join(Tsvector, ShelterPicture.shelter_id==Tsvector.shelter_id).filter(Tsvector.lexeme.match(attribute))
    	shelter_documents = shelter_documents.join(Tsvector, ShelterDocument.shelter_id==Tsvector.shelter_id).filter(Tsvector.lexeme.match(attribute))
    
    if request.args.get('format') == 'prettytext':
        pretty = True
    
    result = populate_dictree(shelter_properties, catquery, result, prettytext=pretty)
    populate_pictures(shelter_pictures, result, picpath)
    
    return jsonify(result)


@docstring_formatter(conf.PLATFORM_URL) 
@apiv02_bp.route('/shelters/latest', methods=['GET'])
@apiv02_bp.route('/shelters/latest/<int:count>', methods=['GET'])
def latestshelters(count=1):
    """
    Retrieves latest shelters (updates to existing shelters also count).
    Only retrieves shelters that have pictures. If no count parameter is supplied, the API
    retrieves the latest shelter.
    
    :param count: number of latest shelters to return
    :type count: int
    
    
    **Example requests**:
     
     .. sourcecode:: html
         
         # get latest shelter
         GET {0}/api/v0.2/shelters/latest
         
         # get the 3 latest shelters
         GET {0}/api/v0.2/shelters/latest/3
    """
    
    result = tree()
    pretty = False
    
    picpath = os.path.relpath(conf.SHELTERS_PICTURES_SITE_PATH)
    
    Supercategory = db.aliased(Category)
    
    subsubquery = db.session.query(ShelterPicture.shelter_id).filter(ShelterPicture.is_main_picture == True).subquery()
    subquery= db.session.query(Shelter)\
            .filter(Shelter.is_published == True)\
            .filter(Shelter.id.in_(subsubquery))\
            .order_by(desc(Shelter.updated_at))\
            .limit(count).subquery()
     
    
    querybase = db.session.query(subquery.c.id.label("shelter_id"), Category.name.label("category_name"), Supercategory.name.label("supercategory_name"), Attribute.name, Attribute.uniqueid, Attribute.type, func.string_agg(Value.name,';').label("value"))\
    		.join(Property, subquery.c.id==Property.shelter_id)\
    		.join(Category, Category.id==Property.category_id)\
    		.join(Attribute, Attribute.id==Property.attribute_id)\
    		.join(Supercategory, Supercategory.id==Category.parent_id)\
    		.join(Association, Property.id==Association.property_id)\
    		.join(Value, Association.value_id==Value.id)\
    		.order_by(desc(subquery.c.updated_at))\
    		.group_by(subquery.c.updated_at,subquery.c.id, Supercategory.name, Category.name, Attribute.name, Attribute.uniqueid,Attribute.type)
    
    
    picquerybase = db.session.query(ShelterPicture.shelter_id, ShelterPicture.file_name.label("filename"), ShelterPicture.is_main_picture, Category.name)\
    		.join(Category, Category.id == ShelterPicture.category_id)		

    catquery = db.session.query(Category.name).filter(Category.section_id != None)
    
    ##queries if no request arguments
    shelter_properties = querybase
    shelter_pictures = picquerybase
        	
    
    if request.args.get('format') == 'prettytext':
        pretty = True
        
    result = populate_dictree(shelter_properties, catquery, result, prettytext=pretty)
    populate_pictures(shelter_pictures, result, picpath)
    
    
    return jsonify(result)
