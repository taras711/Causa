import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Alert,
  TableContainer,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material'
import { api } from '../api'
import { LayoutDashboard, Play, CheckCircle, Pencil, Trash2 } from 'lucide-react'

export default function CasePage() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState<any>(null)
  const [ledger, setLedger] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [running, setRunning] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editContext, setEditContext] = useState<Record<string, string>>({})

  const editableFields = [
    ['problem_statement', 'Popis problému'],
    ['desired_outcome', 'Požadovaný výsledek'],
    ['current_state', 'Současný stav'],
    ['scope', 'Rozsah a hranice'],
    ['impact', 'Dopad problému'],
    ['timeframe', 'Kdy a jak často se problém objevuje'],
    ['evidence_notes', 'Dostupná data a podklady'],
    ['previous_attempts', 'Co už se zkoušelo'],
    ['constraints', 'Omezení a důležité podmínky'],
    ['success_criteria', 'Kritéria úspěchu'],
  ] as const

  const openEdit = () => {
    setEditTitle(caseData.title)
    setEditContext(Object.fromEntries(editableFields.map(([key]) => [key, caseData.context?.[key] ?? ''])))
    setEditOpen(true)
  }

  const handleSave = async () => {
    if (!caseId) return
    setSaving(true)
    setError(null)
    try {
      const updated = await api.updateCase(caseId, { title: editTitle, context: editContext })
      setCaseData((current: any) => ({ ...current, ...updated }))
      setEditOpen(false)
    } catch (err: any) {
      setError(err.message || 'Případ se nepodařilo uložit.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!caseId) return
    setSaving(true)
    setError(null)
    try {
      await api.deleteCase(caseId)
      navigate('/')
    } catch (err: any) {
      setError(err.message || 'Případ se nepodařilo odstranit.')
      setDeleteOpen(false)
    } finally {
      setSaving(false)
    }
  }

  useEffect(() => {
    if (!caseId) return
    api.getCase(caseId)
      .then((data: any) => setCaseData(data))
      .catch((err: Error) => setError(err.message))

    api.getLedger(caseId)
      .then((data: any) => setLedger(data.entries ?? []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [caseId])

  const handleRun = async () => {
    if (!caseId) return
    setRunning(true)
    setError(null)
    try {
      const saveStage = async (key: string, value: any) => {
        const result = await api.updateCaseContext(caseId, { [key]: value })
        setCaseData((current: any) => ({ ...current, context: result.context }))
      }
      const context = caseData.context ?? {}
      const framing = await api.runAgent('framer', {
        case_title: caseData.title,
        problem_statement: context.problem_statement ?? '',
        context: { ...context, tenant_id: caseData.tenant_id },
      })
      await saveStage('framing', framing)

      const evidenceQuery = [
        framing.scope,
        context.problem_statement,
        context.desired_outcome,
        context.current_state,
        context.evidence_notes,
      ].filter(Boolean).join(' ')
      const evidence = await api.runAgent('evidence_retriever', {
        query: evidenceQuery,
        tenant_id: caseData.tenant_id,
        top_k: 5,
      })
      await saveStage('evidence', evidence)
      const evidenceTexts = (evidence.results ?? []).map((item: any) =>
        [item.title, item.content, item.source].filter(Boolean).join(' — '),
      )

      const diagnosis = await api.runAgent('diagnostician', {
        scope: framing.scope,
        evidence: evidenceTexts,
        context,
      })
      await saveStage('diagnosis', diagnosis)

      const solution = await api.runAgent('solution_designer', {
        root_causes: diagnosis.root_causes ?? [],
        evidence: evidenceTexts,
        context,
      })
      await saveStage('solution', solution)
    } catch (err: any) {
      setError(err.message || 'A3 analýzu se nepodařilo dokončit. Uložené fáze zůstávají zachované.')
    } finally {
      setRunning(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ height: 'calc(100vh - 80px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Načítám případ…
        </Typography>
      </Box>
    )
  }

  if (error && !caseData) {
    return (
      <Box sx={{ height: 'calc(100vh - 80px)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'error.main' }}>
        <Typography variant="body2">Chyba: {error}</Typography>
      </Box>
    )
  }

  if (!caseData) {
    return (
      <Box sx={{ height: 'calc(100vh - 80px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body2">Případ nenalezen.</Typography>
      </Box>
    )
  }

  const statusColor: Record<string, string> = {
    DONE: '#22c55e',
    RUNNING: '#f59e0b',
    FAILED: '#ef4444',
    DRAFT: '#64748b',
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.5px', mb: 0.5 }}>
            {caseData.title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {caseData.case_id} &nbsp;•&nbsp; Tenant: {caseData.tenant_id}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            label={caseData.status}
            sx={{
              bgcolor: (statusColor[caseData.status] || '#64748b') + '15',
              color: statusColor[caseData.status] || '#64748b',
              border: `1px solid ${(statusColor[caseData.status] || '#64748b')}33`,
              fontWeight: 600,
              fontSize: '0.8125rem',
              mr: 1,
            }}
          />
          <Button
            startIcon={<Pencil size={18} />}
            onClick={openEdit}
            disabled={running}
            variant="outlined"
            sx={{ height: 44, borderRadius: 3, fontWeight: 600 }}
          >
            Upravit
          </Button>
          <Button
            startIcon={<Trash2 size={18} />}
            onClick={() => setDeleteOpen(true)}
            disabled={running}
            color="error"
            variant="outlined"
            sx={{ height: 44, borderRadius: 3, fontWeight: 600 }}
          >
            Smazat
          </Button>
          <Button
            startIcon={<Play size={18} />}
            onClick={handleRun}
            disabled={running || !caseData.context?.problem_statement}
            variant="contained"
            sx={{
              height: 44,
              borderRadius: 3,
              fontWeight: 600,
              '&:disabled': { opacity: 0.5, cursor: 'not-allowed' },
              boxShadow: running ? 'none' : '0 4px 12px rgba(79,70,229,0.25)',
            }}
          >
            {running ? 'Probíhá A3…' : 'Spustit A3 analýzu'}
          </Button>
          <Link to="/">
            <Button variant="outlined" sx={{ height: 44, borderRadius: 3, fontWeight: 600 }}>
              Zpět
            </Button>
          </Link>
        </Box>
      </Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {!caseData.context?.problem_statement && (
        <Alert severity="warning" sx={{ mb: 3 }}>Případu chybí popis problému. Pro založení případu s A3 vstupy použijte formulář Nový případ.</Alert>
      )}
      <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', mb: 3 }}>
        <CardHeader title="A3 pracovní tok" subheader="Výstupy agentů se ukládají do kontextu případu po jednotlivých fázích." />
        <CardContent>
          <Grid container spacing={2}>
            {[
              ['Popis problému', caseData.context?.problem_statement],
              ['Požadovaný výsledek', caseData.context?.desired_outcome],
              ['Současný stav', caseData.context?.current_state],
              ['Rozsah a hranice', caseData.context?.scope],
              ['Dopad', caseData.context?.impact],
              ['Časový průběh', caseData.context?.timeframe],
              ['Data a podklady', caseData.context?.evidence_notes],
              ['Dosavadní pokusy', caseData.context?.previous_attempts],
              ['Omezení', caseData.context?.constraints],
              ['Kritéria úspěchu', caseData.context?.success_criteria],
              ['Vymezení a otázky', caseData.context?.framing],
              ['Nalezené důkazy', caseData.context?.evidence],
              ['Kořenové příčiny', caseData.context?.diagnosis],
              ['Návrhy řešení', caseData.context?.solution],
            ].filter(([, value]) => value !== undefined && value !== null && value !== '').map(([label, value]) => (
              <Grid item xs={12} md={6} key={label as string}>
                <Box sx={{ p: 2, height: '100%', border: '1px solid rgba(0,0,0,0.06)', borderRadius: 2, bgcolor: '#f8fafc' }}>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 700 }}>{label}</Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
                    {value ? JSON.stringify(value, null, 2) : 'Zatím bez výsledku.'}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
          <Alert severity="info" sx={{ mt: 2 }}>
            Finanční návratnost není součástí tohoto A3 toku. Pokud je pro navržené řešení relevantní, vyhodnoťte ji samostatně v Quant Engine.
          </Alert>
        </CardContent>
      </Card>
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'background.paper', overflow: 'hidden' }}>
            <CardHeader
              title="Zaznamenané výstupy"
              subheader="Doporučení a tvrzení, pokud je některá backendová fáze vytvořila"
              sx={{ pb: 1, borderBottom: '1px solid rgba(0,0,0,0.04)' }}
              titleTypographyProps={{ fontWeight: 600, fontSize: '1.0625rem' }}
              subheaderTypographyProps={{ fontSize: '0.875rem', color: '#64748b' }}
            />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Box sx={{ border: '1px solid rgba(0,0,0,0.06)', borderRadius: 2, p: 2, bgcolor: '#f8fafc' }}>
                    <Typography variant="body2" color="#64748b" sx={{ fontSize: '0.8125rem', mb: 1, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                      Doporučení
                    </Typography>
                    <Box>
                      {(caseData.recommendations?.length ?? 0) > 0 ? (
                        <Box component="ul" sx={{ p: 0, m: 0, listStyle: 'none' }}>
                          {caseData.recommendations.map((r: any, i: number) => (
                            <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 2, pb: 2, borderBottom: '1px solid rgba(0,0,0,0.04)' }}>
                              <CheckCircle size={20} color="#22c55e" style={{ flexShrink: 0, marginTop: 4 }} />
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                {typeof r === 'string' ? r : JSON.stringify(r)}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="#94a3b8" sx={{ fontSize: '0.875rem' }}>
                          Žádná doporučení.
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ border: '1px solid rgba(0,0,0,0.06)', borderRadius: 2, p: 2, bgcolor: '#f8fafc' }}>
                    <Typography variant="body2" color="#64748b" sx={{ fontSize: '0.8125rem', mb: 1, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                      Claimy (nároky)
                    </Typography>
                    <Box>
                      {(caseData.claims?.length ?? 0) > 0 ? (
                        <Box component="ul" sx={{ p: 0, m: 0, listStyle: 'none' }}>
                          {caseData.claims.map((c: any, i: number) => (
                            <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 2, pb: 2, borderBottom: '1px solid rgba(0,0,0,0.04)' }}>
                              <LayoutDashboard size={20} color="#6366f1" style={{ flexShrink: 0, marginTop: 4 }} />
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                {typeof c === 'string' ? c : JSON.stringify(c)}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="#94a3b8" sx={{ fontSize: '0.875rem' }}>
                          Žádné claimy.
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'background.paper', height: '100%' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, letterSpacing: '-0.5px' }}>
                Detaily případu
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(0,0,0,0.06)', pb: 1 }}>
                  <Typography variant="body2" color="#64748b" sx={{ fontSize: '0.875rem' }}>Stav</Typography>
                  <Typography variant="body2" sx={{ fontSize: '0.875rem', fontWeight: 600 }}>{caseData.status}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(0,0,0,0.06)', pb: 1 }}>
                  <Typography variant="body2" color="#64748b" sx={{ fontSize: '0.875rem' }}>Dokončené kroky</Typography>
                  <Typography variant="body2" sx={{ fontSize: '0.875rem', fontFamily: 'monospace' }}>
                    {(caseData.completed_steps ?? []).join(', ') || '—'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(0,0,0,0.06)', pb: 1 }}>
                  <Typography variant="body2" color="#64748b" sx={{ fontSize: '0.875rem' }}>Vytvořeno</Typography>
                  <Typography variant="body2" sx={{ fontSize: '0.875rem', color: '#64748b' }}>
                    {new Date(caseData.created_at).toLocaleString('cs-CZ')}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="#64748b" sx={{ fontSize: '0.875rem' }}>Aktualizováno</Typography>
                  <Typography variant="body2" sx={{ fontSize: '0.875rem', color: '#64748b' }}>
                    {new Date(caseData.updated_at).toLocaleString('cs-CZ')}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'background.paper', mt: 4, overflow: 'hidden' }}>
        <CardHeader
          title="Auditní ledger"
          subheader={ledger.length + ' záznamů'}
          sx={{ pb: 1, borderBottom: '1px solid rgba(0,0,0,0.04)' }}
          titleTypographyProps={{ fontWeight: 600, fontSize: '1.0625rem' }}
          subheaderTypographyProps={{ fontSize: '0.875rem', color: '#64748b' }}
        />
        <TableContainer component={Paper} sx={{ marginTop: 0, borderRadius: 0 }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ '& th': { borderBottom: '1px solid rgba(0,0,0,0.06)', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b' } }}>
                <TableCell sx={{ padding: '12px 20px', fontWeight: 600 }}>Krok</TableCell>
                <TableCell sx={{ padding: '12px 20px', fontWeight: 600 }}>Stav</TableCell>
                <TableCell sx={{ padding: '12px 20px', fontWeight: 600 }}>Čas</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {ledger.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} sx={{ padding: '24px', textAlign: 'center', color: '#94a3b8' }}>
                    Žádné záznamy v ledgeru.
                  </TableCell>
                </TableRow>
              ) : (
                ledger.map((entry: any, i: number) => (
                  <TableRow key={i} sx={{ '&:last-child td': { border: 0 } }}>
                    <TableCell component="th" scope="row" sx={{ padding: '12px 20px', fontFamily: 'monospace', fontSize: '0.8125rem' }}>
                      {entry.step || '—'}
                    </TableCell>
                    <TableCell sx={{ padding: '12px 20px', fontSize: '0.8125rem', fontWeight: 500 }}>
                      <Chip
                        label={entry.status || '—'}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem', borderColor: 'rgba(0,0,0,0.12)', color: '#64748b' }}
                      />
                    </TableCell>
                    <TableCell sx={{ padding: '12px 20px', fontSize: '0.8125rem', color: '#64748b' }}>
                      {entry.timestamp || '—'}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <Dialog open={editOpen} onClose={() => !saving && setEditOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Upravit případ</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '12px !important' }}>
          <TextField
            fullWidth
            label="Název případu"
            value={editTitle}
            onChange={(event) => setEditTitle(event.target.value)}
            required
            inputProps={{ maxLength: 500 }}
          />
          {editableFields.map(([key, label]) => (
            <TextField
              key={key}
              fullWidth
              multiline
              minRows={key === 'problem_statement' ? 3 : 2}
              label={label}
              value={editContext[key] ?? ''}
              onChange={(event) => setEditContext((current) => ({ ...current, [key]: event.target.value }))}
            />
          ))}
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setEditOpen(false)} disabled={saving}>Zrušit</Button>
          <Button onClick={handleSave} disabled={saving || !editTitle.trim()} variant="contained">
            {saving ? 'Ukládám…' : 'Uložit změny'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteOpen} onClose={() => !saving && setDeleteOpen(false)}>
        <DialogTitle>Odstranit případ?</DialogTitle>
        <DialogContent>
          <Typography>
            Opravdu chcete odstranit „{caseData.title}“? Záznam případu zmizí ze seznamu, auditní historie zůstane zachována.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDeleteOpen(false)} disabled={saving}>Zrušit</Button>
          <Button onClick={handleDelete} disabled={saving} color="error" variant="contained">
            {saving ? 'Odstraňuji…' : 'Odstranit'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}