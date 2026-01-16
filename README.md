🎮 League of Legends Integration für Home Assistant
Eine benutzerdefinierte Home Assistant Integration, um deine League of Legends Statistiken direkt in dein Dashboard zu holen. Diese Integration wurde von Grund auf neu geschrieben, um die moderne Riot ID (Name#Tag) und die neuen API-Endpunkte zu unterstützen. Sie benötigt keine externen Python-Bibliotheken (wie Cassiopeia), was sie extrem schnell und stabil macht.

✨ Features
✅ Riot ID Support: Unterstützt das neue Format Name#Tag (z.B. TomTorjäger#007).

🏆 Rang-Anzeige: Zeigt aktuellen Solo/Duo Queue Rang (z.B. "GOLD IV") und LP.

📈 Winrate Berechnung: Berechnet automatisch deine Winrate basierend auf Wins/Losses.

🖼️ Profilbild: Lädt dein aktuelles Summoner-Icon als Entity-Bild.

⚡ Leichtgewichtig: Basiert auf aiohttp (nativ in Home Assistant), keine Abhängigkeiten.

🛡️ API-Schonend: Aktualisiert Daten alle 15 Minuten, um Rate-Limits nicht zu verletzen.

📥 Installation
Option 1: HACS (Empfohlen)
Öffne HACS in deinem Home Assistant.

Gehe auf Integrationen > Drei Punkte (oben rechts) > Benutzerdefinierte Repositories.

Füge die URL dieses Repositories hinzu.

Wähle als Kategorie Integration.

Klicke auf "Installieren" und starte Home Assistant neu.

Option 2: Manuell
Lade den Ordner custom_components/league_of_legends aus diesem Repository herunter.

Kopiere den Ordner in dein Home Assistant Verzeichnis: /config/custom_components/league_of_legends.

Starte Home Assistant neu.

⚙️ Konfiguration
Füge folgenden Eintrag in deine configuration.yaml ein:

sensor:
  - platform: league_of_legends
    api_key: "RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    region: "euw1"
    name: "DeinName#Tag"


Variable,Beschreibung,Beispiel
platform,Muss league_of_legends sein.,league_of_legends
api_key,Dein Riot Games API Key.,RGAPI-...
region,Deine Server-Region (kleingeschrieben!).,"euw1, eun1, na1"
name,Deine Riot ID (Name + Tag).

🔑 Wie bekomme ich einen API Key?
Gehe auf das Riot Developer Portal.

Logge dich mit deinem Riot Account ein.

Kopiere den Development API Key.

⚠️ Wichtiger Hinweis: Der Development API Key läuft alle 24 Stunden ab! Wenn der Sensor "Unavailable" anzeigt, musst du den Key im Portal erneuern ("Regenerate") und in deiner Config austauschen. Für eine dauerhafte Nutzung musst du bei Riot ein "Personal Project" registrieren (dauert etwas, aber der Key hält länger).

🐛 Troubleshooting
Sensor ist "Unavailable": Prüfe in den Logs (Einstellungen -> System -> Protokolle). Meistens ist der API Key abgelaufen (Fehler 403).

Falsches Level/Rang: Prüfe, ob du die richtige Region (euw1 vs eun1) angegeben hast.

Format Fehler: Stelle sicher, dass du Name und Tagline mit einem # getrennt hast.

⚖️ Disclaimer
League of Legends Custom isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.
