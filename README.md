cheating_detection_system/
├── 📁 api/                     # FastAPI application
│   ├── main.py                 # App entry point
│   ├── routes.py               # All API routes
│   └── 📁 endpoints/
│       ├── __init__.py
│       ├── admin.py            # Admin authentication & session management
│       ├── student.py          # Student authentication & test taking
│       ├── monitoring.py       # Real-time monitoring endpoints
│       ├── violations.py       # Violation logging & reporting
│       └── downloads.py        # Screenshot & report downloads
│
├── 📁 detectors/               # Computer vision detectors
│   ├── face_detector.py        # Cheating detection via face tracking
│   ├── gaze_detector.py        # Gaze tracking & attention analysis
│   ├── object_detector.py      # Person count & object detection
│   └── __init__.py
│
├── 📁 models/                  # Database models
│   ├── __init__.py
│   ├── database.py             # DB connection setup
│   ├── admin.py                # Admin model
│   ├── student.py              # Student model
│   ├── session.py              # Test session model
│   ├── violation.py            # Violation logging model
│   └── schemas.py              # Pydantic schemas
│
├── 📁 services/                # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py         # Google OAuth & JWT handling
│   ├── session_service.py      # Session creation & management
│   ├── detection_service.py    # Combines detector results
│   ├── violation_service.py    # Process & log violations
│   ├── screenshot_service.py   # Screenshot handling
│   └── websocket_service.py    # Real-time communication
│
├── 📁 utils/                   # Utilities
│   ├── __init__.py
│   ├── config.py               # App configuration
│   ├── security.py             # Password hashing, JWT utils
│   ├── file_utils.py           # File operations
│   └── response_utils.py       # Standard API responses
│
├── 📁 storage/                 # Local file storage
│   ├── 📁 screenshots/         # Screenshots per session
│   │   └── session_{id}/student_{id}/violation_1.jpg
│   └── 📁 temp/                # Temporary files
│
├── 📁 websockets/              # WebSocket handlers
│   ├── __init__.py
│   ├── student_monitor.py      # Student real-time monitoring
│   ├── admin_dashboard.py      # Admin live dashboard
│   └── connection_manager.py   # Connection management
│
├── 📁 background_tasks/        # Async background jobs
│   ├── __init__.py
│   ├── file_cleanup.py         # Auto-delete expired screenshots
│   ├── violation_processor.py  # Process violation data
│   └── session_monitor.py      # Monitor session status
│
├── 📁 middleware/              # Custom middleware
│   ├── __init__.py
│   ├── cors.py                 # CORS configuration
│   ├── auth.py                 # Authentication middleware
│   └── rate_limit.py           # Rate limiting
│
├── 📁 tests/                   # Unit & integration tests
│   ├── __init__.py
│   ├── test_detectors.py       # Detector tests
│   ├── test_api.py             # API endpoint tests
│   └── test_websockets.py      # WebSocket tests
│
├── 📁 frontend/                # Frontend app
├── 📁 pipeline/                # Detection pipeline
├── 📁 __pycache__/             # Python cache
│
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
├── .gitignore
├── README.md
└── .env                        # Environment variables
