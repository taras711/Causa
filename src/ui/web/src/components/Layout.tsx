import { useEffect, useState } from 'react'
import { Box, Collapse, Toolbar, Typography } from '@mui/material'
import { Drawer, AppBar, IconButton, List, ListItemButton, ListItemIcon, ListItemText } from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import { Link, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'
import { LayoutDashboard, FileText, Search, BarChart3, Plus, ChevronDown } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

const drawerWidth = 260

interface NavItem {
  to: string
  label: string
  icon: ReactNode
  children?: NavItem[]
}

const NAV: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
  {
    to: '/cases',
    label: 'Případy',
    icon: <FileText size={20} />,
    children: [
      { to: '/cases', label: 'Seznam případů', icon: <FileText size={18} /> },
      { to: '/cases/new', label: 'Nový případ', icon: <Plus size={18} /> },
    ],
  },
  { to: '/knowledge', label: 'Znalostní báze', icon: <Search size={20} /> },
  { to: '/quant', label: 'Quant Engine', icon: <BarChart3 size={20} /> },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [casesExpanded, setCasesExpanded] = useState(
    location.pathname.startsWith('/cases'),
  )

  useEffect(() => {
    if (location.pathname.startsWith('/cases')) setCasesExpanded(true)
  }, [location.pathname])

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const drawer = (
    <Box component="nav" aria-label="Hlavní navigace" sx={{ width: drawerWidth, minHeight: '100%', flexShrink: 0, color: '#e2e8f0', bgcolor: '#0f172a' }}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2, py: 1.5 }}>
          <Box sx={{ fontWeight: 700, fontSize: '1.125rem', letterSpacing: '-0.5px', color: 'common.white' }}>
            Causa
          </Box>
        </Box>
      </Toolbar>
      <List sx={{ mt: 2, px: 1.5, borderTop: '1px solid rgba(255,255,255,0.12)' }}>
          {NAV.map((item) => (
            <Box key={item.to}>
              {item.children ? (
                <ListItemButton
                  onClick={() => setCasesExpanded((expanded) => !expanded)}
                  aria-expanded={casesExpanded}
                  sx={{
                    minHeight: 44,
                    mb: 0.5,
                    borderRadius: 1.5,
                    color: '#cbd5e1',
                    '&:hover': { backgroundColor: 'rgba(255,255,255,0.10)', color: '#ffffff' },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: 'inherit' }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.label} />
                  <ChevronDown
                    size={18}
                    style={{
                      transform: casesExpanded ? 'rotate(180deg)' : 'none',
                      transition: 'transform 180ms ease',
                    }}
                  />
                </ListItemButton>
              ) : (
                <ListItemButton
                  component={Link}
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                  selected={location.pathname === item.to}
                  sx={{
                    minHeight: 44,
                    mb: 0.5,
                    borderRadius: 1.5,
                    color: '#cbd5e1',
                    '& .MuiListItemIcon-root': { color: 'inherit' },
                    '& .MuiListItemText-primary': { color: 'inherit', fontSize: '0.9375rem', fontWeight: 500 },
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(99,102,241,0.24)',
                      color: '#ffffff',
                      borderLeftColor: '#818cf8',
                    },
                    borderLeft: '3px solid transparent',
                    '&:hover': { backgroundColor: 'rgba(255,255,255,0.10)', color: '#ffffff' },
                    '&.Mui-selected:hover': { backgroundColor: 'rgba(99,102,241,0.32)' },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: 'inherit' }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              )}
              {item.children && (
                <Collapse in={casesExpanded} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {item.children.map((child) => (
                      <ListItemButton
                        key={child.to}
                        component={Link}
                        to={child.to}
                        onClick={() => setMobileOpen(false)}
                        selected={location.pathname === child.to}
                        sx={{
                          minHeight: 40,
                          mb: 0.5,
                          ml: 2,
                          pl: 2,
                          borderRadius: 1.5,
                          color: '#94a3b8',
                          '& .MuiListItemIcon-root': { color: 'inherit' },
                          '& .MuiListItemText-primary': { color: 'inherit', fontSize: '0.875rem' },
                          '&.Mui-selected': {
                            backgroundColor: 'rgba(99,102,241,0.18)',
                            color: '#ffffff',
                          },
                          '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.10)',
                            color: '#ffffff',
                          },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 30, color: 'inherit' }}>
                          {child.icon}
                        </ListItemIcon>
                        <ListItemText primary={child.label} />
                      </ListItemButton>
                    ))}
                  </List>
                </Collapse>
              )}
            </Box>
          ))}
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        sx={{
          left: { xs: 0, md: `${drawerWidth}px` },
          width: { xs: '100%', md: `calc(100% - ${drawerWidth}px)` },
          bgcolor: '#0f172a',
          color: 'common.white',
          boxShadow: 'none',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          zIndex: 1201,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            component="div"
            variant="h6"
            noWrap
            sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: '-0.5px' }}
          >
            Causa Admin
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        component="nav"
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            bgcolor: '#0f172a',
            color: '#e2e8f0',
          },
        }}
      >
        {drawer}
      </Drawer>

      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            bgcolor: '#0f172a',
            color: '#e2e8f0',
            borderRight: '1px solid rgba(255,255,255,0.08)',
          },
        }}
        open
      >
        {drawer}
      </Drawer>

      <Box
        component="main"
        sx={{
          flex: '1 1 0%',
          width: { xs: '100%', md: `calc(100% - ${drawerWidth}px)` },
          maxWidth: '100%',
          minWidth: 0,
          minHeight: '100vh',
          overflowX: 'hidden',
          px: { xs: 2, sm: 3 },
          pt: { xs: '80px', sm: '88px' },
          pb: 4,
          '& > *': { minWidth: 0, maxWidth: '100%' },
        }}
      >
        {children}
      </Box>
    </Box>
  )
}