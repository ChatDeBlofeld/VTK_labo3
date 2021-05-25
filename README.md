# VTK - Labo 3

## Explications vidéo

- Couper (descendre d'une dimension -> courbe) : VTKCutter (entrée polydata lue et une fonction implicite, par ex VtkPlane avec set origin et set normal)
- Cliper (garder la même dimension mais garde le truc) : "enlève de la matière en polydata"

VtkRenderWindow -> plusieurs renderer dans la window

Set de données : 

Haut gauche : Affiche l'os tel quel et affiche la peau avec des coupes horizontales à différentes hauteurs (tubées -> VtkTubeFilter à partie de la courbe)
Haut droite : peau faces visibles -> transparente, peau faces non visibles -> visibles (retirer le backface culling) + coupe de la surface (peau) avec une sphere au niveau du genou
Bas gauche : coupe avec même sphère que haut droite mais affichée en la convertissant explicite + transparence
Bas droite : affiche que l'os. Colorier l'os -> lookup table (fonction de transfer vu la gueule du truc, carte de couleur arc-enciel du bleu au rouge). Paramètres : distance à la surface de la peau (rouge près bleu loin)

Coordonner les renderer : utilise tous les quatre la même caméra