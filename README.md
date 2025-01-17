# Face Analysis System

A real-time facial analysis system that provides comprehensive facial feature assessment and metrics calculation. Built with Vue.js frontend and FastAPI backend.

## Project Structure

```
FaceAnalysis/
├─ client/             # Frontend Vue.js application
│  ├─ src/
│  │  ├─ components/  # Vue components
│  │  ├─ assets/     # Static assets
│  │  ├─ App.vue    # Root component
│  │  └─ main.js    # Application entry
│  └─ package.json   # Frontend dependencies
│
└─ server/            # Backend FastAPI application
   ├─ app/
   │  ├─ api/        # API routes and dependencies
   │  ├─ core/       # Core business logic
   │  ├─ schemas/    # Data models
   │  └─ utils/      # Utility functions
   └─ requirements.txt # Backend dependencies
```

## Features

- Real-time facial feature detection and analysis
- WebSocket-based video streaming
- Multiple facial metrics calculation:
  - Face symmetry analysis
  - Golden ratio measurements
  - Face shape classification
  - Three-section facial proportions
  - Eye measurements and angles
  - Overall facial harmony score
- Interactive visualization of results

## Prerequisites

- Python 3.9+
- Node.js 16+
- Webcam device
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/face-analysis.git
cd face-analysis
```

2. Start the backend server:
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
./scripts/start.sh
```

3. Start the frontend application:
```bash
cd client
npm install
npm run serve
```

4. Open your browser and visit: `http://localhost:8080`

## Development

### Backend Development
- Located in `/server`
- FastAPI for API endpoints
- MediaPipe for facial landmark detection
- WebSocket support for real-time communication

Run development server:
```bash
cd server
./scripts/start.sh
```

Access API documentation at `http://localhost:8000/docs`

### Frontend Development
- Located in `/client`
- Vue.js 3.x framework
- Real-time webcam integration
- Interactive data visualization

Run development server:
```bash
cd client
npm run serve
```

## Production Deployment

1. Build frontend:
```bash
cd client
npm run build
```

2. Deploy backend:
```bash
cd server
./scripts/start.sh
```

## Configuration

### Frontend Configuration
- Vue configuration: `client/vue.config.js`
- Environment variables: `client/.env`

### Backend Configuration
- FastAPI settings: `server/app/config.py`
- Environment variables: `server/.env`

## Testing

### Backend Tests
```bash
cd server
./scripts/test.sh
```

### Frontend Tests
```bash
cd client
npm run test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Add license information]

## Authors

[Add author information]

## Acknowledgments

- MediaPipe for facial landmark detection
- Vue.js team
- FastAPI team

## Support

For issues and feature requests, please use the GitHub issue tracker or contact the maintainers.