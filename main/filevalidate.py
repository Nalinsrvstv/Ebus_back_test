import jsonschema

# Define the schema
schema = {
 "depot":{ 
     "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "ID": {"type": "string"},
      "age": {"type": "integer"}
    }
    ,
      "required": ["ID","age"]}
  }
}



def Validate(data,type):
    # Validate the data
    validator = jsonschema.Draft4Validator(schema[type])
    errors = validator.validate(data)
    return errors