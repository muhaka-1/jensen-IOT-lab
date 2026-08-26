# Reflektionsdokument – Jensen IoT Platform

## 1. Varför ska sensorerna kommunicera med ett API i stället för direkt med PostgreSQL?

Sensorerna kommunicerar med REST API:t eftersom API:t fungerar som ett
kontrollerat lager mellan IoT-enheterna och databasen. API:t kan validera
data, kontrollera att `deviceId` finns och bestämma vilka operationer som
är tillåtna.

Det gör också att sensorerna inte behöver känna till PostgreSQL eller
databasens struktur. Det ger en tydligare separation mellan IoT-enheter,
applikationslogik och datalagring.

---

## 2. Varför ska felaktig sensordata stoppas innan den sparas?

Felaktig data ska stoppas innan den sparas för att databasen annars kan
innehålla ogiltiga mätvärden som senare påverkar historik, statistik och
andra funktioner.

I projektet valideras exempelvis temperatur, luftfuktighet, batterinivå
och `deviceId`. Ogiltiga mätningar returnerar HTTP `400` och sparas inte
i PostgreSQL.

Det gör datan mer tillförlitlig och minskar risken för fel längre fram i
systemet.

---

## 3. Varför passar PostgreSQL för historiska mätvärden?

PostgreSQL passar bra för historiska mätvärden eftersom databasen är
persistent och kan lagra många mätningar strukturerat över tid.

I projektet används PostgreSQL som den beständiga källan för
sensorhistoriken. Mätningar kan hämtas med SQL-frågor och sorteras eller
filtreras efter exempelvis sensor och tid.

PostgreSQL använder dessutom en Docker-volume i den lokala miljön, vilket
gör att data finns kvar efter att containrarna stoppas och startas igen.

---

## 4. Vad händer med lösningen om Redis försvinner?

Redis används som cache och inte som den permanenta lagringen av
sensorhistoriken.

Om Redis försvinner kan cachevärdena inte längre hämtas. Den senaste
mätningen kan däremot hämtas från PostgreSQL eftersom PostgreSQL innehåller
den beständiga datan.

Det betyder att historiken inte försvinner när Redis försvinner.
Nackdelen är att cachefördelen försvinner och läsningar måste gå till
PostgreSQL.

---

## 5. Vad händer med lösningen om PostgreSQL försvinner?

Om PostgreSQL försvinner kan API:t inte längre läsa eller spara den
beständiga mätdata.

Redis kan fortfarande innehålla vissa cachevärden, exempelvis den senaste
mätningen för en sensor, men Redis ersätter inte PostgreSQL som historisk
datakälla.

Om PostgreSQL är otillgängligt påverkas därför framför allt lagring av
nya mätningar och hämtning av historiska mätningar.

---

## 6. Varför används Docker Compose lokalt?

Docker Compose används för att köra hela den lokala IoT-plattformen som
flera samverkande tjänster.

Projektet består bland annat av API, simulator, PostgreSQL och Redis.
Med Docker Compose kan dessa tjänster startas tillsammans och
konfigureras med rätt nätverk, beroenden, portar och volymer.

Det gör utvecklingsmiljön reproducerbar och minskar behovet av att
installera PostgreSQL, Redis och andra beroenden direkt på datorn.

---

## 7. Vad automatiserar din CI-pipeline?

Min GitHub Actions-pipeline körs vid push och pull request.

Pipelinen:

1. checkar ut repositoryt
2. installerar Python 3.12
3. installerar beroenden från `api/requirements.txt`
4. kör pytest-testerna
5. bygger API:ts Docker-image

Det innebär att tester och Docker-build kontrolleras automatiskt varje
gång kod skickas till GitHub.

Det minskar risken att felaktig kod eller en Docker-build som inte
fungerar kommer vidare utan att upptäckas.

---

## 8. Vad observerade du när du tog bort en Kubernetes Pod?

När en av API:ts Pods togs bort upptäckte Kubernetes att Deploymenten
hade färre repliker än det önskade antalet.

Deploymenten skapade därför automatiskt en ny Pod. Efter en kort stund
var antalet API-Pods tillbaka på tre.

Det demonstrerade Kubernetes self-healing och visade praktiskt att
Deploymenten försöker upprätthålla det önskade antalet repliker.

---

## 9. Varför kan flera repliker ge högre tillgänglighet?

Flera repliker innebär att applikationen körs i flera separata Pods.

Om en Pod slutar fungera kan de andra replikerna fortfarande hantera
trafik medan Kubernetes skapar en ersättande Pod.

En Kubernetes Service kan dessutom distribuera inkommande trafik till
de tillgängliga Pod-replikerna.

Det gör lösningen mindre beroende av en enda instans och kan därför öka
tillgängligheten.

---

## 10. När hade Kubernetes varit overkill för en lösning?

Kubernetes hade varit overkill för en mycket liten applikation som bara
körs lokalt eller på en enda server och som inte behöver scaling,
self-healing eller flera repliker.

För en enkel utvecklingsmiljö kan Docker Compose vara betydligt enklare
att konfigurera och underhålla.

Kubernetes blir mer motiverat när systemet växer och behöver exempelvis
flera repliker, automatisk återställning, service discovery, scaling och
mer avancerad containerorkestrering.