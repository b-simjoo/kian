from flask import Flask, request, session, render_template, redirect, jsonify, g, url_for, abort
from flask_session import Session
from datetime import timedelta,datetime
from flask_mobility import Mobility
from openpyxl import load_workbook
from model import db, Student, Device, Attendance, Score, Meeting
from getmac import get_mac_address
from playhouse.shortcuts import model_to_dict
from tempfile import NamedTemporaryFile

import json

DEBUG= True,
SESSION_PERMANENT= True
SESSION_TYPE = 'filesystem',
TRAP_HTTP_EXCEPTIONS= True
PERMANENT_SESSION_LIFETIME= timedelta(hours=2)

app = Flask(__name__)
app.config.from_object(__name__)

config:dict = json.load(open('config.json','r'))

Session(app)
Mobility(app)


@app.before_first_request
def initialize():
    db.connect()
    db.create_tables([Student,Device,Attendance,Score,Meeting])
    

@app.before_request
def _before_request():
    if not db.is_connection_usable():
        db.connect()
    
    if session.get('mac') is None:
        if request.remote_addr in ('localhost', '127.0.0.1'):
            session['local_user'] = True
            if app.debug:
                mac = 'local'
            else:
                return
        else:
            mac = get_mac_address(ip=request.remote_addr)
        device:Device = Device.get_or_create(mac=mac)
        session['mac'] = mac
        session['device'] = device

@app.teardown_request
def _db_close(exc):
   if not db.is_closed():
      db.close()

EASTER_EGG = " Hey, I'm so happy that you are reading this! good luck! BSimjoo ;-)"      # An easter-egg for my students!

@app.route('/api/v1/register')
def register_device():
    device = session['device']
    if device.student is not None:   #device is not registered
        if (std_num:=request.args.get('std_num')) is not None:
            if (student:=Student.get_or_none(Student.number==std_num)) is not None:
                device.student = student
                device.save()
                session['student'] = student
                return jsonify(student_name=student.name)
            else:   # student not existed
                return jsonify(error_code=1, info='student not existed. check std_num.'+EASTER_EGG), 404
        else:   # std_num didn't send
            return jsonify(error_code=2, info="std_num didn't send."+EASTER_EGG), 400
    else:   # The student has already registered this device
        return jsonify(error_code=3, info="device is already register, new registration is forbidden."+EASTER_EGG), 403
    
@app.route('/api/v1/attendance')
def attendance():
    if (getattr(g,'meeting',None) is not None):
        if (student:=session.get('student')) is not None:
            Attendance(student = student, device = session['device'], meeting = g.meeting).save()
            res={
                'name':student.name,
                'number': student.number,
                'attendances': list(student.attendances.dicts()),
                'meetings': list(Meeting.select().dicts())
            }
            return jsonify(res)
        else:   # user has not registered yet
            return jsonify(error_code=4,info="You must register first."+EASTER_EGG), 403
    else:
        return jsonify(error_code=8, info="session did not started yet."+EASTER_EGG), 404
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin'):
        return redirect(url_for('admin'))
    if request.method == 'POST':
        if (not session.get('banned')):
            username = request.form.get('username',type=str)
            password = request.form.get('password',type=str)
            if username and password:
                if (config['admin username'],config['admin password']) == (username, password):
                    session['admin'] = True
                    return redirect(url_for('admin'))
            session['failed tries'] = session.get('failed tries',0) + 1
            if session['failed tries'] == 5:
                session['banned'] = True
                return jsonify(error_code=4, banned=True, info="login failed, you got banned."+EASTER_EGG), 401
            return jsonify(error_code=5, banned=False, failed_tries=session['failed tries'], info="login failed."+EASTER_EGG), 401
        else:
            return jsonify(error_code=6, banned=True, info="you are banned."+EASTER_EGG), 403
    return render_template('login.html')
    
def login_required(func):
    def wrapper(*args, **kwargs):
        if session.get('admin'):
            return func(*args,**kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper
        
@app.route('/admin')
@login_required
def admin():
    return render_template('admin')

@app.route('/api/v1/students',method = ['POST'])
@login_required
def set_students():
    if (file:=request.files.get('file')):
        if file.filename:
            if file.filename.rsplit('.',1)[1]=='xlsx':
                with NamedTemporaryFile('r+b') as tmp:
                    file.save(tmp)
                    tmp.seek(0)
                    wb = load_workbook(tmp.name)
                    ws = wb.active
                    for row in ws.iter_rows(max_col=2):
                        std = Student.get_or_create(number = row[0].value, name = row[1].value)
                        std.save()
                    return redirect(url_for('admin'))
            else:
                return jsonify(error_code=7, info="bad file format")
    abort(400)              

@app.route('/api/v1/students/<int:number>')
@login_required
def get_students(number=None):
    if number is None:
        students = []
        for student in Student.select():
            d = student.to_dict(
                attendances = list(student.attendances.dicts()),
                scores = list(student.scores.dicts()),
                devices = list(student.devices.dicts())
            )
            students.append(d)
        return jsonify(students)
    if (student:=Student.get_or_none(Student.id==number)) is not None:   # type: ignore
        return jsonify(student.to_dict(
            attendances = [a.to_dict() for a in student.attendances],
            scores = [s.to_dict() for s in student.scores],
            devices = [d.to_dict() for d in student.devices]
        ))  
    abort(404)
            
@app.route('/api/v1/meetings/',method=['POST'])
@login_required
def set_meetings():
    if getattr(g,'meeting',None) is None:
        g.meeting = Meeting()
        if g.meeting.save() == 1:
            return jsonify(done=True)
        else:
            return jsonify(done=False, error_code=9, info="Unknown error while creating database record")
    else:
        return jsonify(done=True, error_code=10, info="meeting is already created")
        
            
@app.route('/api/v1/meetings/<int:meeting_id>')
@login_required
def get_meetings(meeting_id:int|None=None):
    if meeting_id is None:
        return jsonify(list(Meeting.select().dicts()))
    if (meet:=Meeting.get_or_none(Meeting.id==meeting_id)) is not None: #type: ignore
        return jsonify(meet.to_dict(
            attendances = [a.to_dict() for a in meet.attendances],
            scores = [s.to_dict() for s in meet.scores]
        ))
    abort(404)
            
@app.route('/api/v1/attendance/<int:attendance_id>')
@login_required
def get_attendance(attendance_id=None):
    if attendance_id is None:
        return jsonify([a.to_dict() for a in Attendance.select()])
    if (a:=Attendance.get_or_none(Attendance.id==attendance_id)) is not None:   #type: ignore
        return jsonify(a.to_dict())
    abort(404)
    
@app.route('/api/v1/device/<int:device_id>')
@login_required
def get_device(device_id=None):
    if device_id is None:
        return jsonify([
            device.to_dict(
                login_history = [l.to_dict for l in device.login_history]
            )
        ] for device in Device.select())
    if (device:=Device.get_or_none(Device.id==device_id)) is not None:      # type: ignore
        return jsonify(device.to_dict(
            login_history = [l.to_dict for l in device.login_history]
        ))
    abort(404)