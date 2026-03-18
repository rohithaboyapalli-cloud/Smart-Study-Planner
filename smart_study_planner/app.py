import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'smart_study_planner_super_secret'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    study_hours_per_day = int(data.get('study_hours', 4))
    subjects = data.get('subjects', [])
    
    if not subjects or study_hours_per_day <= 0:
        return jsonify({'error': 'Invalid input'}), 400
        
    start_date = datetime.now().date()
    
    parsed_subjects = []
    max_exam_date = start_date
    for s in subjects:
        try:
            exam_date = datetime.strptime(s['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
            
        days_left = (exam_date - start_date).days
        if days_left <= 0:
            continue
            
        topics = float(s.get('topics', 1))
        
        if exam_date > max_exam_date:
            max_exam_date = exam_date
            
        parsed_subjects.append({
            'name': s['name'],
            'exam_date': exam_date,
            'days_left': days_left,
            'topics_total': topics,
            'topics_remaining': topics,
            'difficulty': 5.0
        })
        
    if not parsed_subjects:
        return jsonify({'error': 'No valid subjects found. Ensure exam dates are in the future.'}), 400
        
    total_days = (max_exam_date - start_date).days
    timetable = []
    
    slot_duration = 2 if study_hours_per_day >= 2 else 1
    slots_per_day = study_hours_per_day // slot_duration
    
    for day in range(total_days + 1):
        current_date = start_date + timedelta(days=day)
        startTime = datetime.strptime("16:00", "%H:%M")
        prev_subject = None
        
        for slot in range(slots_per_day):
            candidates = []
            for s in parsed_subjects:
                if s['exam_date'] > current_date and s['topics_remaining'] > 0:
                    d_left = max(1, (s['exam_date'] - current_date).days)
                    priority = s['topics_remaining'] / d_left
                    if prev_subject == s['name']:
                        priority *= 0.1
                    candidates.append((priority, s))
            
            if not candidates:
                break
                
            candidates.sort(key=lambda x: x[0], reverse=True)
            chosen = candidates[0][1]
            
            endTime = startTime + timedelta(hours=slot_duration)
            time_str = f"{startTime.strftime('%I:%M %p')} - {endTime.strftime('%I:%M %p')}"
            
            topics_covered = max(1, chosen['topics_total'] / max(1, (chosen['days_left'] * slots_per_day * 0.8)))
            chosen['topics_remaining'] -= topics_covered
            
            timetable.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'time_slot': time_str,
                'subject': chosen['name']
            })
            
            prev_subject = chosen['name']
            startTime = endTime
            
        total_remaining = sum(s['topics_remaining'] for s in parsed_subjects)
        if total_remaining <= 0:
            break

    session['timetable'] = timetable
    return jsonify({'success': True, 'redirect': url_for('timetable')})

@app.route('/timetable')
def timetable():
    schedule = session.get('timetable')
    if not schedule:
        return redirect(url_for('setup'))
    return render_template('timetable.html', schedule=schedule)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
