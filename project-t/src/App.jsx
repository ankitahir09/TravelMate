import { Routes, Route } from "react-router-dom";
import ChatUI from './pages/chatui';
import CreateVendor from './pages/CreateVendor';
import LandingPage from './pages/LandingPage';
import './index.css';


function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/chat" element={<ChatUI />} />
      <Route path="/vendor" element={<CreateVendor />} />
    </Routes>
  );
}

export default App;
