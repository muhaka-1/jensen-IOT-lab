# Jensen IoT Platform – studentguide

Detta starter-repository hör till uppgiftsunderlaget **Labb för DDM**. Uppgiftsunderlaget beskriver syfte, milstolpar, bedömning, deadline och inlämning. Repositoryt innehåller de praktiska instruktionerna, startkoden och övningarna.

## Hitta rätt

- [docs/lab-guide.md](docs/lab-guide.md) – steg-för-steg-instruktioner för alla fyra milstolpar
- [docs/architecture.md](docs/architecture.md) – instruktion och mall för arkitekturdiagrammet
- [docs/reflection.md](docs/reflection.md) – obligatoriska reflektionsfrågor
- `api/` – Flask-API, databas- och cachekod samt tester
- `simulator/` – tre simulerade IoT-sensorer
- `database/init.sql` – databastabeller och startdata
- `k8s/` – färdiga manifest för den introducerande Kubernetes-övningen

## Verktyg som behövs

Installera innan du börjar:

1. Git och ett GitHub-konto.
2. Docker Desktop (Windows/macOS) eller Docker Engine med Docker Compose-plugin (Linux).
3. En valfri kodeditor, exempelvis Visual Studio Code.
4. Inför milstolpe 3: `kubectl` och Minikube.

Python behöver inte installeras lokalt för grunduppgifterna; Python och beroenden finns i containrarna. Kontrollera installationerna i PowerShell, Terminal eller ett Linux-skal:

```text
git --version
docker --version
docker compose version
kubectl version --client
minikube version
```

> Windows: använd PowerShell och kör Docker Desktop innan Docker-kommandona. Kommandona i guiden är desamma på Windows, macOS och Linux. Där ett kommando skiljer sig anges det uttryckligen.

## Start här – första 10 minuterna

### 1. Skapa och klona din fork

Skapa en fork av kursens starter-repository på GitHub. Kopiera URL:en till **din fork** och kör:

```text
git clone <URL-TILL-DIN-FORK>
cd <REPOSITORY-MAPP>
```

Kontrollera att du står i repositoryts rot, alltså mappen som innehåller `docker-compose.yml`. Alla Docker Compose-kommandon i guiden ska köras därifrån.

### 2. Kontrollera Docker

Starta Docker Desktop på Windows/macOS eller Docker Engine på Linux. Kontrollera sedan installationen:

```text
docker info
docker compose version
```

Båda kommandona ska fungera utan fel. Ingen `.env`-fil eller lokal Python-installation behövs; projektet har fungerande standardvärden och kör Python i containern.

### 3. Bygg och starta miljön

```text
docker compose up --build -d
docker compose ps
```

`docker compose ps` ska visa tjänsterna `api`, `simulator`, `db` och `redis`. Databasen ska efter en kort stund visa `healthy`. Om någon tjänst fortfarande startar, vänta några sekunder och kör statuskommandot igen.

### 4. Kontrollera API:t

Öppna följande adresser:

- <http://localhost:5001> – enkel startsida
- <http://localhost:5001/health> – ska visa `"status": "ok"`
- <http://localhost:5001/devices> – ska visa tre sensorer
- <http://localhost:5001/measurements> – ska visa en tom lista `[]`

Den tomma listan är förväntad. Simulatorns giltiga data tas emot men sparas inte förrän du har implementerat lagringen i milstolpe 1.

### 5. Följ simulatorn

```text
docker compose logs -f simulator
```

Från början returnerar API:t status `202` för giltiga mätningar. `sensor-003` skickar ibland avsiktligt felaktig data och ska då få `400`. Det är förväntat. Avsluta den löpande loggvisningen med `Ctrl+C`; tjänsterna fortsätter att köras i bakgrunden.

### 6. Ändra och testa koden

Du kommer främst att arbeta i:

- `api/app.py` – endpoints och HTTP-statuskoder
- `api/db.py` – PostgreSQL-frågor
- `api/cache.py` – Redis-cache
- `api/validation.py` – valideringsregler
- `api/tests/` – automatiserade tester

Källkoden kopieras in i Docker-imagen. Bygg därför om efter kodändringar och kör testerna:

```text
docker compose up --build -d
docker compose exec api python -m pytest -q
```

Visa API-loggen om något går fel:

```text
docker compose logs --tail=100 api
```

### 7. Stoppa miljön

```text
docker compose down
```

Databasen sparas i en Docker-volym och finns kvar till nästa start. Använd endast följande kommando om du avsiktligt vill radera all lokal databasdata för labben:

```text
docker compose down -v
```

Fortsätt nu till [docs/lab-guide.md](docs/lab-guide.md) och genomför milstolparna i ordning.

## Om starten misslyckas

- Kontrollera att Docker Desktop/Docker Engine körs med `docker info`.
- Kör kommandot från repositoryts rot.
- Om port `5001` används av ett annat program: stoppa programmet eller starta med en annan port. PowerShell: `$env:API_PORT=5002; docker compose up --build`. macOS/Linux: `API_PORT=5002 docker compose up --build`.
- Visa status med `docker compose ps` och loggar med `docker compose logs api db redis simulator`.
- Om en kodändring inte syns, kontrollera att du har kört `docker compose up --build -d` efter ändringen.

## SQL Queries

The project includes the three mandatory SQL queries required by the assignment:

1. Total number of measurements using `COUNT`
2. Average temperature using `AVG`
3. Measurements from the last 24 hours

The queries are available in:

[`docs/sql-queries.sql`](docs/sql-queries.sql)