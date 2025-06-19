
# 🌩️ Pixel Rain Tornado Explosion

Transformez vos images en spectacles visuels époustouflants !  
`Pixel Rain Animator` est une animation artistique où chaque image s'affiche, **s'effondre pixel par pixel**, est emportée par une **tornade animée**, puis **explose violemment** dans un flash blanc final 💥… avant qu'une nouvelle image n'entre en scène.

---

## 🖼️ Fonctionnalités

- 🧩 Affiche toute image en plein écran
- 🌧️ Pixels tombent individuellement avec gravité et collisions (effet "tas")
- 🌪️ Tornade aléatoire qui balaie l'écran dans toutes les directions possibles
- 💥 Flash + explosion dynamique au centre de l'image
- 🔁 Animation en boucle sur toutes les images du dossier

---

## 🚀 Installation

### 1. Télécharger le script

📥 [Télécharger `prog.py`](https://github.com/damballah/Pixel-Rain-Tornado-Explosion/blob/main/prog.py)  

### 2. Installer les dépendances

Assurez-vous d’avoir Python 3.10+ installé, puis :

```bash
pip install pygame pillow
```

### 3. Préparer les images

- Créez un dossier nommé `images` à côté de `prog.py`
- Ajoutez-y vos images `.jpg`, `.jpeg`, ou `.png`

### 4. Lancer le programme

```bash
python prog.py
```

---

## 🧱 Fonctionnement technique

| Élément     | Détail |
|-------------|--------|
| Taille de pixel | 4x4 |
| Résolution cible | 800x600 |
| Cadence | 60 FPS |
| Langages | Python (pygame + Pillow) |

---

## 🛠️ Compiler en `.exe` (Windows)

Vous pouvez créer un exécutable autonome :

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole prog.py
```

⚠️ Si une erreur apparaît à propos de `prog.spec` ou d’autorisations :
- Supprimez manuellement `prog.spec`
- Exécutez le terminal en tant qu’administrateur

---

## 📦 Dépendances

- [pygame](https://www.pygame.org/news) — pour le rendu graphique
- [Pillow](https://python-pillow.org/) — pour charger et redimensionner les images

---

## 💡 Idées futures

- Ajouter de la musique / des effets sonores
- Interface utilisateur pour choisir les images
- Mode plein écran dynamique
- Transitions personnalisables

---

## ✨ Démo (optionnel)

Ajoutez ici un GIF ou une vidéo si vous souhaitez montrer l’effet en action.

---

## ©️ Licence

Projet open-source. Utilisation libre sous licence MIT.
