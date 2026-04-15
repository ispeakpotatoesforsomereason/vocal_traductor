# In questo file creiamo lo script che permettera' di ascoltare dal nostro microfono quello che diciamo (decidiamo noi per quanti secondi)
# L'audio viene salvato in un file e poi viene convertito in testo

import sounddevice as sd  # serve per far partire la registrazione
import scipy.io.wavfile as wav  # serve per salvare l'audio
import speech_recognition as sr  # serve per riconoscimento del parlato e conversione in testo
import time  # serve per gestire i tempi di registrazione
from googletrans import Translator
import numpy as np  #   serve per convertire il formato audio
import asyncio  # serve per gestire le coroutine
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image

print("benvenuto in questa applicazione fatta in solo 30 minuti (quindi farà un po' schifo) che ti fa vedere una parola in italiano e tu dovrai pronunciarla in inglese")
difficulty = input("Che difficoltà vuoi affrontare? (1 facile, 2 media, 3 difficile) o scrivi un nome di 4 lettere per un segreto:")
correct_words = 0

if difficulty == "1":
    parole = ["cane", "gatto", "casa", "albero", "libro", "sedia", "tavolo", "auto", "bicicletta", "telefono", "computer", "penna", "finestra", "porta", "strada", "fiore", "sole", "luna", "stella", "nuvola", "mare", "montagna", "cielo", "vento", "pioggia", "neve", "fuoco", "acqua", "terra", "uomo", "donna", "bambino", "amico", "scuola", "lavoro", "gioco", "sport", "musica", "arte", "cibo", "bevanda", "vestito", "scarpa", "orologio", "occhiale", "borsa", "cappello", "gonna", "pantalone", "maglietta", "giacca", "calzino", "guanto", "ombrello", "zaino", "valigia", "carta", "penna", "matita"]
elif difficulty == "2":
    parole = ["elefante", "giraffa", "coccodrillo", "rinoceronte", "ippopotamo", "leone", "tigre", "orso", "lupo", "volpe", "cervo", "coniglio", "scoiattolo", "pinguino", "canguro", "koala", "panda", "scimmia", "gorilla", "orangotango", "zebra", "gazzella", "antilope", "cavallo", "asino", "mucca", "pecora", "capra", "maiale", "pollo", "anatra", "oca", "tacchino", "struzzo", "fenicottero", "avvoltoio", "aquila", "falco", "gufo", "civetta", "corvo", "passero", "rondine", "gabbiano", "pavone", "colibrì", "piccione", "tordo", "usignolo", "cardellino", "canarino", "fringuello", "cinciallegra", "merlo", "pettirosso", "ghiandaia", "gazza", "cornacchia", "upupa"]
elif difficulty == "3":
    parole = ["anticonstitucionalmente", "inconstitucionalmente", "antidisestablishmentarianism", "floccinaucinihilipilification", "pneumonoultramicroscopicsilicovolcanoconiosis", "supercalifragilisticexpialidocious", "hippopotomonstrosesquipedaliophobia", "thyroparathyroidectomized", "psychoneuroendocrinological", "hepaticocholangiocholecystenterostomies", "spectrophotofluorometrically", "pseudopseudohypoparathyroidism", "electroencephalographically", "psychophysicotherapeutics", "radioimmunoelectrophoresis", "psychoneuroimmunology", "hepaticocholangiogastrostomy", "thyroparathyroidectomize", "dichlorodifluoromethane", "incomprehensibilities", "ultramicroscopicsilicovolcanoconiosis"]
elif difficulty == "nyan":
    try:
        fig = plt.figure()
        img = Image.open("nyan_cat.gif")
        frames = []
        try:
            while True:
                frames.append([plt.imshow(img.convert('RGB'))])
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        
        ani = animation.ArtistAnimation(fig, frames, interval=50, blit=True)
        plt.axis('off')
        plt.show()
    except Exception as e:
        print(f"Error: {e}")
        exit()
else:
    print("Difficoltà non riconosciuta!")
    exit()
        
    

def trascrittore_audio(durata_registrazione):
    segmenti_al_sec = 44100  # samplerate
    lingua_destinazione = "en"  # lingua in cui vogliamo tradurre il testo
    parola_selezionata = parole[np.random.randint(0, len(parole))]
    print("La parola da pronunciare è: " + parola_selezionata)  # scegliamo una parola a caso tra quelle disponibili

    # ora avviamo la registrazione
    print("Sta per partire la registrazione, quindi di qualcosa per i prossimi 5 secondi!")
    # creiamo la registrazione
    registrazione = sd.rec(int(durata_registrazione * segmenti_al_sec), samplerate=segmenti_al_sec, channels=1, dtype="int16")
    # sounddevice aspetta che l'utente finisca di registrare
    sd.wait()

    # aumentiamo il volume se troppo basso
    max_volume = np.max(np.abs(registrazione))
    print(f"[DEBUG] Volume massimo registrato: {max_volume}")
    
    if max_volume < 100:
        print("[DEBUG] Audio troppo silenzioso! Prova ad alzare la voce o controlla il microfono.")
    
    if max_volume > 0:
        registrazione = np.int16(registrazione * (32767 / max_volume) * 0.95)

    wav.write('audio.wav', segmenti_al_sec, registrazione)  # salviamo la registrazione in un file .wav
    print("Registrazione terminata con successo, a breve avrai la tua trascrizione....")

    time.sleep(1)
    # siamo arrivati ad avere il file salvato, ora dobbiamo andare a creare la trascrizione
    trascrittore = sr.Recognizer()
    trascrittore.energy_threshold = 1000  # abbassa molto la soglia di sensibilità
    trascrittore.dynamic_energy_threshold = False  # disabilita la regolazione automatica
    
    with sr.AudioFile("audio.wav") as source:
        audio = trascrittore.record(source)  # il trascrittore apre il file audio salvato prima e lo va ad ascoltare 

    testo_trascritto = ""
    testo_tradotto = ""
    
    try:
        # ora il nostro trascrittore deve trasformare l'audio in testo
        testo_trascritto = trascrittore.recognize_google(audio, language="en-US")
        print(f"Trascritto: {testo_trascritto}")
    except sr.UnknownValueError:             # - se Google non è riuscito a comprendere il discorso a causa di rumori o silenzi
        print("Il parlato non è stato riconosciuto.")
        return testo_trascritto, testo_tradotto, parola_selezionata
    except sr.RequestError as e:             # - se non c'è connessione Internet o l'API non è disponibile
        print(f"Errore di servizio: {e}")
        return testo_trascritto, testo_tradotto, parola_selezionata
    
    # traduciamo il testo
    traduttore = Translator()
    testo_tradotto = asyncio.run(traduttore.translate(testo_trascritto, dest="it"))
    print(f"Tradotto: {testo_tradotto.text}")
    return testo_trascritto, testo_tradotto, parola_selezionata

for i in range(10):
    testo_trascritto, testo_tradotto, parola_selezionata = trascrittore_audio(5)
    print(f"TESTO TRASCRITTO: {testo_trascritto}")
    
    if testo_trascritto and testo_tradotto and parola_selezionata.lower() in testo_tradotto.text.lower():
        print("Hai pronunciato correttamente la parola!")
        print("Passiamo alla parola successiva...")
        correct_words += 1
    else:
        print("Non hai pronunciato correttamente la parola.")
        print("Riprova con la prossima parola...")

print(f"Hai pronunciato correttamente {correct_words} parole su 10.")
