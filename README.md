# API Astrológica - FastAPI + Kerykeion

API moderna para cálculos astrológicos usando FastAPI e a biblioteca Kerykeion, seguindo as melhores práticas de desenvolvimento Python.

## 🌟 Funcionalidades

- ✨ **Mapas Natais**: Geração de cartas astrológicas em formato SVG
- 🪐 **Posições Planetárias**: Cálculo preciso de posições dos planetas
- 🏠 **Casas Astrológicas**: Sistema de casas Placidus (padrão)
- 📐 **Aspectos**: Detecção de aspectos entre planetas
- 🌙 **Trânsitos**: Cálculo de trânsitos planetários
- 📊 **API RESTful**: Endpoints bem documentados com OpenAPI/Swagger
- 🔒 **Validação**: Validação robusta usando Pydantic
- 📝 **Logging**: Sistema de logging estruturado
- 🌐 **CORS**: Configurado para desenvolvimento frontend

## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **Kerykeion**: Biblioteca para cálculos astrológicos
- **Pydantic**: Validação de dados e serialização
- **Uvicorn**: Servidor ASGI de alta performance
- **Swiss Ephemeris**: Cálculos astronômicos precisos

## 📋 Requisitos

- Python 3.11+
- pip ou uv

## 🚀 Setup

### 1. Clonar e configurar ambiente

```bash
# Clonar o repositório
git clone <repo-url>
cd api-psicologa

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Instalar dependências
pip install -e .
# ou usando uv (recomendado)
uv pip install -e .
```

### 2. Configuração de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações se necessário
nano .env
```

## ▶️ Executar

### Desenvolvimento
```bash
# Usando uvicorn diretamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Usando uv (recomendado)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Produção
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

A API estará disponível em `http://localhost:8000`

## 📚 Documentação da API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Endpoints Principais

### Health Check
```bash
GET /api/v1/health/
```

### Criar Sujeito Astrológico
```bash
POST /api/v1/astrology/subject
Content-Type: application/json

{
  "name": "João Silva",
  "year": 1990,
  "month": 5,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "city": "São Paulo",
  "nation": "BR",
  "timezone": "America/Sao_Paulo"
}
```

### Gerar Mapa Natal
```bash
POST /api/v1/astrology/natal-chart
Content-Type: application/json

{
  "subject": {
    "name": "João Silva",
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "city": "São Paulo",
    "nation": "BR"
  },
  "chart_type": "natal",
  "format": "svg",
  "include_aspects": true,
  "house_system": "Placidus"
}
```

### Calcular Trânsitos Atuais
```bash
GET /api/v1/astrology/current-transits/João?year=1990&month=5&day=15&hour=14&minute=30&city=São Paulo&nation=BR
```

## 🏗️ Estrutura do Projeto

```
app/
├── __init__.py              # Inicialização do módulo
├── main.py                  # Aplicação FastAPI principal
├── api/
│   └── v1/
│       └── routers/
│           ├── astrology.py # Endpoints astrológicos
│           └── health.py    # Health check
├── core/
│   ├── config.py           # Configurações
│   ├── exceptions.py       # Exception handlers
│   └── middleware.py       # Middleware personalizado
├── schemas/
│   └── astrology.py        # Modelos Pydantic
└── services/
    └── astrology_service.py # Lógica de negócio
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com coverage
pytest --cov=app

# Testes específicos
pytest tests/test_main.py::test_health_check
```

## 🐳 Docker

```bash
# Build da imagem
docker build -t astrologer-api .

# Executar container
docker run -p 8000:8000 astrologer-api

# Docker Compose (se disponível)
docker-compose up
```

## 🔧 Comandos de Desenvolvimento

```bash
# Formatação de código
ruff format .

# Linting
ruff check .

# Type checking
mypy app/

# Instalar dependências de desenvolvimento
pip install -e ".[dev,test]"
```

## 📖 Exemplos de Uso

### Python
```python
import httpx

# Criar cliente
client = httpx.Client(base_url="http://localhost:8000")

# Dados de nascimento
birth_data = {
    "name": "Maria Santos",
    "year": 1985,
    "month": 12,
    "day": 25,
    "hour": 10,
    "minute": 15,
    "city": "Rio de Janeiro",
    "nation": "BR"
}

# Obter dados astrológicos
response = client.post("/api/v1/astrology/subject", json=birth_data)
astro_data = response.json()

print(f"Status: {astro_data['status']}")
print(f"Planetas: {len(astro_data['data']['planets'])}")
```

### cURL
```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Criar sujeito astrológico
curl -X POST "http://localhost:8000/api/v1/astrology/subject" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "year": 1990,
    "month": 1,
    "day": 1,
    "hour": 12,
    "minute": 0,
    "city": "São Paulo",
    "nation": "BR"
  }'
```

## 🤝 Contribuição

1. Fork do projeto
2. Criar branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -am 'Add nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abrir Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🙏 Agradecimentos

- [Kerykeion](https://github.com/g-battaglia/kerykeion) - Biblioteca para cálculos astrológicos
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Swiss Ephemeris](https://www.astro.com/swisseph/) - Dados astronômicos precisos