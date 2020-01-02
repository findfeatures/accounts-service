from marshmallow import Schema, fields


class CreateUserRequest(Schema):
    email = fields.String(required=True)
    display_name = fields.String(required=True)
    password = fields.String(required=True)


class CreateProjectRequest(Schema):
    name = fields.String(required=True)
