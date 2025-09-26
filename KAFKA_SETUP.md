# Kafka Setup Guide for Clinisight

## Prerequisites
- Java 8+ installed on your system
- Python virtual environment activated

## Step 1: Download and Setup Kafka

1. Download Kafka from the official website:
   ```
   https://kafka.apache.org/downloads
   ```
   Download the binary for Scala 2.13 (e.g., kafka_2.13-3.6.0.tgz)

2. Extract the downloaded file to a folder (e.g., `C:\kafka`)

## Step 2: Start Kafka Services

### Option A: Using Kafka with Zookeeper (Traditional)

1. **Start Zookeeper** (in first terminal):
   ```powershell
   cd C:\kafka
   .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
   ```

2. **Start Kafka Server** (in second terminal):
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-server-start.bat .\config\server.properties
   ```

### Option B: Using KRaft Mode (Kafka without Zookeeper)

1. **Generate cluster UUID**:
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-storage.bat random-uuid
   ```

2. **Format storage directories**:
   ```powershell
   .\bin\windows\kafka-storage.bat format -t <UUID-from-step-1> -c .\config\kraft\server.properties
   ```

3. **Start Kafka server**:
   ```powershell
   .\bin\windows\kafka-server-startup.bat .\config\kraft\server.properties
   ```

## Step 3: Create Required Kafka Topics

Open a new terminal and create the topics used by Clinisight:

```powershell
cd C:\kafka

# Create video-frames topic
.\bin\windows\kafka-topics.bat --create --topic video-frames --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Create alerts topic
.\bin\windows\kafka-topics.bat --create --topic alerts --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Verify topics were created
.\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
```

## Step 4: Environment Configuration

Create a `.env` file in your Clinisight project root:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
DATABASE_URL=postgresql://username:password@localhost:5432/clinisight
GEMINI_API_KEY=your_gemini_api_key_here
```

## Step 5: Start the Clinisight Application

1. **Start the backend Flask application**:
   ```powershell
   cd C:\Users\VICTUS\Clinisight
   C:/Users/VICTUS/Clinisight/venv/Scripts/python.exe app.py
   ```

2. **Start the frontend React application** (in another terminal):
   ```powershell
   cd C:\Users\VICTUS\Clinisight\frontend
   npm start
   ```

## Step 6: Testing the Setup

### Monitor Kafka Topics (Optional)

You can monitor the topics to see the data flow:

**Monitor video frames**:
```powershell
cd C:\kafka
.\bin\windows\kafka-console-consumer.bat --topic video-frames --from-beginning --bootstrap-server localhost:9092
```

**Monitor alerts**:
```powershell
cd C:\kafka
.\bin\windows\kafka-console-consumer.bat --topic alerts --from-beginning --bootstrap-server localhost:9092
```

## Architecture Overview

```
[Video Source] → [VideoProcessor] → [Kafka: video-frames] → [Flask API: /api/stream]
                      ↓
               [AlertManager] → [Kafka: alerts] → [Flask API: alerts endpoint]
```

1. **VideoProcessor**: Captures video frames, processes them with YOLO, and publishes to Kafka
2. **Kafka Topics**: 
   - `video-frames`: Stores processed video frames
   - `alerts`: Stores detection alerts
3. **Flask API**: Consumes from Kafka topics and serves data to frontend
4. **React Frontend**: Displays video stream and alerts

## Troubleshooting

### Common Issues:

1. **Port 9092 already in use**: Stop any existing Kafka instances
2. **Java not found**: Ensure Java 8+ is installed and in PATH
3. **Connection refused**: Verify Kafka server is running on localhost:9092
4. **Topic not found**: Ensure topics are created before starting the application

### Useful Kafka Commands:

```powershell
# List all topics
.\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

# Delete a topic
.\bin\windows\kafka-topics.bat --delete --topic topic-name --bootstrap-server localhost:9092

# Describe a topic
.\bin\windows\kafka-topics.bat --describe --topic video-frames --bootstrap-server localhost:9092
```

## Performance Tips

1. **Adjust frame skip rate**: Modify `frame_skip` in VideoProcessor for better performance
2. **Tune Kafka**: Adjust `batch.size` and `linger.ms` in producer configuration
3. **Monitor resources**: Use Task Manager to monitor CPU and memory usage