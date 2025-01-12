# app/schemas.py
from app import ma
from app.models import Doctor, Chamber, Schedule, User, Visit
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class DoctorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Doctor

    id = ma.auto_field()
    name = ma.auto_field()
    contact_number = ma.auto_field()
    specializations = ma.auto_field()
    hospital_affiliations = ma.auto_field()
    degrees = ma.auto_field()
    chambers = ma.Nested('ChamberSchema', many=True, exclude=('doctors',))


class ScheduleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Schedule

    id = ma.auto_field()
    time_slots = ma.auto_field()


class ChamberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Chamber

    id = ma.auto_field()
    location = ma.auto_field()
    schedule = ma.Nested(ScheduleSchema)
    doctors = ma.Nested(DoctorSchema, many=True, exclude=('chambers',))

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User

    id = ma.auto_field()
    name = ma.auto_field()
    contact_number = ma.auto_field()
    email = ma.auto_field()
    address = ma.auto_field()
    bkash_number = ma.auto_field()
    identifying_document_id = ma.auto_field()
    precondition_keywords = ma.auto_field()
    is_primary_user = ma.auto_field()

    # Exclude sensitive fields and circular references
    dependents = ma.Nested('UserSchema', many=True, exclude=('dependents',))


class VisitSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Visit

    id = ma.auto_field()
    chamber_id = ma.auto_field()
    doctor_id = ma.auto_field()
    booking_user_id = ma.auto_field()
    patient_user_id = ma.auto_field()
    visit_document_ids = ma.auto_field()
    booking_remarks = ma.auto_field()
    booking_time = ma.auto_field()
    appointment_time = ma.auto_field()
    visit_end_time = ma.auto_field()
    visit_cost = ma.auto_field()
    visit_status = ma.auto_field()
    cancel_reason = ma.auto_field()

    doctor = ma.Nested(DoctorSchema, exclude=('chambers',))
    chamber = ma.Nested(ChamberSchema, exclude=('doctors',))


class VisitDocumentSchema(ma.Schema):
    id = ma.String()
    type = ma.String()
    upload_time = ma.DateTime()


