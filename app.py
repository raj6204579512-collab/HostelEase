from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from functools import wraps
from datetime import datetime, date

from models import (
    db,
    User,
    Room,
    RoomAllocation,
    RoomSwap,
    Complaint,
    Fee,
    Payment,
    LeaveRequest,
    Message,
    Announcement,
    HostelNotice
)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "hostelease-secret-key-2026"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hostelease.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_date(date_value):
    """
    Convert HTML date string YYYY-MM-DD
    into Python date object.
    """

    if not date_value:
        return None

    try:
        return datetime.strptime(
            date_value,
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError):
        return None


def parse_float(value):
    """
    Safely convert value to float.
    """

    try:
        return float(value)

    except (ValueError, TypeError):
        return 0.0


def get_student():

    student_id = session.get("student_id")

    if not student_id:
        return None

    return User.query.filter_by(
        id=student_id,
        role="student"
    ).first()


def get_admin():

    admin_id = session.get("admin_id")

    if not admin_id:
        return None

    return User.query.filter_by(
        id=admin_id,
        role="admin"
    ).first()


# ============================================================
# LOGIN DECORATORS
# ============================================================

def student_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        student = get_student()

        if not student:

            flash(
                "Please login as a student first.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return wrapper


def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        admin = get_admin()

        if not admin:

            flash(
                "Please login as administrator first.",
                "error"
            )

            return redirect(
                url_for("admin_login")
            )

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    # These values are optional for the homepage.
    # The page will still work if it does not use them.
    try:
        total_students = User.query.filter_by(
            role="student"
        ).count()

        total_rooms = Room.query.count()

        total_notices = HostelNotice.query.count()

    except Exception:
        total_students = 0
        total_rooms = 0
        total_notices = 0

    return render_template(
        "index.html",
        total_students=total_students,
        total_rooms=total_rooms,
        total_notices=total_notices
    )


# ============================================================
# STUDENT REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        roll_number = request.form.get(
            "roll_number",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        department = request.form.get(
            "department",
            ""
        ).strip()

        year_value = request.form.get(
            "year",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        # -------------------------------
        # VALIDATION
        # -------------------------------

        if not name:

            flash(
                "Please enter your name.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        if not roll_number:

            flash(
                "Please enter enrollment number.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        if not email:

            flash(
                "Please enter email.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        if not password:

            flash(
                "Please enter password.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        # -------------------------------
        # CHECK EMAIL
        # -------------------------------

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash(
                "Email already registered.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        # -------------------------------
        # CHECK ROLL NUMBER
        # -------------------------------

        existing_roll = User.query.filter_by(
            roll_number=roll_number
        ).first()

        if existing_roll:

            flash(
                "Enrollment number already registered.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        # -------------------------------
        # YEAR
        # -------------------------------

        year = None

        if year_value:

            try:
                year = int(year_value)

            except ValueError:
                year = None


        # -------------------------------
        # CREATE STUDENT
        # -------------------------------

        student = User(
            name=name,
            roll_number=roll_number,
            email=email,
            phone=phone,
            gender=gender,
            department=department,
            year=year,
            role="student"
        )

        student.set_password(password)

        db.session.add(student)

        db.session.commit()


        flash(
            "Account created successfully! Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


# ============================================================
# STUDENT LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        roll_number = request.form.get(
            "roll_number",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        student = User.query.filter_by(
            roll_number=roll_number,
            role="student"
        ).first()


        if student and student.check_password(password):

            session.clear()

            session["student_id"] = student.id

            session["student_name"] = student.name

            session["role"] = "student"

            return redirect(
                url_for("student_dashboard")
            )


        flash(
            "Invalid enrollment number or password.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "login.html"
    )


# ============================================================
# STUDENT LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("home")
    )
# ============================================================
# STUDENT LOGOUT ALIAS
# ============================================================

@app.route("/student/logout")
def student_logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# ============================================================
# STUDENT PROFILE
# ============================================================

@app.route(
    "/student/profile",
    methods=["GET", "POST"]
)
@student_required
def student_profile():

    student = get_student()

    # ========================================================
    # POST REQUEST
    # ========================================================

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        ).strip()


        # ====================================================
        # UPDATE PROFILE
        # ====================================================

        if action == "update_profile":

            name = request.form.get(
                "name",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip().lower()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            gender = request.form.get(
                "gender",
                ""
            ).strip()

            department = request.form.get(
                "department",
                ""
            ).strip()

            year_value = request.form.get(
                "year",
                ""
            ).strip()


            # -----------------------------
            # VALIDATION
            # -----------------------------

            if not name:

                flash(
                    "Please enter your full name.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            if not email:

                flash(
                    "Please enter your email.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            # -----------------------------
            # CHECK EMAIL
            # -----------------------------

            existing_email = User.query.filter(
                User.email == email,
                User.id != student.id
            ).first()


            if existing_email:

                flash(
                    "This email is already being used.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            # -----------------------------
            # UPDATE DATABASE
            # -----------------------------

            try:

                student.name = name

                student.email = email

                student.phone = phone

                student.gender = gender

                student.department = department

                if year_value:

                    student.year = int(
                        year_value
                    )

                else:

                    student.year = None


                db.session.commit()


                # Update session name

                session["student_name"] = (
                    student.name
                )


                flash(
                    "Profile updated successfully!",
                    "success"
                )


            except Exception as e:

                db.session.rollback()

                print(
                    "STUDENT PROFILE UPDATE ERROR:",
                    e
                )

                flash(
                    "Unable to update profile.",
                    "error"
                )


            return redirect(
                url_for("student_profile")
            )


        # ====================================================
        # CHANGE PASSWORD
        # ====================================================

        if action == "change_password":

            current_password = request.form.get(
                "current_password",
                ""
            )

            new_password = request.form.get(
                "new_password",
                ""
            )

            confirm_password = request.form.get(
                "confirm_password",
                ""
            )


            # -----------------------------
            # CURRENT PASSWORD
            # -----------------------------

            if not current_password:

                flash(
                    "Please enter your current password.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            # -----------------------------
            # CHECK CURRENT PASSWORD
            # -----------------------------

            if not student.check_password(
                current_password
            ):

                flash(
                    "Current password is incorrect.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            # -----------------------------
            # NEW PASSWORD
            # -----------------------------

            if not new_password:

                flash(
                    "Please enter a new password.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            if len(new_password) < 6:

                flash(
                    "New password must contain at least 6 characters.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            # -----------------------------
            # CONFIRM PASSWORD
            # -----------------------------

            if new_password != confirm_password:

                flash(
                    "New passwords do not match.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            # -----------------------------
            # SAVE NEW PASSWORD
            # -----------------------------

            try:

                student.set_password(
                    new_password
                )

                db.session.commit()


                flash(
                    "Password changed successfully!",
                    "success"
                )


            except Exception as e:

                db.session.rollback()

                print(
                    "STUDENT PASSWORD UPDATE ERROR:",
                    e
                )

                flash(
                    "Unable to change password.",
                    "error"
                )


            return redirect(
                url_for("student_profile")
            )


        # ====================================================
        # INVALID ACTION
        # ====================================================

        flash(
            "Invalid profile action.",
            "error"
        )

        return redirect(
            url_for("student_profile")
        )


    # ========================================================
    # GET REQUEST
    # ========================================================

    return render_template(
        "student-profile.html",
        student=student
    )
# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/student/dashboard")
@student_required
def student_dashboard():

    student = get_student()

    current_allocation = RoomAllocation.query.filter(
        RoomAllocation.student_id == student.id,
        db.func.lower(RoomAllocation.status) == "active"
    ).first()

    complaints = Complaint.query.filter_by(
        student_id=student.id
    ).order_by(
        Complaint.id.desc()
    ).all()

    fees = Fee.query.filter_by(
        student_id=student.id
    ).order_by(
        Fee.id.desc()
    ).all()

    leave_requests = LeaveRequest.query.filter_by(
        student_id=student.id
    ).order_by(
        LeaveRequest.id.desc()
    ).all()

    announcements = Announcement.query.order_by(
        Announcement.id.desc()
    ).limit(5).all()

    notices = HostelNotice.query.order_by(
        HostelNotice.id.desc()
    ).limit(5).all()

    swap_requests = RoomSwap.query.filter(
        (RoomSwap.requester_id == student.id)
        |
        (RoomSwap.target_student_id == student.id)
    ).order_by(
        RoomSwap.id.desc()
    ).all()

    return render_template(
        "student-dashboard.html",
        student=student,
        current_allocation=current_allocation,
        allocation=current_allocation,
        complaints=complaints,
        fees=fees,
        leave_requests=leave_requests,
        announcements=announcements,
        notices=notices,
        swap_requests=swap_requests
    )


# ============================================================
# STUDENT ROOM SWAP
# ============================================================

@app.route(
    "/student/room-swap",
    methods=["GET", "POST"]
)
@student_required
def student_room_swap():

    student = get_student()


    current_allocation = RoomAllocation.query.filter(
        RoomAllocation.student_id == student.id,
        db.func.lower(RoomAllocation.status) == "active"
    ).first()


    if request.method == "POST":

        target_student_id = request.form.get(
            "target_student_id",
            type=int
        )

        message = request.form.get(
            "message",
            ""
        ).strip()


        if not current_allocation:

            flash(
                "You do not have an active room allocation.",
                "error"
            )

            return redirect(
                url_for("student_room_swap")
            )


        if not target_student_id:

            flash(
                "Please select a student.",
                "error"
            )

            return redirect(
                url_for("student_room_swap")
            )


        if target_student_id == student.id:

            flash(
                "You cannot swap your room with yourself.",
                "error"
            )

            return redirect(
                url_for("student_room_swap")
            )


        if not message:

            flash(
                "Please enter a reason for the swap.",
                "error"
            )

            return redirect(
                url_for("student_room_swap")
            )


        target_student = User.query.filter_by(
            id=target_student_id,
            role="student"
        ).first()


        if not target_student:

            flash(
                "Selected student was not found.",
                "error"
            )

            return redirect(
                url_for("student_room_swap")
            )


        target_allocation = RoomAllocation.query.filter(
            RoomAllocation.student_id == target_student.id,
            db.func.lower(RoomAllocation.status) == "active"
        ).first()


        if not target_allocation:

            flash(
                "Selected student does not have an active room.",
                "error"
            )

            return redirect(
                url_for("student_room_swap")
            )


        existing_swap = RoomSwap.query.filter(
            RoomSwap.requester_id == student.id,
            RoomSwap.target_student_id == target_student.id,
            db.func.lower(RoomSwap.status) == "pending"
        ).first()


        if existing_swap:

            flash(
                "You already have a pending request with this student.",
                "error"
            )

            return redirect(
                url_for("student_room_swap")
            )


        swap = RoomSwap(
            requester_id=student.id,
            target_student_id=target_student.id,
            message=message,
            status="pending"
        )


        db.session.add(swap)

        db.session.commit()


        flash(
            "Room swap request sent successfully!",
            "success"
        )

        return redirect(
            url_for("student_room_swap")
        )


    # All other students
    all_students = User.query.filter(
        User.role == "student",
        User.id != student.id
    ).order_by(
        User.name.asc()
    ).all()


    available_students = []


    for other_student in all_students:

        other_allocation = RoomAllocation.query.filter(
            RoomAllocation.student_id == other_student.id,
            db.func.lower(RoomAllocation.status) == "active"
        ).first()


        if other_allocation:

            other_student.active_allocation = other_allocation

            available_students.append(
                other_student
            )


    my_requests = RoomSwap.query.filter(
        (
            RoomSwap.requester_id == student.id
        )
        |
        (
            RoomSwap.target_student_id == student.id
        )
    ).order_by(
        RoomSwap.id.desc()
    ).all()


    return render_template(
        "student-room-swap.html",
        student=student,
        current_allocation=current_allocation,
        available_students=available_students,
        other_students=available_students,
        students=available_students,
        my_requests=my_requests,
        swap_requests=my_requests
    )


# ============================================================
# ADMIN REGISTER
# ============================================================

@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        admin_key = request.form.get("admin_key", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not name:
            flash(
                "Please enter administrator name.",
                "error"
            )
            return redirect(
                url_for("admin_register")
            )

        if not email:
            flash(
                "Please enter administrator email.",
                "error"
            )
            return redirect(
                url_for("admin_register")
            )

        if not admin_key:
            flash(
                "Please enter admin registration key.",
                "error"
            )
            return redirect(
                url_for("admin_register")
            )

        if not password:
            flash(
                "Please enter a password.",
                "error"
            )
            return redirect(
                url_for("admin_register")
            )

        if len(password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "error"
            )
            return redirect(
                url_for("admin_register")
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "error"
            )
            return redirect(
                url_for("admin_register")
            )

        # -----------------------------
        # ADMIN REGISTRATION KEY
        # -----------------------------

        if admin_key != "HOSTELADMIN2026":
            flash(
                "Invalid admin registration key.",
                "error"
            )
            return redirect(
                url_for("admin_register")
            )

        # -----------------------------
        # CHECK EXISTING EMAIL
        # -----------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash(
                "An account with this email already exists.",
                "error"
            )
            return redirect(
                url_for("admin_register")
            )

        # -----------------------------
        # CREATE ADMIN
        # -----------------------------

        try:

            admin_roll = (
                "ADMIN-" +
                datetime.now().strftime("%Y%m%d%H%M%S")
            )

            admin = User(
                name=name,
                roll_number=admin_roll,
                email=email,
                phone=phone,
                role="admin"
            )

            admin.set_password(password)

            db.session.add(admin)

            db.session.commit()

            # -----------------------------
            # SUCCESS
            # -----------------------------

            flash(
                "Admin account created successfully. Please login.",
                "success"
            )

            # IMPORTANT:
            # Registration ke baad Admin Login par jayega
            return redirect(
                url_for("admin_login")
            )

        except Exception as e:

            db.session.rollback()

            print(
                "ADMIN REGISTRATION ERROR:",
                e
            )

            flash(
                "Something went wrong while creating the admin account.",
                "error"
            )

            return redirect(
                url_for("admin_register")
            )

    # GET request
    return render_template(
        "admin-register.html"
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        admin = User.query.filter_by(
            email=email,
            role="admin"
        ).first()


        if admin and admin.check_password(password):

            session.clear()

            session["admin_id"] = admin.id

            session["admin_name"] = admin.name

            session["role"] = "admin"


            return redirect(
                url_for("admin_dashboard")
            )


        flash(
            "Invalid admin email or password.",
            "error"
        )

        return redirect(
            url_for("admin_login")
        )


    return render_template(
        "admin-login.html"
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
@admin_required
def admin_logout():

    session.clear()

    flash(
        "Admin logged out successfully.",
        "success"
    )

    return redirect(
        url_for("admin_login")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route(
    "/admin/dashboard"
)
@admin_required
def admin_dashboard():

    admin = get_admin()

    # --------------------------------------------------------
    # STUDENTS
    # --------------------------------------------------------

    total_students = User.query.filter_by(
        role="student"
    ).count()


    # --------------------------------------------------------
    # ROOMS
    # --------------------------------------------------------

    total_rooms = Room.query.count()


    # --------------------------------------------------------
    # ACTIVE ROOM ALLOCATIONS
    # --------------------------------------------------------

    active_allocations = RoomAllocation.query.filter(
        db.func.lower(RoomAllocation.status) == "active"
    ).count()


    # --------------------------------------------------------
    # AVAILABLE ROOMS
    # --------------------------------------------------------

    available_rooms = Room.query.filter(
        db.func.lower(Room.status) == "available"
    ).count()


    # --------------------------------------------------------
    # PENDING COMPLAINTS
    # --------------------------------------------------------

    pending_complaints = Complaint.query.filter(
        db.func.lower(Complaint.status) == "pending"
    ).count()


    # --------------------------------------------------------
    # PENDING FEES
    # --------------------------------------------------------

    pending_fees = Fee.query.filter(
        db.func.lower(Fee.status) == "pending"
    ).count()


    # --------------------------------------------------------
    # PENDING LEAVE REQUESTS
    # --------------------------------------------------------

    pending_leave_requests = LeaveRequest.query.filter(
        db.func.lower(LeaveRequest.status) == "pending"
    ).count()


    # --------------------------------------------------------
    # PENDING ROOM SWAPS
    # --------------------------------------------------------

    pending_swaps = RoomSwap.query.filter(
        db.func.lower(RoomSwap.status) == "pending"
    ).count()


    # --------------------------------------------------------
    # ANNOUNCEMENTS
    # --------------------------------------------------------

    total_announcements = Announcement.query.count()


    # --------------------------------------------------------
    # MESSAGES
    # --------------------------------------------------------

    total_messages = Message.query.count()


    # --------------------------------------------------------
    # RECENT STUDENTS
    # --------------------------------------------------------

    recent_students = User.query.filter_by(
        role="student"
    ).order_by(
        User.id.desc()
    ).limit(5).all()


    # --------------------------------------------------------
    # RECENT COMPLAINTS
    # --------------------------------------------------------

    recent_complaints = Complaint.query.order_by(
        Complaint.id.desc()
    ).limit(5).all()


    # --------------------------------------------------------
    # RECENT PAYMENTS
    # --------------------------------------------------------

    recent_payments = Payment.query.order_by(
        Payment.id.desc()
    ).limit(5).all()


    # --------------------------------------------------------
    # RECENT LEAVE REQUESTS
    # --------------------------------------------------------

    recent_leave_requests = LeaveRequest.query.order_by(
        LeaveRequest.id.desc()
    ).limit(5).all()


    return render_template(
        "admin-dashboard.html",

        admin=admin,

        total_students=total_students,

        total_rooms=total_rooms,

        active_allocations=active_allocations,

        available_rooms=available_rooms,

        pending_complaints=pending_complaints,

        pending_fees=pending_fees,

        pending_leave_requests=pending_leave_requests,

        pending_swaps=pending_swaps,

        total_announcements=total_announcements,

        total_messages=total_messages,

        recent_students=recent_students,

        recent_complaints=recent_complaints,

        recent_payments=recent_payments,

        recent_leave_requests=recent_leave_requests
    )


# ============================================================
# ADMIN STUDENTS
# ============================================================

@app.route(
    "/admin/students"
)
@admin_required
def admin_students():

    admin = get_admin()

    students = User.query.filter_by(
        role="student"
    ).order_by(
        User.id.desc()
    ).all()


    student_data = []


    for student in students:

        allocation = RoomAllocation.query.filter(
            RoomAllocation.student_id == student.id,
            db.func.lower(RoomAllocation.status) == "active"
        ).first()


        student_data.append({
            "student": student,
            "allocation": allocation
        })


    return render_template(
        "admin-students.html",
        admin=admin,
        students=students,
        student_data=student_data
    )


# ============================================================
# ADMIN ROOMS
# ============================================================

@app.route(
    "/admin/rooms",
    methods=["GET", "POST"]
)
@admin_required
def admin_rooms():

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        ).strip()


        # ----------------------------------------------------
        # ADD ROOM
        # ----------------------------------------------------

        if action == "add_room":

            room_number = request.form.get(
                "room_number",
                ""
            ).strip()

            hostel = request.form.get(
                "hostel",
                ""
            ).strip()

            floor = request.form.get(
                "floor",
                ""
            ).strip()

            gender = request.form.get(
                "gender",
                ""
            ).strip()

            capacity = request.form.get(
                "capacity",
                type=int
            )


            if not room_number:

                flash(
                    "Please enter room number.",
                    "error"
                )

                return redirect(
                    url_for("admin_rooms")
                )


            if not hostel:

                flash(
                    "Please enter hostel name.",
                    "error"
                )

                return redirect(
                    url_for("admin_rooms")
                )


            if not capacity or capacity <= 0:

                flash(
                    "Please enter a valid room capacity.",
                    "error"
                )

                return redirect(
                    url_for("admin_rooms")
                )


            existing_room = Room.query.filter_by(
                room_number=room_number
            ).first()


            if existing_room:

                flash(
                    "Room number already exists.",
                    "error"
                )

                return redirect(
                    url_for("admin_rooms")
                )


            room = Room(
                room_number=room_number,
                hostel=hostel,
                floor=floor,
                gender=gender,
                capacity=capacity,
                occupied=0,
                status="Available"
            )


            db.session.add(room)

            db.session.commit()


            flash(
                "Room added successfully!",
                "success"
            )


            return redirect(
                url_for("admin_rooms")
            )


        # ----------------------------------------------------
        # DELETE ROOM
        # ----------------------------------------------------

        if action == "delete_room":

            room_id = request.form.get(
                "room_id",
                type=int
            )


            room = Room.query.get(
                room_id
            )


            if not room:

                flash(
                    "Room not found.",
                    "error"
                )

                return redirect(
                    url_for("admin_rooms")
                )


            allocation_exists = RoomAllocation.query.filter(
                RoomAllocation.room_id == room.id,
                db.func.lower(RoomAllocation.status) == "active"
            ).first()


            if allocation_exists:

                flash(
                    "Cannot delete a room with an active allocation.",
                    "error"
                )

                return redirect(
                    url_for("admin_rooms")
                )


            db.session.delete(room)

            db.session.commit()


            flash(
                "Room deleted successfully!",
                "success"
            )


            return redirect(
                url_for("admin_rooms")
            )


    rooms = Room.query.order_by(
        Room.id.desc()
    ).all()


    return render_template(
        "admin-rooms.html",
        rooms=rooms
    )


# ============================================================
# ADMIN ROOM ALLOCATION
# ============================================================

@app.route(
    "/admin/room-allocation",
    methods=["GET", "POST"]
)
@admin_required
def admin_room_allocation():

    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            type=int
        )

        room_id = request.form.get(
            "room_id",
            type=int
        )


        if not student_id:

            flash(
                "Please select a student.",
                "error"
            )

            return redirect(
                url_for("admin_room_allocation")
            )


        if not room_id:

            flash(
                "Please select a room.",
                "error"
            )

            return redirect(
                url_for("admin_room_allocation")
            )


        student = User.query.filter_by(
            id=student_id,
            role="student"
        ).first()


        if not student:

            flash(
                "Student not found.",
                "error"
            )

            return redirect(
                url_for("admin_room_allocation")
            )


        room = Room.query.get(
            room_id
        )


        if not room:

            flash(
                "Room not found.",
                "error"
            )

            return redirect(
                url_for("admin_room_allocation")
            )


        existing_allocation = RoomAllocation.query.filter(
            RoomAllocation.student_id == student.id,
            db.func.lower(RoomAllocation.status) == "active"
        ).first()


        if existing_allocation:

            flash(
                "This student already has an active room.",
                "error"
            )

            return redirect(
                url_for("admin_room_allocation")
            )


        if room.occupied >= room.capacity:

            flash(
                "This room is already full.",
                "error"
            )

            return redirect(
                url_for("admin_room_allocation")
            )


        allocation = RoomAllocation(
            student_id=student.id,
            room_id=room.id,
            allocation_date=date.today(),
            status="Active"
        )


        room.occupied = (
            room.occupied + 1
        )


        if room.occupied >= room.capacity:

            room.status = "Full"

        else:

            room.status = "Available"


        db.session.add(
            allocation
        )

        db.session.commit()


        flash(
            "Room allocated successfully!",
            "success"
        )


        return redirect(
            url_for("admin_room_allocation")
        )


    students = User.query.filter_by(
        role="student"
    ).order_by(
        User.name.asc()
    ).all()


    rooms = Room.query.order_by(
        Room.room_number.asc()
    ).all()


    allocations = RoomAllocation.query.order_by(
        RoomAllocation.id.desc()
    ).all()


    return render_template(
        "admin-room-allocation.html",
        students=students,
        rooms=rooms,
        allocations=allocations
    )
# ============================================================
# ADMIN ROOM SWAPS
# ============================================================

@app.route(
    "/admin/room-swaps"
)
@admin_required
def admin_room_swaps():

    swaps = RoomSwap.query.order_by(
        RoomSwap.id.desc()
    ).all()


    return render_template(
        "admin-room-swaps.html",
        swaps=swaps,
        swap_requests=swaps
    )


# ============================================================
# APPROVE ROOM SWAP
# ============================================================

@app.route(
    "/admin/room-swap/<int:swap_id>/approve",
    methods=["POST"]
)
@admin_required
def approve_room_swap(swap_id):

    swap = RoomSwap.query.get(
        swap_id
    )


    if not swap:

        flash(
            "Swap request not found.",
            "error"
        )

        return redirect(
            url_for("admin_room_swaps")
        )


    if str(swap.status).lower() != "pending":

        flash(
            "This request has already been processed.",
            "error"
        )

        return redirect(
            url_for("admin_room_swaps")
        )


    requester_allocation = RoomAllocation.query.filter(
        RoomAllocation.student_id == swap.requester_id,
        db.func.lower(RoomAllocation.status) == "active"
    ).first()


    target_allocation = RoomAllocation.query.filter(
        RoomAllocation.student_id == swap.target_student_id,
        db.func.lower(RoomAllocation.status) == "active"
    ).first()


    if not requester_allocation:

        flash(
            "Requester room allocation not found.",
            "error"
        )

        return redirect(
            url_for("admin_room_swaps")
        )


    if not target_allocation:

        flash(
            "Target student room allocation not found.",
            "error"
        )

        return redirect(
            url_for("admin_room_swaps")
        )


    requester_room = requester_allocation.room_id

    target_room = target_allocation.room_id


    requester_allocation.room_id = target_room

    target_allocation.room_id = requester_room


    swap.status = "approved"


    db.session.commit()


    flash(
        "Room swap approved successfully!",
        "success"
    )


    return redirect(
        url_for("admin_room_swaps")
    )


# ============================================================
# REJECT ROOM SWAP
# ============================================================

@app.route(
    "/admin/room-swap/<int:swap_id>/reject",
    methods=["POST"]
)
@admin_required
def reject_room_swap(swap_id):

    swap = RoomSwap.query.get(
        swap_id
    )


    if not swap:

        flash(
            "Swap request not found.",
            "error"
        )

        return redirect(
            url_for("admin_room_swaps")
        )


    swap.status = "rejected"


    db.session.commit()


    flash(
        "Room swap request rejected.",
        "success"
    )


    return redirect(
        url_for("admin_room_swaps")
    )


# ============================================================
# STUDENT COMPLAINTS
# ============================================================

@app.route(
    "/student/complaints",
    methods=["GET", "POST"]
)
@student_required
def student_complaints():

    student = get_student()


    if request.method == "POST":

        complaint = Complaint(
            student_id=student.id,
            category=request.form.get(
                "category",
                ""
            ),
            title=request.form.get(
                "title",
                ""
            ),
            description=request.form.get(
                "description",
                ""
            ),
            priority=request.form.get(
                "priority",
                "Medium"
            ),
            room_number=request.form.get(
                "room_number",
                ""
            ),
            status="Pending"
        )


        db.session.add(complaint)

        db.session.commit()


        flash(
            "Complaint submitted successfully!",
            "success"
        )


        return redirect(
            url_for("student_complaints")
        )


    complaints = Complaint.query.filter_by(
        student_id=student.id
    ).order_by(
        Complaint.id.desc()
    ).all()


    return render_template(
        "student-complaints.html",
        student=student,
        complaints=complaints
    )


# ============================================================
# ADMIN COMPLAINTS
# ============================================================

@app.route(
    "/admin/complaints"
)
@admin_required
def admin_complaints():

    complaints = Complaint.query.order_by(
        Complaint.id.desc()
    ).all()


    total_complaints = len(
        complaints
    )


    pending_complaints = sum(
        1
        for complaint in complaints
        if str(complaint.status).lower() == "pending"
    )


    resolved_complaints = sum(
        1
        for complaint in complaints
        if str(complaint.status).lower() == "resolved"
    )


    return render_template(
        "admin-complaints.html",
        complaints=complaints,
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints
    )


# ============================================================
# ADMIN UPDATE COMPLAINT STATUS
# ============================================================

@app.route(
    "/admin/complaint/<int:complaint_id>/update",
    methods=["POST"]
)
@admin_required
def update_complaint_status(complaint_id):

    complaint = Complaint.query.get(
        complaint_id
    )


    if not complaint:

        flash(
            "Complaint not found.",
            "error"
        )

        return redirect(
            url_for("admin_complaints")
        )


    status = request.form.get(
        "status",
        "Pending"
    )


    complaint.status = status


    db.session.commit()


    flash(
        "Complaint status updated successfully!",
        "success"
    )


    return redirect(
        url_for("admin_complaints")
    )


# ============================================================
# STUDENT ANNOUNCEMENTS
# ============================================================

@app.route(
    "/student/announcements"
)
@student_required
def student_announcements():

    announcements = Announcement.query.order_by(
        Announcement.id.desc()
    ).all()


    return render_template(
        "student-announcements.html",
        announcements=announcements
    )


# ============================================================
# STUDENT HOSTEL NOTICES
# ============================================================

@app.route(
    "/student/hostel-notices"
)
@student_required
def student_hostel_notices():

    notices = Announcement.query.order_by(
        Announcement.id.desc()
    ).all()

    return render_template(
        "student-hostel-notices.html",
        notices=notices
    )


# ============================================================
# ADMIN ANNOUNCEMENTS
# ============================================================

@app.route(
    "/admin/announcements",
    methods=["GET", "POST"]
)
@admin_required
def admin_announcements():

    admin = get_admin()


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()


        if not title or not content:

            flash(
                "Please enter title and content.",
                "error"
            )

            return redirect(
                url_for("admin_announcements")
            )


        announcement = Announcement(
            title=title,
            content=content,
            created_by=admin.id
        )


        db.session.add(
            announcement
        )


        db.session.commit()


        flash(
            "Announcement published successfully!",
            "success"
        )


        return redirect(
            url_for("admin_announcements")
        )


    announcements = Announcement.query.order_by(
        Announcement.id.desc()
    ).all()


    return render_template(
        "admin-announcements.html",
        announcements=announcements
    )


# ============================================================
# ADMIN HOSTEL NOTICES
# ============================================================

@app.route(
    "/admin/hostel-notices",
    methods=["GET", "POST"]
)
@admin_required
def admin_hostel_notices():

    admin = get_admin()


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()


        if not title or not content:

            flash(
                "Please enter notice title and content.",
                "error"
            )

            return redirect(
                url_for("admin_hostel_notices")
            )


        notice = HostelNotice(
            title=title,
            content=content,
            created_by=admin.id
        )


        db.session.add(
            notice
        )


        db.session.commit()


        flash(
            "Hostel notice published successfully!",
            "success"
        )


        return redirect(
            url_for("admin_hostel_notices")
        )


    notices = HostelNotice.query.order_by(
        HostelNotice.id.desc()
    ).all()


    return render_template(
        "admin-hostel-notices.html",
        notices=notices
    )


# ============================================================
# STUDENT FEES
# ============================================================

@app.route(
    "/student/fees"
)
@student_required
def student_fees():

    student = get_student()


    fees = Fee.query.filter_by(
        student_id=student.id
    ).order_by(
        Fee.id.desc()
    ).all()


    total_fee = sum(
        float(fee.amount or 0)
        for fee in fees
    )


    paid_fee = sum(
        float(fee.amount or 0)
        for fee in fees
        if str(fee.status).lower() == "paid"
    )


    pending_fee = total_fee - paid_fee


    return render_template(
        "student-fees.html",
        student=student,
        fees=fees,
        total_fee=total_fee,
        paid_fee=paid_fee,
        pending_fee=pending_fee
    )


# ============================================================
# ADMIN FEES
# ============================================================

@app.route(
    "/admin/fees",
    methods=["GET", "POST"]
)
@admin_required
def admin_fees():

    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            type=int
        )


        fee_type = request.form.get(
            "fee_type",
            ""
        ).strip()


        amount = parse_float(
            request.form.get(
                "amount",
                "0"
            )
        )


        due_date = parse_date(
            request.form.get(
                "due_date",
                ""
            )
        )


        if not student_id:

            flash(
                "Please select a student.",
                "error"
            )

            return redirect(
                url_for("admin_fees")
            )


        student = User.query.filter_by(
            id=student_id,
            role="student"
        ).first()


        if not student:

            flash(
                "Student not found.",
                "error"
            )

            return redirect(
                url_for("admin_fees")
            )


        if amount <= 0:

            flash(
                "Fee amount must be greater than zero.",
                "error"
            )

            return redirect(
                url_for("admin_fees")
            )


        if not due_date:

            flash(
                "Please enter a valid due date.",
                "error"
            )

            return redirect(
                url_for("admin_fees")
            )


        fee = Fee(
            student_id=student_id,
            fee_type=fee_type,
            amount=amount,
            due_date=due_date,
            status="Pending"
        )


        db.session.add(
            fee
        )


        db.session.commit()


        flash(
            "Fee created successfully!",
            "success"
        )


        return redirect(
            url_for("admin_fees")
        )


    students = User.query.filter_by(
        role="student"
    ).order_by(
        User.name.asc()
    ).all()


    fees = Fee.query.order_by(
        Fee.id.desc()
    ).all()


    return render_template(
        "admin-fees.html",
        students=students,
        fees=fees
    )


# ============================================================
# STUDENT PAYMENTS
# ============================================================

@app.route(
    "/student/payments"
)
@student_required
def student_payments():

    student = get_student()


    payments = Payment.query.filter_by(
        student_id=student.id
    ).order_by(
        Payment.id.desc()
    ).all()


    return render_template(
        "student-payments.html",
        student=student,
        payments=payments
    )


# ============================================================
# STUDENT MAKE PAYMENT
# ============================================================

@app.route(
    "/student/payment/<int:fee_id>",
    methods=["GET", "POST"]
)
@student_required
def student_make_payment(fee_id):

    student = get_student()


    fee = Fee.query.filter_by(
        id=fee_id,
        student_id=student.id
    ).first()


    if not fee:

        flash(
            "Fee record not found.",
            "error"
        )

        return redirect(
            url_for("student_fees")
        )


    if str(fee.status).lower() == "paid":

        flash(
            "This fee has already been paid.",
            "success"
        )

        return redirect(
            url_for("student_payments")
        )


    if request.method == "POST":

        transaction_id = request.form.get(
            "transaction_id",
            ""
        ).strip()


        if not transaction_id:

            transaction_id = (
                "TXN"
                + datetime.now().strftime(
                    "%Y%m%d%H%M%S"
                )
            )


        existing_payment = Payment.query.filter_by(
            transaction_id=transaction_id
        ).first()


        if existing_payment:

            flash(
                "Transaction ID already exists.",
                "error"
            )

            return redirect(
                url_for(
                    "student_make_payment",
                    fee_id=fee.id
                )
            )


        payment = Payment(
            student_id=student.id,
            fee_id=fee.id,
            amount=fee.amount,
            transaction_id=transaction_id,
            payment_date=date.today(),
            status="Success"
        )


        db.session.add(
            payment
        )


        fee.status = "Paid"


        db.session.commit()


        flash(
            "Payment completed successfully!",
            "success"
        )


        return redirect(
            url_for("student_payments")
        )


    return render_template(
        "student-make-payment.html",
        student=student,
        fee=fee
    )


# ============================================================
# ADMIN PAYMENTS
# ============================================================

@app.route(
    "/admin/payments"
)
@admin_required
def admin_payments():

    payments = Payment.query.order_by(
        Payment.id.desc()
    ).all()


    total_payments = len(
        payments
    )


    total_amount = sum(
        float(payment.amount or 0)
        for payment in payments
        if str(payment.status).lower() == "success"
    )


    return render_template(
        "admin-payments.html",
        payments=payments,
        total_payments=total_payments,
        total_amount=total_amount
    )
# ============================================================
# STUDENT LEAVE
# ============================================================

@app.route(
    "/student/leave",
    methods=["GET", "POST"]
)
@student_required
def student_leave():

    student = get_student()


    if request.method == "POST":

        from_date = parse_date(
            request.form.get(
                "from_date",
                ""
            )
        )


        to_date = parse_date(
            request.form.get(
                "to_date",
                ""
            )
        )


        reason = request.form.get(
            "reason",
            ""
        ).strip()


        # -------------------------------
        # DATE VALIDATION
        # -------------------------------

        if not from_date:

            flash(
                "Please select a valid From Date.",
                "error"
            )

            return redirect(
                url_for("student_leave")
            )


        if not to_date:

            flash(
                "Please select a valid To Date.",
                "error"
            )

            return redirect(
                url_for("student_leave")
            )


        if to_date < from_date:

            flash(
                "To Date cannot be before From Date.",
                "error"
            )

            return redirect(
                url_for("student_leave")
            )


        if not reason:

            flash(
                "Please enter the reason for leave.",
                "error"
            )

            return redirect(
                url_for("student_leave")
            )


        # -------------------------------
        # CREATE LEAVE
        # -------------------------------

        leave = LeaveRequest(
            student_id=student.id,
            from_date=from_date,
            to_date=to_date,
            reason=reason,
            status="Pending"
        )


        db.session.add(
            leave
        )


        db.session.commit()


        flash(
            "Leave request submitted successfully!",
            "success"
        )


        return redirect(
            url_for("student_leave")
        )


    leave_requests = LeaveRequest.query.filter_by(
        student_id=student.id
    ).order_by(
        LeaveRequest.id.desc()
    ).all()


    return render_template(
        "student-leave.html",
        student=student,
        leave_requests=leave_requests
    )


# ============================================================
# ADMIN LEAVE REQUESTS
# ============================================================

@app.route(
    "/admin/leave"
)
@admin_required
def admin_leave():

    leave_requests = LeaveRequest.query.order_by(
        LeaveRequest.id.desc()
    ).all()


    total_leave_requests = len(
        leave_requests
    )


    pending_leave_requests = sum(
        1
        for leave in leave_requests
        if str(leave.status).lower() == "pending"
    )


    approved_leave_requests = sum(
        1
        for leave in leave_requests
        if str(leave.status).lower() == "approved"
    )


    rejected_leave_requests = sum(
        1
        for leave in leave_requests
        if str(leave.status).lower() == "rejected"
    )


    return render_template(
        "admin-leave.html",
        leave_requests=leave_requests,
        total_leave_requests=total_leave_requests,
        pending_leave_requests=pending_leave_requests,
        approved_leave_requests=approved_leave_requests,
        rejected_leave_requests=rejected_leave_requests
    )


# ============================================================
# ADMIN LEAVE REQUESTS ALIAS
# ============================================================

@app.route(
    "/admin/leave-requests"
)
@admin_required
def admin_leave_requests():

    return redirect(
        url_for("admin_leave")
    )


# ============================================================
# APPROVE LEAVE
# ============================================================

@app.route(
    "/admin/leave/<int:leave_id>/approve",
    methods=["POST"]
)
@admin_required
def approve_leave(leave_id):

    leave = LeaveRequest.query.get(
        leave_id
    )


    if not leave:

        flash(
            "Leave request not found.",
            "error"
        )

        return redirect(
            url_for("admin_leave")
        )


    if str(leave.status).lower() != "pending":

        flash(
            "This leave request has already been processed.",
            "error"
        )

        return redirect(
            url_for("admin_leave")
        )


    leave.status = "Approved"


    db.session.commit()


    flash(
        "Leave request accepted successfully!",
        "success"
    )


    return redirect(
        url_for("admin_leave")
    )


# ============================================================
# REJECT LEAVE
# ============================================================

@app.route(
    "/admin/leave/<int:leave_id>/reject",
    methods=["POST"]
)
@admin_required
def reject_leave(leave_id):

    leave = LeaveRequest.query.get(
        leave_id
    )


    if not leave:

        flash(
            "Leave request not found.",
            "error"
        )

        return redirect(
            url_for("admin_leave")
        )


    if str(leave.status).lower() != "pending":

        flash(
            "This leave request has already been processed.",
            "error"
        )

        return redirect(
            url_for("admin_leave")
        )


    leave.status = "Rejected"


    db.session.commit()


    flash(
        "Leave request rejected.",
        "success"
    )


    return redirect(
        url_for("admin_leave")
    )


# ============================================================
# STUDENT MESSAGES
# ============================================================

@app.route(
    "/student/messages",
    methods=["GET"]
)
@student_required
def student_messages():

    student = get_student()

    # Get all administrators
    admins = User.query.filter_by(
        role="admin"
    ).order_by(
        User.name.asc()
    ).all()

    # Get messages related to this student
    messages = Message.query.filter(
        (
            Message.sender_id == student.id
        )
        |
        (
            Message.receiver_id == student.id
        )
    ).order_by(
        Message.created_at.asc()
    ).all()

    return render_template(
        "student-messages.html",
        student=student,
        admins=admins,
        messages=messages
    )


# ============================================================
# STUDENT SEND MESSAGE TO ADMIN
# ============================================================

@app.route(
    "/student/messages/send",
    methods=["POST"]
)
@student_required
def student_send_message():

    student = get_student()

    message_text = request.form.get(
        "message",
        ""
    ).strip()

    admin_id = request.form.get(
        "admin_id",
        type=int
    )

    if not message_text:

        flash(
            "Please type a message first.",
            "error"
        )

        return redirect(
            url_for("student_messages")
        )

    # If no admin selected, use first admin
    admin = None

    if admin_id:

        admin = User.query.filter_by(
            id=admin_id,
            role="admin"
        ).first()

    if not admin:

        admin = User.query.filter_by(
            role="admin"
        ).order_by(
            User.id.asc()
        ).first()

    if not admin:

        flash(
            "No administrator is available.",
            "error"
        )

        return redirect(
            url_for("student_messages")
        )

    new_message = Message(
        sender_id=student.id,
        receiver_id=admin.id,
        message=message_text,
        is_read=False
    )

    db.session.add(
        new_message
    )

    db.session.commit()

    flash(
        "Message sent to hostel administration successfully!",
        "success"
    )

    return redirect(
        url_for("student_messages")
    )


# ============================================================
# ADMIN MESSAGES
# ============================================================

@app.route("/admin/messages")
@admin_required
def admin_messages():

    admin = get_admin()

    messages = Message.query.filter(
        (
            Message.sender_id == admin.id
        )
        |
        (
            Message.receiver_id == admin.id
        )
    ).order_by(
        Message.created_at.asc()
    ).all()

    message_data = []

    for msg in messages:

        # ----------------------------------------------------
        # STUDENT MESSAGE
        # ----------------------------------------------------

        if msg.sender_id != admin.id:

            student = User.query.filter_by(
                id=msg.sender_id,
                role="student"
            ).first()

            if student:

                # Find student's room allocation
                allocation = RoomAllocation.query.filter(
                    RoomAllocation.student_id == student.id
                ).order_by(
                    RoomAllocation.id.desc()
                ).first()

                room = None

                if allocation:

                    room = Room.query.get(
                        allocation.room_id
                    )

                message_data.append({
                    "message": msg,
                    "student": student,
                    "room": room,
                    "is_student_message": True
                })

        # ----------------------------------------------------
        # ADMIN MESSAGE
        # ----------------------------------------------------

        else:

            student = User.query.filter_by(
                id=msg.receiver_id,
                role="student"
            ).first()

            if student:

                allocation = RoomAllocation.query.filter(
                    RoomAllocation.student_id == student.id
                ).order_by(
                    RoomAllocation.id.desc()
                ).first()

                room = None

                if allocation:

                    room = Room.query.get(
                        allocation.room_id
                    )

                message_data.append({
                    "message": msg,
                    "student": student,
                    "room": room,
                    "is_student_message": False
                })


    return render_template(
        "admin-messages.html",
        admin=admin,
        message_data=message_data
    )


# ============================================================
# ADMIN SEND MESSAGE / REPLY TO STUDENT
# ============================================================

@app.route(
    "/admin/messages/send",
    methods=["POST"]
)
@admin_required
def admin_send_message():

    admin = get_admin()

    student_id = request.form.get(
        "student_id",
        type=int
    )

    message_text = request.form.get(
        "message",
        ""
    ).strip()


    if not student_id:

        flash(
            "Student not selected.",
            "error"
        )

        return redirect(
            url_for("admin_messages")
        )


    if not message_text:

        flash(
            "Please type a message.",
            "error"
        )

        return redirect(
            url_for("admin_messages")
        )


    student = User.query.filter_by(
        id=student_id,
        role="student"
    ).first()


    if not student:

        flash(
            "Student not found.",
            "error"
        )

        return redirect(
            url_for("admin_messages")
        )


    new_message = Message(
        sender_id=admin.id,
        receiver_id=student.id,
        message=message_text,
        is_read=False
    )


    db.session.add(
        new_message
    )

    db.session.commit()


    flash(
        "Reply sent successfully!",
        "success"
    )


    return redirect(
        url_for("admin_messages")
    )


# ============================================================
# ADMIN REPORTS
# ============================================================

@app.route("/admin/reports")
@admin_required
def admin_reports():

    admin = get_admin()

    # --------------------------------------------------------
    # STUDENTS
    # --------------------------------------------------------

    total_students = User.query.filter_by(
        role="student"
    ).count()

    # --------------------------------------------------------
    # ROOMS + OCCUPANCY
    # --------------------------------------------------------

    rooms = Room.query.all()

    total_rooms = len(rooms)
    occupied_rooms = 0
    available_rooms = 0
    total_capacity = 0
    occupied_beds = 0

    for room in rooms:

        capacity = int(room.capacity or 0)
        total_capacity += capacity

        occupied_count = RoomAllocation.query.filter(
            RoomAllocation.room_id == room.id,
            db.func.lower(RoomAllocation.status) == "active"
        ).count()

        occupied_beds += occupied_count

        if occupied_count > 0:
            occupied_rooms += 1

        if occupied_count < capacity:
            available_rooms += 1

    # --------------------------------------------------------
    # COMPLAINTS
    # --------------------------------------------------------

    complaints = Complaint.query.all()

    total_complaints = len(complaints)

    pending_complaints = sum(
        1
        for complaint in complaints
        if str(complaint.status).lower() == "pending"
    )

    resolved_complaints = sum(
        1
        for complaint in complaints
        if str(complaint.status).lower() == "resolved"
    )

    # --------------------------------------------------------
    # FEES
    # --------------------------------------------------------

    fees = Fee.query.all()

    total_fees = len(fees)

    total_fee_amount = sum(
        float(fee.amount or 0)
        for fee in fees
    )

    paid_fee_amount = sum(
        float(fee.amount or 0)
        for fee in fees
        if str(fee.status).lower() == "paid"
    )

    pending_fee_amount = sum(
        float(fee.amount or 0)
        for fee in fees
        if str(fee.status).lower() == "pending"
    )

    paid_fees = sum(
        1
        for fee in fees
        if str(fee.status).lower() == "paid"
    )

    pending_fees = sum(
        1
        for fee in fees
        if str(fee.status).lower() == "pending"
    )

    # --------------------------------------------------------
    # PAYMENTS
    # --------------------------------------------------------

    payments = Payment.query.order_by(
        Payment.id.desc()
    ).all()

    total_payments = len(payments)

    successful_payments = sum(
        1
        for payment in payments
        if str(payment.status).lower()
        in ["success", "successful", "paid"]
    )

    total_payment_amount = sum(
        float(payment.amount or 0)
        for payment in payments
        if str(payment.status).lower()
        in ["success", "successful", "paid"]
    )

    # --------------------------------------------------------
    # LEAVE REQUESTS
    # --------------------------------------------------------

    leave_requests = LeaveRequest.query.all()

    total_leave_requests = len(leave_requests)

    pending_leave_requests = sum(
        1
        for leave in leave_requests
        if str(leave.status).lower() == "pending"
    )

    approved_leave_requests = sum(
        1
        for leave in leave_requests
        if str(leave.status).lower() == "approved"
    )

    rejected_leave_requests = sum(
        1
        for leave in leave_requests
        if str(leave.status).lower() == "rejected"
    )

    # --------------------------------------------------------
    # ROOM SWAPS
    # --------------------------------------------------------

    swaps = RoomSwap.query.all()

    total_swaps = len(swaps)

    pending_swaps = sum(
        1
        for swap in swaps
        if str(swap.status).lower() == "pending"
    )

    approved_swaps = sum(
        1
        for swap in swaps
        if str(swap.status).lower() == "approved"
    )

    rejected_swaps = sum(
        1
        for swap in swaps
        if str(swap.status).lower() == "rejected"
    )

    # --------------------------------------------------------
    # NOTICES
    # --------------------------------------------------------

    total_notices = HostelNotice.query.count()

    # --------------------------------------------------------
    # RECENT DATA
    # --------------------------------------------------------

    recent_students = User.query.filter_by(
        role="student"
    ).order_by(
        User.id.desc()
    ).limit(5).all()

    recent_complaints = Complaint.query.order_by(
        Complaint.id.desc()
    ).limit(5).all()

    recent_payments = Payment.query.order_by(
        Payment.id.desc()
    ).limit(5).all()

    recent_leave_requests = LeaveRequest.query.order_by(
        LeaveRequest.id.desc()
    ).limit(5).all()

    # --------------------------------------------------------
    # RENDER REPORTS
    # --------------------------------------------------------

    return render_template(
        "admin-reports.html",

        admin=admin,

        total_students=total_students,

        total_rooms=total_rooms,
        occupied_rooms=occupied_rooms,
        available_rooms=available_rooms,
        total_capacity=total_capacity,
        occupied_beds=occupied_beds,

        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,

        total_fees=total_fees,
        paid_fees=paid_fees,
        pending_fees=pending_fees,
        total_fee_amount=total_fee_amount,
        paid_fee_amount=paid_fee_amount,
        pending_fee_amount=pending_fee_amount,

        total_payments=total_payments,
        successful_payments=successful_payments,
        total_payment_amount=total_payment_amount,

        total_leave_requests=total_leave_requests,
        pending_leave_requests=pending_leave_requests,
        approved_leave_requests=approved_leave_requests,
        rejected_leave_requests=rejected_leave_requests,

        total_swaps=total_swaps,
        pending_swaps=pending_swaps,
        approved_swaps=approved_swaps,
        rejected_swaps=rejected_swaps,

        total_notices=total_notices,

        recent_students=recent_students,
        recent_complaints=recent_complaints,
        recent_payments=recent_payments,
        recent_leave_requests=recent_leave_requests
    )


# ============================================================
# ADMIN SETTINGS
# ============================================================

@app.route("/admin/settings", methods=["GET", "POST"])
@admin_required
def admin_settings():

    admin = get_admin()

    if request.method == "POST":

        action = request.form.get("action", "").strip()

        # ----------------------------------------------------
        # UPDATE PROFILE
        # ----------------------------------------------------

        if action == "update_profile":

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()

            if not name or not email:
                flash(
                    "Name and email are required.",
                    "error"
                )
                return redirect(url_for("admin_settings"))

            # Check whether email belongs to another user
            existing_user = User.query.filter(
                User.email == email,
                User.id != admin.id
            ).first()

            if existing_user:
                flash(
                    "This email is already being used.",
                    "error"
                )
                return redirect(url_for("admin_settings"))

            try:

                admin.name = name
                admin.email = email
                admin.phone = phone

                db.session.commit()

                flash(
                    "Admin profile updated successfully.",
                    "success"
                )

            except Exception as e:

                db.session.rollback()

                print("PROFILE UPDATE ERROR:", e)

                flash(
                    "Unable to update profile.",
                    "error"
                )

            return redirect(url_for("admin_settings"))

        # ----------------------------------------------------
        # CHANGE PASSWORD
        # ----------------------------------------------------

        if action == "change_password":

            current_password = request.form.get(
                "current_password",
                ""
            )

            new_password = request.form.get(
                "new_password",
                ""
            )

            confirm_password = request.form.get(
                "confirm_password",
                ""
            )

            if not current_password:
                flash(
                    "Please enter your current password.",
                    "error"
                )
                return redirect(url_for("admin_settings"))

            if not new_password:
                flash(
                    "Please enter a new password.",
                    "error"
                )
                return redirect(url_for("admin_settings"))

            if len(new_password) < 6:
                flash(
                    "New password must contain at least 6 characters.",
                    "error"
                )
                return redirect(url_for("admin_settings"))

            if new_password != confirm_password:
                flash(
                    "New passwords do not match.",
                    "error"
                )
                return redirect(url_for("admin_settings"))

            if not admin.check_password(current_password):
                flash(
                    "Current password is incorrect.",
                    "error"
                )
                return redirect(url_for("admin_settings"))

            try:

                admin.set_password(new_password)

                db.session.commit()

                flash(
                    "Password changed successfully.",
                    "success"
                )

            except Exception as e:

                db.session.rollback()

                print("PASSWORD CHANGE ERROR:", e)

                flash(
                    "Unable to change password.",
                    "error"
                )

            return redirect(url_for("admin_settings"))

    return render_template(
        "admin-settings.html",
        admin=admin
    )


# ============================================================
# DEFAULT ADMIN CREATION
# ============================================================

def create_default_admin():

    admin = User.query.filter_by(
        email="admin@hostelease.com"
    ).first()


    if not admin:

        admin = User(
            name="HostelEase Administrator",
            roll_number="ADMIN001",
            email="admin@hostelease.com",
            role="admin"
        )


        admin.set_password(
            "admin123"
        )


        db.session.add(
            admin
        )


        db.session.commit()


        print("")
        print("==============================================")
        print("HOSTEASE DEFAULT ADMIN CREATED")
        print("==============================================")
        print("Email    : admin@hostelease.com")
        print("Password : admin123")
        print("==============================================")
        print("")


# ============================================================
# DATABASE + DEFAULT ADMIN
# ============================================================

with app.app_context():

    db.create_all()
    create_default_admin()


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )