# Server za otvaranje vrata u Veselina Masleše 120 #

Projekat sam razvio za potrebe zgrade u kojoj živim i kao takav je otvoren za sve zainteresovane da ga kontrolišu i predlože izmene.
U ovom dokumentu ću pokušati da objasnim funkcionisanje sistema na način da mogu da ga razumeju nestručna lica.
Za stručna lica koja razumeju Python programski jezik, preporučujem da posete git repozitorijum:

    https://github.com/ujagaga/door_lock_server

i prebace se na granu "vm120"

## Komponente sistema ##

1. Server je web sajt koji sam napisao lično i samostalno ga održavam. Osnovne funkcije su:
    - Obrada i čuvanje korisničkih naloga. Naloge kreiram isključivo ja i to po prijavi. Tako ih ja mogu i brisati u slučaju zloupotrebe.
    - Slanje komande za otključavanje interfonskih vrata, koju izvršava, za tu namenu napravljen, uređaj povezan sa interfonskom kontrolom.
    - Generisanje privremenog linka za otključavanje. Ovo je korisno ako imate goste ili želite link koji možete da sačuvate u obeleživaču 
      internet pretraživača i koristite bez logovanja.
    - prihvatanje prijave detektovanog koda sa RFID TAG-a za otključavanje ili bilo kakvog NFC uređaja 
      (pametni telefon, kreditna kartica, NFC prsten...).
    - prisvajanje ne odobrenog koda svom korisničkom nalogu, radi otključavanja vrata koristeći isti. 
      Napomena: svi detektovani kodovi se prvo na uređaju kodiraju (skrembluju), pa se onda šalju na server gde se dodatno modifikuju. Ne postoji proces kojim bi se 
      dešifrovao originalni kod. Mogu samo da se jednoznačno identifikuju, tj. razaznaju međusobno. Tako možete da koristite i kreditnu karticu
      ili NFC pametni telefon za otključavanje vrata bez mogućnosti da se sačuvani kod upotrebi u druge svrhe.

2. MQTT server je specijalan servis koji je javni i ne održavam ja. Preko njega se šalju komande uređaju za otključavanje i nikakve bezbednosne informacije.
    Kanali preko kojih se šalje se nasumično biraju prilikom prijavljivanja uređaja na server i menjaju se ako se primeti bilo kakvo ne predviđeno ponašanje.
    Ovo je neohodno radi momentalnog otključavanja kada se zada komanda. Druga opcija bi bila da uređaj periodično pita server za instrukcije, što bi usporavalo odziv.

3. Uređaj za otključavanje radi preko WiFi konekcije sa ruterom postavljenim u mom stanu. Prihvata zasad RFID TAG-ove kakve imamo već na ključevima, a uskoro i NFC kodove
   sa telefona, kreditnih kartica,...Dizajnirao sam ga i napravio lično, pa za bilo kakvo održavanje možete da se obratite samo meni. 

## Contact ##

* web: http://www.radinaradionica.com
* email: ujagaga@gmail.com

