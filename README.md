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

Campos relevantes para deploy em VPS:
- `API_BASE_PATH` e `UI_BASE_PATH`: mantenha vazio quando o Traefik utilizar `StripPrefix` para `/api` e `/ui`.
- `TRAEFIK_ENTRYPOINT`, `TRAEFIK_DOMAIN` e `TRAEFIK_ACME_EMAIL`: alimentam as labels dinâmicas do Traefik no `docker-compose`.
- `LOG_LEVEL`, `LOG_FORMAT`, `ENABLE_METRICS` e `METRICS_PATH`: controlam observabilidade e formato de logs.

## ▶️ Executar

### Desenvolvimento

#### API Apenas
```bash
# Script automatizado (recomendado)
./run.sh

# Ou manualmente com uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### API + Interface Web
```bash
# Script automatizado com interface Streamlit
./run-ui.sh
```

### Produção
Utilize a imagem Docker multi-stage para rodar em produção. O entrypoint envia logs de progresso antes do Uvicorn iniciar, e o healthcheck built-in valida `/api/v1/health/`.

```bash
# Build manual da imagem
docker build -t astrologer-api:latest .

# Subir usando docker compose (inclui Traefik e Redis opcionais)
docker compose up -d

# Verificar status de saúde do container
docker inspect --format='{{json .State.Health}}' api-psicologa-api
```

A API responderá via Traefik no host configurado (ex.: `https://api.exemplo.com/api/v1/health/`).
Se `ENABLE_METRICS=true`, exponha `https://api.exemplo.com/metrics`.

## 🌟 Interface Web

Além da API REST, o projeto inclui uma interface web Streamlit para facilitar o uso:

- **Interface Streamlit**: http://localhost:8501
- **Funcionalidades**:
  - 📊 Formulário para calcular mapa natal
  - 🔄 Visualização de trânsitos atuais
  - 📱 Interface responsiva e intuitiva

Para executar a interface completa:
```bash
./run-ui.sh
```

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

- Imagem multi-stage localizada em `Dockerfile`, com usuário não-root, healthcheck e entrypoint com feedback.
- Arquivo `docker-compose.yml` orquestra Traefik, API e Redis (opcional) para execução em VPS.
- Acompanhe logs de inicialização com `docker compose logs -f api` e confirme o healthcheck com `docker inspect`.
- Personalize domínio/entrypoint via `.env` (`TRAEFIK_DOMAIN`, `TRAEFIK_ENTRYPOINT`, `TRAEFIK_ACME_EMAIL`).

## 🚢 Deploy em VPS (Traefik + Portainer)

1. Ajuste o `.env` com domínio público, entrypoint do Traefik e e-mail para ACME.
2. Build e push da imagem: `docker build -t registry.example.com/astrologer-api:latest .` seguido de `docker push`.
3. Atualize `docker-compose.yml` ou `deploy/portainer-stack.yml` com o repositório da imagem.
4. Para Portainer, importe `deploy/portainer-stack.yml` como stack, informe as variáveis (`TRAEFIK_DOMAIN`, `TRAEFIK_ENTRYPOINT`) e faça o deploy.
5. Em caso de rollback, publique a tag anterior e use `docker compose pull` + `docker compose up -d` ou `portainer stack rollback`.

Observabilidade:
- Logs estruturados JSON podem ser habilitados com `LOG_FORMAT=json` (útil para Portainer/ELK).
- Habilite métricas Prometheus com `ENABLE_METRICS=true` para expor `/<metrics_path>` e conectar ao Traefik Prometheus plugin.

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

## 🗺️ Roadmap

### Constatações Principais
- `app/main.py:19` mantém handlers e middlewares organizados, porém faltam endpoints de readiness/liveness e parametrização por ambiente.
- `Dockerfile` é single stage, sem `HEALTHCHECK`, sem labels para Traefik/Portainer e carece de feedback explícito durante o boot.
- `tests/test_main.py:1` utiliza `app.test_client()` (padrão Flask) e não cobre fluxos principais da API.
- `streamlit_app.py` expõe interface isolada na porta 8501 e não em `/ui`, tornando a experiência inconsistente.
- `README.md` atual não orienta deploy com Traefik/Portainer, variáveis de ambiente ou observabilidade.

### Infraestrutura e Deploy (VPS, Portainer, Traefik)
- Refatorar `Dockerfile` para multi-stage, adicionar dependências do Swiss Ephemeris, usuário não-root, `uvicorn --proxy-headers --root-path=/api`, script de entrypoint com feedback de inicialização e `HEALTHCHECK`.
- Criar `docker-compose.yml` voltado à VPS com serviços `api`, `traefik` e opcionalmente `redis`, adicionando labels Traefik (`traefik.enable=true`, roteadores HTTP/HTTPS, middleware `strip-prefix` para `/api` e `/ui`).
- Ajustar `.env.example` com variáveis específicas para Traefik/Portainer (`TRAEFIK_ENTRYPOINT`, `API_BASE_PATH`, `UI_BASE_PATH`, hostnames) e documentar no README.
- Adotar logging estruturado configurável via env (`LOG_LEVEL`, `LOG_FORMAT`) e expor `/metrics` com `prometheus_client`.
- Documentar scripts de stack do Portainer (`portainer.yml`) com instruções de deploy e rollback.

### Backend e Observabilidade
- Tratar exceções específicas do Kerykeion em `AstrologyService`, propagando `AstrologyAPIException` com mensagens consistentes e garantindo timezone correto.
- Implementar cache leve (por exemplo, Redis) para mapas/trânsitos e rate limiting via middleware (`fastapi-limiter`).
- Criar endpoints `/api/v1/health/live` e `/api/v1/health/ready` com checagens reais (ephemeris, cache) e expor métricas Prometheus.
- Expandir suíte de testes com `TestClient` ou `httpx.AsyncClient`, cobrindo cenários de sucesso/erro para `/astrology/subject`, `/astrology/natal-chart`, `/astrology/transits`, incluindo validações de schema.
- Configurar pipeline de CI (GitHub Actions ou similar) executando `uv run pytest`, `uv run ruff check` e `uv run mypy`.

### UI/UX em `/ui`
- Substituir Streamlit por UI servida pelo FastAPI (`app.mount("/ui")`) com templates Jinja2 ou build estático (por exemplo, Vite + Tailwind/Alpine).
- Implementar SPA consumindo a API via `fetch`/`axios`, com feedback visual (spinners, toasts) e suporte a PT-BR.
- Criar `ui_service.py` para adaptar respostas da API aos componentes da interface (normalização de planetas, aspectos, etc.).
- Garantir responsividade e acessibilidade (WCAG), oferecendo fluxos: consulta de mapa natal, download de SVG, visualização de trânsitos atuais e histórico, modo demo offline.
- Adicionar testes E2E (Playwright) validando o fluxo principal de `/ui` e smoke test de integração com a API.

### Documentação e DX
- Reestruturar README com seções dedicadas (Arquitetura, Requisitos VPS, Deploy com Portainer/Traefik, Observabilidade, UI em `/ui`, Troubleshooting, Roadmap).
- Criar diretório `docs/` com diagramas (Sequence, Deployment) e tabela de variáveis de ambiente, referenciando `API_DOCUMENTATION.md`.
- Publicar `CONTRIBUTING.md` e `CODE_OF_CONDUCT.md` com convenções de commit, checklist de PR e comandos `uv`.
- Manter `CHANGELOG.md` e adicionar badges de build/test/coverage após configurar CI.
- Atualizar documentação dos scripts `run.sh` e `run-ui.sh`, destacando uso restrito a desenvolvimento.

### Próximos Passos Sugeridos
1. Refatorar contêiner e compose alinhados a Traefik/Portainer, incluindo feedback de boot e healthchecks.
2. Integrar UI estática em `/ui`, removendo dependência do Streamlit e cobrindo com testes E2E.
3. Reforçar camada de serviços e testes automatizados, validando cenários reais da API.
4. Atualizar documentação (README e materiais auxiliares) refletindo a nova arquitetura e fluxos de deploy.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🙏 Agradecimentos

- [Kerykeion](https://github.com/g-battaglia/kerykeion) - Biblioteca para cálculos astrológicos
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Swiss Ephemeris](https://www.astro.com/swisseph/) - Dados astronômicos precisos
