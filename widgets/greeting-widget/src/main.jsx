import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);


// import React from "react";
// import { createRoot } from "react-dom/client";
//
// function GreetingWidget({ name }) {
//   return (
//     <div style={{
//       fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial",
//       padding: 16,
//       borderRadius: 8,
//       border: "1px solid #e6e6e6",
//       background: "#fafafa"
//     }}>
//       <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>👋 React Greeting Widget</div>
//       <div>Hello, <strong>{name}</strong>!</div>
//     </div>
//   );
// }
//
// function mountFromWindowOpenAI() {
//   const rootEl = document.getElementById("root");
//   if (!rootEl) return;
//
//   const tryRender = () => {
//     const output = window.openai?.toolOutput;
//     const meta = window.openai?.toolResponseMetadata;
//     const name = meta?.structuredContent?.name ?? (output?.text ?? "friend");
//
//     createRoot(rootEl).render(<GreetingWidget name={name} />);
//   };
//
//   tryRender();
//
//   window.addEventListener && window.addEventListener("openai-tool-output-update", tryRender);
// }
//
// mountFromWindowOpenAI();
