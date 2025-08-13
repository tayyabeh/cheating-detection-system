# cheating-detection-system

cheating_detection_system/
├── 📁 api/
│   ├── 📄 main.py                    # FastAPI app entry point
│   ├── 📄 routes.py                  # All API routes
│   └── 📁 endpoints/
│       ├── 📄 __init__.py
│       ├── 📄 admin.py               # Admin authentication & session management
│       ├── 📄 student.py             # Student authentication & test taking
│       ├── 📄 monitoring.py          # Real-time monitoring endpoints
│       ├── 📄 violations.py          # Violation logging & reporting
│       └── 📄 downloads.py           # Screenshot & report downloads

├── 📁 detectors/                     # ✅ Your existing detector folder
│   ├── 📄 face_detector.py          # Returns: cheating, direction, count, duration
│   ├── 📄 gaze_detector.py          # Returns: cheating, direction, count, duration  
│   ├── 📄 object_detector.py        # Returns: person_count, objects, alerts
│   └── 📄 __init__.py

├── 📁 models/                        # Database models
│   ├── 📄 __init__.py
│   ├── 📄 database.py               # Database connection setup
│   ├── 📄 admin.py                  # Admin model
│   ├── 📄 student.py                # Student model
│   ├── 📄 session.py                # Test session model
│   ├── 📄 violation.py              # Violation logging model
│   └── 📄 schemas.py                # Pydantic models for API

├── 📁 services/                     # Business logic layer
│   ├── 📄 __init__.py
│   ├── 📄 auth_service.py           # Google OAuth & JWT handling
│   ├── 📄 session_service.py        # Session creation & management
│   ├── 📄 detection_service.py      # Combines all detector results
│   ├── 📄 violation_service.py      # Process & log violations
│   ├── 📄 screenshot_service.py     # Screenshot handling & cleanup
│   └── 📄 websocket_service.py      # Real-time communication

├── 📁 utils/                        # Utility functions
│   ├── 📄 __init__.py
│   ├── 📄 config.py                 # App configuration & settings
│   ├── 📄 security.py               # Password hashing, JWT utils
│   ├── 📄 file_utils.py             # File operations & cleanup
│   └── 📄 response_utils.py         # Standard API responses

├── 📁 storage/                      # Local file storage
│   ├── 📁 screenshots/              # Temporary screenshot storage
│   │   └── 📁 session_{id}/
│   │       └── 📁 student_{id}/
│   │           ├── 📄 violation_1.jpg
│   │           └── 📄 violation_2.jpg
│   └── 📁 temp/                     # Temporary files

├── 📁 websockets/                   # WebSocket handlers
│   ├── 📄 __init__.py
│   ├── 📄 student_monitor.py        # Student real-time monitoring
│   ├── 📄 admin_dashboard.py        # Admin live dashboard
│   └── 📄 connection_manager.py     # WebSocket connection management

├── 📁 background_tasks/             # Async background jobs
│   ├── 📄 __init__.py
│   ├── 📄 file_cleanup.py           # Auto-delete expired screenshots
│   ├── 📄 violation_processor.py    # Process violation data
│   └── 📄 session_monitor.py        # Monitor session status

├── 📁 middleware/                   # Custom middleware
│   ├── 📄 __init__.py
│   ├── 📄 cors.py                   # CORS configuration
│   ├── 📄 auth.py                   # Authentication middleware
│   └── 📄 rate_limit.py             # Rate limiting

├── 📁 tests/                        # Unit & integration tests
│   ├── 📄 __init__.py
│   ├── 📄 test_detectors.py         # Test your detector functions
│   ├── 📄 test_api.py               # Test API endpoints
│   └── 📄 test_websockets.py        # Test real-time features

├── 📁 frontend/                     # Your existing frontend
├── 📁 pipeline/                     # Your existing pipeline
├── 📁 __pycache__/                  # Python cache

├── 📄 main.py                       # Your existing main file
├── 📄 requirements.txt              # Dependencies
├── 📄 .gitignore
├── 📄 README.md
└── 📄 .env                          # Environment variables

# Key Integration Points:

📊 DETECTOR INTEGRATION:
services/detection_service.py will combine all your detector results:
- face_detector.py → cheating status & face tracking
- gaze_detector.py → gaze direction & attention
- object_detector.py → person count & object detection

📡 API FLOW:
Student Extension → API Endpoints → Detection Service → Your Detectors → Database

📱 REAL-TIME FLOW:
Extension → WebSocket → Violation Service → Admin Dashboard

📁 FILE FLOW:
Screenshot → storage/screenshots/ → Admin Download → Auto Cleanup

🔄 BACKGROUND TASKS:
- Process detector results
- Clean up old screenshots  
- Monitor session timeouts