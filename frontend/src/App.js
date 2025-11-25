  import React, { useState, useEffect } from 'react';
  import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
  import { ThemeProvider, createTheme } from '@mui/material/styles';
  import CssBaseline from '@mui/material/CssBaseline';
  import Container from '@mui/material/Container';
  import AppBar from '@mui/material/AppBar';
  import Toolbar from '@mui/material/Toolbar';
  import Typography from '@mui/material/Typography';
  import Tabs from '@mui/material/Tabs';
  import Tab from '@mui/material/Tab';
  import Box from '@mui/material/Box';
  import Button from '@mui/material/Button';
  import TextField from '@mui/material/TextField';
  import Card from '@mui/material/Card';
  import CardContent from '@mui/material/CardContent';
  import LinearProgress from '@mui/material/LinearProgress';
  import Table from '@mui/material/Table';
  import TableBody from '@mui/material/TableBody';
  import TableCell from '@mui/material/TableCell';
  import TableContainer from '@mui/material/TableContainer';
  import TableHead from '@mui/material/TableHead';
  import TableRow from '@mui/material/TableRow';
  import Alert from '@mui/material/Alert';
  import axios from 'axios';
  import LoginIcon from '@mui/icons-material/Login';
  import DashboardIcon from '@mui/icons-material/Dashboard';

  // API base URL – Update to your backend (local or deployed)
  const API_BASE = 'http://localhost:8000';

  const api = axios.create({ baseURL: API_BASE });
  api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  const theme = createTheme({
    palette: { mode: 'light' },
    breakpoints: { values: { xs: 0, sm: 600, md: 900 } },
  });

  const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
      e.preventDefault();
      try {
        const response = await api.post('/auth/login', { username, password });
        localStorage.setItem('token', response.data.access_token);
        setError('');
        navigate('/dashboard');
      } catch (err) {
        setError(err.response?.data?.detail || 'Login failed');
      }
    };

    return (
      <Container maxWidth="sm">
        <Card sx={{ mt: 8, p: 4 }}>
          <CardContent>
            <Typography variant="h4" align="center" gutterBottom>
              PV Site Manager Login
            </Typography>
            <form onSubmit={handleLogin}>
              <TextField
                fullWidth
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
                required
                autoComplete="current-password"
              />
              {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
              <Button
                type="submit"
                fullWidth
                variant="contained"
                startIcon={<LoginIcon />}
                sx={{ mt: 3 }}
              >
                Login
              </Button>
            </form>
          </CardContent>
        </Card>
      </Container>
    );
  };

  const Dashboard = () => {
    const [tabValue, setTabValue] = useState(0);
    const [logs, setLogs] = useState([]);
    const [materials, setMaterials] = useState([]);
    const [progress, setProgress] = useState({ kpis: [], dashboard_summary: {} });
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
      const fetchData = async () => {
        try {
          setLoading(true);
          const [logsRes, materialsRes, progressRes, documentsRes] = await Promise.all([
            api.get('/logs/'),
            api.get('/materials/'),
            api.get('/progress/'),
            api.get('/documents/')
          ]);
          setLogs(logsRes.data);
          setMaterials(materialsRes.data);
          setProgress(progressRes.data);
          setDocuments(documentsRes.data);
        } catch (err) {
          setError('Failed to fetch data');
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }, []);

    const handleTabChange = (event, newValue) => {
      setTabValue(newValue);
    };

    const Logout = () => {
      localStorage.removeItem('token');
      window.location.href = '/login';
    };

    if (loading) return <LinearProgress sx={{ position: 'fixed', top: 0, width: '100%' }} />;

    return (
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <DashboardIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              PV Site Manager Dashboard Live  # Force change here
            </Typography>
            <Button color="inherit" onClick={Logout}>Logout</Button>
          </Toolbar>
        </AppBar>
        <Container maxWidth="md" sx={{ mt: 2 }}>
          {error && <Alert severity="error">{error}</Alert>}
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} centered>
              <Tab label="Daily Logs" />
              <Tab label="Materials" />
              <Tab label="Progress" />
              <Tab label="Documents" />
            </Tabs>
          </Box>
          <TabPanel value={tabValue} index={0}>
            <Typography variant="h5" gutterBottom>Daily Logs</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Workers</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>{log.id}</TableCell>
                      <TableCell>{log.date}</TableCell>
                      <TableCell>{log.workers_count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <Typography variant="h5" gutterBottom>Materials</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>DDT Number</TableCell>
                    <TableCell>Batch</TableCell>
                    <TableCell>Non-Conformity</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {materials.map((m) => (
                    <TableRow key={m.id}>
                      <TableCell>{m.id}</TableCell>
                      <TableCell>{m.ddt_number}</TableCell>
                      <TableCell>{m.batch_number}</TableCell>
                      <TableCell>{m.non_conformity ? 'Yes' : 'No'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            <Typography variant="h5" gutterBottom>Progress Dashboard</Typography>
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6">Overall Progress: {progress.dashboard_summary.overall_progress_percent}%</Typography>
                <LinearProgress variant="determinate" value={progress.dashboard_summary.overall_progress_percent} />
              </CardContent>
            </Card>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>KPI</TableCell>
                    <TableCell>Progress %</TableCell>
                    <TableCell>Target Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {progress.kpis.map((kpi) => (
                    <TableRow key={kpi.id}>
                      <TableCell>{kpi.kpi_name}</TableCell>
                      <TableCell>{kpi.progress_percent}%</TableCell>
                      <TableCell>{kpi.target_date || 'N/A'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
          <TabPanel value={tabValue} index={3}>
            <Typography variant="h5" gutterBottom>Documents</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>File Type</TableCell>
                    <TableCell>Notes</TableCell>
                    <TableCell>Linked Log ID</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {documents.map((d) => (
                    <TableRow key={d.id}>
                      <TableCell>{d.id}</TableCell>
                      <TableCell>{d.file_type}</TableCell>
                      <TableCell>{d.notes || 'N/A'}</TableCell>
                      <TableCell>{d.log_id || 'N/A'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        </Container>
      </Box>
    );
  };

  const TabPanel = (props) => {
    const { children, value, index, ...other } = props;
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`simple-tabpanel-${index}`}
        aria-labelledby={`simple-tab-${index}`}
        {...other}
      >
        {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
      </div>
    );
  };

  const AppContent = () => {
    const token = localStorage.getItem('token');
    return (
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={token ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/" element={<Navigate to={token ? "/dashboard" : "/login"} />} />
        </Routes>
      </Router>
    );
  };

  function App() {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppContent />
      </ThemeProvider>
    );
  }

  export default App;