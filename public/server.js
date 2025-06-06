const express = require('express');
const path = require('path');
const app = express();

// A MÁGICA ACONTECE AQUI:
// Serve os arquivos estáticos da pasta 'public'
app.use(express.static(path.join(__dirname, 'public')));

// Sua rota de API existente
app.get('/api/data', (req, res) => {
    // Sua lógica para buscar dados, usando a chave de API
    const data = { /* seus dados aqui */ };
    res.json(data);
});

// Qualquer outra rota vai servir o index.html (para single-page applications)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ... resto do seu código