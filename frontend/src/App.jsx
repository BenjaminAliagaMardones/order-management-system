import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from '@/components/Sidebar'
import Dashboard from '@/pages/Dashboard'
import Clientes from '@/pages/Clientes'
import Pedidos from '@/pages/Pedidos'
import NuevoPedido from '@/pages/NuevoPedido'
import DetallePedido from '@/pages/DetallePedido'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <div className="main-content">
            <Routes>
              <Route path="/" index element={<Dashboard />} />
              <Route path="/clientes" element={<Clientes />} />
              <Route path="/pedidos" element={<Pedidos />} />
              <Route path="/pedidos/nuevo" element={<NuevoPedido />} />
              <Route path="/pedidos/:id" element={<DetallePedido />} />
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  )
}
