import React from "react";
import DistrictSummary from "./components/DistrictSummary.jsx";
import PhcTable from "./components/PhcTable.jsx";
import RedistributionList from "./components/RedistributionList.jsx";
import InsightsPanel from "./components/InsightsPanel.jsx";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>PHC/CHC Health Ops Dashboard</h1>
        <p className="subtitle">
          Rohtak · Jhajjar · Sonipat · Panipat · Karnal — deterministic analytics,
          Google-only AI layer
        </p>
      </header>
      <main>
        <DistrictSummary />
        <InsightsPanel />
        <PhcTable />
        <RedistributionList />
      </main>
    </div>
  );
}
