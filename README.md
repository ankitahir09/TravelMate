# TravelMate

TravelMate is an AI-powered travel planning application that helps users create personalized trip itineraries and connect with local vendors. The app features a conversational AI interface built with LangGraph and Google's Gemini model, a modern React frontend, and a FastAPI backend with MongoDB integration.

## Screenshots: 
Landing Page:
![Picture1](https://github.com/user-attachments/assets/301b4496-d402-45cb-8922-8c0cfb5a5d03)


Chat Page:
![Picture2](https://github.com/user-attachments/assets/76a3507e-89ba-496a-9e3c-b99ccc1e1281)
![Picture3](https://github.com/user-attachments/assets/07e6318e-80a6-423b-a226-152e949c93e3)
![Picture4](https://github.com/user-attachments/assets/f926c7c8-12e8-4bac-ab72-c387cdd0a320)


Add Vendor Page:

![Picture7](https://github.com/user-attachments/assets/6ef226f3-0091-46dc-94a4-ecfec1b1727d)


Code Snippet:
![Picture5](https://github.com/user-attachments/assets/5cb18a61-395e-4a02-9aa9-fbd6fc0a4760)
![Picture6](https://github.com/user-attachments/assets/0f885f21-2cd8-4ad6-9e21-b8b559d904e5)

## Features

- **AI-Powered Trip Planning**: Interactive chat interface using LangGraph and Gemini AI to generate customized itineraries based on destination, duration, and interests.
- **Vendor Management**: Register and discover local vendors (drivers, restaurants, artworks, etc.) stored in MongoDB.
- **Modern UI**: Responsive React frontend with Tailwind CSS styling.
- **RESTful API**: FastAPI backend providing endpoints for chat and vendor operations.

## Project Structure

```
TravelMate/
├── LICENSE
├── project-t/                          # Frontend (React + Vite)
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── chatui.jsx             # Chat interface for trip planning
│   │   │   ├── CreateVendor.jsx       # Vendor registration form
│   │   │   └── LandingPage.jsx        # Welcome page
│   │   ├── App.jsx                    # Main app component with routing
│   │   ├── main.jsx                   # React entry point
│   │   └── index.css                  # Global styles
│   ├── package.json                   # Frontend dependencies
│   ├── vite.config.js                 # Vite configuration
│   └── tailwind.config.js             # Tailwind CSS configuration
└── Tourism_LangGraph_Backend-main/    # Backend (FastAPI + LangGraph)
    ├── main.py                        # FastAPI app with LangGraph agent
    ├── database.py                    # MongoDB connection and vendor operations
    ├── .env                           # Environment variables (GOOGLE_API_KEY)
    └── __pycache__/                   # Python cache
```

## Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- MongoDB (running locally on port 27017)
- Google Gemini API key

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd Tourism_LangGraph_Backend-main
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pymongo langchain-google-genai python-dotenv
   ```

4. Set up environment variables:
   - Create a `.env` file in the backend directory
   - Add your Google Gemini API key: `GOOGLE_API_KEY=your_api_key_here`

5. Ensure MongoDB is running locally.

6. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd project-t
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

## Usage

1. Open the frontend in your browser.
2. On the landing page, click "Start Chat" to begin planning your trip.
3. Interact with the AI chat to provide destination, duration, and interests.
4. The AI will generate a personalized itinerary.
5. Use "Add Vendor" to register local service providers.
6. Vendors can be discovered through the chat interface.

## API Endpoints

- `POST /chat`: Send chat messages to the AI agent
- `POST /vendors`: Create a new vendor
- `GET /vendors`: Retrieve all vendors
- `GET /vendors/{id}`: Get vendor by ID
- `GET /vendors/type/{type}`: Get vendors by type
- `GET /vendors/city/{city}/type/{type}`: Get vendors by city and type

## Technologies Used

- **Frontend**: React, Vite, Tailwind CSS, Axios, React Router, React Markdown
- **Backend**: FastAPI, LangGraph, LangChain, Google Gemini AI
- **Database**: MongoDB
- **AI/ML**: Google's Gemini 1.5 Flash model

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the terms specified in the LICENSE file.

## Acknowledgments

- Built with LangGraph for AI agent orchestration
- Powered by Google's Gemini AI model
- UI styled with Tailwind CSS</content>
