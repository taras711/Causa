import { useState } from 'react'
import { Box, Container, Typography, Button, Card, CardContent, Alert, TextField } from '@mui/material'
import { api } from '../api'
import { BarChart3, Play, TrendingUp } from 'lucide-react'

export default function QuantPage() {
  const [inputs, setInputs] = useState({ investment: 100000, annual_return: 30000, years: 5, discount_rate: 0.08 })
  const [roiResult, setRoiResult] = useState<unknown>(null)
  const [sensitivityResult, setSensitivityResult] = useState<unknown>(null)
  const [mcResult, setMcResult] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleROI = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.quantROI(inputs)
      setRoiResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chyba při výpočtu ROI')
    } finally {
      setLoading(false)
    }
  }

  const handleSensitivity = async () => {
    setLoading(true)
    setError(null)
    try {
      const { annual_return, discount_rate } = inputs
      const data = await api.quantSensitivity({
        base_case: inputs,
        variations: [
          { name: 'Roční výnos −20 %', changes: { annual_return: annual_return * 0.8 } },
          { name: 'Roční výnos +20 %', changes: { annual_return: annual_return * 1.2 } },
          { name: 'Diskontní sazba −2 p. b.', changes: { discount_rate: Math.max(-0.99, discount_rate - 0.02) } },
          { name: 'Diskontní sazba +2 p. b.', changes: { discount_rate: discount_rate + 0.02 } },
        ],
      })
      setSensitivityResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chyba při citlivostní analýze')
    } finally {
      setLoading(false)
    }
  }

  const handleMonteCarlo = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.quantMonteCarlo({
        model: {
          investment_range: [inputs.investment * 0.8, inputs.investment * 1.2],
          annual_return_range: [inputs.annual_return * 0.7, inputs.annual_return * 1.3],
          discount_rate_range: [Math.max(-0.99, inputs.discount_rate - 0.02), inputs.discount_rate + 0.02],
          years: inputs.years,
        },
        iterations: 1000,
      })
      setMcResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chyba při simulaci')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.5px', mb: 0.5 }}>
          Quant Engine
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Deterministické výpočty ROI, citlivostní analýza a Monte Carlo simulace.
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Vstupní předpoklady</Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, minmax(0, 1fr))', lg: 'repeat(4, minmax(0, 1fr))' }, gap: 2 }}>
            <TextField label="Investice" type="number" value={inputs.investment} inputProps={{ min: 1 }} onChange={(e) => setInputs({ ...inputs, investment: Number(e.target.value) })} />
            <TextField label="Roční výnos / cash flow" type="number" value={inputs.annual_return} onChange={(e) => setInputs({ ...inputs, annual_return: Number(e.target.value) })} />
            <TextField label="Doba (roky)" type="number" value={inputs.years} inputProps={{ min: 1, max: 10000, step: 1 }} onChange={(e) => setInputs({ ...inputs, years: Number(e.target.value) })} />
            <TextField label="Diskontní sazba (0,08 = 8 %)" type="number" value={inputs.discount_rate} inputProps={{ step: 0.01 }} onChange={(e) => setInputs({ ...inputs, discount_rate: Number(e.target.value) })} />
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: 'minmax(0, 1fr)', lg: 'repeat(3, minmax(0, 1fr))' }, gap: 3, alignItems: 'start' }}>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Výpočet ROI</Typography>
            <Button disabled={loading} onClick={handleROI} variant="contained" startIcon={<BarChart3 size={18} />}>
              Spočítat ROI
            </Button>
            {roiResult !== null && (
              <Box component="pre" sx={{ mt: 2, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
                {JSON.stringify(roiResult, null, 2)}
              </Box>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Citlivostní analýza</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Porovnání změn výnosu a diskontní sazby vůči základnímu scénáři.
            </Typography>
            <Button disabled={loading} onClick={handleSensitivity} variant="contained" startIcon={<TrendingUp size={18} />}>
              Analyzovat scénáře
            </Button>
            {sensitivityResult !== null && (
              <Box component="pre" sx={{ mt: 2, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
                {JSON.stringify(sensitivityResult, null, 2)}
              </Box>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Monte Carlo simulace</Typography>
            <Button disabled={loading} onClick={handleMonteCarlo} variant="contained" startIcon={<Play size={18} />}>
              Spustit simulaci
            </Button>
            {mcResult !== null && (
              <Box component="pre" sx={{ mt: 2, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
                {JSON.stringify(mcResult, null, 2)}
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}