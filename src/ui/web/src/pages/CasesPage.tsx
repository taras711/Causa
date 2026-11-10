import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Alert, Box, Button, Card, CardContent, Chip, Container, FormControl, InputLabel,
  MenuItem, Pagination, Select, Stack, TextField, Typography,
} from '@mui/material'
import { ArrowRight, FilePlus2, Search } from 'lucide-react'
import { api } from '../api'

type CaseSummary = {
  case_id: string
  title: string
  tenant_id: string
  status: string
  created_at: string
}

const statusLabels: Record<string, string> = {
  draft: 'Koncept', running: 'Probíhá', completed: 'Dokončeno', failed: 'Chyba', paused: 'Pozastaveno',
}

export default function CasesPage() {
  const [cases, setCases] = useState<CaseSummary[]>([])
  const [query, setQuery] = useState('')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pageSize = 20

  useEffect(() => {
    let active = true
    setLoading(true)
    api.listCases({ page, page_size: pageSize, q: search, status })
      .then((data: { cases: CaseSummary[]; total: number }) => {
        if (active) { setCases(data.cases); setTotal(data.total); setError(null) }
      })
      .catch((err: Error) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [page, search, status])

  const submitSearch = (event: React.FormEvent) => {
    event.preventDefault()
    setPage(1)
    setSearch(query.trim())
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ sm: 'center' }} spacing={2} sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Případy</Typography>
          <Typography color="text.secondary">Vyhledávání a správa analytických případů ({total})</Typography>
        </Box>
        <Button component={Link} to="/cases/new" variant="contained" startIcon={<FilePlus2 size={18} />}>Nový případ</Button>
      </Stack>

      <Card sx={{ border: '1px solid rgba(0,0,0,0.06)', borderRadius: 3 }}>
        <CardContent>
          <Stack component="form" onSubmit={submitSearch} direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
            <TextField
              fullWidth size="small" label="Hledat podle názvu nebo ID" value={query}
              onChange={(event) => setQuery(event.target.value)} inputProps={{ maxLength: 200 }}
            />
            <FormControl size="small" sx={{ minWidth: { sm: 190 } }}>
              <InputLabel id="case-status-label">Stav</InputLabel>
              <Select labelId="case-status-label" label="Stav" value={status} onChange={(event) => { setStatus(event.target.value); setPage(1) }}>
                <MenuItem value="">Všechny stavy</MenuItem>
                {Object.entries(statusLabels).map(([value, label]) => <MenuItem key={value} value={value}>{label}</MenuItem>)}
              </Select>
            </FormControl>
            <Button type="submit" variant="outlined" startIcon={<Search size={16} />}>Hledat</Button>
          </Stack>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {loading ? <Typography color="text.secondary" sx={{ py: 5, textAlign: 'center' }}>Načítám případy…</Typography> : (
            <Stack spacing={1}>
              {cases.length === 0 ? (
                <Typography color="text.secondary" sx={{ py: 5, textAlign: 'center' }}>Žádné případy neodpovídají hledání.</Typography>
              ) : cases.map((item) => (
                <Box key={item.case_id} sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center', justifyContent: 'space-between', p: 2, border: '1px solid rgba(0,0,0,0.08)', borderRadius: 2 }}>
                  <Box sx={{ minWidth: 0, flex: '1 1 260px' }}>
                    <Typography component={Link} to={`/cases/${item.case_id}`} sx={{ fontWeight: 600, color: 'text.primary', textDecoration: 'none', '&:hover': { color: 'primary.main' } }}>{item.title}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace', overflowWrap: 'anywhere' }}>{item.case_id}</Typography>
                  </Box>
                  <Chip size="small" label={statusLabels[item.status] ?? item.status} variant="outlined" />
                  <Typography variant="body2" color="text.secondary" sx={{ minWidth: 140 }}>{new Date(item.created_at).toLocaleDateString('cs-CZ')}</Typography>
                  <Button component={Link} to={`/cases/${item.case_id}`} endIcon={<ArrowRight size={16} />}>Otevřít</Button>
                </Box>
              ))}
              {total > pageSize && <Pagination count={Math.ceil(total / pageSize)} page={page} onChange={(_, value) => setPage(value)} sx={{ display: 'flex', justifyContent: 'center', pt: 2 }} />}
            </Stack>
          )}
        </CardContent>
      </Card>
    </Container>
  )
}
