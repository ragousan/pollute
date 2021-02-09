# pollute
Το πρόγραμμα παίρνει ως είσοδο δεδομένα από το European Environment Agency που αφορούν τα επίπεδα του όζοντος στην Αθήνα για την περίοδο 2013-2015.
Με την κατάλληλη επεξεργασία παράγεται ένας χάρτης σε html μορφή ο οποίος παρουσιάζει την ατμοσφαιρική ρύπανση με την πάροδο του χρόνου.
Στη συνέχεια μέσω ενός flask_app μπορούμε να δούμε τον χάρτη

•	To 1ο  docker image έγινε push στο dockerhub

    o	Περιέχει το κώδικα (air_pollute.py)

•	Το 2ο δημιουργείται με το docker-compose

    o	Περιέχει το flask_app (post_pollute.py)


RUN:

  git clone -b withimage git@github.com:ragousan/pollute.git
  
  cd pollute
  
  docker-compose up

GO TO http://0.0.0.0:5000/ 


**Το branch *withimage* περιέχει το dockerhub image. Το main branch δημιουργει locally και τα 2 images**
