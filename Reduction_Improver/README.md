### How to run? Use Python 3.13.13

1. conda create -n llmapp python=3.13.13 -y

2. conda activate llmapp

3. pip install -r requirements.txt

4. streamlit run main.py

Enter your own Grok API key in the app when it starts. The key is not loaded
from `.env` or displayed as a default value. You can optionally set
`GROK_MODEL`; it defaults to `grok-4`.


input demo:

Please, please, please, My customer, buy my product