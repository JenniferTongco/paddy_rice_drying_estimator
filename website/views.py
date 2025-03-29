from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from mlmodels.drying_time_model.predict_drying_time import predict_drying_time
from mlmodels.moisture_model.predict_moisture import predict_moisture
from .models import DryingRecord
from . import db
import traceback

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        try:
            # Get form values
            initial_weight = float(request.form.get('initial_weight'))
            humidity = float(request.form.get('humidity'))
            temperature = float(request.form.get('temperature'))
            sensor_value = float(request.form.get('sensor_value'))  # capacitive

            # Predict moisture content
            moisture_content = predict_moisture(sensor_value, temperature, humidity)
            moisture_content = round(moisture_content, 2)

            # Render moisture content selection page
            return render_template("calculation.html",
                                   user=current_user,
                                   moisture_content=moisture_content,
                                   initial_weight=initial_weight,
                                   temperature=temperature,
                                   humidity=humidity,
                                   sensor_value=sensor_value)

        except Exception as e:
           flash(f"Error processing sensor data: {e}", category="error")


    return render_template("home.html", user=current_user)

@views.route('/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        # Print raw form inputs for debugging
        print("== Incoming Form Data ==")
        for field in ["initial_weight", "temperature", "humidity", "sensor_value", "moisture_content", "final_moisture"]:
            print(f"{field}: {request.form.get(field)} (type: {type(request.form.get(field))})")

        # Retrieve and convert form data
        initial_weight = float(request.form.get('initial_weight'))
        temperature = float(request.form.get('temperature'))
        humidity = float(request.form.get('humidity'))
        sensor_value = float(request.form.get('sensor_value'))
        moisture_content = float(request.form.get('moisture_content'))
        final_moisture = float(request.form.get('final_moisture'))

        # Predict drying time
        hours, minutes = predict_drying_time(moisture_content, temperature, humidity, final_moisture)
        drying_time = f"{hours}:{minutes:02d}"


        # Calculate final weight
        dry_matter = initial_weight * (1 - moisture_content / 100)
        final_weight = round(dry_matter / (1 - final_moisture / 100), 2)


        # Save drying record to DB
        new_record = DryingRecord(
            initial_weight=initial_weight,
            temperature=temperature,
            humidity=humidity,
            sensor_value=sensor_value,
            initial_moisture=moisture_content,
            final_moisture=final_moisture,
            drying_time=drying_time,
            final_weight=final_weight,
            user_id=current_user.id
        )
        db.session.add(new_record)
        db.session.commit()

        return render_template("prediction.html",
                               user=current_user,
                               drying_time=drying_time,
                               final_weight=final_weight)

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Calculation error: {e}", category="error")
        return redirect(url_for('views.home'))


@views.route('/records')
@login_required
def records():
    user_records = DryingRecord.query.filter_by(user_id=current_user.id).order_by(DryingRecord.timestamp.desc()).all()
    return render_template("records.html", user=current_user, records=user_records)
