import { useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  CardHeader,
  TextField,
  InputAdornment,
  Alert,
  Chip,
  Paper,
} from '@mui/material'
import { api } from '../api'
import { Search, FileText, Clock } from 'lucide-react'

export default function KnowledgePage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const data = await api.searchKnowledge(query, 10)
      setResults(data.results ?? [])
    } catch (err: any) {
      setError(err.message || 'Chyba při vyhledávání')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.5px', mb: 0.5 }}>
          Znalostní báze
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Vyhledávání v kurátovaných záznamech a FaceModel vzorech.
        </Typography>
      </Box>

      <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'background.paper', mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' }, alignItems: 'stretch' }}>
            <TextField
              fullWidth
              sx={{ flex: 1, minWidth: 0, '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleSearch() }}
              placeholder="Hledat v znalostní bázi…"
              variant="outlined"
              size="medium"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search size={18} />
                  </InputAdornment>
                ),
              }}
            />
            <Button
              onClick={handleSearch}
              disabled={loading}
              variant="contained"
              startIcon={<FileText size={18} />}
              sx={{ height: 48, borderRadius: 3, fontWeight: 600, boxShadow: '0 4px 12px rgba(79,70,229,0.25)' }}
            >
              {loading ? 'Vyhledávám…' : 'Vyhledat'}
            </Button>
          </Box>
          {error && (
            <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          )}
          {loading && !error && (
            <Box sx={{ mt: 3, display: 'flex', alignItems: 'center', gap: 1, color: '#64748b' }}>
              <Clock size={16} /> <Typography variant="body2">Vyhledávám…</Typography>
            </Box>
          )}
        </CardContent>
      </Card>
      {results.length > 0 && (
        <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'background.paper' }}>
          <CardHeader
            title="Výsledky vyhledávání"
            subheader={results.length + ' záznamů'}
            sx={{ pb: 1, borderBottom: '1px solid rgba(0,0,0,0.04)' }}
            titleTypographyProps={{ fontWeight: 600, fontSize: '1.0625rem' }}
            subheaderTypographyProps={{ fontSize: '0.875rem', color: '#64748b' }}
          />
          <CardContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {results.map((r, i) => (
                <Paper key={i} sx={{ p: 2, borderRadius: 2, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'common.white' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.9375rem', color: '#0f172a' }}>
                      {r.title || 'Bez názvu'}
                    </Typography>
                    <Chip label={r.source || '—'} size="small" variant="outlined" sx={{ fontSize: '0.75rem' }} />
                  </Box>
                  <Typography variant="body2" sx={{ color: '#64748b', fontSize: '0.875rem', whiteSpace: 'pre-wrap', mb: 0 }}>
                    {r.content || ''}
                  </Typography>
                </Paper>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}
    </Container>
  )
}