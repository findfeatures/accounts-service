from marshmallow import Schema, fields


class CreateUserRequest(Schema):
    email = fields.String(required=True)
    display_name = fields.String(required=True)
    password = fields.String(required=True)


class CreateProjectRequest(Schema):
    name = fields.String(required=True)


class CreateStripeCheckoutSessionRequest(Schema):
    user_id = fields.Integer(required=True)
    email = fields.String(required=True)
    plan = fields.String(required=True)
    success_url = fields.String(required=True)
    cancel_url = fields.String(required=True)
    project_id = fields.Integer(required=True)
