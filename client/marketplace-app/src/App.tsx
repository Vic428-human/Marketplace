import { Routes, Route, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import MarketPlace from "./pages/MarketPlace";
import Navbar from "./pages/Navbar";

function App() {
  const { pathname } = useLocation();

  return (
    <>
      <div>
        {!pathname.includes("/admin") && (
          <>
            <Navbar />
          </>
        )}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/marketplace" element={<MarketPlace />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
