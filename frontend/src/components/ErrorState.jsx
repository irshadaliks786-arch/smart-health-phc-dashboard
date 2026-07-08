import React from "react";

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="error-state">
      <p>Couldn't load this section: {message}</p>
      <button onClick={onRetry}>Retry</button>
    </div>
  );
}
