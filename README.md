# MapReduce
Le projet est un Map-Reduce en python. On aura une gestion de sockets entre clients et serveur. 
Le Server, les Mappers et les Reducers ne seront pas forcement sur le meme ordinateur. Les différents ordinateurs devront cependant être sur le même réseau domestique (on utilise les IP locales). 
On peut utiliser autant de Mappers et de Reducers que l'on veut.
On gère les erreurs des Mappers et des Reducers. Si un Mapper crash, on le retire de notre liste de Mappers et le texte qui lui a été fourni est redistribué. Si un Reducer crash, on relance la fonction map_reduce sans ce Reducer.
L'opération à effectuer est simplement de compter les occurences de chaque mot d'un texte donné.
Le texte pourra être donné sous forme de chaine de caractères ou de fichier texte. On peut facilement rajouter des sources grace à la structure de la classe Text.
