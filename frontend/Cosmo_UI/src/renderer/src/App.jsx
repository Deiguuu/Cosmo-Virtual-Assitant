import CosmoAssistant from "./components/CosmoAssistant";
// si el archivo está en src/components/CosmoAssistant.jsx

function App() {
  const ipcHandle = () => window.electron.ipcRenderer.send('ping')

  return (
    <div>
      <CosmoAssistant />
    </div>
  )
}

export default App;
