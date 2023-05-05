import sys
import gi
import sqlite3
import time

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk

import os   # ermöglicht es herauszufinden ob ein file existiert
        
class StartSeite(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(title="Karteibox", *args, **kwargs)
        
        self.set_default_size(400, 400)
    
        self.frame1 = Gtk.Frame()
        self.box1 = Gtk.Fixed()

        bild = Gtk.Image.new_from_file("karteibox.png")
        bild.set_pixel_size(110)
        self.box1.put(bild, 150, 30)

        label1 = Gtk.Label()
        label1.set_use_markup(True)
        label1.set_label('<b><span foreground="blue" size="xx-large">Lernu!</span></b>')
        self.box1.put(label1, 160, 150)
        self.eing1 = Gtk.Entry()
        self.eing1.set_width_chars(20)
        self.eing1.set_placeholder_text("Name der Kartei")
        self.box1.put(self.eing1, 50, 220)

        self.but = Gtk.Button(label="suchen")  # die Kartei suchen
        self.but.connect("clicked", self.db_erkunden)  # Funktion button_clicked wird ausgeführt bei klick
        self.box1.put(self.but, 270, 220)

        self.set_child(self.frame1)
        self.frame1.set_child(self.box1)
        

    def db_erkunden(self, widget): # untersucht ob es eine Kartei mit dem Namen gibt
        
        self.name = self.eing1.get_text()
        db_name = self.name + '.db'
        os.getcwd() #return the current working directory
           
        for root, dirs, files in os.walk(os.getcwd()):
            if db_name in files:  # wenn es eine Datenbank für die Kartei gibt wird sie aufgerufen                         
                self.oeffne_kartei(self.name)
                break
            else:
                mtl = "Kartei "+self.name+" nicht gefunden!" \
                          " Neu erstellen?"
                self.mitteilung(mtl, self.name)
                break
       
    def mitteilung(self, mtl, name): # öffnet ein Fenster für die Mitteilung
        self.dialog = Gtk.MessageDialog(
                    #transient_for=self,
                    buttons = Gtk.ButtonsType.YES_NO ,
                    message_type=Gtk.MessageType.QUESTION,
                    text = mtl)
        self.dialog.show()
        self.dialog.connect("response", self.ergebnis)
        return None
            
    def ergebnis(self, dialog, response):
        if response == Gtk.ResponseType.YES:
            self.name = self.eing1.get_text()
            self.erstel_kartei(self.name)
        elif response == Gtk.ResponseType.NO:
            print("WARN dialog closed by clicking NO button")

        self.dialog.destroy()

    def erstel_kartei(self, name):  # neue kartei wird erstellt
        db_name = self.name + '.db'
            #print(db_name)
        conn = sqlite3.connect(db_name)        
        c = conn.cursor() # eine cursor instanz erstellen
        c.execute('DROP TABLE IF EXISTS karten')  # Tabelle wird gelöscht
            # Tabelle mit Karteikarten
        c.execute("""CREATE TABLE if not exists karten (
                                  vorne TEXT, hinten TEXT)""")
           
        conn.commit()    # Änderungen mitteilen   
        conn.close()   # Verbindung schließen

    def oeffne_kartei(self, *args):
        #print('kartei ' + self.name)
        self.hide()   # schließt das Fenster der Karteikartenbox
        win2 = KarteiSeite(self.name) 
        win2.present()
        
        
class KarteiSeite(Gtk.Window):

    def __init__(self, name):
        super().__init__(title="Kartei")

        self.set_default_size(400, 400)

        self.name = name
        self.box1 = Gtk.Fixed()
        self.set_child(self.box1)

        bild = Gtk.Image.new_from_file("kartei.png")
        bild.set_pixel_size(110)
        self.box1.put(bild, 150, 30)

        label1 = Gtk.Label()
        label1.set_use_markup(True)
        label1.set_label(name)
        self.box1.put(label1, 160, 150)
        self.eing1 = Gtk.Entry()
        self.eing1.set_width_chars(20)
        self.eing1.set_placeholder_text("Name der Karteikarte")
        self.box1.put(self.eing1, 50, 220)

        self.but = Gtk.Button(label="suchen")  # die Karteikarte suchen
        self.but.connect("clicked", self.db_erkunden)  # Funktion button_clicked wird ausgeführt bei klick
        self.box1.put(self.but, 270, 220)

        self.but1 = Gtk.Button(label="andere Kartei")  # die Karteikarte suchen
        self.but1.connect("clicked", self.zeige_start)  # Funktion button_clicked wird ausgeführt bei klick
        self.box1.put(self.but1, 140, 270)

    def db_erkunden(self, *args): # untersucht ob es eine Karteikarte mit dem Namen gibt
        self.kart_name = self.eing1.get_text()
        self.db_name = self.name + '.db'
        #print ('gesuchte Kartei', self.db_name)

        conn = sqlite3.connect(self.db_name)  #Verbindung mit Kartei wird hergestellt
        c = conn.cursor()

        c.execute('SELECT rowid, * FROM karten') # rowid heißt, dass eine eigene originale ID erstellt wird * bedeutet alles  
        records = c.fetchall() # alles aus karten wird in records eingelesen, die ID ist dann in record[0]
        #print('Daten der Kartei')
        #print(records)
        karte_da = 'N'   # Karte gibt es vorläufig nicht
        for record in records: # alle Zeilen werden durchsucht
            if self.kart_name in record: # sucht nach der Karteikarte in records
                print('karte gefunden', self.kart_name)
                self.zeige_karte(self.name, self.kart_name)
                karte_da = 'J'  # Karte gibt es
                break
            else:
                pass
        #print('karte da', karte_da)
        conn.commit()    # Änderungen mitteilen   
        conn.close()   # Verbindung schließen

        if not karte_da =='J':
            mtl = "Karte "+self.kart_name+" nicht gefunden!" \
                      " Neu erstellen?"
            self.mitteilung(mtl)

 
    def mitteilung(self, mtl): # öffnet ein Fenster für die Mitteilung
        self.dialog = Gtk.MessageDialog(                    
                    buttons = Gtk.ButtonsType.YES_NO ,
                    message_type=Gtk.MessageType.QUESTION,
                    text = mtl)
        self.dialog.show()
        self.dialog.connect("response", self.ergebnis)
        return None

    def ergebnis(self, dialog, response):
        if response == Gtk.ResponseType.YES:
            print ('ergebnis aus karteiseite', self.kart_name)
            self.leere_karte(self.kart_name)
        elif response == Gtk.ResponseType.NO:
            print("WARN dialog closed by clicking NO button")

        self.dialog.destroy()

    def zeige_karte(self, *args):
        #print('karte in zeige ' + self.kart_name)
        win4 = KarteVorn(self.name, self.kart_name)
        win2 = KarteiSeite(self.name)

        self.hide()
        win4.present()
            
    def leere_karte(self, *args):
        
        win3 = KartenSeite(self.name, self.kart_name)
        
        self.hide()   # schließt das Fenster der Karteikartenbox
        win3.present()

    def zeige_start(self, *args):
        
        win1 = StartSeite()
        
        self.hide()   # schließt das Fenster der Karteikartenbox
        win1.present()
        
       
class KartenSeite(Gtk.Window):

    def __init__(self,  name, kart_name):
        super().__init__(title="Karteikarte")

        self.set_default_size(400, 400)

        self.name = name
        self.kart_name = kart_name
        self.box1 = Gtk.Fixed()
        self.set_child(self.box1)

        bild = Gtk.Image.new_from_file("karte.png")
        bild.set_pixel_size(110)
        self.box1.put(bild, 150, 30)

        label1 = Gtk.Label()
        label1.set_use_markup(True)
        label1.set_label(kart_name)
        self.box1.put(label1, 160, 150)
        self.eing1 = Gtk.Entry()
        self.eing1.set_width_chars(20)
        self.eing1.set_placeholder_text("Text der Karteikarte")
        self.box1.put(self.eing1, 50, 220)

        self.but = Gtk.Button(label="speichern")  # die Kartei suchen
        self.but.connect("clicked", self.txt_speichern)  # Funktion button_clicked wird ausgeführt bei klick
        self.box1.put(self.but, 270, 220)
    
    def txt_speichern(self, *args):
        #print ('speichern der Karte ',self.kart_name)
        db_name = self.name + '.db'
        kart_text = self.eing1.get_text()
        
        conn = sqlite3.connect(db_name)        
        c = conn.cursor() # eine cursor instanz erstellen
        c.execute("""INSERT INTO karten VALUES (
                    :vorne, :hinten)""",              
                    {'vorne': self.kart_name,
                    'hinten': kart_text})
        
        conn.commit()    # Änderungen mitteilen   
        conn.close()   # Verbindung schließen

        self.hide() # schließt Eingabeseite der Karte
        KarteiSeite.zeige_karte(self, self.name, self.kart_name)

class KarteVorn(Gtk.Window):

    def __init__(self, name, kart_name):
        super().__init__(title="Karteikarte vorn")

        self.set_default_size(400, 400)

        self.name = name
        self.kart_name = kart_name

        print('kartenname', self.kart_name)
        
        self.box1 = Gtk.Fixed()
        self.set_child(self.box1)

        bild = Gtk.Image.new_from_file("karte.png")
        bild.set_pixel_size(110)
        self.box1.put(bild, 150, 20)

        label1 = Gtk.Label()
        label1.set_use_markup(True)
        label1.set_label(self.kart_name)
        self.box1.put(label1, 150, 150)

        self.but = Gtk.Button(label="zeige Rückseite")  # die Kartei suchen
        self.but.connect("clicked", self.zeige_hinten)  # Funktion button_clicked wird ausgeführt bei klick
        self.box1.put(self.but, 150, 220)

    def zeige_hinten(self, widget):
        self.hide()   # schließt das Fenster der Kartei vorne
         
        win5 = KarteHinten(self.name, self.kart_name)
        win5.present()

class KarteHinten(Gtk.Window):

    def __init__(self, name, kart_name):
    
        super().__init__(title="Karteikarte hinten")

        self.name = name
        self.kart_name = kart_name
        
        self.set_default_size(400, 400)
        
        self.box1 = Gtk.Fixed()
        self.set_child(self.box1)
        label1 = Gtk.Label()
        label1.set_use_markup(True)
        label1.set_label(self.kart_name)
        self.box1.put(label1, 150, 150)

        self.db_name = self.name + '.db'
        
        conn = sqlite3.connect(self.db_name)  #Verbindung mit Kartei wird hergestellt
        c = conn.cursor()
        
        c.execute('SELECT rowid, * FROM karten') # rowid heißt, dass eine eigene originale ID erstellt wird * bedeutet alles  
        records = c.fetchall() # alles aus karten wird in records eingelesen, die ID ist dann in record[0]
        for record in records: # alle Zeilen werden durchsucht
            if self.kart_name in record: # sucht nach der Karteikarte in records
                self.text_hinten = record[2]
                print(self.text_hinten)
                break
            else:
                pass            
        
        conn.commit()    # Änderungen mitteilen   
        conn.close()   # Verbindung schließen
        
        label2 = Gtk.Label()
        label2.set_use_markup(True)
        label2.set_label(self.text_hinten)
        self.box1.put(label2, 150, 180)

        self.but = Gtk.Button(label="zur Kartei " + self.name)  # die Kartei suchen
        self.but.connect("clicked", self.zu_kartei)  # Funktion button_clicked wird ausgeführt bei klick
        self.box1.put(self.but, 150, 220)

    def zu_kartei(self, widget):
        self.hide()
        win2 = KarteiSeite(self.name)
        win2.present()


def on_activate(app):
    win1 = StartSeite(application=app)
    win1.present()

app = Gtk.Application()
app.connect('activate', on_activate)

app.run(None)
