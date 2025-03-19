import React, { useState } from "react";

const App = () => {
  const [prize, setPrize] = useState(undefined);

  const openMysteryBox = () => {
    setPrize("Teddy Bear");
  };

  return (
    <div>
      <h1>Mystery Box</h1>
      <p>{prize !== undefined ? prize : ""}</p>
      <button onClick={openMysteryBox}>Open</button>
    </div>
  );
};

export default App;