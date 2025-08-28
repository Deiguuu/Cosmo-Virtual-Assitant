import { useState } from "react";
import { Mic, MicOff, Power, MoreHorizontal, AlertTriangle } from "lucide-react";
import "../assets/cosmo.css";

export default function CosmoAssistant() {
    const [active, setActive] = useState(false);
    const [micOn, setMicOn] = useState(false);
    const [status, setStatus] = useState("INACTIVO");

    const toggleAssistant = () => {
        console.log("[REACT] Intentando ejecutar el asistente");

        try {
            // Llama a la función expuesta desde preload
            window.api.ejecutarAsistente();

            setStatus("ACTIVO");
            setActive(true);
            console.log("[REACT] Asistente iniciado");
        } catch (e) {
            console.error("[REACT] Error al ejecutar el asistente:", e);
            setStatus("ERROR");
        }
    };

    return (
        <div className="cosmo-container">
            <div className="cosmo-title">Cosmo Assistant Preview</div>

            <div className={`cosmo-panel ${active ? "active" : ""}`}>
                <div className="cosmo-controls">
                    {/* Botón Mic */}
                    <button
                        onClick={() => setMicOn(!micOn)}
                        className={`cosmo-btn ${micOn ? "mic-on" : "mic-off"}`}
                    >
                        {micOn ? <Mic /> : <MicOff />}
                    </button>

                    {/* Botón Power */}
                    <button
                        onClick={toggleAssistant}
                        className="cosmo-btn power"
                    >
                        <Power />
                    </button>

                    {/* Botón Opciones */}
                    <button className="cosmo-btn options">
                        <MoreHorizontal />
                    </button>
                </div>
            </div>

            {/* Notificación de estado */}
            <div className={`cosmo-notification ${active ? "active" : "inactive"}`}>
                <span>COSMO ASSISTANT - {status}</span>
                <AlertTriangle />
            </div>
        </div>
    );
}
