from app.database.db_config import get_db_connection
import time

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            room_id VARCHAR(50),
            event_type VARCHAR(50),
            severity INTEGER,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id SERIAL PRIMARY KEY,
            event_id INTEGER REFERENCES events(id),
            recipient_id VARCHAR(50),
            status VARCHAR(20),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def save_alert(alert):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (room_id, event_type, severity, description, timestamp)
        VALUES (%s, %s, %s, %s, to_timestamp(%s))
        RETURNING id
    ''', (alert['room'], 'detection', 1 if alert['severity'] == 'high' else 0, alert['description'], alert['timestamp']))
    event_id = cursor.fetchone()[0]
    cursor.execute('''
        INSERT INTO alerts (event_id, recipient_id, status, timestamp)
        VALUES (%s, %s, %s, to_timestamp(%s))
    ''', (event_id, 'caregiver', 'new', alert['timestamp']))
    conn.commit()
    cursor.close()
    conn.close()

def get_alerts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.room_id, e.description, e.severity, EXTRACT(EPOCH FROM e.timestamp) as timestamp
        FROM events e
        JOIN alerts a ON e.id = a.event_id
        ORDER BY e.timestamp DESC
        LIMIT 10
    ''')
    alerts = [
        {
            'room': row[0],
            'description': row[1],
            'severity': 'high' if row[2] == 1 else 'medium',
            'timestamp': row[3]
        } for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return alerts