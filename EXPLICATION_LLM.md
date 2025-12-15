# Comment le LLM est utilisé dans ce projet

## Vue d'ensemble

Ce projet utilise un **LLM (Large Language Model)** pour contrôler des robots Thymio dans un jeu de stratégie tour par tour. Les robots (agents) utilisent le LLM pour prendre des décisions, communiquer entre eux et naviguer dans une grille pour trouver des trésors.

**Note** : Le projet contient deux systèmes d'orchestration :
- **Supervisor** (utilisé dans `app.py` avec interface Streamlit) - système principal
- **Assembly** (dans `assembly.py`) - système alternatif plus simple

Cette documentation se concentre principalement sur le système Supervisor, mais les deux utilisent les mêmes principes de base.

## Architecture du système

### 1. Bibliothèque principale : ell-ai

Le projet utilise la bibliothèque `ell-ai` (version 0.0.14) qui est un framework pour créer des applications multi-agents basées sur des LLM. Elle permet de :
- Gérer des conversations structurées avec les LLM
- Créer des prompts système et utilisateur
- Enregistrer et tracer les interactions avec le modèle
- Faciliter les interactions multi-agents

### 2. Configuration du LLM

La configuration du LLM se fait dans `app.py` :

```python
import ell
from openai import OpenAI

# Initialisation du système ell avec stockage des logs
ell.init(store="./logdir")

# Configuration du client OpenAI (compatible avec Ollama)
client = OpenAI(
    base_url = os.getenv('BASE_URL'),  # Ex: http://localhost:11434/v1
    api_key = os.getenv('API_KEY'),     # Ex: "ollama"
)

# Enregistrement du modèle
ell.config.register_model(os.getenv('MODEL'), client)
```

**Variables d'environnement requises :**
- `BASE_URL` : URL du serveur LLM (ex: http://localhost:11434/v1 pour Ollama)
- `API_KEY` : Clé API (ex: "ollama" pour un serveur local)
- `MODEL` : Nom du modèle à utiliser (ex: "llama3.2:3b", "Qwen/Qwen2.5-72B-Instruct-AWQ")

### 3. Modèles supportés

Le projet peut utiliser différents modèles LLM :
- **llama3.2:3b** (mentionné dans `ell_multiagent.py`)
- **Qwen/Qwen2.5-72B-Instruct-AWQ** (mentionné dans `agent.py`)
- Tout modèle compatible avec l'API OpenAI

Le projet utilise **Ollama** comme serveur LLM local, ce qui permet d'exécuter des modèles open-source sans dépendre de services cloud.

## Utilisation du LLM dans les agents

### 1. Classe Agent

Chaque robot Thymio est représenté par un `Agent` qui utilise le LLM pour décider de ses actions.

Dans `agent.py`, la méthode `act()` est décorée avec `@ell.complex` :

```python
@ell.complex(model=os.getenv('MODEL'), temperature=0.3)
def act(self, conversation_history: list[Message]) -> Message:
    prompt = prompt_ally(self.name, self.color, conversation_history, 
                        self.pos, self.vision, self.allowed_move)
    sys_prompt = ell.system(prompt)
    return [sys_prompt] + conversation_history
```

**Paramètres importants :**
- `model` : Le modèle LLM à utiliser
- `temperature=0.3` : Contrôle la créativité des réponses (0.3 = plus déterministe et cohérent)

### 2. Système de prompts

Le projet utilise deux types de prompts principaux :

#### a) Prompt pour agents alliés (`prompt.py`)

Ce prompt structure le comportement de l'agent dans le jeu :

**Informations données au LLM :**
- Nom de l'agent (ex: "Thymio1")
- Couleur du trésor à trouver
- Historique des conversations avec les autres agents
- Position actuelle [x, y]
- Vision (cellules adjacentes et leur contenu)
- Actions possibles

**Format de réponse attendu :**
```
THOUGHTS: [Raisonnement sur l'action suivante en 50 mots]
MESSAGE: [Message à envoyer aux alliés]
ACTION: [Prochaine action]
```

#### b) Prompt initial (`initial_prompt.py`)

Utilisé pour initialiser les agents avec les règles du jeu :

**Règles du jeu expliquées au LLM :**
1. Carte composée de cellules sur une grille orthogonale (4x4 ou 10x10)
2. Chaque cellule peut contenir un robot, un trésor, un piège ou être vide
3. Impossible de se déplacer vers une cellule occupée par un allié
4. Vision limitée aux cellules adjacentes
5. Identification du type d'objet uniquement en étant sur la même cellule
6. Communication possible entre agents

**Objectifs donnés au LLM :**
1. Trouver son propre trésor (identifié par sa couleur)
2. Aider les alliés à trouver leurs trésors
3. Éviter les pièges (immobilisent pendant 1 tour)
4. Identifier et signaler les traîtres éventuels

### 3. Flux de conversation

Le `Supervisor` (dans `Supervisor.py`) orchestre les interactions :

```python
def _launch_discussion(self, round=1):
    for i, agent in enumerate(self.agents):
        # Premier agent à communiquer
        if i == 0:
            self.conversation_hist.append(
                ell.user(f"{agent.name}, you are the first to communicate!")
            )
        
        # L'agent génère sa réponse via le LLM
        message = agent.act(self.conversation_hist)
        
        # Extraction des composants de la réponse
        extraction = process_response_item(message)
        
        # Ajout du message à l'historique
        hist = extraction["MESSAGE"]
        self.conversation_hist.append(ell.user([f'{agent.name}:', hist]))
```

**Étapes d'une conversation :**
1. Le superviseur initialise la conversation
2. Chaque agent, à tour de rôle :
   - Reçoit l'historique complet de la conversation
   - Génère une réponse via le LLM (pensées + message + action)
   - Son message est ajouté à l'historique
3. Le cycle se répète jusqu'à ce que tous les agents atteignent leurs objectifs

## Traitement des réponses du LLM

### Parsing structuré

Le projet utilise deux systèmes de parsing selon le contexte :

#### Système 1 : Supervisor (utilisé dans app.py)

Fonction `process_response_item()` définie dans `Supervisor.py` :

```python
def process_response_item(response: Message):
    message = dict()
    message["THOUGHTS"] = response.text.split("MESSAGE:")[0]
    message["MESSAGE"] = response.text.split("MESSAGE:")[1].split("ACTION:")[0]
    message["ACTION"] = response.text.split("ACTION:")[1]
    return message
```

Ce système utilise le format **MESSAGE/ACTION** comme défini dans `prompt.py`.

#### Système 2 : Assembly (système alternatif)

Fonction `split_response()` dans `message_processing.py` :

```python
def split_response(response: Message, items: List) -> dict:
    out = {}
    for item in items:
        out[item] = get_response_item(response, item)
    return out
```

Ce système utilise le format **COMMUNICATE/BOT_COMMAND** et est plus flexible car il peut extraire n'importe quelle liste de champs.

### Conversion en commandes robot

Les actions textuelles du LLM sont converties en commandes pour les robots Thymio :

1. **Extraction de la position cible** : 
   ```python
   new_pos = tuple(int(v) for v in re.findall(r'\d+', command))
   ```

2. **Calcul de la direction relative** (fonction `get_move()`) :
   - Détermine la direction absolue (UP, DOWN, LEFT, RIGHT)
   - Convertit en direction relative selon l'orientation du robot
   - Génère la commande pour le robot physique

3. **Sauvegarde des ordres** :
   ```python
   with open("orders.txt", 'w+') as f:
       for direction in directions:
           f.write(f'{direction}\n')
   ```

## Interface utilisateur (Streamlit)

L'application Streamlit (`app.py`) affiche en temps réel :
- Les conversations entre agents
- Les pensées de chaque agent (THOUGHTS)
- Les messages échangés (MESSAGE)
- Les actions prises (ACTION)

```python
st.markdown(f"""
    <div class="chat-container">
        <div class="message-bubble {agent_class}">
            <div class="agent-name">{agent.name}</div>
            {message.content[-1].text}
        </div>
    </div>
""", unsafe_allow_html=True)
```

## Exemples concrets d'utilisation du LLM

### Exemple 1 : Prise de décision

**Contexte donné au LLM :**
- Agent : Thymio1
- Position : [0, 0]
- Vision : {(1,0): "empty", (0,1): "object"}
- Conversation : "Thymio1, you are the first to communicate!"

**Réponse générée par le LLM :**
```
THOUGHTS: I see an object at position (0,1). I should move there to identify if it's my treasure or a trap. I'll communicate this to my allies.
MESSAGE: I'm at position [0,0] and I can see an object at [0,1]. I'm going to investigate it.
ACTION: [0,1]
```

### Exemple 2 : Coordination entre agents

**Contexte :**
- Thymio1 a trouvé un trésor rouge à [2,3]
- Thymio2 cherche son trésor rouge

**Conversation :**

Thymio1 :
```
THOUGHTS: I found a red treasure at my position [2,3]. This might be Thymio2's treasure. I should inform him immediately.
MESSAGE: Thymio2, I found a red treasure at position [2,3]! You should come here if that's your color.
ACTION: [2,3]
```

Thymio2 :
```
THOUGHTS: Thymio1 found a red treasure at [2,3] and that's my color! I need to navigate there. From my current position [0,0], I'll move right first.
MESSAGE: Thanks Thymio1! The red treasure is mine. I'm heading to [2,3] now.
ACTION: [1,0]
```

## Avantages de cette architecture

1. **Flexibilité** : Les agents peuvent s'adapter à différentes situations grâce au raisonnement du LLM
2. **Communication naturelle** : Les agents échangent en langage naturel
3. **Décisions contextuelles** : Le LLM prend en compte tout l'historique de la conversation
4. **Extensibilité** : Facile d'ajouter de nouvelles règles ou comportements via les prompts
5. **Débogage** : Les "THOUGHTS" permettent de comprendre le raisonnement de l'agent

## Fichiers clés du projet

- `app.py` : Configuration du LLM et initialisation
- `agent.py` : Classe Agent avec la méthode `act()` utilisant le LLM
- `Supervisor.py` : Orchestration des agents et gestion de la conversation
- `prompt.py` : Template du prompt pour les agents alliés
- `initial_prompt.py` : Template du prompt initial avec les règles du jeu
- `message_processing.py` : Parsing des réponses du LLM
- `ell_multiagent.py` : Exemple d'utilisation du système multi-agent
- `env_conda.yml` : Dépendances du projet (incluant ell-ai, openai, streamlit)

## Configuration recommandée

Pour utiliser ce projet :

1. **Installer Ollama** : https://ollama.ai
2. **Télécharger un modèle** : `ollama pull llama3.2:3b`
3. **Créer un fichier `.env`** :
   ```
   BASE_URL=http://localhost:11434/v1
   API_KEY=ollama
   MODEL=llama3.2:3b
   ```
4. **Lancer l'application** : `streamlit run app.py`

## Conclusion

Ce projet démontre une utilisation innovante des LLM pour le contrôle de robots autonomes. Le LLM ne se contente pas de générer du texte : il raisonne, planifie et coordonne des actions dans un environnement multi-agent, tout en maintenant une communication naturelle entre les robots.
