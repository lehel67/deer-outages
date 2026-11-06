# DEER áramszünetek – Home Assistant

[Magyar](#magyar) | [Română](#română) | [English](#english)

---

## Magyar

A **Distribuție Energie Electrică Romania (DEER)** tervezett áramszünetei és üzemzavarai a Home Assistantban, **a saját címedre szűrve**. Szól, ha holnap nem lesz áram az utcádban, a naptárban mutatja a leállásokat, és a leállás kezdetekor és végén pontosan vált.

Nem kell hozzá se fiók, se jelszó. A DEER nyilvános adatait olvassa, ugyanazt, amit a [DEER áramszünet-oldala](https://www.distributie-energie.ro/intreruperi-deer/) mutat.

**Megyék:** Alba, Bihar, Beszterce-Naszód, Brăila, Brassó, Buzău, Kolozs, Kovászna, Dâmbovița, Galați, Hargita, Máramaros, Maros, Prahova, Szilágy, Szatmár, Szeben, Vrancea.

### Telepítés

**HACS-szal (ajánlott)**

1. HACS → jobb felül a három pont → **Egyéni tárolók** (Custom repositories).
2. Tároló: `https://github.com/lehel67/ha-deer-outages`, típus: **Integráció**.
3. Keresd meg a „DEER” integrációt, **Letöltés**, majd indítsd újra a Home Assistantot.

**Kézzel:** másold a `custom_components/deer_outages` mappát a Home Assistant `config/custom_components/` mappájába, és indítsd újra.

### Beállítás

**Beállítások → Eszközök és szolgáltatások → Integráció hozzáadása → DEER áramszünetek**

- **Megye**, **település**: a települést írhatod románul vagy magyarul is (`Târgu Secuiesc` vagy `Kézdivásárhely`, `Sfântu Gheorghe` vagy `Sepsiszentgyörgy`). Az ékezet és a kis- és nagybetű nem számít.
- **Utcák** (nem kötelező): vesszővel elválasztva, például `Gábor Áron, Ady Endre`. Üresen hagyva az egész település leállásait figyeli.

Több címet is felvehetsz (például a szüleidét). Az utcákat később is módosíthatod a fogaskerék ikonnal.

### Mit kapsz?

| Entitás | Mit mutat |
| --- | --- |
| `binary_sensor.…_aramszunet_most` | Be van kapcsolva, amíg leállás tart a címeden (tervezett vagy üzemzavar). Pontosan a kezdéskor és a befejezéskor vált. |
| `sensor.…_kovetkezo_aramszunet` | A következő (vagy a mostani) leállás kezdete. Tulajdonságai: `end`, `type`, `addresses`, `message` (kész szöveg értesítéshez), `count`, `outages`. |
| `calendar.…_aramszunetek` | Minden leállás eseményként, az érintett címekkel. |

Új leállásnál a Home Assistant egy `deer_outages_new_outage` eseményt küld. Az első lekérdezésnél és újraindítás után nem jelzi újra a már ismert leállásokat.

**Jó tudni:**

- Ha a DEER egy egész falura vagy körzetre (pl. `ZONA PT 7`) jelent leállást, abból nem derül ki, hogy a te utcád benne van-e. Ezeket biztonságból mindig mutatja, és ilyenkor `area_only: true`.
- Az üzemzavaroknak gyakran nincs még befejezési ideje. Ilyenkor 2 órát feltételez, amíg a DEER meg nem adja.
- 30 percenként frissít. Ha a DEER oldala nem érhető el, legfeljebb 3 óráig az utolsó jó adatot mutatja (`stale: true`).

### Értesítés példa

```yaml
alias: Áramszünet értesítő
triggers:
  - trigger: event
    event_type: deer_outages_new_outage
actions:
  - action: notify.mobile_app_telefonom
    data:
      title: ⚡ Áramszünet
      message: "{{ trigger.event.data.message }}"
```

Az esemény adatai: `message`, `type` (`planned` / `incident`), `start`, `end`, `end_known`, `addresses`, `area_only`, `county`, `locality`, `streets`.

---

## Română

Întreruperile programate și incidentele **Distribuție Energie Electrică Romania (DEER)** în Home Assistant, **filtrate pentru adresa ta**: senzor „întrerupere acum”, „următoarea întrerupere”, calendar și un eveniment `deer_outages_new_outage` pentru notificări. Fără cont sau parolă; se folosesc datele publice afișate pe [pagina de întreruperi DEER](https://www.distributie-energie.ro/intreruperi-deer/).

Instalare: HACS → Custom repositories → `https://github.com/lehel67/ha-deer-outages` (Integration), apoi **Setări → Dispozitive și servicii → Adaugă integrare → DEER**. Localitatea se poate scrie în română sau maghiară; străzile (opțional) se separă prin virgulă.

---

## English

Planned power outages and incidents of **Distribuție Energie Electrică Romania (DEER)** in Home Assistant, **filtered for your address**: an "outage now" binary sensor, a "next outage" timestamp sensor, a calendar, and a `deer_outages_new_outage` event for notifications. No account needed; it reads the public data shown on the [DEER outage page](https://www.distributie-energie.ro/intreruperi-deer/).

Install with HACS (Custom repositories → `https://github.com/lehel67/ha-deer-outages`, type Integration) or copy `custom_components/deer_outages` into your config folder, restart, then add **DEER** under Settings → Devices & services. Localities can be typed in Romanian or Hungarian; streets are optional and comma separated.

---

*Ez egy nem hivatalos, közösségi projekt, nincs kapcsolatban a Distribuție Energie Electrică Romania-val. / Proiect neoficial, neafiliat cu Distribuție Energie Electrică Romania. / Unofficial project, not affiliated with Distribuție Energie Electrică Romania.*

*A kód nagy részét Claude (Anthropic) segítségével írtuk. / Developed with the help of Claude (Anthropic).*
