from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from mlmodels.drying_time_model.predict_drying_time import predict_drying_time
from mlmodels.moisture_model.predict_moisture import predict_moisture
from .models import DryingRecord
from . import db
from datetime import datetime
import serial
import traceback

views = Blueprint('views', __name__)

# Function to read sensor data from Arduino over serial
def read_arduino_serial():
    try:
        with serial.Serial('/dev/ttyACM0', 115200, timeout=2) as ser:
            ser.write(b'read\n')
            line = ser.readline().decode().strip()
            print("Arduino says:", line)

            parts = line.split(",")
            if len(parts) == 3:
                sensor_value = float(parts[0])
                temperature = float(parts[1])
                humidity = float(parts[2])
                return sensor_value, temperature, humidity
    except Exception as e:
        print("Error reading from Arduino:", e)
    return None, None, None


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        try:
            initial_weight = float(request.form.get('initial_weight'))
            final_moisture = float(request.form.get('final_moisture'))
            date_planted = request.form.get('date_planted')
            date_harvested = request.form.get('date_harvested')
            date_dried = request.form.get('date_dried')

            # Parse dates safely
            date_planted = datetime.strptime(date_planted, "%Y-%m-%d").date() if date_planted else None
            date_harvested = datetime.strptime(date_harvested, "%Y-%m-%d").date() if date_harvested else None
            date_dried = datetime.strptime(date_dried, "%Y-%m-%d").date() if date_dried else None

            sensor_value, temperature, humidity = read_arduino_serial()
            if None in (sensor_value, temperature, humidity):
                flash("Error: could not read sensor data from Arduino.", category="error")
                return redirect(url_for('views.home'))

            moisture_content = round(predict_moisture(sensor_value, temperature, humidity), 2)

            return render_template("readings.html",
                                   user=current_user,
                                   initial_weight=initial_weight,
                                   final_moisture=final_moisture,
                                   sensor_value=sensor_value,
                                   temperature=temperature,
                                   humidity=humidity,
                                   moisture_content=moisture_content,
                                   date_planted=date_planted,
                                   date_harvested=date_harvested,
                                   date_dried=date_dried)
        except Exception as e:
            traceback.print_exc()
            flash(f"Error processing form: {e}", category="error")

    return render_template("home.html", user=current_user)


@views.route('/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        # Gather all values from form
        initial_weight = float(request.form.get('initial_weight'))
        temperature = float(request.form.get('temperature'))
        humidity = float(request.form.get('humidity'))
        sensor_value = float(request.form.get('sensor_value'))
        moisture_content = float(request.form.get('moisture_content'))
        final_moisture = float(request.form.get('final_moisture'))

        # Optional dates
        date_planted = request.form.get('date_planted')
        date_harvested = request.form.get('date_harvested')
        date_dried = request.form.get('date_dried')

        date_planted = datetime.strptime(date_planted, "%Y-%m-%d").date() if date_planted else None
        date_harvested = datetime.strptime(date_harvested, "%Y-%m-%d").date() if date_harvested else None
        date_dried = datetime.strptime(date_dried, "%Y-%m-%d").date() if date_dried else None

        # Predict drying time
        hours, minutes = predict_drying_time(moisture_content, temperature, humidity, final_moisture)
        drying_time = f"{hours}:{minutes:02d}"

        # Calculate final weight
        final_weight = round(initial_weight * (1 - moisture_content / 100) / (1 - final_moisture / 100), 2)

        # Save to database
        new_record = DryingRecord(
            initial_weight=initial_weight,
            temperature=temperature,
            humidity=humidity,
            sensor_value=sensor_value,
            initial_moisture=moisture_content,
            final_moisture=final_moisture,
            drying_time=drying_time,
            final_weight=final_weight,
            date_planted=date_planted,
            date_harvested=date_harvested,
            date_dried=date_dried,
            user_id=current_user.id
        )
        db.session.add(new_record)
        db.session.commit()

        return render_template("prediction.html",
                               user=current_user,
                               drying_time=drying_time,
                               final_weight=final_weight)

    except Exception as e:
        traceback.print_exc()
        flash(f"Calculation error: {e}", category="error")
        return redirect(url_for('views.home'))


@views.route('/records')
@login_required
def records():
    user_records = DryingRecord.query.filter_by(user_id=current_user.id).order_by(DryingRecord.timestamp.desc()).all()
    return render_template("records.html", user=current_user, records=user_records)
