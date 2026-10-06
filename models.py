from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

db = SQLAlchemy()


# ============================================================
# USER MODEL
# ============================================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    roll_number = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    gender = db.Column(
        db.String(20),
        nullable=True
    )

    department = db.Column(
        db.String(100),
        nullable=True
    )

    year = db.Column(
        db.Integer,
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    role = db.Column(
        db.String(30),
        default="student"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    # --------------------------------------------------------
    # SET PASSWORD
    # --------------------------------------------------------

    def set_password(self, password):

        self.password = generate_password_hash(
            password
        )


    # --------------------------------------------------------
    # CHECK PASSWORD
    # --------------------------------------------------------

    def check_password(self, password):

        return check_password_hash(
            self.password,
            password
        )


# ============================================================
# ROOM MODEL
# ============================================================

class Room(db.Model):

    __tablename__ = "rooms"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    room_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    hostel = db.Column(
        db.String(100),
        nullable=True
    )

    floor = db.Column(
        db.Integer,
        nullable=True
    )

    gender = db.Column(
        db.String(20),
        nullable=True
    )

    capacity = db.Column(
        db.Integer,
        default=1
    )

    occupied = db.Column(
        db.Integer,
        default=0
    )

    status = db.Column(
        db.String(30),
        default="available"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ============================================================
# ROOM ALLOCATION MODEL
# ============================================================

class RoomAllocation(db.Model):

    __tablename__ = "room_allocations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id"),
        nullable=False
    )

    allocation_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(30),
        default="active"
    )

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )

    room = db.relationship(
        "Room",
        foreign_keys=[room_id]
    )


# ============================================================
# ROOM SWAP MODEL
# ============================================================

class RoomSwap(db.Model):

    __tablename__ = "room_swaps"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    requester_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    target_student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    requester = db.relationship(
        "User",
        foreign_keys=[requester_id]
    )

    target_student = db.relationship(
        "User",
        foreign_keys=[target_student_id]
    )


# ============================================================
# COMPLAINT MODEL
# ============================================================

class Complaint(db.Model):

    __tablename__ = "complaints"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    priority = db.Column(
        db.String(30),
        default="Medium"
    )

    room_number = db.Column(
        db.String(50),
        nullable=True
    )

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )


# ============================================================
# FEE MODEL
# ============================================================

class Fee(db.Model):

    __tablename__ = "fees"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    fee_type = db.Column(
        db.String(100),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    due_date = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )


# ============================================================
# PAYMENT MODEL
# ============================================================

class Payment(db.Model):

    __tablename__ = "payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    fee_id = db.Column(
        db.Integer,
        db.ForeignKey("fees.id"),
        nullable=True
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    transaction_id = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    payment_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(50),
        default="Success"
    )

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )

    fee = db.relationship(
        "Fee",
        foreign_keys=[fee_id]
    )


# ============================================================
# LEAVE REQUEST MODEL
# ============================================================

class LeaveRequest(db.Model):

    __tablename__ = "leave_requests"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    from_date = db.Column(
        db.Date,
        nullable=False
    )

    to_date = db.Column(
        db.Date,
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )


# ============================================================
# MESSAGE MODEL
# ============================================================

class Message(db.Model):

    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id]
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id]
    )


# ============================================================
# ANNOUNCEMENT MODEL
# ============================================================

class Announcement(db.Model):

    __tablename__ = "announcements"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by]
    )


# ============================================================
# HOSTEL NOTICE MODEL
# ============================================================

class HostelNotice(db.Model):

    __tablename__ = "hostel_notices"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by]
    )