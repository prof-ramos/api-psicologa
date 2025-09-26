Análise e Plano de Ação para Deploy da API no Portainer
Prezado colega,
Diante da decisão de priorizar a operacionalização da API astrológica no ambiente Portainer da VPS, com integração ao Traefik existente, procederei a uma análise precisa do estado atual do repositório prof-ramos/api-psicologa. Baseado na documentação disponível, o setup Docker já apresenta uma base sólida — com Dockerfile, docker-compose.yml e suporte a labels Traefik —, mas carece de refinamentos para robustez em produção, conforme destacado nas constatações do roadmap. Essa lacuna compromete aspectos como observabilidade, segurança e automação de healthchecks, essenciais para um deploy gerenciado via Portainer.
A seguir, delineio sistematicamente os elementos pendentes, fundamentados em práticas DevOps consolidadas, seguidos de um plano de ação iterativo. O objetivo é elevar o deploy a um patamar de maturidade que suporte monitoramento proativo e rollbacks ágeis, sem demandar refatorações invasivas.
1. Estado Atual e Lacunas Identificadas
A configuração Docker atual é single-stage, com entrypoint básico e healthcheck implícito, mas exibe as seguintes deficiências principais:
	•	Dockerfile: Ausência de multi-stage build, usuário não-root e HEALTHCHECK explícito, o que eleva riscos de privilégios excessivos e falhas não detectadas.
	•	Docker Compose: Labels Traefik presentes, mas incompletos para middlewares como StripPrefix; falta de serviços dependentes (ex.: Redis opcional) e healthchecks dependentes.
	•	Observabilidade: Logs em formato não estruturado por padrão; métricas Prometheus não expostas de forma nativa.
	•	Portainer-Specific: Arquivo deploy/portainer-stack.yml referenciado, mas sem instruções granulares para importação, injeção de variáveis e auto-update.
	•	Segurança e Feedback: Entrypoint sem logs de progresso; ausência de scans de vulnerabilidades integrados.
Essas omissões, embora funcionais em desenvolvimento, podem induzir instabilidades em produção, como downtime não monitorado ou configurações de rede inconsistentes.
2. Itens Pendentes Priorizados
Com base no roadmap, priorizo os itens críticos para deploy imediato, classificados por impacto (alto/médio) e esforço estimado (em horas-homem):
Item
Descrição
Impacto
Esforço Estimado
Dependência
Refatoração do Dockerfile
Converter para multi-stage com Swiss Ephemeris, usuário não-root, HEALTHCHECK em /api/v1/health/ e entrypoint com logs de inicialização.
Alto (segurança e confiabilidade)
4-6 horas
Nenhuma
Atualização do Docker Compose
Incluir labels completas Traefik (roteadores HTTP/HTTPS, middleware StripPrefix para /api), healthchecks dependentes e serviço Redis opcional.
Alto (integração com Traefik)
2-3 horas
Dockerfile refatorado
Configuração de Variáveis de Ambiente
Expandir .env.example com chaves para Portainer (ex.: TRAEFIK_DOMAIN, TRAEFIK_ACME_EMAIL) e documentar injeção via UI.
Médio (facilitação de deploy)
1 hora
Nenhuma
Integração de Observabilidade
Habilitar logs JSON (LOG_FORMAT=json) e métricas Prometheus (ENABLE_METRICS=true), com exposição em /metrics.
Médio (monitoramento)
2 horas
Atualização do Compose
Guia de Deploy no Portainer
Formalizar deploy/portainer-stack.yml com instruções para importação, rollback e webhook para CI.
Médio (operacionalização)
3 horas
Todos os itens acima
Essa priorização segue o princípio de MVP (Minimum Viable Product) para deploy, focando em estabilidade antes de otimizações avançadas como CI pipelines.
3. Plano de Ação Detalhado
Implemente os itens em sequência, validando localmente com docker compose up -d antes do push para registry. Assuma um registry privado na VPS (ex.: registry.sua-vps.com).
Passo 1: Refatorar o Dockerfile (backend/Dockerfile)
	•	Adote estrutura multi-stage: # Stage 1: Build
	•	FROM python:3.11-slim AS builder
	•	WORKDIR /app
	•	COPY requirements.txt .
	•	RUN pip install --no-cache-dir -r requirements.txt && pip install Swiss Ephemeris
	•	
	•	# Stage 2: Runtime
	•	FROM python:3.11-slim
	•	RUN useradd -m appuser && chown -R appuser /app
	•	WORKDIR /app
	•	COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
	•	COPY . .
	•	RUN chown -R appuser:appuser /app
	•	USER appuser
	•	ENV PATH="/home/appuser/.local/bin:$PATH"
	•	EXPOSE 8000
	•	HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
	•	  CMD curl -f http://localhost:8000/api/v1/health/ || exit 1
	•	ENTRYPOINT ["sh", "-c", "echo 'Iniciando API...' && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --root-path=/api && echo 'API pronta.'"]
	•	
	•	Validação: docker build -t test-api . && docker run --rm test-api.
Passo 2: Atualizar Docker Compose (backend/docker-compose.yml)
	•	Expanda para: version: '3.8'
	•	services:
	•	  api:
	•	    build: .
	•	    image: registry.sua-vps.com/astrologer-api:latest
	•	    labels:
	•	      - "traefik.enable=true"
	•	      - "traefik.http.routers.api.rule=Host(`${TRAEFIK_DOMAIN}`) && PathPrefix(`/api`)"
	•	      - "traefik.http.routers.api.entrypoints=${TRAEFIK_ENTRYPOINT}"
	•	      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
	•	      - "traefik.http.middlewares.api-stripprefix.stripprefix.prefixes=/api"
	•	      - "traefik.http.routers.api.middlewares=api-stripprefix"
	•	    environment:
	•	      - API_BASE_PATH=/api
	•	      - LOG_FORMAT=json
	•	      - ENABLE_METRICS=true
	•	      - METRICS_PATH=/metrics
	•	    healthcheck:
	•	      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
	•	      interval: 30s
	•	      timeout: 10s
	•	      retries: 3
	•	    depends_on:
	•	      - redis  # Opcional
	•	  redis:
	•	    image: redis:alpine
	•	    healthcheck:
	•	      test: ["CMD", "redis-cli", "ping"]
	•	
	•	Validação: docker compose up -d && docker compose logs -f api.
Passo 3: Configurações Adicionais e Deploy
	•	Atualize .env.example com as variáveis listadas na tabela.
	•	Crie/atualize deploy/portainer-stack.yml idêntico ao compose, com placeholders ${VAR} para injeção.
	•	Build e push: docker build -t registry.sua-vps.com/astrologer-api:latest . && docker push ....
	•	No Portainer:
	1	Acesse Stacks > Add Stack > Web Editor.
	2	Cole o conteúdo de portainer-stack.yml.
	3	Em Environment Variables, injete valores (ex.: TRAEFIK_DOMAIN=seudominio.com).
	4	Deploy e ative Auto Update (para tag :latest).
	5	Monitore via docker inspect --format='{{json .State.Health}}' .
	•	Para rollback: Crie tag anterior (ex.: :v1.0) e atualize a stack.
Passo 4: Validação Final
	•	Teste end-to-end: curl https://seudominio.com/api/v1/health/ e métricas em /metrics.
	•	Integre scans: Adicione docker scout cves em script de build.
4. Considerações Finais e Recomendações
Essa intervenção, estimada em 12-15 horas, confere à API uma maturidade compatível com ambientes gerenciados, mitigando riscos inerentes a deploys containerizados. Recomendo documentar as alterações em um CHANGELOG.md e agendar uma revisão pós-deploy para métricas iniciais (ex.: uptime >99% via Portainer).
Caso necessite de esclarecimentos sobre implementações específicas ou adaptações ao seu registry, forneça detalhes adicionais para refinamento.
Atenciosamente, Grok
