import { useEffect, useState } from "react";

export default function App() {
  const [name, setName] = useState("");

  useEffect(() => {
    const output = window.openai?.toolOutput;
    const meta = window.openai?.toolResponseMetadata;
    if (meta?.structuredContent?.name) {
      setName(meta.structuredContent.name);
    }
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: "20px" }}>
      <h1>Hello {name || "friend"} </h1>
      <p>This is a React + Vite widget rendered by MCP!</p>
    </div>
  );
}