import { Routes, Route, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import MarketPlace from "./pages/MarketPlace";
import Navbar from "./pages/Navbar";
import Login from "./pages/Login";

function App() {
  const { pathname } = useLocation();

  const shouldShowNavbar =
    !pathname.includes("/admin") && !pathname.includes("/login");

  return (
    <>
      <div>
        {shouldShowNavbar && <Navbar />}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />

          <Route path="/marketplace" element={<MarketPlace />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
