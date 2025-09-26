@echo off
echo Starting Kafka services for Clinisight...

REM Set Kafka directory - modify this path as needed
set KAFKA_HOME=C:\kafka_2.13-3.9.1

REM Check if Kafka directory exists
if not exist "%KAFKA_HOME%" (
    echo ERROR: Kafka directory not found at %KAFKA_HOME%
    echo Please download and extract Kafka, then update KAFKA_HOME in this script.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Zookeeper...
echo ========================================
start "Zookeeper" cmd /k "cd /d %KAFKA_HOME% && .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties"

REM Wait for Zookeeper to start
timeout /t 10

echo.
echo ========================================
echo Starting Kafka Server...
echo ========================================
start "Kafka Server" cmd /k "cd /d %KAFKA_HOME% && .\bin\windows\kafka-server-start.bat .\config\server.properties"

REM Wait for Kafka to start
timeout /t 15

echo.
echo ========================================
echo Creating Kafka Topics...
echo ========================================

REM Create video-frames topic
%KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic video-frames --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists

REM Create alerts topic
%KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic alerts --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists

echo.
echo ========================================
echo Listing all topics:
echo ========================================
%KAFKA_HOME%\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

echo.
echo ========================================
echo Kafka setup complete!
echo ========================================
echo.
echo You can now start the Clinisight application:
echo 1. Backend: python app.py
echo 2. Frontend: cd frontend && npm start
echo.
echo Press any key to exit...
pause > nul