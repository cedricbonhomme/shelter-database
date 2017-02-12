/**
 * CREATE-SHELTER : create-shelter.js
 */
 
function create_shelter (name_of_shelter, country_value_id, country_name, callback) {
    new_shelter_dict = {} // the id of the shelter's owner is controlled by a POST preprocessor function
    $.ajax({
        type: 'POST',
        url: '/api/shelter',
        contentType: "application/json",
        dataType: "json",
        data: JSON.stringify(new_shelter_dict),
        success: function (new_shelter) {
            // creation of the shelter OK
 
            // Creation of the property: Name of shelter
            var filters = [{"name":"name","op":"eq","val":"Name of shelter"}];
            $.ajax({
                type: 'GET',
                url: '/api/attribute',
                contentType: "application/json",
                dataType: "json",
                data: {"q": JSON.stringify({"filters": filters})},
                success: function(result) {
                    attribute_id = result.objects[0].id;
                    category_id = result.objects[0].category_id;
                    _new_property = {
                        shelter_id: new_shelter.id,
                        attribute_id: attribute_id,
                        category_id: category_id,
                        values : [{
                            name: name_of_shelter,
                            attribute_id: attribute_id
                        }]
                    }
                    $.ajax({
                        type: 'POST',
                        url: '/api/property',
                        contentType: "application/json",
                        dataType: "json",
                        data: JSON.stringify(_new_property),
                        success: function (result) {
                            // Creation of the property: Country
                            var filters = [{"name":"name","op":"eq","val":"Country"}];
                            $.ajax({
                                type: 'GET',
                                url: '/api/attribute',
                                contentType: "application/json",
                                dataType: "json",
                                data: {"q": JSON.stringify({"filters": filters})},
                                success: function(result) {
                                    attribute_id = result.objects[0].id;
                                    category_id = result.objects[0].category_id;
                                    _new_property = {
                                        shelter_id: new_shelter.id,
                                        attribute_id: attribute_id,
                                        category_id: category_id,
                                        values : [{
                                            id: country_value_id
                                        }]
                                    }
                                    $.ajax({
                                        type: 'POST',
                                        url: '/api/property',
                                        contentType: "application/json",
                                        dataType: "json",
                                        data: JSON.stringify(_new_property),
                                        success: function (result) {
                                            // Creation of the property: ID
                                            var filters = [{"name":"name","op":"eq","val":"ID"}];
                                            $.ajax({
                                                type: 'GET',
                                                url: '/api/attribute',
                                                contentType: "application/json",
                                                dataType: "json",
                                                data: {"q": JSON.stringify({"filters": filters})},
                                                success: function(result) {
                                                    _new_property = {
                                                        shelter_id: new_shelter.id,
                                                        attribute_id: result.objects[0].id,
                                                        category_id: result.objects[0].category_id,
                                                        values : [{
                                                            name: getCountryCode(country_name)+new_shelter.id,
                                                            attribute_id: result.objects[0].id
                                                        }]
                                                    }
                                                    $.ajax({
                                                        type: 'POST',
                                                        url: '/api/property',
                                                        contentType: "application/json",
                                                        dataType: "json",
                                                        data: JSON.stringify(_new_property),
                                                        success: function (result) {
															if(callback != null) {
																callback(true, new_shelter.id);                
															}
                                                            //window.location = '/shelter/' + new_shelter.id + '/general-Information';
                                                        },
                                                        error: function(XMLHttpRequest, textStatus, errorThrown){
															// invoke the callback function here
															if(callback != null)  {
																callback(false, errorThrown);
															}
                                                        }
                                                    });
                                                },
                                                error: function(XMLHttpRequest, textStatus, errorThrown){
                                                    //alert(errorThrown);
                                                }
                                            })











                                        },
                                        error: function(XMLHttpRequest, textStatus, errorThrown){
                                            console.log(errorThrown);
                                        }
                                    });
                                },
                                error: function(XMLHttpRequest, textStatus, errorThrown){
                                    //alert(errorThrown);
                                }
                            })
















                        },
                        error: function(XMLHttpRequest, textStatus, errorThrown){
                            console.log(errorThrown);
                        }
                    });
                },
                error: function(XMLHttpRequest, textStatus, errorThrown){
                    //alert(errorThrown);
                }
            })
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            console.log(errorThrown);
        }
    }); // end POST api Shelter
}
