# 🌟 API Astrológica - Documentação Completa

## 📋 Visão Geral

API REST para cálculos astrológicos profissionais usando a biblioteca Kerykeion. Automaticamente detecta timezone baseado na cidade informada, proporcionando uma experiência simplificada para o usuário final.

**Base URL**: `http://localhost:8000`
**Versão**: 1.0.0
**Documentação Interativa**: http://localhost:8000/docs

---

## 🚀 Endpoints Disponíveis

### 1. Health Check
- **GET** `/api/v1/health/` - Verifica se a API está funcionando
- **GET** `/api/v1/health/status` - Status detalhado com features

### 2. Cálculos Astrológicos
- **POST** `/api/v1/astrology/subject` - Criar sujeito astrológico
- **POST** `/api/v1/astrology/natal-chart` - Gerar mapa natal (SVG)
- **POST** `/api/v1/astrology/transits` - Calcular trânsitos
- **GET** `/api/v1/astrology/current-transits/{name}` - Trânsitos atuais

---

## 🎯 Para Integração Frontend - Formulário Simplificado

### Formulário Recomendado (UX Otimizada)

```html
<form id="astrology-form">
  <input type="text" name="name" placeholder="Nome completo" required>
  <input type="date" name="birthDate" required>
  <input type="time" name="birthTime" required>
  <input type="text" name="city" placeholder="Cidade de nascimento" required>
  <select name="country">
    <option value="BR">Brasil</option>
    <option value="PT">Portugal</option>
    <option value="US">Estados Unidos</option>
    <!-- Mais países -->
  </select>
  <button type="submit">Gerar Mapa Astral</button>
</form>
```

### JavaScript de Integração

```javascript
class AstrologyAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  // Converte dados do formulário para formato da API
  formatRequestData(formData) {
    const birthDate = new Date(formData.birthDate);

    return {
      name: formData.name,
      year: birthDate.getFullYear(),
      month: birthDate.getMonth() + 1,
      day: birthDate.getDate(),
      hour: parseInt(formData.birthTime.split(':')[0]),
      minute: parseInt(formData.birthTime.split(':')[1]),
      city: formData.city,
      nation: formData.country,
      timezone: null // Deixa a API detectar automaticamente
    };
  }

  // Gera mapa natal
  async generateNatalChart(formData) {
    const requestData = this.formatRequestData(formData);

    const response = await fetch(`${this.baseURL}/api/v1/astrology/natal-chart`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        subject: requestData,
        chart_type: "natal",
        include_aspects: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  // Obter dados astrológicos básicos
  async getAstrologicalData(formData) {
    const requestData = this.formatRequestData(formData);

    const response = await fetch(`${this.baseURL}/api/v1/astrology/subject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  // Calcular trânsitos atuais
  async getCurrentTransits(formData) {
    const requestData = this.formatRequestData(formData);

    const response = await fetch(`${this.baseURL}/api/v1/astrology/transits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        natal_subject: requestData,
        transit_date: new Date().toISOString(),
        orb_limit: 5.0
      })
    });

    return await response.json();
  }
}

// Exemplo de uso
const api = new AstrologyAPI();

document.getElementById('astrology-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);

  try {
    // Opção 1: Dados astrológicos completos
    const astroData = await api.getAstrologicalData(data);
    console.log('Dados astrológicos:', astroData);

    // Opção 2: Gerar mapa natal visual
    const chart = await api.generateNatalChart(data);
    console.log('Mapa natal:', chart);

    // Opção 3: Trânsitos atuais
    const transits = await api.getCurrentTransits(data);
    console.log('Trânsitos:', transits);

  } catch (error) {
    console.error('Erro:', error);
    alert('Erro ao processar solicitação. Verifique os dados informados.');
  }
});
```

---

## 🏗️ Estruturas de Dados (Schemas)

### Request - Dados de Nascimento
```json
{
  "name": "João Silva",
  "year": 1990,
  "month": 5,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "city": "São Paulo",
  "nation": "BR",
  "timezone": null
}
```

### Response - Dados Astrológicos
```json
{
  "status": "OK",
  "data": {
    "name": "João Silva",
    "birth_date": "1990-05-15T14:30:00",
    "city": "São Paulo",
    "nation": "BR",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "timezone": "America/Sao_Paulo",
    "planets": [
      {
        "name": "Sun",
        "longitude": 54.234,
        "sign": "Taurus",
        "house": 1,
        "retrograde": false
      }
    ],
    "houses": [
      {
        "house_number": 1,
        "longitude": 120.5,
        "sign": "Leo"
      }
    ],
    "aspects": [
      {
        "planet1": "Sun",
        "planet2": "Moon",
        "aspect": "Trine",
        "orb": 2.5,
        "applying": true
      }
    ]
  },
  "message": "Dados astrológicos calculados com sucesso"
}
```

---

## 🎨 Frontend - Exemplos de Interface

### 1. Formulário de Entrada
```html
<div class="astro-form-container">
  <h2>🌟 Seu Mapa Astral Personalizado</h2>

  <form id="natal-chart-form">
    <div class="form-group">
      <label for="name">Nome completo</label>
      <input type="text" id="name" name="name" required
             placeholder="Digite seu nome completo">
    </div>

    <div class="form-row">
      <div class="form-group">
        <label for="birthDate">Data de nascimento</label>
        <input type="date" id="birthDate" name="birthDate" required>
      </div>

      <div class="form-group">
        <label for="birthTime">Horário de nascimento</label>
        <input type="time" id="birthTime" name="birthTime" required>
        <small>Se não souber o horário exato, use 12:00</small>
      </div>
    </div>

    <div class="form-group">
      <label for="city">Cidade de nascimento</label>
      <input type="text" id="city" name="city" required
             placeholder="Ex: São Paulo, Rio de Janeiro">
    </div>

    <div class="form-group">
      <label for="country">País</label>
      <select id="country" name="country" required>
        <option value="BR">🇧🇷 Brasil</option>
        <option value="PT">🇵🇹 Portugal</option>
        <option value="US">🇺🇸 Estados Unidos</option>
        <option value="ES">🇪🇸 Espanha</option>
        <option value="FR">🇫🇷 França</option>
      </select>
    </div>

    <button type="submit" class="btn-generate">
      ✨ Gerar Mapa Astral
    </button>
  </form>
</div>
```

### 2. Exibição dos Resultados
```html
<div id="results-container" style="display: none;">
  <div class="astro-results">
    <h3>🎯 Seus Dados Astrológicos</h3>

    <!-- Informações básicas -->
    <div class="basic-info">
      <h4>📍 Informações de Nascimento</h4>
      <p><strong>Local:</strong> <span id="birth-location"></span></p>
      <p><strong>Data/Hora:</strong> <span id="birth-datetime"></span></p>
      <p><strong>Coordenadas:</strong> <span id="coordinates"></span></p>
    </div>

    <!-- Planetas principais -->
    <div class="planets-section">
      <h4>🪐 Planetas Principais</h4>
      <div id="planets-list"></div>
    </div>

    <!-- Mapa SVG -->
    <div class="chart-section">
      <h4>🎨 Seu Mapa Natal</h4>
      <div id="natal-chart-svg"></div>
    </div>

    <!-- Aspectos -->
    <div class="aspects-section">
      <h4>⚡ Aspectos Planetários</h4>
      <div id="aspects-list"></div>
    </div>
  </div>
</div>
```

### 3. JavaScript para Processar Resultados
```javascript
function displayResults(astroData) {
  const data = astroData.data;

  // Informações básicas
  document.getElementById('birth-location').textContent =
    `${data.city}, ${data.nation}`;

  document.getElementById('birth-datetime').textContent =
    new Date(data.birth_date).toLocaleString('pt-BR');

  document.getElementById('coordinates').textContent =
    `${data.latitude.toFixed(4)}°, ${data.longitude.toFixed(4)}°`;

  // Planetas principais (Sol, Lua, Ascendente)
  const mainPlanets = data.planets.filter(p =>
    ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars'].includes(p.name)
  );

  const planetsHTML = mainPlanets.map(planet => `
    <div class="planet-item">
      <span class="planet-name">${getPlanetEmoji(planet.name)} ${planet.name}</span>
      <span class="planet-sign">${planet.sign}</span>
      <span class="planet-house">Casa ${planet.house}</span>
      ${planet.retrograde ? '<span class="retrograde">℞</span>' : ''}
    </div>
  `).join('');

  document.getElementById('planets-list').innerHTML = planetsHTML;

  // Aspectos importantes
  const importantAspects = data.aspects.filter(a =>
    Math.abs(a.orb) <= 3 && ['Conjunction', 'Trine', 'Square', 'Opposition'].includes(a.aspect)
  );

  const aspectsHTML = importantAspects.map(aspect => `
    <div class="aspect-item">
      <span>${aspect.planet1}</span>
      <span class="aspect-type">${getAspectSymbol(aspect.aspect)}</span>
      <span>${aspect.planet2}</span>
      <span class="orb">(${Math.abs(aspect.orb).toFixed(1)}°)</span>
    </div>
  `).join('');

  document.getElementById('aspects-list').innerHTML = aspectsHTML;

  // Mostrar resultados
  document.getElementById('results-container').style.display = 'block';
}

function getPlanetEmoji(planet) {
  const emojis = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿',
    'Venus': '♀', 'Mars': '♂', 'Jupiter': '♃',
    'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇'
  };
  return emojis[planet] || '⭐';
}

function getAspectSymbol(aspect) {
  const symbols = {
    'Conjunction': '☌', 'Trine': '△', 'Square': '□',
    'Opposition': '☍', 'Sextile': '⚹'
  };
  return symbols[aspect] || aspect;
}
```

---

## 🔧 Tratamento de Erros

### Códigos de Status HTTP
- **200**: Sucesso
- **400**: Dados inválidos (cidade não encontrada, data inválida, etc.)
- **422**: Erro de validação (campos obrigatórios)
- **500**: Erro interno do servidor

### Exemplo de Erro
```json
{
  "detail": [
    {
      "loc": ["body", "city"],
      "msg": "Cidade não encontrada: Atlantida",
      "type": "value_error"
    }
  ]
}
```

### Tratamento no Frontend
```javascript
async function handleAPIRequest(requestFunc) {
  try {
    const response = await requestFunc();
    return response;
  } catch (error) {
    if (error.response) {
      // Erro da API
      const errorData = await error.response.json();
      showError(`Erro: ${errorData.detail || 'Dados inválidos'}`);
    } else {
      // Erro de rede
      showError('Erro de conexão. Verifique sua internet.');
    }
    throw error;
  }
}

function showError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.textContent = message;

  // Adicionar à página e remover após 5 segundos
  document.body.appendChild(errorDiv);
  setTimeout(() => errorDiv.remove(), 5000);
}
```

---

## 🌍 Configuração de Timezone (Automática)

A API automaticamente detecta o timezone baseado na cidade informada. Principais regiões suportadas:

### Brasil
- **SP, RJ, MG, PR, SC, RS**: `America/Sao_Paulo`
- **AC, RO**: `America/Rio_Branco`
- **MT, MS**: `America/Cuiaba`
- **AM, RR, AP**: `America/Manaus`

### Outros Países
- **Portugal**: `Europe/Lisbon`
- **EUA**: Detecta por cidade (NY → `America/New_York`)
- **Reino Unido**: `Europe/London`

---

## 🚀 Deploy e Produção

### Variáveis de Ambiente
```bash
ENV_TYPE=production
DEBUG=false
CORS_ORIGINS=https://seusite.com,https://www.seusite.com
```

### Docker (Opcional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📱 Exemplos de Interface Responsiva

### CSS Sugerido
```css
.astro-form-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  color: white;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.btn-generate {
  background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
  border: none;
  padding: 1rem 2rem;
  border-radius: 50px;
  color: white;
  font-weight: bold;
  cursor: pointer;
  width: 100%;
  font-size: 1.1rem;
}

.planet-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  margin: 0.5rem 0;
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
}
```

---

Esta documentação fornece tudo o que você precisa para integrar a API Astrológica ao seu frontend, com timezone automático e UX otimizada! 🌟