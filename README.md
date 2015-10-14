#Installation:

* Brick Deamon
* cherrypy
* tinkerforge python ist schon im Ordner enthalten

#Grundsätze:
Programmierung so einfach/wenig verstrickt wie möglich -> lieber ein paar unnötige Komfortfeatures weg lassen
Kein Zugemülle durch python packages -> alles in diesem Projekt enthalten

Jedes Objekt ist wie folgt implementiert:
	meinHeim.py: 
		* Bereitstellung einer URL für JEDE Funktion eines Objektes
		* Zusätzliche Informationen (wie die angeschlossenen Geräte) werden hier schon vorformatiert
		* Regeln in einer eigenen Klasse definiert (todo)
	static/index.html: 
		* ein Panel für jedes Objekt, JEDE Aktion wird über einen eigenen Button in diesem Panel aktiviert, identifiziert durch ein val Attribut
	static/frontend.js: 
		* ein Listener für alle Aktionen/Buttons, leitet die Anfragen an meinHeim.py weiter. Anfragen sind mittels des val Wertes zusammengesetzt.
		* möglichst wenig Logik wird hier erledigt, beispielsweise werden angefragte Informationen nur an der Stelle im HTML eingesetzt, keine extra Formatierung