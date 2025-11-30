# Weather Monitoring System - Documentation Index

Welcome to the Weather Monitoring System documentation! This guide will help you navigate through all available documentation.

## 📚 Documentation Structure

### Getting Started
- **[README.md](../README.md)** - Main project overview and quick start guide
- **[QUICK_START.md](./QUICK_START.md)** - Step-by-step guide to get the project running
- **[SETUP.md](./SETUP.md)** - Detailed setup instructions for development

### Project Information
- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - Comprehensive project structure and organization
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design patterns
- **[STATUS.md](./STATUS.md)** - Current project status and progress

### Technical Guides
- **[PYTHON_313_FIX.md](./PYTHON_313_FIX.md)** - Python 3.13 compatibility fixes
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick reference for common commands

## 🎯 Key Features

### Theme System
The application features a sophisticated dual-theme system:
- **Dark Theme** (Default): Black to dark blue gradient with semi-transparent cards
- **Light Theme**: Vibrant purple gradient with white cards
- **Toggle Control**: Custom sun/moon slider with smooth animations
- **Persistence**: Theme preference saved in browser localStorage

### Dashboard Components

#### 1. Temperature Gauge
- Circular SVG-based visualization
- Real-time temperature display
- Min/max temperature markers
- Weather condition icons

#### 2. Hourly Chart
- Last 8 hours of temperature data
- Temperature values on bars
- Animated transitions
- Interactive hover effects

#### 3. Highlight Cards (6 Metrics)
- Pressure (hPa) - Orange glow
- Wind Status (km/h) - Cyan glow
- Sunrise & Sunset - Gold glow
- Humidity (%) - Light blue glow
- Visibility (km) - Green glow
- Cloud Cover (%) - Purple glow

#### 4. 7-Day Trend Chart
- Bar chart with max, avg, min temperatures
- Color-coded data series
- Custom tooltips
- Responsive design

#### 5. Weather Animations
Dynamic background effects:
- Rain: Falling raindrops
- Snow: Floating snowflakes
- Clouds: Drifting cloud shapes
- Sun: Glowing sun with pulse
- Fog: Layered fog effect

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **MongoDB** - NoSQL database with Motor async driver
- **Pydantic** - Data validation and settings management
- **Python 3.11+** - Latest Python features

### Frontend
- **React 18** - UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Material-UI** - Component library
- **Recharts** - Data visualization
- **Vite** - Fast build tool

## 📂 Project Organization

```
Weather_Python/
├── backend/          # Python FastAPI server
├── frontend/         # React TypeScript app
├── docs/             # Documentation (you are here)
├── scripts/          # Utility scripts
└── [config files]    # Root configuration
```

## 🚀 Quick Commands

### Backend
```bash
# Start development server
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Populate data
python scripts/populate_historical_data.py
python scripts/populate_data.py

# Run tests
python scripts/test_connection.py
python scripts/test_api_simple.py
python scripts/test_system.py
```

### Frontend
```bash
# Start development server
cd frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔧 Configuration

### Backend Environment Variables
```env
OPENWEATHER_API_KEY=your_api_key
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=weather_dashboard
LOG_LEVEL=INFO
```

### Frontend Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📊 Database Schema

### Collections
1. **weatherraw** - Raw weather data from API
2. **dashboardsummaries** - Pre-aggregated dashboard data
3. **alerts** - Weather alert records

## 🎨 Design System

### Color Palette

#### Dark Theme
- Background: `#0f0f0f` → `#1a1a2e` → `#16213e`
- Cards: `rgba(30, 30, 46, 0.6)`
- Text: `#FFFFFF`, `rgba(255, 255, 255, 0.6)`

#### Light Theme
- Background: `#667eea` → `#764ba2`
- Cards: `rgba(255, 255, 255, 0.85)`
- Text: `#1a1a2e`, `#64748B`

#### Metric Colors
- Pressure: `#FF6B35`
- Wind: `#00D9FF`
- Sunrise/Sunset: `#FFD700`
- Humidity: `#4FC3F7`
- Visibility: `#00E676`
- Cloud Cover: `#B388FF`

## 🐛 Troubleshooting

### Backend Issues
- **MongoDB connection failed**: Check MongoDB is running
- **Module not found**: Verify PYTHONPATH is set
- **Import errors**: Check virtual environment is activated

### Frontend Issues
- **Port in use**: Change port in vite.config.ts
- **API connection failed**: Verify backend is running
- **Build errors**: Clear node_modules and reinstall

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Aditya-Takawale/Weather_Python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Aditya-Takawale/Weather_Python/discussions)

## 👨‍💻 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenWeather API for weather data
- Material-UI for React components
- Recharts for data visualization
- FastAPI for the backend framework

---

**Last Updated**: November 30, 2025
**Version**: 1.0.0
**Author**: Aditya Takawale
