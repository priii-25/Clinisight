from flask import Response, request
from app.services.video_processor import VideoProcessor

def register_stream_routes(app, video_processors):
    @app.route('/api/stream')
    def video_feed():
        room_id = request.args.get('room')
        processor = video_processors.get(room_id)
        if not processor:
            return Response("Invalid room ID", status=404)

        def generate():
            while True:
                frame = processor.queue.get()
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')