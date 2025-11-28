import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import MarketPlace from "./pages/MarketPlace";

function App() {
  return (
    <>
      <div>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/marketplace" element={<MarketPlace />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
