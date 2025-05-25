# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    criticality = db.Column(db.String(20), nullable=False)  # RED, ORANGE, YELLOW, LIGHT GREEN, BLUE
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start_datetime.isoformat(),
            'end': self.end_datetime.isoformat(),
            'criticality': self.criticality,
            'description': self.description,
            'backgroundColor': self.get_color(),
            'borderColor': self.get_color()
        }
    
    def get_color(self):
        colors = {
            'RED': '#FF0000',
            'ORANGE': '#FFA500',
            'YELLOW': '#FFFF00',
            'LIGHT GREEN': '#90EE90',
            'BLUE': '#0000FF'
        }
        return colors.get(self.criticality, '#FFFFFF')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events])

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    start = datetime.fromisoformat(data['start'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(data['end'].replace('Z', '+00:00'))
    
    event = Event(
        title=data['title'],
        start_datetime=start,
        end_datetime=end,
        criticality=data['criticality'],
        description=data.get('description', '')
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify(event.to_dict()), 201

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.json
    
    event.title = data['title']
    event.start_datetime = datetime.fromisoformat(data['start'].replace('Z', '+00:00'))
    event.end_datetime = datetime.fromisoformat(data['end'].replace('Z', '+00:00'))
    event.criticality = data['criticality']
    event.description = data.get('description', '')
    
    db.session.commit()
    
    return jsonify(event.to_dict())

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    
    return '', 204

@app.route('/api/dashboard-data', methods=['GET'])
def dashboard_data():
    # Get counts for each criticality level
    criticality_counts = {
        'RED': Event.query.filter_by(criticality='RED').count(),
        'ORANGE': Event.query.filter_by(criticality='ORANGE').count(),
        'YELLOW': Event.query.filter_by(criticality='YELLOW').count(),
        'LIGHT GREEN': Event.query.filter_by(criticality='LIGHT GREEN').count(),
        'BLUE': Event.query.filter_by(criticality='BLUE').count()
    }
    
    return jsonify(criticality_counts)

if __name__ == '__main__':
    if not os.path.exists('instance/events.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
