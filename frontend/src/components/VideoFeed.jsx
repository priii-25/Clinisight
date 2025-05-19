import React from 'react';

const VideoFeed = ({ roomId }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-medium">Room {roomId}</h3>
      <img
        src={`http://localhost:5000/api/stream?room=${roomId}`}
        alt={`Room ${roomId} Feed`}
        className="w-full h-64 object-cover rounded"
      />
    </div>
  );
};

export default VideoFeed;