# Ajapaik API Võtmete (API Keys) Arhitektuur ja Rakendusplaan

**Kuupäev:** 30. september 2026  
**Dokumendi staatus:** Aruteluks / Kavand  
**Sihtgrupp:** Vahur Puik, Märt Põder, Kimmo Virtanen  

---

## 1. Kontekst ja Eesmärk

Ajapaiga platvorm pakub ulatuslikku REST API-t, mida on ajalooliselt kasutanud mobiilirakendused (Androidi äpp), partnerid (Delfi, Wikidocumentaries, Finna) ning mitmesugused teadus- ja kultuuripärandi projektid.

### Hetkeolukord ja vajadus muutuseks
- **Päringute kontrollimatus ja kraapimine:** Praegu on enamik Ajapaiga API otspunkte avalikult ja autentimata kättesaadavad. See tekitab riske serveri ülekoormusele (DDoS / agressiivsed andmekorjed / tehisintellekti treeningkraapijad) ning ei võimalda eristada heatahtlikke partnereid pahatahtlikest päringutest.
- **Vananenud kliendid:**
  - **Ajapaik Androidi äpp:** Äpp on amortiseerunud ja kasutusest maas. Selle tagasiühilduvuse hoidmine pole enam prioriteet.
  - **Delfi kaardikiht:** Eemaldatud Delfi poolt, eraldi partner-API tuge pole vaja säilitada endisel kujul.
- **Eesmärk:**
  - Muuta Ajapaiga välised API-d ligipääsetavaks **ainult kehtiva API võtmega**.
  - Luua selge, standardne ja turvaline võtmete väljastamise ja haldamise süsteem (Django adminis).
  - Välispartneritele ja huvilistele anda selge veateade ja juhis: **API kasutamiseks tuleb võtta ühendust `info@ajapaik.ee`**.
  - Tagada, et **Ajapaiga enda veebileht (brauser, PWA jms)** jätkaks veatult tööd tavaliste veebisessioonide ja CSRF-märkide baasil.

---

## 2. API-de Inventuur ja Mõjuala

Ajapaiga koodibaas toetub valdavas osas **Django REST Frameworkile (DRF)**, mis teeb globaalse autentimise jõustamise tehniliselt väga puhtaks.

### A. Põhiline REST API (`/api/v1/...`) — ~30 otspunkti
*Asukoht:* `ajapaik/ajapaik/api.py` ja `ajapaik/ajapaik/urls.py`
- **Fotod:**
  - Otsing ja nimekirjad: `/api/v1/photos/search/`, `/api/v1/photos/search/user-rephotos/`, `/api/v1/photos/similar/`
  - Seisund ja metaandmed: `/api/v1/photo/state/`, `/api/v1/photo/applied-operations/`
  - Rephotod ja üleslaadimine: `/api/v1/photo/upload/`, `/api/v1/photo/upload/settings`
  - Lemmikud ja soovitused: `/api/v1/photo/favorite/set/`, `/api/v1/photo/suggestion/`
- **Albumid:**
  - `/api/v1/albums/`, `/api/v1/albums/search/`, `/api/v1/album/<id>/`, `/api/v1/album/nearest/`, `/api/v1/album/photos/search/`
- **Transkriptsioonid:**
  - `/api/v1/transcriptions/`, `/api/v1/transcriptions/<photo_id>/`, `/api/v1/transcription-feedback/`
- **Partner-/integratsiooniliidesed:**
  - `/api/v1/finna/nearest/`, `/api/v1/photo/fetch-hkm-finna/`
  - `/api/v1/wikidocumentaries/`, `/api/v1/wikidocumentaries/photos/`
- **Kasutajad ja seaded:**
  - `/api/v1/user/me/`, `/api/v1/user-settings/`, `/api/v1/merge-profiles/`, `/api/v1/change-profile-display-name`

### B. Tuvastusmoodulite API-d
*Asukoht:* `ajapaik/ajapaik_face_recognition/` ja `ajapaik/ajapaik_object_recognition/`
- `/face-recognition/api/v1/annotation/<id>/`
- `/face-recognition/api/v1/subject-data/` *(Märkus: kasutatakse ka veebis näotuvastuse sildistaja poolt)*
- `/face-recognition/api/v1/album-has-annotations/<id>/`
- `/object-recognition/api/v1/annotation/<id>/`

### C. Teised otsad ja erandid
- **Delfi ja Bbox:** `/delfi-api/v1/...`, `/bbox/v1/` — suunata kas samuti API võtme alla või sulgeda/deprecate'ida.
- **IIIF protokoll:** `/photo/<id>/info.json/`, `/photo/<id>/manifest.json/` — *soovitus:* jätta avalikuks, kuna IIIF on kultuuripärandi avatud pildistandard ja selle sulgemine rikuks integreeritud pildivaaturid.
- **Veebirakenduse sisesed AJAX-vaated:** `/map-data/`, `/frontpage-async/`, `/autocomplete/...` — need ei kuulu `/api/v1/` alla, vaid töötavad tavalise veebiliikluse ja sessioonidega.

---

## 3. Tehniline Arhitektuur

### 3.1. Andmemudel: `ApiKey`
Luua uus mudel `ApiKey` (rakenduses `ajapaik_auth` või eraldi `ajapaik_api_auth`):

```python
class ApiKey(models.Model):
    name = models.CharField(max_length=255, help_text="Kliendi või projekti nimi (nt 'Tartu Ülikooli uurimisrühm')")
    contact_email = models.EmailField(help_text="Vastutava isiku e-posti aadress")
    prefix = models.CharField(max_length=8, unique=True, db_index=True)
    hashed_key = models.CharField(max_length=128)
    
    is_active = models.BooleanField(default=True)
    rate_limit_per_minute = models.PositiveIntegerField(default=60)
    rate_limit_per_day = models.PositiveIntegerField(default=10000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
```

- **Turvalisus:** API võtit ennast (nt formaadis `ajp_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`) kuvatakse administraatorile **ainult üks kord** selle loomisel. Andmebaasis säilitatakse vaid SHA-256 räsi ja 8-kohalist prefiksit identifitseerimiseks.

### 3.2. Päringu Autoriseerimine
Klient saab saata võtit:
1. **HTTP päises (Soovituslik standard):**
   ```http
   Authorization: Api-Key ajp_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   või
   ```http
   X-API-KEY: ajp_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
2. **URL päringuparameetrina (mugav GET päringutel):**
   ```http
   https://ajapaik.ee/api/v1/photos/search/?query=Tallinn&api_key=ajp_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 3.3. DRF Permission Klass: `HasApiKeyOrWebSession`
Kuna Ajapaiga veebiliides (nt näotuvastuse frontend) teeb kohati päringuid samadesse API otstesse, peab reegel olema hübriidne:
- **LUBATUD**, kui päringuga tuleb kaasa kehtiv ja aktiivne `ApiKey`.
- **LUBATUD**, kui päring tuleb Ajapaiga veebisessioonist (autenditud kasutaja või kehtiv veebisessioon CSRF kaitsega).
- **KEELATUD (401/403)**, kui puuduvad mõlemad.

Konfigureeritakse globaalselt failis `ajapaik/settings/default.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'ajapaik.ajapaik.permissions.HasApiKeyOrWebSession',
    ],
    ...
}
```

---

## 4. Veateade (Error Response) ja Teavitamine

Kui päringul puudub võti või see on kehtetu, tagastab API HTTP staatuse **401 Unauthorized** selge JSON struktuuriga:

```json
{
  "error": "api_key_required",
  "detail": "Ajapaik API requires a valid API key. If you wish to use the Ajapaik API, please contact info@ajapaik.ee to request an access key.",
  "contact": "info@ajapaik.ee",
  "documentation": "https://ajapaik.ee/api/"
}
```

See tagab, et iga väline skript või arendaja saab kohe selge ja ühese suunise kontakteerumiseks.

---

## 5. Administraatori Liides (Django Admin)

Admin-paneelis (`/admin/`):
- Võtmete nimekiri: näha omanik, e-post, staatus (aktiivne/peatatud), viimane kasutusaeg, päringulimiidid.
- Võtme loomise vorm:
  - Sisestatakse kliendi nimi ja kontaktmeil.
  - Salvestamisel genereeritakse krüptograafiliselt turvaline võti ja kuvatakse hüpikaknas kopeerimiseks.
- Võtme kohene deaktiveerimine (revocation ühe nupuvajutusega kuritarvituse korral).

---

## 6. Päringute Piiramine (Rate Limiting)

Lihtsalt võtme nõudmine ei kaitse serverit, kui üks lubatud partner teeb sekundis 500 rasket päringut.
- Integreerida DRF `Throttling` mehhanism võtmepõhiselt.
- Vaikimisi profiil:
  - Tavavõti: 60 päringut minutis, 10 000 päringut ööpäevas.
  - Partner / teadustöö: vajadusel erikokkuleppega suuremad limiidid.
- Limiidi ületamisel vastatakse HTTP **429 Too Many Requests**.

---

## 7. Juurutamise ja Ülemineku Plaan (Rollout Strategy)

Muudatuse sujuvaks elluviimiseks on soovitatav 3-etapiline plaan:

### Etapp 1: Koodibaasi ettevalmistus ja Admin-tugi (1–2 päeva)
1. Luua `ApiKey` mudel ja migratsioonid.
2. Luua Django admin vaated võtmete genereerimiseks ja haldamiseks.
3. Luua `HasApiKeyOrWebSession` autentimis- ja õiguste klass.

### Etapp 2: Testimine ja "Shadow Mode" / Telemeetria (3–7 päeva)
1. Paigaldada `staging` serverisse ja testida kõiki veebilehe funktsioone (et brauseri liides ei tõrguks).
2. Toodangus käivitada esmalt "Shadow Mode" (pehme režiim):
   - Päringuid ei blokeerita veel, kuid iga võtmeta `/api/v1/` päring logitakse (IP, User-Agent, otspunkt).
   - See annab Märtile, Kimmole ja Vahurile täpse ülevaate: kas kuskil tiksub veel mõni oluline teenus, mida me ei teadnud?

### Etapp 3: Täielik jõustamine (Enforcement)
1. Väljastada vajadusel võtmed teadaolevatele elulistele partneritele (kui neid on).
2. Lülitada sisse range režiim: ilma võtmeta päringud saavad `401 Unauthorized` koos teavitusega võtta ühendust `info@ajapaik.ee`.
3. Lisada Ajapaiga kodulehele/jalusesse lühike leht või viide API võtme taotlemise kohta.

---

## 8. Küsimused ja Otsustuspunktid Aruteluks (Märt & Kimmo)

1. **Kas on teadaolevaid aktiivseid välispartnereid?**
   - Kas Wikidocumentaries või mõni Soome muuseum teeb praegu regulaarseid päringuid otse tootmisserveri vastu?
2. **Kuidas suhtuda IIIF-i ja avaandmete otsadesse?**
   - Kas hoiame IIIF manifestid täielikult avalikud (soovitus: jah, sest see on standardne pildiprotokoll)?
3. **Kas iseteenindus on vajalik või piisab esialgu ainult administraatori väljastatud võtmetest?**
   - Soovitus: hoida esialgu lihtne – võtmeid väljastab administraator `info@ajapaik.ee` pöördumise peale. Iseteeninduse (kasutajaprofiili alt võtme genereerimine) saab lisada hiljem, kui selleks tekib reaalne vajadus.
