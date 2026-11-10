import React from "react";

function App() {
    return (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <h1>Vítejte v Causa</h1>
            <p>Lokální, auditovatelná platforma pro firemní rozhodování</p>
            
            <div style={{ margin: '2rem 0', padding: '1rem', background: '#f0f0f0', borderRadius: '8px' }}>
                <h2>API Status</h2>
                <p>Backend API: <span style="color: green">running on http://localhost:8000</span></p>
                <p>Ollama LLM: <span style="color: green">available on port 11434</span></p>
            </div>
            
            <div>
                <h2>K dispozici</h2>
                <ul>
                    <li>Správa případů (/cases)</li>
                    <li>Agenti (/agents)</li>
                    <li>Knowledge base (/knowledge)</li>
                    <li>Quant engine (/quant)</li>
                </ul>
            </div>
        </div>
    );
}

export default App;