import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { createTheme, CssBaseline, ThemeProvider } from '@mui/material'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#4f46e5' },
    background: { default: '#f5f7fb', paper: '#ffffff' },
    text: { primary: '#172033', secondary: '#64748b' },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    button: { textTransform: 'none', fontWeight: 600 },
  },
})
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CasesPage from './pages/CasesPage'
import CasePage from './pages/CasePage'
import CaseForm from './pages/CaseForm'
import KnowledgePage from './pages/KnowledgePage'
import QuantPage from './pages/QuantPage'

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cases/new" element={<CaseForm />} />
            <Route path="/cases" element={<CasesPage />} />
            <Route path="/cases/:caseId" element={<CasePage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="/quant" element={<QuantPage />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  )
}