import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Button,
  Card,
  CardContent,
  CardHeader,
  TextField,
  Alert,
  Divider,
  Typography,
  Link as MuiLink,
} from '@mui/material'
import { api } from '../api'
import { FileText, ArrowLeft, Mail } from 'lucide-react'

export default function CaseForm() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '', problem_statement: '', desired_outcome: '', current_state: '', scope: '',
    impact: '', timeframe: '', evidence_notes: '', previous_attempts: '',
    constraints: '', success_criteria: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!form.title.trim() || !form.problem_statement.trim() || !form.desired_outcome.trim()) {
      setError('Vyplňte název, popis problému a požadovaný výsledek.')
      return
    }
    setSubmitting(true)
    try {
      const { title, ...answers } = form
      const context = Object.fromEntries(
        Object.entries(answers).filter(([, value]) => value.trim()).map(([key, value]) => [key, value.trim()]),
      )
      const data = await api.createCase({
        title: title.trim(),
        context,
      })
      navigate(`/cases/${data.case_id}`)
    } catch (err: any) {
      setError(err.message || 'Chyba při vytváření případu')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 1 }}>
        <MuiLink component={Link} to="/" sx={{ color: '#64748b', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 1 }}>
          <ArrowLeft size={16} strokeWidth={1.5} />
          <Box component="span" sx={{ fontSize: '0.875rem', fontWeight: 500 }}>Zpět na dashboard</Box>
        </MuiLink>
      </Box>

      <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'background.paper', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
        <CardHeader
          title="Nový případ"
          subheader="Strukturované zadání pomůže analýze zaměřit se na správný problém. Vyplňte, co víte; neznámé údaje lze doplnit později."
          sx={{ pb: 1, borderBottom: '1px solid rgba(0,0,0,0.04)' }}
          titleTypographyProps={{ fontWeight: 700, fontSize: '1.25rem', letterSpacing: '-0.5px' }}
          subheaderTypographyProps={{ fontSize: '0.9375rem', color: '#64748b' }}
          action={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FileText size={24} color="#6366f1" />
            </Box>
          }
        />
        <CardContent sx={{ px: 4, py: 3 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          )}
          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>

            <TextField
              fullWidth
              name="title"
              label="Název případu"
              value={form.title}
              onChange={handleChange}
              required
              autoFocus
              variant="outlined"
              size="medium"
              sx={{ borderRadius: 2, '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }}
              placeholder="Např. Analýza odchodu zákazníků"
            />
            <Typography variant="h6" sx={{ fontWeight: 700 }}>Základní údaje</Typography>
            <TextField fullWidth name="problem_statement" label="Popis problému" value={form.problem_statement} onChange={handleChange} required multiline minRows={4} inputProps={{ maxLength: 5000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Co konkrétně se děje? Uveďte pozorovaná fakta, ne předpokládanou příčinu nebo řešení." helperText="Stručný, věcný popis stačí. Rozsah, dopad a další souvislosti můžete doplnit níže." />
            <TextField fullWidth name="desired_outcome" label="Co potřebujete zjistit nebo rozhodnout?" value={form.desired_outcome} onChange={handleChange} required multiline minRows={2} inputProps={{ maxLength: 2000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Např. zjistit, ve které části procesu vzniká poškození a které příčiny máme ověřit." helperText="Definujte účel analýzy, ne předem zvolené řešení." />
            <Divider />
            <Typography variant="h6" sx={{ fontWeight: 700 }}>Kontext a rozsah <Typography component="span" variant="body2" color="text.secondary">(volitelné)</Typography></Typography>
            <TextField fullWidth name="current_state" label="Současný stav" value={form.current_state} onChange={handleChange} multiline minRows={2} inputProps={{ maxLength: 4000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Jak situace nebo proces vypadá dnes? Kde se problém projevuje?" />
            <TextField fullWidth name="scope" label="Rozsah a hranice problému" value={form.scope} onChange={handleChange} multiline minRows={2} inputProps={{ maxLength: 4000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Kterých týmů, procesů, produktů či lokalit se týká? Co do analýzy nepatří?" />
            <TextField fullWidth name="impact" label="Dopad problému" value={form.impact} onChange={handleChange} multiline minRows={2} inputProps={{ maxLength: 4000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Dopad na zákazníky, kvalitu, provoz nebo náklady. Čísla a odhady jasně označte." />
            <TextField fullWidth name="timeframe" label="Kdy a jak často se problém objevuje" value={form.timeframe} onChange={handleChange} multiline minRows={2} inputProps={{ maxLength: 2000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Od kdy, jak často, případně po jaké změně se problém objevil?" />
            <Divider />
            <Typography variant="h6" sx={{ fontWeight: 700 }}>Podklady a podmínky <Typography component="span" variant="body2" color="text.secondary">(volitelné)</Typography></Typography>
            <TextField fullWidth name="evidence_notes" label="Dostupná data a podklady" value={form.evidence_notes} onChange={handleChange} multiline minRows={3} inputProps={{ maxLength: 4000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Uveďte data, období, názvy reportů nebo krátké anonymizované shrnutí." helperText="Nahrávání souborů zatím není podporované. Nevkládejte osobní, citlivé ani důvěrné údaje." />
            <TextField fullWidth name="previous_attempts" label="Co už se zkoušelo" value={form.previous_attempts} onChange={handleChange} multiline minRows={2} inputProps={{ maxLength: 3000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Jaká opatření proběhla a s jakým výsledkem?" />
            <TextField fullWidth name="constraints" label="Omezení a důležité podmínky" value={form.constraints} onChange={handleChange} multiline minRows={2} inputProps={{ maxLength: 3000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Provozní, technická, bezpečnostní, kapacitní nebo termínová omezení." />
            <TextField fullWidth name="success_criteria" label="Jak poznáme, že je problém vyřešen" value={form.success_criteria} onChange={handleChange} multiline minRows={2} inputProps={{ maxLength: 2000 }} sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'common.white' } }} placeholder="Pozorovatelný výsledek nebo cílový stav; pokud zatím nevíte, ponechte prázdné." />
            <Button
              type="submit"
              disabled={submitting}
              variant="contained"
              size="large"
              startIcon={<Mail size={20} />}
              sx={{
                height: 48,
                borderRadius: 3,
                fontWeight: 600,
                '&:disabled': { opacity: 0.5, cursor: 'not-allowed' },
                boxShadow: '0 4px 12px rgba(79,70,229,0.25)',
              }}
            >
              {submitting ? 'Vytvářím…' : 'Vytvořit případ'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  )
}