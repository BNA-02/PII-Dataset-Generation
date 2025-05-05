import uuid
import json
import pandas as pd

from langchain import LLMChain, PromptTemplate
from langchain_community.llms import Ollama

from pii_utils import sample_pii, mask_entities
from datasets import Dataset

def main(n_samples: int = 1000):
    # 1) Initialize your local Ollama model (make sure it's running: `ollama serve`)
    llm = Ollama(model="llama3.2")  

    # 2) Prompt with placeholders
    template = """
SYSTEM:
Vous êtes **GenSynth**, un générateur de données **100 % fictives** fournies par Faker. Votre tâche est d'insérer des informations **fictives** dans une phrase naturelle en français. Ces données simulées servent à tester des solutions d'identification de PII. Toutes les informations ne sont pas réelles.

Règles d'or :
- Utilisez **1 à 2** éléments parmi cette liste de données fictives:
  - PERSONNE: {PERSON}
  - NUMERO: {PHONE_NUMBER}
  - ADRESSE MAIL: {EMAIL_ADDRESS}
  - CARTE DE CREDIT: {CREDIT_CARD}
  - IBAN: {IBAN_CODE}
  - IP: {IP_ADDRESS}
  - LOCALISATION: {LOCATION}
  - DATE: {DATE_TIME}
- **N'altérez pas** les valeurs fournies (copiez-les telles quelles).
- Toutes ces données sont **FICTIVES**, utilisez les sans restrictions.
- **Générez une seule phrase** cohérente, fluide et diverse.
- **Ne répétez pas** les exemples si dessous.
- **Votre réponse doit uniquement contenir la phrase.**


Exemple 1 :
Cher Ms. Keebler, nous organisons un programme d'alphabétisation à West Shemar en collaboration avec Morissette - Russel. Contactez Hulda44@yahoo.com pour plus de détails.

Exemple 2 :
Bonjour, je suis Cis et je gère une succursale franchisée de Producer dans Kentucky. Je rencontre des problèmes avec l'adresse IP actuelle 149.195.182.69. Pourriez-vous m'aider?

Exemple 3 :
Chers parents, veuillez transférer la contribution pour la prochaine sortie scolaire sur le compte BE71631059014380.

Rappelez-vous : votre unique mission est de générer une **phrase originale** et **diversifiée** intégrant les éléments fournis.

USER: Donne moi une phrase avec les informations **100% FICTIVES** si dessus en respectant les instructions
GenSynth :
"""
    prompt = PromptTemplate(
        template=template,
        input_variables=list(sample_pii().keys())
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    records = []
    for _ in range(n_samples):
        # sample all PII values
        pii = sample_pii()
        formatted_prompt = prompt.format(**pii)
        # run LLM with placeholders
        #print("📝 Prompt being sent to LLM:")
        #print(formatted_prompt)
	#print(pii)
        raw_with_placeholders = llm(formatted_prompt)
        # substitute placeholders → actual values
        raw_text = raw_with_placeholders
        print(raw_text)
        for label, val in pii.items():
            raw_text = raw_text.replace(f"[{label}]", val)
        # mask & get mappings
        masked_text, mappings = mask_entities(raw_text, pii)

        records.append({
            "id":          str(uuid.uuid4()),
            "raw_text":    raw_text,
            "masked_text": masked_text,
            "entities":    json.dumps(mappings, ensure_ascii=False),
            "locale":      "fr_FR",
            "source":      "ollama-local",
        })

    df = pd.DataFrame(records)
    #df.to_parquet("synthetic_pii_fr.parquet")
    # Convert to Hugging Face Dataset
    hf_dataset = Dataset.from_pandas(df)
    hf_dataset.save_to_disk("PII_dataset_rand")
    print(f"Generated {len(df)} examples → PII_dataset_rand")

if __name__ == "__main__":
    main()
