#Target Group
People familiar with Python, HTML and Javascript who want their own lightweight, customized smart home system. The system here is highly adjusted to meet my needs, but they follow some easy paradigms so feel free to use them for your own home. If you create interesting modules I would be happy if you contribute them back to the project :).

#Motivation

Many home assistant and SmartHome systems exists. Two popular open-source examples are [openHab](https://github.com/openhab/openhab) and [home-assistant](https://github.com/balloob/home-assistant). These tools try to offer support for as many platforms as possible.
This makes these systems in my opinion hard to configure (because the documentation has often weaknesses), hard to extend (because there are so many other components, ...) and horrible slowly starting (at least on my Raspberry Pi). In addition, they try to generalize everything in order to allow the generation of automatic user interfaces and machine to machine communication. Unfortunately this reduces the customizeability.

To encounter this problem, I started my own home assistant system: meinHeim. It follows some really basic paradigms to allow as much customizeability and extentability as possible.

1. Avoid to much generalization. There are billions of different devices, use cases, etc. It is a lot of faster if one simply implements the things that he/she needs for his own project and does not need to fit them into any predefined models/classes.
2. Skip "comfort features" such as simplified programming languages and configurations files to include devices, rules, ... . Learning to use these features usually cost more time than programming the support for the devices in Python in the first place and decreases the customizeability.
 
By following these paradigms, I created a very simple project structure. There are only 4 files that are used:

* meinHeim.py
* modules.py
* website/index.html
* website/js/frontent.js

In the later chapters I will go into more detail what these files are for and how one needs to adjust these files to get is own project running. Keep in mind: All these files are written for myself, change the logic to work for you.

#Installation/Run:

* Fork/Download the project from GitHub
* Install the package by running the install.sh script. This script installs all python dependencies and removes unimportant folders from the directory afterwards.
* If the TinkerforgeConnection module is used -> install the Brick Deamon from [Tinkerforge](tinkerforge.com)
* Change directory into meinHeim/meinHeim
* Run python meinHeim.py
* You find the webpage (in the default configuration) at localhost:8081

#The Different Files

##meinHeim.py

* Bereitstellung einer URL für JEDE Funktion eines Objektes
* Zusätzliche Informationen (wie die angeschlossenen Geräte) werden hier schon vorformatiert
* Regeln in einer eigenen Klasse definiert (todo)

	Fehler bei Regeln: TypeError: Can't instantiate abstract class Test_Rule with abstract methods rule

##modules.py

##website/index.html

If the project gets more complex, more html pages are needed, 

* ein Panel für jedes Objekt, JEDE Aktion wird über einen eigenen Button in diesem Panel aktiviert, identifiziert durch ein val Attribut

##website/js/frontent.js

* ich benutze kein stetiges nachladen
* ein Listener für alle Aktionen/Buttons, leitet die Anfragen an meinHeim.py weiter. Anfragen sind mittels des val Wertes zusammengesetzt.
* möglichst wenig Logik wird hier erledigt, beispielsweise werden angefragte Informationen nur an der Stelle im HTML eingesetzt, keine extra Formatierung
* 
