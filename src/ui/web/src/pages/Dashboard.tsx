import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Chip,
  TableContainer,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material'
import { api } from '../api'
import { LayoutDashboard, FileText, ArrowRight, Users, BarChart3 } from 'lucide-react'

const StatCard = ({ title, value, Icon, color }: { title: string; value: number | string; Icon: any; color: string }) => (
  <Card
    sx={{
      borderRadius: 3,
      border: '1px solid rgba(0,0,0,0.06)',
      boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      transition: 'all 0.2s',
      '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.08)', transform: 'translateY(-2px)' },
      bgcolor: 'background.paper',
    }}
  >
    <CardHeader
      sx={{ pb: 1, borderBottom: '1px solid rgba(0,0,0,0.04)' }}
      titleTypographyProps={{ fontSize: '0.9375rem', fontWeight: 600, color: '#64748b' }}
      subheaderTypographyProps={{ fontSize: '0.75rem', color: '#94a3b8' }}
      title={title}
      avatar={<Icon size={18} color={color} />}
    />
    <CardContent sx={{ pt: 1 }}>
      <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.5px', mb: 0 }}>
        {value}
      </Typography>
    </CardContent>
  </Card>
)

export default function Dashboard() {
  const [cases, setCases] = useState<{ case_id: string; title: string; tenant_id: string; status: string }[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listCases({ page: 1, page_size: 20 })
      .then((data: any) => { setCases(data.cases ?? []); setTotal(data.total ?? 0) })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <Box sx={{ height: 'calc(100vh - 80px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Načítám řídicí panel…
        </Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ height: 'calc(100vh - 80px)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'error.main' }}>
        <Typography variant="body2">Chyba: {error}</Typography>
      </Box>
    )
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.5px', mb: 0.5 }}>
            Přehled případů
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Správa a spouštění analytických případů
          </Typography>
        </Box>
        <Button
          startIcon={<FileText size={18} />}
          component={Link}
          to="/cases/new"
          variant="contained"
          size="large"
          sx={{ height: 44, borderRadius: 3, fontWeight: 600, boxShadow: '0 4px 12px rgba(79,70,229,0.25)' }}
        >
          Nový případ
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6} lg={3}>
          <StatCard title="Celkem případů" value={total} Icon={LayoutDashboard} color="#6366f1" />
        </Grid>
      </Grid>
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'background.paper', overflow: 'hidden' }}>
            <CardHeader
              title="Případy"
              subheader={total + ' případů v systému'}
              sx={{ pb: 1, borderBottom: '1px solid rgba(0,0,0,0.04)' }}
              titleTypographyProps={{ fontWeight: 600, fontSize: '1.0625rem' }}
              subheaderTypographyProps={{ fontSize: '0.875rem', color: '#64748b' }}
              action={
                <Chip label={total} size="small" variant="outlined" color="primary" />
              }
            />
            <TableContainer component={Paper} sx={{ marginTop: 0, width: '100%', maxWidth: '100%', minWidth: 0, overflowX: 'auto', borderRadius: 0 }}>
              <Table sx={{ minWidth: { xs: 560, sm: 650 }, width: '100%' }} size="small">
                <TableHead>
                  <TableRow sx={{ '& th': { borderBottom: '1px solid rgba(0,0,0,0.06)', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b' } }}>
                    <TableCell sx={{ padding: '12px 20px', fontWeight: 600 }}>ID případu</TableCell>
                    <TableCell sx={{ padding: '12px 20px', fontWeight: 600 }}>Tenant</TableCell>
                    <TableCell sx={{ padding: '12px 20px', fontWeight: 600 }}>Akce</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {cases.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} sx={{ padding: '32px', textAlign: 'center', color: '#94a3b8' }}>
                        Žádné případy k zobrazení
                      </TableCell>
                    </TableRow>
                  ) : (
                    cases.map((item) => (
                      <TableRow
                        key={item.case_id}
                        sx={{
                          '&:last-child td, &:last-child th': { border: 0 },
                          '&:hover': { bgcolor: 'rgba(79,70,229,0.04)', cursor: 'pointer' },
                        }}
                      >
                        <TableCell component="th" scope="row" sx={{ padding: '12px 20px', fontSize: '0.875rem', fontWeight: 500 }}>
                          <Typography component="div" sx={{ fontWeight: 600 }}>{item.title}</Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>{item.case_id}</Typography>
                        </TableCell>
                        <TableCell sx={{ padding: '12px 20px', fontSize: '0.875rem', color: '#64748b' }}>
                          {item.tenant_id}
                        </TableCell>
                        <TableCell sx={{ padding: '12px 20px' }}>
                          <Button
                            component={Link}
                            to={`/cases/${item.case_id}`}
                            startIcon={<ArrowRight size={16} />}
                            size="small"
                            sx={{ textTransform: 'none', color: '#4f46e5', fontWeight: 600, '&:hover': { color: '#4338ca' } }}
                          >
                            Otevřít
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Card>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.06)', bgcolor: 'background.paper', height: '100%' }}>
            <CardContent sx={{ px: 3, py: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, letterSpacing: '-0.5px' }}>
                Rychlá akce
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Button
                  fullWidth
                  startIcon={<Users size={20} />}
                  component={Link}
                  to="/cases/new"
                  variant="outlined"
                  sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.12)', textTransform: 'none', fontWeight: 500 }}
                >
                  Vytvořit nový případ
                </Button>
                <Button
                  fullWidth
                  startIcon={<BarChart3 size={20} />}
                  component={Link}
                  to="/quant"
                  variant="outlined"
                  sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.12)', textTransform: 'none', fontWeight: 500 }}
                >
                  Otevřít Quant Engine
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  )
}