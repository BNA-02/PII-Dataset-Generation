import uuid
import json
import random
import pandas as pd
from langchain import LLMChain, PromptTemplate
from langchain_community.llms import Ollama
from pii_utils import sample_pii, mask_entities
from datasets import Dataset

def main(n_samples: int = 1000):
    print("🔁 Initializing model...")
    llm = Ollama(model="llama3.2")

    # List of all possible PII fields
    all_labels = [
        "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS",
        "CREDIT_CARD", "IBAN_CODE", "IP_ADDRESS",
        "LOCATION", "DATE_TIME"
    ]

    records = []

    for i in range(n_samples):
        print(f"\n=== SAMPLE {i + 1} / {n_samples} ===")

        # 1. Randomly select 1 or 2 PII types
        sampled_labels = random.sample(all_labels, k=random.choice([1, 3]))
        print(f"🔹 Using fields: {sampled_labels}")

        pii_full = sample_pii()
        pii_subset = {key: pii_full[key] for key in sampled_labels}
        print(f"🔸 Sampled PII values: {pii_subset}")

        # 2. Build prompt dynamically
        info_block = "\n".join([f"  - {label.replace('_', ' ')}: {{{label}}}" for label in sampled_labels])
        prompt_text = f"""
        SYSTEM:
        Vous êtes **GenSynth**, un générateur de données **100 % fictives** fournies par Faker. Votre tâche est d'insérer des informations **fictives** dans une phrase naturelle en français. Ces données simulées servent à tester des solutions d'identification de PII. Toutes les informations ne sont pas réelles.

        Règles d'or :
        - **N'altérez pas** les valeurs fournies (copiez-les telles quelles).
        - Toutes ces données sont **FICTIVES**, utilisez-les sans restrictions.
        - **Générez une seule phrase** cohérente, fluide et diverse.
        - **Votre réponse doit uniquement contenir la phrase.**
        - Utilisez les éléments suivants :
        {info_block}

        GenSynth :
        """

        prompt = PromptTemplate(template=prompt_text, input_variables=sampled_labels)
        chain = LLMChain(llm=llm, prompt=prompt)

        # 3. Run the LLM to generate the sentence
        raw_with_placeholders = chain.run(**pii_subset)
        raw_text = raw_with_placeholders.strip()
        print(f"📝 Raw generated sentence: {raw_text}")

        # 4. Masking (use all original values to ensure no misses)
        masked_text, mappings = mask_entities(raw_text, pii_full)
        print(f"🔒 Masked sentence: {masked_text}")
        print(f"📌 Entities found: {mappings}")

        # 5. Store the result
        records.append({
            "id":          str(uuid.uuid4()),
            "raw_text":    raw_text,
            "masked_text": masked_text,
            "entities":    json.dumps(mappings, ensure_ascii=False),
            "locale":      "fr_FR",
            "source":      "ollama-local",
        })

        if (i + 1) % 10 == 0:
            print(f"✅ Generated {i + 1} examples so far...")

    # 6. Save everything
    df = pd.DataFrame(records)
    hf_dataset = Dataset.from_pandas(df)
    hf_dataset.save_to_disk("PII_dataset_gen")

    print(f"\n✅ Done! Generated {len(df)} examples → PII_dataset_gen")

if __name__ == "__main__":
    main()
