import unittest
from app.database.models import save_alert, get_alerts

class TestAlerts(unittest.TestCase):
    def test_save_and_get_alerts(self):
        alert = {
            'room': '101',
            'severity': 'high',
            'description': 'Test alert',
            'timestamp': int(time.time())
        }
        save_alert(alert)
        alerts = get_alerts()
        self.assertTrue(any(a['description'] == 'Test alert' for a in alerts))

if __name__ == '__main__':
    unittest.main()